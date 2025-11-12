"""
Ollama Client with Multi-Endpoint Failover

Supports automatic failover between multiple Ollama servers for high availability:
- Primary: edgeserver (192.168.0.30:11434)
- Secondary: corertx (to be configured)

Features:
- Automatic failover on timeout/error
- Health monitoring per endpoint
- Performance metrics (requests, latency, success rate)
- Prometheus integration ready
"""

import aiohttp
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import os

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client Ollama avec failover automatique multi-serveurs.
    
    Attributes:
        endpoints: Liste URLs Ollama (edgeserver, corertx, etc.)
        current_endpoint_index: Index de l'endpoint actif
        metrics: Statistiques de performance
    """
    
    def __init__(self):
        """Initialize Ollama client with multiple endpoints."""
        # Endpoints configurables via environment variables
        self.endpoints = [
            os.getenv("OLLAMA_PRIMARY_URL", "http://192.168.0.30:11434"),   # edgeserver
            os.getenv("OLLAMA_SECONDARY_URL", "http://192.168.0.31:11434")  # corertx (à configurer)
        ]
        
        self.current_endpoint_index = 0
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "failovers": 0,
            "endpoint_health": {ep: True for ep in self.endpoints},
            "latency_history": []  # Dernières 100 requêtes
        }
        
        logger.info(f"OllamaClient initialized with {len(self.endpoints)} endpoints: {self.endpoints}")
    
    async def _check_endpoint_health(self, endpoint: str, timeout: int = 5) -> bool:
        """
        Vérifier la santé d'un endpoint Ollama.
        
        Args:
            endpoint: URL de l'endpoint Ollama
            timeout: Timeout en secondes
            
        Returns:
            True si endpoint répond, False sinon
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{endpoint}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    if resp.status == 200:
                        logger.debug(f"Endpoint healthy: {endpoint}")
                        return True
                    else:
                        logger.warning(f"Endpoint unhealthy ({resp.status}): {endpoint}")
                        return False
        except Exception as e:
            logger.warning(f"Health check failed for {endpoint}: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        model: str = "llama3.2:1b",
        temperature: float = 0.7,
        max_retries: int = 2,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Générer une réponse avec failover automatique.
        
        Essaie chaque endpoint dans l'ordre jusqu'à succès.
        Fallback automatique si un endpoint échoue.
        
        Args:
            prompt: Le prompt à envoyer au modèle
            model: Modèle Ollama (default: llama3.2:1b)
            temperature: Créativité 0.0-1.0 (default: 0.7)
            max_retries: Retry par endpoint (default: 2)
            timeout: Timeout requête en secondes (default: 60)
            
        Returns:
            Dict contenant:
            - status: "success" ou "error"
            - response: Texte généré (si succès)
            - model: Modèle utilisé
            - endpoint: Endpoint ayant répondu
            - timing: Statistiques de performance
            - error: Message d'erreur (si échec)
        """
        self.metrics["requests_total"] += 1
        start_time = datetime.now(timezone.utc)
        
        # Essayer chaque endpoint dans l'ordre
        for endpoint_index, endpoint in enumerate(self.endpoints):
            # Skip si endpoint connu comme down
            if not self.metrics["endpoint_health"][endpoint]:
                logger.debug(f"Skipping unhealthy endpoint: {endpoint}")
                continue
            
            for attempt in range(max_retries):
                try:
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "model": model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": temperature,
                                "num_predict": 512  # Max tokens
                            }
                        }
                        
                        logger.debug(f"Sending request to {endpoint} (attempt {attempt+1}/{max_retries})")
                        
                        async with session.post(
                            f"{endpoint}/api/generate",
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=timeout)
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                
                                # Succès!
                                self.metrics["requests_success"] += 1
                                self.metrics["endpoint_health"][endpoint] = True
                                self.current_endpoint_index = endpoint_index
                                
                                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                                
                                # Enregistrer latence (max 100 dernières)
                                self.metrics["latency_history"].append(elapsed)
                                if len(self.metrics["latency_history"]) > 100:
                                    self.metrics["latency_history"].pop(0)
                                
                                logger.info(
                                    f"Ollama success: {endpoint} ({elapsed:.2f}s, "
                                    f"{data.get('eval_count', 0)} tokens)"
                                )
                                
                                return {
                                    "status": "success",
                                    "response": data.get("response", ""),
                                    "model": model,
                                    "endpoint": endpoint,
                                    "timing": {
                                        "total_seconds": elapsed,
                                        "eval_count": data.get("eval_count", 0),
                                        "eval_duration_ms": data.get("eval_duration", 0) / 1_000_000,
                                        "prompt_eval_count": data.get("prompt_eval_count", 0),
                                        "prompt_eval_duration_ms": data.get("prompt_eval_duration", 0) / 1_000_000
                                    },
                                    "metadata": {
                                        "total_duration_ns": data.get("total_duration", 0),
                                        "load_duration_ns": data.get("load_duration", 0),
                                        "done": data.get("done", False)
                                    }
                                }
                            else:
                                logger.warning(f"Ollama error {resp.status} from {endpoint}")
                                error_text = await resp.text()
                                logger.debug(f"Error response: {error_text}")
                
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Timeout on {endpoint} after {timeout}s "
                        f"(attempt {attempt+1}/{max_retries})"
                    )
                except aiohttp.ClientError as e:
                    logger.error(f"Client error on {endpoint}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error on {endpoint}: {e}", exc_info=True)
                
                # Si dernier retry, marquer endpoint comme down
                if attempt == max_retries - 1:
                    self.metrics["endpoint_health"][endpoint] = False
                    logger.warning(f"Marking endpoint as unhealthy: {endpoint}")
            
            # Failover au prochain endpoint
            if endpoint_index < len(self.endpoints) - 1:
                self.metrics["failovers"] += 1
                logger.warning(
                    f"Failover from {endpoint} to next endpoint "
                    f"({self.metrics['failovers']} total failovers)"
                )
        
        # Tous les endpoints ont échoué
        self.metrics["requests_failed"] += 1
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        logger.error(
            f"All Ollama endpoints failed after {elapsed:.2f}s. "
            f"Tried: {self.endpoints}"
        )
        
        return {
            "status": "error",
            "error": "All Ollama servers unavailable",
            "endpoints_tried": self.endpoints,
            "timing": {"total_seconds": elapsed},
            "metrics": self.get_metrics()
        }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        Liste les modèles disponibles sur l'endpoint actif.
        
        Returns:
            Liste de dicts avec info sur chaque modèle:
            - name: Nom du modèle
            - modified_at: Date modification
            - size: Taille en bytes
        """
        endpoint = self.endpoints[self.current_endpoint_index]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{endpoint}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("models", [])
                        logger.info(f"Found {len(models)} models on {endpoint}")
                        return models
                    else:
                        logger.warning(f"Failed to list models: HTTP {resp.status}")
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        
        return []
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Vérifier la santé de tous les endpoints.
        
        Returns:
            Dict {endpoint: is_healthy}
        """
        health = {}
        
        for endpoint in self.endpoints:
            is_healthy = await self._check_endpoint_health(endpoint)
            health[endpoint] = is_healthy
            self.metrics["endpoint_health"][endpoint] = is_healthy
        
        logger.info(f"Health check results: {health}")
        return health
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques de performance.
        
        Returns:
            Dict contenant:
            - requests_total: Nombre total requêtes
            - requests_success: Nombre succès
            - requests_failed: Nombre échecs
            - success_rate_percent: Taux de succès %
            - failovers: Nombre de failovers
            - current_endpoint: Endpoint actif
            - endpoint_health: Status de chaque endpoint
            - avg_latency_seconds: Latence moyenne
        """
        success_rate = (
            self.metrics["requests_success"] / self.metrics["requests_total"] * 100
            if self.metrics["requests_total"] > 0 else 0
        )
        
        avg_latency = (
            sum(self.metrics["latency_history"]) / len(self.metrics["latency_history"])
            if self.metrics["latency_history"] else 0
        )
        
        return {
            "requests_total": self.metrics["requests_total"],
            "requests_success": self.metrics["requests_success"],
            "requests_failed": self.metrics["requests_failed"],
            "success_rate_percent": round(success_rate, 2),
            "failovers": self.metrics["failovers"],
            "current_endpoint": self.endpoints[self.current_endpoint_index],
            "endpoint_health": self.metrics["endpoint_health"].copy(),
            "avg_latency_seconds": round(avg_latency, 3),
            "latency_p50": round(
                sorted(self.metrics["latency_history"])[len(self.metrics["latency_history"])//2]
                if self.metrics["latency_history"] else 0,
                3
            ),
            "latency_p95": round(
                sorted(self.metrics["latency_history"])[int(len(self.metrics["latency_history"]) * 0.95)]
                if len(self.metrics["latency_history"]) > 0 else 0,
                3
            )
        }
    
    def reset_metrics(self):
        """Reset toutes les métriques (pour tests)."""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "failovers": 0,
            "endpoint_health": {ep: True for ep in self.endpoints},
            "latency_history": []
        }
        logger.info("Metrics reset")


# Singleton global
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """
    Retourne l'instance singleton du client Ollama.
    
    Returns:
        Instance OllamaClient configurée
    """
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client

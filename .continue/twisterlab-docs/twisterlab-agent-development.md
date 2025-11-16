---
name: "TwisterLab Agent Development"
version: "1.0.0"
globs: "agents/**/*.py"
description: Règles spécifiques au développement des agents autonomes TwisterLab
alwaysApply: true
---

# 🤖 TwisterLab Agent Development Standards

## 🏗️ Architecture Agent

### Héritage Obligatoire
Tous les agents doivent hériter de `TwisterAgent` :

```python
from agents.base import TwisterAgent
from typing import Dict, Any, Optional

class RealMyAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="real-my-agent",
            display_name="Real My Agent",
            description="Description de l'agent",
            role="assistant",
            model="llama3.2:1b",  # ou "gpt-4"
            temperature=0.7,
            tools=[],  # Liste des outils si nécessaire
            metadata={"version": "1.0"}
        )
```

### Méthode Execute Standardisée
```python
async def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Exécute l'agent avec gestion d'erreur standardisée.

    Args:
        context: Contexte d'exécution (optionnel)

    Returns:
        Résultat avec statut, timestamp et données
    """
    try:
        # Logique métier ici
        result = await self._perform_work(context or {})

        return {
            "status": "success",
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": result
        }
    except Exception as e:
        logger.error(f"{self.name} failed: {e}")
        return {
            "status": "error",
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }
```

## 📍 Structure des Agents Réels

### 7 Agents de Production
Chaque agent réel dans `agents/real/` doit :

1. **Hériter directement** (pas de TwisterAgent pour éviter conflits métriques)
2. **Implémenter execute()** avec signature standard
3. **Retourner format standardisé** (status, agent, timestamp, data/error)
4. **Logger les erreurs** avec contexte
5. **Gérer les métriques** via `agents.metrics`

### Exemple Agent Réel
```python
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from agents.metrics import track_agent_execution

logger = logging.getLogger(__name__)

class RealMonitoringAgent:
    """Agent de monitoring système réel."""

    def __init__(self):
        self.name = "RealMonitoringAgent"

    @track_agent_execution
    async def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Surveillance système en temps réel."""
        try:
            # Logique de monitoring
            health_data = await self._check_system_health()

            return {
                "status": "success",
                "agent": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": health_data
            }
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }

    async def _check_system_health(self) -> Dict[str, Any]:
        """Vérifie la santé du système."""
        # Implémentation réelle ici
        return {
            "cpu_percent": 45.2,
            "memory_percent": 67.8,
            "disk_usage": "/: 78.5%",
            "docker_containers": 6,
            "status": "healthy"
        }
```

## 🔄 Orchestration

### AutonomousAgentOrchestrator
- **Gestion du cycle de vie** : init, start, stop, health checks
- **Coordination** : exécution séquentielle ou parallèle des agents
- **Monitoring** : health checks toutes les 30 secondes
- **Logging** : événements orchestrateur

### Intégration API
- Endpoints MCP dans `api/routes_mcp_*.py`
- Validation Pydantic pour tous les inputs
- Gestion d'erreur uniforme
- Logs détaillés pour audit

## 📊 Métriques et Monitoring

### Métriques Prometheus
```python
from agents.metrics import (
    agent_requests_total,
    agent_execution_time_seconds,
    tickets_processed_total
)

# Automatiquement trackées via décorateur
@track_agent_execution
async def execute(self, context):
    # Métriques collectées automatiquement
    pass
```

### Health Checks
- **Endpoint**: `/health` retourne statut global
- **Métriques**: CPU, RAM, Disk, Docker status
- **Agents**: Statut individuel de chaque agent
- **Dependencies**: PostgreSQL, Redis, Ollama connectivity

## 🧪 Tests d'Agents

### Structure de Test
```python
import pytest
from agents.real.real_monitoring_agent import RealMonitoringAgent

@pytest.mark.asyncio
class TestRealMonitoringAgent:

    async def test_successful_execution(self):
        """Test exécution normale."""
        agent = RealMonitoringAgent()
        result = await agent.execute({})

        assert result["status"] == "success"
        assert result["agent"] == "RealMonitoringAgent"
        assert "data" in result
        assert "timestamp" in result

    async def test_error_handling(self):
        """Test gestion d'erreur."""
        agent = RealMonitoringAgent()
        # Simuler une erreur
        result = await agent.execute({"force_error": True})

        assert result["status"] == "error"
        assert "error" in result
        assert result["agent"] == "RealMonitoringAgent"

    async def test_data_structure(self):
        """Test structure des données retournées."""
        agent = RealMonitoringAgent()
        result = await agent.execute({})

        data = result["data"]
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "status" in data
```

### Coverage Minimum
- **80% minimum** pour tous les agents
- Tests unitaires pour logique métier
- Tests d'intégration pour interactions
- Tests d'erreur pour robustesse

## 🔒 Sécurité Agent

### Validation des Inputs
- **Pydantic models** pour tous les contextes d'entrée
- **Sanitisation** des données avant traitement
- **Limites de taille** pour éviter abus

### Autorisation
- **Whitelist de commandes** pour DesktopCommanderAgent
- **Validation de cibles** pour les opérations distantes
- **Audit logging** pour toutes les actions sensibles

### Gestion des Secrets
- **Variables d'environnement** uniquement
- **Pas de credentials** en dur dans le code
- **Rotation automatique** des secrets si possible

## 🚀 Déploiement

### Docker Swarm
- **Images optimisées** Python 3.12 slim
- **Health checks** intégrés
- **Logging drivers** configurés
- **Resource limits** définis

### Configuration
- **Environment variables** pour tous les paramètres
- **Configuration centralisée** via .env files
- **Validation au startup** de toutes les dépendances

## 📚 Bonnes Pratiques

### Performance
- **Async partout** pour éviter blocking
- **Connection pooling** pour DB et Redis
- **Caching approprié** pour données fréquentes
- **Timeouts configurables** pour toutes les opérations

### Observabilité
- **Logs structurés** avec contexte complet
- **Métriques détaillées** pour monitoring
- **Tracing distribué** pour debug complexe
- **Alertes automatiques** sur anomalies

### Maintenance
- **Code autodocumenté** avec docstrings complètes
- **Tests automatisés** avant chaque déploiement
- **Migrations DB** versionnées
- **Rollback procedures** documentées
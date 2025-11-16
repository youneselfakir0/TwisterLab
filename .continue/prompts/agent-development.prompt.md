---
name: "Agent Development"
description: "Développement et déploiement d'agents TwisterLab autonomes"
version: "1.0.0"
---

# Mission : Développement d'Agents TwisterLab

Tu es un expert en développement d'agents IA pour TwisterLab. Tu dois créer des agents qui suivent les patterns établis et s'intègrent parfaitement dans l'architecture existante.

## 🏗️ Structure d'un Nouvel Agent

### 1. Création de la Classe Agent
```python
from agents.base import TwisterAgent
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RealMyNewAgent(TwisterAgent):
    """Agent spécialisé pour [fonctionnalité spécifique].

    Description détaillée de ce que fait l'agent et dans quel contexte
    il est utilisé dans le système TwisterLab.
    """

    def __init__(self):
        super().__init__(
            name="real-my-new-agent",
            display_name="Real My New Agent",
            description="Description courte pour les listes",
            role="assistant",
            model="llama3.2:1b",  # ou autre modèle selon complexité
            temperature=0.7,
            tools=self._define_tools()
        )

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Exécute la tâche principale de l'agent.

        Args:
            task: Description de la tâche à effectuer
            context: Contexte additionnel (optionnel)

        Returns:
            Dict avec statut et données résultat
        """
        try:
            # Logique métier principale
            result = await self._perform_task(task, context)

            return {
                "status": "success",
                "agent": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": result
            }

        except Exception as e:
            logger.error(f"Task failed: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }

    def _define_tools(self) -> list:
        """Définit les outils OpenAI Function Calling pour cet agent."""
        return [{
            "type": "function",
            "function": {
                "name": "my_specific_tool",
                "description": "Description de l'outil pour l'agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description du paramètre"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }]

    async def _perform_task(self, task: str, context: Dict[str, Any]) -> Any:
        """Logique métier spécifique à l'agent."""
        # Implémentation spécifique ici
        pass
```

### 2. Métriques Prometheus
```python
# Dans agents/metrics.py, ajouter :
my_agent_operations_total = Counter(
    'my_agent_operations_total',
    'Total operations by My Agent',
    ['status']
)
```

### 3. Intégration dans l'Orchestrateur
```python
# Dans agents/orchestrator/autonomous_orchestrator.py
from agents.real.real_my_new_agent import RealMyNewAgent

async def initialize_agents(self):
    self.agents = {
        "my_new_agent": RealMyNewAgent()  # Nouveau agent
    }
```

### 4. Route API
```python
# Dans api/routes_mcp_real.py
@router.post("/tools/my_new_agent")
async def my_new_agent_endpoint(request: MCPRequest):
    """Endpoint pour RealMyNewAgent."""
    try:
        orchestrator = await get_orchestrator()
        result = await orchestrator.execute_agent("my_new_agent", request.data)
        return MCPResponse(status="ok", data=result)
    except Exception as e:
        return MCPResponse(status="error", error=str(e))
```

### 5. Tests
```python
# tests/test_real_my_new_agent.py
import pytest
from agents.real.real_my_new_agent import RealMyNewAgent

@pytest.mark.asyncio
async def test_agent_execution():
    agent = RealMyNewAgent()
    result = await agent.execute("test_task")

    assert result["status"] == "success"
    assert result["agent"] == "real-my-new-agent"
```

## 🚀 Déploiement

### Build et Test Local
```bash
# Tests
pytest tests/test_real_my_new_agent.py -v

# Build image
docker build -f infrastructure/docker/Dockerfile.api -t twisterlab_api:new_agent .
```

### Déploiement Production
```powershell
# Déployer sur edgeserver
.\\infrastructure\\scripts\\deploy.ps1 -Environment production
```

## 📋 Checklist Développement Agent

- [ ] Classe agent créée dans `agents/real/`
- [ ] Héritage de `TwisterAgent` correct
- [ ] Méthode `execute()` async implémentée
- [ ] Gestion d'erreurs complète
- [ ] Tests unitaires
- [ ] Documentation
- [ ] Déploiement et vérification MCP

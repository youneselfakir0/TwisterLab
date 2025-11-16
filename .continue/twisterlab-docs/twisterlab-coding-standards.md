---
name: "TwisterLab Coding Standards"
version: "1.0.0"
globs: "**/*.py"
description: Standards de codage Python et FastAPI pour TwisterLab v1.0.0
alwaysApply: true
---

# 📋 TwisterLab Coding Standards v1.0.0

## 🐍 Python Best Practices

### Type Hints Obligatoires (PEP 484)
- **MANDATORY**: Toutes les fonctions, méthodes et classes doivent avoir des type hints complets
- Utiliser le module `typing` pour les types complexes
- Exemple: `async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:`

### Docstrings Google-Style
- **OBLIGATOIRE**: Docstrings au format Google pour toutes les fonctions/classes publiques
- Inclure description, paramètres, types de retour et exceptions

```python
async def execute_task(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Exécute une tâche spécifique par ID.

    Args:
        task_id: Identifiant unique de la tâche
        context: Contexte additionnel (optionnel)

    Returns:
        Résultat de l'exécution avec statut

    Raises:
        TaskNotFoundError: Si task_id n'existe pas
    """
```

### Patterns Async/Await
- **PRÉFÉRÉ**: Fonctions async pour toutes les opérations I/O
- Toutes les méthodes `execute()` des agents doivent être async
- Utiliser `httpx` pour les requêtes HTTP async (pas `requests`)

### Gestion d'Erreurs
- Logging structuré avec `logging` (pas `print` !)
- Capturer des exceptions spécifiques, pas `Exception` générique
- Logger les erreurs avec contexte pour le debugging

## 🚀 FastAPI Development

### Structure API
- Routes organisées par domaine dans `api/routes_*.py`
- Documentation OpenAPI automatique sur `/docs`

### Response Models
- Utiliser Pydantic pour tous les modèles de réponse
- Format standard: `{"status": "success|error", "data": {...}, "error": "..."}`

### Validation
- Valider tous les inputs avec Pydantic models
- Sanitiser les données utilisateur
- Vérifier les permissions avant exécution

## 🤖 TwisterAgent Development

### Base Class Inheritance
```python
from agents.base import TwisterAgent
from typing import Dict, Any, Optional

class MyAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            display_name="My Agent",
            description="What this agent does",
            role="assistant",
            model="llama3.2:1b",
            temperature=0.7
        )

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute agent task - MUST be implemented"""
        try:
            # Agent logic here
            result = await self._perform_task(task, context)
            return {
                "status": "success",
                "agent": self.name,
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }
```

### Métriques Prometheus
- Tous les agents doivent exposer des métriques via `agents.metrics`
- Counters pour les opérations, Histograms pour les temps d'exécution
- Labels: `agent_name`, `status`

### Testing
- Tests pytest avec `pytest.mark.asyncio`
- Mock des dépendances externes
- Coverage minimum 80%
- Tests d'intégration pour les agents critiques

## 🔒 Sécurité

### Credentials
- Jamais de credentials en dur dans le code
- Utiliser variables d'environnement ou secrets Docker
- Rotation automatique des secrets

### Input Validation
- Valider tous les inputs utilisateur
- Sanitiser les commandes système
- Whitelist des opérations autorisées

### Audit Logging
- Logger toutes les actions sensibles
- Inclure contexte utilisateur/agent
- Format JSON pour parsing automatique

## 📊 Monitoring

### Logs Structurés
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Task completed", extra={
    "agent": self.name,
    "task_id": task_id,
    "duration_ms": duration,
    "status": "success"
})
```

### Health Checks
- Endpoint `/health` pour tous les services
- Métriques Prometheus exposées sur `/metrics`
- Status détaillé des dépendances

## 🧪 Testing Standards

### Unit Tests
```python
import pytest
from agents.real.my_agent import MyAgent

@pytest.mark.asyncio
async def test_agent_execution():
    agent = MyAgent()
    result = await agent.execute("test_task")

    assert result["status"] == "success"
    assert "data" in result
    assert result["agent"] == "my-agent"
```

### Integration Tests
- Tester l'intégration avec PostgreSQL/Redis
- Valider les appels API externes
- Vérifier la sérialisation/désérialisation

## 📚 Documentation

### Code Documentation
- Docstrings pour toutes les fonctions publiques
- Commentaires pour la logique complexe
- README pour chaque module

### API Documentation
- OpenAPI généré automatiquement
- Exemples d'utilisation
- Gestion des erreurs documentée
- Injection de dépendances pour les services partagés

### Modèles Request/Response
- Définir des modèles Pydantic pour tous les inputs/outputs API
- Validation appropriée avec contraintes de champs
- Inclure des exemples dans la documentation du schéma

## 🤖 Développement d'Agents

### Héritage d'Agents
- Tous les agents doivent hériter de `TwisterAgent` dans `agents/base.py`
- Implémenter les méthodes abstraites requises
- Suivre le pattern standard du constructeur (name, display_name, description, etc.)

### Communication Inter-Agents
- Utiliser l'`AutonomousAgentOrchestrator` pour la coordination
- Implémenter la sérialisation/désérialisation appropriée des messages
- Gérer les timeouts et retries des messages

## 🧪 Standards de Test

### Coverage de Test
- **Minimum 80% coverage** requis
- Utiliser `pytest` avec fixtures partagées dans `tests/conftest.py`
- Écrire des tests d'intégration pour les flux end-to-end

### Organisation des Tests
- Fichiers de test nommés `test_{component}.py`
- Noms de test descriptifs avec docstrings
- Mock des services externes pour les tests unitaires

## 🛠️ Outils Qualité Code

### Linting et Formatage
- **ruff**: Linter principal (rapide et strict)
- **black**: Formatage du code (longueur ligne 88)
- **mypy**: Vérification de types statiques

### Pre-commit Hooks
- Tous les contrôles qualité s'exécutent automatiquement
- Aucun commit autorisé avec des contrôles échouants

## 🗄️ Accès Base de Données

### PostgreSQL Async
- Utiliser asyncpg pour les connexions PostgreSQL
- Implémenter la logique métier dans la couche service
- Éviter le SQL brut dans le code applicatif

### Gestion des Connexions
- Pool de connexions approprié
- Gestion des transactions pour la cohérence des données
- Gestion d'erreur pour les échecs de connexion

## 📊 Standards de Logging

### Logging Structuré
- Utiliser `logging` pour les logs formatés JSON
- Inclure le contexte pertinent dans les messages de log
- Différents niveaux de log pour différents environnements

### Niveaux de Log
- `DEBUG`: Informations détaillées de debugging
- `INFO`: Messages opérationnels généraux
- `WARNING`: Conditions d'avertissement
- `ERROR`: Conditions d'erreur
- `CRITICAL`: Erreurs critiques nécessitant attention immédiate

## 🔒 Considérations Sécurité

### Validation des Inputs
- Valider toutes les entrées utilisateur
- Sanitiser les données avant traitement
- Utiliser des requêtes paramétrées pour les opérations DB

### Authentification/Autorisation
- Implémenter des mécanismes d'auth appropriés
- Utiliser le contrôle d'accès basé sur les rôles si nécessaire
- Sécuriser la configuration sensible avec les variables d'environnement

## 🎯 Patterns TwisterLab Spécifiques

### Agent Execute Pattern
```python
async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute l'agent avec gestion d'erreur standardisée."""
    try:
        # Logique métier ici
        result = await self._perform_work(context)

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

### Gestion Métriques Prometheus
```python
from agents.metrics import track_agent_execution

@track_agent_execution
async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    # Les métriques sont automatiquement trackées
    pass
```

### Tests Async Standard
```python
import pytest

@pytest.mark.asyncio
async def test_agent_execution():
    agent = RealMonitoringAgent()
    result = await agent.execute({"test": True})

    assert result["status"] == "success"
    assert result["agent"] == "RealMonitoringAgent"
    assert "data" in result
```
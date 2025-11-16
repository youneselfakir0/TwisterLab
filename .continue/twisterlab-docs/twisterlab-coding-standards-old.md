---
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

### API Structure

- Routes organized by domain in `agents/api/routes_*.py`
- Automatic OpenAPI docs available at `/docs`
- Use dependency injection for shared services

### Request/Response Models

- Define Pydantic models for all API inputs/outputs
- Use proper validation with field constraints
- Include example data in schema documentation

## Agent Development

### Agent Inheritance

- All agents must inherit from `TwisterAgent` in `agents/base.py`
- Implement required abstract methods
- Follow the standard constructor pattern with name, display_name, description, etc.

### Swarm Communication

- Use `SwarmMessenger` for inter-agent communication via Redis pub/pub
- Implement proper message serialization/deserialization
- Handle message timeouts and retries

## Testing Standards

### Test Coverage

- **Minimum 80% coverage** enforced
- Use `pytest` with shared fixtures in `tests/conftest.py`
- Write integration tests for end-to-end flows

### Test Organization

- Test files named `test_{component}.py`
- Use descriptive test names and docstrings
- Mock external services for unit tests

## Code Quality Tools

### Linting and Formatting

- **ruff**: Primary linter with fast performance
- **black**: Code formatting (line length 88)
- **mypy**: Static type checking

### Pre-commit Hooks

- All quality checks run automatically
- No commits allowed with failing checks

## Database Access

### Async SQLAlchemy

- Use async sessions from `agents/database/services.py`
- Implement business logic in service layer
- Avoid raw SQL in application code

### Connection Management

- Proper connection pooling
- Transaction management for data consistency
- Error handling for connection failures

## Logging Standards

### Structured Logging

- Use `structlog` for JSON-formatted logs
- Include relevant context in log messages
- Different log levels for different environments

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors requiring immediate attention

## Security Considerations

### Input Validation

- Validate all user inputs
- Sanitize data before processing
- Use parameterized queries for database operations

### Authentication/Authorization

- Implement proper auth mechanisms
- Use role-based access control where needed
- Secure sensitive configuration with environment variables

# TwisterLab Coding Standards

## Python Best Practices

### Type Hints (PEP 484)
- **Mandatory**: All functions, methods, and classes must have complete type hints
- Use `typing` module imports for complex types
- Example: `def execute(self, task: str, context: Dict[str, Any] = None) -> Any:`

### Docstrings
- **Required**: Google-style docstrings for all public functions and classes
- Include description, parameters, return types, and exceptions
- Example:
  ```python
  def execute_task(self, task_id: str) -> bool:
      """Execute a specific task by ID.

      Args:
          task_id: Unique identifier for the task

      Returns:
          True if execution successful, False otherwise

      Raises:
          TaskNotFoundError: If task_id doesn't exist
      """
  ```

### Async/Await Patterns
- **Preferred**: Use async functions for I/O operations and agent execution
- All agent `execute()` methods must be async
- Use `httpx` for async HTTP requests instead of `requests`

### Error Handling
- Use structured logging with `structlog` instead of print statements
- Catch specific exceptions, not bare `Exception`
- Log errors with context for debugging

## FastAPI Development

### API Structure
- Routes organized by domain in `agents/api/routes_*.py`
- Automatic OpenAPI docs available at `/docs`
- Use dependency injection for shared services

### Request/Response Models
- Define Pydantic models for all API inputs/outputs
- Use proper validation with field constraints
- Include example data in schema documentation

## Agent Development

### Agent Inheritance
- All agents must inherit from `TwisterAgent` in `agents/base.py`
- Implement required abstract methods
- Follow the standard constructor pattern with name, display_name, description, etc.

### Swarm Communication
- Use `SwarmMessenger` for inter-agent communication via Redis pub/sub
- Implement proper message serialization/deserialization
- Handle message timeouts and retries

## Testing Standards

### Test Coverage
- **Minimum 80% coverage** enforced
- Use `pytest` with shared fixtures in `tests/conftest.py`
- Write integration tests for end-to-end flows

### Test Organization
- Test files named `test_{component}.py`
- Use descriptive test names and docstrings
- Mock external services for unit tests

## Code Quality Tools

### Linting and Formatting
- **ruff**: Primary linter with fast performance
- **black**: Code formatting (line length 88)
- **mypy**: Static type checking

### Pre-commit Hooks
- All quality checks run automatically
- No commits allowed with failing checks

## Database Access

### Async SQLAlchemy
- Use async sessions from `agents/database/services.py`
- Implement business logic in service layer
- Avoid raw SQL in application code

### Connection Management
- Proper connection pooling
- Transaction management for data consistency
- Error handling for connection failures

## Logging Standards

### Structured Logging
- Use `structlog` for JSON-formatted logs
- Include relevant context in log messages
- Different log levels for different environments

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors requiring immediate attention

## Security Considerations

### Input Validation
- Validate all user inputs
- Sanitize data before processing
- Use parameterized queries for database operations

### Authentication/Authorization
- Implement proper auth mechanisms
- Use role-based access control where needed
- Secure sensitive configuration with environment variables

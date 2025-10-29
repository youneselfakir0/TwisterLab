# TwisterLab - Prochaines Étapes de Développement
## Contexte Complet du Projet

**Date**: 28 octobre 2025
**Projet**: TwisterLab - Système d'automatisation IT Helpdesk multi-agent
**Version**: 1.0.0-alpha.1
**État Actuel**: Phase 1 terminée (corrections maestro.py), Phase 2 à implémenter

### Architecture du Projet
TwisterLab est un système multi-agent utilisant FastAPI, PostgreSQL, Redis et le protocole MCP pour l'automatisation des helpdesks IT.

**Composants Principaux**:
- **Agents**: Classes spécialisées dans `agents/` (Classifier, Resolver, Desktop Commander)
- **API**: FastAPI dans `agents/api/main.py` avec routers pour tickets, agents, SOPs
- **Base de Données**: SQLAlchemy models dans `agents/database/models.py`, migrations Alembic
- **Orchestration**: Agent Maestro coordonne le routage des tâches

### État Actuel (Phase 1 Terminée ✅)
- ✅ maestro.py corrigé (9 erreurs de type annotations, exceptions, logging)
- ✅ Variable `requestor` nettoyée et utilisée dans les logs
- ✅ Tests d'intégration créés (6 tests) - PASSENT ✓
- ✅ Tests unitaires créés (19 tests) - À EXÉCUTER
- ✅ Routes API complétées (4 nouveaux endpoints)
- ✅ Documentation créée (3 fichiers MD)
- ✅ Script d'automatisation (run_all_tests.ps1)

### Technologies Utilisées
- **Backend**: Python 3.12, FastAPI, Uvicorn
- **Base de Données**: PostgreSQL, SQLAlchemy, Alembic
- **Tests**: pytest, pytest-asyncio, pytest-cov
- **Cache/État**: Redis
- **IA**: Ollama (local), modèles llama-3.2
- **Protocole**: MCP (Model Context Protocol)
- **Déploiement**: Docker, docker-compose

---

## 🚀 5 ÉTAPES À IMPLÉMENTER (PHASE 2)

### ÉTAPE 1: Installation des Dépendances (Priorité: CRITIQUE)
**Délai**: Immédiat (5 minutes)
**Critères de Succès**: Toutes les dépendances installées, aucun import error

#### Code à Exécuter:
```bash
# Vérifier Python
python --version  # Doit être 3.12+

# Installer les dépendances
pip install -r requirements.txt

# Vérifier les imports critiques
python -c "import fastapi, uvicorn, sqlalchemy, alembic, pytest, asyncpg"
```

#### Commandes PowerShell:
```powershell
# Vérifier Python
python --version

# Installer dépendances
pip install -r requirements.txt

# Vérifier imports
python -c "import fastapi, uvicorn, sqlalchemy, alembic, pytest, asyncpg"
```

**Résultat Attendu**:
```
Python 3.12.x
Requirement already satisfied: fastapi in c:\users\...\lib\site-packages (0.104.1)
# ... autres packages ...
# Aucun message d'erreur d'import
```

### ÉTAPE 2: Exécution des Tests (Priorité: HAUTE)
**Délai**: 15 minutes
**Critères de Succès**: Tous les tests passent (19 unitaires + 6 intégration)

#### Tests à Exécuter:
```bash
# Tests unitaires (19 tests)
pytest tests/unit/ -v --tb=short

# Tests d'intégration (6 tests)
pytest tests/integration/ -v --tb=short

# Tous les tests avec coverage
pytest --cov=agents --cov-report=html --cov-report=term-missing
```

#### Commandes PowerShell:
```powershell
# Tests unitaires
pytest tests/unit/ -v --tb=short

# Tests d'intégration
pytest tests/integration/ -v --tb=short

# Coverage complet
pytest --cov=agents --cov-report=html --cov-report=term-missing
```

**Résultat Attendu**:
```
======================== 25 passed, 0 failed, 0 errors ========================
Coverage: 85% (minimum acceptable: 80%)
```

### ÉTAPE 3: Test de l'API REST (Priorité: MOYENNE)
**Délai**: 20 minutes
**Critères de Succès**: API démarre, endpoints répondent correctement

#### Démarrage de l'API:
```bash
# Démarrer l'API en mode développement
uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --reload

# Dans un autre terminal, tester les endpoints
curl http://localhost:8000/docs  # Documentation Swagger
curl http://localhost:8000/health  # Health check
```

#### Tests API Automatisés:
```python
# test_api_endpoints.py
import requests
import pytest

BASE_URL = "http://localhost:8000"

def test_api_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_ticket():
    ticket_data = {
        "subject": "Test ticket",
        "description": "Test description",
        "requestor": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/api/v1/tickets/", json=ticket_data)
    assert response.status_code == 201
    assert "id" in response.json()
```

### ÉTAPE 4: Création de la Documentation Technique (Priorité: FAIBLE)
**Délai**: 30 minutes
**Critères de Succès**: Documentation complète et à jour

#### Fichiers à Créer:
1. **MAESTRO_WORKFLOW.md**: Workflow détaillé de l'orchestrateur
2. **API_REFERENCE.md**: Référence complète des endpoints API
3. **DEPLOYMENT_GUIDE.md**: Guide de déploiement production

#### Contenu MAESTRO_WORKFLOW.md:
```markdown
# Workflow de l'Orchestrateur Maestro

## Vue d'Ensemble
L'agent Maestro orchestre le flux de travail IT helpdesk selon ces règles:

1. **Réception du Ticket** → Classification automatique
2. **Évaluation** → Priorité + Complexité + Confiance
3. **Routage**:
   - URGENT → Humain immédiatement
   - SIMPLE + Haute Confiance → Résolution automatique
   - COMPLEXE/Basse Confiance → Revue humaine

## Métriques Suivies
- Tickets traités automatiquement
- Temps de résolution moyen
- Taux d'escalade humain
- Santé des agents
```

### ÉTAPE 5: Implémentation MCP Desktop Commander (Priorité: FAIBLE)
**Délai**: 45 minutes
**Critères de Succès**: Agent Desktop Commander fonctionnel

#### Code de Base pour Desktop Commander:
```python
# agents/helpdesk/desktop_commander.py
from agents.base import TwisterAgent
import subprocess
import platform

class DesktopCommanderAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="desktop-commander",
            display_name="Desktop Commander",
            tools=[{
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a safe desktop command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "timeout": {"type": "integer", "default": 30}
                        },
                        "required": ["command"]
                    }
                }
            }],
            model="llama-3.2",
            temperature=0.1
        )

    async def execute_command(self, command: str, timeout: int = 30) -> dict:
        """Execute a safe desktop command."""
        try:
            # Security: whitelist of allowed commands
            allowed_commands = [
                "ipconfig", "ping", "tracert", "netstat",
                "systeminfo", "tasklist", "whoami"
            ]

            base_cmd = command.split()[0].lower()
            if base_cmd not in allowed_commands:
                return {
                    "status": "error",
                    "error": f"Command '{base_cmd}' not allowed"
                }

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Command timed out"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
```

---

## 📋 CHECKLIST FINALE DE VÉRIFICATION

### ✅ Vérifications Automatiques
```bash
# 1. Dépendances
python -c "import fastapi, uvicorn, sqlalchemy, asyncpg, pytest"

# 2. Tests
pytest --cov=agents --cov-fail-under=80

# 3. API
uvicorn agents.api.main:app --host 127.0.0.1 --port 8000 &
sleep 5
curl http://localhost:8000/health
kill %1

# 4. Base de données
alembic current  # Vérifier migrations
```

### ✅ Vérifications Manuelles
- [ ] API démarre sans erreur (`uvicorn agents.api.main:app --reload`)
- [ ] Documentation Swagger accessible (`http://localhost:8000/docs`)
- [ ] Création de ticket fonctionne (via Swagger ou curl)
- [ ] Orchestrateur route correctement les tickets
- [ ] Logs sont générés correctement
- [ ] Base de données PostgreSQL accessible
- [ ] Redis fonctionne pour le cache

### ✅ Métriques de Succès
- **Coverage**: ≥ 80%
- **Tests**: 25/25 passent
- **Performance**: API répond en < 500ms
- **Fiabilité**: 0 erreurs de type en production

---

## 🔧 GUIDE DE DÉPANNAGE

### Erreur: ImportError
**Symptôme**: `ModuleNotFoundError: No module named 'asyncpg'`
**Solution**:
```bash
pip install asyncpg
# Ou pour Windows:
pip install asyncpg --no-binary asyncpg
```

### Erreur: Tests échouent
**Symptôme**: `pytest` trouve 0 tests
**Cause**: Tests pas dans le bon répertoire
**Solution**:
```bash
# Créer la structure de répertoires
mkdir -p tests/unit tests/integration

# Déplacer les tests
mv test_*.py tests/unit/
mv test_*_integration.py tests/integration/
```

### Erreur: API ne démarre pas
**Symptôme**: `uvicorn` échoue avec erreur de port
**Solution**:
```bash
# Tuer les processus sur le port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Ou changer de port
uvicorn agents.api.main:app --port 8001
```

### Erreur: Base de données indisponible
**Symptôme**: `ConnectionError` PostgreSQL
**Solution**:
```bash
# Vérifier Docker
docker ps

# Redémarrer les services
docker-compose down
docker-compose up -d

# Attendre que PostgreSQL soit prêt
sleep 10
alembic upgrade head
```

### Erreur: Coverage trop basse
**Symptôme**: Coverage < 80%
**Solution**:
```bash
# Identifier les fichiers non couverts
pytest --cov=agents --cov-report=html
start htmlcov/index.html  # Ouvrir le rapport

# Ajouter des tests pour les lignes manquées
# Cible: agents/orchestrator/maestro.py (lignes 450-500)
```

### Erreur: Commandes Desktop non autorisées
**Symptôme**: Desktop Commander refuse les commandes
**Solution**: Ajouter la commande à la whitelist dans `desktop_commander.py`
```python
allowed_commands = [
    "ipconfig", "ping", "tracert", "netstat",
    "systeminfo", "tasklist", "whoami",
    "nslookup", "route", "arp"  # Ajouter ici
]
```

---

## 🎯 COMMANDES BASH/POWERSHELL À EXÉCUTER

### Installation Complète (One-liner):
```bash
# Linux/Mac
pip install -r requirements.txt && pytest --cov=agents --cov-fail-under=80 && uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --reload

# Windows PowerShell
pip install -r requirements.txt; pytest --cov=agents --cov-fail-under=80; uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Démarrage Complet du Système:
```bash
# Terminal 1: Base de données
docker-compose up -d

# Terminal 2: API
uvicorn agents.api.main:app --reload

# Terminal 3: Tests continus
pytest-watch --cov=agents --cov-report=term-missing
```

### Nettoyage Complet:
```bash
# Arrêter tout
docker-compose down
pkill -f uvicorn
pkill -f pytest

# Nettoyer cache Python
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Réinitialiser base de données
alembic downgrade base
alembic upgrade head
```

---

## 📊 MÉTRIQUES ET MONITORING

### Métriques à Surveiller:
- **Performance API**: Latence moyenne < 500ms
- **Coverage Tests**: > 80%
- **Taux de Succès**: > 95% des tickets traités
- **Disponibilité**: 99.9% uptime

### Commandes de Monitoring:
```bash
# Métriques API
curl http://localhost:8000/metrics

# Health checks
curl http://localhost:8000/health

# Logs en temps réel
tail -f logs/twisterlab.log

# Status des agents
curl http://localhost:8000/api/v1/agents/status
```

---

## 🚀 PROCHAINES ACTIONS

Après avoir complété ces 5 étapes:

1. **Phase 3**: Intégration avec interfaces utilisateur
2. **Phase 4**: Déploiement en production
3. **Phase 5**: Optimisation et scaling

**Prochaine commande à exécuter**:
```bash
# Vérifier l'état actuel
python -c "import sys; print(f'Python: {sys.version}')"

# Installer et tester
pip install -r requirements.txt
pytest tests/unit/test_maestro.py -v
```

**Temps estimé pour Phase 2**: 2 heures
**Risques**: Dépendances manquantes, conflits de ports, configuration DB
**Mitigation**: Utiliser le script `run_all_tests.ps1` pour automatisation

---

*Ce document fait partie des instructions Copilot pour TwisterLab v1.0.0-alpha.1*

**Tâches**:
1. Installer les packages Python manquants:
   ```bash
   pip install asyncpg pytest pytest-asyncio
   ```

2. Vérifier que PostgreSQL fonctionne:
   ```bash
   docker ps | grep postgres
   ```

3. Tester la connexion à la base de données:
   ```bash
   python test_sops_api.py
   ```

**Critères de Succès**:
- [ ] Aucune erreur `No module named 'asyncpg'`
- [ ] Les tests de base de données passent avec succès
- [ ] Le fichier `requirements.txt` est mis à jour avec les nouvelles dépendances

---

### ÉTAPE 2: Exécuter les Tests Unitaires avec Pytest

**Objectif**: Valider le comportement de MaestroOrchestratorAgent avec 19 tests unitaires.

**Tâches**:
1. Exécuter les tests unitaires:
   ```bash
   pytest tests/unit/test_maestro.py -v --tb=short
   ```

2. Vérifier la couverture de code:
   ```bash
   pip install pytest-cov
   pytest tests/unit/test_maestro.py --cov=agents.orchestrator.maestro --cov-report=html
   ```

3. Analyser les résultats dans `htmlcov/index.html`

4. Si des tests échouent, corriger les erreurs dans `maestro.py`

**Critères de Succès**:
- [ ] Tous les 19 tests unitaires passent (100%)
- [ ] Couverture de code > 80% pour maestro.py
- [ ] Aucune régression introduite

**Fichiers à Modifier**:
- `tests/unit/test_maestro.py` - Ajouter plus de tests si nécessaire
- `agents/orchestrator/maestro.py` - Corriger les bugs détectés

---

### ÉTAPE 3: Tester l'API REST Localement

**Objectif**: Démarrer l'API FastAPI et tester tous les endpoints de l'orchestrateur.

**Tâches**:

1. **Démarrer le serveur API**:
   ```bash
   cd C:\TwisterLab
   uvicorn agents.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Tester les endpoints avec curl ou Postman**:

   **A) Process Ticket** (Traitement complet d'un ticket):
   ```bash
   curl -X POST http://localhost:8000/api/v1/orchestrator/process-ticket \
     -H "Content-Type: application/json" \
     -d '{
       "ticket_id": "TEST-001",
       "ticket_data": {
         "subject": "Password reset needed",
         "description": "I forgot my Active Directory password",
         "requestor_email": "john.doe@example.com",
         "priority": "high"
       }
     }'
   ```

   **B) Agent Status** (Statut des agents):
   ```bash
   curl http://localhost:8000/api/v1/orchestrator/agents/status?include_health=true
   ```

   **C) Metrics** (Métriques de performance):
   ```bash
   curl http://localhost:8000/api/v1/orchestrator/metrics
   ```

   **D) Rebalance** (Rééquilibrage de charge):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/orchestrator/rebalance?strategy=round_robin"
   ```

   **E) Get Results** (Résultats pour un ticket):
   ```bash
   curl http://localhost:8000/api/v1/orchestrator/results/TEST-001
   ```

3. **Créer un script de test automatisé**:
   Créer le fichier `test_api_endpoints.py`:
   ```python
   import requests
   import json

   BASE_URL = "http://localhost:8000/api/v1/orchestrator"

   def test_all_endpoints():
       # Test 1: Process ticket
       print("Test 1: Process Ticket...")
       response = requests.post(f"{BASE_URL}/process-ticket", json={
           "ticket_id": "API-TEST-001",
           "ticket_data": {
               "subject": "Password reset",
               "description": "Need password reset",
               "requestor_email": "test@example.com"
           }
       })
       print(f"Status: {response.status_code}")
       print(json.dumps(response.json(), indent=2))

       # Test 2: Agent status
       print("\nTest 2: Agent Status...")
       response = requests.get(f"{BASE_URL}/agents/status?include_health=true")
       print(json.dumps(response.json(), indent=2))

       # Test 3: Metrics
       print("\nTest 3: Metrics...")
       response = requests.get(f"{BASE_URL}/metrics")
       print(json.dumps(response.json(), indent=2))

   if __name__ == "__main__":
       test_all_endpoints()
   ```

**Critères de Succès**:
- [ ] L'API démarre sans erreur sur le port 8000
- [ ] La page Swagger est accessible à http://localhost:8000/docs
- [ ] Tous les 5 endpoints répondent avec status 200
- [ ] Les réponses JSON sont valides et contiennent les données attendues

---

### ÉTAPE 4: Créer la Documentation Technique Complète

**Objectif**: Documenter l'architecture Maestro pour les développeurs futurs.

**Tâches**:

1. **Créer `docs/MAESTRO_WORKFLOW.md`**:
   - Diagramme du workflow de routing
   - Règles de routage détaillées
   - Exemples de tickets et leurs chemins de traitement
   - Documentation des métriques

2. **Créer `docs/API_ORCHESTRATOR.md`**:
   - Documentation complète de tous les endpoints
   - Exemples de requêtes/réponses
   - Codes d'erreur et leur signification
   - Guide de dépannage

3. **Créer `docs/TESTING_GUIDE.md`**:
   - Comment exécuter les tests unitaires
   - Comment exécuter les tests d'intégration
   - Comment ajouter de nouveaux tests
   - Stratégie de couverture de code

**Template pour `docs/MAESTRO_WORKFLOW.md`**:
```markdown
# Maestro Orchestrator - Workflow Documentation

## Architecture Overview

Le Maestro Orchestrator est le cerveau central de TwisterLab. Il route les tickets vers les agents appropriés basé sur la classification intelligente.

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│              INCOMING TICKET                            │
│  (ID, Subject, Description, Requestor, Priority)        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                  MAESTRO ORCHESTRATOR                   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  STEP 1: CLASSIFICATION                          │  │
│  │  → TicketClassifierAgent.execute()               │  │
│  │  → Returns: category, priority, complexity,      │  │
│  │              confidence                           │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                     │
│                   ▼                                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  STEP 2: ROUTING DECISION                        │  │
│  │  Based on classification results                 │  │
│  └────────┬─────────────┬──────────────┬─────────────┘  │
│           │             │              │                │
│     ┌─────▼─────┐  ┌────▼────┐  ┌─────▼──────┐        │
│     │  URGENT   │  │ SIMPLE  │  │  COMPLEX   │        │
│     │ priority  │  │conf>0.8 │  │ OR conf<0.6│        │
│     └─────┬─────┘  └────┬────┘  └─────┬──────┘        │
│           │             │              │                │
│           ▼             ▼              ▼                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  STEP 3: ROUTE TO AGENT                          │  │
│  └──────┬────────────┬──────────────┬────────────────┘  │
│         │            │              │                   │
└─────────┼────────────┼──────────────┼───────────────────┘
          │            │              │
          ▼            ▼              ▼
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │  HUMAN  │  │  AUTO    │  │  HUMAN   │
    │  AGENT  │  │ RESOLVER │  │ REVIEW   │
    └─────────┘  └──────────┘  └──────────┘
```

## Routing Rules

| Priority | Complexity | Confidence | Action                      | Agent                    |
|----------|-----------|------------|----------------------------|--------------------------|
| URGENT   | *         | *          | Escalate immediately       | Human (senior_helpdesk)  |
| *        | SIMPLE    | > 0.8      | Auto-resolve               | HelpdeskResolverAgent    |
| *        | COMPLEX   | *          | Human review               | Human (senior_helpdesk)  |
| *        | MODERATE  | > 0.6      | Auto-resolve (supervised)  | HelpdeskResolverAgent    |
| *        | *         | < 0.6      | Human review               | Human (senior_helpdesk)  |

## Example Tickets

### Example 1: Password Reset (Auto-resolved)
**Input**:
```json
{
  "ticket_id": "PASS-001",
  "subject": "Password reset",
  "description": "I forgot my password",
  "requestor": "user@example.com"
}
```

**Classification**:
- Category: password
- Priority: high
- Complexity: simple
- Confidence: 0.9

**Routing Decision**: Auto-resolve (confidence > 0.8, complexity = simple)

**Result**: HelpdeskResolverAgent executes SOP for password reset

---

### Example 2: Server Down (Escalated)
**Input**:
```json
{
  "ticket_id": "URGENT-001",
  "subject": "URGENT: Production server down",
  "description": "Critical failure",
  "requestor": "admin@example.com"
}
```

**Classification**:
- Category: urgent
- Priority: urgent
- Complexity: complex
- Confidence: 0.95

**Routing Decision**: Escalate to human (priority = urgent)

**Result**: Ticket sent to senior_helpdesk with estimated response time 30 minutes

## Performance Metrics

Le Maestro track les métriques suivantes:

- `tickets_processed`: Total tickets traités
- `auto_resolved`: Tickets résolus automatiquement (succès)
- `escalated_to_human`: Tickets escaladés à un humain
- `average_resolution_time`: Temps moyen de résolution
- `agent_failures`: Nombre d'échecs d'agents

## API Endpoints

Voir [API_ORCHESTRATOR.md](./API_ORCHESTRATOR.md) pour la documentation complète des endpoints.
```

**Critères de Succès**:
- [ ] 3 fichiers de documentation créés dans `docs/`
- [ ] Diagrammes d'architecture inclus
- [ ] Exemples de code fonctionnels
- [ ] Guide de dépannage complet

---

### ÉTAPE 5: Implémenter l'Intégration MCP pour Desktop Commander

**Objectif**: Connecter le Desktop Commander aux vrais clients via le protocole MCP (Model Context Protocol).

**Contexte**: Actuellement, Desktop Commander utilise des simulations. Il faut implémenter les vraies connexions MCP pour exécuter des commandes sur les postes à distance.

**Tâches**:

1. **Créer le serveur MCP pour Desktop Commander**:

   Créer `agents/mcp/desktop_commander_server.py`:
   ```python
   """
   MCP Server for Desktop Commander
   Permet aux agents d'exécuter des commandes sur les postes clients
   """
   import asyncio
   import logging
   from typing import Dict, Any, Optional

   logger = logging.getLogger(__name__)

   class DesktopCommanderMCPServer:
       """Serveur MCP pour la gestion des clients Desktop Commander"""

       def __init__(self):
           self.connected_clients: Dict[str, Dict[str, Any]] = {}
           self.command_whitelist = {
               "systeminfo", "ipconfig", "ping", "tracert",
               "nslookup", "gpupdate", "whoami", "hostname"
           }

       async def register_client(self, device_id: str, metadata: Dict[str, Any]):
           """Enregistre un nouveau client Desktop Commander"""
           self.connected_clients[device_id] = {
               "device_id": device_id,
               "status": "connected",
               "last_seen": asyncio.get_event_loop().time(),
               **metadata
           }
           logger.info(f"Client registered: {device_id}")

       async def execute_command(
           self,
           device_id: str,
           command: str,
           timeout: int = 300
       ) -> Dict[str, Any]:
           """Exécute une commande sur un client distant"""

           # Vérifier que le client est connecté
           if device_id not in self.connected_clients:
               return {
                   "status": "error",
                   "error": f"Client {device_id} not connected"
               }

           # Vérifier la whitelist
           command_base = command.split()[0].lower()
           if command_base not in self.command_whitelist:
               return {
                   "status": "denied",
                   "error": f"Command {command_base} not in whitelist"
               }

           # TODO: Implémenter la vraie exécution via MCP
           # Pour l'instant, retourne une simulation
           logger.info(f"Executing command on {device_id}: {command}")

           return {
               "status": "success",
               "device_id": device_id,
               "command": command,
               "output": f"Simulated output for: {command}",
               "execution_time": 2.5
           }
   ```

2. **Modifier Desktop Commander pour utiliser MCP**:

   Dans `agents/helpdesk/desktop_commander.py`, remplacer les fonctions de simulation par des appels MCP réels.

3. **Créer le client MCP**:

   Créer `agents/mcp/client.py` pour permettre aux agents de communiquer avec le serveur MCP.

4. **Tester l'intégration**:
   ```bash
   python test_mcp_integration.py
   ```

**Critères de Succès**:
- [ ] Serveur MCP démarre sans erreur
- [ ] Desktop Commander peut enregistrer des clients
- [ ] Commandes de la whitelist s'exécutent avec succès
- [ ] Les commandes non autorisées sont bloquées
- [ ] Tests d'intégration MCP passent

---

## 🎯 PRIORITÉS D'EXÉCUTION

**CETTE SEMAINE** (Critique):
1. ✅ ÉTAPE 1: Installer dépendances
2. ✅ ÉTAPE 2: Exécuter tests pytest
3. ✅ ÉTAPE 3: Tester API REST

**SEMAINE PROCHAINE** (Important):
4. ÉTAPE 4: Créer documentation
5. ÉTAPE 5: Implémenter MCP

---

## 📋 CHECKLIST FINALE

Avant de considérer cette phase complète, vérifie que:

- [ ] Toutes les dépendances Python sont installées
- [ ] PostgreSQL fonctionne et les migrations sont appliquées
- [ ] 19 tests unitaires passent (pytest)
- [ ] 6 tests d'intégration passent
- [ ] L'API FastAPI démarre sans erreur
- [ ] Tous les endpoints orchestrator répondent correctement
- [ ] La documentation technique est créée (3 fichiers MD)
- [ ] Le serveur MCP est implémenté
- [ ] Les commandes Desktop Commander fonctionnent via MCP

---

## 🚀 COMMANDES RAPIDES

```bash
# Installation complète
pip install -r requirements.txt
pip install asyncpg pytest pytest-asyncio pytest-cov

# Tests
pytest tests/unit/test_maestro.py -v
python test_maestro_integration.py

# Démarrer API
uvicorn agents.api.main:app --reload --port 8000

# Tester API
curl http://localhost:8000/api/v1/orchestrator/agents/status
curl http://localhost:8000/api/v1/orchestrator/metrics

# Couverture de code
pytest tests/unit/test_maestro.py --cov=agents.orchestrator.maestro --cov-report=html
```

---

## ⚠️ NOTES IMPORTANTES

1. **Erreur asyncpg**: Cette erreur est normale si asyncpg n'est pas installé. Installer avec `pip install asyncpg`.

2. **Tests qui échouent**: Si des tests pytest échouent, vérifier:
   - Les imports sont corrects
   - PostgreSQL est démarré
   - Les migrations Alembic sont appliquées

3. **API ne démarre pas**: Vérifier que le port 8000 n'est pas déjà utilisé:
   ```bash
   netstat -ano | findstr :8000
   ```

4. **MCP Protocol**: Le protocole MCP 2024-11-05 est utilisé pour la communication agents↔clients.

---

## 📚 RESSOURCES

- Documentation FastAPI: https://fastapi.tiangolo.com/
- Documentation pytest: https://docs.pytest.org/
- MCP Protocol: Voir `.github/copilot-instructions.md`
- Architecture TwisterLab: Voir `docs/ARCHITECTURE.md` (à créer)

---

**BONNE CHANCE! 🚀**

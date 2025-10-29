# Guide de Tests - TwisterLab

## Vue d'Ensemble

TwisterLab utilise une stratégie de tests multi-niveaux pour assurer la qualité du code:

1. **Tests Unitaires** (pytest) - Tests isolés des fonctions et méthodes
2. **Tests d'Intégration** - Tests end-to-end du workflow complet
3. **Tests API** - Tests des endpoints REST
4. **Tests de Charge** (future) - Tests de performance sous charge

---

## Tests Unitaires avec Pytest

### Installation

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Exécution

```bash
# Tous les tests unitaires
pytest tests/unit/test_maestro.py -v

# Test spécifique
pytest tests/unit/test_maestro.py::test_route_urgent_ticket_to_human -v

# Avec couverture de code
pytest tests/unit/test_maestro.py --cov=agents.orchestrator.maestro --cov-report=html

# Mode verbose avec traceback détaillé
pytest tests/unit/test_maestro.py -v --tb=long

# Arrêter au premier échec
pytest tests/unit/test_maestro.py -x

# Mode parallèle (plus rapide)
pytest tests/unit/test_maestro.py -n auto
```

### Structure des Tests

**Fichier**: `tests/unit/test_maestro.py`

**Organisation**:
```python
import pytest
from agents.orchestrator.maestro import MaestroOrchestratorAgent

@pytest.fixture
def maestro():
    """Fixture pour créer une instance de Maestro"""
    return MaestroOrchestratorAgent()

@pytest.mark.asyncio
async def test_initialization(maestro):
    """Test que Maestro s'initialise correctement"""
    assert maestro.name == "maestro-orchestrator"
    assert len(maestro.available_agents) == 3
```

### Tests Disponibles (18 tests)

| Test | Description | Cible |
|------|-------------|-------|
| `test_maestro_initialization` | Vérification initialisation | Maestro __init__ |
| `test_route_urgent_ticket_to_human` | Ticket URGENT → Escalade | Routing logic |
| `test_route_password_ticket` | Ticket password → Classification | Classifier |
| `test_route_software_ticket` | Ticket software → Classification | Classifier |
| `test_get_agent_status` | Récupération statut agents | Status endpoint |
| `test_get_agent_status_without_health` | Statut sans health metrics | Status endpoint |
| `test_rebalance_load` | Rééquilibrage de charge | Load balancer |
| `test_get_metrics` | Récupération métriques | Metrics tracking |
| `test_metrics_update_after_ticket` | Mise à jour métriques | Metrics update |
| `test_route_ticket_without_context` | Erreur sans contexte | Error handling |
| `test_route_ticket_without_ticket_id` | Erreur sans ticket_id | Validation |
| `test_is_agent_available` | Vérification disponibilité | Availability check |
| `test_ticket_priority_enum` | Enum TicketPriority | Data models |
| `test_ticket_complexity_enum` | Enum TicketComplexity | Data models |
| `test_execute_with_route_ticket_operation` | execute() route_ticket | Execute method |
| `test_execute_with_get_agent_status_operation` | execute() get_agent_status | Execute method |
| `test_execute_with_rebalance_operation` | execute() rebalance | Execute method |
| `test_execute_with_unknown_operation` | execute() unknown op | Error handling |

### Couverture de Code

**Objectif**: > 80% de couverture

**Génération du rapport**:
```bash
pytest tests/unit/test_maestro.py --cov=agents.orchestrator.maestro --cov-report=html
```

**Visualiser le rapport**:
```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

**Résultats attendus**:
```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
agents/orchestrator/maestro.py      250     38    85%
-----------------------------------------------------
TOTAL                               250     38    85%
```

---

## Tests d'Intégration

### Fichier Principal

**Fichier**: `test_maestro_integration.py`

### Exécution

```bash
# Exécution simple
python test_maestro_integration.py

# Avec capture des logs
python test_maestro_integration.py 2>&1 | tee test_results.log
```

### Tests Disponibles (6 tests)

#### Test 1: Password Reset
```python
# Input
{
    "ticket_id": "TICKET-001",
    "subject": "Password reset required",
    "description": "User forgot password and needs reset for Active Directory account",
    "requestor": "john.doe@example.com"
}

# Output attendu
{
    "status": "auto_resolved" ou "escalated_to_human",
    "classification": {
        "category": "password",
        "priority": "high",
        "complexity": "simple",
        "confidence": 0.9
    }
}
```

#### Test 2: Urgent Ticket
```python
# Input
{
    "ticket_id": "TICKET-002",
    "subject": "URGENT: Production server down",
    "description": "Critical server failure requires immediate attention",
    "requestor": "admin@example.com"
}

# Output attendu
{
    "status": "escalated_to_human",
    "reason": "urgent_priority",
    "recommended_agent": "senior_helpdesk",
    "estimated_response_time": "30 minutes"
}
```

#### Test 3: Software Installation
```python
# Input
{
    "ticket_id": "TICKET-003",
    "subject": "Install Microsoft Office",
    "description": "Need to install Office 365 on new laptop",
    "requestor": "jane.smith@example.com"
}

# Output attendu
{
    "status": "auto_resolved" ou "escalated_to_human",
    "classification": {
        "category": "software",
        "complexity": "moderate"
    }
}
```

#### Test 4: Access Request
```python
# Vérification du routing pour demande d'accès
```

#### Test 5: Agent Status
```python
# Vérification que tous les agents sont disponibles
# Validation des health metrics
```

#### Test 6: Load Balancing
```python
# Test des 3 stratégies de load balancing
```

### Résultat Attendu

```
============================================================
  TwisterLab - Maestro Orchestrator Integration Tests
============================================================

============================================================
  Test 1: Password Reset
============================================================
[OK] Status: auto_resolved
[OK] Ticket ID: TICKET-001
[OK] Category: password
[OK] Priority: high
[OK] Complexity: simple
[OK] Confidence: 0.9

...

============================================================
  Test Summary
============================================================
[OK] Total Tests Run: 6
[OK] All Tests Passed Successfully!
============================================================
```

---

## Tests API avec cURL

### Script de Test Complet

Créer un fichier `test_api_endpoints.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1/orchestrator"

echo "=== Test 1: Health Check ==="
curl -s http://localhost:8000/health | jq

echo -e "\n=== Test 2: Agent Status ==="
curl -s "$BASE_URL/agents/status?include_health=true" | jq

echo -e "\n=== Test 3: Metrics ==="
curl -s "$BASE_URL/metrics" | jq

echo -e "\n=== Test 4: Process Ticket ==="
curl -s -X POST "$BASE_URL/process-ticket" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "ticket_data": {
      "subject": "Password reset",
      "description": "Forgot password",
      "requestor_email": "test@example.com"
    }
  }' | jq

echo -e "\n=== Test 5: Rebalance ==="
curl -s -X POST "$BASE_URL/rebalance?strategy=round_robin" | jq

echo -e "\n=== Test 6: Get Results ==="
curl -s "$BASE_URL/results/TEST-001" | jq

echo -e "\n=== All Tests Completed ==="
```

**Exécution**:
```bash
chmod +x test_api_endpoints.sh
./test_api_endpoints.sh
```

---

## Tests avec Python Requests

### Script de Test

**Fichier**: `test_api_requests.py`

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/orchestrator"

def test_process_ticket():
    """Test traitement d'un ticket"""
    print("\n=== Test Process Ticket ===")

    payload = {
        "ticket_id": f"TEST-{datetime.now().timestamp()}",
        "ticket_data": {
            "subject": "Install Zoom",
            "description": "Need Zoom for remote meetings",
            "requestor_email": "user@company.com"
        }
    }

    response = requests.post(f"{BASE_URL}/process-ticket", json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    result = response.json()
    print(f"✓ Ticket ID: {result['ticket_id']}")
    print(f"✓ Status: {result['status']}")
    print(f"✓ Processing Time: {result['processing_time']}s")

    return result

def test_agent_status():
    """Test récupération du statut des agents"""
    print("\n=== Test Agent Status ===")

    response = requests.get(f"{BASE_URL}/agents/status", params={"include_health": True})

    assert response.status_code == 200

    result = response.json()
    print(f"✓ Overall Health: {result['overall_health']}")
    print(f"✓ Number of Agents: {len(result['agents'])}")

    for agent_name, agent_info in result['agents'].items():
        print(f"  - {agent_name}: {agent_info['status']} ({agent_info['load']}/{agent_info['max_load']})")

    return result

def test_metrics():
    """Test récupération des métriques"""
    print("\n=== Test Metrics ===")

    response = requests.get(f"{BASE_URL}/metrics")

    assert response.status_code == 200

    result = response.json()
    metrics = result['metrics']

    print(f"✓ Tickets Processed: {metrics['tickets_processed']}")
    print(f"✓ Auto Resolved: {metrics['auto_resolved']}")
    print(f"✓ Escalated: {metrics['escalated_to_human']}")

    if metrics['tickets_processed'] > 0:
        auto_rate = (metrics['auto_resolved'] / metrics['tickets_processed']) * 100
        print(f"✓ Auto-Resolution Rate: {auto_rate:.1f}%")

    return metrics

def test_rebalance():
    """Test rééquilibrage de charge"""
    print("\n=== Test Rebalance ===")

    strategies = ["round_robin", "least_loaded", "priority_based"]

    for strategy in strategies:
        response = requests.post(
            f"{BASE_URL}/rebalance",
            params={"strategy": strategy}
        )

        assert response.status_code == 200

        result = response.json()
        print(f"✓ Strategy '{strategy}': {result['agents_adjusted']} agents adjusted")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("  TwisterLab API Tests")
        print("=" * 60)

        test_agent_status()
        test_metrics()
        test_process_ticket()
        test_rebalance()

        print("\n" + "=" * 60)
        print("  All Tests Passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API. Is the server running?")
        print("   Start with: uvicorn agents.api.main:app --reload")
```

**Exécution**:
```bash
python test_api_requests.py
```

---

## Automatisation avec PowerShell

### Script Complet

**Fichier**: `run_all_tests.ps1`

Déjà créé! Utilisation:

```powershell
.\run_all_tests.ps1
```

**Ce script fait**:
1. ✓ Vérifie Python
2. ✓ Vérifie les dépendances
3. ✓ Vérifie PostgreSQL
4. ✓ Exécute pytest (18 tests unitaires)
5. ✓ Exécute tests d'intégration (6 tests)
6. ✓ Affiche un résumé coloré

---

## Continuous Integration (CI/CD)

### GitHub Actions

**Fichier**: `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run pytest
        run: |
          pytest tests/unit/test_maestro.py -v --cov

      - name: Run integration tests
        run: |
          python test_maestro_integration.py

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Tests de Charge (Future)

### Avec Locust

**Fichier**: `locustfile.py`

```python
from locust import HttpUser, task, between

class OrchestratorUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def process_ticket(self):
        self.client.post("/api/v1/orchestrator/process-ticket", json={
            "ticket_id": f"LOAD-{self.environment.runner.user_count}",
            "ticket_data": {
                "subject": "Load test ticket",
                "description": "Testing under load",
                "requestor_email": "loadtest@example.com"
            }
        })

    @task(1)
    def get_metrics(self):
        self.client.get("/api/v1/orchestrator/metrics")
```

**Exécution**:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## Bonnes Pratiques

### 1. Écrire des Tests Maintenables

```python
# ✓ BON: Test isolé et clair
@pytest.mark.asyncio
async def test_route_urgent_ticket_to_human(maestro):
    """Test qu'un ticket URGENT est escaladé immédiatement"""
    context = {"ticket_id": "URGENT-001", "subject": "URGENT: Server down"}
    result = await maestro.route_ticket(context)
    assert result["status"] == "escalated_to_human"

# ✗ MAUVAIS: Test trop large
async def test_everything(maestro):
    # Teste trop de choses à la fois
    result1 = await maestro.route_ticket(...)
    result2 = await maestro.get_metrics()
    # ...
```

### 2. Utiliser des Fixtures

```python
@pytest.fixture
async def sample_ticket():
    """Fixture pour un ticket de test"""
    return {
        "ticket_id": "TEST-001",
        "subject": "Test ticket",
        "description": "Testing",
        "requestor": "test@example.com"
    }

@pytest.mark.asyncio
async def test_with_fixture(maestro, sample_ticket):
    result = await maestro.route_ticket(sample_ticket)
    assert result["status"] is not None
```

### 3. Mocker les Dépendances Externes

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock(maestro):
    with patch('agents.orchestrator.maestro.TicketClassifierAgent') as mock_classifier:
        mock_classifier.return_value.execute = AsyncMock(return_value={
            "classification": {"category": "password"}
        })

        result = await maestro.route_ticket({"ticket_id": "MOCK-001"})
        assert result is not None
```

---

## Dépannage

### Les tests pytest échouent

**Problème**: `ModuleNotFoundError: No module named 'agents'`

**Solution**:
```bash
# Ajouter le répertoire au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou installer en mode développement
pip install -e .
```

### PostgreSQL n'est pas disponible

**Problème**: `InterfaceError: cannot perform operation: another operation is in progress`

**Solution**:
```bash
# Redémarrer PostgreSQL
docker-compose restart postgres

# Vérifier qu'il fonctionne
docker ps | grep postgres
```

### Tests d'intégration échouent

**Problème**: Erreur asyncpg

**Solution**:
```bash
pip install asyncpg
```

---

## Checklist de Tests

Avant de merger du code:

- [ ] Tous les tests pytest passent (18/18)
- [ ] Tous les tests d'intégration passent (6/6)
- [ ] Couverture de code > 80%
- [ ] Aucun warning pendant les tests
- [ ] Tests API passent
- [ ] Documentation mise à jour

---

**Version**: 1.0.0
**Dernière mise à jour**: 2025-10-28

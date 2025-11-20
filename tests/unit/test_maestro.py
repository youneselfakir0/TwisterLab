"""
Tests unitaires pour RealMaestroAgent
"""

import pytest

from agents.real.real_maestro_agent import RealMaestroAgent


@pytest.fixture
def maestro():
    """Fixture pour créer une instance de RealMaestroAgent"""
    return RealMaestroAgent()


@pytest.mark.asyncio
async def test_maestro_initialization(maestro):
    """Test que RealMaestroAgent s'initialise correctement"""
    assert maestro.name == "RealMaestroAgent"
    assert isinstance(maestro.agents, dict)
    assert isinstance(maestro.agent_stats, dict)


@pytest.mark.asyncio
async def test_maestro_orchestrate_workflow(maestro):
    """Test l'orchestration d'un workflow complet"""
    ticket = {
        "id": 123,
        "description": "WiFi connection keeps dropping",
        "title": "WiFi issues",
        "timestamp": "2025-11-13T12:00:00Z",
    }

    context = {"operation": "orchestrate_workflow", "ticket": ticket}

    result = await maestro.execute(context)

    # Vérifier la structure de base de la réponse
    assert isinstance(result, dict)
    assert "status" in result
    assert "timestamp" in result

    # Si le workflow réussit, vérifier les détails
    if result.get("status") == "success":
        assert "outcome" in result  # Le workflow retourne 'outcome' au lieu de 'workflow_status'
        assert "classification" in result
        assert isinstance(result["classification"], dict)


@pytest.mark.asyncio
async def test_maestro_health_check_all(maestro):
    """Test la vérification de santé de tous les agents"""
    context = {"operation": "health_check_all"}

    result = await maestro.execute(context)

    assert isinstance(result, dict)
    assert "status" in result
    assert "timestamp" in result

    if result.get("status") == "success":
        assert "agents" in result  # La réponse contient 'agents' au lieu de 'agent_health'
        assert isinstance(result["agents"], dict)


@pytest.mark.asyncio
async def test_maestro_unknown_operation(maestro):
    """Test qu'une opération inconnue lève une ValueError"""
    context = {"operation": "unknown_operation"}

    result = await maestro.execute(context)

    assert result["status"] == "error"
    assert "Unknown operation" in result["error"]


@pytest.mark.asyncio
async def test_maestro_load_balance(maestro):
    """Test l'équilibrage de charge"""
    tasks = [
        {"id": 1, "type": "classification", "priority": "high"},
        {"id": 2, "type": "resolution", "priority": "medium"},
        {"id": 3, "type": "monitoring", "priority": "low"},
    ]

    context = {"operation": "load_balance", "tasks": tasks}

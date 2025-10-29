"""
Tests unitaires pour MaestroOrchestratorAgent
"""
import pytest
from agents.orchestrator.maestro import (
    MaestroOrchestratorAgent,
    TicketPriority,
    TicketComplexity
)


@pytest.fixture
def maestro():
    """Fixture pour créer une instance de Maestro"""
    return MaestroOrchestratorAgent()


@pytest.mark.asyncio
async def test_maestro_initialization(maestro):
    """Test que Maestro s'initialise correctement"""
    assert maestro.name == "maestro-orchestrator"
    assert maestro.display_name == "Maestro Orchestrator"
    assert maestro.role == "orchestrator"
    assert len(maestro.available_agents) == 3
    assert "classifier" in maestro.available_agents
    assert "resolver" in maestro.available_agents
    assert "desktop_commander" in maestro.available_agents


@pytest.mark.asyncio
async def test_route_urgent_ticket_to_human(maestro):
    """Test qu'un ticket URGENT est escaladé immédiatement"""
    context = {
        "ticket_id": "URGENT-001",
        "subject": "URGENT: Serveur en panne",
        "description": "Le serveur de production est complètement down",
        "requestor": "admin@example.com"
    }

    result = await maestro.route_ticket(context)

    assert result["status"] == "escalated_to_human"
    assert result["reason"] == "urgent_priority"
    assert result["ticket_id"] == "URGENT-001"
    assert result["recommended_agent"] == "senior_helpdesk"


@pytest.mark.asyncio
async def test_route_password_ticket(maestro):
    """Test qu'un ticket de reset password est bien classifié"""
    context = {
        "ticket_id": "PASS-001",
        "subject": "Reset password",
        "description": "J'ai oublié mon mot de passe",
        "requestor": "user@example.com"
    }

    result = await maestro.route_ticket(context)

    # Le ticket devrait être classifié avec category=password
    assert result["ticket_id"] == "PASS-001"
    assert result["status"] in ["auto_resolved", "escalated_to_human"]
    if "classification" in result:
        assert result["classification"]["category"] == "password"


@pytest.mark.asyncio
async def test_route_software_ticket(maestro):
    """Test qu'un ticket d'installation software est bien classifié"""
    context = {
        "ticket_id": "SOFT-001",
        "subject": "Install Office",
        "description": "Need to install Microsoft Office on my laptop",
        "requestor": "user@example.com"
    }

    result = await maestro.route_ticket(context)

    assert result["ticket_id"] == "SOFT-001"
    if "classification" in result:
        assert result["classification"]["category"] == "software"


@pytest.mark.asyncio
async def test_get_agent_status(maestro):
    """Test la récupération du statut des agents"""
    result = await maestro.get_agent_status(include_health=True)

    assert result["status"] == "success"
    assert "agents" in result
    assert "classifier" in result["agents"]
    assert "resolver" in result["agents"]
    assert "desktop_commander" in result["agents"]

    # Vérifier que les health metrics sont présents
    classifier_info = result["agents"]["classifier"]
    assert "health_metrics" in classifier_info
    assert "response_time" in classifier_info["health_metrics"]
    assert "error_rate" in classifier_info["health_metrics"]
    assert "uptime" in classifier_info["health_metrics"]


@pytest.mark.asyncio
async def test_get_agent_status_without_health(maestro):
    """Test la récupération du statut sans health metrics"""
    result = await maestro.get_agent_status(include_health=False)

    assert result["status"] == "success"
    assert "agents" in result

    # Vérifier que les health metrics ne sont PAS présents
    classifier_info = result["agents"]["classifier"]
    assert "health_metrics" not in classifier_info


@pytest.mark.asyncio
async def test_rebalance_load(maestro):
    """Test le rééquilibrage de charge"""
    # Test avec round_robin
    result1 = await maestro.rebalance_load(strategy="round_robin")
    assert result1["status"] == "success"
    assert result1["strategy"] == "round_robin"
    assert result1["agents_adjusted"] == 3

    # Test avec least_loaded
    result2 = await maestro.rebalance_load(strategy="least_loaded")
    assert result2["status"] == "success"
    assert result2["strategy"] == "least_loaded"

    # Test avec priority_based
    result3 = await maestro.rebalance_load(strategy="priority_based")
    assert result3["status"] == "success"
    assert result3["strategy"] == "priority_based"


@pytest.mark.asyncio
async def test_get_metrics(maestro):
    """Test la récupération des métriques"""
    metrics = maestro.get_metrics()

    assert "tickets_processed" in metrics
    assert "auto_resolved" in metrics
    assert "escalated_to_human" in metrics
    assert "average_resolution_time" in metrics
    assert "agent_failures" in metrics

    # Les valeurs initiales devraient être 0
    assert metrics["tickets_processed"] >= 0
    assert metrics["auto_resolved"] >= 0
    assert metrics["escalated_to_human"] >= 0


@pytest.mark.asyncio
async def test_metrics_update_after_ticket(maestro):
    """Test que les métriques sont mises à jour après traitement d'un ticket"""
    initial_metrics = maestro.get_metrics()
    initial_escalated = initial_metrics["escalated_to_human"]

    # Traiter un ticket URGENT (qui sera escaladé)
    context = {
        "ticket_id": "METRIC-001",
        "subject": "URGENT: Critical issue",
        "description": "Urgent problem needs immediate attention",
        "requestor": "admin@example.com"
    }

    await maestro.route_ticket(context)

    # Vérifier que les métriques ont été mises à jour
    updated_metrics = maestro.get_metrics()
    assert updated_metrics["escalated_to_human"] == initial_escalated + 1


@pytest.mark.asyncio
async def test_route_ticket_without_context(maestro):
    """Test qu'une erreur est retournée si le contexte est vide"""
    result = await maestro.route_ticket(None)

    assert result["status"] == "error"
    assert "error" in result
    assert "Context required" in result["error"]


@pytest.mark.asyncio
async def test_route_ticket_without_ticket_id(maestro):
    """Test qu'une erreur est retournée si ticket_id manque"""
    context = {
        "subject": "Some subject",
        "description": "Some description"
    }

    result = await maestro.route_ticket(context)

    assert result["status"] == "error"
    assert "error" in result
    assert "ticket_id is required" in result["error"]


@pytest.mark.asyncio
async def test_is_agent_available(maestro):
    """Test la vérification de disponibilité des agents"""
    # Classifier devrait être disponible (load=0, max_load=10)
    assert maestro._is_agent_available("classifier") is True

    # Resolver devrait être disponible (load=0, max_load=5)
    assert maestro._is_agent_available("resolver") is True

    # Agent inexistant devrait retourner False
    assert maestro._is_agent_available("nonexistent") is False

    # Simuler un agent à pleine charge
    maestro.available_agents["classifier"]["load"] = 10
    assert maestro._is_agent_available("classifier") is False


@pytest.mark.asyncio
async def test_ticket_priority_enum():
    """Test que l'enum TicketPriority fonctionne correctement"""
    assert TicketPriority.LOW.value == "low"
    assert TicketPriority.MEDIUM.value == "medium"
    assert TicketPriority.HIGH.value == "high"
    assert TicketPriority.URGENT.value == "urgent"


@pytest.mark.asyncio
async def test_ticket_complexity_enum():
    """Test que l'enum TicketComplexity fonctionne correctement"""
    assert TicketComplexity.SIMPLE.value == "simple"
    assert TicketComplexity.MODERATE.value == "moderate"
    assert TicketComplexity.COMPLEX.value == "complex"


@pytest.mark.asyncio
async def test_execute_with_route_ticket_operation(maestro):
    """Test execute() avec l'opération route_ticket"""
    context = {
        "operation": "route_ticket",
        "ticket_id": "EXEC-001",
        "subject": "Test ticket",
        "description": "Testing execute method",
        "requestor": "test@example.com"
    }

    result = await maestro.execute("Route ticket", context)

    assert "orchestrator" in result
    assert result["orchestrator"] == "maestro"
    assert "timestamp" in result
    assert "status" in result


@pytest.mark.asyncio
async def test_execute_with_get_agent_status_operation(maestro):
    """Test execute() avec l'opération get_agent_status"""
    context = {
        "operation": "get_agent_status",
        "include_health": True
    }

    result = await maestro.execute("Get agent status", context)

    assert result["orchestrator"] == "maestro"
    assert result["status"] == "success"
    assert "agents" in result


@pytest.mark.asyncio
async def test_execute_with_rebalance_operation(maestro):
    """Test execute() avec l'opération rebalance_load"""
    context = {
        "operation": "rebalance_load",
        "strategy": "round_robin"
    }

    result = await maestro.execute("Rebalance load", context)

    assert result["orchestrator"] == "maestro"
    assert result["status"] == "success"
    assert result["strategy"] == "round_robin"


@pytest.mark.asyncio
async def test_execute_with_unknown_operation(maestro):
    """Test execute() avec une opération inconnue"""
    context = {
        "operation": "invalid_operation"
    }

    result = await maestro.execute("Unknown operation", context)

    assert result["orchestrator"] == "maestro"
    assert result["status"] == "error"
    assert "Unknown operation" in result["error"]

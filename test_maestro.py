import pytest

from agents.orchestrator.maestro import MaestroOrchestratorAgent


@pytest.mark.asyncio
async def test_maestro_basic_routing() -> None:
    agent = MaestroOrchestratorAgent()
    context = {
        "ticket_id": "T-001",
        "subject": "Problème de mot de passe",
        "description": "Impossible de se connecter à la messagerie.",
    }
    result = await agent.route_ticket(context)
    assert "status" in result
    assert result["status"] in ["auto_resolved", "escalated_to_human", "error"]

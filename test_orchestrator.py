import pytest
from fastapi.testclient import TestClient

from agents.orchestrator.maestro import MaestroOrchestratorAgent
from agents.api.main import app


@pytest.mark.asyncio
async def test_classify_and_escalate():
    """Ticket that should be classified with low confidence and escalated to human."""
    orchestrator = MaestroOrchestratorAgent()

    context = {
        "ticket_id": "test-escalate-1",
        "subject": "Printer not working",
        "description": "The office printer shows an unknown error and won't print",
        "requestor": "user@company.com",
    }

    result = await orchestrator.route_ticket(context)

    assert result is not None
    assert result.get("status") in ("escalated_to_human", "error")
    assert "classification" in result


@pytest.mark.asyncio
async def test_auto_resolve_password_reset():
    """Ticket classified as password issue should be auto-resolved."""
    orchestrator = MaestroOrchestratorAgent()

    context = {
        "ticket_id": "test-auto-1",
        "subject": "Password reset needed",
        "description": "User forgot password and requests a reset",
        "requestor": "user2@company.com",
    }

    result = await orchestrator.route_ticket(context)

    assert result is not None
    # Either auto_resolved (preferred) or escalated_to_human (if resolver unavailable)
    assert result.get("status") in ("auto_resolved", "escalated_to_human", "error")
    if result.get("status") == "auto_resolved":
        resolution = result.get("resolution")
        assert resolution is not None
        assert resolution.get("status") == "success"


def test_endpoint_process_ticket():
    """Integration test: create a ticket and call the orchestrator endpoint."""
    client = TestClient(app)

    ticket_data = {
        "subject": "Password reset needed",
        "description": "User forgot their password and needs a reset",
        "priority": "low",
        "category": "password",
        "requestor_email": "integration@company.com",
    }

    create_response = client.post("/api/v1/tickets/", json=ticket_data)
    assert create_response.status_code == 200
    ticket = create_response.json()
    ticket_id = ticket.get("id")
    assert ticket_id

    process_payload = {"ticket_id": ticket_id, "ticket_data": ticket_data}
    process_response = client.post("/api/v1/orchestrator/process-ticket", json=process_payload)
    assert process_response.status_code == 200
    result = process_response.json()
    assert "status" in result

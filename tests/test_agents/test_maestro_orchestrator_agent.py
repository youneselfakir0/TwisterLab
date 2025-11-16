"""
Tests for MaestroOrchestratorAgent.

Tests cover workflow orchestration, load balancing, performance monitoring,
and error handling scenarios.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.core.maestro_orchestrator_agent import MaestroOrchestratorAgent


@pytest.fixture
def maestro_agent():
    """Fixture for MaestroOrchestratorAgent instance."""
    return MaestroOrchestratorAgent()


@pytest.mark.asyncio
async def test_maestro_initialization(maestro_agent):
    """Test agent initializes correctly."""
    assert maestro_agent.name == "MaestroOrchestratorAgent"
    assert maestro_agent.priority == 1
    assert "workflow_orchestration" in maestro_agent.capabilities
    assert "load_balancing" in maestro_agent.capabilities
    assert isinstance(maestro_agent.registered_agents, dict)
    assert isinstance(maestro_agent.workflow_templates, dict)


@pytest.mark.asyncio
async def test_unknown_operation(maestro_agent):
    """Test handling of unknown operations."""
    context = {"operation": "unknown_operation"}

    with pytest.raises(ValueError, match="Unknown orchestration operation"):
        await maestro_agent.execute(context)


@pytest.mark.asyncio
async def test_missing_required_fields(maestro_agent):
    """Test validation of required context fields."""
    context = {}  # Missing operation

    with pytest.raises(ValueError, match="Missing required field: operation"):
        await maestro_agent.execute(context)


@pytest.mark.asyncio
async def test_unknown_workflow_template(maestro_agent):
    """Test handling of unknown workflow templates."""
    context = {"operation": "execute_workflow", "workflow_name": "unknown_workflow"}

    with pytest.raises(ValueError, match="Unknown workflow template"):
        await maestro_agent.execute(context)


import pytest


@pytest.fixture
def maestro_agent():
    """Fixture for MaestroOrchestratorAgent instance."""
    return MaestroOrchestratorAgent()


@pytest.fixture
def mock_agents():
    """Fixture for mock agents."""
    # Create mock agents with required attributes
    mock_classifier = MagicMock()
    mock_classifier.name = "TicketClassifierAgent"
    mock_classifier.capabilities = ["ticket_processing"]
    mock_classifier.execute = AsyncMock(
        return_value={"status": "success", "classification": "software"}
    )

    mock_resolver = MagicMock()
    mock_resolver.name = "ResolverAgent"
    mock_resolver.capabilities = ["issue_resolution"]
    mock_resolver.execute = AsyncMock(return_value={"status": "success", "resolution": "applied"})

    return {"classifier": mock_classifier, "resolver": mock_resolver}


@pytest.mark.asyncio
async def test_maestro_initialization(maestro_agent):
    """Test agent initializes correctly."""
    assert maestro_agent.name == "MaestroOrchestratorAgent"
    assert maestro_agent.priority == 1
    assert "workflow_orchestration" in maestro_agent.capabilities
    assert "load_balancing" in maestro_agent.capabilities
    assert isinstance(maestro_agent.registered_agents, dict)
    assert isinstance(maestro_agent.workflow_templates, dict)


@pytest.mark.asyncio
async def test_register_agents(maestro_agent, mock_agents):
    """Test agent registration functionality."""
    # Mock the imports to avoid actual agent instantiation
    with (
        patch(
            "agents.core.maestro_orchestrator_agent.TicketClassifierAgent",
            return_value=mock_agents["classifier"],
        ),
        patch(
            "agents.core.maestro_orchestrator_agent.ResolverAgent",
            return_value=mock_agents["resolver"],
        ),
        patch("agents.core.maestro_orchestrator_agent.DesktopCommanderAgent"),
        patch("agents.core.maestro_orchestrator_agent.SyncAgent"),
        patch("agents.core.maestro_orchestrator_agent.BackupAgent"),
        patch("agents.core.maestro_orchestrator_agent.MonitoringAgent"),
    ):
        context = {"operation": "register_agents"}
        result = await maestro_agent.execute(context)

        assert result["status"] == "success"
        assert "registered_agents" in result
        assert "workflow_templates" in result
        assert len(result["registered_agents"]) == 6  # All 6 agents
        assert (
            len(result["workflow_templates"]) == 3
        )  # ticket_resolution, system_backup, emergency_response


@pytest.mark.asyncio
async def test_execute_workflow_ticket_resolution(maestro_agent):
    """Test execution of ticket_resolution workflow."""
    # First register agents
    with (
        patch("agents.core.maestro_orchestrator_agent.TicketClassifierAgent"),
        patch("agents.core.maestro_orchestrator_agent.ResolverAgent"),
        patch("agents.core.maestro_orchestrator_agent.DesktopCommanderAgent"),
        patch("agents.core.maestro_orchestrator_agent.SyncAgent"),
        patch("agents.core.maestro_orchestrator_agent.BackupAgent"),
        patch("agents.core.maestro_orchestrator_agent.MonitoringAgent"),
    ):
        await maestro_agent.execute({"operation": "register_agents"})

        # Mock the actual agent executions
        maestro_agent.registered_agents["classifier"].execute = AsyncMock(
            return_value={
                "status": "success",
                "classification": {"category": "software", "priority": "medium"},
            }
        )
        maestro_agent.registered_agents["resolver"].execute = AsyncMock(
            return_value={"status": "success", "resolution": "applied"}
        )
        maestro_agent.registered_agents["sync"].execute = AsyncMock(
            return_value={"status": "success", "sync_result": "completed"}
        )
        maestro_agent.registered_agents["monitoring"].execute = AsyncMock(
            return_value={"status": "success", "health": "good"}
        )

        # Execute workflow
        context = {
            "operation": "execute_workflow",
            "workflow_name": "ticket_resolution",
            "workflow_context": {"ticket_id": "T-001"},
        }

        result = await maestro_agent.execute(context)

        assert result["status"] == "success"
        assert result["workflow_name"] == "ticket_resolution"
        assert result["workflow_status"] == "completed"
        assert len(result["results"]) >= 4  # At least classifier, resolver, sync, monitoring
        assert "execution_time" in result
        assert result["execution_time"] > 0


@pytest.mark.asyncio
async def test_load_balancing(maestro_agent):
    """Test load balancing functionality."""
    # Register agents first
    with (
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.TicketClassifierAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.ResolverAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.DesktopCommanderAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.SyncAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.BackupAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.MonitoringAgent"),
    ):
        await maestro_agent.execute({"operation": "register_agents"})

        context = {
            "operation": "load_balance",
            "agent_type": "ticket_processing",
            "task": "process",
        }

        result = await maestro_agent.execute(context)

        assert result["status"] == "success"
        assert "selected_agent" in result
        assert "available_agents" in result
        assert "load_distribution" in result


@pytest.mark.asyncio
async def test_performance_monitoring(maestro_agent):
    """Test performance monitoring functionality."""
    # Register agents first
    with (
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.TicketClassifierAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.ResolverAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.DesktopCommanderAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.SyncAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.BackupAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.MonitoringAgent"),
    ):
        await maestro_agent.execute({"operation": "register_agents"})

        # Mock get_metrics methods
        for agent in maestro_agent.registered_agents.values():
            agent.get_metrics = AsyncMock(return_value={"cpu": 45, "memory": 256})

        context = {"operation": "monitor_performance"}
        result = await maestro_agent.execute(context)

        assert result["status"] == "success"
        assert "performance_data" in result
        assert "system_metrics" in result
        assert len(result["performance_data"]) == 6  # All 6 agents


@pytest.mark.asyncio
async def test_workflow_failure_handling(maestro_agent):
    """Test workflow continues despite individual step failures."""
    # Register agents
    with (
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.TicketClassifierAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.ResolverAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.DesktopCommanderAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.SyncAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.BackupAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.MonitoringAgent"),
    ):
        await maestro_agent.execute({"operation": "register_agents"})

        # Make resolver fail
        maestro_agent.registered_agents["classifier"].execute = AsyncMock(
            return_value={"status": "success"}
        )
        maestro_agent.registered_agents["resolver"].execute = AsyncMock(
            side_effect=Exception("Resolution failed")
        )
        maestro_agent.registered_agents["sync"].execute = AsyncMock(
            return_value={"status": "success"}
        )

        context = {
            "operation": "execute_workflow",
            "workflow_name": "ticket_resolution",
            "workflow_context": {"ticket_id": "T-001"},
        }

        result = await maestro_agent.execute(context)

        assert result["status"] == "success"
        assert result["workflow_status"] == "failed"
        assert "failed_steps" in result
        assert len(result["failed_steps"]) > 0


@pytest.mark.asyncio
async def test_unknown_operation(maestro_agent):
    """Test handling of unknown operations."""
    context = {"operation": "unknown_operation"}

    with pytest.raises(ValueError, match="Unknown orchestration operation"):
        await maestro_agent.execute(context)


@pytest.mark.asyncio
async def test_missing_required_fields(maestro_agent):
    """Test validation of required context fields."""
    context = {}  # Missing operation

    with pytest.raises(ValueError, match="Missing required field: operation"):
        await maestro_agent.execute(context)


@pytest.mark.asyncio
async def test_unknown_workflow_template(maestro_agent):
    """Test handling of unknown workflow templates."""
    context = {"operation": "execute_workflow", "workflow_name": "unknown_workflow"}

    with pytest.raises(ValueError, match="Unknown workflow template"):
        await maestro_agent.execute(context)


@pytest.mark.asyncio
async def test_workflow_status_tracking(maestro_agent):
    """Test workflow status tracking and history."""
    # Register agents
    with (
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.TicketClassifierAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.ResolverAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.DesktopCommanderAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.SyncAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.BackupAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.MonitoringAgent"),
    ):
        await maestro_agent.execute({"operation": "register_agents"})

        # Mock successful executions
        for agent in maestro_agent.registered_agents.values():
            agent.execute = AsyncMock(return_value={"status": "success"})

        # Execute workflow
        context = {
            "operation": "execute_workflow",
            "workflow_name": "ticket_resolution",
            "workflow_context": {"ticket_id": "T-001"},
        }

        result = await maestro_agent.execute(context)
        workflow_id = result["workflow_id"]

        # Check workflow status
        status_result = await maestro_agent.execute(
            {"operation": "get_workflow_status", "workflow_id": workflow_id}
        )

        assert status_result["status"] == "success"
        assert status_result["workflow"]["status"] == "completed"
        assert "execution_time" in status_result["workflow"]

        # Check workflow history
        assert len(maestro_agent.workflow_history) > 0
        assert maestro_agent.workflow_history[-1]["workflow_id"] == workflow_id


@pytest.mark.asyncio
async def test_workflow_cancellation(maestro_agent):
    """Test workflow cancellation functionality."""
    # Register agents
    with (
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.TicketClassifierAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.ResolverAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.DesktopCommanderAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.SyncAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.BackupAgent"),
        pytest.mock.patch("agents.core.maestro_orchestrator_agent.MonitoringAgent"),
    ):
        await maestro_agent.execute({"operation": "register_agents"})

        # Mock long-running operations
        async def slow_operation():
            await asyncio.sleep(10)  # Long operation
            return {"status": "success"}

        for agent in maestro_agent.registered_agents.values():
            agent.execute = AsyncMock(side_effect=slow_operation)

        # Start workflow in background
        workflow_task = asyncio.create_task(
            maestro_agent.execute(
                {
                    "operation": "execute_workflow",
                    "workflow_name": "ticket_resolution",
                    "workflow_context": {"ticket_id": "T-001"},
                }
            )
        )

        # Wait a bit then cancel
        await asyncio.sleep(0.1)

        # Get workflow ID from active workflows
        workflow_id = list(maestro_agent.active_workflows.keys())[0]

        # Cancel workflow
        cancel_result = await maestro_agent.execute(
            {"operation": "cancel_workflow", "workflow_id": workflow_id}
        )

        assert cancel_result["status"] == "success"
        assert cancel_result["workflow_id"] == workflow_id

        # Wait for workflow to complete cancellation
        workflow_result = await workflow_task
        assert workflow_result["workflow_status"] == "cancelled"

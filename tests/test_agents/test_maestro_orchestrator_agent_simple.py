"""
Tests for MaestroOrchestratorAgent.

Tests cover basic functionality, validation, and error handling.
"""

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


@pytest.mark.asyncio
async def test_register_agents_basic(maestro_agent):
    """Test basic agent registration functionality."""
    # Test that the method exists and can be called (without mocking complex imports)
    # This tests the basic structure without full integration
    assert hasattr(maestro_agent, "_register_agents")
    assert callable(maestro_agent._register_agents)

    # Test that workflow templates are initialized as empty dict initially
    assert isinstance(maestro_agent.workflow_templates, dict)
    assert (
        len(maestro_agent.workflow_templates) == 0
    )  # Initially empty, populated during registration

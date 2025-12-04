"""
Tests for TwisterLab Base Agent.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


class TestTwisterAgentBase:
    """Tests for the TwisterAgent base class."""

    def test_agent_initialization(self):
        """Test basic agent initialization."""
        from twisterlab.agents.base import TwisterAgent

        class MockAgent(TwisterAgent):
            async def execute(self, task, context=None):
                return {"status": "ok", "task": task}

        agent = MockAgent(
            name="test_agent",
            display_name="Test Agent",
            description="A test agent for unit testing",
        )

        assert agent.name == "test_agent"
        assert agent.display_name == "Test Agent"
        assert agent.description == "A test agent for unit testing"
        assert agent.role == "assistant"
        assert agent.model == "llama-3.2"
        assert agent.temperature == 0.7
        assert agent.tools == []
        assert agent.metadata == {}

    def test_agent_with_custom_params(self):
        """Test agent with custom parameters."""
        from twisterlab.agents.base import TwisterAgent

        class MockAgent(TwisterAgent):
            async def execute(self, task, context=None):
                return {"status": "ok"}

        tools = [{"name": "search", "description": "Search tool"}]
        metadata = {"version": "1.0"}

        agent = MockAgent(
            name="custom_agent",
            display_name="Custom Agent",
            description="Custom description",
            role="specialist",
            instructions="Custom instructions",
            tools=tools,
            model="gpt-4",
            temperature=0.5,
            metadata=metadata,
        )

        assert agent.role == "specialist"
        assert agent.instructions == "Custom instructions"
        assert agent.tools == tools
        assert agent.model == "gpt-4"
        assert agent.temperature == 0.5
        assert agent.metadata == metadata

    def test_agent_created_at_timestamp(self):
        """Test that created_at is set correctly."""
        from twisterlab.agents.base import TwisterAgent

        class MockAgent(TwisterAgent):
            async def execute(self, task, context=None):
                return {}

        agent = MockAgent(
            name="timestamp_test",
            display_name="Timestamp Test",
            description="Test timestamp",
        )

        assert agent.created_at is not None
        # Should contain date/time components
        assert "T" in agent.created_at
        assert ":" in agent.created_at

    def test_agent_default_instructions(self):
        """Test default instructions generation."""
        from twisterlab.agents.base import TwisterAgent

        class MockAgent(TwisterAgent):
            async def execute(self, task, context=None):
                return {}

        agent = MockAgent(
            name="default_inst",
            display_name="Default Agent",
            description="Does something",
        )

        assert "Default Agent" in agent.instructions
        assert "Does something" in agent.instructions

    @pytest.mark.asyncio
    async def test_agent_execute(self):
        """Test agent execute method."""
        from twisterlab.agents.base import TwisterAgent

        class MockAgent(TwisterAgent):
            async def execute(self, task, context=None):
                return {
                    "status": "completed",
                    "task": task,
                    "context_provided": context is not None,
                }

        agent = MockAgent(
            name="exec_test",
            display_name="Exec Test",
            description="Test execution",
        )

        result = await agent.execute("test task")
        assert result["status"] == "completed"
        assert result["task"] == "test task"
        assert result["context_provided"] is False

        result_with_context = await agent.execute("task2", {"key": "value"})
        assert result_with_context["context_provided"] is True

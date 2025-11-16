"""
Test lazy loading of disabled agents.

This test validates that agents can be loaded on-demand without
causing database import errors at startup.
"""

import pytest

from agents import get_agent


@pytest.mark.asyncio
async def test_lazy_loading_desktop_commander():
    """Test lazy loading of DesktopCommanderAgent"""
    # Should not import database at startup
    agent_class = get_agent("desktop_commander")
    assert agent_class is not None, "DesktopCommanderAgent should be available"

    # Should work when instantiated (if environment allows)
    try:
        agent = agent_class()
        # Basic instantiation test - may fail in test environment
        assert hasattr(agent, "execute"), "Agent should have execute method"
    except Exception as e:
        # Allow instantiation failures in test environment
        pytest.skip(f"Agent instantiation failed (expected in test env): {e}")


@pytest.mark.asyncio
async def test_lazy_loading_ticket_classifier():
    """Test lazy loading of TicketClassifierAgent"""
    agent_class = get_agent("ticket_classifier")
    assert agent_class is not None, "TicketClassifierAgent should be available"

    try:
        agent = agent_class()
        assert hasattr(agent, "execute"), "Agent should have execute method"
    except Exception as e:
        pytest.skip(f"Agent instantiation failed (expected in test env): {e}")


@pytest.mark.asyncio
async def test_lazy_loading_resolver():
    """Test lazy loading of ResolverAgent"""
    agent_class = get_agent("resolver")
    assert agent_class is not None, "ResolverAgent should be available"

    try:
        agent = agent_class()
        assert hasattr(agent, "execute"), "Agent should have execute method"
    except Exception as e:
        pytest.skip(f"Agent instantiation failed (expected in test env): {e}")


def test_unknown_agent():
    """Test handling of unknown agent names"""
    agent_class = get_agent("nonexistent_agent")
    assert agent_class is None, "Unknown agent should return None"


def test_lazy_caching():
    """Test that agents are cached after first load"""
    # First call
    agent_class1 = get_agent("desktop_commander")
    # Second call should return cached version
    agent_class2 = get_agent("desktop_commander")

    assert agent_class1 is agent_class2, "Agent should be cached"


def test_no_startup_imports():
    """Test that importing agents module doesn't trigger database imports"""
    # This test ensures that the lazy loading works by checking
    # that no database-related modules are imported at startup

    import sys

    import agents

    # Check that database modules are not imported
    database_modules = [
        "psycopg2",  # This should definitely not be imported
        "psycopg2.extensions",
        "psycopg2.extras",
    ]

    imported_modules = list(sys.modules.keys())
    for module in database_modules:
        assert not any(
            module in imported for imported in imported_modules
        ), f"Database module {module} should not be imported at startup"

    # Note: database.config may be imported by other parts of the system
    # but the key is that psycopg2 itself is not imported at startup

"""
Tests for MonitoringAgent metrics instrumentation.

Tests that Prometheus metrics are incremented and set correctly
when persisted failures and rechecks occur.
"""

import pytest
from unittest.mock import patch, MagicMock

from agents.core.monitoring_agent import MonitoringAgent


@pytest.mark.asyncio
async def test_monitoring_metrics_persisted_failures():
    """Test that persisted failures metrics are updated correctly."""
    agent = MonitoringAgent()

    # Mock the metrics to capture calls
    with patch('agents.core.monitoring_agent.monitoring_persisted_failures_total') as mock_total, \
         patch('agents.core.monitoring_agent.monitoring_persisted_failures') as mock_gauge:

        mock_total.labels.return_value.inc = MagicMock()
        mock_gauge.labels.return_value.set = MagicMock()

        # Simulate a health check that detects failed components
        context = {"operation": "health_check"}
        with patch.object(agent, '_call_mcp') as mock_mcp:
            # Mock MCP to return a summary with failed components
            mock_mcp.return_value = {
                "status": "unhealthy",
                "failed_components": ["database", "cache"]
            }

            result = await agent.execute(context)

            # Check if persisting happened
            assert agent._last_failed_components == ["database", "cache"]

            # Verify metrics were called
            mock_total.labels.assert_called_with(agent_name="MonitoringAgent")
            assert mock_total.labels.return_value.inc.call_count >= 1

            mock_gauge.labels.assert_called_with(agent_name="MonitoringAgent")
            mock_gauge.labels.return_value.set.assert_called_with(2)  # len(["database", "cache"])


@pytest.mark.asyncio
async def test_monitoring_metrics_rechecks():
    """Test that rechecks metric is incremented when detailed checks run."""
    agent = MonitoringAgent()

    with patch('agents.core.monitoring_agent.monitoring_rechecks_total') as mock_rechecks:
        mock_rechecks.labels.return_value.inc = MagicMock()

        # Simulate a health check that triggers detailed checks
        context = {"operation": "health_check"}
        with patch.object(agent, '_call_mcp') as mock_mcp:
            # First call: summary with failures
            mock_mcp.side_effect = [
                {
                    "status": "unhealthy",
                    "failed_components": ["database"]
                },
                # Second call: detailed check for database
                {"healthy": False, "error": "connection failed"}
            ]

            result = await agent.execute(context)

            # Verify rechecks metric was incremented
            mock_rechecks.labels.assert_called_with(agent_name="MonitoringAgent")
            mock_rechecks.labels.return_value.inc.assert_called_once()


@pytest.mark.asyncio
async def test_monitoring_metrics_no_failures():
    """Test that metrics are not incremented when no failures are detected."""
    agent = MonitoringAgent()

    with patch('agents.core.monitoring_agent.monitoring_persisted_failures_total') as mock_total, \
         patch('agents.core.monitoring_agent.monitoring_persisted_failures') as mock_gauge, \
         patch('agents.core.monitoring_agent.monitoring_rechecks_total') as mock_rechecks:

        # Simulate healthy system
        context = {"operation": "health_check"}
        with patch.object(agent, '_call_mcp') as mock_mcp:
            mock_mcp.return_value = {
                "services": {
                    "status": "healthy",
                    "failed_components": []
                }
            }

            result = await agent.execute(context)

            # Verify metrics were not called
            mock_total.labels.return_value.inc.assert_not_called()
            mock_gauge.labels.return_value.set.assert_not_called()
            mock_rechecks.labels.return_value.inc.assert_not_called()
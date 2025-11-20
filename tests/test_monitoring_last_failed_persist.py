import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict, Optional
from agents.core.monitoring_agent import MonitoringAgent


@pytest.mark.asyncio
async def test_monitoring_persists_failed_components_and_rechecks() -> None:
    agent = MonitoringAgent()

    async def router_side_effect(
        agent_name: Optional[str] = None,
        mcp_name: Optional[str] = None,
        operation: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> dict:
        # First summary: report database failed
        if operation == "check_service_health" and (not params or not params.get("service")):
            return {"status": "critical", "failed_components": ["database"]}
        # Per-service details: when asked for service 'api' or 'cache' return healthy
        if operation == "check_service_health" and params and params.get("service"):
            svc = params.get("service")
            return {"service": svc, "status": "healthy", "healthy": True}
        return {"status": "ok"}

    with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        mock_router.route_to_mcp = AsyncMock(side_effect=router_side_effect)

        agent.reset_mcp_trace()

        # Initial detection: should perform summary + detailed per-service checks
        _ = await agent.execute({"operation": "health_check"})
        # At a minimum, we should have summary + at least one per-service check
        assert agent.get_mcp_call_count() >= 2
        # Confirm persisted failed component
        assert getattr(agent, "_last_failed_components", []) == ["database"]

        # Final detection: summary returns healthy but we should still re-check because of persisted failure
        async def router_side_effect_recovered(
            agent_name: Optional[str] = None,
            mcp_name: Optional[str] = None,
            operation: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
        ) -> dict:
            if operation == "check_service_health" and (not params or not params.get("service")):
                return {"status": "stable"}
            if operation == "check_service_health" and params and params.get("service"):
                svc = params.get("service")
                return {"service": svc, "status": "healthy", "healthy": True}
            return {"status": "ok"}

        mock_router.route_to_mcp.side_effect = router_side_effect_recovered
        _ = await agent.execute({"operation": "health_check"})
        # After final healthy summary, because we had persisted a failure, we should have performed per-service checks again
        assert agent.get_mcp_call_count() >= 4

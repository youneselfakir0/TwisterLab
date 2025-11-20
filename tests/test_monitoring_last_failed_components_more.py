import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict, Optional
from agents.core.monitoring_agent import MonitoringAgent


@pytest.mark.asyncio
async def test_monitoring_handles_multi_failure_and_rechecks() -> None:
    agent = MonitoringAgent()

    async def router_side_effect(
        agent_name: Optional[str] = None,
        mcp_name: Optional[str] = None,
        operation: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> dict:
        # First summary: report database+cache failed
        if operation == "check_service_health" and (not params or not params.get("service")):
            return {"status": "critical", "failed_components": ["database", "cache"]}
        # Per-service check: return unhealthy for database/cache, healthy for others
        if operation == "check_service_health" and params and params.get("service"):
            svc = params.get("service")
            if svc in ("database", "cache"):
                return {"service": svc, "status": "unhealthy", "healthy": False}
            return {"service": svc, "status": "healthy", "healthy": True}
        return {"status": "ok"}

    with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        mock_router.route_to_mcp = AsyncMock(side_effect=router_side_effect)

        agent.reset_mcp_trace()

        _ = await agent.execute({"operation": "health_check", "force_detailed": True})
        assert agent.get_mcp_call_count() >= 3
        assert set(getattr(agent, "_last_failed_components", [])) == {"database", "cache"}

        # Now summary becomes healthy but previous failed components should trigger per-service recheck
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
        _ = await agent.execute({"operation": "health_check", "force_detailed": True})
        # Should have rechecked both per-service and hence increased call count
        assert agent.get_mcp_call_count() >= 6


@pytest.mark.asyncio
async def test_monitoring_partial_recovery_updates_persisted_failures() -> None:
    agent = MonitoringAgent()

    async def router_side_effect(
        agent_name: Optional[str] = None,
        mcp_name: Optional[str] = None,
        operation: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> dict:
        if operation == "check_service_health" and (not params or not params.get("service")):
            return {"status": "critical", "failed_components": ["database", "cache"]}
        if operation == "check_service_health" and params and params.get("service"):
            svc = params.get("service")
            if svc == "database":
                # Database recovered in detailed check
                return {"service": svc, "status": "healthy", "healthy": True}
            if svc == "cache":
                # Cache still unhealthy
                return {"service": svc, "status": "unhealthy", "healthy": False}
            return {"service": svc, "status": "healthy", "healthy": True}
        return {"status": "ok"}

    with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        mock_router.route_to_mcp = AsyncMock(side_effect=router_side_effect)

        agent.reset_mcp_trace()
        _ = await agent.execute({"operation": "health_check"})
        assert agent.get_mcp_call_count() >= 3
        assert set(getattr(agent, "_last_failed_components", [])) == {"database", "cache"}

        # Recovered summary but cache remains unhealthy per re-check
        async def router_recovered_partial(
            agent_name: Optional[str] = None,
            mcp_name: Optional[str] = None,
            operation: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
        ) -> dict:
            if operation == "check_service_health" and (not params or not params.get("service")):
                    # Provide a detailed services summary indicating database is healthy and cache remains unhealthy
                    return {
                        "status": "stable",
                        "services": {
                            "database": {"status": "healthy", "healthy": True},
                            "cache": {"status": "unhealthy", "healthy": False},
                        },
                    }
            if operation == "check_service_health" and params and params.get("service"):
                svc = params.get("service")
                if svc == "cache":
                    return {"service": svc, "status": "unhealthy", "healthy": False}
                return {"service": svc, "status": "healthy", "healthy": True}
            return {"status": "ok"}

        mock_router.route_to_mcp.side_effect = router_recovered_partial
        _ = await agent.execute({"operation": "health_check"})
        # Database recovered, only cache remains persisted
        assert set(getattr(agent, "_last_failed_components", [])) == {"cache"}
        # Call count increments reflecting the recheck (>=7 depending on which per-services were checked)
        assert agent.get_mcp_call_count() >= 7


    @pytest.mark.asyncio
    async def test_monitoring_related_map_toggle() -> None:
        agent = MonitoringAgent()

        async def router_side_effect(
            agent_name: Optional[str] = None,
            mcp_name: Optional[str] = None,
            operation: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
        ) -> dict:
            # Summary indicates database is failed
            if operation == "check_service_health" and (not params or not params.get("service")):
                return {"status": "critical", "failed_components": ["database"]}
            if operation == "check_service_health" and params and params.get("service"):
                svc = params.get("service")
                return {"service": svc, "status": "unhealthy" if svc == "database" else "healthy", "healthy": svc != "database"}
            return {"status": "ok"}

        with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router
            mock_router.route_to_mcp = AsyncMock(side_effect=router_side_effect)

            # Toggle off related investigations
            agent.investigate_related = False
            agent.reset_mcp_trace()
            _ = await agent.execute({"operation": "health_check", "force_detailed": True})
            # summary + database per-service => 2 calls
            assert agent.get_mcp_call_count() >= 2

            # Turn on related investigations and run again
            agent.investigate_related = True
            agent.reset_mcp_trace()
            _ = await agent.execute({"operation": "health_check", "force_detailed": True})
            # summary + database + related services (cache, api, agents) => at least 5 calls
            assert agent.get_mcp_call_count() >= 5


    @pytest.mark.asyncio
    async def test_monitoring_investigate_override_context() -> None:
        agent = MonitoringAgent()

        async def router_side_effect(
            agent_name: Optional[str] = None,
            mcp_name: Optional[str] = None,
            operation: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
        ) -> dict:
            if operation == "check_service_health" and (not params or not params.get("service")):
                return {"status": "critical", "failed_components": ["database"]}
            if operation == "check_service_health" and params and params.get("service"):
                svc = params.get("service")
                return {"service": svc, "status": "unhealthy" if svc == "database" else "healthy", "healthy": svc != "database"}
            return {"status": "ok"}

        with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router
            mock_router.route_to_mcp = AsyncMock(side_effect=router_side_effect)

            agent.investigate_related = False
            agent.reset_mcp_trace()
            # Override via context to enable related checks for this run
            _ = await agent.execute({"operation": "health_check", "investigate_related": True, "force_detailed": True})
            assert agent.get_mcp_call_count() >= 5
            # Now override to disable related checks for a run explicitly
            agent.reset_mcp_trace()
            _ = await agent.execute({"operation": "health_check", "investigate_related": False, "force_detailed": True})
            assert agent.get_mcp_call_count() >= 2

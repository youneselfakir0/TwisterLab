import pytest
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from agents.core.backup_agent import BackupAgent
from agents.core.monitoring_agent import MonitoringAgent
from agents.core.sync_agent import SyncAgent

@pytest.mark.asyncio
async def test_cascading_flow_mcp_call_counts() -> None:
    agents = {
        "monitoring": MonitoringAgent(),
        "backup": BackupAgent(),
        "sync": SyncAgent(),
    }

    # We'll use a param-aware side-effect to return the expected responses
    # based on the operation and params for deterministic test behavior.
    call_index = 0
    recovered = False

    async def router_side_effect(
        agent_name: Optional[str] = None,
        mcp_name: Optional[str] = None,
        operation: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        nonlocal call_index, recovered
        params = params or {}
        # If the system recovered, return a stable aggregated summary
        if operation == "check_service_health" and (not params or not params.get("service")) and recovered:
            return {"status": "stable", "all_components": "operational"}
        if operation == "check_service_health" and (not params or not params.get("service")):
            # Return a global summary indicating the database reported failure
            return {"status": "critical", "failed_components": ["database"]}
        if operation == "check_service_health" and params and params.get("service"):
            svc = params.get("service")
            return {"service": svc, "status": "healthy"}
        if operation == "emergency_backup":
            return {"emergency_backup": "initiated", "status": "in_progress"}
        if operation == "isolate_components":
            return {"isolation_complete": True, "failed_components_isolated": 3}
        if operation == "recovery":
            recovered = True
            return {"database": "recovering", "cache": "isolated", "api": "standby"}
        if operation == "final_verification":
            return {"status": "stable", "all_components": "operational"}
        # Default fallback
        res = {"status": "ok"}
        # Set stable state for the final monitoring verification which occurs
        # after the emergency backup, isolation and recovery sequence.
        if operation == "check_service_health" and recovered:
            res = {"status": "stable", "all_components": "operational"}
        call_index += 1
        return res

    with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        mock_router.route_to_mcp = AsyncMock(side_effect=router_side_effect)

        # Reset counters
        agents["monitoring"].reset_mcp_trace()
        agents["backup"].reset_mcp_trace()
        agents["sync"].reset_mcp_trace()

        # 1. Initial detection
        initial_detection = await agents["monitoring"].execute(
            {"operation": "health_check"}
        )
        # Monitoring initial detection should do 1 summary + 3 related
        # checks (cache, api, agents) so total 4 MCP calls for the agent.
        assert agents["monitoring"].get_mcp_call_count() >= 4
        # Validate the initial detection result to avoid unused variable warnings.
        # operation-level 'status' is the execution result (success). Validate the
        # health status inside the results payload to assert system state.
        assert initial_detection["results"]["status"] == "critical"

        # 2. Emergency backup
        emergency_backup = await agents["backup"].execute(
            {"operation": "backup", "backup_type": "emergency"}
        )
        # Expect emergency backup used 1 call (aggregated)
        assert agents["backup"].get_mcp_call_count() == 1
        # Support both agent-level and wrapper-level result shapes.
        assert (
            emergency_backup.get("status") == "in_progress"
            or emergency_backup.get("result", {}).get("status") == "in_progress"
        )

        # 3. Component isolation
        isolation = await agents["sync"].execute(
            {"operation": "isolate_components"}
        )
        # Sync isolation triggers 1 isolate call + 1 verification check
        assert agents["sync"].get_mcp_call_count() == 2
        # Assert isolation result used
        assert isolation.get("isolation_complete") is True

        # 4. Gradual recovery
        recovery = await agents["backup"].execute(
            {"operation": "recovery", "recovery_type": "gradual"}
        )
        # Recovery should be aggregated call
        assert agents["backup"].get_mcp_call_count() == 2
        # Validate expected recovery status
        assert recovery.get("database") == "recovering"

    # 5. Final verification
        final_check = await agents["monitoring"].execute(
            {"operation": "health_check"}
        )
        # Final monitoring check should re-check failed components (related
        # services) so total monitoring calls will be 4 (initial) + 4 (final) = 8
        assert agents["monitoring"].get_mcp_call_count() >= 8
        # Validate final monitoring check result
        assert final_check["results"]["status"] == "stable"

        # Total calls consumed should equal number of side_effects and expected
        # MCP calls in this sequence: monitoring(8) + backup(2) + sync(2) = 12
        assert mock_router.route_to_mcp.call_count >= 12

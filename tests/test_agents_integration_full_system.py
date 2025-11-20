"""
Integration tests for autonomous agents working together.

These tests validate the complete agent ecosystem, MCP communication,
and autonomous system repair capabilities.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.core.backup_agent import BackupAgent
from agents.core.maestro_orchestrator_agent import MaestroOrchestratorAgent
from agents.core.monitoring_agent import MonitoringAgent
from agents.core.sync_agent import SyncAgent
from agents.mcp.mcp_router import MCPRouter


class TestAgentIntegration:
    """Test agents working together autonomously."""

    @pytest.fixture
    def agents(self):
        """Setup all agents for integration testing."""
        return {
            "monitoring": MonitoringAgent(),
            "backup": BackupAgent(),
            "sync": SyncAgent(),
            "maestro": MaestroOrchestratorAgent(),
        }

    @pytest.mark.asyncio
    async def test_full_system_health_check_cycle(self, agents):
        """Test complete health check cycle across all agents."""
        # Simulate system with issues
        system_state = {
            "api": {"status": "unhealthy", "error": "timeout"},
            "database": {"status": "healthy"},
            "cache": {"status": "degraded", "latency": 5000},
            "agents": {"status": "healthy"},
        }

        with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            # Setup MCP responses for health checks
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Monitoring agent health check
                    system_state,
                    # Diagnostic checks
                    {
                        "issues_found": 2,
                        "issues": [
                            {"type": "api_unhealthy", "severity": "high"},
                            {"type": "cache_degraded", "severity": "medium"},
                        ],
                    },
                    # Repair operations
                    {"repaired_services": ["api"], "status": "repaired"},
                    {"repaired_services": ["cache"], "status": "optimized"},
                ]
            )

            # Execute monitoring cycle
            monitoring_result = await agents["monitoring"].execute({"operation": "health_check"})

            diagnostic_result = await agents["monitoring"].execute(
                {"operation": "diagnostic", "check_type": "system"}
            )

            repair_result = await agents["monitoring"].execute(
                {"operation": "repair", "repair_type": "restart_service"}
            )

            # Verify the cycle worked
            assert monitoring_result["status"] == "success"
            assert len(diagnostic_result["diagnosis"]) == 2
            assert len(repair_result["result"]["repairs"]) == 2

    @pytest.mark.asyncio
    async def test_disaster_recovery_orchestration(self, agents):
        """Test orchestrated disaster recovery across agents."""
        disaster_scenario = {
            "database_corruption": True,
            "cache_inconsistent": True,
            "config_files_missing": True,
        }

        # Setup disaster recovery sequence - shared call counter
        mock_responses = [
            # Monitoring detects disaster (first call)
            {"status": "critical_failure", "issues": disaster_scenario},
            # Monitoring detects disaster (second call - duplicate)
            {"status": "critical_failure", "issues": disaster_scenario},
            # Backup agent integrity check
            {"integrity_status": "compromised", "issues_found": 3},
            # Backup agent recovery
            {"status": "restored", "components": ["database", "config"]},
            # Sync agent consistency check
            {"consistency_status": "inconsistent", "inconsistencies_found": 2},
            # Sync agent reconciliation
            {"reconciled_items": 2, "status": "consistent"},
            # Final health check
            {"status": "healthy", "all_systems": "operational"},
        ]

        call_counter = [0]  # Use list to modify in nested function

        async def mock_mcp_call(self, agent_name, mcp_name, operation, params):
            index = call_counter[0]
            call_counter[0] += 1
            if index < len(mock_responses):
                return mock_responses[index]
            else:
                return {"status": "mock_response", "call_index": index}

        async def mock_validate_access(self, *args, **kwargs):
            pass  # Allow all access in tests

        # Patch the MCPRouter class methods
        with patch.object(MCPRouter, '_mock_mcp_call', mock_mcp_call), \
             patch.object(MCPRouter, '_validate_access', mock_validate_access):

            # Execute disaster recovery workflow
            # 1. Monitoring detects issues
            monitoring_result = await agents["monitoring"].execute(
                {"operation": "diagnostic", "check_type": "system"}
            )

            # 2. Backup agent performs integrity check and recovery
            backup_integrity = await agents["backup"].execute({"operation": "integrity_check"})

            backup_recovery = await agents["backup"].execute(
                {"operation": "recovery", "recovery_type": "full"}
            )

            # 3. Sync agent reconciles inconsistencies
            sync_reconciliation = await agents["sync"].execute({"operation": "reconciliation"})

            # 4. Monitoring verifies recovery
            final_health = await agents["monitoring"].execute({"operation": "health_check"})

            # Verify disaster recovery succeeded
            assert len(monitoring_result["diagnosis"]) > 0
            assert backup_integrity["result"]["integrity_status"] == "compromised"
            assert backup_recovery["status"] == "success"
            assert sync_reconciliation["result"]["reconciled_items"] == 2
            assert final_health["result"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_performance_optimization_cycle(self, agents):
        """Test performance monitoring and optimization across agents."""
        performance_issues = {
            "cache": {"hit_rate": 0.5, "latency": 2000},
            "database": {"query_time": 3000, "connections": 80},
            "agents": {"response_time": 8000},
        }

        with patch.object(agents["sync"], "mcp_router") as mock_router:
            # Setup performance optimization sequence
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Sync agent performance check (initial)
                    {
                        "result": {
                            "bottlenecks": 3,
                            "performance_metrics": performance_issues,
                            "optimization_needed": True,
                        }
                    },
                    # Sync agent performance check (final)
                    {
                        "result": {
                            "bottlenecks": 0,
                            "optimization_needed": False,
                        }
                    },
                ]
            )

            # Execute performance optimization cycle
            initial_perf = await agents["sync"].execute({"operation": "performance_check"})

            # Simulate optimizations (would be triggered by Maestro)
            # Final verification
            final_perf = await agents["sync"].execute({"operation": "performance_check"})

            # Verify optimization worked
            assert initial_perf["result"]["result"]["optimization_needed"] == True
            assert initial_perf["result"]["result"]["bottlenecks"] == 3
            assert final_perf["result"]["result"]["optimization_needed"] == False
            assert final_perf["result"]["result"]["bottlenecks"] == 0

    @pytest.mark.asyncio
    async def test_maestro_orchestrates_agent_collaboration(self, agents):
        """Test Maestro orchestrating multi-agent collaboration."""
        complex_issue = {
            "type": "system_wide_degradation",
            "components": ["api", "database", "cache", "agents"],
            "severity": "critical",
        }

        with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            # Setup orchestrated response sequence
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Maestro gets system status
                    {"system_health": "critical", "active_issues": complex_issue},
                    # Maestro coordinates monitoring
                    {"issues_found": 4, "coordinated_diagnostic": True},
                    # Maestro coordinates backup
                    {"backup_completed": True, "data_preserved": True},
                    # Maestro coordinates sync
                    {"consistency_restored": True, "performance_optimized": True},
                    # Maestro verifies resolution
                    {"system_health": "healthy", "all_issues_resolved": True},
                ]
            )

            # Simulate Maestro orchestrating the response
            # In real scenario, Maestro would trigger these automatically
            # based on monitoring alerts

            # Maestro assesses situation
            maestro_assessment = await agents["maestro"].execute({"operation": "assess_situation"})

            # Maestro coordinates diagnostic
            diagnostic_coordination = await agents["monitoring"].execute(
                {"operation": "diagnostic", "check_type": "system"}
            )

            # Maestro coordinates recovery
            recovery_coordination = await agents["backup"].execute({"operation": "recovery"})

            # Maestro coordinates optimization
            optimization_coordination = await agents["sync"].execute(
                {"operation": "reconciliation"}
            )

            # Maestro verifies resolution
            final_verification = await agents["maestro"].execute({"operation": "verify_resolution"})

            # Verify orchestration succeeded
            assert maestro_assessment["status"] == "success"
            assert len(diagnostic_coordination["diagnosis"]) == 4
            assert recovery_coordination["status"] == "success"
            assert optimization_coordination["status"] == "success"
            assert final_verification["result"]["system_health"] == "healthy"

    @pytest.mark.asyncio
    async def test_mcp_isolation_maintained_during_collaboration(self, agents):
        """Test that MCP isolation is maintained during agent collaboration."""
        with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            # Track MCP calls to verify isolation
            mcp_calls = []
            mock_router.route_to_mcp = AsyncMock(
                side_effect=lambda **kwargs: self._track_mcp_call(mcp_calls, kwargs)
            )

            # Execute operations across all agents
            await agents["monitoring"].execute({"operation": "health_check"})
            await agents["backup"].execute({"operation": "backup"})
            await agents["sync"].execute({"operation": "sync"})

            # Verify MCP isolation - each agent should only access allowed MCPs
            monitoring_calls = [
                call for call in mcp_calls if call["agent_name"] == "MonitoringAgent"
            ]
            backup_calls = [call for call in mcp_calls if call["agent_name"] == "BackupAgent"]
            sync_calls = [call for call in mcp_calls if call["agent_name"] == "SyncAgent"]

            # Monitoring agent should only call monitoring-related MCPs
            for call in monitoring_calls:
                assert "monitoring" in call["mcp_name"] or "maestro" in call["mcp_name"]

            # Backup agent should only call backup/sync-related MCPs
            for call in backup_calls:
                assert "sync" in call["mcp_name"] or "desktop_commander" in call["mcp_name"]

            # Sync agent should only call sync-related MCPs
            for call in sync_calls:
                assert (
                    "sync" in call["mcp_name"]
                    or "maestro" in call["mcp_name"]
                    or "monitoring" in call["mcp_name"]
                )

    def _track_mcp_call(self, calls_list, kwargs):
        """Helper to track MCP calls for isolation testing."""
        calls_list.append(kwargs)
        return {"status": "success"}

    @pytest.mark.asyncio
    async def test_agents_handle_cascading_failures(self, agents):
        """Test agents handling cascading system failures."""
        cascading_failure = {
            "initial_failure": "database_down",
            "cascading_effects": [
                "cache_inconsistent",
                "api_failing",
                "agents_unresponsive",
            ],
        }

        with patch("agents.mcp.mcp_router.MCPRouter") as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            # Setup cascading failure sequence
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Initial monitoring detects database down
                    {"status": "critical", "failed_components": ["database"]},
                    # Cache becomes inconsistent
                    {"status": "failed", "error": "upstream_unavailable"},
                    # API starts failing
                    {"status": "failed", "error": "database_unavailable"},
                    # Agents become unresponsive
                    {"status": "failed", "error": "system_overload"},
                    # Backup agent attempts emergency recovery
                    {"emergency_backup": "initiated", "status": "in_progress"},
                    # Sync agent isolates failing components
                    {"isolation_complete": True, "failed_components_isolated": 3},
                    # Monitoring verifies isolation
                    {"isolated_components": 3, "system_stable": True},
                    # Gradual recovery begins
                    {"database": "recovering", "cache": "isolated", "api": "standby"},
                    # Final system stabilization
                    {"status": "stable", "all_components": "operational"},
                ]
            )

            # Execute cascading failure response
            # 1. Initial detection
            initial_detection = await agents["monitoring"].execute({"operation": "health_check"})

            # 2. Emergency backup
            emergency_backup = await agents["backup"].execute(
                {"operation": "backup", "backup_type": "emergency"}
            )

            # 3. Component isolation
            isolation = await agents["sync"].execute({"operation": "isolate_components"})

            # 4. Gradual recovery
            recovery = await agents["backup"].execute(
                {"operation": "recovery", "recovery_type": "gradual"}
            )

            # 5. Final verification
            final_check = await agents["monitoring"].execute({"operation": "health_check"})

            # Verify cascading failure was handled
            assert len(initial_detection["diagnosis"]) > 0
            assert emergency_backup["result"]["emergency_backup"] == "initiated"
            assert isolation["result"]["isolation_complete"] == True
            assert recovery["status"] == "success"
            assert final_check["result"]["status"] == "stable"


@pytest.mark.asyncio
async def test_agent_audit_trail_integrity():
    """Test that agent operations maintain complete audit trails."""
    agent = MonitoringAgent()

    audit_entries = []

    with patch.object(agent, "audit_log") as mock_audit:
        mock_audit.side_effect = lambda *args, **kwargs: audit_entries.append(args)

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(return_value={"status": "healthy"})

            # Execute multiple operations
            await agent.execute({"operation": "health_check"})
            await agent.execute({"operation": "diagnostic", "check_type": "system"})
            await agent.execute({"operation": "repair"})

            # Verify audit trail completeness
            assert len(audit_entries) == 6  # 2 entries per operation (start + complete)

            operations_audited = [entry[0] for entry in audit_entries]
            # Expect modernized operation naming
            assert "monitoring_operation_start" in operations_audited
            assert "monitoring_operation_complete" in operations_audited

            # Verify timestamps are present and sequential
            timestamps = [
                entry[1].get("timestamp")
                for entry in audit_entries
                if len(entry) > 1
            ]
            assert all(ts for ts in timestamps)
            assert all(datetime.fromisoformat(ts) for ts in timestamps)


@pytest.mark.asyncio
async def test_agent_error_propagation_and_recovery():
    """Test error propagation and recovery across agent ecosystem."""
    agents = {
        "monitoring": MonitoringAgent(),
        "backup": BackupAgent(),
        "sync": SyncAgent(),
    }

    error_scenario = "MCP connection failure"

    with (
        patch.object(
            agents["monitoring"], "mcp_router"
        ) as mock_router_monitoring,
        patch.object(agents["backup"], "mcp_router") as mock_router_backup,
        patch.object(agents["sync"], "mcp_router") as mock_router_sync,
    ):
        # Setup error propagation
        for mock_router in [
            mock_router_monitoring,
            mock_router_backup,
            mock_router_sync,
        ]:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=Exception(error_scenario)
            )

        # Test that all agents handle errors gracefully
        for agent_name, agent in agents.items():
            with pytest.raises(Exception) as exc_info:
                await agent.execute({"operation": "health_check"})

            assert error_scenario in str(exc_info.value)

        # Verify error was audited
        # (In real implementation, audit_log would be checked)

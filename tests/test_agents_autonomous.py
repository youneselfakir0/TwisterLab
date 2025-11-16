"""
Tests for autonomous agents - MonitoringAgent, BackupAgent, SyncAgent.

These tests validate the self-healing capabilities, MCP isolation,
and autonomous operation of the TwisterLab agent system.
"""

from unittest.mock import AsyncMock, patch

import pytest

from agents.core.backup_agent import BackupAgent
from agents.core.monitoring_agent import MonitoringAgent
from agents.core.sync_agent import SyncAgent


class TestMonitoringAgent:
    """Test MonitoringAgent autonomous operations."""

    @pytest.fixture
    def agent(self):
        """Setup test monitoring agent."""
        return MonitoringAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "MonitoringAgent"
        assert agent.priority == 1
        assert "health_check" in agent.capabilities
        assert "diagnostic" in agent.capabilities
        assert "self_repair" in agent.capabilities

    @pytest.mark.asyncio
    async def test_execute_health_check_success(self, agent):
        """Test successful health check execution."""
        context = {"operation": "health_check"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                return_value={
                    "status": "healthy",
                    "services": ["api", "database", "cache"],
                }
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "health_check"
            assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_diagnostic_with_issues(self, agent):
        """Test diagnostic execution that finds issues."""
        context = {"operation": "diagnostic"}

        with patch.object(agent, "mcp_router") as mock_router:
            # Mock health check showing issues
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Health check response
                    {
                        "status": "degraded",
                        "issues": [{"service": "database", "status": "unhealthy"}],
                    },
                    # Diagnostic response
                    {
                        "issues_found": 1,
                        "issues": [
                            {
                                "type": "database_connection",
                                "severity": "high",
                                "description": "Database connection failed",
                            }
                        ],
                    },
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "diagnostic"
            assert result["result"]["issues_found"] == 1

    @pytest.mark.asyncio
    async def test_execute_self_repair(self, agent):
        """Test self-repair execution."""
        context = {"operation": "repair", "repair_type": "restart_service"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                return_value={"repaired_services": ["database"], "status": "repaired"}
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "repair"
            assert "repaired_services" in result["result"]

    @pytest.mark.asyncio
    async def test_execute_invalid_operation(self, agent):
        """Test execution with invalid operation."""
        context = {"operation": "invalid_op"}

        with pytest.raises(ValueError, match="Unknown operation"):
            await agent.execute(context)

    @pytest.mark.asyncio
    async def test_health_check_all_services(self, agent):
        """Test comprehensive health check."""
        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                return_value={
                    "status": "healthy",
                    "services": ["api", "database", "cache", "agents"],
                }
            )

            result = await agent._check_health_all()

            assert "services" in result
            assert len(result["services"]) == 4

    @pytest.mark.asyncio
    async def test_diagnose_issues_with_multiple_problems(self, agent):
        """Test diagnosis of multiple system issues."""
        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # API health
                    {"status": "unhealthy", "error": "timeout"},
                    # Database health
                    {"status": "healthy"},
                    # Cache health
                    {"status": "degraded", "latency": 5000},
                    # Agent health
                    {"status": "healthy"},
                ]
            )

            issues = await agent._diagnose_issues()

            assert len(issues) >= 2  # Should find API and cache issues
            issue_types = [issue["type"] for issue in issues]
            assert "api_unhealthy" in issue_types
            assert "cache_degraded" in issue_types

    @pytest.mark.asyncio
    async def test_perform_repairs_with_critical_issues(self, agent):
        """Test repair operations for critical issues."""
        issues = [
            {
                "type": "database_connection",
                "severity": "critical",
                "description": "Database completely down",
            },
            {
                "type": "api_timeout",
                "severity": "high",
                "description": "API unresponsive",
            },
        ]

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Database restart
                    {"status": "restarted", "service": "database"},
                    # API restart
                    {"status": "restarted", "service": "api"},
                ]
            )

            repairs = await agent._perform_repairs(issues)

            assert len(repairs) == 2
            assert all(repair["result"]["status"] == "restarted" for repair in repairs)


class TestBackupAgent:
    """Test BackupAgent autonomous operations."""

    @pytest.fixture
    def agent(self):
        """Setup test backup agent."""
        return BackupAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "BackupAgent"
        assert agent.priority == 2
        assert "automated_backup" in agent.capabilities
        assert "integrity_check" in agent.capabilities

    @pytest.mark.asyncio
    async def test_execute_backup_full(self, agent):
        """Test full backup execution."""
        context = {"operation": "backup", "backup_type": "full"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Database backup
                    {"status": "success", "size": "1.2GB"},
                    # Config backup
                    {"status": "success", "files": 15},
                    # Logs backup
                    {"status": "success", "rotated": True},
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "backup"
            assert "database" in result["result"]
            assert "config" in result["result"]
            assert "logs" in result["result"]

    @pytest.mark.asyncio
    async def test_execute_integrity_check_with_issues(self, agent):
        """Test integrity check that finds corruption."""
        context = {"operation": "integrity_check", "check_type": "full"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Database integrity - corrupted
                    {"integrity_ok": False, "corruption_detected": True},
                    # Config integrity - OK
                    [],
                    # Log integrity - OK
                    {"corrupted_logs": 0},
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["result"]["integrity_status"] == "compromised"
            assert result["result"]["issues_found"] >= 1

    @pytest.mark.asyncio
    async def test_execute_recovery_database(self, agent):
        """Test database recovery execution."""
        context = {"operation": "recovery", "recovery_type": "database"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                return_value={
                    "status": "restored",
                    "backup_file": "database_2024-01-01.bak",
                    "records_restored": 15000,
                }
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "recovery"
            assert result["result"]["database"]["status"] == "restored"

    @pytest.mark.asyncio
    async def test_execute_self_repair_integrity(self, agent):
        """Test self-repair of integrity issues."""
        context = {"operation": "repair", "repair_type": "integrity"}

        with patch.object(agent, "mcp_router") as mock_router:
            # Mock integrity check finding issues
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Integrity check - finds database corruption
                    {
                        "issues_found": 1,
                        "issues": [{"type": "database_corruption", "severity": "critical"}],
                        "integrity_status": "compromised",
                    },
                    # Database recovery
                    {"status": "restored", "records_restored": 15000},
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "repair"
            assert result["result"]["repairs_attempted"] == 1


class TestSyncAgent:
    """Test SyncAgent autonomous operations."""

    @pytest.fixture
    def agent(self):
        """Setup test sync agent."""
        return SyncAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "SyncAgent"
        assert agent.priority == 3
        assert "cache_sync" in agent.capabilities
        assert "consistency_check" in agent.capabilities

    @pytest.mark.asyncio
    async def test_execute_sync_full(self, agent):
        """Test full synchronization execution."""
        context = {"operation": "sync", "sync_type": "full"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Cache-DB sync
                    {"status": "synced", "records_synced": 500},
                    # Agent state sync
                    {"status": "synced", "agents_synced": 7},
                    # Metrics sync
                    {"status": "synced", "metrics_synced": 25},
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "sync"
            assert "cache_db_sync" in result["result"]
            assert "agent_state_sync" in result["result"]
            assert "metrics_sync" in result["result"]

    @pytest.mark.asyncio
    async def test_execute_consistency_check_with_drift(self, agent):
        """Test consistency check that finds drift."""
        context = {"operation": "consistency_check", "check_type": "full"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Cache-DB consistency - drift found
                    {
                        "inconsistencies_found": 2,
                        "inconsistencies": [
                            {"key": "user:123", "drift_seconds": 400},
                            {"key": "ticket:T-001", "drift_seconds": 600},
                        ],
                    },
                    # Agent consistency - OK
                    {"inconsistent_agents": 0},
                    # Metrics consistency - OK
                    {"metrics_mismatch": 0},
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["result"]["consistency_status"] == "inconsistent"
            assert result["result"]["inconsistencies_found"] >= 2

    @pytest.mark.asyncio
    async def test_execute_reconciliation(self, agent):
        """Test automatic reconciliation execution."""
        context = {"operation": "reconciliation", "reconciliation_type": "full"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Consistency check - finds issues
                    {
                        "inconsistencies_found": 1,
                        "inconsistencies": [{"type": "cache_db_drift", "severity": "medium"}],
                        "consistency_status": "inconsistent",
                    },
                    # Reconciliation sync
                    {"status": "synced", "records_synced": 1},
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "reconciliation"
            assert result["result"]["reconciliation_needed"] == True
            assert len(result["result"]["reconciled_items"]) == 1

    @pytest.mark.asyncio
    async def test_execute_performance_check_with_bottlenecks(self, agent):
        """Test performance check that identifies bottlenecks."""
        context = {"operation": "performance_check"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                side_effect=[
                    # Cache performance - low hit rate
                    {"hit_rate": 0.65, "latency_avg": 150},
                    # Database performance - slow queries
                    {"query_time_avg": 1200, "connections_active": 45},
                    # Agent performance - slow responses
                    {"response_time_avg": 6000, "active_agents": 7},
                ]
            )

            result = await agent.execute(context)

            assert result["status"] == "success"
            assert result["operation"] == "performance_check"
            assert result["result"]["optimization_needed"] == True
            assert len(result["result"]["bottlenecks"]) >= 2  # Should find multiple bottlenecks

    @pytest.mark.asyncio
    async def test_sync_cache_database(self, agent):
        """Test cache-database synchronization."""
        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(
                return_value={
                    "status": "synced",
                    "records_synced": 250,
                    "sync_duration_ms": 1500,
                }
            )

            result = await agent._sync_cache_database()

            assert result["status"] == "synced"
            assert result["records_synced"] == 250

    @pytest.mark.asyncio
    async def test_identify_bottlenecks(self, agent):
        """Test bottleneck identification logic."""
        performance_metrics = {
            "cache": {"hit_rate": 0.6},  # Below threshold
            "database": {"query_time_avg": 1500},  # Above threshold
            "agents": {"response_time_avg": 3000},  # OK
        }

        bottlenecks = agent._identify_bottlenecks(performance_metrics)

        assert len(bottlenecks) == 2
        bottleneck_types = [b["type"] for b in bottlenecks]
        assert "low_hit_rate" in bottleneck_types
        assert "slow_queries" in bottleneck_types


@pytest.mark.asyncio
async def test_agents_mcp_isolation():
    """Test that agents maintain MCP isolation."""
    monitoring = MonitoringAgent()
    backup = BackupAgent()
    sync = SyncAgent()

    # Each agent should have its own MCP router instance
    assert monitoring.mcp_router is not backup.mcp_router
    assert backup.mcp_router is not sync.mcp_router
    assert monitoring.mcp_router is not sync.mcp_router


@pytest.mark.asyncio
async def test_agents_audit_logging():
    """Test that agents properly audit their operations."""
    agent = MonitoringAgent()

    with patch.object(agent, "audit_log") as mock_audit:
        context = {"operation": "health_check"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(return_value={"status": "healthy"})

            await agent.execute(context)

            # Should have logged start and complete
            assert mock_audit.call_count == 2
            calls = mock_audit.call_args_list
            assert calls[0][0][0] == "monitoring_operation_start"
            assert calls[1][0][0] == "monitoring_operation_complete"


@pytest.mark.asyncio
async def test_agents_error_handling():
    """Test that agents handle errors gracefully."""
    agent = MonitoringAgent()

    with patch.object(agent, "audit_log") as mock_audit:
        context = {"operation": "health_check"}

        with patch.object(agent, "mcp_router") as mock_router:
            mock_router.route_to_mcp = AsyncMock(side_effect=Exception("MCP connection failed"))

            with pytest.raises(Exception):
                await agent.execute(context)

            # Should have logged failure
            mock_audit.assert_called_with(
                "monitoring_operation_failed", {"error": "MCP connection failed"}
            )

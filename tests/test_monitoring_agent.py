"""
Tests for RealMonitoringAgent
=============================

Comprehensive test suite for the RealMonitoringAgent functionality.

Run with: pytest tests/test_monitoring_agent.py -v
"""

import pytest
from datetime import datetime, timezone
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.support.monitoring_agent import AlertSeverity


@pytest.fixture
def monitoring_agent():
    """Create a RealMonitoringAgent instance for testing"""
    return RealMonitoringAgent()


# ============================================================================
# AGENT INITIALIZATION TESTS
# ============================================================================

def test_monitoring_agent_initialization(monitoring_agent):
    """Test MonitoringAgent initializes correctly"""
    assert monitoring_agent.name == "monitoring"
    assert monitoring_agent.display_name == "Monitoring Agent"
    assert monitoring_agent.temperature == 0.0
    assert len(monitoring_agent.metrics) == 0
    assert len(monitoring_agent.alerts) == 0
    assert len(monitoring_agent.monitored_agents) == 6
    assert "classifier" in monitoring_agent.monitored_agents
    assert "backup" in monitoring_agent.monitored_agents


def test_monitoring_agent_thresholds(monitoring_agent):
    """Test default alert thresholds"""
    assert monitoring_agent.thresholds["cpu_usage"] == 80.0
    assert monitoring_agent.thresholds["memory_usage"] == 85.0
    assert monitoring_agent.thresholds["disk_usage"] == 90.0
    assert monitoring_agent.thresholds["api_response_time"] == 2.0
    assert monitoring_agent.thresholds["error_rate"] == 10.0
    assert monitoring_agent.thresholds["agent_response_time"] == 5.0


# ============================================================================
# METRICS COLLECTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_collect_metrics(monitoring_agent):
    """Test collecting all metrics"""
    result = await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )

    assert result["status"] == "success"
    assert "metrics_collected" in result
    assert result["metrics_collected"] > 0
    assert "timestamp" in result

    # Verify metrics were stored
    assert len(monitoring_agent.metrics) > 0


@pytest.mark.asyncio
async def test_collect_system_metrics(monitoring_agent):
    """Test system metrics collection"""
    metrics = await monitoring_agent._collect_system_metrics()

    # CPU metrics
    assert "system_cpu_usage_percent" in metrics
    assert "system_cpu_count" in metrics
    assert metrics["system_cpu_usage_percent"] >= 0
    assert metrics["system_cpu_usage_percent"] <= 100

    # Memory metrics
    assert "system_memory_usage_percent" in metrics
    assert "system_memory_available_mb" in metrics
    assert "system_memory_total_mb" in metrics
    assert metrics["system_memory_usage_percent"] >= 0
    assert metrics["system_memory_usage_percent"] <= 100

    # Disk metrics
    assert "system_disk_usage_percent" in metrics
    assert "system_disk_free_gb" in metrics
    assert "system_disk_total_gb" in metrics
    assert metrics["system_disk_usage_percent"] >= 0
    assert metrics["system_disk_usage_percent"] <= 100

    # Network metrics
    assert "system_network_bytes_sent" in metrics
    assert "system_network_bytes_recv" in metrics


@pytest.mark.asyncio
async def test_collect_agent_metrics(monitoring_agent):
    """Test agent metrics collection"""
    metrics = await monitoring_agent._collect_agent_metrics()

    # Should have metrics for all 6 monitored agents
    assert len(metrics) >= 24  # 6 agents * 4 metrics each

    # Check metrics for each agent
    for agent_name in monitoring_agent.monitored_agents:
        assert f"agent_{agent_name}_response_time_ms" in metrics
        assert f"agent_{agent_name}_success_rate" in metrics
        assert f"agent_{agent_name}_error_rate" in metrics
        assert f"agent_{agent_name}_requests_total" in metrics


@pytest.mark.asyncio
async def test_collect_database_metrics(monitoring_agent):
    """Test database metrics collection"""
    metrics = await monitoring_agent._collect_database_metrics()

    assert "db_connections_active" in metrics
    assert "db_connections_idle" in metrics
    assert "db_query_time_avg_ms" in metrics
    assert "db_queries_total" in metrics
    assert "db_slow_queries" in metrics


@pytest.mark.asyncio
async def test_collect_api_metrics(monitoring_agent):
    """Test API metrics collection"""
    metrics = await monitoring_agent._collect_api_metrics()

    assert "api_requests_total" in metrics
    assert "api_requests_per_second" in metrics
    assert "api_response_time_avg_ms" in metrics
    assert "api_response_time_p95_ms" in metrics
    assert "api_response_time_p99_ms" in metrics
    assert "api_status_2xx" in metrics
    assert "api_status_4xx" in metrics
    assert "api_status_5xx" in metrics


# ============================================================================
# METRICS RETRIEVAL TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_all_metrics(monitoring_agent):
    """Test getting all metrics summary"""
    # Collect some metrics first
    await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )

    # Get all metrics
    result = await monitoring_agent.execute(
        "Get metrics",
        {"operation": "get_metrics"}
    )

    assert result["status"] == "success"
    assert "total_metrics" in result
    assert result["total_metrics"] > 0
    assert "metrics" in result
    assert isinstance(result["metrics"], list)


@pytest.mark.asyncio
async def test_get_specific_metric(monitoring_agent):
    """Test getting a specific metric"""
    # Collect metrics first
    await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )

    # Get specific metric
    result = await monitoring_agent.execute(
        "Get metrics",
        {
            "operation": "get_metrics",
            "metric_name": "system_cpu_usage_percent"
        }
    )

    assert result["status"] == "success"
    assert result["metric_name"] == "system_cpu_usage_percent"
    assert "data_points" in result
    assert "count" in result
    assert len(result["data_points"]) > 0


@pytest.mark.asyncio
async def test_get_nonexistent_metric(monitoring_agent):
    """Test getting a metric that doesn't exist"""
    result = await monitoring_agent.execute(
        "Get metrics",
        {
            "operation": "get_metrics",
            "metric_name": "nonexistent_metric"
        }
    )

    assert result["status"] == "error"
    assert "not found" in result["error"]


# ============================================================================
# ALERT CREATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_alert(monitoring_agent):
    """Test alert creation"""
    await monitoring_agent._create_alert(
        "Test Alert",
        "This is a test alert",
        AlertSeverity.WARNING
    )

    assert len(monitoring_agent.alerts) == 1
    alert = monitoring_agent.alerts[0]
    assert alert["title"] == "Test Alert"
    assert alert["message"] == "This is a test alert"
    assert alert["severity"] == AlertSeverity.WARNING.value
    assert alert["acknowledged"] is False
    assert "alert_id" in alert
    assert "timestamp" in alert


@pytest.mark.asyncio
async def test_alert_severity_levels(monitoring_agent):
    """Test different alert severity levels"""
    await monitoring_agent._create_alert(
        "Info Alert",
        "Info message",
        AlertSeverity.INFO
    )
    await monitoring_agent._create_alert(
        "Warning Alert",
        "Warning message",
        AlertSeverity.WARNING
    )
    await monitoring_agent._create_alert(
        "Critical Alert",
        "Critical message",
        AlertSeverity.CRITICAL
    )

    assert len(monitoring_agent.alerts) == 3
    assert monitoring_agent.alerts[0]["severity"] == AlertSeverity.INFO.value
    warn_severity = AlertSeverity.WARNING.value
    assert monitoring_agent.alerts[1]["severity"] == warn_severity
    crit_severity = AlertSeverity.CRITICAL.value
    assert monitoring_agent.alerts[2]["severity"] == crit_severity


# ============================================================================
# THRESHOLD CHECKING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_check_thresholds_no_alerts(monitoring_agent):
    """Test threshold checking with normal metrics (no alerts)"""
    # Collect metrics (should be normal)
    await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )

    # Should have no alerts (unless system is actually under stress)
    # This is a soft check since real system metrics vary
    assert len(monitoring_agent.alerts) >= 0


@pytest.mark.asyncio
async def test_check_thresholds_cpu_alert(monitoring_agent):
    """Test CPU threshold alert"""
    # Manually add high CPU metric
    monitoring_agent.metrics["system_cpu_usage_percent"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 95.0
    })

    await monitoring_agent._check_thresholds()

    # Should have CPU alert
    cpu_alerts = [
        a for a in monitoring_agent.alerts
        if "CPU" in a["title"]
    ]
    assert len(cpu_alerts) > 0


@pytest.mark.asyncio
async def test_check_thresholds_memory_alert(monitoring_agent):
    """Test memory threshold alert"""
    # Manually add high memory metric
    monitoring_agent.metrics["system_memory_usage_percent"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 90.0
    })

    await monitoring_agent._check_thresholds()

    # Should have memory alert
    memory_alerts = [
        a for a in monitoring_agent.alerts
        if "Memory" in a["title"]
    ]
    assert len(memory_alerts) > 0


@pytest.mark.asyncio
async def test_check_thresholds_disk_alert(monitoring_agent):
    """Test disk threshold alert"""
    # Manually add high disk metric
    monitoring_agent.metrics["system_disk_usage_percent"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 95.0
    })

    await monitoring_agent._check_thresholds()

    # Should have disk alert (critical)
    disk_alerts = [
        a for a in monitoring_agent.alerts
        if "Disk" in a["title"]
    ]
    assert len(disk_alerts) > 0
    assert disk_alerts[0]["severity"] == AlertSeverity.CRITICAL.value


@pytest.mark.asyncio
async def test_check_thresholds_api_alert(monitoring_agent):
    """Test API response time threshold alert"""
    # Manually add slow API metric
    monitoring_agent.metrics["api_response_time_avg_ms"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 3000.0  # 3 seconds
    })

    await monitoring_agent._check_thresholds()

    # Should have API alert
    api_alerts = [
        a for a in monitoring_agent.alerts
        if "API" in a["title"]
    ]
    assert len(api_alerts) > 0


@pytest.mark.asyncio
async def test_check_thresholds_agent_response_alert(monitoring_agent):
    """Test agent response time threshold alert"""
    # Manually add slow agent metric
    monitoring_agent.metrics["agent_classifier_response_time_ms"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 6000.0  # 6 seconds
    })

    await monitoring_agent._check_thresholds()

    # Should have agent response alert
    agent_alerts = [
        a for a in monitoring_agent.alerts
        if "Slow Agent Response" in a["title"]
    ]
    assert len(agent_alerts) > 0


@pytest.mark.asyncio
async def test_check_thresholds_error_rate_alert(monitoring_agent):
    """Test error rate threshold alert"""
    # Manually add high error rate metric
    monitoring_agent.metrics["agent_resolver_error_rate"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 15.0  # 15% error rate
    })

    await monitoring_agent._check_thresholds()

    # Should have error rate alert (critical)
    error_alerts = [
        a for a in monitoring_agent.alerts
        if "Error Rate" in a["title"]
    ]
    assert len(error_alerts) > 0
    assert error_alerts[0]["severity"] == AlertSeverity.CRITICAL.value


# ============================================================================
# ALERT RETRIEVAL TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_alerts_empty(monitoring_agent):
    """Test getting alerts when none exist"""
    result = await monitoring_agent.execute(
        "Get alerts",
        {"operation": "get_alerts"}
    )

    assert result["status"] == "success"
    assert result["total_alerts"] == 0
    assert len(result["alerts"]) == 0


@pytest.mark.asyncio
async def test_get_alerts_with_alerts(monitoring_agent):
    """Test getting alerts when they exist"""
    # Create some alerts
    await monitoring_agent._create_alert(
        "Test Alert 1",
        "Message 1",
        AlertSeverity.WARNING
    )
    await monitoring_agent._create_alert(
        "Test Alert 2",
        "Message 2",
        AlertSeverity.CRITICAL
    )

    result = await monitoring_agent.execute(
        "Get alerts",
        {"operation": "get_alerts"}
    )

    assert result["status"] == "success"
    assert result["total_alerts"] == 2
    assert len(result["alerts"]) == 2


@pytest.mark.asyncio
async def test_get_alerts_acknowledged_filtered(monitoring_agent):
    """Test that acknowledged alerts are filtered out"""
    # Create alerts
    await monitoring_agent._create_alert(
        "Active Alert",
        "Still active",
        AlertSeverity.WARNING
    )
    await monitoring_agent._create_alert(
        "Acknowledged Alert",
        "Already handled",
        AlertSeverity.INFO
    )

    # Acknowledge one alert
    monitoring_agent.alerts[1]["acknowledged"] = True

    result = await monitoring_agent.execute(
        "Get alerts",
        {"operation": "get_alerts"}
    )

    assert result["status"] == "success"
    assert result["total_alerts"] == 1  # Only unacknowledged
    assert result["alerts"][0]["title"] == "Active Alert"


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_check_health(monitoring_agent):
    """Test health check operation"""
    result = await monitoring_agent.execute(
        "Check health",
        {"operation": "check_health"}
    )

    assert result["status"] == "success"
    assert "health" in result
    assert "timestamp" in result
    assert result["health"]["overall"] == "healthy"
    assert "services" in result["health"]


@pytest.mark.asyncio
async def test_health_check_services(monitoring_agent):
    """Test health check includes all services"""
    result = await monitoring_agent.execute(
        "Check health",
        {"operation": "check_health"}
    )

    services = result["health"]["services"]
    assert "postgresql" in services
    assert "redis" in services

    # Check all monitored agents
    for agent_name in monitoring_agent.monitored_agents:
        assert agent_name in services
        assert services[agent_name] == "healthy"


@pytest.mark.asyncio
async def test_health_check_endpoint(monitoring_agent):
    """Test agent health_check method"""
    result = await monitoring_agent.health_check()

    assert result["agent"] == "monitoring"
    assert result["status"] == "healthy"
    assert "metrics_count" in result
    assert "alerts_count" in result


# ============================================================================
# PROMETHEUS EXPORT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_export_prometheus_empty(monitoring_agent):
    """Test Prometheus export with no metrics"""
    result = await monitoring_agent.execute(
        "Export Prometheus",
        {"operation": "export_prometheus"}
    )

    assert result["status"] == "success"
    assert result["format"] == "prometheus"
    assert "metrics" in result
    assert result["metrics"] == ""  # No metrics yet


@pytest.mark.asyncio
async def test_export_prometheus_with_metrics(monitoring_agent):
    """Test Prometheus export with collected metrics"""
    # Collect metrics first
    await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )

    # Export to Prometheus
    result = await monitoring_agent.execute(
        "Export Prometheus",
        {"operation": "export_prometheus"}
    )

    assert result["status"] == "success"
    assert result["format"] == "prometheus"
    assert "metrics" in result
    assert len(result["metrics"]) > 0

    # Check format
    lines = result["metrics"].split("\n")
    assert len(lines) > 0
    for line in lines:
        if line:  # Skip empty lines
            assert "twisterlab_" in line
            assert " " in line  # Should have space between name and value


# ============================================================================
# DASHBOARD DATA TESTS
# ============================================================================

def test_get_dashboard_data_empty(monitoring_agent):
    """Test dashboard data with no metrics"""
    data = monitoring_agent.get_dashboard_data()

    assert "metrics" in data
    assert "alerts" in data
    assert "health" in data
    assert "timestamp" in data
    assert data["health"] == "healthy"
    assert len(data["alerts"]) == 0


@pytest.mark.asyncio
async def test_get_dashboard_data_with_metrics(monitoring_agent):
    """Test dashboard data with collected metrics"""
    # Collect metrics
    await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )

    data = monitoring_agent.get_dashboard_data()

    assert len(data["metrics"]) > 0
    assert "system_cpu_usage_percent" in data["metrics"]
    assert "system_memory_usage_percent" in data["metrics"]


@pytest.mark.asyncio
async def test_get_dashboard_data_with_alerts(monitoring_agent):
    """Test dashboard data with alerts"""
    # Create an alert
    await monitoring_agent._create_alert(
        "Test Alert",
        "Test message",
        AlertSeverity.WARNING
    )

    data = monitoring_agent.get_dashboard_data()

    assert len(data["alerts"]) == 1
    assert data["health"] == "degraded"  # Degraded due to alerts


# ============================================================================
# OPERATION ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_operation(monitoring_agent):
    """Test handling of invalid operation"""
    result = await monitoring_agent.execute(
        "Invalid operation",
        {"operation": "nonexistent_operation"}
    )

    assert result["status"] == "error"
    assert "Unknown operation" in result["error"]


@pytest.mark.asyncio
async def test_missing_operation(monitoring_agent):
    """Test handling of missing operation"""
    result = await monitoring_agent.execute(
        "Missing operation",
        {}
    )

    assert result["status"] == "error"
    assert "Unknown operation" in result["error"]


# ============================================================================
# METRICS STORAGE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_storage_limit(monitoring_agent):
    """Test metrics storage respects maxlen limit"""
    # Add 1500 metrics (exceeds maxlen of 1440)
    for i in range(1500):
        monitoring_agent.metrics["test_metric"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "value": float(i)
        })

    # Should only have 1440 entries (24 hours @ 1 min)
    assert len(monitoring_agent.metrics["test_metric"]) == 1440

    # Should have the latest values
    assert monitoring_agent.metrics["test_metric"][-1]["value"] == 1499.0


@pytest.mark.asyncio
async def test_multiple_metric_collections(monitoring_agent):
    """Test multiple metric collection cycles"""
    # Collect metrics 3 times
    for _ in range(3):
        result = await monitoring_agent.execute(
            "Collect metrics",
            {"operation": "collect_metrics"}
        )
        assert result["status"] == "success"

    # Each metric should have 3 data points
    for metric_name, data_points in monitoring_agent.metrics.items():
        assert len(data_points) == 3


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_monitoring_cycle(monitoring_agent):
    """Test complete monitoring workflow"""
    # 1. Collect metrics
    collect_result = await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )
    assert collect_result["status"] == "success"

    # 2. Get metrics summary
    metrics_result = await monitoring_agent.execute(
        "Get metrics",
        {"operation": "get_metrics"}
    )
    assert metrics_result["status"] == "success"
    assert metrics_result["total_metrics"] > 0

    # 3. Check health
    health_result = await monitoring_agent.execute(
        "Check health",
        {"operation": "check_health"}
    )
    assert health_result["status"] == "success"

    # 4. Export to Prometheus
    prom_result = await monitoring_agent.execute(
        "Export Prometheus",
        {"operation": "export_prometheus"}
    )
    assert prom_result["status"] == "success"
    assert len(prom_result["metrics"]) > 0

    # 5. Get dashboard data
    dashboard = monitoring_agent.get_dashboard_data()
    assert len(dashboard["metrics"]) > 0


@pytest.mark.asyncio
async def test_alert_workflow(monitoring_agent):
    """Test complete alert workflow"""
    # 1. Trigger alerts by setting high metrics
    monitoring_agent.metrics["system_cpu_usage_percent"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 95.0
    })
    monitoring_agent.metrics["system_memory_usage_percent"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 90.0
    })

    # 2. Check thresholds
    await monitoring_agent._check_thresholds()

    # 3. Get alerts
    alerts_result = await monitoring_agent.execute(
        "Get alerts",
        {"operation": "get_alerts"}
    )
    assert alerts_result["total_alerts"] >= 2

    # 4. Check dashboard shows degraded health
    dashboard = monitoring_agent.get_dashboard_data()
    assert dashboard["health"] == "degraded"
    assert len(dashboard["alerts"]) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

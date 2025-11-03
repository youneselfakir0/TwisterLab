# AGENT 6: MONITORING AGENT - COMPLETE IMPLEMENTATION PLAN

**Priority:** 6
**Status:** Planning Phase
**Estimated Lines:** 400+
**Dependencies:** All agents, Prometheus, Grafana (optional)

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 Role in System
The Monitoring-AgentAgent provides **continuous performance monitoring, metrics collection, and alerting** for the entire TwisterLab system.

**Monitoring Targets:**
- All agent performance (response time, success rate, error rate)
- System resources (CPU, memory, disk, network)
- Database performance (query time, connection pool)
- Redis cache (hit rate, memory usage)
- API endpoints (request rate, latency)

### 1.2 Core Responsibilities
1. **Metrics Collection** - Gather performance metrics every 60 seconds
2. **Health Checks** - Verify all services are operational
3. **Anomaly Detection** - Identify performance degradation
4. **Alerting** - Notify on critical issues
5. **Dashboard Data** - Export metrics for visualization

### 1.3 Metrics Architecture

**Collection Flow:**
```
Agents → Monitoring Agent → Prometheus → Grafana
   ↓                             ↓
Database                     Alertmanager
```

**Metrics Categories:**
- **Agent Metrics:** Ticket processing rate, resolution time, error rate
- **System Metrics:** CPU, memory, disk I/O, network
- **Database Metrics:** Query performance, connection count
- **Cache Metrics:** Hit/miss ratio, memory usage
- **API Metrics:** Request rate, response time, status codes

---

## 2. CODE TEMPLATE

**File:** `agents/support/monitoring_agent.py`

```python
"""
TwisterLab - Monitoring Agent
Continuous performance monitoring and alerting
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from collections import defaultdict, deque
import psutil

from ..base import TwisterAgent
from ..database.config import get_db

logger = logging.getLogger(__name__)


class AlertSeverity:
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitoringAgent(TwisterAgent):
    """
    Agent for continuous system monitoring and alerting.
    """

    def __init__(self):
        super().__init__(
            name="monitoring-agent",
            display_name="System Monitoring Agent",
            description="Continuous performance monitoring, metrics collection, and alerting",
            role="monitoring",
            instructions=self._get_instructions(),
            tools=self._define_tools(),
            model="llama-3.2",
            temperature=0.1,
            metadata={
                "department": "Infrastructure",
                "collection_interval": "60 seconds",
                "retention_hours": 24,
                "alerting_enabled": True
            }
        )

        # Metrics storage (in-memory, would use time-series DB in production)
        self.metrics = defaultdict(lambda: deque(maxlen=1440))  # 24 hours at 1-min intervals

        # Alert history
        self.alerts = []

        # Performance thresholds
        self.thresholds = {
            "cpu_usage": 80.0,  # %
            "memory_usage": 85.0,  # %
            "disk_usage": 90.0,  # %
            "api_response_time": 2.0,  # seconds
            "error_rate": 0.1,  # 10%
            "agent_response_time": 5.0  # seconds
        }

    def _get_instructions(self) -> str:
        return """
        You are the Monitoring Agent, responsible for system health and performance monitoring.

        Your responsibilities:
        1. Collect metrics from all agents every 60 seconds
        2. Monitor system resources (CPU, memory, disk)
        3. Track API performance (latency, error rates)
        4. Detect anomalies and performance degradation
        5. Generate alerts on threshold violations
        6. Export metrics for visualization (Prometheus, Grafana)

        Alert Conditions:
        - CPU usage > 80%
        - Memory usage > 85%
        - Disk usage > 90%
        - API response time > 2 seconds
        - Error rate > 10%
        - Agent not responding

        Always log all metrics for historical analysis.
        """

    def _define_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "collect_metrics",
                    "description": "Collect system and agent metrics",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_metrics",
                    "description": "Get collected metrics",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric_name": {"type": "string"},
                            "time_range": {"type": "string"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_health",
                    "description": "Check health of all services",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_alerts",
                    "description": "Get active alerts",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "export_prometheus",
                    "description": "Export metrics in Prometheus format",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main execution method"""
        try:
            logger.info(f"Monitoring Agent executing: {task}")

            operation = context.get("operation", "collect_metrics") if context else "collect_metrics"

            if operation == "collect_metrics":
                result = await self._collect_metrics()
            elif operation == "get_metrics":
                metric_name = context.get("metric_name") if context else None
                result = await self._get_metrics(metric_name)
            elif operation == "check_health":
                result = await self._check_health()
            elif operation == "get_alerts":
                result = await self._get_alerts()
            elif operation == "export_prometheus":
                result = await self._export_prometheus()
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }

            return result

        except Exception as e:
            logger.error(f"Error in monitoring execution: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect all system and agent metrics"""
        try:
            timestamp = datetime.now(timezone.utc)
            logger.info("Collecting metrics")

            metrics_collected = {}

            # System metrics
            system_metrics = await self._collect_system_metrics()
            metrics_collected.update(system_metrics)

            # Agent metrics
            agent_metrics = await self._collect_agent_metrics()
            metrics_collected.update(agent_metrics)

            # Database metrics
            db_metrics = await self._collect_database_metrics()
            metrics_collected.update(db_metrics)

            # API metrics
            api_metrics = await self._collect_api_metrics()
            metrics_collected.update(api_metrics)

            # Store metrics
            for metric_name, metric_value in metrics_collected.items():
                self.metrics[metric_name].append({
                    "timestamp": timestamp.isoformat(),
                    "value": metric_value
                })

            # Check thresholds and generate alerts
            await self._check_thresholds(metrics_collected)

            return {
                "status": "success",
                "metrics_collected": len(metrics_collected),
                "timestamp": timestamp.isoformat(),
                "metrics": metrics_collected
            }

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect system resource metrics"""
        try:
            metrics = {}

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["system_cpu_usage_percent"] = cpu_percent

            # Memory usage
            memory = psutil.virtual_memory()
            metrics["system_memory_usage_percent"] = memory.percent
            metrics["system_memory_used_bytes"] = memory.used
            metrics["system_memory_available_bytes"] = memory.available

            # Disk usage
            disk = psutil.disk_usage('/')
            metrics["system_disk_usage_percent"] = disk.percent
            metrics["system_disk_used_bytes"] = disk.used
            metrics["system_disk_free_bytes"] = disk.free

            # Network I/O
            net_io = psutil.net_io_counters()
            metrics["system_network_bytes_sent"] = net_io.bytes_sent
            metrics["system_network_bytes_recv"] = net_io.bytes_recv

            logger.debug(f"System metrics collected: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}

    async def _collect_agent_metrics(self) -> Dict[str, float]:
        """Collect metrics from all agents"""
        try:
            metrics = {}

            # Agent list
            agents = [
                "classifier",
                "resolver",
                "desktop_commander",
                "maestro",
                "sync",
                "backup"
            ]

            for agent_name in agents:
                # Would query actual agent health endpoints
                # For now, simulate metrics

                # Response time (ms)
                metrics[f"agent_{agent_name}_response_time_ms"] = 150.0

                # Success rate (%)
                metrics[f"agent_{agent_name}_success_rate_percent"] = 95.0

                # Error rate (%)
                metrics[f"agent_{agent_name}_error_rate_percent"] = 5.0

                # Tickets processed (count)
                metrics[f"agent_{agent_name}_tickets_processed"] = 10.0

            logger.debug(f"Agent metrics collected: {len(metrics)} metrics")
            return metrics

        except Exception as e:
            logger.error(f"Error collecting agent metrics: {e}")
            return {}

    async def _collect_database_metrics(self) -> Dict[str, float]:
        """Collect database performance metrics"""
        try:
            metrics = {}

            # Would query actual database metrics
            # For now, simulate

            metrics["database_connections_active"] = 5.0
            metrics["database_connections_idle"] = 10.0
            metrics["database_query_time_avg_ms"] = 50.0
            metrics["database_slow_queries"] = 2.0

            logger.debug("Database metrics collected")
            return metrics

        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return {}

    async def _collect_api_metrics(self) -> Dict[str, float]:
        """Collect API performance metrics"""
        try:
            metrics = {}

            # Would integrate with FastAPI metrics
            # For now, simulate

            metrics["api_requests_total"] = 100.0
            metrics["api_requests_success"] = 95.0
            metrics["api_requests_failed"] = 5.0
            metrics["api_response_time_avg_ms"] = 200.0
            metrics["api_response_time_p95_ms"] = 500.0
            metrics["api_response_time_p99_ms"] = 1000.0

            logger.debug("API metrics collected")
            return metrics

        except Exception as e:
            logger.error(f"Error collecting API metrics: {e}")
            return {}

    async def _check_thresholds(self, metrics: Dict[str, float]):
        """Check metrics against thresholds and generate alerts"""
        try:
            # Check CPU
            cpu_usage = metrics.get("system_cpu_usage_percent", 0)
            if cpu_usage > self.thresholds["cpu_usage"]:
                await self._create_alert(
                    "High CPU Usage",
                    f"CPU usage is {cpu_usage}% (threshold: {self.thresholds['cpu_usage']}%)",
                    AlertSeverity.WARNING
                )

            # Check Memory
            memory_usage = metrics.get("system_memory_usage_percent", 0)
            if memory_usage > self.thresholds["memory_usage"]:
                await self._create_alert(
                    "High Memory Usage",
                    f"Memory usage is {memory_usage}% (threshold: {self.thresholds['memory_usage']}%)",
                    AlertSeverity.WARNING
                )

            # Check Disk
            disk_usage = metrics.get("system_disk_usage_percent", 0)
            if disk_usage > self.thresholds["disk_usage"]:
                await self._create_alert(
                    "High Disk Usage",
                    f"Disk usage is {disk_usage}% (threshold: {self.thresholds['disk_usage']}%)",
                    AlertSeverity.CRITICAL
                )

            # Check API response time
            api_response_time = metrics.get("api_response_time_avg_ms", 0) / 1000.0
            if api_response_time > self.thresholds["api_response_time"]:
                await self._create_alert(
                    "Slow API Response",
                    f"API response time is {api_response_time}s (threshold: {self.thresholds['api_response_time']}s)",
                    AlertSeverity.WARNING
                )

        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")

    async def _create_alert(
        self,
        title: str,
        message: str,
        severity: str
    ):
        """Create and store an alert"""
        try:
            alert = {
                "alert_id": f"ALERT-{len(self.alerts) + 1:04d}",
                "title": title,
                "message": message,
                "severity": severity,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "acknowledged": False
            }

            self.alerts.append(alert)

            logger.warning(f"[{severity.upper()}] {title}: {message}")

            # In production, would send to alerting system
            # (Email, Slack, PagerDuty, etc.)

        except Exception as e:
            logger.error(f"Error creating alert: {e}")

    async def _get_metrics(self, metric_name: Optional[str] = None) -> Dict[str, Any]:
        """Get collected metrics"""
        try:
            if metric_name:
                # Get specific metric
                if metric_name in self.metrics:
                    return {
                        "status": "success",
                        "metric_name": metric_name,
                        "data_points": list(self.metrics[metric_name])
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Metric '{metric_name}' not found"
                    }
            else:
                # Get all metrics summary
                return {
                    "status": "success",
                    "total_metrics": len(self.metrics),
                    "metrics": list(self.metrics.keys())
                }

        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _check_health(self) -> Dict[str, Any]:
        """Check health of all services"""
        try:
            health_status = {
                "overall": "healthy",
                "services": {}
            }

            # Check PostgreSQL
            try:
                async for session in get_db():
                    # Simple query to check connection
                    await session.execute("SELECT 1")
                    health_status["services"]["postgresql"] = "healthy"
                    break
            except Exception as e:
                health_status["services"]["postgresql"] = "unhealthy"
                health_status["overall"] = "degraded"
                logger.error(f"PostgreSQL health check failed: {e}")

            # Check Redis
            try:
                # Would check Redis connection
                health_status["services"]["redis"] = "healthy"
            except Exception as e:
                health_status["services"]["redis"] = "unhealthy"
                health_status["overall"] = "degraded"
                logger.error(f"Redis health check failed: {e}")

            # Check agents
            agents = ["classifier", "resolver", "desktop_commander", "maestro"]
            for agent_name in agents:
                # Would ping agent health endpoint
                health_status["services"][agent_name] = "healthy"

            return {
                "status": "success",
                "health": health_status,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking health: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _get_alerts(self) -> Dict[str, Any]:
        """Get active alerts"""
        try:
            # Filter unacknowledged alerts
            active_alerts = [
                alert for alert in self.alerts
                if not alert.get("acknowledged", False)
            ]

            return {
                "status": "success",
                "total_alerts": len(active_alerts),
                "alerts": active_alerts
            }

        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _export_prometheus(self) -> Dict[str, Any]:
        """Export metrics in Prometheus format"""
        try:
            prometheus_metrics = []

            # Convert metrics to Prometheus format
            for metric_name, data_points in self.metrics.items():
                if data_points:
                    latest = data_points[-1]
                    prometheus_metrics.append(
                        f"{metric_name} {latest['value']}"
                    )

            return {
                "status": "success",
                "format": "prometheus",
                "metrics": "\n".join(prometheus_metrics)
            }

        except Exception as e:
            logger.error(f"Error exporting Prometheus metrics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard visualization"""
        try:
            # Get latest values for key metrics
            latest_metrics = {}

            for metric_name, data_points in self.metrics.items():
                if data_points:
                    latest_metrics[metric_name] = data_points[-1]["value"]

            # Get active alerts
            active_alerts = [
                alert for alert in self.alerts
                if not alert.get("acknowledged", False)
            ]

            return {
                "metrics": latest_metrics,
                "alerts": active_alerts,
                "health": "healthy" if len(active_alerts) == 0 else "degraded",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
```

---

## 3. API ENDPOINTS

**Add to `agents/api/monitoring.py`:**

```python
from fastapi import APIRouter
from agents.support.monitoring_agent import MonitoringAgent

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Initialize Monitoring Agent
monitoring_agent = MonitoringAgent()


@router.get("/metrics")
async def get_metrics(metric_name: str = None):
    """Get collected metrics"""
    return await monitoring_agent.execute(
        "Get metrics",
        {"operation": "get_metrics", "metric_name": metric_name}
    )


@router.get("/health")
async def check_health():
    """Check system health"""
    return await monitoring_agent.execute(
        "Check health",
        {"operation": "check_health"}
    )


@router.get("/alerts")
async def get_alerts():
    """Get active alerts"""
    return await monitoring_agent.execute(
        "Get alerts",
        {"operation": "get_alerts"}
    )


@router.get("/prometheus")
async def export_prometheus():
    """Export metrics in Prometheus format"""
    result = await monitoring_agent.execute(
        "Export Prometheus",
        {"operation": "export_prometheus"}
    )
    return result.get("metrics", "")


@router.get("/dashboard")
async def get_dashboard_data():
    """Get dashboard data"""
    return monitoring_agent.get_dashboard_data()
```

---

## 4. TESTING

```python
# tests/test_monitoring_agent.py

@pytest.mark.asyncio
async def test_collect_metrics():
    """Test metrics collection"""
    monitoring_agent = MonitoringAgent()

    result = await monitoring_agent.execute(
        "Collect metrics",
        {"operation": "collect_metrics"}
    )

    assert result["status"] == "success"
    assert "metrics_collected" in result
    assert result["metrics_collected"] > 0

@pytest.mark.asyncio
async def test_health_check():
    """Test health check"""
    monitoring_agent = MonitoringAgent()

    result = await monitoring_agent.execute(
        "Check health",
        {"operation": "check_health"}
    )

    assert result["status"] == "success"
    assert "health" in result

@pytest.mark.asyncio
async def test_prometheus_export():
    """Test Prometheus export"""
    monitoring_agent = MonitoringAgent()

    # Collect some metrics first
    await monitoring_agent.execute("Collect metrics", {"operation": "collect_metrics"})

    # Export to Prometheus format
    result = await monitoring_agent.execute(
        "Export Prometheus",
        {"operation": "export_prometheus"}
    )

    assert result["status"] == "success"
    assert result["format"] == "prometheus"
```

---

## 5. DEPLOYMENT

**Environment Variables:**
```bash
MONITORING_INTERVAL=60
MONITORING_RETENTION_HOURS=24
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
ALERTING_EMAIL=alerts@example.com
ALERTING_SLACK_WEBHOOK=https://hooks.slack.com/...
```

**Prometheus Configuration (prometheus.yml):**
```yaml
scrape_configs:
  - job_name: 'twisterlab'
    scrape_interval: 60s
    static_configs:
      - targets: ['monitoring-agent:8000']
```

---

## 6. GRAFANA DASHBOARD

**Dashboard Components:**
- System resources (CPU, Memory, Disk)
- Agent performance (response time, success rate)
- Database metrics (connections, query time)
- API metrics (request rate, latency)
- Active alerts panel

---

**Implementation Complete!** ✅

All 6 agent plans are now ready for implementation. See [AGENTS_MASTER_ROADMAP.md](AGENTS_MASTER_ROADMAP.md) for the complete overview.

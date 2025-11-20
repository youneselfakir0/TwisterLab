#!/usr/bin/env python3
"""
TwisterLab Performance Monitoring System

Comprehensive monitoring and metrics collection for the multi-agent system.
Integrates with Prometheus for metrics collection and Grafana for visualization.

Features:
- Agent performance metrics (response time, success rate, error rate)
- Workflow execution metrics (duration, success rate, step completion)
- System health metrics (CPU, memory, disk usage)
- MCP communication metrics (message throughput, latency)
- Alerting system for performance degradation and failures
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import psutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.mcp.agent_communication_system import MCPAgentCommunicationSystem
from agents.registry import agent_registry
from agents.monitoring.alerting_system import alerting_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"  # Monotonically increasing value
    GAUGE = "gauge"      # Value that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"   # Similar to histogram but with quantiles


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Represents a single metric"""
    name: str
    help_text: str
    type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    timestamp: Optional[float] = None

    def to_prometheus_format(self) -> str:
        """Convert metric to Prometheus format"""
        label_str = ""
        if self.labels:
            label_parts = [f'{k}="{v}"' for k, v in self.labels.items()]
            label_str = f"{{{','.join(label_parts)}}}"

        if self.timestamp:
            return f"# HELP {self.name} {self.help_text}\n# TYPE {self.name} {self.type.value}\n{self.name}{label_str} {self.value} {int(self.timestamp * 1000)}"
        else:
            return f"# HELP {self.name} {self.help_text}\n# TYPE {self.name} {self.type.value}\n{self.name}{label_str} {self.value}"


@dataclass
class Alert:
    """Represents an alert condition"""
    name: str
    description: str
    severity: AlertSeverity
    condition: Callable[[], bool]
    active: bool = False
    last_triggered: Optional[float] = None
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects and manages metrics for the TwisterLab system"""

    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self._lock = threading.Lock()

    def register_metric(self, metric: Metric):
        """Register a new metric"""
        with self._lock:
            self.metrics[metric.name] = metric

    def update_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Update a metric value"""
        with self._lock:
            if name in self.metrics:
                self.metrics[name].value = value
                self.metrics[name].timestamp = time.time()
                if labels:
                    self.metrics[name].labels.update(labels)

    def increment_counter(self, name: str, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        with self._lock:
            if name in self.metrics and self.metrics[name].type == MetricType.COUNTER:
                self.metrics[name].value += 1
                self.metrics[name].timestamp = time.time()
                if labels:
                    self.metrics[name].labels.update(labels)

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a value for a histogram metric"""
        with self._lock:
            if name in self.metrics and self.metrics[name].type == MetricType.HISTOGRAM:
                # For simplicity, we'll just update the gauge with the latest value
                # In a real implementation, you'd maintain buckets
                self.metrics[name].value = value
                self.metrics[name].timestamp = time.time()
                if labels:
                    self.metrics[name].labels.update(labels)

    def get_prometheus_output(self) -> str:
        """Get all metrics in Prometheus format"""
        with self._lock:
            return "\n".join([metric.to_prometheus_format() for metric in self.metrics.values()])


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.alerts: Dict[str, Alert] = {}
        self.metrics = metrics_collector
        self._lock = threading.Lock()

    def register_alert(self, alert: Alert):
        """Register a new alert"""
        with self._lock:
            self.alerts[alert.name] = alert

    def check_alerts(self) -> List[Alert]:
        """Check all alerts and return triggered ones"""
        triggered = []
        with self._lock:
            for alert in self.alerts.values():
                try:
                    is_triggered = alert.condition()
                    if is_triggered and not alert.active:
                        alert.active = True
                        alert.last_triggered = time.time()
                        triggered.append(alert)

                        # Use the new alerting system
                        asyncio.create_task(self._trigger_alert_async(alert.name, {
                            "severity": alert.severity.value,
                            "description": alert.description,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }))

                    elif not is_triggered and alert.active:
                        alert.active = False
                        logger.info(f"Alert resolved: {alert.name}")
                except Exception as e:
                    logger.error(f"Error checking alert {alert.name}: {e}")

        return triggered

    async def _trigger_alert_async(self, alert_name: str, metadata: Dict[str, Any]):
        """Trigger alert asynchronously using the alerting system"""
        try:
            await alerting_system.trigger_alert(alert_name, metadata)
        except Exception as e:
            logger.error(f"Failed to trigger alert {alert_name}: {e}")

    def get_active_alerts(self) -> List[Alert]:
        """Get currently active alerts"""
        with self._lock:
            return [alert for alert in self.alerts.values() if alert.active]


class PerformanceMonitor:
    """Main performance monitoring system"""

    def __init__(self, communication_system: MCPAgentCommunicationSystem):
        self.communication_system = communication_system
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.metrics_collector)
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False

        # Initialize metrics
        self._setup_metrics()

        # Initialize alerts
        self._setup_alerts()

    def _setup_metrics(self):
        """Set up all metrics to be collected"""

        # Agent metrics
        self.metrics_collector.register_metric(Metric(
            name="twisterlab_agent_requests_total",
            help_text="Total number of agent requests",
            type=MetricType.COUNTER
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_agent_requests_success_total",
            help_text="Total number of successful agent requests",
            type=MetricType.COUNTER
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_agent_requests_error_total",
            help_text="Total number of failed agent requests",
            type=MetricType.COUNTER
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_agent_response_time_seconds",
            help_text="Agent response time in seconds",
            type=MetricType.HISTOGRAM
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_agent_active_count",
            help_text="Number of currently active agents",
            type=MetricType.GAUGE
        ))

        # Workflow metrics
        self.metrics_collector.register_metric(Metric(
            name="twisterlab_workflow_executions_total",
            help_text="Total number of workflow executions",
            type=MetricType.COUNTER
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_workflow_executions_success_total",
            help_text="Total number of successful workflow executions",
            type=MetricType.COUNTER
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_workflow_executions_failed_total",
            help_text="Total number of failed workflow executions",
            type=MetricType.COUNTER
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_workflow_execution_duration_seconds",
            help_text="Workflow execution duration in seconds",
            type=MetricType.HISTOGRAM
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_workflow_active_count",
            help_text="Number of currently active workflows",
            type=MetricType.GAUGE
        ))

        # MCP Communication metrics
        self.metrics_collector.register_metric(Metric(
            name="twisterlab_mcp_messages_total",
            help_text="Total number of MCP messages",
            type=MetricType.COUNTER
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_mcp_message_latency_seconds",
            help_text="MCP message latency in seconds",
            type=MetricType.HISTOGRAM
        ))

        # System metrics
        self.metrics_collector.register_metric(Metric(
            name="twisterlab_system_cpu_usage_percent",
            help_text="System CPU usage percentage",
            type=MetricType.GAUGE
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_system_memory_usage_percent",
            help_text="System memory usage percentage",
            type=MetricType.GAUGE
        ))

        self.metrics_collector.register_metric(Metric(
            name="twisterlab_system_disk_usage_percent",
            help_text="System disk usage percentage",
            type=MetricType.GAUGE
        ))

    def _setup_alerts(self):
        """Set up alert conditions"""

        # High error rate alert
        self.alert_manager.register_alert(Alert(
            name="high_agent_error_rate",
            description="Agent error rate is above 10%",
            severity=AlertSeverity.WARNING,
            condition=lambda: self._calculate_error_rate() > 0.1
        ))

        # Workflow failure alert
        self.alert_manager.register_alert(Alert(
            name="workflow_failure_rate_high",
            description="Workflow failure rate is above 5%",
            severity=AlertSeverity.ERROR,
            condition=lambda: self._calculate_workflow_failure_rate() > 0.05
        ))

        # High system resource usage
        self.alert_manager.register_alert(Alert(
            name="high_cpu_usage",
            description="System CPU usage is above 90%",
            severity=AlertSeverity.WARNING,
            condition=lambda: psutil.cpu_percent() > 90
        ))

        self.alert_manager.register_alert(Alert(
            name="high_memory_usage",
            description="System memory usage is above 90%",
            severity=AlertSeverity.WARNING,
            condition=lambda: psutil.virtual_memory().percent > 90
        ))

        # Agent response time degradation
        self.alert_manager.register_alert(Alert(
            name="slow_agent_response",
            description="Average agent response time is above 30 seconds",
            severity=AlertSeverity.WARNING,
            condition=lambda: self._calculate_avg_response_time() > 30
        ))

    def _calculate_error_rate(self) -> float:
        """Calculate agent error rate"""
        total_requests = self.metrics_collector.metrics.get("twisterlab_agent_requests_total", Metric("", "", MetricType.COUNTER)).value
        error_requests = self.metrics_collector.metrics.get("twisterlab_agent_requests_error_total", Metric("", "", MetricType.COUNTER)).value

        if total_requests == 0:
            return 0.0
        return error_requests / total_requests

    def _calculate_workflow_failure_rate(self) -> float:
        """Calculate workflow failure rate"""
        total_workflows = self.metrics_collector.metrics.get("twisterlab_workflow_executions_total", Metric("", "", MetricType.COUNTER)).value
        failed_workflows = self.metrics_collector.metrics.get("twisterlab_workflow_executions_failed_total", Metric("", "", MetricType.COUNTER)).value

        if total_workflows == 0:
            return 0.0
        return failed_workflows / total_workflows

    def _calculate_avg_response_time(self) -> float:
        """Calculate average agent response time"""
        # This is a simplified calculation - in practice you'd maintain a sliding window
        response_time = self.metrics_collector.metrics.get("twisterlab_agent_response_time_seconds", Metric("", "", MetricType.HISTOGRAM)).value
        return response_time

    async def start_monitoring(self):
        """Start the monitoring system"""
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")

    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()

                # Collect agent metrics
                await self._collect_agent_metrics()

                # Check alerts
                triggered_alerts = self.alert_manager.check_alerts()
                if triggered_alerts:
                    await self._handle_alerts(triggered_alerts)

                # Log active alerts
                active_alerts = self.alert_manager.get_active_alerts()
                if active_alerts:
                    logger.warning(f"Active alerts: {[alert.name for alert in active_alerts]}")

                await asyncio.sleep(30)  # Collect metrics every 30 seconds

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.update_metric("twisterlab_system_cpu_usage_percent", cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics_collector.update_metric("twisterlab_system_memory_usage_percent", memory.percent)

            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics_collector.update_metric("twisterlab_system_disk_usage_percent", disk.percent)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def _collect_agent_metrics(self):
        """Collect agent-related metrics"""
        try:
            # Get active agents count
            active_agents = len(agent_registry.list_agents())
            self.metrics_collector.update_metric("twisterlab_agent_active_count", active_agents)

            # Get active workflows (this would need to be integrated with workflow orchestrator)
            # For now, we'll set it to 0
            self.metrics_collector.update_metric("twisterlab_workflow_active_count", 0)

        except Exception as e:
            logger.error(f"Error collecting agent metrics: {e}")

    async def _handle_alerts(self, alerts: List[Alert]):
        """Handle triggered alerts"""
        for alert in alerts:
            # In a real system, this would send notifications via email, Slack, etc.
            logger.warning(f"ALERT: {alert.name} ({alert.severity.value}) - {alert.description}")

            # You could integrate with notification services here
            # await self._send_notification(alert)

    def record_agent_request(self, agent_name: str, success: bool, response_time: float):
        """Record an agent request"""
        self.metrics_collector.increment_counter("twisterlab_agent_requests_total", {"agent": agent_name})

        if success:
            self.metrics_collector.increment_counter("twisterlab_agent_requests_success_total", {"agent": agent_name})
        else:
            self.metrics_collector.increment_counter("twisterlab_agent_requests_error_total", {"agent": agent_name})

        self.metrics_collector.observe_histogram("twisterlab_agent_response_time_seconds", response_time, {"agent": agent_name})

    def record_workflow_execution(self, workflow_name: str, success: bool, duration: float):
        """Record a workflow execution"""
        self.metrics_collector.increment_counter("twisterlab_workflow_executions_total", {"workflow": workflow_name})

        if success:
            self.metrics_collector.increment_counter("twisterlab_workflow_executions_success_total", {"workflow": workflow_name})
        else:
            self.metrics_collector.increment_counter("twisterlab_workflow_executions_failed_total", {"workflow": workflow_name})

        self.metrics_collector.observe_histogram("twisterlab_workflow_execution_duration_seconds", duration, {"workflow": workflow_name})

    def record_mcp_message(self, message_type: str, latency: float):
        """Record an MCP message"""
        self.metrics_collector.increment_counter("twisterlab_mcp_messages_total", {"type": message_type})
        self.metrics_collector.observe_histogram("twisterlab_mcp_message_latency_seconds", latency, {"type": message_type})

    def get_metrics_output(self) -> str:
        """Get all metrics in Prometheus format"""
        return self.metrics_collector.get_prometheus_output()

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        active_alerts = self.alert_manager.get_active_alerts()

        return {
            "status": "unhealthy" if active_alerts else "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_alerts": len(active_alerts),
            "alerts": [{"name": alert.name, "severity": alert.severity.value, "description": alert.description} for alert in active_alerts],
            "metrics": {
                "agents_active": int(self.metrics_collector.metrics.get("twisterlab_agent_active_count", Metric("", "", MetricType.GAUGE)).value),
                "cpu_usage": self.metrics_collector.metrics.get("twisterlab_system_cpu_usage_percent", Metric("", "", MetricType.GAUGE)).value,
                "memory_usage": self.metrics_collector.metrics.get("twisterlab_system_memory_usage_percent", Metric("", "", MetricType.GAUGE)).value,
                "disk_usage": self.metrics_collector.metrics.get("twisterlab_system_disk_usage_percent", Metric("", "", MetricType.GAUGE)).value,
            }
        }


# Example usage and testing
async def main():
    """Example usage of the performance monitoring system"""
    # Initialize communication system
    comm_system = MCPAgentCommunicationSystem()

    # Initialize performance monitor
    monitor = PerformanceMonitor(comm_system)

    # Start monitoring
    await monitor.start_monitoring()

    # Simulate some activity
    monitor.record_agent_request("monitoring", True, 2.5)
    monitor.record_agent_request("backup", False, 15.0)
    monitor.record_workflow_execution("system_maintenance", True, 45.0)
    monitor.record_mcp_message("task_request", 0.1)

    # Wait a bit for monitoring to collect data
    await asyncio.sleep(35)

    # Print metrics
    print("=== Prometheus Metrics ===")
    print(monitor.get_metrics_output())

    print("\n=== Health Status ===")
    print(json.dumps(monitor.get_health_status(), indent=2))

    # Stop monitoring
    await monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())

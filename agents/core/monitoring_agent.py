"""
MonitoringAgent - Real-time diagnostics and self-healing system.

This agent continuously monitors system health, diagnoses issues,
and triggers automated repairs when possible.

Responsibilities:
- Health checks for all services
- Performance monitoring
- Automated issue diagnosis
- Self-healing triggers
- Alert escalation
"""

from datetime import datetime
from typing import Any, Dict, List

from agents.base.base_agent import BaseAgent


class MonitoringAgent(BaseAgent):
    """
    Autonomous monitoring and self-healing agent.

    Capabilities:
    - Service health monitoring
    - Performance diagnostics
    - Automated repair triggers
    - Alert management
    """

    def __init__(self):
        super().__init__()
        self.name = "MonitoringAgent"
        self.priority = 1  # Highest priority for monitoring
        self.capabilities = [
            "health_check",
            "performance_monitoring",
            "diagnostic_analysis",
            "self_healing",
            "alert_management",
        ]

        # Monitoring thresholds
        self.thresholds = {
            "cpu_usage": 80.0,  # %
            "memory_usage": 85.0,  # %
            "disk_usage": 90.0,  # %
            "response_time": 2.0,  # seconds
            "error_rate": 5.0,  # %
        }

        # Self-healing actions
        self.healing_actions = {
            "high_memory": "restart_service",
            "high_cpu": "scale_service",
            "service_down": "restart_service",
            "db_connection_lost": "reconnect_db",
            "cache_miss_high": "invalidate_cache",
        }

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute monitoring cycle with diagnosis and repair.

        Args:
            context: Monitoring context (service_name, check_type, etc.)

        Returns:
            Dict with monitoring results and actions taken
        """
        try:
            # Validate context
            self._validate_context(context)

            # Log execution start
            await self.audit_log("monitoring_start", context)

            # Execute monitoring cycle
            results = await self._monitor_system(context)

            # Analyze results and diagnose issues
            diagnosis = await self._diagnose_issues(results)

            # Perform self-healing if issues found
            repairs = await self._perform_repairs(diagnosis)

            # Generate alerts if needed
            alerts = await self._generate_alerts(diagnosis, repairs)

            # Log completion
            await self.audit_log(
                "monitoring_complete",
                {
                    "results": results,
                    "diagnosis": diagnosis,
                    "repairs": repairs,
                    "alerts": alerts,
                },
            )

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "diagnosis": diagnosis,
                "repairs": repairs,
                "alerts": alerts,
            }

        except Exception as e:
            await self.audit_log("monitoring_failed", {"error": str(e)})
            raise

    async def _monitor_system(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor all system components."""
        results = {}

        # Health checks
        results["services"] = await self._check_service_health()
        results["database"] = await self._check_database_health()
        results["cache"] = await self._check_cache_health()
        results["performance"] = await self._check_performance_metrics()

        return results

    async def _diagnose_issues(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze monitoring results and diagnose issues."""
        issues = []

        # Check service health
        for service, status in results["services"].items():
            if not status.get("healthy", False):
                issues.append(
                    {
                        "type": "service_down",
                        "service": service,
                        "severity": "critical",
                        "description": f"Service {service} is not responding",
                        "suggested_action": "restart_service",
                    }
                )

        # Check performance thresholds
        perf = results.get("performance", {})
        if perf.get("cpu_usage", 0) > self.thresholds["cpu_usage"]:
            issues.append(
                {
                    "type": "high_cpu",
                    "service": "system",
                    "severity": "high",
                    "description": f"CPU usage {perf.get('cpu_usage', 0)}% exceeds threshold",
                    "suggested_action": "scale_service",
                }
            )

        if perf.get("memory_usage", 0) > self.thresholds["memory_usage"]:
            issues.append(
                {
                    "type": "high_memory",
                    "service": "system",
                    "severity": "high",
                    "description": f"Memory usage {perf.get('memory_usage', 0)}% exceeds threshold",
                    "suggested_action": "restart_service",
                }
            )

        return issues

    async def _perform_repairs(
        self, issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform automated repairs for diagnosed issues."""
        repairs = []

        for issue in issues:
            action = issue.get("suggested_action")
            if action and action in self.healing_actions:
                try:
                    # Execute repair action
                    result = await self._execute_repair_action(action, issue)
                    repairs.append(
                        {
                            "issue": issue,
                            "action": action,
                            "result": "success",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                except Exception as e:
                    repairs.append(
                        {
                            "issue": issue,
                            "action": action,
                            "result": "failed",
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

        return repairs

    async def _execute_repair_action(
        self, action: str, issue: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific repair action."""
        if action == "restart_service":
            return await self._restart_service(issue["service"])
        elif action == "scale_service":
            return await self._scale_service(issue["service"])
        elif action == "reconnect_db":
            return await self._reconnect_database()
        elif action == "invalidate_cache":
            return await self._invalidate_cache()
        else:
            raise ValueError(f"Unknown repair action: {action}")

    async def _restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a failed service."""
        # Use MCP to call Maestro for service restart
        return await self.mcp_router.route_to_mcp(
            agent_name=self.name,
            mcp_name="maestro_mcp",
            operation="restart_service",
            params={"service": service_name},
        )

    async def _scale_service(self, service_name: str) -> Dict[str, Any]:
        """Scale a service to handle load."""
        return await self.mcp_router.route_to_mcp(
            agent_name=self.name,
            mcp_name="maestro_mcp",
            operation="scale_service",
            params={"service": service_name, "replicas": 2},
        )

    async def _reconnect_database(self) -> Dict[str, Any]:
        """Reconnect to database."""
        return await self.mcp_router.route_to_mcp(
            agent_name=self.name,
            mcp_name="sync_mcp",
            operation="reconnect_database",
            params={},
        )

    async def _invalidate_cache(self) -> Dict[str, Any]:
        """Invalidate cache to clear stale data."""
        return await self.mcp_router.route_to_mcp(
            agent_name=self.name,
            mcp_name="sync_mcp",
            operation="invalidate_cache",
            params={},
        )

    async def _generate_alerts(
        self, issues: List[Dict[str, Any]], repairs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate alerts for critical issues."""
        alerts = []

        for issue in issues:
            if issue["severity"] == "critical":
                alerts.append(
                    {
                        "level": "critical",
                        "message": issue["description"],
                        "service": issue.get("service", "unknown"),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # Alert if repairs failed
        failed_repairs = [r for r in repairs if r["result"] == "failed"]
        if failed_repairs:
            alerts.append(
                {
                    "level": "warning",
                    "message": f"{len(failed_repairs)} automated repairs failed",
                    "details": failed_repairs,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return alerts

    async def _check_service_health(self) -> Dict[str, Any]:
        """Check health of all services."""
        services = ["api", "postgres", "redis", "nginx"]
        results = {}

        for service in services:
            try:
                # Health check via MCP
                health = await self.mcp_router.route_to_mcp(
                    agent_name=self.name,
                    mcp_name="maestro_mcp",
                    operation="check_service_health",
                    params={"service": service},
                )
                results[service] = health
            except Exception as e:
                results[service] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        return results

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            return await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="sync_mcp",
                operation="check_database_health",
                params={},
            )
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache performance and connectivity."""
        try:
            return await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="sync_mcp",
                operation="check_cache_health",
                params={},
            )
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _check_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics."""
        try:
            return await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="maestro_mcp",
                operation="get_performance_metrics",
                params={},
            )
        except Exception as e:
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process monitoring operation.

        Args:
            context: Operation context

        Returns:
            Processing results
        """
        operation_type = context.get("operation", "health_check")

        if operation_type == "health_check":
            return await self._check_health_all()
        elif operation_type == "diagnostic":
            return await self._diagnose_issues()
        elif operation_type == "repair":
            issues = context.get("issues", [])
            return await self._perform_repairs(issues)
        else:
            raise ValueError(f"Unknown operation: {operation_type}")

    def _validate_context(self, context: Dict[str, Any]) -> None:
        """Validate monitoring context."""
        operation = context.get("operation", "")
        # check_type is only required for specific diagnostic operations
        if operation in ["diagnostic", "detailed_check"]:
            required_fields = ["check_type"]
            for field in required_fields:
                if field not in context:
                    raise ValueError(f"Missing required field: {field}")

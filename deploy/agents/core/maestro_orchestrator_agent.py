"""
Maestro Orchestrator Agent - Advanced workflow orchestration and load balancing.

This agent coordinates multi-agent workflows, manages load balancing between agents,
monitors workflow execution, handles failures and retries, and optimizes resource usage.

Follows TwisterLab BaseAgent pattern with MCP isolation and secure credential management.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

from agents.base.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MaestroOrchestratorAgent(BaseAgent):
    """
    Maestro Orchestrator Agent - Advanced workflow orchestration and load balancing.

    Responsibilities:
    - Coordinate multi-agent workflows
    - Load balance between agents
    - Monitor workflow execution
    - Handle workflow failures and retries
    - Optimize agent resource usage
    - Maintain workflow state and audit trails

    Security:
    - MCP isolation: Only accesses allowed MCPs (orchestrator_mcp)
    - Credential scoping: Enterprise credentials only
    - Audit logging: All orchestration decisions logged
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "MaestroOrchestratorAgent"
        self.priority = 1  # Highest priority for orchestration
        self.capabilities = [
            "workflow_orchestration",
            "load_balancing",
            "resource_optimization",
            "failure_handling",
            "performance_monitoring",
            "workflow_state_management",
        ]

        # Initialize agent registry and workflow management
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.workflow_templates: Dict[str, List[Dict[str, Any]]] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.agent_load: Dict[str, int] = {}
        self.workflow_history: List[Dict[str, Any]] = []

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestration logic based on operation type.

        Args:
            context: Operation context containing operation type and parameters

        Returns:
            Dict containing operation results with status, data, and metadata

        Raises:
            ValueError: If operation is unknown or context is invalid
            CredentialScopeViolation: If attempting to access unauthorized credentials
        """
        try:
            self._validate_context(context)
            operation = context.get("operation", "orchestrate")

            # Audit log the orchestration request
            await self.audit_log(
                "orchestration_start",
                {"operation": operation, "context_keys": list(context.keys())},
            )

            if operation == "register_agents":
                result = await self._register_agents(context)
            elif operation == "execute_workflow":
                result = await self._execute_workflow(context)
            elif operation == "load_balance":
                result = await self._load_balance(context)
            elif operation == "monitor_performance":
                result = await self._monitor_performance(context)
            elif operation == "get_workflow_status":
                result = await self._get_workflow_status(context)
            elif operation == "cancel_workflow":
                result = await self._cancel_workflow(context)
            elif operation == "assess_situation":
                result = await self._assess_situation(context)
            elif operation == "verify_resolution":
                result = await self._verify_resolution(context)
            else:
                raise ValueError(f"Unknown orchestration operation: {operation}")

            # Audit log successful completion
            await self.audit_log(
                "orchestration_success",
                {"operation": operation, "result_status": result.get("status")},
            )

            return result

        except Exception as e:
            # Audit log failure
            await self.audit_log(
                "orchestration_failed",
                {
                    "operation": context.get("operation"),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )

            logger.error("Maestro orchestration failed: %s", e)
            raise

    async def _register_agents(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register available agents for orchestration.

        Dynamically imports and registers all operational agents.
        This ensures the orchestrator always has access to the latest agent implementations.

        Args:
            context: Registration context (currently unused but reserved for future filtering)

        Returns:
            Dict with registration status and registered agents list
        """
        try:
            # Import agents dynamically to avoid circular imports
            from agents.core.backup_agent import BackupAgent
            from agents.core.monitoring_agent import MonitoringAgent
            from agents.core.sync_agent import SyncAgent
            from agents.desktop_commander.desktop_commander_agent import (
                DesktopCommanderAgent,
            )
            from agents.helpdesk.classifier import TicketClassifierAgent
            from agents.resolver.resolver_agent import ResolverAgent

            # Register agents with their capabilities
            self.registered_agents = {
                "classifier": TicketClassifierAgent(),
                "resolver": ResolverAgent(),
                "desktop_commander": DesktopCommanderAgent(),
                "sync": SyncAgent(),
                "backup": BackupAgent(),
                "monitoring": MonitoringAgent(),
            }

            # Initialize load tracking
            self.agent_load = {name: 0 for name in self.registered_agents.keys()}

            # Define workflow templates
            self.workflow_templates = {
                "ticket_resolution": [
                    {
                        "agent": "classifier",
                        "operation": "classify",
                        "description": "Classify incoming ticket by category and priority",
                        "timeout": 30,
                        "allow_failure": False,
                    },
                    {
                        "agent": "resolver",
                        "operation": "resolve",
                        "description": "Execute resolution steps based on SOPs",
                        "timeout": 120,
                        "allow_failure": False,
                        "conditional": True,  # Only if classification indicates resolvable issue
                    },
                    {
                        "agent": "desktop_commander",
                        "operation": "execute_commands",
                        "description": "Execute system commands if required",
                        "timeout": 300,
                        "allow_failure": True,  # Commands might fail but workflow can continue
                        "conditional": True,  # Only if resolver determines commands needed
                    },
                    {
                        "agent": "sync",
                        "operation": "sync",
                        "description": "Synchronize data and cache",
                        "timeout": 60,
                        "allow_failure": False,
                    },
                    {
                        "agent": "monitoring",
                        "operation": "health_check",
                        "description": "Final health check and monitoring",
                        "timeout": 30,
                        "allow_failure": True,
                    },
                ],
                "system_backup": [
                    {
                        "agent": "monitoring",
                        "operation": "pre_backup_check",
                        "description": "Verify system health before backup",
                        "timeout": 30,
                        "allow_failure": False,
                    },
                    {
                        "agent": "backup",
                        "operation": "backup",
                        "description": "Create system backup",
                        "timeout": 1800,  # 30 minutes
                        "allow_failure": False,
                    },
                    {
                        "agent": "sync",
                        "operation": "sync",
                        "description": "Verify backup integrity",
                        "timeout": 120,
                        "allow_failure": False,
                    },
                    {
                        "agent": "monitoring",
                        "operation": "post_backup_check",
                        "description": "Verify system after backup",
                        "timeout": 30,
                        "allow_failure": True,
                    },
                ],
                "emergency_response": [
                    {
                        "agent": "monitoring",
                        "operation": "emergency_diagnosis",
                        "description": "Diagnose emergency situation",
                        "timeout": 60,
                        "allow_failure": False,
                    },
                    {
                        "agent": "desktop_commander",
                        "operation": "emergency_commands",
                        "description": "Execute emergency remediation commands",
                        "timeout": 300,
                        "allow_failure": True,
                    },
                    {
                        "agent": "sync",
                        "operation": "emergency_sync",
                        "description": "Ensure data consistency",
                        "timeout": 30,
                        "allow_failure": False,
                    },
                ],
            }

            registered_count = len(self.registered_agents)
            template_count = len(self.workflow_templates)

            logger.info(
                "Registered %d agents and %d workflow templates",
                registered_count,
                template_count,
            )

            return {
                "status": "success",
                "registered_agents": list(self.registered_agents.keys()),
                "workflow_templates": list(self.workflow_templates.keys()),
                "total_agents": registered_count,
                "total_templates": template_count,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error("Agent registration failed: %s", e)
            raise

    async def _execute_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow with error handling and monitoring.

        Args:
            context: Workflow execution context containing workflow_name and workflow_context

        Returns:
            Dict with workflow execution results
        """
        workflow_name = context.get("workflow_name")
        workflow_context = context.get("workflow_context", {})

        if workflow_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {workflow_name}")

        # Generate unique workflow ID
        workflow_id = f"{workflow_name}_{asyncio.get_event_loop().time()}_{id(self)}"

        # Initialize workflow tracking
        start_time = asyncio.get_event_loop().time()
        self.active_workflows[workflow_id] = {
            "status": "running",
            "workflow_name": workflow_name,
            "start_time": start_time,
            "steps": [],
            "context": workflow_context.copy(),
        }

        template = self.workflow_templates[workflow_name]
        results: List[Dict[str, Any]] = []
        failed_steps = []

        try:
            for step_config in template:
                step_start = asyncio.get_event_loop().time()

                # Check conditional execution
                if step_config.get("conditional", False):
                    should_execute = await self._should_execute_step(
                        step_config, workflow_context, results
                    )
                    if not should_execute:
                        results.append(
                            {
                                "step": f"{step_config['agent']}.{step_config['operation']}",
                                "status": "skipped",
                                "reason": "conditional_not_met",
                                "execution_time": 0.0,
                            }
                        )
                        continue

                try:
                    # Load balance agent selection
                    agent_name = await self._select_agent_for_step(step_config, workflow_context)

                    # Execute step with timeout
                    timeout = step_config.get("timeout", 60)
                    step_result = await asyncio.wait_for(
                        self._execute_step(agent_name, step_config, workflow_context),
                        timeout=timeout,
                    )

                    step_end = asyncio.get_event_loop().time()
                    execution_time = step_end - step_start

                    results.append(
                        {
                            "step": f"{agent_name}.{step_config['operation']}",
                            "status": "success",
                            "result": step_result,
                            "execution_time": execution_time,
                            "agent": agent_name,
                        }
                    )

                    # Update agent load
                    self.agent_load[agent_name] += 1

                except asyncio.TimeoutError:
                    step_end = asyncio.get_event_loop().time()
                    execution_time = step_end - step_start

                    results.append(
                        {
                            "step": f"{step_config['agent']}.{step_config['operation']}",
                            "status": "timeout",
                            "execution_time": execution_time,
                            "timeout_seconds": timeout,
                        }
                    )

                    if not step_config.get("allow_failure", False):
                        failed_steps.append(step_config["agent"])
                        break

                except Exception as e:
                    step_end = asyncio.get_event_loop().time()
                    execution_time = step_end - step_start

                    results.append(
                        {
                            "step": f"{step_config['agent']}.{step_config['operation']}",
                            "status": "failed",
                            "error": str(e),
                            "execution_time": execution_time,
                        }
                    )

                    if not step_config.get("allow_failure", False):
                        failed_steps.append(step_config["agent"])
                        break

            # Determine final workflow status
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time

            if failed_steps:
                workflow_status = "failed"
                error_message = f"Workflow failed at steps: {', '.join(failed_steps)}"
            else:
                workflow_status = "completed"
                error_message = None

            # Update workflow tracking
            self.active_workflows[workflow_id].update(
                {
                    "status": workflow_status,
                    "end_time": end_time,
                    "execution_time": execution_time,
                    "results": results,
                    "error_message": error_message,
                }
            )

            # Add to history
            self.workflow_history.append(self.active_workflows[workflow_id].copy())

            # Clean up old workflows (keep last 100)
            if len(self.workflow_history) > 100:
                self.workflow_history = self.workflow_history[-100:]

            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "workflow_status": workflow_status,
                "results": results,
                "execution_time": execution_time,
                "failed_steps": failed_steps if failed_steps else None,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            # Update workflow status on critical failure
            end_time = asyncio.get_event_loop().time()
            self.active_workflows[workflow_id].update(
                {
                    "status": "critical_failure",
                    "end_time": end_time,
                    "error_message": str(e),
                }
            )

            logger.error("Critical workflow failure: %s", e)
            raise

    async def _load_balance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load balance between available agents for a specific operation.

        Args:
            context: Load balancing context with agent_type and operation

        Returns:
            Dict with selected agent and load distribution info
        """
        agent_type = context.get("agent_type")
        operation = context.get("operation")

        if not agent_type or not operation:
            raise ValueError("agent_type and operation are required for load balancing")

        # Find agents capable of the requested operation
        capable_agents = []
        for name, agent in self.registered_agents.items():
            if agent_type in getattr(agent, "capabilities", []):
                capable_agents.append(name)

        if not capable_agents:
            raise ValueError(f"No agents available for type: {agent_type}")

        # Simple load balancing: select least loaded agent
        selected_agent = min(capable_agents, key=lambda x: self.agent_load.get(x, 0))

        # Update load
        self.agent_load[selected_agent] += 1

        return {
            "status": "success",
            "selected_agent": selected_agent,
            "available_agents": capable_agents,
            "load_distribution": self.agent_load.copy(),
            "timestamp": datetime.now().isoformat(),
        }

    async def _monitor_performance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor performance and health of all registered agents.

        Args:
            context: Monitoring context (reserved for future filtering)

        Returns:
            Dict with performance metrics for all agents
        """
        performance_data = {}
        timestamp = datetime.now().isoformat()

        for name, agent in self.registered_agents.items():
            try:
                # Get agent metrics if available
                if hasattr(agent, "get_metrics"):
                    metrics = await agent.get_metrics()
                else:
                    metrics = {"status": "no_metrics_available"}

                # Add load information
                metrics["current_load"] = self.agent_load.get(name, 0)
                metrics["capabilities"] = getattr(agent, "capabilities", [])

                performance_data[name] = {
                    "status": "success",
                    "metrics": metrics,
                    "timestamp": timestamp,
                }

            except Exception as e:
                performance_data[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": timestamp,
                }

        # Add system-wide metrics
        total_workflows = len(self.workflow_history)
        active_workflows = len(
            [w for w in self.active_workflows.values() if w["status"] == "running"]
        )
        completed_workflows = len([w for w in self.workflow_history if w["status"] == "completed"])
        failed_workflows = len([w for w in self.workflow_history if w["status"] == "failed"])

        return {
            "status": "success",
            "performance_data": performance_data,
            "system_metrics": {
                "total_workflows": total_workflows,
                "active_workflows": active_workflows,
                "completed_workflows": completed_workflows,
                "failed_workflows": failed_workflows,
                "success_rate": completed_workflows / max(total_workflows, 1),
            },
            "timestamp": timestamp,
        }

    async def _get_workflow_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of a specific workflow."""
        workflow_id = context.get("workflow_id")
        if not workflow_id or workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        return {
            "status": "success",
            "workflow": self.active_workflows[workflow_id],
            "timestamp": datetime.now().isoformat(),
        }

    async def _cancel_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a running workflow."""
        workflow_id = context.get("workflow_id")
        if not workflow_id or workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.active_workflows[workflow_id]
        if workflow["status"] != "running":
            raise ValueError(f"Workflow is not running: {workflow['status']}")

        workflow["status"] = "cancelled"
        workflow["end_time"] = asyncio.get_event_loop().time()
        workflow["cancelled_at"] = datetime.now().isoformat()

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "message": "Workflow cancelled successfully",
            "timestamp": datetime.now().isoformat(),
        }

    async def _assess_situation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the current system situation by coordinating with monitoring and other agents."""
        try:
            # Get system health from monitoring agent
            health_result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="monitoring_mcp",
                operation="health_check",
                params={"check_type": "system"},
            )

            # Assess agent status
            agent_status = {}
            for agent_name in self.registered_agents:
                try:
                    agent_result = await self.mcp_router.route_to_mcp(
                        agent_name=self.name,
                        mcp_name=f"{agent_name.lower()}_mcp",
                        operation="status",
                        params={},
                    )
                    agent_status[agent_name] = agent_result
                except Exception as e:
                    agent_status[agent_name] = {"status": "error", "error": str(e)}

            # Determine overall system health
            system_health = "healthy"
            issues_found = []

            if health_result.get("status") != "healthy":
                system_health = "degraded"
                issues_found.append("system_health_issues")

            unhealthy_agents = [
                name for name, status in agent_status.items() if status.get("status") != "healthy"
            ]
            if unhealthy_agents:
                system_health = "critical" if system_health == "degraded" else "warning"
                issues_found.append(f"unhealthy_agents: {unhealthy_agents}")

            return {
                "status": "success",
                "assessment": {
                    "system_health": system_health,
                    "issues_found": issues_found,
                    "health_details": health_result,
                    "agent_status": agent_status,
                    "timestamp": datetime.now().isoformat(),
                },
                "recommendations": self._generate_recommendations(system_health, issues_found),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to assess situation: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_recommendations(self, system_health: str, issues_found: List[str]) -> List[str]:
        """Generate recommendations based on system assessment."""
        recommendations = []

        if system_health == "critical":
            recommendations.extend(
                [
                    "Immediate intervention required",
                    "Consider emergency backup procedures",
                    "Isolate failing components",
                ]
            )
        elif system_health == "degraded":
            recommendations.extend(
                [
                    "Monitor system closely",
                    "Schedule maintenance during next maintenance window",
                    "Review recent changes for potential issues",
                ]
            )
        elif system_health == "warning":
            recommendations.extend(
                [
                    "Investigate agent health issues",
                    "Review system logs for anomalies",
                    "Consider performance optimization",
                ]
            )

        for issue in issues_found:
            if "unhealthy_agents" in issue:
                recommendations.append("Restart or redeploy unhealthy agents")
            elif "system_health_issues" in issue:
                recommendations.append("Run comprehensive system diagnostics")

        return recommendations

    async def _verify_resolution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify that issues have been resolved."""
        try:
            # Get current system health
            health_result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="monitoring_mcp",
                operation="health_check",
                params={"check_type": "system"},
            )

            # Check if issues are resolved
            system_healthy = health_result.get("status") == "healthy"
            active_issues = health_result.get("issues_found", 0)

            return {
                "status": "success",
                "resolution_verified": system_healthy and active_issues == 0,
                "current_health": health_result,
                "issues_remaining": active_issues,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to verify resolution: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def _select_agent_for_step(
        self, step_config: Dict[str, Any], workflow_context: Dict[str, Any]
    ) -> str:
        """Select the best agent for a workflow step."""
        agent_name = str(step_config["agent"])

        # For now, use direct agent selection
        # Future: implement intelligent agent selection based on context
        if agent_name not in self.registered_agents:
            raise ValueError(f"Agent not registered: {agent_name}")

        return agent_name

    async def _execute_step(
        self,
        agent_name: str,
        step_config: Dict[str, Any],
        workflow_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        agent = self.registered_agents[agent_name]
        operation = step_config["operation"]

        # Prepare step context
        step_context = {"operation": operation, **workflow_context}

        # Execute the step
        return await agent.execute(step_context)

    async def _should_execute_step(
        self,
        step_config: Dict[str, Any],
        workflow_context: Dict[str, Any],
        previous_results: List[Dict[str, Any]],
    ) -> bool:
        """
        Determine if a conditional step should execute based on previous results.

        Args:
            step_config: Step configuration
            workflow_context: Current workflow context
            previous_results: Results from previous steps

        Returns:
            bool: Whether the step should execute
        """
        agent = step_config["agent"]
        # operation = step_config['operation']  # Not used in this context

        if agent == "resolver":
            # Execute resolver only if classifier found a resolvable issue
            classifier_result = next(
                (r for r in previous_results if r["step"].startswith("classifier")),
                None,
            )
            if classifier_result and classifier_result["status"] == "success":
                result_data = classifier_result.get("result", {})
                # Check if issue is resolvable (not requiring escalation)
                return not result_data.get("requires_escalation", False)
            return False

        elif agent == "desktop_commander":
            # Execute commands only if resolver determined they're needed
            resolver_result = next(
                (r for r in previous_results if r["step"].startswith("resolver")), None
            )
            if resolver_result and resolver_result["status"] == "success":
                result_data = resolver_result.get("result", {})
                requires_commands = result_data.get("requires_commands", False)
                return bool(requires_commands)
            return False

        return True

    def _validate_context(self, context: Dict[str, Any]) -> None:
        """
        Validate orchestration context.

        Args:
            context: Context to validate

        Raises:
            ValueError: If context is invalid
        """
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")

        required_fields = ["operation"]
        for field in required_fields:
            if field not in context:
                raise ValueError(f"Missing required field: {field}")

        # Validate operation-specific requirements
        operation = context.get("operation")
        if operation == "execute_workflow":
            if "workflow_name" not in context:
                raise ValueError("workflow_name required for execute_workflow operation")
        elif operation == "load_balance":
            if "agent_type" not in context or "operation" not in context:
                raise ValueError("agent_type and operation required for load_balance")
        elif operation == "get_workflow_status":
            if "workflow_id" not in context:
                raise ValueError("workflow_id required for get_workflow_status operation")
        elif operation == "cancel_workflow":
            if "workflow_id" not in context:
                raise ValueError("workflow_id required for cancel_workflow operation")

    async def _process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process orchestration operation.

        Args:
            context: Operation context

        Returns:
            Processing results
        """
        operation = context.get("operation")

        if operation == "register_agents":
            return await self._register_agents(context)
        elif operation == "execute_workflow":
            return await self._execute_workflow(context)
        elif operation == "load_balance":
            return await self._load_balance(context)
        elif operation == "monitor_performance":
            return await self._monitor_performance(context)
        elif operation == "get_workflow_status":
            return await self._get_workflow_status(context)
        elif operation == "cancel_workflow":
            return await self._cancel_workflow(context)
        else:
            raise ValueError(f"Unknown orchestration operation: {operation}")

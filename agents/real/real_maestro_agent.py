"""
TwisterLab - Real Working Maestro Orchestrator Agent
Orchestrates and coordinates all other agents
"""
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class RealMaestroAgent:
    """
    Real maestro orchestrator that coordinates ACTUAL multi-agent workflows.

    Operations:
    - orchestrate_workflow: Execute complete ticket resolution workflow
    - coordinate_agents: Coordinate multiple agents for complex tasks
    - health_check_all: Check health of all agents
    - load_balance: Distribute work across agents
    """

    def __init__(self):
        self.name = "RealMaestroAgent"

        # Import other real agents (lazy loading to avoid circular imports)
        self.agents = {}
        self.agent_stats = {}

    async def _load_agents(self):
        """Lazy load other agents."""
        if not self.agents:
            try:
                from agents.real.real_classifier_agent import RealClassifierAgent
                from agents.real.real_resolver_agent import RealResolverAgent
                from agents.real.real_monitoring_agent import RealMonitoringAgent
                from agents.real.real_backup_agent import RealBackupAgent
                from agents.real.real_sync_agent import RealSyncAgent
                from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent

                self.agents = {
                    "classifier": RealClassifierAgent(),
                    "resolver": RealResolverAgent(),
                    "monitoring": RealMonitoringAgent(),
                    "backup": RealBackupAgent(),
                    "sync": RealSyncAgent(),
                    "desktop_commander": RealDesktopCommanderAgent()
                }

                # Initialize stats
                for agent_name in self.agents.keys():
                    self.agent_stats[agent_name] = {
                        "tasks_executed": 0,
                        "tasks_succeeded": 0,
                        "tasks_failed": 0,
                        "last_execution": None
                    }

                logger.info(f"✅ Loaded {len(self.agents)} agents")
            except Exception as e:
                logger.error(f"Failed to load agents: {e}")
                self.agents = {}

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute maestro operation.

        Args:
            context: Must contain 'operation' key
                Operations: orchestrate_workflow, coordinate_agents, health_check_all, load_balance

        Returns:
            Orchestration results
        """
        operation = context.get("operation", "orchestrate_workflow")

        logger.info(f"🎭 RealMaestroAgent executing: {operation}")

        # Ensure agents are loaded
        await self._load_agents()

        try:
            if operation == "orchestrate_workflow":
                ticket = context.get("ticket", {})
                return await self._orchestrate_workflow(ticket)
            elif operation == "coordinate_agents":
                agents_to_run = context.get("agents", [])
                return await self._coordinate_agents(agents_to_run)
            elif operation == "health_check_all":
                return await self._health_check_all()
            elif operation == "load_balance":
                tasks = context.get("tasks", [])
                return await self._load_balance(tasks)
            else:
                raise ValueError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(f"❌ Orchestration failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _orchestrate_workflow(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate complete ticket resolution workflow.

        Workflow:
        1. ClassifierAgent analyzes ticket
        2. Based on classification, route to appropriate agent
        3. ResolverAgent executes SOP
        4. DesktopCommanderAgent performs system checks if needed
        5. MonitoringAgent verifies resolution
        6. BackupAgent creates backup if needed
        """
        logger.info(f"🎯 Orchestrating workflow for ticket: {ticket.get('title', 'Untitled')}")

        workflow_start = datetime.now(timezone.utc)
        workflow_steps = []

        try:
            # Step 1: Classify ticket
            logger.info("Step 1: Classifying ticket...")
            classify_result = await self.agents["classifier"].execute({
                "operation": "classify_ticket",
                "ticket": ticket
            })

            workflow_steps.append({
                "step": 1,
                "agent": "classifier",
                "action": "classify_ticket",
                "status": classify_result["status"],
                "result": classify_result
            })

            category = classify_result["classification"]["category"]
            priority = classify_result["classification"]["priority"]

            # Step 2: Resolve ticket
            logger.info("Step 2: Resolving ticket...")
            resolve_result = await self.agents["resolver"].execute({
                "operation": "resolve_ticket",
                "ticket": {
                    **ticket,
                    "category": category,
                    "priority": priority
                }
            })

            workflow_steps.append({
                "step": 2,
                "agent": "resolver",
                "action": "resolve_ticket",
                "status": resolve_result["status"],
                "result": resolve_result
            })

            # Step 3: Verify with monitoring (if critical)
            if priority == "critical":
                logger.info("Step 3: Verifying resolution...")
                monitor_result = await self.agents["monitoring"].execute({
                    "operation": "health_check"
                })

                workflow_steps.append({
                    "step": 3,
                    "agent": "monitoring",
                    "action": "health_check",
                    "status": monitor_result["status"],
                    "result": monitor_result
                })

            # Step 4: Create backup (if needed)
            if category in ["database", "security"]:
                logger.info("Step 4: Creating backup...")
                backup_result = await self.agents["backup"].execute({
                    "operation": "create_backup"
                })

                workflow_steps.append({
                    "step": 4,
                    "agent": "backup",
                    "action": "create_backup",
                    "status": backup_result["status"],
                    "result": backup_result
                })

            workflow_duration = (datetime.now(timezone.utc) - workflow_start).total_seconds()

            # Update stats
            for step in workflow_steps:
                agent_name = step["agent"]
                self.agent_stats[agent_name]["tasks_executed"] += 1
                if step["status"] == "success":
                    self.agent_stats[agent_name]["tasks_succeeded"] += 1
                else:
                    self.agent_stats[agent_name]["tasks_failed"] += 1
                self.agent_stats[agent_name]["last_execution"] = datetime.now(timezone.utc).isoformat()

            result = {
                "status": "success",
                "ticket": ticket,
                "classification": {
                    "category": category,
                    "priority": priority
                },
                "workflow": {
                    "steps_executed": len(workflow_steps),
                    "duration_seconds": round(workflow_duration, 2),
                    "steps": workflow_steps
                },
                "outcome": "resolved",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info(f"✅ Workflow complete: {len(workflow_steps)} steps, {workflow_duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "workflow_steps": workflow_steps,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _coordinate_agents(self, agents_to_run: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Coordinate multiple agents running in parallel or sequence.

        Args:
            agents_to_run: List of {agent, operation, context}
        """
        logger.info(f"🔄 Coordinating {len(agents_to_run)} agents...")

        results = []

        for agent_config in agents_to_run:
            agent_name = agent_config["agent"]
            operation = agent_config["operation"]
            context = agent_config.get("context", {})

            if agent_name not in self.agents:
                logger.warning(f"Agent not found: {agent_name}")
                continue

            logger.info(f"  Running {agent_name}.{operation}...")

            result = await self.agents[agent_name].execute({
                "operation": operation,
                **context
            })

            results.append({
                "agent": agent_name,
                "operation": operation,
                "status": result.get("status"),
                "result": result
            })

        overall_success = all(r["status"] == "success" for r in results)

        return {
            "status": "success" if overall_success else "partial",
            "agents_coordinated": len(results),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _health_check_all(self) -> Dict[str, Any]:
        """
        Check health of all agents.

        Tests each agent with a simple operation.
        """
        logger.info("🏥 Checking health of all agents...")

        health_results = {}

        # Test each agent
        for agent_name, agent in self.agents.items():
            try:
                # Run appropriate health check for each agent
                if agent_name == "monitoring":
                    result = await agent.execute({"operation": "health_check"})
                elif agent_name == "classifier":
                    result = await agent.execute({
                        "operation": "classify_ticket",
                        "ticket": {"title": "test", "description": "health check"}
                    })
                elif agent_name == "resolver":
                    result = await agent.execute({"operation": "list_sops"})
                elif agent_name == "backup":
                    result = await agent.execute({"operation": "list_backups"})
                elif agent_name == "sync":
                    result = await agent.execute({"operation": "verify_consistency"})
                elif agent_name == "desktop_commander":
                    result = await agent.execute({"operation": "get_system_info"})
                else:
                    result = {"status": "unknown"}

                is_healthy = result.get("status") in ["success", "healthy"]

                health_results[agent_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_test": datetime.now(timezone.utc).isoformat(),
                    "stats": self.agent_stats.get(agent_name, {})
                }

            except Exception as e:
                logger.error(f"Health check failed for {agent_name}: {e}")
                health_results[agent_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_test": datetime.now(timezone.utc).isoformat()
                }

        healthy_count = sum(1 for h in health_results.values() if h["status"] == "healthy")

        result = {
            "status": "success",
            "total_agents": len(health_results),
            "healthy_agents": healthy_count,
            "unhealthy_agents": len(health_results) - healthy_count,
            "agents": health_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"✅ Health check: {healthy_count}/{len(health_results)} healthy")
        return result

    async def _load_balance(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Distribute tasks across agents based on load.

        Simple round-robin for now.
        """
        logger.info(f"⚖️ Load balancing {len(tasks)} tasks...")

        # Get agent loads
        agent_loads = {}
        for agent_name, stats in self.agent_stats.items():
            agent_loads[agent_name] = stats["tasks_executed"] - stats["tasks_succeeded"]

        # Sort agents by current load (least loaded first)
        sorted_agents = sorted(agent_loads.items(), key=lambda x: x[1])

        # Distribute tasks
        task_assignments = []
        agent_index = 0

        for task in tasks:
            assigned_agent = sorted_agents[agent_index % len(sorted_agents)][0]
            task_assignments.append({
                "task": task,
                "assigned_to": assigned_agent,
                "current_load": agent_loads[assigned_agent]
            })
            agent_index += 1

        result = {
            "status": "success",
            "total_tasks": len(tasks),
            "assignments": task_assignments,
            "load_distribution": agent_loads,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"✅ Load balanced {len(tasks)} tasks across {len(sorted_agents)} agents")
        return result

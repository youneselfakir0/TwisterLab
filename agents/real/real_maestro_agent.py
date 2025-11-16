"""
TwisterLab - Real Working Maestro Orchestrator Agent (v2 - Unified)
Orchestrates and coordinates all other agents, aligned with the UnifiedAgentBase.
"""
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

from agents.base.unified_agent import UnifiedAgentBase, AgentStatus
from agents.registry import agent_registry # Import the global agent registry

logger = logging.getLogger(__name__)


class RealMaestroAgent(UnifiedAgentBase):
    """
    Real maestro orchestrator that coordinates ACTUAL multi-agent workflows. Inherits from UnifiedAgentBase.
    """

    def __init__(self):
        super().__init__(
            name="RealMaestroAgent",
            version="2.0",
            description="Orchestrates and coordinates multi-agent workflows for IT automation.",
        )
        self.agent_registry = agent_registry # Get reference to the global registry
        self.agent_stats = {} # To track stats of agents managed by Maestro

        # Initialize stats for all known agents in the registry
        for agent_name in self.agent_registry.list_agents().keys():
            self.agent_stats[agent_name] = {
                "tasks_executed": 0,
                "tasks_succeeded": 0,
                "tasks_failed": 0,
                "last_execution": None
            }
        logger.info(f"✅ {self.name} initialized with access to {len(self.agent_registry.list_agents())} agents.")


    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute maestro operation.
        This method is called by the parent 'run' method, which handles status and error management.

        Args:
            context: Must contain 'operation' key
                Operations: orchestrate_workflow, coordinate_agents, health_check_all, load_balance

        Returns:
            Orchestration results
        """
        operation = context.get("operation", "orchestrate_workflow")
        logger.info(f"🎭 {self.name} executing: {operation}")

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
            raise ValueError(f"Unknown operation for {self.name}: {operation}")

    async def _orchestrate_workflow(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate complete ticket resolution workflow.
        """
        logger.info(f"🎯 Orchestrating workflow for ticket: {ticket.get('title', 'Untitled')}")

        workflow_start = datetime.now(timezone.utc)
        workflow_steps = []

        try:
            # Step 1: Classify ticket
            logger.info("Step 1: Classifying ticket...")
            classifier_agent = self.agent_registry.get_agent("classifieragent")
            if not classifier_agent: raise ValueError("ClassifierAgent not found in registry.")
            classify_result = await classifier_agent.run(context={
                "operation": "classify_ticket",
                "ticket": ticket
            })

            workflow_steps.append({
                "step": 1, "agent": "classifier", "action": "classify_ticket",
                "status": classify_result["status"], "result": classify_result
            })

            category = classify_result["result"]["classification"]["category"]
            priority = classify_result["result"]["classification"]["priority"]

            # Step 2: Resolve ticket
            logger.info("Step 2: Resolving ticket...")
            resolver_agent = self.agent_registry.get_agent("resolveragent")
            if not resolver_agent: raise ValueError("ResolverAgent not found in registry.")
            resolve_result = await resolver_agent.run(context={
                "operation": "resolve_ticket",
                "ticket": {**ticket, "category": category, "priority": priority}
            })

            workflow_steps.append({
                "step": 2, "agent": "resolver", "action": "resolve_ticket",
                "status": resolve_result["status"], "result": resolve_result
            })

            # Step 3: Verify with monitoring (if critical)
            if priority == "critical":
                logger.info("Step 3: Verifying resolution...")
                monitoring_agent = self.agent_registry.get_agent("realmonitoringagent")
                if not monitoring_agent: raise ValueError("RealMonitoringAgent not found in registry.")
                monitor_result = await monitoring_agent.run(context={"operation": "health_check"})

                workflow_steps.append({
                    "step": 3, "agent": "monitoring", "action": "health_check",
                    "status": monitor_result["status"], "result": monitor_result
                })

            # Step 4: Create backup (if needed)
            if category in ["database", "security"]:
                logger.info("Step 4: Creating backup...")
                backup_agent = self.agent_registry.get_agent("realbackupagent")
                if not backup_agent: raise ValueError("RealBackupAgent not found in registry.")
                backup_result = await backup_agent.run(context={"operation": "create_backup"})

                workflow_steps.append({
                    "step": 4, "agent": "backup", "action": "create_backup",
                    "status": backup_result["status"], "result": backup_result
                })

            workflow_duration = (datetime.now(timezone.utc) - workflow_start).total_seconds()

            # Update stats (simplified, as base agent handles its own metrics)
            for step in workflow_steps:
                agent_name = step["agent"]
                if agent_name in self.agent_stats:
                    self.agent_stats[agent_name]["tasks_executed"] += 1
                    if step["status"] == "success":
                        self.agent_stats[agent_name]["tasks_succeeded"] += 1
                    else:
                        self.agent_stats[agent_name]["tasks_failed"] += 1
                    self.agent_stats[agent_name]["last_execution"] = datetime.now(timezone.utc).isoformat()

            return {
                "status": "success",
                "ticket": ticket,
                "classification": {"category": category, "priority": priority},
                "workflow": {"steps_executed": len(workflow_steps), "duration_seconds": round(workflow_duration, 2), "steps": workflow_steps},
                "outcome": "resolved",
            }

        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            raise

    async def _coordinate_agents(self, agents_to_run: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Coordinate multiple agents running in parallel or sequence.
        """
        logger.info(f"🔄 Coordinating {len(agents_to_run)} agents...")
        results = []
        for agent_config in agents_to_run:
            agent_name = agent_config["agent"]
            operation = agent_config["operation"]
            context = agent_config.get("context", {})

            agent_instance = self.agent_registry.get_agent(agent_name)
            if not agent_instance:
                logger.warning(f"Agent not found in registry: {agent_name}")
                results.append({"agent": agent_name, "status": "skipped", "error": "Agent not found"})
                continue

            logger.info(f"  Running {agent_name}.{operation}...")
            result = await agent_instance.run(context={"operation": operation, **context})
            results.append({"agent": agent_name, "operation": operation, "status": result.get("status"), "result": result})

        overall_success = all(r["status"] == "success" for r in results)
        return {"status": "success" if overall_success else "partial", "agents_coordinated": len(results), "results": results}

    async def _health_check_all(self) -> Dict[str, Any]:
        """
        Check health of all agents.
        """
        logger.info("🏥 Checking health of all agents...")
        health_results = {}
        for agent_name, agent_instance in self.agent_registry._agents.items(): # Accessing _agents directly for iteration
            try:
                # Each agent's run method handles its own health check
                result = await agent_instance.run(context={"operation": "health_check"}) # Assuming all agents have a health_check operation
                is_healthy = result.get("status") in ["success", "healthy"]
                health_results[agent_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_test": datetime.now(timezone.utc).isoformat(),
                    "details": result
                }
            except Exception as e:
                logger.error(f"Health check failed for {agent_name}: {e}")
                health_results[agent_name] = {"status": "error", "error": str(e)}

        healthy_count = sum(1 for h in health_results.values() if h["status"] == "healthy")
        return {"status": "success", "total_agents": len(health_results), "healthy_agents": healthy_count, "agents": health_results}

    async def _load_balance(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Distribute tasks across agents based on load.
        """
        logger.info(f"⚖️ Load balancing {len(tasks)} tasks...")
        # This is a simplified load balancing. In a real system, this would be more sophisticated.
        # For now, we'll just assign tasks to agents in a round-robin fashion.
        
        available_agents = [name for name in self.agent_registry.list_agents().keys() if name != self.name.lower()] # Exclude self
        if not available_agents:
            return {"status": "error", "message": "No other agents available for load balancing."}

        task_assignments = []
        agent_index = 0
        for task in tasks:
            assigned_agent = available_agents[agent_index % len(available_agents)]
            task_assignments.append({"task": task, "assigned_to": assigned_agent})
            agent_index += 1

        return {"status": "success", "total_tasks": len(tasks), "assignments": task_assignments}
"""
TwisterLab Autonomous Agent Orchestrator

This module provides orchestration and management for autonomous agents,
integrating them into the main TwisterLab system with scheduling,
monitoring, and coordination capabilities.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from agents.base.base_agent import BaseAgent
from agents.core.backup_agent import BackupAgent
from agents.core.monitoring_agent import MonitoringAgent
from agents.core.sync_agent import SyncAgent

logger = logging.getLogger(__name__)


class AutonomousAgentOrchestrator:
    """
    Orchestrator for autonomous agents in TwisterLab.

    Manages agent lifecycle, scheduling, coordination, and health monitoring.
    Integrates autonomous agents into the main system workflow.
    """

    def __init__(self):
        """Initialize the agent orchestrator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="agent_orchestrator")

        # Agent health monitoring
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        self.health_check_interval = 30  # seconds

        # Scheduling configuration
        self.schedules = {
            "monitoring_health_check": timedelta(seconds=30),
            "monitoring_diagnostic": timedelta(minutes=5),
            "backup_full": timedelta(hours=6),
            "backup_incremental": timedelta(hours=1),
            "sync_cache_db": timedelta(minutes=5),
            "sync_consistency_check": timedelta(minutes=15),
            "performance_check": timedelta(hours=1),
        }

        # Coordination state
        self.system_status = "initializing"
        self.last_coordination = None
        self.coordination_lock = asyncio.Lock()

        logger.info("≡ƒñû Autonomous Agent Orchestrator initialized")

    async def initialize_agents(self) -> None:
        """Initialize all autonomous agents."""
        logger.info("≡ƒÜÇ Initializing autonomous agents...")

        # Create agent instances
        self.agents = {
            "monitoring": MonitoringAgent(),
            "backup": BackupAgent(),
            "sync": SyncAgent(),
        }

        # Initialize agent health tracking
        for agent_name, agent in self.agents.items():
            self.agent_health[agent_name] = {
                "status": "initializing",
                "last_check": datetime.now(),
                "error_count": 0,
                "last_error": None,
            }

        logger.info(f"Γ£à Initialized {len(self.agents)} autonomous agents")

    async def start_orchestration(self) -> None:
        """Start the agent orchestration system."""
        logger.info("≡ƒÄ» Starting autonomous agent orchestration...")

        # Initialize agents
        await self.initialize_agents()

        # Start health monitoring
        asyncio.create_task(self._health_monitoring_loop())

        # Start scheduled tasks
        await self._start_scheduled_tasks()

        # Start coordination loop
        asyncio.create_task(self._coordination_loop())

        self.system_status = "running"
        logger.info("Γ£à Autonomous agent orchestration started")

    async def stop_orchestration(self) -> None:
        """Stop the agent orchestration system."""
        logger.info("≡ƒ¢æ Stopping autonomous agent orchestration...")

        # Cancel all tasks
        for task in list(self.agent_tasks.values()) + list(self.scheduled_tasks.values()):
            task.cancel()

        # Shutdown executor
        self.executor.shutdown(wait=True)

        self.system_status = "stopped"
        logger.info("Γ£à Autonomous agent orchestration stopped")

    async def execute_agent_operation(
        self, agent_name: str, operation: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an operation on a specific agent.

        Args:
            agent_name: Name of the agent
            operation: Operation to execute
            context: Operation context

        Returns:
            Operation result
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent = self.agents[agent_name]
        context = context or {}

        # Add operation to context
        context["operation"] = operation

        logger.info(f"≡ƒñû Executing {operation} on {agent_name}")

        try:
            # Execute in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, lambda: asyncio.run(agent.execute(context))
            )

            # Update health status
            self.agent_health[agent_name]["status"] = "healthy"
            self.agent_health[agent_name]["last_check"] = datetime.now()
            self.agent_health[agent_name]["error_count"] = 0

            logger.info(f"Γ£à {agent_name} {operation} completed successfully")
            return result

        except Exception as e:
            # Update health status
            self.agent_health[agent_name]["status"] = "error"
            self.agent_health[agent_name]["last_check"] = datetime.now()
            self.agent_health[agent_name]["error_count"] += 1
            self.agent_health[agent_name]["last_error"] = str(e)

            logger.error(f"Γ¥î {agent_name} {operation} failed: {str(e)}")
            raise

    async def get_agent_status(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of agents.

        Args:
            agent_name: Specific agent name, or None for all

        Returns:
            Agent status information
        """
        if agent_name:
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not found")

            agent = self.agents[agent_name]
            health_info = await agent.get_health_status()

            return {
                "agent": agent_name,
                "status": self.agent_health[agent_name]["status"],
                "health": health_info,
                "capabilities": agent.get_capabilities(),
                "orchestrator_status": self.agent_health[agent_name],
            }

        # Return all agents status
        all_status = {}
        for name, agent in self.agents.items():
            health_info = await agent.get_health_status()
            all_status[name] = {
                "status": self.agent_health[name]["status"],
                "health": health_info,
                "capabilities": agent.get_capabilities(),
                "orchestrator_status": self.agent_health[name],
            }

        return {
            "system_status": self.system_status,
            "agents": all_status,
            "last_coordination": (
                self.last_coordination.isoformat() if self.last_coordination else None
            ),
        }

    async def trigger_emergency_response(self, issue_type: str, severity: str) -> Dict[str, Any]:
        """
        Trigger emergency response for critical issues.

        Args:
            issue_type: Type of issue detected
            severity: Severity level (low, medium, high, critical)

        Returns:
            Emergency response result
        """
        logger.warning(f"≡ƒÜ¿ Emergency response triggered: {issue_type} ({severity})")

        responses = []

        # Critical issues require immediate action
        if severity == "critical":
            # Stop all non-essential operations
            await self._pause_non_critical_operations()

            # Execute emergency diagnostics
            try:
                diag_result = await self.execute_agent_operation(
                    "monitoring",
                    "diagnostic",
                    {"emergency": True, "issue_type": issue_type},
                )
                responses.append(
                    {
                        "agent": "monitoring",
                        "operation": "diagnostic",
                        "result": diag_result,
                    }
                )
            except Exception as e:
                logger.error(f"Emergency diagnostic failed: {str(e)}")

            # Execute emergency backup if data-related
            if "data" in issue_type.lower() or "database" in issue_type.lower():
                try:
                    backup_result = await self.execute_agent_operation(
                        "backup",
                        "backup",
                        {"backup_type": "emergency", "reason": issue_type},
                    )
                    responses.append(
                        {
                            "agent": "backup",
                            "operation": "emergency_backup",
                            "result": backup_result,
                        }
                    )
                except Exception as e:
                    logger.error(f"Emergency backup failed: {str(e)}")

        # High severity issues
        elif severity == "high":
            # Execute targeted repair
            try:
                repair_result = await self.execute_agent_operation(
                    "monitoring",
                    "repair",
                    {"issue_type": issue_type, "severity": severity},
                )
                responses.append(
                    {
                        "agent": "monitoring",
                        "operation": "repair",
                        "result": repair_result,
                    }
                )
            except Exception as e:
                logger.error(f"High-priority repair failed: {str(e)}")

        return {
            "emergency_triggered": True,
            "issue_type": issue_type,
            "severity": severity,
            "responses": responses,
            "timestamp": datetime.now().isoformat(),
        }

    async def _health_monitoring_loop(self) -> None:
        """Continuous health monitoring loop."""
        logger.info("≡ƒÅÑ Starting agent health monitoring loop")

        while self.system_status == "running":
            try:
                # Check each agent's health
                for agent_name, agent in self.agents.items():
                    try:
                        health = await agent.get_health_status()
                        current_status = self.agent_health[agent_name]["status"]

                        # Update status based on health
                        if health["healthy"]:
                            if current_status != "healthy":
                                logger.info(f"Γ£à {agent_name} health restored")
                                self.agent_health[agent_name]["status"] = "healthy"
                        else:
                            if current_status == "healthy":
                                logger.warning(f"ΓÜá∩╕Å  {agent_name} health degraded")
                                self.agent_health[agent_name]["status"] = "degraded"

                        self.agent_health[agent_name]["last_check"] = datetime.now()

                    except Exception as e:
                        logger.error(f"Health check failed for {agent_name}: {str(e)}")
                        self.agent_health[agent_name]["status"] = "error"
                        self.agent_health[agent_name]["last_error"] = str(e)
                        self.agent_health[agent_name]["error_count"] += 1

                # Trigger emergency response if needed
                critical_agents = [
                    name
                    for name, health in self.agent_health.items()
                    if health["status"] == "error" and health["error_count"] > 3
                ]

                if critical_agents:
                    await self.trigger_emergency_response(
                        f"Multiple agent failures: {', '.join(critical_agents)}",
                        "critical",
                    )

            except Exception as e:
                logger.error(f"Health monitoring loop error: {str(e)}")

            await asyncio.sleep(self.health_check_interval)

    async def _start_scheduled_tasks(self) -> None:
        """Start scheduled autonomous tasks."""
        logger.info("≡ƒôà Starting scheduled autonomous tasks")

        # Health check every 30 seconds
        self.scheduled_tasks["health_check"] = asyncio.create_task(
            self._schedule_task(
                "monitoring",
                "health_check",
                self.schedules["monitoring_health_check"],
                {"check_type": "system"},
            )
        )

        # Full diagnostic every 5 minutes
        self.scheduled_tasks["diagnostic"] = asyncio.create_task(
            self._schedule_task(
                "monitoring",
                "diagnostic",
                self.schedules["monitoring_diagnostic"],
                {"check_type": "full"},
            )
        )

        # Full backup every 6 hours
        self.scheduled_tasks["backup_full"] = asyncio.create_task(
            self._schedule_task(
                "backup",
                "backup",
                self.schedules["backup_full"],
                {"backup_type": "full"},
            )
        )

        # Cache-DB sync every 5 minutes
        self.scheduled_tasks["sync_cache_db"] = asyncio.create_task(
            self._schedule_task(
                "sync",
                "sync",
                self.schedules["sync_cache_db"],
                {"sync_type": "cache_db"},
            )
        )

        # Consistency check every 15 minutes
        self.scheduled_tasks["consistency_check"] = asyncio.create_task(
            self._schedule_task(
                "sync", "consistency_check", self.schedules["sync_consistency_check"]
            )
        )

        # Performance check every hour
        self.scheduled_tasks["performance_check"] = asyncio.create_task(
            self._schedule_task("sync", "performance_check", self.schedules["performance_check"])
        )

        logger.info(f"Γ£à Started {len(self.scheduled_tasks)} scheduled tasks")

    async def _schedule_task(
        self,
        agent_name: str,
        operation: str,
        interval: timedelta,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Schedule a recurring task.

        Args:
            agent_name: Agent to execute on
            operation: Operation to perform
            interval: Time interval between executions
            context: Additional context for the operation
        """
        context = context or {}

        while self.system_status == "running":
            try:
                await self.execute_agent_operation(agent_name, operation, context.copy())
            except Exception as e:
                logger.error(f"Scheduled task failed ({agent_name}:{operation}): {str(e)}")

            await asyncio.sleep(interval.total_seconds())

    async def _coordination_loop(self) -> None:
        """Main coordination loop for agent orchestration."""
        logger.info("≡ƒÄ╝ Starting agent coordination loop")

        while self.system_status == "running":
            try:
                async with self.coordination_lock:
                    await self._coordinate_agents()
                    self.last_coordination = datetime.now()

            except Exception as e:
                logger.error(f"Coordination loop error: {str(e)}")

            await asyncio.sleep(60)  # Coordinate every minute

    async def _coordinate_agents(self) -> None:
        """Coordinate actions between agents based on system state."""
        # Get current system health from monitoring agent
        try:
            health_status = await self.execute_agent_operation(
                "monitoring", "health_check", {"check_type": "system"}
            )

            # Ensure health_status is a dict
            if not isinstance(health_status, dict):
                logger.warning(f"Health status is not a dict: {type(health_status)}")
                health_status = {"diagnosis": [], "overall_health": "unknown"}

            # If system is degraded, trigger sync operations
            diagnosis = health_status.get("diagnosis", [])
            overall_health = "healthy"
            if diagnosis and len(diagnosis) > 0:
                overall_health = "degraded"

            if overall_health == "degraded":
                logger.info("≡ƒöä System degraded - triggering synchronization")
                await self.execute_agent_operation("sync", "sync", {"sync_type": "full"})

            # If system has issues, trigger backup
            issues = diagnosis
            if issues:
                logger.info(f"≡ƒÆ╛ System has {len(issues)} issues - triggering backup")
                await self.execute_agent_operation(
                    "backup", "backup", {"backup_type": "incremental"}
                )

        except Exception as e:
            logger.error(f"Agent coordination failed: {str(e)}")

    async def _pause_non_critical_operations(self) -> None:
        """Pause non-critical operations during emergencies."""
        logger.warning("ΓÅ╕∩╕Å  Pausing non-critical operations")

        # Cancel non-essential scheduled tasks
        critical_tasks = {"health_check", "diagnostic"}  # Keep only critical monitoring

        for task_name, task in self.scheduled_tasks.items():
            if task_name not in critical_tasks:
                task.cancel()
                logger.info(f"ΓÅ╕∩╕Å  Paused scheduled task: {task_name}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "status": self.system_status,
            "agents_count": len(self.agents),
            "scheduled_tasks_count": len(self.scheduled_tasks),
            "healthy_agents": sum(
                1 for h in self.agent_health.values() if h["status"] == "healthy"
            ),
            "last_coordination": (
                self.last_coordination.isoformat() if self.last_coordination else None
            ),
            "uptime": (
                str(datetime.now() - datetime.fromisoformat("2025-11-09T00:00:00"))
                if self.system_status == "running"
                else None
            ),
        }


# Global orchestrator instance
orchestrator = AutonomousAgentOrchestrator()
_initialized = False


async def get_orchestrator() -> AutonomousAgentOrchestrator:
    """Get the global orchestrator instance, ensuring it's initialized."""
    global _initialized
    if not _initialized:
        await orchestrator.initialize_agents()
        _initialized = True
    return orchestrator


async def start_autonomous_agents() -> None:
    """Start the autonomous agent system."""
    await orchestrator.start_orchestration()


async def stop_autonomous_agents() -> None:
    """Stop the autonomous agent system."""
    await orchestrator.stop_orchestration()

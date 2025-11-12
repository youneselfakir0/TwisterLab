"""
TwisterLab Autonomous Agent Scheduler
Configures automatic execution of agents with cron-like scheduling
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentScheduler:
    """
    Scheduler for autonomous agent execution.

    Manages periodic tasks, cron-like schedules, and automatic agent execution.
    """

    def __init__(self, orchestrator):
        """
        Initialize scheduler.

        Args:
            orchestrator: AutonomousAgentOrchestrator instance
        """
        self.orchestrator = orchestrator
        self.scheduled_tasks = {}
        self.task_history = []
        self.max_history = 1000

        # Default schedules (in seconds)
        self.schedules = {
            "monitoring_health_check": {
                "agent": "monitoring",
                "operation": "health_check",
                "interval": 60,  # Every minute
                "enabled": True,
            },
            "monitoring_full_diagnostic": {
                "agent": "monitoring",
                "operation": "full_diagnostic",
                "interval": 300,  # Every 5 minutes
                "enabled": True,
            },
            "backup_create": {
                "agent": "backup",
                "operation": "create_backup",
                "interval": 21600,  # Every 6 hours
                "enabled": True,
            },
            "sync_verify_consistency": {
                "agent": "sync",
                "operation": "verify_consistency",
                "interval": 900,  # Every 15 minutes
                "enabled": True,
            },
            "sync_clear_stale": {
                "agent": "sync",
                "operation": "clear_stale_cache",
                "params": {"max_age_hours": 24},
                "interval": 3600,  # Every hour
                "enabled": True,
            },
            "maestro_health_check_all": {
                "agent": "maestro",
                "operation": "health_check_all",
                "interval": 180,  # Every 3 minutes
                "enabled": True,
            },
        }

        logger.info("📅 Agent Scheduler initialized")

    async def start(self):
        """Start all scheduled tasks."""
        logger.info("🚀 Starting agent scheduler...")

        for task_name, config in self.schedules.items():
            if config.get("enabled", True):
                task = asyncio.create_task(self._run_scheduled_task(task_name, config))
                self.scheduled_tasks[task_name] = task
                logger.info(
                    f"  ✅ Scheduled: {task_name} (every {config['interval']}s)"
                )

        logger.info(f"✅ Scheduler started with {len(self.scheduled_tasks)} tasks")

    async def stop(self):
        """Stop all scheduled tasks."""
        logger.info("🛑 Stopping scheduler...")

        for task_name, task in self.scheduled_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"  ✅ Stopped: {task_name}")

        self.scheduled_tasks.clear()
        logger.info("✅ Scheduler stopped")

    async def _run_scheduled_task(self, task_name: str, config: Dict[str, Any]):
        """
        Run a scheduled task periodically.

        Args:
            task_name: Name of the task
            config: Task configuration (agent, operation, interval, params)
        """
        agent_name = config["agent"]
        operation = config["operation"]
        interval = config["interval"]
        params = config.get("params", {})

        logger.info(
            f"📅 Task '{task_name}' started (agent={agent_name}, op={operation})"
        )

        while True:
            try:
                # Wait for interval
                await asyncio.sleep(interval)

                # Execute agent operation
                start_time = datetime.now(timezone.utc)

                agent = self.orchestrator.agents.get(agent_name)
                if not agent:
                    logger.warning(
                        f"Agent '{agent_name}' not found for task '{task_name}'"
                    )
                    continue

                logger.debug(f"⏰ Executing scheduled task: {task_name}")

                # Execute with timeout
                try:
                    result = await asyncio.wait_for(
                        agent.execute({"operation": operation, **params}),
                        timeout=300,  # 5 minute timeout
                    )

                    execution_time = (
                        datetime.now(timezone.utc) - start_time
                    ).total_seconds()

                    # Record in history
                    self._record_execution(
                        task_name=task_name,
                        agent_name=agent_name,
                        operation=operation,
                        status=result.get("status", "unknown"),
                        execution_time=execution_time,
                        result=result,
                    )

                    if result.get("status") == "success":
                        logger.info(
                            f"✅ Task '{task_name}' completed ({execution_time:.2f}s)"
                        )
                    else:
                        logger.warning(
                            f"⚠️  Task '{task_name}' partial success: {result.get('error', 'Unknown error')}"
                        )

                except asyncio.TimeoutError:
                    logger.error(f"⏱️  Task '{task_name}' timeout (>300s)")
                    self._record_execution(
                        task_name=task_name,
                        agent_name=agent_name,
                        operation=operation,
                        status="timeout",
                        execution_time=300,
                        result={"error": "Execution timeout"},
                    )

            except asyncio.CancelledError:
                logger.info(f"Task '{task_name}' cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Task '{task_name}' error: {e}", exc_info=True)
                self._record_execution(
                    task_name=task_name,
                    agent_name=agent_name,
                    operation=operation,
                    status="error",
                    execution_time=0,
                    result={"error": str(e)},
                )
                # Continue despite errors
                await asyncio.sleep(60)  # Wait 1 minute before retry

    def _record_execution(
        self,
        task_name: str,
        agent_name: str,
        operation: str,
        status: str,
        execution_time: float,
        result: Dict[str, Any],
    ):
        """Record task execution in history."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_name": task_name,
            "agent_name": agent_name,
            "operation": operation,
            "status": status,
            "execution_time_seconds": round(execution_time, 2),
            "result_summary": {
                "status": result.get("status"),
                "error": result.get("error"),
            },
        }

        self.task_history.append(record)

        # Trim history
        if len(self.task_history) > self.max_history:
            self.task_history = self.task_history[-self.max_history :]

    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        if not self.task_history:
            return {"total_executions": 0, "tasks": {}}

        stats = {"total_executions": len(self.task_history), "tasks": {}}

        for record in self.task_history:
            task_name = record["task_name"]
            if task_name not in stats["tasks"]:
                stats["tasks"][task_name] = {
                    "executions": 0,
                    "success": 0,
                    "error": 0,
                    "timeout": 0,
                    "avg_execution_time": 0,
                    "last_execution": None,
                }

            task_stats = stats["tasks"][task_name]
            task_stats["executions"] += 1

            if record["status"] == "success":
                task_stats["success"] += 1
            elif record["status"] == "error":
                task_stats["error"] += 1
            elif record["status"] == "timeout":
                task_stats["timeout"] += 1

            # Update average execution time
            current_avg = task_stats["avg_execution_time"]
            new_time = record["execution_time_seconds"]
            task_stats["avg_execution_time"] = (
                current_avg * (task_stats["executions"] - 1) + new_time
            ) / task_stats["executions"]

            task_stats["last_execution"] = record["timestamp"]

        return stats

    def save_history(self, filepath: str):
        """Save execution history to file."""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w") as f:
                json.dump(
                    {
                        "scheduler_stats": self.get_statistics(),
                        "execution_history": self.task_history,
                    },
                    f,
                    indent=2,
                )

            logger.info(f"📝 Scheduler history saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save scheduler history: {e}")

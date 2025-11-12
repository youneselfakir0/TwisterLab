"""
MaestroOrchestratorAgent - Enhanced Central Orchestrator
=======================================================

The central nervous system of TwisterLab v1.0 that coordinates all agents
with intelligent load balancing, health monitoring, failover, and task scheduling.

Author: Claude + Copilot Collaborative Development
Version: 1.0.0-alpha.1
License: Apache 2.0
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from agents.base import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("maestro_agent")


# ============================================================================
# LOAD BALANCING MODULE
# ============================================================================


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    PRIORITY_BASED = "priority_based"
    WEIGHTED = "weighted"


class LoadBalancer:
    """
    Intelligent load balancer for distributing work across agent instances.

    Features:
    - Round-robin distribution
    - Least-loaded selection
    - Priority-based routing
    - Weighted distribution
    """

    def __init__(self):
        # agent_type -> list of instances
        self.agent_instances: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Track current loads
        self.agent_loads: Dict[str, int] = {}

        # Round-robin counters
        self.rr_counters: Dict[str, int] = defaultdict(int)

    def register_instance(
        self,
        agent_type: str,
        instance_id: str,
        max_load: int = 10,
        priority: int = 1,
        weight: float = 1.0,
    ):
        """
        Register an agent instance.

        Args:
            agent_type: Type of agent (classifier, resolver, etc.)
            instance_id: Unique instance identifier
            max_load: Maximum concurrent tasks
            priority: Priority level (higher = more preferred)
            weight: Weight for weighted balancing
        """
        instance = {
            "instance_id": instance_id,
            "max_load": max_load,
            "current_load": 0,
            "priority": priority,
            "weight": weight,
            "is_healthy": True,
            "registered_at": datetime.now(timezone.utc),
        }

        self.agent_instances[agent_type].append(instance)
        self.agent_loads[instance_id] = 0

        logger.info(
            f"Registered {agent_type} instance: {instance_id} "
            f"(max_load={max_load}, priority={priority})"
        )

    def select_instance(
        self,
        agent_type: str,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED,
    ) -> Optional[str]:
        """
        Select best instance based on strategy.

        Args:
            agent_type: Type of agent needed
            strategy: Load balancing strategy

        Returns:
            Instance ID or None if no available instance
        """
        instances = self.agent_instances.get(agent_type, [])

        if not instances:
            logger.warning(f"No instances registered for {agent_type}")
            return None

        # Filter healthy instances with capacity
        available = [
            inst
            for inst in instances
            if inst["is_healthy"] and inst["current_load"] < inst["max_load"]
        ]

        if not available:
            logger.warning(f"No available capacity for {agent_type}")
            return None

        # Apply selection strategy
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._select_round_robin(agent_type, available)
        elif strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._select_least_loaded(available)
        elif strategy == LoadBalancingStrategy.PRIORITY_BASED:
            return self._select_priority_based(available)
        elif strategy == LoadBalancingStrategy.WEIGHTED:
            return self._select_weighted(available)
        else:
            return self._select_least_loaded(available)

    def _select_round_robin(
        self, agent_type: str, available: List[Dict[str, Any]]
    ) -> str:
        """Round-robin selection"""
        counter = self.rr_counters[agent_type]
        instance = available[counter % len(available)]
        self.rr_counters[agent_type] += 1
        return instance["instance_id"]

    def _select_least_loaded(self, available: List[Dict[str, Any]]) -> str:
        """Select instance with lowest load"""
        instance = min(available, key=lambda x: x["current_load"])
        return instance["instance_id"]

    def _select_priority_based(self, available: List[Dict[str, Any]]) -> str:
        """Select highest priority instance"""
        instance = max(available, key=lambda x: x["priority"])
        return instance["instance_id"]

    def _select_weighted(self, available: List[Dict[str, Any]]) -> str:
        """Weighted selection (prefers higher weights)"""
        # Simple weighted selection: higher weight = more likely
        instance = max(available, key=lambda x: x["weight"] / (x["current_load"] + 1))
        return instance["instance_id"]

    def increment_load(self, agent_type: str, instance_id: str):
        """Increment instance load"""
        instances = self.agent_instances[agent_type]
        for inst in instances:
            if inst["instance_id"] == instance_id:
                inst["current_load"] += 1
                self.agent_loads[instance_id] = inst["current_load"]
                logger.debug(
                    f"Incremented load for {instance_id}: {inst['current_load']}"
                )
                break

    def decrement_load(self, agent_type: str, instance_id: str):
        """Decrement instance load"""
        instances = self.agent_instances[agent_type]
        for inst in instances:
            if inst["instance_id"] == instance_id:
                inst["current_load"] = max(0, inst["current_load"] - 1)
                self.agent_loads[instance_id] = inst["current_load"]
                logger.debug(
                    f"Decremented load for {instance_id}: {inst['current_load']}"
                )
                break

    def mark_unhealthy(self, agent_type: str, instance_id: str):
        """Mark instance as unhealthy"""
        instances = self.agent_instances[agent_type]
        for inst in instances:
            if inst["instance_id"] == instance_id:
                inst["is_healthy"] = False
                logger.warning(f"Marked {instance_id} as unhealthy")
                break

    def mark_healthy(self, agent_type: str, instance_id: str):
        """Mark instance as healthy"""
        instances = self.agent_instances[agent_type]
        for inst in instances:
            if inst["instance_id"] == instance_id:
                inst["is_healthy"] = True
                logger.info(f"Marked {instance_id} as healthy")
                break


# ============================================================================
# HEALTH MONITORING MODULE
# ============================================================================


class HealthStatus(Enum):
    """Agent health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class HealthMonitor:
    """
    Monitors health of all agents in the system.

    Features:
    - Continuous health checks
    - Response time monitoring
    - Error rate tracking
    - Health history retention
    """

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        self.health_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.running = False

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.running = True
        logger.info("Health monitoring started")

        while self.running:
            await self._check_all_agents()
            await asyncio.sleep(self.check_interval)

    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.running = False
        logger.info("Health monitoring stopped")

    async def _check_all_agents(self):
        """Check health of all agents"""
        agent_types = [
            "classifier",
            "resolver",
            "desktop_commander",
            "sync",
            "backup",
            "monitoring",
        ]

        for agent_type in agent_types:
            health = await self._check_agent_health(agent_type)
            self.agent_health[agent_type] = health

            # Store in history
            self.health_history[agent_type].append(
                {
                    "timestamp": datetime.now(timezone.utc),
                    "status": health["status"],
                    "metrics": health.get("metrics", {}),
                }
            )

            # Keep only last 100 entries
            if len(self.health_history[agent_type]) > 100:
                self.health_history[agent_type].pop(0)

            # Log if unhealthy
            if health["status"] != HealthStatus.HEALTHY.value:
                logger.warning(
                    f"Agent {agent_type} is {health['status']}: "
                    f"{health.get('reason', 'unknown')}"
                )

    async def _check_agent_health(self, agent_type: str) -> Dict[str, Any]:
        """
        Check individual agent health.

        Checks:
        - Is agent responding?
        - Response time < threshold?
        - Error rate < threshold?
        - Recent activity?
        """
        try:
            # Ping agent (simulate for now, would be actual API call)
            start_time = datetime.now(timezone.utc)
            await asyncio.sleep(0.1)  # Simulate network call
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Evaluate health based on response time
            if response_time > 5.0:
                return {
                    "status": HealthStatus.DEGRADED.value,
                    "reason": "slow_response",
                    "response_time": response_time,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Check error rate (mock for now)
            error_rate = 0.05  # 5% mock error rate

            if error_rate > 0.2:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "reason": "high_error_rate",
                    "error_rate": error_rate,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            elif error_rate > 0.1:
                return {
                    "status": HealthStatus.DEGRADED.value,
                    "reason": "elevated_error_rate",
                    "error_rate": error_rate,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            return {
                "status": HealthStatus.HEALTHY.value,
                "response_time": response_time,
                "error_rate": error_rate,
                "last_check": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error checking health of {agent_type}: {e}")
            return {
                "status": HealthStatus.OFFLINE.value,
                "reason": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def get_agent_health(self, agent_type: str) -> Dict[str, Any]:
        """Get current health status of agent"""
        return self.agent_health.get(
            agent_type,
            {"status": HealthStatus.OFFLINE.value, "reason": "not_monitored"},
        )

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        if not self.agent_health:
            return {"status": "unknown", "reason": "no_health_data"}

        unhealthy_count = sum(
            1
            for health in self.agent_health.values()
            if health["status"]
            in [HealthStatus.UNHEALTHY.value, HealthStatus.OFFLINE.value]
        )

        degraded_count = sum(
            1
            for health in self.agent_health.values()
            if health["status"] == HealthStatus.DEGRADED.value
        )

        total_agents = len(self.agent_health)

        if unhealthy_count > 0:
            return {
                "status": "unhealthy",
                "unhealthy_agents": unhealthy_count,
                "degraded_agents": degraded_count,
                "total_agents": total_agents,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        elif degraded_count > 0:
            return {
                "status": "degraded",
                "degraded_agents": degraded_count,
                "total_agents": total_agents,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            return {
                "status": "healthy",
                "total_agents": total_agents,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# ============================================================================
# TASK SCHEDULER MODULE
# ============================================================================


class ScheduledTask:
    """Represents a scheduled recurring task"""

    def __init__(
        self,
        task_id: str,
        name: str,
        callback: Callable,
        interval_seconds: int,
        enabled: bool = True,
    ):
        self.task_id = task_id
        self.name = name
        self.callback = callback
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.execution_count = 0


class TaskScheduler:
    """
    Cron-like task scheduler for background operations.

    Schedules:
    - Sync operations (every 5 minutes)
    - Backups (every 6 hours)
    - Monitoring metrics collection (every 1 minute)
    - Health checks (every 60 seconds)
    """

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False

    def schedule_task(
        self,
        task_id: str,
        name: str,
        callback: Callable,
        interval_seconds: int,
        enabled: bool = True,
    ):
        """
        Schedule a recurring task.

        Args:
            task_id: Unique task identifier
            name: Human-readable task name
            callback: Async function to call
            interval_seconds: Run every N seconds
            enabled: Start enabled
        """
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            callback=callback,
            interval_seconds=interval_seconds,
            enabled=enabled,
        )

        task.next_run = datetime.now(timezone.utc) + timedelta(seconds=interval_seconds)

        self.tasks[task_id] = task
        logger.info(f"Scheduled task: {name} (every {interval_seconds}s)")

    async def start_scheduler(self):
        """Start the scheduler loop"""
        self.running = True
        logger.info("Task scheduler started")

        while self.running:
            now = datetime.now(timezone.utc)

            for task_id, task in self.tasks.items():
                if not task.enabled:
                    continue

                if task.next_run and now >= task.next_run:
                    # Execute task asynchronously
                    asyncio.create_task(self._execute_task(task))

            # Check every 10 seconds
            await asyncio.sleep(10)

    async def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Task scheduler stopped")

    async def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        try:
            logger.info(f"Executing scheduled task: {task.name}")

            start_time = datetime.now(timezone.utc)

            # Execute callback
            await task.callback()

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Update task
            task.last_run = start_time
            task.execution_count += 1
            task.next_run = datetime.now(timezone.utc) + timedelta(
                seconds=task.interval_seconds
            )

            logger.info(
                f"Task {task.name} completed in {execution_time:.2f}s. "
                f"Next run: {task.next_run.isoformat()}"
            )

        except Exception as e:
            logger.error(f"Error executing task {task.name}: {e}", exc_info=True)

    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks"""
        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "enabled": task.enabled,
                "interval_seconds": task.interval_seconds,
                "execution_count": task.execution_count,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
            }
            for task in self.tasks.values()
        ]


# ============================================================================
# MAESTRO ORCHESTRATOR AGENT
# ============================================================================


class MaestroOrchestratorAgent(BaseAgent):
    """
    Enhanced Maestro Orchestrator with load balancing, health monitoring,
    and task scheduling.

    The central nervous system of TwisterLab that:
    - Routes tickets to appropriate agents
    - Balances load across agent instances
    - Monitors agent health continuously
    - Schedules background tasks (sync, backup, monitoring)
    - Handles failover and circuit breaking
    """

    def __init__(self):
        super().__init__(
            name="maestro-orchestrator",
            display_name="Maestro Orchestrator",
            description="Central orchestrator coordinating all TwisterLab agents",
            model="deepseek-r1",
            temperature=0.1,  # Very low temperature for consistent routing
            tools=[],  # No direct tools, orchestrates other agents
        )

        # Initialize components
        self.load_balancer = LoadBalancer()
        self.health_monitor = HealthMonitor(check_interval=60)
        self.task_scheduler = TaskScheduler()

        # Initialize load balancer with agent instances
        self._initialize_load_balancer()

        # Schedule background tasks
        self._schedule_background_tasks()

        # Metrics tracking
        self.metrics = {
            "tickets_routed": 0,
            "classification_requests": 0,
            "resolution_requests": 0,
            "command_executions": 0,
            "errors": 0,
        }

        logger.info("MaestroOrchestratorAgent initialized")

    def _initialize_load_balancer(self):
        """Initialize load balancer with agent instances"""
        # Register classifier instances
        self.load_balancer.register_instance(
            "classifier", "classifier-001", max_load=10, priority=1
        )

        # Register resolver instances
        self.load_balancer.register_instance(
            "resolver", "resolver-001", max_load=5, priority=1
        )

        # Register desktop commander instances
        self.load_balancer.register_instance(
            "desktop_commander", "dc-001", max_load=3, priority=1
        )

        logger.info("Load balancer initialized with agent instances")

    def _schedule_background_tasks(self):
        """Schedule recurring background tasks"""

        # Sync every 5 minutes (300 seconds)
        self.task_scheduler.schedule_task(
            task_id="sync_data",
            name="Data Synchronization",
            callback=self._run_sync_task,
            interval_seconds=300,
            enabled=True,
        )

        # Backup every 6 hours (21600 seconds)
        self.task_scheduler.schedule_task(
            task_id="backup_data",
            name="Database Backup",
            callback=self._run_backup_task,
            interval_seconds=21600,
            enabled=True,
        )

        # Collect metrics every 1 minute (60 seconds)
        self.task_scheduler.schedule_task(
            task_id="collect_metrics",
            name="Metrics Collection",
            callback=self._run_monitoring_task,
            interval_seconds=60,
            enabled=True,
        )

        logger.info("Background tasks scheduled")

    async def start(self):
        """Start Maestro and all background services"""
        logger.info("Starting Maestro Orchestrator")

        # Start health monitoring
        asyncio.create_task(self.health_monitor.start_monitoring())

        # Start task scheduler
        asyncio.create_task(self.task_scheduler.start_scheduler())

        logger.info("Maestro Orchestrator started successfully")

    async def stop(self):
        """Stop Maestro gracefully"""
        logger.info("Stopping Maestro Orchestrator")

        await self.health_monitor.stop_monitoring()
        await self.task_scheduler.stop_scheduler()

        logger.info("Maestro Orchestrator stopped")

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestration task.

        Args:
            task: Task description (e.g., "route_ticket", "get_status")
            context: Task context with parameters

        Returns:
            Execution result
        """
        try:
            if task == "route_ticket":
                return await self.route_ticket_with_load_balancing(context)
            elif task == "get_status":
                return await self.get_orchestrator_status()
            elif task == "get_health":
                return self.health_monitor.get_system_health()
            else:
                return {"status": "error", "error": f"Unknown task: {task}"}

        except Exception as e:
            logger.error(f"Error executing task {task}: {e}", exc_info=True)
            self.metrics["errors"] += 1
            return {"status": "error", "error": str(e)}

    async def route_ticket_with_load_balancing(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced ticket routing with load balancing.

        Pipeline:
        1. Select classifier instance (load balanced)
        2. Classify ticket
        3. Select resolver instance (load balanced)
        4. Resolve ticket
        5. Execute commands via Desktop Commander (if needed)

        Args:
            context: Ticket context

        Returns:
            Routing result
        """
        try:
            self.metrics["tickets_routed"] += 1

            ticket_id = context.get("ticket_id")
            subject = context.get("subject")
            description = context.get("description")

            logger.info(f"Routing ticket {ticket_id} with load balancing")

            # Step 1: Select classifier instance
            classifier_instance = self.load_balancer.select_instance(
                "classifier", LoadBalancingStrategy.LEAST_LOADED
            )

            if not classifier_instance:
                return {"status": "error", "error": "No classifier instances available"}

            # Increment load
            self.load_balancer.increment_load("classifier", classifier_instance)

            try:
                # Step 2: Classify ticket
                classification_result = await self._classify_ticket(
                    ticket_id, subject, description
                )

                self.metrics["classification_requests"] += 1

            finally:
                # Decrement load
                self.load_balancer.decrement_load("classifier", classifier_instance)

            # Step 3: Select resolver instance
            resolver_instance = self.load_balancer.select_instance(
                "resolver", LoadBalancingStrategy.LEAST_LOADED
            )

            if not resolver_instance:
                return {"status": "error", "error": "No resolver instances available"}

            # Increment load
            self.load_balancer.increment_load("resolver", resolver_instance)

            try:
                # Step 4: Resolve ticket
                resolution_result = await self._resolve_ticket(
                    ticket_id, classification_result
                )

                self.metrics["resolution_requests"] += 1

            finally:
                # Decrement load
                self.load_balancer.decrement_load("resolver", resolver_instance)

            return {
                "status": "success",
                "ticket_id": ticket_id,
                "classification": classification_result,
                "resolution": resolution_result,
                "classifier_instance": classifier_instance,
                "resolver_instance": resolver_instance,
            }

        except Exception as e:
            logger.error(f"Error in load-balanced routing: {e}", exc_info=True)
            self.metrics["errors"] += 1
            return {"status": "error", "error": str(e)}

    async def _classify_ticket(
        self, ticket_id: str, subject: str, description: str
    ) -> Dict[str, Any]:
        """Call classifier agent (mock for now)"""
        # TODO: Replace with actual classifier call
        await asyncio.sleep(0.1)  # Simulate processing
        return {"category": "password_reset", "priority": "medium", "confidence": 0.92}

    async def _resolve_ticket(
        self, ticket_id: str, classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call resolver agent (mock for now)"""
        # TODO: Replace with actual resolver call
        await asyncio.sleep(0.2)  # Simulate processing
        return {
            "resolution_strategy": "direct",
            "status": "resolved",
            "confidence": 0.88,
        }

    async def _run_sync_task(self):
        """Execute sync task"""
        logger.info("Running sync task")
        # TODO: Call SyncAgent when implemented
        await asyncio.sleep(0.1)

    async def _run_backup_task(self):
        """Execute backup task"""
        logger.info("Running backup task")
        # TODO: Call BackupAgent when implemented
        await asyncio.sleep(0.1)

    async def _run_monitoring_task(self):
        """Execute monitoring task"""
        logger.info("Running monitoring task")
        # TODO: Call MonitoringAgent when implemented
        await asyncio.sleep(0.1)

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        return {
            "status": "running",
            "system_health": self.health_monitor.get_system_health(),
            "scheduled_tasks": self.task_scheduler.get_scheduled_tasks(),
            "load_balancer": {
                "strategies": [s.value for s in LoadBalancingStrategy],
                "agent_instances": {
                    agent_type: [
                        {
                            "instance_id": inst["instance_id"],
                            "current_load": inst["current_load"],
                            "max_load": inst["max_load"],
                            "is_healthy": inst["is_healthy"],
                        }
                        for inst in instances
                    ]
                    for agent_type, instances in self.load_balancer.agent_instances.items()
                },
            },
            "metrics": self.metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def health_check(self) -> Dict[str, Any]:
        """Agent health check"""
        return {
            "status": "healthy",
            "agent": self.name,
            "components": {
                "load_balancer": "operational",
                "health_monitor": "running"
                if self.health_monitor.running
                else "stopped",
                "task_scheduler": "running"
                if self.task_scheduler.running
                else "stopped",
            },
            "metrics": self.metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":

    async def main():
        maestro = MaestroOrchestratorAgent()

        # Start maestro
        await maestro.start()

        # Test routing
        result = await maestro.route_ticket_with_load_balancing(
            {
                "ticket_id": "TEST-001",
                "subject": "Password Reset Request",
                "description": "User cannot log in to system",
            }
        )

        print("\n=== Routing Result ===")
        print(result)

        # Get status
        status = await maestro.get_orchestrator_status()
        print("\n=== Orchestrator Status ===")
        print(status)

        # Let background tasks run for 5 seconds
        await asyncio.sleep(5)

        # Stop maestro
        await maestro.stop()

    asyncio.run(main())

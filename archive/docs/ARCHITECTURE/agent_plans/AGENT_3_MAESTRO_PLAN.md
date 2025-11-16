# AGENT 3: MAESTRO ORCHESTRATOR - ENHANCED IMPLEMENTATION PLAN

**Priority:** 3
**Status:** Partial Implementation (Enhancement Needed)
**Estimated Lines:** 900+
**Dependencies:** All agents (coordinates entire system)

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 Role in System
The MaestroOrchestratorAgent is the **central nervous system** of TwisterLab. It coordinates all agents, manages load balancing, handles failover, and maintains system health.

**Current Status:**
- Basic routing implemented (see `agents/orchestrator/maestro.py`)
- Needs: Load balancing, health monitoring, advanced scheduling

**Architecture:**
```
Email/API → Maestro → ClassifierAgent → Maestro → ResolverAgent
                ↓                                      ↓
         Health Monitoring                    Desktop-Commander
                ↓                                      ↓
         Load Balancing                            Resolution
                ↓
         Sync/Backup/Monitoring
```

### 1.2 Core Responsibilities
1. **Intelligent Routing** - Route tickets to appropriate agents
2. **Load Balancing** - Distribute work across agent instances
3. **Health Monitoring** - Track agent availability and performance
4. **Failover Management** - Handle agent failures gracefully
5. **Scheduling** - Schedule background tasks (sync, backup, monitoring)
6. **Result Aggregation** - Combine results from multiple agents

### 1.3 Enhanced Features Needed

**Current Maestro has:**
- Basic ticket routing
- Simple agent status tracking
- Escalation logic

**Needs to add:**
- Advanced load balancing algorithms
- Real-time health monitoring
- Automatic failover
- Task scheduling (cron-like)
- Performance optimization
- Circuit breaker pattern

---

## 2. ENHANCED CODE TEMPLATE

### 2.1 Load Balancing Extension

**Add to existing `agents/orchestrator/maestro.py`:**

```python
"""
Enhanced Maestro Orchestrator - Load Balancing Module
"""

from enum import Enum
from collections import defaultdict
import asyncio

class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    PRIORITY_BASED = "priority_based"
    WEIGHTED = "weighted"


class LoadBalancer:
    """
    Load balancer for distributing work across agent instances.
    """

    def __init__(self):
        self.agent_instances = defaultdict(list)
        self.round_robin_index = defaultdict(int)
        self.agent_loads = defaultdict(int)

    def register_instance(
        self,
        agent_type: str,
        instance_id: str,
        max_load: int = 10
    ):
        """Register agent instance"""
        self.agent_instances[agent_type].append({
            "instance_id": instance_id,
            "max_load": max_load,
            "current_load": 0,
            "status": "available"
        })

    def select_instance(
        self,
        agent_type: str,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED
    ) -> Optional[str]:
        """
        Select best agent instance based on strategy.
        """
        instances = self.agent_instances.get(agent_type, [])

        if not instances:
            return None

        # Filter available instances
        available = [
            inst for inst in instances
            if inst["status"] == "available" and
            inst["current_load"] < inst["max_load"]
        ]

        if not available:
            return None

        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin(agent_type, available)
        elif strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._least_loaded(available)
        elif strategy == LoadBalancingStrategy.PRIORITY_BASED:
            return self._priority_based(available)
        else:
            return available[0]["instance_id"]

    def _round_robin(self, agent_type: str, instances: List[Dict]) -> str:
        """Round-robin selection"""
        index = self.round_robin_index[agent_type]
        selected = instances[index % len(instances)]
        self.round_robin_index[agent_type] += 1
        return selected["instance_id"]

    def _least_loaded(self, instances: List[Dict]) -> str:
        """Select least loaded instance"""
        return min(instances, key=lambda x: x["current_load"])["instance_id"]

    def _priority_based(self, instances: List[Dict]) -> str:
        """Priority-based selection (first available)"""
        return instances[0]["instance_id"]

    def increment_load(self, agent_type: str, instance_id: str):
        """Increment instance load"""
        instances = self.agent_instances[agent_type]
        for inst in instances:
            if inst["instance_id"] == instance_id:
                inst["current_load"] += 1
                break

    def decrement_load(self, agent_type: str, instance_id: str):
        """Decrement instance load"""
        instances = self.agent_instances[agent_type]
        for inst in instances:
            if inst["instance_id"] == instance_id:
                inst["current_load"] = max(0, inst["current_load"] - 1)
                break
```

### 2.2 Health Monitoring Module

```python
"""
Enhanced Maestro Orchestrator - Health Monitoring Module
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

class HealthStatus(Enum):
    """Agent health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class HealthMonitor:
    """
    Monitors health of all agents in the system.
    """

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.agent_health = {}
        self.health_history = defaultdict(list)
        self.running = False

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.running = True

        while self.running:
            await self._check_all_agents()
            await asyncio.sleep(self.check_interval)

    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.running = False

    async def _check_all_agents(self):
        """Check health of all agents"""
        agent_types = [
            "classifier",
            "resolver",
            "desktop_commander",
            "sync",
            "backup",
            "monitoring"
        ]

        for agent_type in agent_types:
            health = await self._check_agent_health(agent_type)
            self.agent_health[agent_type] = health
            self.health_history[agent_type].append({
                "timestamp": datetime.now(timezone.utc),
                "status": health["status"],
                "metrics": health.get("metrics", {})
            })

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
            # Ping agent
            start_time = datetime.now(timezone.utc)

            # Call agent health endpoint (would be actual API call)
            # response = await agent_client.health_check()
            # Simulate for now
            await asyncio.sleep(0.1)

            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Evaluate health
            if response_time > 5.0:
                return {
                    "status": HealthStatus.DEGRADED.value,
                    "reason": "slow_response",
                    "response_time": response_time
                }

            # Check error rate (would query metrics database)
            error_rate = 0.05  # Mock 5% error rate

            if error_rate > 0.2:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "reason": "high_error_rate",
                    "error_rate": error_rate
                }
            elif error_rate > 0.1:
                return {
                    "status": HealthStatus.DEGRADED.value,
                    "reason": "elevated_error_rate",
                    "error_rate": error_rate
                }

            return {
                "status": HealthStatus.HEALTHY.value,
                "response_time": response_time,
                "error_rate": error_rate,
                "last_check": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking health of {agent_type}: {e}")
            return {
                "status": HealthStatus.OFFLINE.value,
                "reason": str(e)
            }

    def get_agent_health(self, agent_type: str) -> Dict[str, Any]:
        """Get current health status of agent"""
        return self.agent_health.get(agent_type, {
            "status": HealthStatus.OFFLINE.value,
            "reason": "not_monitored"
        })

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        if not self.agent_health:
            return {
                "status": "unknown",
                "reason": "no_health_data"
            }

        unhealthy_count = sum(
            1 for health in self.agent_health.values()
            if health["status"] in [
                HealthStatus.UNHEALTHY.value,
                HealthStatus.OFFLINE.value
            ]
        )

        degraded_count = sum(
            1 for health in self.agent_health.values()
            if health["status"] == HealthStatus.DEGRADED.value
        )

        if unhealthy_count > 0:
            return {
                "status": "unhealthy",
                "unhealthy_agents": unhealthy_count,
                "total_agents": len(self.agent_health)
            }
        elif degraded_count > 0:
            return {
                "status": "degraded",
                "degraded_agents": degraded_count,
                "total_agents": len(self.agent_health)
            }
        else:
            return {
                "status": "healthy",
                "total_agents": len(self.agent_health)
            }
```

### 2.3 Task Scheduler Module

```python
"""
Enhanced Maestro Orchestrator - Task Scheduler Module
"""

import asyncio
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, List


class ScheduledTask:
    """Represents a scheduled task"""

    def __init__(
        self,
        task_id: str,
        name: str,
        callback: Callable,
        schedule: str,  # Cron-like: "*/5 * * * *"
        enabled: bool = True
    ):
        self.task_id = task_id
        self.name = name
        self.callback = callback
        self.schedule = schedule
        self.enabled = enabled
        self.last_run = None
        self.next_run = None


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
        enabled: bool = True
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
            schedule=f"*/{interval_seconds} * * * *",
            enabled=enabled
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
                    # Execute task
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

            # Schedule next run (extract interval from schedule string)
            # For simplicity, assume interval is in task metadata
            # In production, parse cron expression properly
            task.next_run = datetime.now(timezone.utc) + timedelta(seconds=60)

            logger.info(
                f"Task {task.name} completed in {execution_time:.2f}s. "
                f"Next run: {task.next_run}"
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
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None
            }
            for task in self.tasks.values()
        ]
```

### 2.4 Enhanced Maestro Class

**Add to existing `MaestroOrchestratorAgent`:**

```python
class MaestroOrchestratorAgent(TwisterAgent):
    """Enhanced with load balancing, health monitoring, and scheduling"""

    def __init__(self):
        # ... existing initialization ...

        # Add new components
        self.load_balancer = LoadBalancer()
        self.health_monitor = HealthMonitor(check_interval=60)
        self.task_scheduler = TaskScheduler()

        # Initialize load balancer with agent instances
        self._initialize_load_balancer()

        # Schedule background tasks
        self._schedule_background_tasks()

    def _initialize_load_balancer(self):
        """Initialize load balancer with agent instances"""
        # Register agent instances
        self.load_balancer.register_instance("classifier", "classifier-001", max_load=10)
        self.load_balancer.register_instance("resolver", "resolver-001", max_load=5)
        self.load_balancer.register_instance("desktop_commander", "dc-001", max_load=3)

    def _schedule_background_tasks(self):
        """Schedule recurring background tasks"""

        # Sync every 5 minutes
        self.task_scheduler.schedule_task(
            task_id="sync_data",
            name="Data Synchronization",
            callback=self._run_sync_task,
            interval_seconds=300
        )

        # Backup every 6 hours
        self.task_scheduler.schedule_task(
            task_id="backup_data",
            name="Database Backup",
            callback=self._run_backup_task,
            interval_seconds=21600
        )

        # Collect metrics every 1 minute
        self.task_scheduler.schedule_task(
            task_id="collect_metrics",
            name="Metrics Collection",
            callback=self._run_monitoring_task,
            interval_seconds=60
        )

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

    async def _run_sync_task(self):
        """Execute sync task"""
        from agents.support.sync_agent import SyncAgent
        sync_agent = SyncAgent()
        await sync_agent.execute("Run scheduled sync", {})

    async def _run_backup_task(self):
        """Execute backup task"""
        from agents.support.backup_agent import BackupAgent
        backup_agent = BackupAgent()
        await backup_agent.execute("Run scheduled backup", {})

    async def _run_monitoring_task(self):
        """Execute monitoring task"""
        from agents.support.monitoring_agent import MonitoringAgent
        monitoring_agent = MonitoringAgent()
        await monitoring_agent.execute("Collect metrics", {})

    async def route_ticket_with_load_balancing(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced ticket routing with load balancing.
        """
        try:
            # Select best classifier instance
            classifier_instance = self.load_balancer.select_instance(
                "classifier",
                LoadBalancingStrategy.LEAST_LOADED
            )

            if not classifier_instance:
                return {
                    "status": "error",
                    "error": "No classifier instances available"
                }

            # Increment load
            self.load_balancer.increment_load("classifier", classifier_instance)

            try:
                # Execute classification
                classification_result = await self._classify_ticket(
                    context.get("ticket_id"),
                    context.get("subject"),
                    context.get("description")
                )

                # Continue with existing routing logic...
                # ...

            finally:
                # Decrement load
                self.load_balancer.decrement_load("classifier", classifier_instance)

            return classification_result

        except Exception as e:
            logger.error(f"Error in load-balanced routing: {e}")
            return {"status": "error", "error": str(e)}

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        return {
            "status": "running",
            "system_health": self.health_monitor.get_system_health(),
            "scheduled_tasks": self.task_scheduler.get_scheduled_tasks(),
            "load_balancer": {
                "strategies": [s.value for s in LoadBalancingStrategy],
                "agent_instances": dict(self.load_balancer.agent_instances)
            },
            "metrics": self.get_metrics(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
```

---

## 3. API ENDPOINTS

**Add to `agents/api/routes_orchestrator.py`:**

```python
from fastapi import APIRouter
from agents.orchestrator.maestro import MaestroOrchestratorAgent

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])

# Initialize Maestro
maestro = MaestroOrchestratorAgent()


@router.get("/status")
async def get_orchestrator_status():
    """Get orchestrator comprehensive status"""
    return await maestro.get_orchestrator_status()


@router.get("/health")
async def get_system_health():
    """Get overall system health"""
    return maestro.health_monitor.get_system_health()


@router.get("/agents/health")
async def get_agents_health():
    """Get health status of all agents"""
    return maestro.health_monitor.agent_health


@router.get("/tasks")
async def get_scheduled_tasks():
    """Get all scheduled tasks"""
    return {
        "tasks": maestro.task_scheduler.get_scheduled_tasks()
    }


@router.post("/tasks/{task_id}/enable")
async def enable_task(task_id: str):
    """Enable a scheduled task"""
    if task_id in maestro.task_scheduler.tasks:
        maestro.task_scheduler.tasks[task_id].enabled = True
        return {"status": "enabled", "task_id": task_id}
    return {"status": "error", "error": "Task not found"}


@router.post("/tasks/{task_id}/disable")
async def disable_task(task_id: str):
    """Disable a scheduled task"""
    if task_id in maestro.task_scheduler.tasks:
        maestro.task_scheduler.tasks[task_id].enabled = False
        return {"status": "disabled", "task_id": task_id}
    return {"status": "error", "error": "Task not found"}


@router.get("/load-balancer/status")
async def get_load_balancer_status():
    """Get load balancer status"""
    return {
        "agent_instances": dict(maestro.load_balancer.agent_instances),
        "current_loads": dict(maestro.load_balancer.agent_loads)
    }
```

---

## 4. TESTING STRATEGY

```python
# tests/test_maestro_enhanced.py

@pytest.mark.asyncio
async def test_load_balancer():
    """Test load balancing functionality"""
    lb = LoadBalancer()

    lb.register_instance("classifier", "c1", max_load=5)
    lb.register_instance("classifier", "c2", max_load=5)

    # Test round-robin
    instance1 = lb.select_instance("classifier", LoadBalancingStrategy.ROUND_ROBIN)
    instance2 = lb.select_instance("classifier", LoadBalancingStrategy.ROUND_ROBIN)

    assert instance1 != instance2

@pytest.mark.asyncio
async def test_health_monitoring():
    """Test health monitoring"""
    monitor = HealthMonitor(check_interval=1)

    # Check single agent
    health = await monitor._check_agent_health("classifier")

    assert "status" in health
    assert health["status"] in [s.value for s in HealthStatus]

@pytest.mark.asyncio
async def test_task_scheduling():
    """Test task scheduler"""
    scheduler = TaskScheduler()

    executed = []

    async def test_task():
        executed.append(datetime.now(timezone.utc))

    scheduler.schedule_task(
        "test_task",
        "Test Task",
        test_task,
        interval_seconds=1
    )

    # Start scheduler for 3 seconds
    asyncio.create_task(scheduler.start_scheduler())
    await asyncio.sleep(3)
    await scheduler.stop_scheduler()

    # Should have executed at least once
    assert len(executed) > 0
```

---

## 5. DEPLOYMENT

### Configuration
```bash
# Maestro Configuration
MAESTRO_HEALTH_CHECK_INTERVAL=60
MAESTRO_LOAD_BALANCING_STRATEGY=least_loaded
MAESTRO_MAX_CONCURRENT_TICKETS=50

# Background Tasks
MAESTRO_SYNC_INTERVAL=300
MAESTRO_BACKUP_INTERVAL=21600
MAESTRO_MONITORING_INTERVAL=60
```

---

**Next Agent:** [Sync-AgentAgent (Priority 4)](AGENT_4_SYNC_PLAN.md)

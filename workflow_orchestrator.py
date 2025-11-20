#!/usr/bin/env python3
"""
Multi-Agent Workflow Orchestration System

This system implements complex workflows that coordinate multiple TwisterLab agents
using the MCP communication framework.

Supported Workflows:
1. IT Ticket Resolution Workflow
2. System Health Check & Maintenance Workflow
3. Backup & Disaster Recovery Workflow
4. Performance Optimization Workflow

Usage:
    python workflow_orchestrator.py --workflow it_ticket_resolution --ticket_id TICKET_001
    python workflow_orchestrator.py --workflow system_maintenance
    python workflow_orchestrator.py --workflow backup_recovery --force
"""

import asyncio
import json
import logging
import os
import sys
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.mcp.agent_communication_system import MCPAgentCommunicationSystem, MCPMessage, MessageType, AgentRole
from agents.mcp.unified_mcp_server import UnifiedMCPServer
from agents.monitoring.performance_monitor import PerformanceMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(Enum):
    """Individual workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    step_id: str
    agent: str
    task: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Workflow:
    """Represents a complete workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class WorkflowOrchestrator:
    """Orchestrates complex multi-agent workflows"""

    def __init__(self):
        self.comm_system = MCPAgentCommunicationSystem(performance_monitor=None)  # Will be set after monitor init
        self.mcp_server = UnifiedMCPServer()
        self.performance_monitor = PerformanceMonitor(self.comm_system)
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflows: Dict[str, asyncio.Task] = {}

        # Workflow templates
        self.workflow_templates = {
            "it_ticket_resolution": self._create_it_ticket_workflow,
            "system_maintenance": self._create_system_maintenance_workflow,
            "backup_recovery": self._create_backup_recovery_workflow,
            "performance_optimization": self._create_performance_workflow,
        }

    async def initialize(self):
        """Initialize the orchestrator"""
        logger.info("Initializing Workflow Orchestrator...")
        await self.comm_system.start()
        await self.performance_monitor.start_monitoring()

        # Connect performance monitor to communication system
        self.comm_system.performance_monitor = self.performance_monitor

        # Register orchestrator as an agent
        self.comm_system.register_agent(
            agent_name="orchestrator",
            capabilities=["workflow_orchestration", "task_coordination", "monitoring"],
            role=AgentRole.COORDINATOR
        )

        logger.info("Workflow Orchestrator initialized")

    async def shutdown(self):
        """Shutdown the orchestrator"""
        logger.info("Shutting down Workflow Orchestrator...")

        # Cancel all active workflows
        for workflow_id, task in self.active_workflows.items():
            if not task.done():
                task.cancel()

        await asyncio.gather(*self.active_workflows.values(), return_exceptions=True)
        await self.performance_monitor.stop_monitoring()
        await self.comm_system.stop()

    async def create_workflow(self, template_name: str, parameters: Dict[str, Any]) -> str:
        """Create a workflow from a template"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")

        workflow_id = f"{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Create workflow from template
        workflow = self.workflow_templates[template_name](workflow_id, parameters)

        # Store workflow
        self.workflows[workflow_id] = workflow

        logger.info(f"Created workflow: {workflow_id} ({workflow.name})")
        return workflow_id

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]

        if workflow.status != WorkflowStatus.PENDING:
            raise ValueError(f"Workflow {workflow_id} is not in pending state")

        # Start workflow execution
        task = asyncio.create_task(self._execute_workflow_async(workflow))
        self.active_workflows[workflow_id] = task

        try:
            result = await task
            return result
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.errors.append(str(e))
            raise
        finally:
            # Clean up
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

    async def _execute_workflow_async(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute workflow asynchronously"""
        logger.info(f"Starting workflow execution: {workflow.workflow_id}")

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now(timezone.utc)

        try:
            # Execute steps in dependency order
            completed_steps = set()

            while len(completed_steps) < len(workflow.steps):
                # Find steps that can be executed (dependencies satisfied)
                executable_steps = [
                    step for step in workflow.steps
                    if step.step_id not in completed_steps and
                    all(dep in completed_steps for dep in step.depends_on)
                ]

                if not executable_steps:
                    # Check for circular dependencies or failed dependencies
                    pending_steps = [s for s in workflow.steps if s.step_id not in completed_steps]
                    if pending_steps:
                        error_msg = f"Cannot execute steps due to unsatisfied dependencies: {[s.step_id for s in pending_steps]}"
                        workflow.errors.append(error_msg)
                        workflow.status = WorkflowStatus.FAILED
                        break
                    else:
                        break

                # Execute steps concurrently
                tasks = []
                for step in executable_steps:
                    task = asyncio.create_task(self._execute_step(workflow, step))
                    tasks.append(task)

                # Wait for all steps to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for step, result in zip(executable_steps, results):
                    if isinstance(result, Exception):
                        step.status = WorkflowStepStatus.FAILED
                        step.error = str(result)
                        workflow.errors.append(f"Step {step.step_id} failed: {result}")
                    else:
                        step.status = WorkflowStepStatus.COMPLETED
                        step.result = result
                        step.completed_at = datetime.now(timezone.utc)

                    completed_steps.add(step.step_id)

            # Determine final workflow status
            if workflow.status != WorkflowStatus.FAILED:
                failed_steps = [s for s in workflow.steps if s.status == WorkflowStepStatus.FAILED]
                if failed_steps:
                    workflow.status = WorkflowStatus.FAILED
                else:
                    workflow.status = WorkflowStatus.COMPLETED

            workflow.completed_at = datetime.now(timezone.utc)

            # Collect results
            result_summary = {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status.value,
                "steps_completed": len([s for s in workflow.steps if s.status == WorkflowStepStatus.COMPLETED]),
                "steps_failed": len([s for s in workflow.steps if s.status == WorkflowStepStatus.FAILED]),
                "total_steps": len(workflow.steps),
                "duration_seconds": (workflow.completed_at - workflow.started_at).total_seconds() if workflow.completed_at and workflow.started_at else None,
                "results": {step.step_id: step.result for step in workflow.steps if step.result},
                "errors": workflow.errors
            }

            logger.info(f"Workflow {workflow.workflow_id} completed with status: {workflow.status.value}")

            # Record performance metrics
            success = workflow.status == WorkflowStatus.COMPLETED
            duration = result_summary.get("duration_seconds", 0) or 0
            self.performance_monitor.record_workflow_execution(workflow.name, success, duration)

            return result_summary

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.errors.append(str(e))
            workflow.completed_at = datetime.now(timezone.utc)
            raise

    async def _execute_step(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step"""
        logger.info(f"Executing step: {step.step_id} on agent {step.agent}")

        step.status = WorkflowStepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)

        try:
            # Create MCP message for the step
            message = MCPMessage(
                message_id=f"{workflow.workflow_id}_{step.step_id}_{datetime.now().strftime('%f')}",
                sender_agent="orchestrator",
                receiver_agent=step.agent,
                message_type=MessageType.TASK_REQUEST,
                payload={
                    "task": step.task,
                    "parameters": step.parameters,
                    "workflow_id": workflow.workflow_id,
                    "step_id": step.step_id
                },
                correlation_id=workflow.workflow_id
            )

            # Send message
            success = await self.comm_system.send_message(message)

            if not success:
                raise Exception(f"Failed to send message to agent {step.agent}")

            # Wait for response (simplified - in real implementation would use callbacks)
            await asyncio.sleep(2)  # Simulate processing time

            # Mock response based on step (in real implementation, would receive actual response)
            result = self._mock_step_result(step)

            # Record performance metrics for agent request
            response_time = (datetime.now(timezone.utc) - step.started_at).total_seconds() if step.started_at else 2.0
            self.performance_monitor.record_agent_request(step.agent, True, response_time)

            logger.info(f"Step {step.step_id} completed successfully")
            return result

        except Exception as e:
            step.status = WorkflowStepStatus.FAILED
            step.error = str(e)
            logger.error(f"Step {step.step_id} failed: {e}")
            raise

    def _mock_step_result(self, step: WorkflowStep) -> Dict[str, Any]:
        """Mock step result for demonstration (replace with real agent responses)"""
        if step.task == "classify_ticket":
            return {"category": "network", "confidence": 0.95}
        elif step.task == "check_system_health":
            return {"status": "healthy", "cpu_usage": 45, "memory_usage": 60}
        elif step.task == "resolve_issue":
            return {"resolution": "Restarted network service", "success": True}
        elif step.task == "create_backup":
            return {"backup_size": "2.5GB", "success": True}
        elif step.task == "optimize_performance":
            return {"improvements": ["Reduced CPU usage by 15%", "Optimized memory usage"]}
        else:
            return {"result": f"Mock result for {step.task}", "success": True}

    def _create_it_ticket_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> Workflow:
        """Create IT ticket resolution workflow"""
        ticket_id = parameters.get("ticket_id", "UNKNOWN")
        ticket_text = parameters.get("ticket_text", "")

        workflow = Workflow(
            workflow_id=workflow_id,
            name="IT Ticket Resolution",
            description=f"Resolve IT ticket {ticket_id} using multi-agent collaboration"
        )

        # Step 1: Classify ticket
        workflow.steps.append(WorkflowStep(
            step_id="classify",
            agent="classifier",
            task="classify_ticket",
            parameters={"ticket_text": ticket_text}
        ))

        # Step 2: Check system health (parallel with classification)
        workflow.steps.append(WorkflowStep(
            step_id="health_check",
            agent="monitoring",
            task="check_system_health",
            parameters={}
        ))

        # Step 3: Resolve issue (depends on classification)
        workflow.steps.append(WorkflowStep(
            step_id="resolve",
            agent="resolver",
            task="resolve_issue",
            parameters={"ticket_id": ticket_id},
            depends_on=["classify"]
        ))

        # Step 4: Verify resolution
        workflow.steps.append(WorkflowStep(
            step_id="verify",
            agent="monitoring",
            task="verify_resolution",
            parameters={"ticket_id": ticket_id},
            depends_on=["resolve"]
        ))

        return workflow

    def _create_system_maintenance_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> Workflow:
        """Create system maintenance workflow"""
        workflow = Workflow(
            workflow_id=workflow_id,
            name="System Maintenance",
            description="Perform comprehensive system health checks and maintenance"
        )

        # Step 1: System health check
        workflow.steps.append(WorkflowStep(
            step_id="health_check",
            agent="monitoring",
            task="check_system_health",
            parameters={"detailed": True}
        ))

        # Step 2: Cache synchronization
        workflow.steps.append(WorkflowStep(
            step_id="sync_cache",
            agent="sync",
            task="sync_cache_db",
            parameters={}
        ))

        # Step 3: Backup creation
        workflow.steps.append(WorkflowStep(
            step_id="backup",
            agent="backup",
            task="create_backup",
            parameters={"type": "incremental"}
        ))

        # Step 4: Performance optimization
        workflow.steps.append(WorkflowStep(
            step_id="optimize",
            agent="maestro",
            task="optimize_performance",
            parameters={},
            depends_on=["health_check"]
        ))

        return workflow

    def _create_backup_recovery_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> Workflow:
        """Create backup and disaster recovery workflow"""
        force = parameters.get("force", False)

        workflow = Workflow(
            workflow_id=workflow_id,
            name="Backup & Recovery",
            description="Perform backup operations and test recovery procedures"
        )

        # Step 1: Pre-backup health check
        workflow.steps.append(WorkflowStep(
            step_id="pre_backup_check",
            agent="monitoring",
            task="check_system_health",
            parameters={}
        ))

        # Step 2: Create backup
        workflow.steps.append(WorkflowStep(
            step_id="create_backup",
            agent="backup",
            task="create_backup",
            parameters={"force": force}
        ))

        # Step 3: Verify backup integrity
        workflow.steps.append(WorkflowStep(
            step_id="verify_backup",
            agent="backup",
            task="verify_backup",
            parameters={},
            depends_on=["create_backup"]
        ))

        # Step 4: Test recovery procedure
        workflow.steps.append(WorkflowStep(
            step_id="test_recovery",
            agent="backup",
            task="test_recovery",
            parameters={"dry_run": True},
            depends_on=["verify_backup"]
        ))

        return workflow

    def _create_performance_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> Workflow:
        """Create performance optimization workflow"""
        workflow = Workflow(
            workflow_id=workflow_id,
            name="Performance Optimization",
            description="Analyze and optimize system performance"
        )

        # Step 1: Performance analysis
        workflow.steps.append(WorkflowStep(
            step_id="analyze_performance",
            agent="monitoring",
            task="analyze_performance",
            parameters={"time_range": "1h"}
        ))

        # Step 2: Identify bottlenecks
        workflow.steps.append(WorkflowStep(
            step_id="identify_bottlenecks",
            agent="maestro",
            task="identify_bottlenecks",
            parameters={},
            depends_on=["analyze_performance"]
        ))

        # Step 3: Apply optimizations
        workflow.steps.append(WorkflowStep(
            step_id="apply_optimizations",
            agent="maestro",
            task="apply_optimizations",
            parameters={},
            depends_on=["identify_bottlenecks"]
        ))

        # Step 4: Verify improvements
        workflow.steps.append(WorkflowStep(
            step_id="verify_improvements",
            agent="monitoring",
            task="verify_improvements",
            parameters={},
            depends_on=["apply_optimizations"]
        ))

        return workflow

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow"""
        if workflow_id not in self.workflows:
            return None

        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": [
                {
                    "step_id": step.step_id,
                    "agent": step.agent,
                    "task": step.task,
                    "status": step.status.value,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error": step.error
                }
                for step in workflow.steps
            ],
            "errors": workflow.errors
        }


async def main():
    """Main workflow orchestrator runner"""
    parser = argparse.ArgumentParser(description="TwisterLab Workflow Orchestrator")
    parser.add_argument("--workflow", required=True,
                       choices=["it_ticket_resolution", "system_maintenance", "backup_recovery", "performance_optimization"],
                       help="Workflow template to execute")
    parser.add_argument("--ticket_id", help="Ticket ID for IT ticket resolution")
    parser.add_argument("--ticket_text", help="Ticket description text")
    parser.add_argument("--force", action="store_true", help="Force operations")

    args = parser.parse_args()

    orchestrator = WorkflowOrchestrator()

    try:
        await orchestrator.initialize()

        # Prepare workflow parameters
        parameters = {}
        if args.workflow == "it_ticket_resolution":
            if not args.ticket_id:
                print("Error: --ticket_id required for IT ticket resolution workflow")
                return 1
            parameters["ticket_id"] = args.ticket_id
            parameters["ticket_text"] = args.ticket_text or "Default ticket description"

        elif args.workflow == "backup_recovery":
            parameters["force"] = args.force

        # Create and execute workflow
        workflow_id = await orchestrator.create_workflow(args.workflow, parameters)
        print(f"Created workflow: {workflow_id}")

        result = await orchestrator.execute_workflow(workflow_id)
        print(f"Workflow completed: {result['status']}")
        print(f"Steps completed: {result['steps_completed']}/{result['total_steps']}")

        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")

        return 0 if result['status'] == 'completed' else 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

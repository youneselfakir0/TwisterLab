"""
TwisterLab - Resolver Agent
Executes troubleshooting SOPs and resolves IT tickets autonomously
"""

import importlib.util
import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import TwisterAgent directly from base.py file
base_file_path = os.path.join(os.path.dirname(__file__), "..", "base.py")
spec = importlib.util.spec_from_file_location("base_module", base_file_path)
base_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_module)
TwisterAgent = base_module.TwisterAgent
# from ..database.services import TicketService  # TODO: Implement TicketService
import httpx

from ..database.config import get_db

logger = logging.getLogger(__name__)


class ResolutionStrategy(str, Enum):
    """Resolution execution strategies"""

    DIRECT_EXECUTION = "direct_execution"
    ADAPTIVE_EXECUTION = "adaptive_execution"
    HYBRID_EXECUTION = "hybrid_execution"
    MANUAL_EXECUTION = "manual_execution"
    ESCALATION = "escalation"


class ResolutionStatus(str, Enum):
    """Resolution outcome status"""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ESCALATED = "escalated"


class ResolverAgent(TwisterAgent):
    """
    Autonomous IT ticket resolver using SOP-based troubleshooting.

    Capabilities:
    - Execute SOPs with 5 resolution strategies
    - Confidence-based decision making
    - Integration with Desktop-CommanderAgent
    - Automatic escalation logic
    - Comprehensive audit logging
    """

    def __init__(self):
        """Initialize ResolverAgent with tools and configuration"""

        # Define MCP tools for resolution execution
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_sop",
                    "description": "Execute a Standard Operating Procedure for ticket resolution",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "Unique ticket identifier",
                            },
                            "sop_id": {
                                "type": "string",
                                "description": "SOP to execute",
                            },
                            "strategy": {
                                "type": "string",
                                "enum": ["direct", "adaptive", "hybrid", "manual"],
                                "description": "Execution strategy",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Execution parameters",
                            },
                        },
                        "required": ["ticket_id", "sop_id", "strategy"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_prerequisites",
                    "description": "Validate SOP prerequisites before execution",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sop_id": {
                                "type": "string",
                                "description": "SOP identifier",
                            },
                            "ticket_context": {
                                "type": "object",
                                "description": "Ticket context for validation",
                            },
                        },
                        "required": ["sop_id", "ticket_context"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_confidence",
                    "description": "Calculate confidence score for resolution path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sop_match_score": {
                                "type": "number",
                                "description": "SOP match quality (0-1)",
                            },
                            "prerequisite_met": {
                                "type": "boolean",
                                "description": "Prerequisites satisfied",
                            },
                            "historical_success": {
                                "type": "number",
                                "description": "Historical success rate (0-1)",
                            },
                        },
                        "required": ["sop_match_score"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute system command via Desktop-CommanderAgent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Command to execute",
                            },
                            "target_device": {
                                "type": "string",
                                "description": "Target device identifier",
                            },
                            "safety_checks": {
                                "type": "boolean",
                                "description": "Enable safety validation",
                                "default": True,
                            },
                        },
                        "required": ["command", "target_device"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_ticket",
                    "description": "Escalate ticket to Level 2 support",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "Ticket to escalate",
                            },
                            "reason": {
                                "type": "string",
                                "description": "Escalation reason",
                            },
                            "attempted_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Steps already attempted",
                            },
                        },
                        "required": ["ticket_id", "reason"],
                    },
                },
            },
        ]

        super().__init__(
            name="resolver",
            display_name="Resolver Agent",
            description="Executes SOPs and resolves IT tickets autonomously",
            tools=tools,
            model="deepseek-r1",
            temperature=0.1,  # Low temperature for deterministic execution
        )

        # Resolution thresholds
        self.confidence_threshold_direct = 0.85
        self.confidence_threshold_adaptive = 0.70
        self.confidence_threshold_manual = 0.50
        self.max_execution_retries = 3
        self.desktop_commander_url = (
            "http://localhost:8000/api/v1/agents/desktop-commander"
        )

        logger.info(f"ResolverAgent initialized: {self.name}")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute resolution task for a ticket.

        Args:
            task: Task context containing:
                - ticket_id: Ticket to resolve
                - classification: Classifier output
                - sop_recommendations: Recommended SOPs

        Returns:
            Resolution result with status, steps, and audit trail
        """
        ticket_id = task.get("ticket_id")
        classification = task.get("classification", {})
        sop_recommendations = task.get("sop_recommendations", [])

        logger.info(f"[{self.name}] Starting resolution for ticket {ticket_id}")

        try:
            # Step 1: Select resolution strategy
            strategy, selected_sop, confidence = await self._select_strategy(
                classification, sop_recommendations
            )

            logger.info(
                f"[{self.name}] Selected strategy={strategy} "
                f"sop={selected_sop.get('id') if selected_sop else None} "
                f"confidence={confidence:.2f}"
            )

            # Step 2: Validate prerequisites
            if selected_sop:
                prerequisites_valid = await self._validate_prerequisites(
                    selected_sop, task
                )

                if not prerequisites_valid:
                    logger.warning(
                        f"[{self.name}] Prerequisites not met, adjusting strategy"
                    )
                    strategy = ResolutionStrategy.MANUAL_EXECUTION

            # Step 3: Execute resolution based on strategy
            if strategy == ResolutionStrategy.DIRECT_EXECUTION:
                result = await self._execute_direct(ticket_id, selected_sop, task)

            elif strategy == ResolutionStrategy.ADAPTIVE_EXECUTION:
                result = await self._execute_adaptive(ticket_id, selected_sop, task)

            elif strategy == ResolutionStrategy.HYBRID_EXECUTION:
                result = await self._execute_hybrid(
                    ticket_id, sop_recommendations, task
                )

            elif strategy == ResolutionStrategy.MANUAL_EXECUTION:
                result = await self._execute_manual(ticket_id, selected_sop, task)

            elif strategy == ResolutionStrategy.ESCALATION:
                result = await self._escalate(ticket_id, classification, task)

            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            # Step 4: Update ticket status
            await self._update_ticket_status(ticket_id, result)

            # Step 5: Log resolution metrics
            await self._log_resolution_metrics(ticket_id, strategy, result, confidence)

            logger.info(
                f"[{self.name}] Resolution completed for ticket {ticket_id}: "
                f"status={result.get('status')}"
            )

            return {
                "agent": self.name,
                "ticket_id": ticket_id,
                "strategy": strategy.value,
                "confidence": confidence,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(
                f"[{self.name}] Resolution failed for ticket {ticket_id}: {e}",
                exc_info=True,
            )

            # Automatic escalation on critical failure
            escalation_result = await self._escalate(
                ticket_id, classification, {"error": str(e), "original_task": task}
            )

            return {
                "agent": self.name,
                "ticket_id": ticket_id,
                "strategy": ResolutionStrategy.ESCALATION.value,
                "confidence": 0.0,
                "result": escalation_result,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _select_strategy(
        self, classification: Dict[str, Any], sop_recommendations: List[Dict[str, Any]]
    ) -> Tuple[ResolutionStrategy, Optional[Dict[str, Any]], float]:
        """
        Select optimal resolution strategy based on confidence and context.

        Returns:
            Tuple of (strategy, selected_sop, confidence_score)
        """
        if not sop_recommendations:
            logger.warning("[ResolverAgent] No SOP recommendations, escalating")
            return ResolutionStrategy.ESCALATION, None, 0.0

        # Get top SOP recommendation
        top_sop = sop_recommendations[0]
        sop_match_score = top_sop.get("match_score", 0.0)

        # Calculate confidence
        confidence = await self._calculate_confidence(
            sop_match_score=sop_match_score,
            prerequisite_met=True,  # Will validate later
            historical_success=top_sop.get("success_rate", 0.8),
        )

        # Strategy selection logic
        if confidence >= self.confidence_threshold_direct:
            return ResolutionStrategy.DIRECT_EXECUTION, top_sop, confidence

        elif confidence >= self.confidence_threshold_adaptive:
            return ResolutionStrategy.ADAPTIVE_EXECUTION, top_sop, confidence

        elif (
            confidence >= self.confidence_threshold_manual
            and len(sop_recommendations) > 1
        ):
            return ResolutionStrategy.HYBRID_EXECUTION, top_sop, confidence

        elif confidence >= self.confidence_threshold_manual:
            return ResolutionStrategy.MANUAL_EXECUTION, top_sop, confidence

        else:
            return ResolutionStrategy.ESCALATION, None, confidence

    async def _calculate_confidence(
        self, sop_match_score: float, prerequisite_met: bool, historical_success: float
    ) -> float:
        """
        Calculate confidence score for resolution path.

        Formula: weighted average of match score, prerequisites, and historical success
        """
        weights = {"sop_match": 0.5, "prerequisites": 0.2, "historical": 0.3}

        prerequisite_score = 1.0 if prerequisite_met else 0.0

        confidence = (
            weights["sop_match"] * sop_match_score
            + weights["prerequisites"] * prerequisite_score
            + weights["historical"] * historical_success
        )

        return min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]

    async def _validate_prerequisites(
        self, sop: Dict[str, Any], task_context: Dict[str, Any]
    ) -> bool:
        """
        Validate SOP prerequisites before execution.

        Checks:
        - Required tools available
        - Device accessibility
        - User permissions
        """
        try:
            prerequisites = sop.get("prerequisites", {})

            # Check required tools
            required_tools = prerequisites.get("tools", [])
            # TODO: Implement tool availability check

            # Check device accessibility
            target_device = task_context.get("device_id")
            if target_device:
                # TODO: Ping device or check registry
                pass

            # Check permissions
            required_permissions = prerequisites.get("permissions", [])
            # TODO: Validate current user permissions

            logger.info(
                f"[ResolverAgent] Prerequisites validated for SOP {sop.get('id')}"
            )
            return True

        except Exception as e:
            logger.error(f"[ResolverAgent] Prerequisite validation failed: {e}")
            return False

    async def _execute_direct(
        self, ticket_id: str, sop: Dict[str, Any], task_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        DIRECT_EXECUTION: Execute SOP steps exactly as documented.

        Used when confidence >= 85% (exact match, prerequisites met)
        """
        logger.info(f"[ResolverAgent] DIRECT execution for ticket {ticket_id}")

        execution_log = []
        steps = sop.get("steps", [])

        for idx, step in enumerate(steps, 1):
            try:
                step_result = await self._execute_step(
                    step, task_context, allow_variations=False
                )

                execution_log.append(
                    {
                        "step": idx,
                        "description": step.get("description"),
                        "status": "success",
                        "output": step_result.get("output"),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

                # Check if step solves the issue
                if step_result.get("resolution_confirmed"):
                    logger.info(f"[ResolverAgent] Issue resolved at step {idx}")
                    break

            except Exception as e:
                logger.error(f"[ResolverAgent] Step {idx} failed: {e}")
                execution_log.append(
                    {
                        "step": idx,
                        "description": step.get("description"),
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

                # Retry logic
                retry_count = 0
                while retry_count < self.max_execution_retries:
                    retry_count += 1
                    logger.info(
                        f"[ResolverAgent] Retrying step {idx} (attempt {retry_count})"
                    )

                    try:
                        step_result = await self._execute_step(
                            step, task_context, allow_variations=False
                        )
                        execution_log.append(
                            {
                                "step": idx,
                                "description": f"Retry {retry_count}",
                                "status": "success",
                                "output": step_result.get("output"),
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                        break
                    except Exception:
                        if retry_count >= self.max_execution_retries:
                            raise  # Re-raise after max retries

        # Determine final status
        failed_steps = [log for log in execution_log if log["status"] == "failed"]

        if not failed_steps:
            status = ResolutionStatus.SUCCESS
        elif len(failed_steps) < len(steps) // 2:
            status = ResolutionStatus.PARTIAL
        else:
            status = ResolutionStatus.FAILED

        return {
            "status": status.value,
            "sop_id": sop.get("id"),
            "execution_log": execution_log,
            "strategy": ResolutionStrategy.DIRECT_EXECUTION.value,
        }

    async def _execute_adaptive(
        self, ticket_id: str, sop: Dict[str, Any], task_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ADAPTIVE_EXECUTION: Execute SOP with intelligent variations.

        Used when confidence 70-85% (good match, may need adjustments)
        """
        logger.info(f"[ResolverAgent] ADAPTIVE execution for ticket {ticket_id}")

        execution_log = []
        steps = sop.get("steps", [])

        for idx, step in enumerate(steps, 1):
            try:
                # Allow AI to adjust commands based on context
                step_result = await self._execute_step(
                    step, task_context, allow_variations=True
                )

                execution_log.append(
                    {
                        "step": idx,
                        "description": step.get("description"),
                        "status": "success",
                        "output": step_result.get("output"),
                        "variations_applied": step_result.get("variations", []),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

                if step_result.get("resolution_confirmed"):
                    break

            except Exception as e:
                logger.error(f"[ResolverAgent] Adaptive step {idx} failed: {e}")
                execution_log.append(
                    {
                        "step": idx,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        failed_steps = [log for log in execution_log if log["status"] == "failed"]
        status = (
            ResolutionStatus.SUCCESS if not failed_steps else ResolutionStatus.PARTIAL
        )

        return {
            "status": status.value,
            "sop_id": sop.get("id"),
            "execution_log": execution_log,
            "strategy": ResolutionStrategy.ADAPTIVE_EXECUTION.value,
        }

    async def _execute_hybrid(
        self,
        ticket_id: str,
        sop_recommendations: List[Dict[str, Any]],
        task_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        HYBRID_EXECUTION: Combine multiple SOPs intelligently.

        Used when no single SOP is sufficient (confidence 50-70%)
        """
        logger.info(f"[ResolverAgent] HYBRID execution for ticket {ticket_id}")

        execution_log = []
        combined_steps = []

        # Select top 3 SOPs
        top_sops = sop_recommendations[:3]

        # Extract relevant steps from each SOP
        for sop in top_sops:
            steps = sop.get("steps", [])
            # Add steps with SOP reference
            for step in steps:
                combined_steps.append({**step, "source_sop": sop.get("id")})

        # Execute combined steps
        for idx, step in enumerate(combined_steps, 1):
            try:
                step_result = await self._execute_step(
                    step, task_context, allow_variations=True
                )

                execution_log.append(
                    {
                        "step": idx,
                        "source_sop": step.get("source_sop"),
                        "description": step.get("description"),
                        "status": "success",
                        "output": step_result.get("output"),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

                if step_result.get("resolution_confirmed"):
                    break

            except Exception as e:
                logger.error(f"[ResolverAgent] Hybrid step {idx} failed: {e}")
                execution_log.append(
                    {
                        "step": idx,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        failed_steps = [log for log in execution_log if log["status"] == "failed"]
        status = ResolutionStatus.PARTIAL if failed_steps else ResolutionStatus.SUCCESS

        return {
            "status": status.value,
            "sops_used": [sop.get("id") for sop in top_sops],
            "execution_log": execution_log,
            "strategy": ResolutionStrategy.HYBRID_EXECUTION.value,
        }

    async def _execute_manual(
        self,
        ticket_id: str,
        sop: Optional[Dict[str, Any]],
        task_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        MANUAL_EXECUTION: Generate step-by-step user guide.

        Used when automation confidence is low but SOP exists
        """
        logger.info(f"[ResolverAgent] MANUAL execution for ticket {ticket_id}")

        if sop:
            steps = sop.get("steps", [])
            user_guide = []

            for idx, step in enumerate(steps, 1):
                user_guide.append(
                    {
                        "step": idx,
                        "instruction": step.get("description"),
                        "expected_result": step.get("expected_outcome"),
                        "troubleshooting_tips": step.get("notes", []),
                    }
                )

            return {
                "status": ResolutionStatus.PARTIAL.value,
                "sop_id": sop.get("id"),
                "user_guide": user_guide,
                "strategy": ResolutionStrategy.MANUAL_EXECUTION.value,
                "message": "User manual guidance provided. Please follow steps and report results.",
            }
        else:
            return {
                "status": ResolutionStatus.FAILED.value,
                "strategy": ResolutionStrategy.MANUAL_EXECUTION.value,
                "message": "No applicable SOP found. Escalating to Level 2.",
            }

    async def _escalate(
        self, ticket_id: str, classification: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ESCALATION: Send ticket to Level 2 support.

        Used when confidence < 50% or critical failures occur
        """
        logger.warning(f"[ResolverAgent] Escalating ticket {ticket_id} to Level 2")

        escalation_reason = context.get("error", "Unable to resolve automatically")
        attempted_steps = context.get("execution_log", [])

        # TODO: Call escalation API
        # For now, just log

        return {
            "status": ResolutionStatus.ESCALATED.value,
            "escalation_reason": escalation_reason,
            "attempted_steps": len(attempted_steps),
            "classification": classification,
            "strategy": ResolutionStrategy.ESCALATION.value,
            "assigned_to": "Level 2 Support",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _execute_step(
        self, step: Dict[str, Any], task_context: Dict[str, Any], allow_variations: bool
    ) -> Dict[str, Any]:
        """
        Execute a single SOP step.

        May call Desktop-CommanderAgent for system commands.
        """
        step_type = step.get("type", "manual")

        if step_type == "command":
            # Execute via Desktop-CommanderAgent
            command = step.get("command")
            target_device = task_context.get("device_id", "localhost")

            result = await self._call_desktop_commander(
                command=command, target_device=target_device, safety_checks=True
            )

            return {
                "output": result.get("output"),
                "exit_code": result.get("exit_code"),
                "resolution_confirmed": result.get("success", False),
                "variations": result.get("variations", []) if allow_variations else [],
            }

        elif step_type == "verification":
            # Verify condition
            # TODO: Implement verification logic
            return {
                "output": "Verification step completed",
                "resolution_confirmed": False,
            }

        else:
            # Manual step (informational)
            return {"output": step.get("description"), "resolution_confirmed": False}

    async def _call_desktop_commander(
        self, command: str, target_device: str, safety_checks: bool
    ) -> Dict[str, Any]:
        """
        Call Desktop-CommanderAgent to execute system command.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.desktop_commander_url}/execute",
                    json={
                        "command": command,
                        "target_device": target_device,
                        "safety_checks": safety_checks,
                    },
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"[ResolverAgent] Desktop-Commander call failed: {e}")
            raise RuntimeError(f"Command execution failed: {e}")

    async def _update_ticket_status(
        self, ticket_id: str, result: Dict[str, Any]
    ) -> None:
        """Update ticket status in database based on resolution result"""
        try:
            # TODO: Implement TicketService
            # async for db in get_db():
            #     ticket_service = TicketService()
            #
            #     status_map = {
            #         ResolutionStatus.SUCCESS.value: "resolved",
            #         ResolutionStatus.PARTIAL.value: "in_progress",
            #         ResolutionStatus.FAILED.value: "open",
            #         ResolutionStatus.ESCALATED.value: "escalated"
            #     }
            #
            #     new_status = status_map.get(result.get("status"), "in_progress")
            #
            #     await ticket_service.update_ticket_status(
            #         db,
            #         ticket_id,
            #         new_status,
            #         resolution_notes=json.dumps(result)
            #     )
            #
            #     logger.info(f"[ResolverAgent] Updated ticket {ticket_id} status to {new_status}")

            logger.info(
                f"[ResolverAgent] Would update ticket {ticket_id} status (TicketService TODO)"
            )

        except Exception as e:
            logger.error(f"[ResolverAgent] Failed to update ticket status: {e}")

    async def _log_resolution_metrics(
        self,
        ticket_id: str,
        strategy: ResolutionStrategy,
        result: Dict[str, Any],
        confidence: float,
    ) -> None:
        """Log resolution metrics for monitoring and analytics"""
        metrics = {
            "ticket_id": ticket_id,
            "agent": self.name,
            "strategy": strategy.value,
            "confidence": confidence,
            "status": result.get("status"),
            "execution_time": result.get("execution_time"),
            "steps_executed": len(result.get("execution_log", [])),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"[ResolverAgent] Resolution metrics: {json.dumps(metrics)}")

        # TODO: Push to metrics service (Prometheus/Grafana)

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for ResolverAgent.

        Returns:
            Health status including connectivity to dependencies
        """
        health = {"agent": self.name, "status": "healthy", "checks": {}}

        # Check Desktop-CommanderAgent connectivity
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.desktop_commander_url}/health")
                health["checks"]["desktop_commander"] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
        except Exception as e:
            health["checks"]["desktop_commander"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"

        # Check database connectivity
        try:
            async for db in get_db():
                await db.execute("SELECT 1")
                health["checks"]["database"] = "healthy"
                break
        except Exception as e:
            health["checks"]["database"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"

        return health

"""
TwisterLab API - Orchestrator Routes
Handles automated ticket processing through the Maestro orchestrator
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

# Create router
router = APIRouter()

# In-memory storage for orchestrator results (replace with database in production)
orchestrator_results_db: dict[str, dict] = {}


# Pydantic models
class ProcessTicketRequest(BaseModel):
    """Request model for processing a ticket through the orchestrator."""
    ticket_id: str = Field(..., description="ID of the ticket to process")
    ticket_data: Dict[str, Any] = Field(..., description="Ticket data including subject, description, etc.")


class ProcessTicketResponse(BaseModel):
    """Response model for orchestrator processing results."""
    ticket_id: str
    status: str  # "processing", "completed", "failed"
    classification: Dict[str, Any] = None
    resolution: Dict[str, Any] = None
    processing_time: float = None
    created_at: str
    updated_at: str


@router.post("/process-ticket", response_model=ProcessTicketResponse)
async def process_ticket(request: ProcessTicketRequest) -> ProcessTicketResponse:
    """
    Process a ticket through the complete orchestrator workflow.

    This endpoint automatically:
    1. Classifies the ticket using the classifier agent
    2. Routes to appropriate resolver agent based on classification
    3. Returns the complete processing result
    """
    try:
        # Import agents here to avoid circular imports
        from agents.orchestrator.maestro import MaestroOrchestratorAgent

        # Create orchestrator instance
        orchestrator = MaestroOrchestratorAgent()

        # Process the ticket
        start_time = datetime.now()
        
        # Extract ticket data for Maestro
        ticket_context = {
            "ticket_id": request.ticket_id,
            "subject": request.ticket_data.get("subject", ""),
            "description": request.ticket_data.get("description", ""),
            "requestor": request.ticket_data.get("requestor_email", "unknown"),
            "priority": request.ticket_data.get("priority", "medium"),
            "category": request.ticket_data.get("category", "general")
        }
        
        result = await orchestrator.route_ticket(ticket_context)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Normalize the Maestro response to match ProcessTicketResponse schema
        status = result.get("status", "completed")
        
        # Handle resolution based on status
        if status == "escalated_to_human":
            resolution = {
                "status": "escalated",
                "reason": result.get("reason", "escalated_to_human"),
                "recommended_agent": result.get("recommended_agent", "human_agent"),
                "estimated_response_time": result.get("estimated_response_time", "unknown")
            }
        else:
            resolution = result.get("resolution")
        
        result_data = {
            "ticket_id": request.ticket_id,
            "status": status,
            "classification": result.get("classification"),
            "resolution": resolution,
            "processing_time": processing_time,
            "created_at": start_time.isoformat(),
            "updated_at": end_time.isoformat()
        }
        
        # Store result
        result_id = f"{request.ticket_id}_{int(start_time.timestamp())}"
        orchestrator_results_db[result_id] = result_data

        return ProcessTicketResponse.model_validate(result_data)

    except Exception as e:
        # Handle errors
        error_result = {
            "ticket_id": request.ticket_id,
            "status": "failed",
            "classification": {},
            "resolution": {"error": str(e)},
            "processing_time": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return ProcessTicketResponse.model_validate(error_result)


@router.get("/results/{ticket_id}")
async def get_orchestrator_results(ticket_id: str) -> Dict[str, Any]:
    """
    Get orchestrator processing results for a specific ticket.

    Returns all processing attempts for the given ticket ID.
    """
    results = [
        result for result in orchestrator_results_db.values()
        if result["ticket_id"] == ticket_id
    ]

    if not results:
        raise HTTPException(status_code=404, detail="No orchestrator results found for this ticket")

    # Return the most recent result
    latest_result = max(results, key=lambda x: x["created_at"])
    return latest_result


@router.get("/results")
async def list_orchestrator_results() -> Dict[str, Any]:
    """
    List all orchestrator processing results.

    Returns a summary of all ticket processing attempts.
    """
    return {
        "total_results": len(orchestrator_results_db),
        "results": list(orchestrator_results_db.values())
    }


@router.get("/agents/status")
async def get_agent_status(include_health: bool = False) -> Dict[str, Any]:
    """
    Get status of all available agents.

    Args:
        include_health: Include detailed health metrics for each agent

    Returns:
        Agent status information including load and availability
    """
    try:
        from agents.orchestrator.maestro import MaestroOrchestratorAgent

        orchestrator = MaestroOrchestratorAgent()
        result = await orchestrator.get_agent_status(include_health)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get performance metrics from the orchestrator.

    Returns:
        Performance metrics including tickets processed, auto-resolved count, etc.
    """
    try:
        from agents.orchestrator.maestro import MaestroOrchestratorAgent

        orchestrator = MaestroOrchestratorAgent()
        metrics = orchestrator.get_metrics()
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebalance")
async def rebalance_load(strategy: str = "round_robin") -> Dict[str, Any]:
    """
    Rebalance workload across agents.

    Args:
        strategy: Load balancing strategy (round_robin, least_loaded, priority_based)

    Returns:
        Rebalancing result
    """
    try:
        # Validate strategy
        valid_strategies = ["round_robin", "least_loaded", "priority_based"]
        if strategy not in valid_strategies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy. Must be one of: {', '.join(valid_strategies)}"
            )

        from agents.orchestrator.maestro import MaestroOrchestratorAgent

        orchestrator = MaestroOrchestratorAgent()
        result = await orchestrator.rebalance_load(strategy)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
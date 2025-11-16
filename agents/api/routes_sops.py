"""
TwisterLab API - SOP Management Routes
Handles Standard Operating Procedures for ticket resolution
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.config import get_db
from ..database.services import SOPService
from .models_sops import SOPCreate, SOPResponse, SOPUpdate

# Create router
router = APIRouter()


@router.get("/hello")
def hello():
    """Test endpoint for SOPs router."""
    return {"hello": "sops"}


@router.post("/", response_model=SOPResponse)
async def create_sop(
    sop: SOPCreate, created_by: str = "system", db: AsyncSession = Depends(get_db)
) -> SOPResponse:
    """
    Create a new Standard Operating Procedure.

    This endpoint creates a new SOP for automated ticket resolution.
    """
    try:
        service = SOPService(db)
        sop_response = await service.create_sop(sop, created_by)
        return sop_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create SOP: {str(e)}")


@router.get("/", response_model=List[SOPResponse])
async def list_sops(
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[SOPResponse]:
    """
    List SOPs with optional filtering.

    Returns a list of SOPs matching the specified criteria.
    """
    try:
        service = SOPService(db)
        sops = await service.list_sops(
            category=category, is_active=is_active, limit=limit, offset=offset
        )
        return sops
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list SOPs: {str(e)}")


@router.get("/{sop_id}", response_model=SOPResponse)
async def get_sop(sop_id: str, db: AsyncSession = Depends(get_db)) -> SOPResponse:
    """
    Get a specific SOP by ID.

    Returns detailed information about a single SOP.
    """
    try:
        service = SOPService(db)
        sop = await service.get_sop(sop_id)
        if not sop:
            raise HTTPException(status_code=404, detail="SOP not found")
        return sop
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SOP: {str(e)}")


@router.put("/{sop_id}", response_model=SOPResponse)
async def update_sop(
    sop_id: str, sop: SOPUpdate, updated_by: str = "system", db: AsyncSession = Depends(get_db)
) -> SOPResponse:
    """
    Update an existing SOP.

    Modifies SOP properties and increments version.
    """
    try:
        service = SOPService(db)
        sop_response = await service.update_sop(sop_id, sop, updated_by)
        if not sop_response:
            raise HTTPException(status_code=404, detail="SOP not found")
        return sop_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update SOP: {str(e)}")


@router.delete("/{sop_id}")
async def delete_sop(sop_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete an SOP.

    Removes an SOP from the system.
    """
    try:
        service = SOPService(db)
        success = await service.delete_sop(sop_id)
        if not success:
            raise HTTPException(status_code=404, detail="SOP not found")
        return {"message": "SOP deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete SOP: {str(e)}")


@router.post("/{sop_id}/execute")
async def execute_sop(sop_id: str, ticket_id: str, db: AsyncSession = Depends(get_db)):
    """
    Execute an SOP for a specific ticket.

    This endpoint triggers SOP execution for automated ticket resolution.
    """
    try:
        service = SOPService(db)
        sop = await service.get_sop(sop_id)
        if not sop:
            raise HTTPException(status_code=404, detail="SOP not found")

        if not sop.is_active:
            raise HTTPException(status_code=400, detail="SOP is not active")

        # For now, return a mock response
        # In production, this would trigger actual SOP execution
        return {
            "sop_id": sop_id,
            "ticket_id": ticket_id,
            "status": "executed",
            "steps_completed": len(sop.steps),
            "result": "SOP executed successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute SOP: {str(e)}")

"""
TwisterLab API - SOP Pydantic Models
Data validation models for Standard Operating Procedures
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SOPCreate(BaseModel):
    """Request model for creating a new SOP."""

    title: str = Field(..., min_length=1, max_length=200, description="SOP title")
    description: str = Field(..., min_length=1, max_length=1000, description="SOP description")
    category: str = Field("general", description="SOP category")
    priority: str = Field("medium", max_length=20, description="SOP priority level")
    steps: List[str] = Field(..., min_length=1, description="List of execution steps")
    applicable_issues: List[str] = Field(..., description="Types of issues this SOP applies to")


class SOPUpdate(BaseModel):
    """Request model for updating an SOP."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    category: Optional[str] = Field(None)
    priority: Optional[str] = Field(None, max_length=20)
    steps: Optional[List[str]] = Field(None, min_length=1)
    applicable_issues: Optional[List[str]] = Field(None)
    is_active: Optional[bool] = Field(None)


class SOPResponse(BaseModel):
    """Response model for SOP data."""

    id: str
    title: str
    description: str
    category: str
    priority: str
    steps: List[str]
    applicable_issues: List[str]
    is_active: bool
    version: int
    created_by: str
    created_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string
    created_by: str
    version: int

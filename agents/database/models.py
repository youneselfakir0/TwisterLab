"""
TwisterLab Database Models
SQLAlchemy models for the application
"""

from datetime import datetime
from typing import List

from sqlalchemy import ARRAY, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .config import Base


class SOP(Base):
    """
    Standard Operating Procedure database model.

    Represents a SOP for automated ticket resolution in the helpdesk system.
    """

    __tablename__ = "sops"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)

    # Basic information
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general", index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")

    # SOP content
    steps: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    applicable_issues: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[])

    # Status and versioning
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="system")

    def __repr__(self) -> str:
        """String representation of the SOP."""
        return f"<SOP(id='{self.id}', title='{self.title}', category='{self.category}', active={self.is_active})>"

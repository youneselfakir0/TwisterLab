"""
Alembic-compatible database models
Separate from async models to avoid import issues during migrations
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ARRAY, JSON, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class SOP(Base):
    """
    Standard Operating Procedure model for database storage
    """
    __tablename__ = "sops"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    # Basic information
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in minutes

    # Content
    steps: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, default=list)
    tools_required: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, default=list)
    common_issues: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, default=list)
    solutions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, default=list)

    # Metadata
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, default=list)

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Usage tracking
    execution_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_rate: Mapped[float] = mapped_column(Integer, nullable=False, default=100)  # percentage
    average_execution_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in seconds

    # Additional data
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Indexes for performance
    __table_args__ = (
        Index('ix_sops_category_priority', 'category', 'priority'),
        Index('ix_sops_title', 'title'),
        Index('ix_sops_created_at', 'created_at'),
        Index('ix_sops_is_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<SOP(id={self.id}, title='{self.title}', category='{self.category}')>"
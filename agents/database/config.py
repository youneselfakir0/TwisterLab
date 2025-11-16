"""
TwisterLab Database Configuration
SQLAlchemy setup for PostgreSQL database with async support
"""

import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Load environment variables
load_dotenv()


def _read_env_file(varname: str) -> str | None:
    file_path = os.getenv(f"{varname}__FILE") or os.getenv(f"{varname}_FILE")
    if not file_path:
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


# Database configuration
DATABASE_URL = _read_env_file("DATABASE_URL") or os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://twisterlab@localhost:5432/twisterlab",
)

# SQLAlchemy engine configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections every 30 minutes
)

# Async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables() -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

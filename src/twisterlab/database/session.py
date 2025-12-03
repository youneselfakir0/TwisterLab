from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Default to a shared in-memory SQLite database (safe for tests) unless overridden
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
if DATABASE_URL.startswith("postgres"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# Ensure models are imported and tables created at module import time to support test clients
async def init_db():
    async with engine.begin() as conn:
        # Import model modules so they register with Base
        from twisterlab.database.models import agent as _agent_model  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)

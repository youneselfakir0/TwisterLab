from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.session import get_db

from twisterlab.storage.inmemory import InMemoryAgentRepo


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    async for db in get_db():
        yield db


# Simple default AgentRepo dependency used in test and dev environments.
_DEFAULT_INMEM_REPO = InMemoryAgentRepo()


async def get_agent_repo():
    """FastAPI dependency that returns a repository implementation for agents.

    The default is an in-memory repository suitable for tests and local dev. In a
    production environment this function may be extended to return a DB-backed
    repo.
    """
    yield _DEFAULT_INMEM_REPO

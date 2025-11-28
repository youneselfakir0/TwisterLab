from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.session import get_db


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    async for db in get_db():
        yield db

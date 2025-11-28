from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models.agent import Agent


async def create_agent(
    db: AsyncSession, name: str, description: str | None = None
) -> Agent:
    agent = Agent(name=name, description=description)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def get_agent(db: AsyncSession, agent_id: int) -> Agent | None:
    return await db.get(Agent, agent_id)


async def get_agents(db: AsyncSession) -> list[Agent]:
    result = await db.execute(select(Agent))
    return result.scalars().all()


async def update_agent(
    db: AsyncSession,
    agent_id: int,
    name: str | None = None,
    description: str | None = None,
) -> Agent | None:
    agent = await get_agent(db, agent_id)
    if not agent:
        return None
    if name is not None:
        agent.name = name
    if description is not None:
        agent.description = description
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def delete_agent(db: AsyncSession, agent_id: int) -> bool:
    agent = await get_agent(db, agent_id)
    if not agent:
        return False
    await db.delete(agent)
    await db.commit()
    return True

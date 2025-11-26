from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from twisterlab.api.dependencies import get_database
from twisterlab.api.schemas.index import AgentCreate, AgentResponse, AgentUpdate
from twisterlab.database.crud_agents import create_agent as db_create_agent
from twisterlab.database.crud_agents import delete_agent as db_delete_agent
from twisterlab.database.crud_agents import get_agent as db_get_agent
from twisterlab.database.crud_agents import get_agents as db_get_agents
from twisterlab.database.crud_agents import update_agent as db_update_agent
from twisterlab.database.models.agent import Agent as AgentModel

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent: AgentCreate, db: AsyncSession = Depends(get_database)
):
    # avoid creating a duplicate agent with the same name
    # simple fallback check using model import to avoid circular references
    result = await db.execute(select(AgentModel).filter(AgentModel.name == agent.name))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent already exists")
    agent_obj = await db_create_agent(
        db, name=agent.name, description=agent.description
    )
    return agent_obj


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_database)):
    agent_obj = await db_get_agent(db, agent_id)
    if not agent_obj:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_obj


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_database),
):
    agent_obj = await db_update_agent(
        db, agent_id, name=agent_update.name, description=agent_update.description
    )
    if not agent_obj:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_obj


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_database)):
    success = await db_delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return Response(status_code=204)


@router.get("/", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_database)):
    return await db_get_agents(db)

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from twisterlab.api.schemas.index import AgentCreate, AgentResponse, AgentUpdate
from twisterlab.database.crud_agents import create_agent as db_create_agent
from twisterlab.database.crud_agents import delete_agent as db_delete_agent
from twisterlab.database.crud_agents import get_agent as db_get_agent
from twisterlab.database.crud_agents import get_agents as db_get_agents
from twisterlab.database.crud_agents import update_agent as db_update_agent
from twisterlab.database.session import get_db

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    # avoid creating a duplicate agent with the same name
    # simple fallback check using model import to avoid circular references
    from twisterlab.database.models.agent import Agent as AgentModel

    existing = db.query(AgentModel).filter(AgentModel.name == agent.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent already exists")
    agent_obj = db_create_agent(db, name=agent.name, description=agent.description)
    return agent_obj


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent_obj = db_get_agent(db, agent_id)
    if not agent_obj:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_obj


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int, agent_update: AgentUpdate, db: Session = Depends(get_db)
):
    agent_obj = db_update_agent(
        db, agent_id, name=agent_update.name, description=agent_update.description
    )
    if not agent_obj:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_obj


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    success = db_delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return Response(status_code=204)


@router.get("/", response_model=list[AgentResponse])
async def list_agents(db: Session = Depends(get_db)):
    return db_get_agents(db)

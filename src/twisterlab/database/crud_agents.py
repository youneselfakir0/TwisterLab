from __future__ import annotations

from sqlalchemy.orm import Session

from .models.agent import Agent


def create_agent(db: Session, name: str, description: str | None = None) -> Agent:
    agent = Agent(name=name, description=description)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def get_agent(db: Session, agent_id: int) -> Agent | None:
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agents(db: Session) -> list[Agent]:
    return db.query(Agent).all()


def update_agent(
    db: Session, agent_id: int, name: str | None = None, description: str | None = None
) -> Agent | None:
    agent = get_agent(db, agent_id)
    if not agent:
        return None
    if name is not None:
        agent.name = name
    if description is not None:
        agent.description = description
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: int) -> bool:
    agent = get_agent(db, agent_id)
    if not agent:
        return False
    db.delete(agent)
    db.commit()
    return True

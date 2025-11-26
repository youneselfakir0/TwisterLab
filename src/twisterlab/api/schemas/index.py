from typing import List, Optional

from pydantic import BaseModel


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: int


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class AgentResponse(AgentBase):
    id: int

    class Config:
        orm_mode = True


class HealthCheckResponse(BaseModel):
    status: str
    message: Optional[str] = None


class TwisterLangMessage(BaseModel):
    twisterlang_version: str
    correlation_id: str
    payload: dict


class ErrorResponse(BaseModel):
    detail: str


class MetricsResponse(BaseModel):
    metrics: List[dict]

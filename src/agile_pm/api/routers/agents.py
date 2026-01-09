"""Agent management endpoints."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

router = APIRouter()

class AgentStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"
    STOPPED = "stopped"

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=50)
    capabilities: list = Field(default_factory=list)
    config: dict = Field(default_factory=dict)

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    capabilities: Optional[list] = None
    config: Optional[dict] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    status: AgentStatus
    capabilities: list
    config: dict
    created_at: datetime
    updated_at: datetime

class AgentExecuteRequest(BaseModel):
    task_id: str
    parameters: dict = Field(default_factory=dict)

@router.get("", response_model=list)
async def list_agents(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    """List all agents."""
    return []

@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(agent: AgentCreate):
    """Create a new agent."""
    return AgentResponse(
        id="agent-001", name=agent.name, role=agent.role, status=AgentStatus.IDLE,
        capabilities=agent.capabilities, config=agent.config,
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent by ID."""
    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent: AgentUpdate):
    """Update agent."""
    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    """Delete agent."""
    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@router.post("/{agent_id}/execute")
async def execute_agent(agent_id: str, request: AgentExecuteRequest):
    """Execute task with agent."""
    return {"agent_id": agent_id, "task_id": request.task_id, "status": "queued"}

"""Sprint management endpoints."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum

router = APIRouter()

class SprintStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SprintCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    goal: str = Field(..., min_length=1, max_length=500)
    start_date: date
    end_date: date
    capacity: int = Field(40, ge=0)

class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[SprintStatus] = None
    capacity: Optional[int] = None

class SprintResponse(BaseModel):
    id: str
    name: str
    goal: str
    status: SprintStatus
    start_date: date
    end_date: date
    capacity: int
    velocity: int
    created_at: datetime
    updated_at: datetime

@router.get("", response_model=list)
async def list_sprints(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    """List sprints."""
    return []

@router.post("", response_model=SprintResponse, status_code=201)
async def create_sprint(sprint: SprintCreate):
    """Create sprint."""
    return SprintResponse(
        id="sprint-001", name=sprint.name, goal=sprint.goal,
        status=SprintStatus.PLANNING, start_date=sprint.start_date,
        end_date=sprint.end_date, capacity=sprint.capacity, velocity=0,
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )

@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(sprint_id: str):
    """Get sprint by ID."""
    raise HTTPException(status_code=404, detail=f"Sprint {sprint_id} not found")

@router.put("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(sprint_id: str, sprint: SprintUpdate):
    """Update sprint."""
    raise HTTPException(status_code=404, detail=f"Sprint {sprint_id} not found")

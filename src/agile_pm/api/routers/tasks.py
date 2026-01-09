"""Task management endpoints."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

router = APIRouter()

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.P1
    sprint_id: Optional[str] = None
    assignee_id: Optional[str] = None
    tags: list = Field(default_factory=list)

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[str] = None
    tags: Optional[list] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    sprint_id: Optional[str]
    assignee_id: Optional[str]
    tags: list
    created_at: datetime
    updated_at: datetime

@router.get("", response_model=list)
async def list_tasks(
    skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatus] = None, priority: Optional[TaskPriority] = None
):
    """List tasks."""
    return []

@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate):
    """Create task."""
    return TaskResponse(
        id="task-001", title=task.title, description=task.description,
        priority=task.priority, status=TaskStatus.TODO, sprint_id=task.sprint_id,
        assignee_id=task.assignee_id, tags=task.tags,
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task by ID."""
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate):
    """Update task."""
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@router.post("/{task_id}/start")
async def start_task(task_id: str):
    """Start task."""
    return {"task_id": task_id, "status": "started"}

@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel task."""
    return {"task_id": task_id, "status": "cancelled"}

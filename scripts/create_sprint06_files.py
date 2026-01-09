#!/usr/bin/env python3
"""Create Sprint 06 files for agile-pm."""
import os

BASE = "/Volumes/Data/CodingWorkPlace/GitHub/agile-pm/src/agile_pm"

def write(path, content):
    with open(f"{BASE}/{path}", "w") as f:
        f.write(content)
    print(f"Created: {path}")

# S06-001: API __init__.py
write("api/__init__.py", '''"""Agile-PM REST API."""
from agile_pm.api.app import create_app, app
__all__ = ["create_app", "app"]
''')

# S06-001: API app.py  
write("api/app.py", '''"""FastAPI Application for Agile-PM."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agile_pm.api.routers import agents, tasks, sprints, memory, system
from agile_pm.api.middleware.logging import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Starting Agile-PM API...")
    yield
    print("Shutting down Agile-PM API...")

def create_app(title: str = "Agile-PM API", version: str = "1.0.0", debug: bool = False) -> FastAPI:
    application = FastAPI(
        title=title, version=version,
        description="AI-Powered Agile Project Management API",
        docs_url="/api/docs", redoc_url="/api/redoc",
        openapi_url="/api/openapi.json", lifespan=lifespan, debug=debug,
    )
    application.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"]
    )
    application.add_middleware(LoggingMiddleware)
    application.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
    application.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
    application.include_router(sprints.router, prefix="/api/v1/sprints", tags=["Sprints"])
    application.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
    application.include_router(system.router, prefix="/api/v1/system", tags=["System"])
    
    @application.get("/", tags=["Root"])
    async def root():
        return {"name": "Agile-PM API", "version": version, "docs": "/api/docs"}
    
    @application.get("/health", tags=["Health"])
    async def health():
        return {"status": "healthy"}
    
    return application

app = create_app()
''')

# S06-001: dependencies.py
write("api/dependencies.py", '''"""Dependency Injection for API."""
from functools import lru_cache

class Settings:
    def __init__(self):
        self.debug = False
        self.database_url = "postgresql://localhost/agile_pm"
        self.redis_url = "redis://localhost:6379"
        self.jwt_secret = "change-me-in-production"
        self.jwt_algorithm = "HS256"
        self.jwt_expiry_minutes = 30

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class CurrentUser:
    def __init__(self, user_id: str, username: str, roles: list):
        self.user_id = user_id
        self.username = username
        self.roles = roles
    
    def has_role(self, role: str) -> bool:
        return role in self.roles or "admin" in self.roles
''')

# S06-001: routers/__init__.py
write("api/routers/__init__.py", '''"""API Routers."""
from agile_pm.api.routers import agents, tasks, sprints, memory, system
__all__ = ["agents", "tasks", "sprints", "memory", "system"]
''')

# S06-001: routers/agents.py
write("api/routers/agents.py", '''"""Agent management endpoints."""
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
''')

# S06-001: routers/tasks.py
write("api/routers/tasks.py", '''"""Task management endpoints."""
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
''')

# S06-001: routers/sprints.py
write("api/routers/sprints.py", '''"""Sprint management endpoints."""
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
''')

# S06-001: routers/memory.py
write("api/routers/memory.py", '''"""Memory management endpoints."""
from typing import Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

class MemoryCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=200)
    value: Any
    namespace: str = Field("default", min_length=1, max_length=50)
    ttl: Optional[int] = Field(None, ge=0)

class MemoryResponse(BaseModel):
    key: str
    value: Any
    namespace: str
    created_at: datetime
    expires_at: Optional[datetime]

@router.get("")
async def list_memories(namespace: str = Query("default"), pattern: str = Query("*")):
    """List memory keys."""
    return {"namespace": namespace, "pattern": pattern, "keys": []}

@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(memory: MemoryCreate):
    """Store value in memory."""
    return MemoryResponse(
        key=memory.key, value=memory.value, namespace=memory.namespace,
        created_at=datetime.utcnow(), expires_at=None
    )

@router.get("/{key}", response_model=MemoryResponse)
async def get_memory(key: str, namespace: str = Query("default")):
    """Get memory value."""
    raise HTTPException(status_code=404, detail=f"Key {key} not found")

@router.delete("/{key}", status_code=204)
async def delete_memory(key: str, namespace: str = Query("default")):
    """Delete memory key."""
    raise HTTPException(status_code=404, detail=f"Key {key} not found")
''')

# S06-001: routers/system.py
write("api/routers/system.py", '''"""System endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import platform

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class MetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_agents: int
    pending_tasks: int
    uptime_seconds: float

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check."""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow(), version="1.0.0")

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """System metrics."""
    return MetricsResponse(
        cpu_percent=0.0, memory_percent=0.0, disk_percent=0.0,
        active_agents=0, pending_tasks=0, uptime_seconds=0.0
    )

@router.get("/info")
async def get_info():
    """System info."""
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture()[0],
    }
''')

# S06-001: middleware/__init__.py
write("api/middleware/__init__.py", '''"""API Middleware."""
from agile_pm.api.middleware.logging import LoggingMiddleware
__all__ = ["LoggingMiddleware"]
''')

# S06-001: middleware/logging.py
write("api/middleware/logging.py", '''"""Logging middleware."""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("agile_pm.api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        response.headers["X-Process-Time"] = str(process_time)
        return response
''')

# S06-001: schemas/__init__.py
write("api/schemas/__init__.py", '''"""API Schemas."""
from agile_pm.api.schemas.common import PaginatedResponse, ErrorResponse
__all__ = ["PaginatedResponse", "ErrorResponse"]
''')

# S06-001: schemas/common.py
write("api/schemas/common.py", '''"""Common API schemas."""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list
    total: int
    skip: int
    limit: int
    has_more: bool

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
''')

print("\n=== S06-001: REST API Endpoints - COMPLETE ===")

"""Dashboard event types for real-time updates."""

from datetime import datetime
from typing import Any, Optional
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of dashboard events."""
    
    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_THINKING = "agent.thinking"
    
    # Task events
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    
    # Crew events
    CREW_STARTED = "crew.started"
    CREW_COMPLETED = "crew.completed"
    
    # Memory events
    MEMORY_SAVED = "memory.saved"
    MEMORY_RETRIEVED = "memory.retrieved"
    
    # System events
    METRICS_UPDATE = "metrics.update"
    ERROR = "error"
    CONNECTION = "connection"


class DashboardEvent(BaseModel):
    """Base event for dashboard updates."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(description="Source component/agent")
    data: dict[str, Any] = Field(default_factory=dict)


class AgentStatusEvent(DashboardEvent):
    """Event for agent status updates."""

    agent_id: str
    agent_role: str
    status: str = Field(description="started, thinking, completed, failed")
    message: Optional[str] = None
    task_id: Optional[str] = None
    
    def __init__(self, **data):
        if "type" not in data:
            data["type"] = EventType.AGENT_STARTED
        super().__init__(**data)


class TaskProgressEvent(DashboardEvent):
    """Event for task progress updates."""

    task_id: str
    title: str
    progress: float = Field(ge=0.0, le=1.0, description="Progress 0-1")
    status: str = Field(description="pending, in_progress, completed, failed")
    assigned_agent: Optional[str] = None
    output: Optional[str] = None
    
    def __init__(self, **data):
        if "type" not in data:
            data["type"] = EventType.TASK_PROGRESS
        super().__init__(**data)


class MetricsEvent(DashboardEvent):
    """Event for metrics updates."""

    metrics: dict[str, Any]
    period: str = Field(default="1m", description="Aggregation period")
    
    def __init__(self, **data):
        if "type" not in data:
            data["type"] = EventType.METRICS_UPDATE
        super().__init__(**data)


class CrewEvent(DashboardEvent):
    """Event for crew lifecycle."""

    crew_id: str
    crew_name: str
    agents: list[str]
    status: str = Field(description="started, in_progress, completed, failed")
    tasks_total: int = 0
    tasks_completed: int = 0
    
    def __init__(self, **data):
        if "type" not in data:
            data["type"] = EventType.CREW_STARTED
        super().__init__(**data)


class MemoryEvent(DashboardEvent):
    """Event for memory operations."""

    memory_type: str = Field(description="buffer, summary, entity, vector")
    session_id: str
    operation: str = Field(description="save, retrieve, clear")
    entries_count: int = 0
    
    def __init__(self, **data):
        if "type" not in data:
            data["type"] = EventType.MEMORY_SAVED
        super().__init__(**data)


class ConnectionEvent(DashboardEvent):
    """Event for client connections."""

    client_id: str
    action: str = Field(description="connected, disconnected")
    ip_address: Optional[str] = None
    
    def __init__(self, **data):
        if "type" not in data:
            data["type"] = EventType.CONNECTION
        super().__init__(**data)


class ErrorEvent(DashboardEvent):
    """Event for errors."""

    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        if "type" not in data:
            data["type"] = EventType.ERROR
        super().__init__(**data)

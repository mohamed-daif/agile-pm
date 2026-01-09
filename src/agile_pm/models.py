"""Pydantic models for Agile-PM Agents."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentProvider(str, Enum):
    """Supported AI agent providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    LOCAL = "local"


class AgentStatus(str, Enum):
    """Agent operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class TaskStatus(str, Enum):
    """Task execution status."""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low


class RoleType(str, Enum):
    """Types of roles in Agile-PM."""
    HUMAN = "human"
    AI_AGENT = "ai-agent"
    SPECIALIST = "specialist"


class RoleDefinition(BaseModel):
    """Definition of a role in Agile-PM."""
    id: str = Field(..., description="Unique role identifier")
    name: str = Field(..., min_length=1, max_length=100)
    type: RoleType
    charter_section: str = Field(..., pattern=r"^§\d+(\.\d+)?$")
    capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class AgentConfig(BaseModel):
    """Configuration for an AI agent."""
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., min_length=1, max_length=100)
    role_id: str = Field(..., description="Associated role ID")
    provider: AgentProvider
    status: AgentStatus = AgentStatus.PENDING
    capabilities: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class TaskAssignment(BaseModel):
    """Assignment of a task to an agent."""
    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: TaskPriority = TaskPriority.P2
    assignee_id: Optional[str] = None
    sprint_id: Optional[str] = None
    story_points: Optional[int] = Field(None, ge=0, le=21)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class GovernanceCheckType(str, Enum):
    """Types of governance checks."""
    APPROVAL_REQUIRED = "approval-required"
    QUALITY_GATE = "quality-gate"
    SECURITY_REVIEW = "security-review"
    COMPLIANCE_CHECK = "compliance-check"


class GovernanceCheckStatus(str, Enum):
    """Status of governance checks."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BYPASSED = "bypassed"


class GovernanceCheck(BaseModel):
    """A governance check for tasks or artifacts."""
    id: str
    type: GovernanceCheckType
    target_id: str
    target_type: str  # task, pr, deployment, adr
    status: GovernanceCheckStatus = GovernanceCheckStatus.PENDING
    checked_by: Optional[str] = None
    checked_at: Optional[datetime] = None
    bypass_reason: Optional[str] = None

    class Config:
        use_enum_values = True

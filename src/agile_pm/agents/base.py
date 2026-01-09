"""
Base Agent Classes

Provides the foundational agent infrastructure for all 33 governance roles.
Implements role switching, capability mapping, and constraint enforcement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Agent classification types from governance."""
    STRATEGIC = "strategic"
    EXECUTOR = "executor"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"


class CapabilityLevel(str, Enum):
    """Capability permission levels."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    APPROVE = "approve"


class ConstraintType(str, Enum):
    """Constraint enforcement types."""
    MUST = "must"
    MUST_NOT = "must-not"
    SHOULD = "should"
    SHOULD_NOT = "should-not"


class AgentCapability(BaseModel):
    """Represents a single agent capability."""
    id: str
    name: str
    description: str
    level: CapabilityLevel
    scope: list[str] = Field(default_factory=list)
    
    def can_execute(self, action: str) -> bool:
        """Check if this capability allows the action."""
        if self.level == CapabilityLevel.APPROVE:
            return True
        if self.level == CapabilityLevel.EXECUTE:
            return action in ["read", "write", "execute"]
        if self.level == CapabilityLevel.WRITE:
            return action in ["read", "write"]
        return action == "read"


class AgentConstraint(BaseModel):
    """Represents a constraint on agent behavior."""
    id: str
    type: ConstraintType
    description: str
    enforceable: bool = True
    
    def is_violated(self, action: str, context: dict[str, Any]) -> bool:
        """Check if this constraint would be violated."""
        # Constraint checking logic - extensible per constraint type
        return False


class AgentTrigger(BaseModel):
    """Defines automatic role switching triggers."""
    id: str
    condition: str
    target_role: str
    priority: int = 0
    charter_ref: Optional[str] = None
    
    def matches(self, context: dict[str, Any]) -> bool:
        """Check if trigger condition is met."""
        # Simple keyword matching for now
        if "file_type" in context:
            file_type = context["file_type"]
            if "backend" in self.condition and file_type in [".ts", ".js", ".py"]:
                return "backend" in self.target_role.lower()
            if "frontend" in self.condition and file_type in [".tsx", ".jsx"]:
                return "frontend" in self.target_role.lower()
            if "test" in self.condition and "test" in context.get("file_path", ""):
                return "qa" in self.target_role.lower()
        return False


class AgentContext(BaseModel):
    """Context passed to agent during execution."""
    task_id: str
    task_type: str
    workspace_path: Path = Field(default_factory=lambda: Path.cwd())
    obsidian_task: Optional[str] = None
    tracking_issue: Optional[str] = None
    files: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class AgentResult(BaseModel):
    """Result from agent execution."""
    success: bool
    agent_id: str
    task_id: str
    output: Any = None
    error: Optional[str] = None
    artifacts: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


@dataclass
class RoleDefinition:
    """Full role definition from governance files."""
    id: str
    name: str
    type: AgentType
    charter_section: str
    description: str
    backstory: str
    capabilities: list[AgentCapability] = field(default_factory=list)
    constraints: list[AgentConstraint] = field(default_factory=list)
    triggers: list[AgentTrigger] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Base class for all Agile-PM agents.
    
    Implements:
    - Role definition parsing from governance files
    - Capability checking
    - Constraint enforcement
    - Role switching triggers
    - Execution lifecycle
    """
    
    # Class-level role definition (override in subclasses)
    ROLE_ID: str = "base-agent"
    ROLE_NAME: str = "Base Agent"
    ROLE_TYPE: AgentType = AgentType.EXECUTOR
    CHARTER_SECTION: str = "§1"
    
    def __init__(
        self,
        role_definition: Optional[RoleDefinition] = None,
        llm: Optional[Any] = None,
        verbose: bool = False,
    ):
        """
        Initialize the agent.
        
        Args:
            role_definition: Full role definition (auto-generated if None)
            llm: Language model to use for AI operations
            verbose: Enable verbose logging
        """
        self._role = role_definition or self._build_default_role()
        self._llm = llm
        self._verbose = verbose
        self._execution_history: list[AgentResult] = []
        
    def _build_default_role(self) -> RoleDefinition:
        """Build default role definition from class attributes."""
        return RoleDefinition(
            id=self.ROLE_ID,
            name=self.ROLE_NAME,
            type=self.ROLE_TYPE,
            charter_section=self.CHARTER_SECTION,
            description=self._get_description(),
            backstory=self._get_backstory(),
            capabilities=self._get_capabilities(),
            constraints=self._get_constraints(),
            triggers=self._get_triggers(),
            tools=self._get_tools(),
        )
    
    @property
    def role_id(self) -> str:
        """Get the agent's role ID."""
        return self._role.id
    
    @property
    def role_name(self) -> str:
        """Get the agent's role name."""
        return self._role.name
    
    @property
    def role_type(self) -> AgentType:
        """Get the agent's role type."""
        return self._role.type
    
    @property
    def capabilities(self) -> list[AgentCapability]:
        """Get the agent's capabilities."""
        return self._role.capabilities
    
    @property
    def constraints(self) -> list[AgentConstraint]:
        """Get the agent's constraints."""
        return self._role.constraints
    
    def can_perform(self, action: str, scope: Optional[str] = None) -> bool:
        """
        Check if the agent can perform an action.
        
        Args:
            action: The action to check (read, write, execute, approve)
            scope: Optional scope to check against
            
        Returns:
            True if the agent has capability for this action
        """
        for cap in self._role.capabilities:
            if cap.can_execute(action):
                if scope is None or scope in cap.scope or not cap.scope:
                    return True
        return False
    
    def check_constraints(self, action: str, context: dict[str, Any]) -> list[str]:
        """
        Check all constraints for violations.
        
        Args:
            action: The action being performed
            context: Execution context
            
        Returns:
            List of violated constraint descriptions
        """
        violations = []
        for constraint in self._role.constraints:
            if constraint.is_violated(action, context):
                violations.append(constraint.description)
        return violations
    
    def should_switch_role(self, context: dict[str, Any]) -> Optional[str]:
        """
        Check if role should be switched based on triggers.
        
        Args:
            context: Current execution context
            
        Returns:
            Target role ID if switch triggered, None otherwise
        """
        matching_triggers = [
            t for t in self._role.triggers
            if t.matches(context)
        ]
        if matching_triggers:
            # Return highest priority trigger's target
            matching_triggers.sort(key=lambda t: t.priority, reverse=True)
            return matching_triggers[0].target_role
        return None
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's primary task.
        
        Args:
            context: Execution context with task details
            
        Returns:
            AgentResult with execution outcome
        """
        try:
            # Pre-execution checks
            if not self._pre_execute_checks(context):
                return AgentResult(
                    success=False,
                    agent_id=self.role_id,
                    task_id=context.task_id,
                    error="Pre-execution checks failed",
                )
            
            # Run the implementation
            result = await self._execute_impl(context)
            
            # Post-execution
            self._execution_history.append(result)
            
            return result
            
        except Exception as e:
            return AgentResult(
                success=False,
                agent_id=self.role_id,
                task_id=context.task_id,
                error=str(e),
            )
    
    def _pre_execute_checks(self, context: AgentContext) -> bool:
        """Run pre-execution validation checks."""
        # Check for constraint violations
        violations = self.check_constraints("execute", context.metadata)
        if violations:
            if self._verbose:
                print(f"Constraint violations: {violations}")
            return False
        return True
    
    @abstractmethod
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        """
        Implementation of the agent's execution logic.
        Override in subclasses.
        
        Args:
            context: Execution context
            
        Returns:
            AgentResult with execution outcome
        """
        pass
    
    @abstractmethod
    def _get_description(self) -> str:
        """Get the agent's description. Override in subclasses."""
        pass
    
    @abstractmethod
    def _get_backstory(self) -> str:
        """Get the agent's backstory for CrewAI. Override in subclasses."""
        pass
    
    def _get_capabilities(self) -> list[AgentCapability]:
        """Get the agent's capabilities. Override in subclasses."""
        return []
    
    def _get_constraints(self) -> list[AgentConstraint]:
        """Get the agent's constraints. Override in subclasses."""
        return []
    
    def _get_triggers(self) -> list[AgentTrigger]:
        """Get the agent's role switch triggers. Override in subclasses."""
        return []
    
    def _get_tools(self) -> list[str]:
        """Get the agent's available tools. Override in subclasses."""
        return []
    
    def to_dict(self) -> dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "id": self.role_id,
            "name": self.role_name,
            "type": self.role_type.value,
            "charter_section": self._role.charter_section,
            "description": self._role.description,
            "capabilities": [c.model_dump() for c in self.capabilities],
            "constraints": [c.model_dump() for c in self.constraints],
            "tools": self._role.tools,
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.role_id}, type={self.role_type.value})>"

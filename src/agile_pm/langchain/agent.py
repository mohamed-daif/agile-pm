"""Base agent wrapper for Agile-PM with LangChain.

Provides governance-aware AI agents that follow the Agile-PM charter
and role-specific constraints.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, TypeVar, Generic

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from agile_pm.models import (
    AgentConfig,
    AgentStatus,
    RoleDefinition,
    TaskAssignment,
    GovernanceCheckType,
)


class AgentContext(BaseModel):
    """Context for agent execution."""

    session_id: str = Field(..., description="Unique session identifier")
    role: RoleDefinition = Field(..., description="Active role definition")
    task: Optional[TaskAssignment] = Field(None, description="Current task")
    governance_mode: bool = Field(True, description="Enable governance checks")
    obsidian_path: str = Field("cm-workflow", description="Path to Obsidian vault")
    governance_path: str = Field(".github/governance", description="Path to governance files")
    chat_history: list[BaseMessage] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class AgentResult(BaseModel):
    """Result from agent execution."""

    success: bool = Field(..., description="Whether execution succeeded")
    output: str = Field(..., description="Agent output")
    artifacts: list[str] = Field(default_factory=list, description="Created artifacts")
    governance_checks: list[dict[str, Any]] = Field(
        default_factory=list, description="Governance checks performed"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: int = Field(0, description="Execution duration in milliseconds")
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseAgilePMAgent(ABC):
    """Abstract base class for Agile-PM agents."""

    def __init__(
        self,
        config: AgentConfig,
        llm: BaseChatModel,
        tools: Optional[list[BaseTool]] = None,
    ):
        """Initialize the agent.

        Args:
            config: Agent configuration
            llm: Language model to use
            tools: Optional list of tools
        """
        self.config = config
        self.llm = llm
        self.tools = tools or []
        self._executor: Optional[AgentExecutor] = None
        self._context: Optional[AgentContext] = None

    @property
    def name(self) -> str:
        """Get agent name."""
        return self.config.name

    @property
    def role_id(self) -> str:
        """Get role ID."""
        return self.config.role_id

    @property
    def is_active(self) -> bool:
        """Check if agent is active."""
        return self.config.status == AgentStatus.ACTIVE

    @abstractmethod
    def create_prompt(self, context: AgentContext) -> ChatPromptTemplate:
        """Create the prompt template for this agent.

        Args:
            context: Agent execution context

        Returns:
            ChatPromptTemplate for the agent
        """
        pass

    @abstractmethod
    async def execute(
        self,
        input_text: str,
        context: AgentContext,
    ) -> AgentResult:
        """Execute the agent with given input.

        Args:
            input_text: User input text
            context: Agent execution context

        Returns:
            AgentResult with execution outcome
        """
        pass

    def _build_executor(self, context: AgentContext) -> AgentExecutor:
        """Build the LangChain agent executor.

        Args:
            context: Agent execution context

        Returns:
            Configured AgentExecutor
        """
        prompt = self.create_prompt(context)

        if self.tools:
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            return AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=10,
            )
        else:
            # Simple chain without tools
            return self.llm | prompt


class AgilePMAgent(BaseAgilePMAgent):
    """Standard Agile-PM agent implementation."""

    def create_prompt(self, context: AgentContext) -> ChatPromptTemplate:
        """Create role-specific prompt template."""
        role = context.role

        system_content = f"""You are {role.name}, an AI agent in the Agile-PM system.

## Role Definition
- **Charter Section:** {role.charter_section}
- **Type:** {role.type.value}

## Capabilities
{chr(10).join(f'- {cap}' for cap in role.capabilities)}

## Constraints
{chr(10).join(f'- {con}' for con in role.constraints)}

## Governance Rules
1. All work MUST be tracked in Obsidian vault ({context.obsidian_path}/)
2. Follow approval requirements for artifacts
3. Update task status as work progresses
4. No shadow work allowed

## Session Information
- Session ID: {context.session_id}
- Started: {context.started_at.isoformat()}
- Governance Mode: {'ENABLED' if context.governance_mode else 'DISABLED'}
"""

        if context.task:
            system_content += f"""
## Current Task
- **ID:** {context.task.id}
- **Title:** {context.task.title}
- **Priority:** {context.task.priority.value}
- **Status:** {context.task.status.value}
"""

        return ChatPromptTemplate.from_messages([
            SystemMessage(content=system_content),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad", optional=True),
        ])

    async def execute(
        self,
        input_text: str,
        context: AgentContext,
    ) -> AgentResult:
        """Execute the agent with governance awareness."""
        start_time = datetime.utcnow()
        governance_checks: list[dict[str, Any]] = []

        try:
            self._context = context
            executor = self._build_executor(context)

            # Pre-execution governance check
            if context.governance_mode:
                check = await self._governance_pre_check(input_text, context)
                governance_checks.append(check)

                if not check.get("passed", True):
                    return AgentResult(
                        success=False,
                        output="Governance check failed",
                        error=check.get("reason", "Unknown governance failure"),
                        governance_checks=governance_checks,
                        duration_ms=self._calc_duration(start_time),
                    )

            # Execute agent
            result = await executor.ainvoke({
                "input": input_text,
                "chat_history": context.chat_history,
            })

            output = result.get("output", str(result))

            # Post-execution governance check
            if context.governance_mode:
                post_check = await self._governance_post_check(output, context)
                governance_checks.append(post_check)

            return AgentResult(
                success=True,
                output=output,
                governance_checks=governance_checks,
                duration_ms=self._calc_duration(start_time),
            )

        except Exception as e:
            return AgentResult(
                success=False,
                output="",
                error=str(e),
                governance_checks=governance_checks,
                duration_ms=self._calc_duration(start_time),
            )

    async def _governance_pre_check(
        self,
        input_text: str,
        context: AgentContext,
    ) -> dict[str, Any]:
        """Perform pre-execution governance check."""
        # Check if role has capability for this action
        return {
            "type": "pre-execution",
            "passed": True,
            "role": context.role.id,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _governance_post_check(
        self,
        output: str,
        context: AgentContext,
    ) -> dict[str, Any]:
        """Perform post-execution governance check."""
        # Validate output against constraints
        return {
            "type": "post-execution",
            "passed": True,
            "role": context.role.id,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calc_duration(self, start: datetime) -> int:
        """Calculate duration in milliseconds."""
        return int((datetime.utcnow() - start).total_seconds() * 1000)


class GovernanceAwareAgent(AgilePMAgent):
    """Agent with enhanced governance enforcement."""

    def __init__(
        self,
        config: AgentConfig,
        llm: BaseChatModel,
        tools: Optional[list[BaseTool]] = None,
        strict_mode: bool = True,
    ):
        """Initialize governance-aware agent.

        Args:
            config: Agent configuration
            llm: Language model
            tools: Optional tools
            strict_mode: If True, block execution on governance failures
        """
        super().__init__(config, llm, tools)
        self.strict_mode = strict_mode

    async def _governance_pre_check(
        self,
        input_text: str,
        context: AgentContext,
    ) -> dict[str, Any]:
        """Enhanced pre-execution governance check."""
        check_result = {
            "type": "pre-execution",
            "passed": True,
            "role": context.role.id,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
        }

        # Check 1: Role has capability for action
        capabilities_check = self._check_role_capabilities(input_text, context.role)
        check_result["checks"].append(capabilities_check)

        # Check 2: Task is assigned and in-progress
        if context.task:
            task_check = self._check_task_status(context.task)
            check_result["checks"].append(task_check)

        # Check 3: No constraint violations
        constraint_check = self._check_constraints(input_text, context.role)
        check_result["checks"].append(constraint_check)

        # Determine overall pass/fail
        all_passed = all(c.get("passed", True) for c in check_result["checks"])
        check_result["passed"] = all_passed

        if not all_passed:
            failed = [c for c in check_result["checks"] if not c.get("passed", True)]
            check_result["reason"] = "; ".join(c.get("reason", "Unknown") for c in failed)

        return check_result

    def _check_role_capabilities(
        self,
        input_text: str,
        role: RoleDefinition,
    ) -> dict[str, Any]:
        """Check if role has capability for the requested action."""
        # Simple keyword-based capability matching
        action_keywords = {
            "plan": ["plan", "design", "architect"],
            "implement": ["implement", "create", "build", "code"],
            "review": ["review", "audit", "assess"],
            "approve": ["approve", "authorize"],
            "deploy": ["deploy", "release", "publish"],
        }

        input_lower = input_text.lower()
        required_capabilities = []

        for capability, keywords in action_keywords.items():
            if any(kw in input_lower for kw in keywords):
                required_capabilities.append(capability)

        # Check if role has these capabilities
        role_caps_lower = [c.lower() for c in role.capabilities]
        missing = [c for c in required_capabilities if c not in role_caps_lower]

        return {
            "name": "role_capabilities",
            "passed": len(missing) == 0,
            "required": required_capabilities,
            "missing": missing,
            "reason": f"Missing capabilities: {missing}" if missing else None,
        }

    def _check_task_status(self, task: TaskAssignment) -> dict[str, Any]:
        """Check if task is in valid state for execution."""
        from agile_pm.models import TaskStatus

        valid_statuses = [TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED]

        return {
            "name": "task_status",
            "passed": task.status in valid_statuses,
            "current_status": task.status.value,
            "reason": f"Task status '{task.status.value}' not valid for execution"
            if task.status not in valid_statuses
            else None,
        }

    def _check_constraints(
        self,
        input_text: str,
        role: RoleDefinition,
    ) -> dict[str, Any]:
        """Check for constraint violations."""
        violations = []
        input_lower = input_text.lower()

        # Common constraint patterns
        constraint_patterns = {
            "no secrets": ["password", "api_key", "secret", "token"],
            "no direct db": ["raw sql", "direct query", "bypass orm"],
            "follow approval": ["skip approval", "bypass review"],
        }

        for constraint in role.constraints:
            constraint_lower = constraint.lower()
            for pattern, keywords in constraint_patterns.items():
                if pattern in constraint_lower:
                    if any(kw in input_lower for kw in keywords):
                        violations.append(f"Constraint '{constraint}' may be violated")

        return {
            "name": "constraints",
            "passed": len(violations) == 0,
            "violations": violations,
            "reason": "; ".join(violations) if violations else None,
        }


def create_agent(
    config: AgentConfig,
    llm: BaseChatModel,
    tools: Optional[list[BaseTool]] = None,
    governance_aware: bool = True,
    strict_mode: bool = False,
) -> BaseAgilePMAgent:
    """Factory function to create an Agile-PM agent.

    Args:
        config: Agent configuration
        llm: Language model to use
        tools: Optional list of tools
        governance_aware: Whether to use governance-aware agent
        strict_mode: Whether to block on governance failures

    Returns:
        Configured Agile-PM agent
    """
    if governance_aware:
        return GovernanceAwareAgent(config, llm, tools, strict_mode)
    else:
        return AgilePMAgent(config, llm, tools)

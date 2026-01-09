"""LangChain chains for Agile-PM task execution.

This module provides specialized chains for different Agile-PM workflows:
- Planning: Break down features into tasks
- Review: Analyze code and artifacts
- Execution: Complete assigned tasks
- Governance: Validate compliance
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from langchain.chains import LLMChain
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field


class ChainResult(BaseModel):
    """Result from chain execution."""

    success: bool
    output: Any
    chain_type: str
    duration_ms: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseChain(ABC):
    """Abstract base class for Agile-PM chains."""

    def __init__(self, llm: BaseChatModel, verbose: bool = False):
        """Initialize chain.

        Args:
            llm: Language model
            verbose: Enable verbose logging
        """
        self.llm = llm
        self.verbose = verbose
        self._chain: Optional[LLMChain] = None

    @property
    @abstractmethod
    def chain_type(self) -> str:
        """Get chain type identifier."""
        pass

    @abstractmethod
    def build_prompt(self) -> ChatPromptTemplate:
        """Build the prompt template."""
        pass

    def get_chain(self) -> Any:
        """Get or create the chain."""
        if self._chain is None:
            prompt = self.build_prompt()
            self._chain = prompt | self.llm | StrOutputParser()
        return self._chain

    async def invoke(self, inputs: dict[str, Any]) -> ChainResult:
        """Execute the chain.

        Args:
            inputs: Input variables

        Returns:
            ChainResult with output
        """
        start = datetime.utcnow()
        try:
            chain = self.get_chain()
            output = await chain.ainvoke(inputs)
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)

            return ChainResult(
                success=True,
                output=output,
                chain_type=self.chain_type,
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            return ChainResult(
                success=False,
                output=str(e),
                chain_type=self.chain_type,
                duration_ms=duration,
                metadata={"error": str(e)},
            )


class PlanningChain(BaseChain):
    """Chain for creating implementation plans."""

    @property
    def chain_type(self) -> str:
        return "planning"

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are a Technical PM creating an implementation plan.

## Output Format
Create a structured plan in Markdown with:
1. Executive Summary
2. Objectives (numbered list)
3. Tasks (table with ID, Task, Priority, Points, Assignee)
4. Dependencies
5. Risks and Mitigations
6. Approval section

## Guidelines
- Break features into 3-8 point stories
- Include acceptance criteria
- Identify P0 vs P1 priorities
- Map tasks to appropriate roles

## Governance
- All tasks must be trackable
- Include PM approval checkbox
- Reference tracking issue
"""),
            HumanMessagePromptTemplate.from_template("""Create an implementation plan for:

**Feature:** {feature_name}
**Description:** {description}
**Constraints:** {constraints}
**Timeline:** {timeline}

Generate the plan:"""),
        ])


class ReviewChain(BaseChain):
    """Chain for code and artifact review."""

    @property
    def chain_type(self) -> str:
        return "review"

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are a Code Reviewer analyzing submitted work.

## Review Categories
1. **Code Quality** - Complexity, readability, patterns
2. **Security** - Input validation, secrets, vulnerabilities
3. **Testing** - Coverage, edge cases, mocks
4. **Documentation** - Comments, README, API docs
5. **Governance** - Approval, tracking, compliance

## Severity Levels
- 🔴 **Critical** - Must fix before merge
- 🟠 **Major** - Should fix before merge
- 🟡 **Minor** - Can fix in follow-up
- 🔵 **Info** - Suggestions/notes

## Output Format
Provide structured feedback with:
1. Summary (overall assessment)
2. Findings (categorized by severity)
3. Recommendations
4. Approval Decision (Approve/Request Changes/Block)
"""),
            HumanMessagePromptTemplate.from_template("""Review the following:

**Type:** {artifact_type}
**File(s):** {files}
**Content:**
```
{content}
```

**Context:** {context}

Provide your review:"""),
        ])


class ExecutionChain(BaseChain):
    """Chain for task execution."""

    @property
    def chain_type(self) -> str:
        return "execution"

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are an Executor Agent completing a task.

## Execution Rules
1. Follow the task specification exactly
2. Write clean, tested code
3. Update task status when complete
4. Document changes made

## Quality Standards
- Code complexity ≤ 10 per function
- No duplicate logic
- All inputs validated
- Error handling present

## Output Format
1. Implementation summary
2. Files created/modified
3. Tests added
4. Remaining work (if any)
"""),
            HumanMessagePromptTemplate.from_template("""Execute the following task:

**Task ID:** {task_id}
**Title:** {task_title}
**Description:** {description}
**Acceptance Criteria:**
{acceptance_criteria}

**Files to modify:** {target_files}
**Role:** {role}

Execute and report results:"""),
        ])


class GovernanceChain(BaseChain):
    """Chain for governance validation."""

    @property
    def chain_type(self) -> str:
        return "governance"

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are a Governance Validator checking compliance.

## Governance Rules
1. All work tracked in Obsidian (cm-workflow/)
2. Approval required for:
   - ADRs → Technical Lead
   - Plans → PM
   - Security changes → Security Lead
   - Infrastructure → DevOps Lead
3. Quality gates:
   - SonarQube analysis passed
   - Test coverage ≥ 80%
   - No Critical/Major issues
4. Documentation updated

## Check Categories
- [ ] Task Tracking - Is task in Obsidian?
- [ ] Approval Status - Are required approvals present?
- [ ] Quality Gates - Are gates satisfied?
- [ ] Documentation - Is documentation current?

## Output Format
Return JSON:
{{
  "compliant": boolean,
  "checks": [
    {{"name": "...", "passed": boolean, "reason": "..."}}
  ],
  "blocking_issues": [...],
  "warnings": [...]
}}
"""),
            HumanMessagePromptTemplate.from_template("""Validate governance compliance:

**Action:** {action}
**Actor:** {actor_role}
**Target:** {target}
**Context:**
{context}

Perform governance validation:"""),
        ])


class RoleSwitchChain(BaseChain):
    """Chain for determining role switches."""

    @property
    def chain_type(self) -> str:
        return "role-switch"

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You determine when an agent should switch roles.

## Role Categories
1. **Strategic** (PM, Architect, Tech Lead, QA Lead, Security Lead)
2. **Executors** (Backend, Frontend, DevOps, QA, Security)
3. **Specialists** (ML, LLM, UI/UX, Performance, Data)
4. **Reviewers** (One per executor role)

## Switch Triggers
| Trigger | Switch To |
|---------|-----------|
| "plan", "design" | Technical PM |
| Backend code edit | Backend Engineer |
| Frontend code edit | Frontend Engineer |
| Test file edit | QA Executor |
| Security keyword | Security Executor |
| Infrastructure/Docker | DevOps Executor |
| Documentation | Technical Writer |
| PR review request | {Domain} Reviewer |

## Output Format
Return JSON:
{{
  "should_switch": boolean,
  "from_role": "current-role",
  "to_role": "new-role",
  "reason": "trigger condition",
  "charter_ref": "§X.Y"
}}
"""),
            HumanMessagePromptTemplate.from_template("""Determine if role switch needed:

**Current Role:** {current_role}
**Action:** {action}
**File Context:** {file_context}
**Keywords:** {keywords}

Analyze and respond:"""),
        ])


# Factory function
def create_chain(
    chain_type: str,
    llm: BaseChatModel,
    verbose: bool = False,
) -> BaseChain:
    """Create a chain by type.

    Args:
        chain_type: Type of chain (planning, review, execution, governance)
        llm: Language model
        verbose: Enable verbose logging

    Returns:
        Configured chain

    Raises:
        ValueError: If chain_type not recognized
    """
    chains = {
        "planning": PlanningChain,
        "review": ReviewChain,
        "execution": ExecutionChain,
        "governance": GovernanceChain,
        "role-switch": RoleSwitchChain,
    }

    if chain_type not in chains:
        raise ValueError(f"Unknown chain type: {chain_type}. Valid: {list(chains.keys())}")

    return chains[chain_type](llm, verbose)

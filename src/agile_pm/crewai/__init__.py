"""CrewAI integration for Agile-PM Agents.

This module provides CrewAI-based multi-agent orchestration including:
- Role-specific agent definitions
- Crew orchestration for complex tasks
- Task flow management
- Agent collaboration patterns
"""

from agile_pm.crewai.crew import (
    AgilePMCrew,
    create_crew,
    SprintCrew,
    ReviewCrew,
    ExecutionCrew,
)
from agile_pm.crewai.agents.strategic import (
    TechnicalPMAgent,
    ArchitectAgent,
    TechLeadAgent,
    QALeadAgent,
    SecurityLeadAgent,
)
from agile_pm.crewai.agents.executors import (
    BackendEngineerAgent,
    FrontendEngineerAgent,
    FullstackEngineerAgent,
    DevOpsEngineerAgent,
    QAExecutorAgent,
    SecurityExecutorAgent,
)
from agile_pm.crewai.agents.specialists import (
    MLSpecialistAgent,
    LLMSpecialistAgent,
    DataEngineerAgent,
    PerformanceEngineerAgent,
    UIUXSpecialistAgent,
)
from agile_pm.crewai.agents.reviewers import (
    BackendReviewerAgent,
    FrontendReviewerAgent,
    SecurityReviewerAgent,
)
from agile_pm.crewai.tasks.definitions import (
    PlanningTask,
    ImplementationTask,
    ReviewTask,
    TestingTask,
    DeploymentTask,
)

__all__ = [
    # Crews
    "AgilePMCrew",
    "create_crew",
    "SprintCrew",
    "ReviewCrew",
    "ExecutionCrew",
    # Strategic Agents
    "TechnicalPMAgent",
    "ArchitectAgent",
    "TechLeadAgent",
    "QALeadAgent",
    "SecurityLeadAgent",
    # Executor Agents
    "BackendEngineerAgent",
    "FrontendEngineerAgent",
    "FullstackEngineerAgent",
    "DevOpsEngineerAgent",
    "QAExecutorAgent",
    "SecurityExecutorAgent",
    # Specialist Agents
    "MLSpecialistAgent",
    "LLMSpecialistAgent",
    "DataEngineerAgent",
    "PerformanceEngineerAgent",
    "UIUXSpecialistAgent",
    # Reviewer Agents
    "BackendReviewerAgent",
    "FrontendReviewerAgent",
    "SecurityReviewerAgent",
    # Tasks
    "PlanningTask",
    "ImplementationTask",
    "ReviewTask",
    "TestingTask",
    "DeploymentTask",
]

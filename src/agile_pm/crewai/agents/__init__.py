"""Agents subpackage."""

from agile_pm.crewai.agents.strategic import (
    TechnicalPMAgent,
    ArchitectAgent,
    TechLeadAgent,
    QALeadAgent,
    SecurityLeadAgent,
    STRATEGIC_CONFIGS,
)
from agile_pm.crewai.agents.executors import (
    BackendEngineerAgent,
    FrontendEngineerAgent,
    FullstackEngineerAgent,
    DevOpsEngineerAgent,
    QAExecutorAgent,
    SecurityExecutorAgent,
    EXECUTOR_CONFIGS,
)
from agile_pm.crewai.agents.specialists import (
    MLSpecialistAgent,
    LLMSpecialistAgent,
    DataEngineerAgent,
    PerformanceEngineerAgent,
    UIUXSpecialistAgent,
    SPECIALIST_CONFIGS,
)
from agile_pm.crewai.agents.reviewers import (
    BackendReviewerAgent,
    FrontendReviewerAgent,
    SecurityReviewerAgent,
    REVIEWER_CONFIGS,
)

__all__ = [
    # Strategic
    "TechnicalPMAgent",
    "ArchitectAgent",
    "TechLeadAgent",
    "QALeadAgent",
    "SecurityLeadAgent",
    "STRATEGIC_CONFIGS",
    # Executors
    "BackendEngineerAgent",
    "FrontendEngineerAgent",
    "FullstackEngineerAgent",
    "DevOpsEngineerAgent",
    "QAExecutorAgent",
    "SecurityExecutorAgent",
    "EXECUTOR_CONFIGS",
    # Specialists
    "MLSpecialistAgent",
    "LLMSpecialistAgent",
    "DataEngineerAgent",
    "PerformanceEngineerAgent",
    "UIUXSpecialistAgent",
    "SPECIALIST_CONFIGS",
    # Reviewers
    "BackendReviewerAgent",
    "FrontendReviewerAgent",
    "SecurityReviewerAgent",
    "REVIEWER_CONFIGS",
]

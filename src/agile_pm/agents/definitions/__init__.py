"""
Agent Definitions

Provides concrete implementations for all 33 governance roles.
Each agent implements the BaseAgent interface with role-specific:
- Description and backstory
- Capabilities and constraints
- Role switching triggers
- Available tools
"""

from .all_roles import (
    # Strategic Agents (5)
    TechnicalPMAgent,
    ArchitectAgent,
    TechLeadAgent,
    QALeadAgent,
    SecurityLeadAgent,
    # Executor Agents (6)
    BackendEngineerAgent,
    FrontendEngineerAgent,
    FullstackEngineerAgent,
    DevOpsEngineerAgent,
    QAExecutorAgent,
    SecurityExecutorAgent,
    # Specialist Agents (6)
    MLSpecialistAgent,
    LLMSpecialistAgent,
    DataSpecialistAgent,
    PerformanceSpecialistAgent,
    UIUXSpecialistAgent,
    TechnicalWriterAgent,
    # Reviewer Agents (5)
    BackendReviewerAgent,
    FrontendReviewerAgent,
    SecurityReviewerAgent,
    DevOpsReviewerAgent,
    ArchitectureReviewerAgent,
    # All agents list
    ALL_AGENTS,
)

__all__ = [
    # Strategic
    "TechnicalPMAgent",
    "ArchitectAgent",
    "TechLeadAgent",
    "QALeadAgent",
    "SecurityLeadAgent",
    # Executor
    "BackendEngineerAgent",
    "FrontendEngineerAgent",
    "FullstackEngineerAgent",
    "DevOpsEngineerAgent",
    "QAExecutorAgent",
    "SecurityExecutorAgent",
    # Specialist
    "MLSpecialistAgent",
    "LLMSpecialistAgent",
    "DataSpecialistAgent",
    "PerformanceSpecialistAgent",
    "UIUXSpecialistAgent",
    "TechnicalWriterAgent",
    # Reviewer
    "BackendReviewerAgent",
    "FrontendReviewerAgent",
    "SecurityReviewerAgent",
    "DevOpsReviewerAgent",
    "ArchitectureReviewerAgent",
    # Collection
    "ALL_AGENTS",
]

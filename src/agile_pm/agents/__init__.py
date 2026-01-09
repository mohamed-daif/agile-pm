"""
Agile-PM Agent Definitions

This module provides agent definitions for all 33 governance roles,
implementing the role switching and capability mapping from governance files.

Usage:
    from agile_pm.agents import AgentRegistry, BaseAgent
    
    registry = AgentRegistry()
    agent = registry.get_agent("backend-engineer")
    result = await agent.execute(task)
"""

from .base import (
    BaseAgent,
    AgentCapability,
    AgentConstraint,
    AgentTrigger,
    AgentContext,
    AgentResult,
)
from .registry import AgentRegistry, get_agent, list_agents
from .definitions import (
    # Strategic Agents
    TechnicalPMAgent,
    ArchitectAgent,
    TechLeadAgent,
    QALeadAgent,
    SecurityLeadAgent,
    # Executor Agents
    BackendEngineerAgent,
    FrontendEngineerAgent,
    FullstackEngineerAgent,
    DevOpsEngineerAgent,
    QAExecutorAgent,
    SecurityExecutorAgent,
    # Specialist Agents
    MLSpecialistAgent,
    LLMSpecialistAgent,
    DataSpecialistAgent,
    PerformanceSpecialistAgent,
    UIUXSpecialistAgent,
    TechnicalWriterAgent,
    # Reviewer Agents
    BackendReviewerAgent,
    FrontendReviewerAgent,
    SecurityReviewerAgent,
    DevOpsReviewerAgent,
    ArchitectureReviewerAgent,
)

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentCapability",
    "AgentConstraint",
    "AgentTrigger",
    "AgentContext",
    "AgentResult",
    # Registry
    "AgentRegistry",
    "get_agent",
    "list_agents",
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
    "DataSpecialistAgent",
    "PerformanceSpecialistAgent",
    "UIUXSpecialistAgent",
    "TechnicalWriterAgent",
    # Reviewer Agents
    "BackendReviewerAgent",
    "FrontendReviewerAgent",
    "SecurityReviewerAgent",
    "DevOpsReviewerAgent",
    "ArchitectureReviewerAgent",
]

"""LangChain integration for Agile-PM Agents.

This module provides LangChain-based AI agent capabilities including:
- Base agent wrappers with governance awareness
- Prompt templates for role-specific behavior
- Chain definitions for task execution
- Tool integrations (Obsidian, GitHub MCP)
- Conversation memory management
"""

from agile_pm.langchain.agent import (
    AgilePMAgent,
    GovernanceAwareAgent,
    create_agent,
)
from agile_pm.langchain.chains import (
    PlanningChain,
    ReviewChain,
    ExecutionChain,
    GovernanceChain,
)
from agile_pm.langchain.prompts import (
    ROLE_PROMPTS,
    SYSTEM_PROMPTS,
    get_role_prompt,
    get_system_prompt,
)
from agile_pm.langchain.tools import (
    ObsidianTool,
    GitHubMCPTool,
    SerenaTool,
    get_tool_registry,
)
from agile_pm.langchain.memory import (
    AgentMemory,
    SessionMemory,
    create_memory,
)

__all__ = [
    # Agents
    "AgilePMAgent",
    "GovernanceAwareAgent",
    "create_agent",
    # Chains
    "PlanningChain",
    "ReviewChain",
    "ExecutionChain",
    "GovernanceChain",
    # Prompts
    "ROLE_PROMPTS",
    "SYSTEM_PROMPTS",
    "get_role_prompt",
    "get_system_prompt",
    # Tools
    "ObsidianTool",
    "GitHubMCPTool",
    "SerenaTool",
    "get_tool_registry",
    # Memory
    "AgentMemory",
    "SessionMemory",
    "create_memory",
]

"""Agile-PM: AI-powered Agile project management agent framework.

This package provides LangChain and CrewAI integrations for AI-powered
Agile project management, including:

- Multi-agent crews for planning, execution, and review
- Persistent memory storage with PostgreSQL/Redis support
- Real-time dashboard with WebSocket updates
- Observability with OpenTelemetry tracing
- CLI for project initialization and provider integration
"""

__version__ = "0.1.0"
__author__ = "Mohamed Daif"
__email__ = "mohamed.daif@gmail.com"

# Core configuration and project management
from agile_pm.core.config import AgileConfig
from agile_pm.core.project import AgileProject

# Models
from agile_pm.models import (
    AgentConfig,
    RoleDefinition,
    TaskAssignment,
    AgentProvider,
    AgentStatus,
    TaskStatus,
    TaskPriority,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    "__email__",
    # Core
    "AgileConfig",
    "AgileProject",
    # Models
    "AgentConfig",
    "RoleDefinition",
    "TaskAssignment",
    "AgentProvider",
    "AgentStatus",
    "TaskStatus",
    "TaskPriority",
]

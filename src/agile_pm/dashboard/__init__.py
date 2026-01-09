"""Real-time dashboard module for agent monitoring.

Implements P4-003: WebSocket server and React component API.
"""

from .server import DashboardServer, DashboardConfig
from .events import (
    DashboardEvent,
    EventType,
    AgentStatusEvent,
    TaskProgressEvent,
    MetricsEvent,
)
from .metrics import MetricsCollector, AgentMetrics, TaskMetrics

__all__ = [
    "DashboardServer",
    "DashboardConfig",
    "DashboardEvent",
    "EventType",
    "AgentStatusEvent",
    "TaskProgressEvent",
    "MetricsEvent",
    "MetricsCollector",
    "AgentMetrics",
    "TaskMetrics",
]

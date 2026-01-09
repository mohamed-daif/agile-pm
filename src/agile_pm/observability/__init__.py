"""Observability module for agent tracing and metrics.

Implements P4-005: OpenTelemetry integration and monitoring.
"""

from .tracer import (
    AgentTracer,
    TracingConfig,
    trace_agent_action,
    trace_task_execution,
)
from .metrics import (
    PrometheusMetrics,
    MetricsConfig,
    counter,
    histogram,
    gauge,
)
from .logging import (
    StructuredLogger,
    LogConfig,
    get_logger,
)

__all__ = [
    "AgentTracer",
    "TracingConfig",
    "trace_agent_action",
    "trace_task_execution",
    "PrometheusMetrics",
    "MetricsConfig",
    "counter",
    "histogram",
    "gauge",
    "StructuredLogger",
    "LogConfig",
    "get_logger",
]

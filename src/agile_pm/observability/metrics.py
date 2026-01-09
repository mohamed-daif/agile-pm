"""Prometheus metrics for agent monitoring."""

import functools
from typing import Any, Callable, Optional, TypeVar
from datetime import datetime
import logging

from pydantic import BaseModel, Field

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Info,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
        start_http_server,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar("T")


class MetricsConfig(BaseModel):
    """Configuration for Prometheus metrics."""

    enabled: bool = Field(default=True)
    port: int = Field(default=8000, description="Metrics server port")
    prefix: str = Field(default="agile_pm")
    
    # Histogram buckets
    duration_buckets: tuple = Field(
        default=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0)
    )
    token_buckets: tuple = Field(
        default=(100, 500, 1000, 2500, 5000, 10000, 25000, 50000)
    )


class PrometheusMetrics:
    """Prometheus metrics collector for agent monitoring."""

    def __init__(
        self,
        config: Optional[MetricsConfig] = None,
        registry: Optional[Any] = None,
    ):
        """Initialize metrics.
        
        Args:
            config: Metrics configuration
            registry: Custom prometheus registry
        """
        self.config = config or MetricsConfig()
        
        if not PROMETHEUS_AVAILABLE or not self.config.enabled:
            self._enabled = False
            return
        
        self._enabled = True
        self._registry = registry or CollectorRegistry()
        self._setup_metrics()
    
    def _setup_metrics(self) -> None:
        """Set up Prometheus metrics."""
        prefix = self.config.prefix
        
        # Agent metrics
        self.agents_active = Gauge(
            f"{prefix}_agents_active_count",
            "Number of active agents",
            ["role"],
            registry=self._registry,
        )
        
        self.agent_tasks_total = Counter(
            f"{prefix}_agent_tasks_total",
            "Total tasks executed by agents",
            ["agent_id", "agent_role", "status"],
            registry=self._registry,
        )
        
        self.agent_task_duration = Histogram(
            f"{prefix}_agent_task_duration_seconds",
            "Agent task duration in seconds",
            ["agent_role"],
            buckets=self.config.duration_buckets,
            registry=self._registry,
        )
        
        # Task metrics
        self.tasks_total = Counter(
            f"{prefix}_tasks_total",
            "Total tasks created",
            ["status"],
            registry=self._registry,
        )
        
        self.tasks_queued = Gauge(
            f"{prefix}_tasks_queued_total",
            "Tasks currently queued",
            registry=self._registry,
        )
        
        self.tasks_in_progress = Gauge(
            f"{prefix}_tasks_in_progress_total",
            "Tasks currently in progress",
            registry=self._registry,
        )
        
        self.task_duration = Histogram(
            f"{prefix}_task_duration_seconds",
            "Task execution duration",
            ["task_type"],
            buckets=self.config.duration_buckets,
            registry=self._registry,
        )
        
        # LLM metrics
        self.llm_calls_total = Counter(
            f"{prefix}_llm_calls_total",
            "Total LLM API calls",
            ["model", "status"],
            registry=self._registry,
        )
        
        self.llm_tokens_total = Counter(
            f"{prefix}_llm_tokens_total",
            "Total LLM tokens used",
            ["model", "type"],
            registry=self._registry,
        )
        
        self.llm_call_duration = Histogram(
            f"{prefix}_llm_call_duration_seconds",
            "LLM API call duration",
            ["model"],
            buckets=self.config.duration_buckets,
            registry=self._registry,
        )
        
        # Memory metrics
        self.memory_sessions = Gauge(
            f"{prefix}_memory_sessions_active",
            "Active memory sessions",
            registry=self._registry,
        )
        
        self.memory_entries = Gauge(
            f"{prefix}_memory_entries_total",
            "Total memory entries",
            ["memory_type"],
            registry=self._registry,
        )
        
        # Dashboard metrics
        self.websocket_connections = Gauge(
            f"{prefix}_websocket_connections",
            "Active WebSocket connections",
            registry=self._registry,
        )
        
        # Crew metrics
        self.crew_executions_total = Counter(
            f"{prefix}_crew_executions_total",
            "Total crew executions",
            ["crew_name", "status"],
            registry=self._registry,
        )
        
        self.crew_duration = Histogram(
            f"{prefix}_crew_duration_seconds",
            "Crew execution duration",
            ["crew_name"],
            buckets=self.config.duration_buckets,
            registry=self._registry,
        )
        
        # Service info
        self.service_info = Info(
            f"{prefix}_service",
            "Service information",
            registry=self._registry,
        )
        self.service_info.info({
            "version": "1.0.0",
            "environment": "production",
        })
        
        logger.info("Prometheus metrics initialized")
    
    def start_server(self) -> None:
        """Start metrics HTTP server."""
        if not self._enabled:
            return
        
        start_http_server(self.config.port, registry=self._registry)
        logger.info(f"Metrics server started on port {self.config.port}")
    
    def get_metrics(self) -> bytes:
        """Get metrics in Prometheus format.
        
        Returns:
            Metrics as bytes
        """
        if not self._enabled:
            return b""
        return generate_latest(self._registry)
    
    # Agent tracking
    def track_agent_start(self, agent_id: str, role: str) -> None:
        """Track agent start."""
        if self._enabled:
            self.agents_active.labels(role=role).inc()
    
    def track_agent_stop(self, agent_id: str, role: str) -> None:
        """Track agent stop."""
        if self._enabled:
            self.agents_active.labels(role=role).dec()
    
    def track_agent_task(
        self,
        agent_id: str,
        role: str,
        duration: float,
        success: bool,
    ) -> None:
        """Track agent task execution."""
        if not self._enabled:
            return
        
        status = "success" if success else "failure"
        self.agent_tasks_total.labels(
            agent_id=agent_id,
            agent_role=role,
            status=status,
        ).inc()
        self.agent_task_duration.labels(agent_role=role).observe(duration)
    
    # Task tracking
    def track_task_created(self, task_type: str = "default") -> None:
        """Track task creation."""
        if self._enabled:
            self.tasks_total.labels(status="created").inc()
            self.tasks_queued.inc()
    
    def track_task_started(self) -> None:
        """Track task start."""
        if self._enabled:
            self.tasks_queued.dec()
            self.tasks_in_progress.inc()
    
    def track_task_completed(
        self,
        task_type: str,
        duration: float,
        success: bool,
    ) -> None:
        """Track task completion."""
        if not self._enabled:
            return
        
        self.tasks_in_progress.dec()
        status = "completed" if success else "failed"
        self.tasks_total.labels(status=status).inc()
        self.task_duration.labels(task_type=task_type).observe(duration)
    
    # LLM tracking
    def track_llm_call(
        self,
        model: str,
        duration: float,
        prompt_tokens: int,
        completion_tokens: int,
        success: bool,
    ) -> None:
        """Track LLM API call."""
        if not self._enabled:
            return
        
        status = "success" if success else "failure"
        self.llm_calls_total.labels(model=model, status=status).inc()
        self.llm_tokens_total.labels(model=model, type="prompt").inc(prompt_tokens)
        self.llm_tokens_total.labels(model=model, type="completion").inc(completion_tokens)
        self.llm_call_duration.labels(model=model).observe(duration)
    
    # Memory tracking
    def track_memory_session(self, active: bool) -> None:
        """Track memory session."""
        if self._enabled:
            if active:
                self.memory_sessions.inc()
            else:
                self.memory_sessions.dec()
    
    def set_memory_entries(self, memory_type: str, count: int) -> None:
        """Set memory entry count."""
        if self._enabled:
            self.memory_entries.labels(memory_type=memory_type).set(count)
    
    # WebSocket tracking
    def track_websocket_connection(self, connected: bool) -> None:
        """Track WebSocket connection."""
        if self._enabled:
            if connected:
                self.websocket_connections.inc()
            else:
                self.websocket_connections.dec()
    
    # Crew tracking
    def track_crew_execution(
        self,
        crew_name: str,
        duration: float,
        success: bool,
    ) -> None:
        """Track crew execution."""
        if not self._enabled:
            return
        
        status = "success" if success else "failure"
        self.crew_executions_total.labels(crew_name=crew_name, status=status).inc()
        self.crew_duration.labels(crew_name=crew_name).observe(duration)


# Global metrics instance
_metrics: Optional[PrometheusMetrics] = None


def get_metrics() -> PrometheusMetrics:
    """Get global metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = PrometheusMetrics()
    return _metrics


def init_metrics(config: Optional[MetricsConfig] = None) -> PrometheusMetrics:
    """Initialize global metrics.
    
    Args:
        config: Metrics configuration
        
    Returns:
        Metrics instance
    """
    global _metrics
    _metrics = PrometheusMetrics(config)
    return _metrics


# Convenience decorators
def counter(name: str, labels: Optional[dict] = None):
    """Decorator to count function calls."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            metrics = get_metrics()
            if metrics._enabled:
                metrics.tasks_total.labels(status="started").inc()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def histogram(name: str, labels: Optional[dict] = None):
    """Decorator to track function duration."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            metrics = get_metrics()
            start = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                if metrics._enabled:
                    duration = (datetime.utcnow() - start).total_seconds()
                    metrics.task_duration.labels(task_type=name).observe(duration)
        return wrapper
    return decorator


def gauge(name: str, value_func: Callable[[], float]):
    """Create a gauge from a value function."""
    pass  # Implementation depends on specific use case

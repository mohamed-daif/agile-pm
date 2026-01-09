"""OpenTelemetry tracing for agent operations."""

import functools
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Optional, TypeVar
import logging

from pydantic import BaseModel, Field

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TracingConfig(BaseModel):
    """Configuration for tracing."""

    enabled: bool = Field(default=True)
    service_name: str = Field(default="agile-pm-agents")
    service_version: str = Field(default="1.0.0")
    environment: str = Field(default="production")
    
    # OTLP exporter settings
    otlp_endpoint: str = Field(default="http://localhost:4317")
    otlp_insecure: bool = Field(default=True)
    
    # Sampling
    sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Span limits
    max_attributes: int = Field(default=128)
    max_events: int = Field(default=128)


class AgentTracer:
    """Tracer for agent operations with OpenTelemetry integration."""

    def __init__(self, config: Optional[TracingConfig] = None):
        """Initialize tracer.
        
        Args:
            config: Tracing configuration
        """
        self.config = config or TracingConfig()
        self._tracer = None
        self._provider = None
        
        if self.config.enabled and OTEL_AVAILABLE:
            self._setup_tracing()
    
    def _setup_tracing(self) -> None:
        """Set up OpenTelemetry tracing."""
        resource = Resource.create({
            "service.name": self.config.service_name,
            "service.version": self.config.service_version,
            "deployment.environment": self.config.environment,
        })
        
        self._provider = TracerProvider(resource=resource)
        
        # Add OTLP exporter
        exporter = OTLPSpanExporter(
            endpoint=self.config.otlp_endpoint,
            insecure=self.config.otlp_insecure,
        )
        self._provider.add_span_processor(BatchSpanProcessor(exporter))
        
        # Set as global provider
        trace.set_tracer_provider(self._provider)
        
        self._tracer = trace.get_tracer(
            self.config.service_name,
            self.config.service_version,
        )
        
        logger.info("OpenTelemetry tracing initialized")
    
    @contextmanager
    def span(
        self,
        name: str,
        attributes: Optional[dict[str, Any]] = None,
        kind: Optional[Any] = None,
    ):
        """Create a traced span.
        
        Args:
            name: Span name
            attributes: Span attributes
            kind: Span kind
            
        Yields:
            Active span
        """
        if not self._tracer:
            yield None
            return
        
        with self._tracer.start_as_current_span(
            name,
            attributes=attributes or {},
            kind=kind,
        ) as span:
            try:
                yield span
            except Exception as e:
                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise
    
    def trace_agent(self, agent_id: str, role: str):
        """Decorator to trace agent operations.
        
        Args:
            agent_id: Agent identifier
            role: Agent role
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> T:
                with self.span(
                    f"agent.{func.__name__}",
                    attributes={
                        "agent.id": agent_id,
                        "agent.role": role,
                        "agent.function": func.__name__,
                    },
                ) as span:
                    result = func(*args, **kwargs)
                    if span:
                        span.set_attribute("agent.success", True)
                    return result
            return wrapper
        return decorator
    
    def trace_task(self, task_id: str, task_name: str):
        """Decorator to trace task execution.
        
        Args:
            task_id: Task identifier
            task_name: Task name
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> T:
                with self.span(
                    f"task.{task_name}",
                    attributes={
                        "task.id": task_id,
                        "task.name": task_name,
                    },
                ) as span:
                    start_time = datetime.utcnow()
                    result = func(*args, **kwargs)
                    duration = (datetime.utcnow() - start_time).total_seconds()
                    if span:
                        span.set_attribute("task.duration_seconds", duration)
                        span.set_attribute("task.success", True)
                    return result
            return wrapper
        return decorator
    
    def trace_llm_call(
        self,
        model: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ):
        """Decorator to trace LLM API calls.
        
        Args:
            model: Model name
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                with self.span(
                    "llm.call",
                    attributes={
                        "llm.model": model,
                        "llm.prompt_tokens": prompt_tokens,
                    },
                ) as span:
                    start_time = datetime.utcnow()
                    result = await func(*args, **kwargs)
                    duration = (datetime.utcnow() - start_time).total_seconds()
                    if span:
                        span.set_attribute("llm.duration_seconds", duration)
                        span.set_attribute("llm.completion_tokens", completion_tokens)
                    return result
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                with self.span(
                    "llm.call",
                    attributes={
                        "llm.model": model,
                        "llm.prompt_tokens": prompt_tokens,
                    },
                ) as span:
                    result = func(*args, **kwargs)
                    return result
            
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        return decorator
    
    def get_trace_id(self) -> Optional[str]:
        """Get current trace ID.
        
        Returns:
            Trace ID if available
        """
        if not OTEL_AVAILABLE:
            return None
        
        span = trace.get_current_span()
        if span:
            context = span.get_span_context()
            if context.is_valid:
                return format(context.trace_id, '032x')
        return None
    
    def inject_context(self, carrier: dict) -> dict:
        """Inject trace context into carrier for propagation.
        
        Args:
            carrier: Dict to inject context into
            
        Returns:
            Carrier with context
        """
        if OTEL_AVAILABLE:
            propagator = TraceContextTextMapPropagator()
            propagator.inject(carrier)
        return carrier
    
    def shutdown(self) -> None:
        """Shutdown tracer and flush spans."""
        if self._provider:
            self._provider.shutdown()


# Convenience decorators
def trace_agent_action(agent_id: str, role: str):
    """Decorator to trace agent actions.
    
    Args:
        agent_id: Agent identifier
        role: Agent role
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not OTEL_AVAILABLE:
                return func(*args, **kwargs)
            
            tracer = trace.get_tracer("agile-pm-agents")
            with tracer.start_as_current_span(
                f"agent.{func.__name__}",
                attributes={
                    "agent.id": agent_id,
                    "agent.role": role,
                },
            ):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def trace_task_execution(task_id: str, task_name: str):
    """Decorator to trace task execution.
    
    Args:
        task_id: Task identifier
        task_name: Task name
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not OTEL_AVAILABLE:
                return func(*args, **kwargs)
            
            tracer = trace.get_tracer("agile-pm-agents")
            with tracer.start_as_current_span(
                f"task.{task_name}",
                attributes={
                    "task.id": task_id,
                    "task.name": task_name,
                },
            ):
                return func(*args, **kwargs)
        return wrapper
    return decorator

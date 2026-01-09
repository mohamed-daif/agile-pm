"""Resilience Module for Agile-PM."""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerStats,
    CircuitState,
)
from .retry_backoff import (
    RetryConfig,
    calculate_delay,
    retry,
    retry_async,
    retry_on_network_error,
    retry_on_rate_limit,
)
from .graceful_shutdown import (
    GracefulShutdown,
    ShutdownConfig,
    graceful_shutdown_context,
)
from .health_check import (
    ComponentHealth,
    HealthCheckResult,
    HealthChecker,
    HealthStatus,
    get_health_checker,
)

__all__ = [
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerError",
    "CircuitBreakerStats",
    "CircuitState",
    # Retry
    "RetryConfig",
    "calculate_delay",
    "retry",
    "retry_async",
    "retry_on_network_error",
    "retry_on_rate_limit",
    # Shutdown
    "GracefulShutdown",
    "ShutdownConfig",
    "graceful_shutdown_context",
    # Health
    "ComponentHealth",
    "HealthCheckResult",
    "HealthChecker",
    "HealthStatus",
    "get_health_checker",
]

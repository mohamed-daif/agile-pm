"""Circuit Breaker Pattern Implementation."""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, TypeVar, Generic

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5           # Failures before opening
    success_threshold: int = 3           # Successes to close from half-open
    timeout: float = 30.0                # Seconds before trying half-open
    excluded_exceptions: tuple = ()      # Exceptions that don't count as failures


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics."""
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: float = field(default_factory=time.time)
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0


class CircuitBreakerError(Exception):
    """Raised when circuit is open."""
    def __init__(self, message: str, retry_after: float):
        super().__init__(message)
        self.retry_after = retry_after


class CircuitBreaker(Generic[T]):
    """Circuit breaker for protecting calls to external services."""

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback: Optional[Callable[..., T]] = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback = fallback
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self.stats.state

    async def _check_state_transition(self) -> None:
        """Check if state should transition based on timeout."""
        if self.stats.state == CircuitState.OPEN:
            elapsed = time.time() - self.stats.last_state_change
            if elapsed >= self.config.timeout:
                await self._transition_to(CircuitState.HALF_OPEN)

    async def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to new state."""
        self.stats.state = new_state
        self.stats.last_state_change = time.time()
        self.stats.failures = 0
        self.stats.successes = 0

    async def _record_success(self) -> None:
        """Record successful call."""
        self.stats.successes += 1
        self.stats.total_successes += 1
        
        if self.stats.state == CircuitState.HALF_OPEN:
            if self.stats.successes >= self.config.success_threshold:
                await self._transition_to(CircuitState.CLOSED)

    async def _record_failure(self, exc: Exception) -> None:
        """Record failed call."""
        # Check if exception should be excluded
        if isinstance(exc, self.config.excluded_exceptions):
            return
        
        self.stats.failures += 1
        self.stats.total_failures += 1
        self.stats.last_failure_time = time.time()
        
        if self.stats.state == CircuitState.CLOSED:
            if self.stats.failures >= self.config.failure_threshold:
                await self._transition_to(CircuitState.OPEN)
        elif self.stats.state == CircuitState.HALF_OPEN:
            await self._transition_to(CircuitState.OPEN)

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function through circuit breaker."""
        async with self._lock:
            self.stats.total_calls += 1
            await self._check_state_transition()
            
            if self.stats.state == CircuitState.OPEN:
                retry_after = self.config.timeout - (time.time() - self.stats.last_state_change)
                if self.fallback:
                    return self.fallback(*args, **kwargs)
                raise CircuitBreakerError(
                    f"Circuit {self.name} is OPEN",
                    retry_after=max(0, retry_after),
                )
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            async with self._lock:
                await self._record_success()
            return result
            
        except Exception as e:
            async with self._lock:
                await self._record_failure(e)
            raise

    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.stats.state.value,
            "failures": self.stats.failures,
            "successes": self.stats.successes,
            "total_calls": self.stats.total_calls,
            "total_failures": self.stats.total_failures,
            "total_successes": self.stats.total_successes,
            "last_failure": self.stats.last_failure_time,
        }

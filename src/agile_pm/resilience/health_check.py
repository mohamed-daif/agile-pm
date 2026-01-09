"""Health Check Implementation."""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health of a single component."""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None
    last_check: float = field(default_factory=time.time)


@dataclass
class HealthCheckResult:
    """Overall health check result."""
    status: HealthStatus
    components: List[ComponentHealth]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                }
                for c in self.components
            ],
        }


class HealthChecker:
    """Health check manager."""

    def __init__(self):
        self._checks: Dict[str, Callable] = {}
        self._cache: Optional[HealthCheckResult] = None
        self._cache_ttl: float = 5.0  # Cache results for 5 seconds
        self._last_check: float = 0

    def register(
        self,
        name: str,
        check_func: Callable,
        critical: bool = True,
    ) -> None:
        """Register a health check."""
        self._checks[name] = {"func": check_func, "critical": critical}

    async def check_component(self, name: str, check_info: dict) -> ComponentHealth:
        """Run health check for a single component."""
        start = time.time()
        try:
            func = check_info["func"]
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(), timeout=5.0)
            else:
                result = func()
            
            latency = (time.time() - start) * 1000
            
            if result is True:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                )
            elif result is False:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message="Check returned False",
                    latency_ms=latency,
                )
            else:
                # Result is a message
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.DEGRADED,
                    message=str(result),
                    latency_ms=latency,
                )
                
        except asyncio.TimeoutError:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message="Health check timed out",
            )
        except Exception as e:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )

    async def check(self, use_cache: bool = True) -> HealthCheckResult:
        """Run all health checks."""
        now = time.time()
        
        # Return cached result if valid
        if use_cache and self._cache and (now - self._last_check) < self._cache_ttl:
            return self._cache
        
        # Run all checks
        components = await asyncio.gather(
            *[
                self.check_component(name, info)
                for name, info in self._checks.items()
            ]
        )
        
        # Determine overall status
        has_unhealthy_critical = any(
            c.status == HealthStatus.UNHEALTHY
            and self._checks[c.name].get("critical", True)
            for c in components
        )
        has_degraded = any(c.status == HealthStatus.DEGRADED for c in components)
        
        if has_unhealthy_critical:
            overall_status = HealthStatus.UNHEALTHY
        elif has_degraded:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        result = HealthCheckResult(
            status=overall_status,
            components=list(components),
        )
        
        self._cache = result
        self._last_check = now
        
        return result


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

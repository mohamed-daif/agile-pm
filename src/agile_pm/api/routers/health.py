"""Deep health check endpoints."""
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from agile_pm.storage.health import check_database, check_redis
from agile_pm.observability.tracing import get_tracer

router = APIRouter(tags=["health"])
tracer = get_tracer(__name__)


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    name: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: HealthStatus
    timestamp: datetime
    version: str
    components: List[ComponentHealth]
    checks_passed: int
    checks_failed: int


@router.get("/health")
async def health_check():
    """Basic health check - fast, for load balancers."""
    return {"status": "ok"}


@router.get("/ready", response_model=HealthResponse)
async def readiness_check(response: Response):
    """Readiness check - verifies all dependencies."""
    with tracer.start_as_current_span("readiness_check"):
        components = []
        
        # Check database
        db_health = await _check_database()
        components.append(db_health)
        
        # Check Redis
        redis_health = await _check_redis()
        components.append(redis_health)
        
        # Check Celery broker
        celery_health = await _check_celery()
        components.append(celery_health)
        
        # Aggregate status
        failed = sum(1 for c in components if c.status == HealthStatus.UNHEALTHY)
        degraded = sum(1 for c in components if c.status == HealthStatus.DEGRADED)
        
        if failed > 0:
            overall_status = HealthStatus.UNHEALTHY
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED
            response.status_code = status.HTTP_200_OK
        else:
            overall_status = HealthStatus.HEALTHY
            response.status_code = status.HTTP_200_OK
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            components=components,
            checks_passed=len(components) - failed,
            checks_failed=failed,
        )


@router.get("/live")
async def liveness_check():
    """Liveness check - is the process alive."""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/deep", response_model=HealthResponse)
async def deep_health_check(response: Response):
    """Deep health check with extended diagnostics."""
    with tracer.start_as_current_span("deep_health_check"):
        components = []
        
        # Core dependencies
        components.append(await _check_database(detailed=True))
        components.append(await _check_redis(detailed=True))
        components.append(await _check_celery(detailed=True))
        
        # External services
        components.append(await _check_external_apis())
        
        # Determine overall status
        failed = sum(1 for c in components if c.status == HealthStatus.UNHEALTHY)
        degraded = sum(1 for c in components if c.status == HealthStatus.DEGRADED)
        
        if failed > 0:
            overall_status = HealthStatus.UNHEALTHY
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            components=components,
            checks_passed=len(components) - failed,
            checks_failed=failed,
        )


async def _check_database(detailed: bool = False) -> ComponentHealth:
    """Check database connectivity and pool status."""
    import time
    start = time.time()
    try:
        result = await check_database()
        latency = (time.time() - start) * 1000
        
        details = None
        if detailed:
            details = {
                "pool_size": result.get("pool_size", 0),
                "active_connections": result.get("active", 0),
                "idle_connections": result.get("idle", 0),
            }
        
        return ComponentHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
            details=details,
        )
    except Exception as e:
        return ComponentHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def _check_redis(detailed: bool = False) -> ComponentHealth:
    """Check Redis connectivity."""
    import time
    start = time.time()
    try:
        result = await check_redis()
        latency = (time.time() - start) * 1000
        
        details = None
        if detailed:
            details = {
                "connected_clients": result.get("connected_clients", 0),
                "used_memory": result.get("used_memory_human", "unknown"),
            }
        
        return ComponentHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
            details=details,
        )
    except Exception as e:
        return ComponentHealth(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def _check_celery(detailed: bool = False) -> ComponentHealth:
    """Check Celery broker connectivity."""
    try:
        from agile_pm.queue.celery_app import celery_app
        
        # Ping the broker
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if not stats:
            return ComponentHealth(
                name="celery",
                status=HealthStatus.DEGRADED,
                message="No workers responding",
            )
        
        details = None
        if detailed:
            details = {
                "workers": len(stats),
                "worker_names": list(stats.keys()),
            }
        
        return ComponentHealth(
            name="celery",
            status=HealthStatus.HEALTHY,
            details=details,
        )
    except Exception as e:
        return ComponentHealth(
            name="celery",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def _check_external_apis() -> ComponentHealth:
    """Check external API dependencies."""
    # Placeholder - would check GitHub API, etc.
    return ComponentHealth(
        name="external_apis",
        status=HealthStatus.HEALTHY,
        message="No external dependencies configured",
    )

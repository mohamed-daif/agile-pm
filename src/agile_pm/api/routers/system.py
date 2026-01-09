"""System endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import platform

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class MetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_agents: int
    pending_tasks: int
    uptime_seconds: float

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check."""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow(), version="1.0.0")

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """System metrics."""
    return MetricsResponse(
        cpu_percent=0.0, memory_percent=0.0, disk_percent=0.0,
        active_agents=0, pending_tasks=0, uptime_seconds=0.0
    )

@router.get("/info")
async def get_info():
    """System info."""
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture()[0],
    }

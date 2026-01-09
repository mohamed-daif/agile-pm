"""Metrics endpoint."""
from fastapi import APIRouter
from agile_pm.observability.metrics import metrics_response

router = APIRouter(tags=["metrics"])

@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return metrics_response()

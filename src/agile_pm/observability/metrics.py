"""Prometheus metrics."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Request metrics
REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "endpoint"])

# Business metrics
ACTIVE_AGENTS = Gauge("agile_pm_active_agents", "Number of active agents")
PENDING_TASKS = Gauge("agile_pm_pending_tasks", "Number of pending tasks")
TASK_COMPLETIONS = Counter("agile_pm_task_completions_total", "Tasks completed", ["priority"])

# Queue metrics
QUEUE_SIZE = Gauge("agile_pm_queue_size", "Task queue size", ["queue"])
TASK_PROCESSING_TIME = Histogram("agile_pm_task_processing_seconds", "Task processing time")

def metrics_response() -> Response:
    """Generate Prometheus metrics response."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

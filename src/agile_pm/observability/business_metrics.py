"""Business-level metrics for Agile-PM."""
from prometheus_client import Counter, Gauge, Histogram, Summary
from functools import wraps
import time


# Task Metrics
TASKS_CREATED = Counter(
    "agile_pm_tasks_created_total",
    "Total number of tasks created",
    ["priority", "type"],
)

TASKS_COMPLETED = Counter(
    "agile_pm_tasks_completed_total",
    "Total number of tasks completed",
    ["priority", "type"],
)

TASKS_BY_STATUS = Gauge(
    "agile_pm_tasks_by_status",
    "Current tasks by status",
    ["status"],
)

TASK_COMPLETION_TIME = Histogram(
    "agile_pm_task_completion_seconds",
    "Time to complete tasks",
    ["priority"],
    buckets=[300, 900, 3600, 14400, 86400, 604800],  # 5m, 15m, 1h, 4h, 1d, 1w
)


# Agent Metrics
AGENTS_ACTIVE = Gauge(
    "agile_pm_agents_active",
    "Number of active agents",
    ["type"],
)

AGENT_UTILIZATION = Gauge(
    "agile_pm_agent_utilization_ratio",
    "Agent utilization (assigned tasks / capacity)",
    ["agent_id"],
)

AGENT_TASK_ASSIGNMENTS = Counter(
    "agile_pm_agent_task_assignments_total",
    "Total task assignments to agents",
    ["agent_id", "outcome"],  # outcome: success, rejected, timeout
)


# Sprint Metrics
SPRINTS_ACTIVE = Gauge(
    "agile_pm_sprints_active",
    "Number of active sprints",
)

SPRINT_VELOCITY = Gauge(
    "agile_pm_sprint_velocity_points",
    "Sprint velocity in story points",
    ["sprint_id"],
)

SPRINT_BURNDOWN = Gauge(
    "agile_pm_sprint_burndown_points",
    "Remaining story points in sprint",
    ["sprint_id"],
)


# Webhook Metrics
WEBHOOK_SUCCESS_RATE = Gauge(
    "agile_pm_webhook_success_rate",
    "Webhook delivery success rate (rolling 1h)",
)

WEBHOOK_LATENCY = Summary(
    "agile_pm_webhook_latency_seconds",
    "Webhook delivery latency",
    ["endpoint"],
)


# API Usage Metrics
API_USAGE_BY_ENDPOINT = Counter(
    "agile_pm_api_usage_total",
    "API usage by endpoint",
    ["method", "endpoint", "tenant_id"],
)

API_USAGE_BY_USER = Counter(
    "agile_pm_api_usage_by_user_total",
    "API usage by user",
    ["user_id", "endpoint"],
)


# Memory/Cache Metrics
MEMORY_OPERATIONS = Counter(
    "agile_pm_memory_operations_total",
    "Memory store operations",
    ["operation", "namespace"],
)

CACHE_OPERATIONS = Counter(
    "agile_pm_cache_operations_total",
    "Cache operations",
    ["operation", "result"],  # result: hit, miss
)


# Helper functions
def track_task_created(priority: str, task_type: str):
    """Track task creation."""
    TASKS_CREATED.labels(priority=priority, type=task_type).inc()


def track_task_completed(priority: str, task_type: str, duration_seconds: float):
    """Track task completion."""
    TASKS_COMPLETED.labels(priority=priority, type=task_type).inc()
    TASK_COMPLETION_TIME.labels(priority=priority).observe(duration_seconds)


def track_api_usage(method: str, endpoint: str, tenant_id: str, user_id: str = None):
    """Track API usage."""
    API_USAGE_BY_ENDPOINT.labels(
        method=method, endpoint=endpoint, tenant_id=tenant_id
    ).inc()
    if user_id:
        API_USAGE_BY_USER.labels(user_id=user_id, endpoint=endpoint).inc()


def update_task_status_gauge(status_counts: dict):
    """Update task status gauge with current counts."""
    for status, count in status_counts.items():
        TASKS_BY_STATUS.labels(status=status).set(count)


def update_agent_metrics(agent_id: str, utilization: float, active: bool):
    """Update agent metrics."""
    AGENT_UTILIZATION.labels(agent_id=agent_id).set(utilization)


def timed_operation(metric: Histogram, **labels):
    """Decorator to time operations."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                metric.labels(**labels).observe(time.time() - start)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                metric.labels(**labels).observe(time.time() - start)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


import asyncio  # For the decorator

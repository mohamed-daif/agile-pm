"""Queue configuration."""
import os

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

TASK_ROUTES = {
    "agile_pm.queue.tasks.agent_tasks.*": {"queue": "agents"},
    "agile_pm.queue.tasks.webhook_tasks.*": {"queue": "webhooks"},
    "agile_pm.queue.tasks.maintenance_tasks.*": {"queue": "maintenance"},
}

TASK_SERIALIZER = "json"
RESULT_SERIALIZER = "json"
ACCEPT_CONTENT = ["json"]
TIMEZONE = "UTC"
ENABLE_UTC = True

TASK_SOFT_TIME_LIMIT = 300
TASK_TIME_LIMIT = 600

WORKER_PREFETCH_MULTIPLIER = 1
WORKER_CONCURRENCY = 4

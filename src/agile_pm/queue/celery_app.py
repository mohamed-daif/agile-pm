"""Celery application configuration."""
from celery import Celery
from agile_pm.queue import config

celery_app = Celery("agile_pm")

celery_app.conf.update(
    broker_url=config.BROKER_URL,
    result_backend=config.RESULT_BACKEND,
    task_routes=config.TASK_ROUTES,
    task_serializer=config.TASK_SERIALIZER,
    result_serializer=config.RESULT_SERIALIZER,
    accept_content=config.ACCEPT_CONTENT,
    timezone=config.TIMEZONE,
    enable_utc=config.ENABLE_UTC,
    task_soft_time_limit=config.TASK_SOFT_TIME_LIMIT,
    task_time_limit=config.TASK_TIME_LIMIT,
    worker_prefetch_multiplier=config.WORKER_PREFETCH_MULTIPLIER,
    worker_concurrency=config.WORKER_CONCURRENCY,
)

celery_app.autodiscover_tasks([
    "agile_pm.queue.tasks.agent_tasks",
    "agile_pm.queue.tasks.webhook_tasks",
    "agile_pm.queue.tasks.maintenance_tasks",
])

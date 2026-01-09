"""Task queue module."""
from agile_pm.queue.celery_app import celery_app

__all__ = ["celery_app"]

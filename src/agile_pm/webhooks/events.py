"""Webhook events."""
from enum import Enum
from datetime import datetime
import secrets

class EventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    SPRINT_STARTED = "sprint.started"
    SPRINT_COMPLETED = "sprint.completed"
    AGENT_STATUS_CHANGED = "agent.status_changed"

class WebhookEvent:
    def __init__(self, type: EventType, data: dict):
        self.id = secrets.token_urlsafe(16)
        self.type = type
        self.data = data
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }

"""Test webhook events."""
import pytest


class TestWebhookEvent:
    """Test webhook events."""

    def test_event_creation(self):
        """Test creating a webhook event."""
        from agile_pm.webhooks.events import WebhookEvent, EventType
        event = WebhookEvent(
            type=EventType.TASK_CREATED,
            data={"task_id": "123"}
        )
        assert event.type == EventType.TASK_CREATED
        assert event.id is not None
        assert event.timestamp is not None

    def test_event_to_dict(self):
        """Test event serialization."""
        from agile_pm.webhooks.events import WebhookEvent, EventType
        event = WebhookEvent(
            type=EventType.TASK_COMPLETED,
            data={"task_id": "123"}
        )
        data = event.to_dict()
        assert data["type"] == "task.completed"
        assert "timestamp" in data
        assert data["data"]["task_id"] == "123"

    def test_all_event_types(self):
        """Test all event types exist."""
        from agile_pm.webhooks.events import EventType
        expected = [
            "TASK_CREATED", "TASK_UPDATED", "TASK_COMPLETED", "TASK_FAILED",
            "SPRINT_STARTED", "SPRINT_COMPLETED", "AGENT_STATUS_CHANGED"
        ]
        for event_name in expected:
            assert hasattr(EventType, event_name)

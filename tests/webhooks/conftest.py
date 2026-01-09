"""Webhook test fixtures."""
import pytest
from datetime import datetime


@pytest.fixture
def webhook_create_data():
    """Webhook creation data."""
    return {
        "url": "https://example.com/webhook",
        "events": ["task.created", "task.completed"],
        "description": "Test webhook"
    }

@pytest.fixture
def mock_webhook():
    """Mock webhook object."""
    from agile_pm.webhooks.models import Webhook
    return Webhook(
        id="wh-001",
        url="https://example.com/webhook",
        secret="test-secret",
        events=["task.created"],
        active=True,
        created_at=datetime.utcnow()
    )

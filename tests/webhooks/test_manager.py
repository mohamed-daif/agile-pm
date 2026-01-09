"""Test webhook manager."""
import pytest


class TestWebhookManager:
    """Test webhook management."""

    def test_create_webhook(self, webhook_create_data):
        """Test creating a webhook."""
        from agile_pm.webhooks.manager import WebhookManager
        from agile_pm.webhooks.models import WebhookCreate
        manager = WebhookManager()
        webhook = manager.create(WebhookCreate(**webhook_create_data))
        assert webhook.url == webhook_create_data["url"]
        assert webhook.secret is not None

    def test_get_webhook(self, webhook_create_data):
        """Test getting a webhook."""
        from agile_pm.webhooks.manager import WebhookManager
        from agile_pm.webhooks.models import WebhookCreate
        manager = WebhookManager()
        created = manager.create(WebhookCreate(**webhook_create_data))
        retrieved = manager.get(created.id)
        assert retrieved.id == created.id

    def test_list_webhooks(self, webhook_create_data):
        """Test listing webhooks."""
        from agile_pm.webhooks.manager import WebhookManager
        from agile_pm.webhooks.models import WebhookCreate
        manager = WebhookManager()
        manager.create(WebhookCreate(**webhook_create_data))
        webhooks = manager.list()
        assert len(webhooks) == 1

    def test_update_webhook(self, webhook_create_data):
        """Test updating a webhook."""
        from agile_pm.webhooks.manager import WebhookManager
        from agile_pm.webhooks.models import WebhookCreate
        manager = WebhookManager()
        created = manager.create(WebhookCreate(**webhook_create_data))
        updated = manager.update(created.id, active=False)
        assert updated.active is False

    def test_delete_webhook(self, webhook_create_data):
        """Test deleting a webhook."""
        from agile_pm.webhooks.manager import WebhookManager
        from agile_pm.webhooks.models import WebhookCreate
        manager = WebhookManager()
        created = manager.create(WebhookCreate(**webhook_create_data))
        deleted = manager.delete(created.id)
        assert deleted is True
        assert manager.get(created.id) is None

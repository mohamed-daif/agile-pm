"""Test webhook delivery integration."""
import pytest
from unittest.mock import AsyncMock, patch


class TestWebhookDeliveryIntegration:
    """Test webhook delivery end-to-end."""

    @pytest.mark.asyncio
    async def test_create_and_trigger_webhook(self):
        """Test creating and triggering a webhook."""
        from agile_pm.webhooks.manager import WebhookManager
        from agile_pm.webhooks.models import WebhookCreate
        from agile_pm.webhooks.events import EventType
        
        manager = WebhookManager()
        
        # Create webhook
        webhook = manager.create(WebhookCreate(
            url="https://example.com/webhook",
            events=[EventType.TASK_CREATED],
            description="Integration test"
        ))
        
        assert webhook.id is not None
        assert webhook.secret is not None
        
        # Trigger webhook (mock HTTP)
        with patch.object(manager._delivery._client, 'post', new_callable=AsyncMock) as mock:
            mock.return_value.status_code = 200
            results = await manager.trigger(
                EventType.TASK_CREATED,
                {"task_id": "123"}
            )
            assert len(results) == 1
            assert results[0].success is True

    @pytest.mark.asyncio
    async def test_webhook_event_filtering(self):
        """Test webhook event filtering."""
        from agile_pm.webhooks.manager import WebhookManager
        from agile_pm.webhooks.models import WebhookCreate
        from agile_pm.webhooks.events import EventType
        
        manager = WebhookManager()
        
        # Create webhook for only TASK_COMPLETED
        manager.create(WebhookCreate(
            url="https://example.com/webhook",
            events=[EventType.TASK_COMPLETED]
        ))
        
        # Trigger TASK_CREATED (should not deliver)
        with patch.object(manager._delivery._client, 'post', new_callable=AsyncMock) as mock:
            results = await manager.trigger(EventType.TASK_CREATED, {})
            assert len(results) == 0
            mock.assert_not_called()

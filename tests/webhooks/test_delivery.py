"""Test webhook delivery."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestWebhookDelivery:
    """Test webhook delivery system."""

    def test_sign_payload(self):
        """Test HMAC signature generation."""
        from agile_pm.webhooks.delivery import WebhookDelivery
        delivery = WebhookDelivery()
        signature = delivery.sign_payload("secret", b'{"test": true}')
        assert signature.startswith("sha256=")
        assert len(signature) > 10

    @pytest.mark.asyncio
    async def test_deliver_success(self, mock_webhook):
        """Test successful delivery."""
        from agile_pm.webhooks.delivery import WebhookDelivery
        from agile_pm.webhooks.events import WebhookEvent, EventType
        delivery = WebhookDelivery()
        event = WebhookEvent(type=EventType.TASK_CREATED, data={"task_id": "1"})
        
        with patch.object(delivery._client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.status_code = 200
            result = await delivery.deliver(mock_webhook, event)
            assert result.success is True
            assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_deliver_failure_retry(self, mock_webhook):
        """Test delivery retry on failure."""
        from agile_pm.webhooks.delivery import WebhookDelivery
        from agile_pm.webhooks.events import WebhookEvent, EventType
        delivery = WebhookDelivery()
        event = WebhookEvent(type=EventType.TASK_CREATED, data={})
        
        with patch.object(delivery._client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection failed")
            result = await delivery.deliver(mock_webhook, event)
            assert result.success is False
            assert result.attempts == delivery.MAX_RETRIES

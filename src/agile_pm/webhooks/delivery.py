"""Webhook delivery with retry."""
import httpx
import hmac
import hashlib
import json
from datetime import datetime
from agile_pm.webhooks.models import Webhook, DeliveryResult
from agile_pm.webhooks.events import WebhookEvent

class WebhookDelivery:
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 5, 30]
    
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self._client.aclose()
    
    def sign_payload(self, secret: str, payload: bytes) -> str:
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return f"sha256={signature}"
    
    async def deliver(self, webhook: Webhook, event: WebhookEvent) -> DeliveryResult:
        payload = json.dumps(event.to_dict()).encode()
        signature = self.sign_payload(webhook.secret, payload)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event.type.value,
            "X-Webhook-Delivery": event.id
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self._client.post(webhook.url, content=payload, headers=headers)
                return DeliveryResult(
                    webhook_id=webhook.id,
                    event_id=event.id,
                    status_code=response.status_code,
                    success=200 <= response.status_code < 300,
                    attempts=attempt + 1,
                    delivered_at=datetime.utcnow()
                )
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    return DeliveryResult(
                        webhook_id=webhook.id,
                        event_id=event.id,
                        status_code=0,
                        success=False,
                        attempts=attempt + 1,
                        error=str(e),
                        delivered_at=datetime.utcnow()
                    )
        return DeliveryResult(webhook_id=webhook.id, event_id=event.id, status_code=0, success=False, attempts=self.MAX_RETRIES)

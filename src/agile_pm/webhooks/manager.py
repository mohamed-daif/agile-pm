"""Webhook management."""
from typing import Optional
from datetime import datetime
import secrets
from agile_pm.webhooks.models import Webhook, WebhookCreate
from agile_pm.webhooks.delivery import WebhookDelivery
from agile_pm.webhooks.events import WebhookEvent, EventType

class WebhookManager:
    def __init__(self):
        self._webhooks: dict = {}
        self._delivery = WebhookDelivery()
    
    def create(self, webhook: WebhookCreate) -> Webhook:
        webhook_id = secrets.token_urlsafe(16)
        secret = secrets.token_urlsafe(32)
        wh = Webhook(
            id=webhook_id,
            url=webhook.url,
            secret=secret,
            events=webhook.events,
            active=True,
            created_at=datetime.utcnow()
        )
        self._webhooks[webhook_id] = wh
        return wh
    
    def get(self, webhook_id: str) -> Optional[Webhook]:
        return self._webhooks.get(webhook_id)
    
    def list(self) -> list:
        return list(self._webhooks.values())
    
    def update(self, webhook_id: str, **kwargs) -> Optional[Webhook]:
        if webhook_id in self._webhooks:
            wh = self._webhooks[webhook_id]
            for k, v in kwargs.items():
                if hasattr(wh, k):
                    setattr(wh, k, v)
            return wh
        return None
    
    def delete(self, webhook_id: str) -> bool:
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            return True
        return False
    
    async def trigger(self, event_type: EventType, data: dict) -> list:
        results = []
        event = WebhookEvent(type=event_type, data=data)
        for wh in self._webhooks.values():
            if wh.active and event_type in wh.events:
                result = await self._delivery.deliver(wh, event)
                results.append(result)
        return results

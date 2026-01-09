"""Webhook delivery with queue integration."""
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel, HttpUrl

from agile_pm.queue.celery_app import celery_app
from agile_pm.storage.redis import get_redis
from agile_pm.observability.metrics import WEBHOOK_DELIVERIES, WEBHOOK_LATENCY
import structlog

logger = structlog.get_logger(__name__)


class WebhookPayload(BaseModel):
    """Webhook event payload."""
    id: UUID
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class WebhookDelivery(BaseModel):
    """Webhook delivery record."""
    id: UUID
    webhook_id: UUID
    payload: WebhookPayload
    url: HttpUrl
    status: str = "pending"  # pending, delivered, failed, dead
    attempts: int = 0
    max_attempts: int = 5
    next_retry: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    delivered_at: Optional[datetime] = None


class WebhookDeliveryService:
    """Manage webhook deliveries."""
    
    RETRY_DELAYS = [60, 300, 900, 3600, 14400]  # 1m, 5m, 15m, 1h, 4h
    
    async def queue_delivery(
        self,
        webhook_id: UUID,
        url: str,
        event_type: str,
        data: Dict[str, Any],
    ) -> UUID:
        """Queue a webhook for delivery."""
        delivery_id = uuid4()
        
        payload = WebhookPayload(
            id=uuid4(),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
        )
        
        # Queue the delivery task
        deliver_webhook.delay(
            delivery_id=str(delivery_id),
            webhook_id=str(webhook_id),
            url=url,
            payload=payload.model_dump_json(),
        )
        
        logger.info(
            "webhook_queued",
            delivery_id=str(delivery_id),
            webhook_id=str(webhook_id),
            event_type=event_type,
        )
        
        return delivery_id
    
    async def get_delivery_status(self, delivery_id: UUID) -> Optional[Dict[str, Any]]:
        """Get delivery status from Redis."""
        redis = await get_redis()
        key = f"webhook:delivery:{delivery_id}"
        data = await redis.get(key)
        if data:
            import json
            return json.loads(data)
        return None


@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    autoretry_for=(httpx.HTTPError,),
    retry_backoff=True,
    retry_backoff_max=14400,
)
def deliver_webhook(
    self,
    delivery_id: str,
    webhook_id: str,
    url: str,
    payload: str,
):
    """Celery task to deliver webhook."""
    import json
    import time
    
    start_time = time.time()
    attempt = self.request.retries + 1
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                url,
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-ID": webhook_id,
                    "X-Delivery-ID": delivery_id,
                    "X-Delivery-Attempt": str(attempt),
                    "User-Agent": "Agile-PM-Webhook/1.0",
                },
            )
            response.raise_for_status()
        
        duration = time.time() - start_time
        WEBHOOK_DELIVERIES.labels(status="success").inc()
        WEBHOOK_LATENCY.observe(duration)
        
        # Store success status
        _store_delivery_status(
            delivery_id, "delivered", attempt, None, duration
        )
        
        logger.info(
            "webhook_delivered",
            delivery_id=delivery_id,
            webhook_id=webhook_id,
            attempt=attempt,
            duration=duration,
        )
        
    except httpx.HTTPError as e:
        duration = time.time() - start_time
        error_msg = str(e)
        
        if attempt >= 5:
            # Move to dead letter queue
            WEBHOOK_DELIVERIES.labels(status="dead").inc()
            _store_delivery_status(
                delivery_id, "dead", attempt, error_msg, duration
            )
            _move_to_dead_letter(delivery_id, webhook_id, url, payload, error_msg)
            logger.error(
                "webhook_dead",
                delivery_id=delivery_id,
                webhook_id=webhook_id,
                error=error_msg,
            )
        else:
            WEBHOOK_DELIVERIES.labels(status="retry").inc()
            _store_delivery_status(
                delivery_id, "retrying", attempt, error_msg, duration
            )
            raise  # Let Celery retry


def _store_delivery_status(
    delivery_id: str,
    status: str,
    attempts: int,
    error: Optional[str],
    duration: float,
):
    """Store delivery status in Redis."""
    import json
    from agile_pm.storage.redis import get_sync_redis
    
    redis = get_sync_redis()
    key = f"webhook:delivery:{delivery_id}"
    data = {
        "status": status,
        "attempts": attempts,
        "last_error": error,
        "duration": duration,
        "updated_at": datetime.utcnow().isoformat(),
    }
    redis.setex(key, 86400 * 7, json.dumps(data))  # 7 day TTL


def _move_to_dead_letter(
    delivery_id: str,
    webhook_id: str,
    url: str,
    payload: str,
    error: str,
):
    """Move failed delivery to dead letter queue."""
    import json
    from agile_pm.storage.redis import get_sync_redis
    
    redis = get_sync_redis()
    data = {
        "delivery_id": delivery_id,
        "webhook_id": webhook_id,
        "url": url,
        "payload": json.loads(payload),
        "error": error,
        "failed_at": datetime.utcnow().isoformat(),
    }
    redis.lpush("webhook:dead_letter", json.dumps(data))

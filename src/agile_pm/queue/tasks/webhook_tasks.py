"""Webhook delivery tasks."""
import logging
import httpx
from agile_pm.queue.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=5, default_retry_delay=30)
def deliver_webhook(self, webhook_id: str, url: str, payload: dict, headers: dict = None) -> dict:
    """Deliver a webhook payload."""
    logger.info(f"Delivering webhook {webhook_id} to {url}")
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, json=payload, headers=headers or {})
            response.raise_for_status()
        
        return {
            "webhook_id": webhook_id,
            "status": "delivered",
            "status_code": response.status_code,
        }
    except httpx.HTTPError as e:
        logger.warning(f"Webhook delivery failed: {e}")
        raise self.retry(exc=e)


@celery_app.task
def batch_deliver_webhooks(webhooks: list[dict]) -> list[dict]:
    """Deliver multiple webhooks."""
    results = []
    for wh in webhooks:
        result = deliver_webhook.delay(wh["id"], wh["url"], wh["payload"], wh.get("headers"))
        results.append({"task_id": result.id, "webhook_id": wh["id"]})
    return results

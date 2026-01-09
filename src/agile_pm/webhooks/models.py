"""Webhook models."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from agile_pm.webhooks.events import EventType

class WebhookCreate(BaseModel):
    url: str
    events: list
    description: str = ""

class Webhook(BaseModel):
    id: str
    url: str
    secret: str
    events: list
    active: bool = True
    description: str = ""
    created_at: datetime
    
    class Config:
        from_attributes = True

class DeliveryResult(BaseModel):
    webhook_id: str
    event_id: str
    status_code: int
    success: bool
    attempts: int = 1
    error: Optional[str] = None
    delivered_at: Optional[datetime] = None

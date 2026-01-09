"""Session storage using Redis."""
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional
from pydantic import BaseModel
from agile_pm.storage.redis import get_redis


class SessionData(BaseModel):
    user_id: str
    roles: list[str] = []
    data: dict = {}
    created_at: datetime
    expires_at: datetime


class SessionStore:
    """Redis-backed session storage."""
    
    def __init__(self, prefix: str = "session", ttl: int = 3600):
        self.prefix = prefix
        self.ttl = ttl
    
    def _key(self, session_id: str) -> str:
        return f"{self.prefix}:{session_id}"
    
    async def create(self, user_id: str, roles: list[str] = None, data: dict = None) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        redis = get_redis()
        
        session = SessionData(
            user_id=user_id,
            roles=roles or [],
            data=data or {},
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=self.ttl)
        )
        
        await redis.set_json(self._key(session_id), session.model_dump(mode="json"), self.ttl)
        return session_id
    
    async def get(self, session_id: str) -> Optional[SessionData]:
        """Get session data."""
        redis = get_redis()
        data = await redis.get_json(self._key(session_id))
        if data:
            return SessionData(**data)
        return None
    
    async def update(self, session_id: str, data: dict) -> bool:
        """Update session data."""
        session = await self.get(session_id)
        if not session:
            return False
        
        session.data.update(data)
        redis = get_redis()
        remaining_ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
        if remaining_ttl > 0:
            await redis.set_json(self._key(session_id), session.model_dump(mode="json"), remaining_ttl)
        return True
    
    async def delete(self, session_id: str) -> None:
        """Delete a session."""
        redis = get_redis()
        await redis.delete(self._key(session_id))
    
    async def refresh(self, session_id: str) -> bool:
        """Refresh session TTL."""
        session = await self.get(session_id)
        if not session:
            return False
        
        session.expires_at = datetime.utcnow() + timedelta(seconds=self.ttl)
        redis = get_redis()
        await redis.set_json(self._key(session_id), session.model_dump(mode="json"), self.ttl)
        return True

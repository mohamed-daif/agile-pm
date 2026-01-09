"""API Key management."""
import secrets
import hashlib
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class APIKey(BaseModel):
    id: str
    name: str
    key_hash: str
    prefix: str
    roles: list = []
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

class APIKeyManager:
    def __init__(self):
        self._keys: dict = {}
    
    @staticmethod
    def generate_key() -> tuple:
        key = secrets.token_urlsafe(32)
        prefix = key[:8]
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, prefix, key_hash
    
    def create_key(self, name: str, roles: list = None, expires_at: datetime = None) -> tuple:
        key, prefix, key_hash = self.generate_key()
        api_key = APIKey(
            id=secrets.token_urlsafe(8),
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            roles=roles or ["viewer"],
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        self._keys[key_hash] = api_key
        return key, api_key
    
    def verify_key(self, key: str) -> Optional[APIKey]:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        api_key = self._keys.get(key_hash)
        if api_key:
            if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                return None
            api_key.last_used_at = datetime.utcnow()
            return api_key
        return None
    
    def revoke_key(self, key_id: str) -> bool:
        for key_hash, api_key in list(self._keys.items()):
            if api_key.id == key_id:
                del self._keys[key_hash]
                return True
        return False

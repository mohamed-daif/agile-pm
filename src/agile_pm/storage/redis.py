"""Redis client wrapper."""
import json
from typing import Any, Optional
import redis.asyncio as redis


class RedisClient:
    """Async Redis client."""
    
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self.url = url
        self._client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        self._client = redis.from_url(self.url, decode_responses=True)
    
    async def close(self) -> None:
        if self._client:
            await self._client.close()
    
    @property
    def client(self) -> redis.Redis:
        if not self._client:
            raise RuntimeError("Redis not connected")
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)
    
    async def delete(self, key: str) -> None:
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0
    
    async def get_json(self, key: str) -> Optional[Any]:
        data = await self.get(key)
        return json.loads(data) if data else None
    
    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        await self.set(key, json.dumps(value), ttl)
    
    async def incr(self, key: str) -> int:
        return await self.client.incr(key)
    
    async def expire(self, key: str, ttl: int) -> None:
        await self.client.expire(key, ttl)
    
    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception:
            return False


_redis: Optional[RedisClient] = None

def init_redis(url: str = "redis://localhost:6379/0") -> RedisClient:
    global _redis
    _redis = RedisClient(url)
    return _redis

def get_redis() -> RedisClient:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis

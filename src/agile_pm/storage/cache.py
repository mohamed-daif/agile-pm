"""Cache decorator and utilities."""
import functools
import hashlib
import json
from typing import Any, Callable, Optional
from agile_pm.storage.redis import get_redis


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(prefix: str, ttl: int = 300):
    """Cache decorator with TTL."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis = get_redis()
            key = f"{prefix}:{cache_key(*args[1:], **kwargs)}"  # Skip self
            
            cached_value = await redis.get_json(key)
            if cached_value is not None:
                return cached_value
            
            result = await func(*args, **kwargs)
            if result is not None:
                await redis.set_json(key, result, ttl)
            return result
        return wrapper
    return decorator


async def invalidate_cache(prefix: str, *args, **kwargs) -> None:
    """Invalidate a specific cache entry."""
    redis = get_redis()
    key = f"{prefix}:{cache_key(*args, **kwargs)}"
    await redis.delete(key)


async def invalidate_prefix(prefix: str) -> None:
    """Invalidate all cache entries with prefix."""
    redis = get_redis()
    async for key in redis.client.scan_iter(f"{prefix}:*"):
        await redis.delete(key)

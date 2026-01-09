"""Memory persistence layer with PostgreSQL and Redis."""
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from agile_pm.storage.database import get_session
from agile_pm.storage.models import Memory
from agile_pm.storage.redis import get_redis
from agile_pm.observability.metrics import MEMORY_OPS
import structlog

logger = structlog.get_logger(__name__)


class MemoryStore(ABC):
    """Abstract memory store interface."""
    
    @abstractmethod
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get a value from memory."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        ttl: Optional[int] = None,
    ) -> None:
        """Set a value in memory."""
        pass
    
    @abstractmethod
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete a value from memory."""
        pass
    
    @abstractmethod
    async def list_keys(self, namespace: str = "default") -> List[str]:
        """List all keys in a namespace."""
        pass


class PostgresMemoryStore(MemoryStore):
    """PostgreSQL-backed memory store for persistence."""
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from PostgreSQL."""
        async with get_session() as session:
            from sqlalchemy import select
            stmt = select(Memory).where(
                Memory.key == key,
                Memory.namespace == namespace,
            )
            result = await session.execute(stmt)
            memory = result.scalar_one_or_none()
            
            if memory and memory.expires_at and memory.expires_at < datetime.utcnow():
                await self.delete(key, namespace)
                return None
            
            MEMORY_OPS.labels(operation="get", store="postgres").inc()
            return memory.value if memory else None
    
    async def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in PostgreSQL."""
        async with get_session() as session:
            from sqlalchemy import select
            
            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            stmt = select(Memory).where(
                Memory.key == key,
                Memory.namespace == namespace,
            )
            result = await session.execute(stmt)
            memory = result.scalar_one_or_none()
            
            if memory:
                memory.value = value
                memory.expires_at = expires_at
                memory.updated_at = datetime.utcnow()
            else:
                memory = Memory(
                    id=uuid4(),
                    key=key,
                    namespace=namespace,
                    value=value,
                    expires_at=expires_at,
                )
                session.add(memory)
            
            await session.commit()
            MEMORY_OPS.labels(operation="set", store="postgres").inc()
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from PostgreSQL."""
        async with get_session() as session:
            from sqlalchemy import delete as sql_delete
            stmt = sql_delete(Memory).where(
                Memory.key == key,
                Memory.namespace == namespace,
            )
            result = await session.execute(stmt)
            await session.commit()
            MEMORY_OPS.labels(operation="delete", store="postgres").inc()
            return result.rowcount > 0
    
    async def list_keys(self, namespace: str = "default") -> List[str]:
        """List keys in namespace."""
        async with get_session() as session:
            from sqlalchemy import select
            stmt = select(Memory.key).where(Memory.namespace == namespace)
            result = await session.execute(stmt)
            return [row[0] for row in result.fetchall()]


class CachedMemoryStore(MemoryStore):
    """Memory store with Redis cache and PostgreSQL persistence."""
    
    def __init__(self, cache_ttl: int = 300):
        self.postgres = PostgresMemoryStore()
        self.cache_ttl = cache_ttl
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get with cache-aside pattern."""
        import json
        redis = await get_redis()
        cache_key = f"memory:{namespace}:{key}"
        
        # Check cache first
        cached = await redis.get(cache_key)
        if cached:
            MEMORY_OPS.labels(operation="get", store="cache_hit").inc()
            return json.loads(cached)
        
        # Fall back to PostgreSQL
        value = await self.postgres.get(key, namespace)
        if value is not None:
            # Populate cache
            await redis.setex(cache_key, self.cache_ttl, json.dumps(value))
            MEMORY_OPS.labels(operation="get", store="cache_miss").inc()
        
        return value
    
    async def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        ttl: Optional[int] = None,
    ) -> None:
        """Set in both cache and database."""
        import json
        redis = await get_redis()
        cache_key = f"memory:{namespace}:{key}"
        
        # Write to PostgreSQL
        await self.postgres.set(key, value, namespace, ttl)
        
        # Update cache
        cache_ttl = min(ttl, self.cache_ttl) if ttl else self.cache_ttl
        await redis.setex(cache_key, cache_ttl, json.dumps(value))
        MEMORY_OPS.labels(operation="set", store="cached").inc()
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete from both cache and database."""
        redis = await get_redis()
        cache_key = f"memory:{namespace}:{key}"
        
        # Delete from cache
        await redis.delete(cache_key)
        
        # Delete from PostgreSQL
        result = await self.postgres.delete(key, namespace)
        MEMORY_OPS.labels(operation="delete", store="cached").inc()
        return result
    
    async def list_keys(self, namespace: str = "default") -> List[str]:
        """List keys from PostgreSQL."""
        return await self.postgres.list_keys(namespace)


# Default memory store instance
_memory_store: Optional[CachedMemoryStore] = None


def get_memory_store() -> CachedMemoryStore:
    """Get the global memory store."""
    global _memory_store
    if not _memory_store:
        _memory_store = CachedMemoryStore()
    return _memory_store

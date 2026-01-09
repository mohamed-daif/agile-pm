"""PostgreSQL persistence for memory storage.

Provides persistent storage for all memory types.
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional, TypeVar, Generic
from uuid import uuid4

from pydantic import BaseModel, Field
import asyncpg


T = TypeVar("T")


class MemoryRecord(BaseModel):
    """Database record for memory storage."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    memory_type: str = Field(description="Type: buffer, summary, entity, vector")
    data: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryPersistence(ABC):
    """Abstract base class for memory persistence."""

    @abstractmethod
    async def save(self, record: MemoryRecord) -> str:
        """Save a memory record."""
        pass

    @abstractmethod
    async def load(self, record_id: str) -> Optional[MemoryRecord]:
        """Load a memory record by ID."""
        pass

    @abstractmethod
    async def load_by_session(
        self,
        session_id: str,
        memory_type: Optional[str] = None,
    ) -> list[MemoryRecord]:
        """Load all records for a session."""
        pass

    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """Delete a memory record."""
        pass

    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete all expired records."""
        pass


class PostgresMemoryStore(MemoryPersistence):
    """PostgreSQL-backed memory persistence.
    
    Provides durable storage for:
    - Buffer memory (conversation history)
    - Summary memory (session summaries)
    - Entity memory (extracted entities)
    - Vector store metadata
    """

    # SQL for table creation
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS agile_pm_memory (
        id VARCHAR(64) PRIMARY KEY,
        session_id VARCHAR(64) NOT NULL,
        memory_type VARCHAR(32) NOT NULL,
        data JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        expires_at TIMESTAMP WITH TIME ZONE,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    
    CREATE INDEX IF NOT EXISTS idx_memory_session 
        ON agile_pm_memory(session_id);
    CREATE INDEX IF NOT EXISTS idx_memory_type 
        ON agile_pm_memory(memory_type);
    CREATE INDEX IF NOT EXISTS idx_memory_expires 
        ON agile_pm_memory(expires_at) 
        WHERE expires_at IS NOT NULL;
    """

    def __init__(self, connection_string: str):
        """Initialize PostgreSQL store.
        
        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Establish database connection pool."""
        self._pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=2,
            max_size=10,
        )
        
        # Create table if not exists
        async with self._pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE_SQL)
    
    async def disconnect(self) -> None:
        """Close database connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    async def save(self, record: MemoryRecord) -> str:
        """Save a memory record.
        
        Args:
            record: Memory record to save
            
        Returns:
            Record ID
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO agile_pm_memory 
                    (id, session_id, memory_type, data, created_at, 
                     updated_at, expires_at, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (id) DO UPDATE SET
                    data = $4,
                    updated_at = $6,
                    expires_at = $7,
                    metadata = $8
                """,
                record.id,
                record.session_id,
                record.memory_type,
                json.dumps(record.data),
                record.created_at,
                record.updated_at,
                record.expires_at,
                json.dumps(record.metadata),
            )
        
        return record.id
    
    async def load(self, record_id: str) -> Optional[MemoryRecord]:
        """Load a memory record by ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            MemoryRecord if found
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, session_id, memory_type, data, created_at,
                       updated_at, expires_at, metadata
                FROM agile_pm_memory
                WHERE id = $1 AND (expires_at IS NULL OR expires_at > NOW())
                """,
                record_id,
            )
        
        if row:
            return MemoryRecord(
                id=row["id"],
                session_id=row["session_id"],
                memory_type=row["memory_type"],
                data=json.loads(row["data"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                expires_at=row["expires_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            )
        
        return None
    
    async def load_by_session(
        self,
        session_id: str,
        memory_type: Optional[str] = None,
    ) -> list[MemoryRecord]:
        """Load all records for a session.
        
        Args:
            session_id: Session ID
            memory_type: Optional type filter
            
        Returns:
            List of memory records
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        async with self._pool.acquire() as conn:
            if memory_type:
                rows = await conn.fetch(
                    """
                    SELECT id, session_id, memory_type, data, created_at,
                           updated_at, expires_at, metadata
                    FROM agile_pm_memory
                    WHERE session_id = $1 
                      AND memory_type = $2
                      AND (expires_at IS NULL OR expires_at > NOW())
                    ORDER BY created_at
                    """,
                    session_id,
                    memory_type,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT id, session_id, memory_type, data, created_at,
                           updated_at, expires_at, metadata
                    FROM agile_pm_memory
                    WHERE session_id = $1 
                      AND (expires_at IS NULL OR expires_at > NOW())
                    ORDER BY created_at
                    """,
                    session_id,
                )
        
        return [
            MemoryRecord(
                id=row["id"],
                session_id=row["session_id"],
                memory_type=row["memory_type"],
                data=json.loads(row["data"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                expires_at=row["expires_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            )
            for row in rows
        ]
    
    async def delete(self, record_id: str) -> bool:
        """Delete a memory record.
        
        Args:
            record_id: Record ID
            
        Returns:
            True if deleted
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM agile_pm_memory WHERE id = $1",
                record_id,
            )
        
        return result == "DELETE 1"
    
    async def delete_by_session(self, session_id: str) -> int:
        """Delete all records for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Number of records deleted
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM agile_pm_memory WHERE session_id = $1",
                session_id,
            )
        
        return int(result.split()[-1])
    
    async def delete_expired(self) -> int:
        """Delete all expired records.
        
        Returns:
            Number of records deleted
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM agile_pm_memory 
                WHERE expires_at IS NOT NULL AND expires_at < NOW()
                """
            )
        
        return int(result.split()[-1])
    
    async def set_expiration(
        self,
        record_id: str,
        ttl_seconds: int,
    ) -> bool:
        """Set expiration time for a record.
        
        Args:
            record_id: Record ID
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            True if updated
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE agile_pm_memory 
                SET expires_at = $2, updated_at = NOW()
                WHERE id = $1
                """,
                record_id,
                expires_at,
            )
        
        return result == "UPDATE 1"
    
    async def get_session_stats(self, session_id: str) -> dict[str, Any]:
        """Get statistics for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict with session statistics
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN memory_type = 'buffer' THEN 1 END) as buffer_count,
                    COUNT(CASE WHEN memory_type = 'summary' THEN 1 END) as summary_count,
                    COUNT(CASE WHEN memory_type = 'entity' THEN 1 END) as entity_count,
                    MIN(created_at) as first_record,
                    MAX(updated_at) as last_updated
                FROM agile_pm_memory
                WHERE session_id = $1
                  AND (expires_at IS NULL OR expires_at > NOW())
                """,
                session_id,
            )
        
        return {
            "session_id": session_id,
            "total_records": row["total_records"],
            "buffer_count": row["buffer_count"],
            "summary_count": row["summary_count"],
            "entity_count": row["entity_count"],
            "first_record": row["first_record"].isoformat() if row["first_record"] else None,
            "last_updated": row["last_updated"].isoformat() if row["last_updated"] else None,
        }

"""Memory manager implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime

from pydantic import BaseModel

from agile_pm.core.config import MemoryConfig


class Memory(BaseModel):
    """A single memory entry."""

    key: str
    value: Any
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = {}


class MemoryManager:
    """Manages persistent memory for Agile-PM agents."""

    def __init__(self, config: MemoryConfig) -> None:
        """Initialize memory manager.
        
        Args:
            config: Memory configuration
        """
        self.config = config
        self._store: dict[str, Memory] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure the memory store is initialized."""
        if self._initialized:
            return
        
        if self.config.backend == "sqlite":
            self._init_sqlite()
        # Future: Add postgresql, redis backends
        
        self._initialized = True

    def _init_sqlite(self) -> None:
        """Initialize SQLite backend."""
        import sqlite3
        
        db_path = Path(self.config.path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store(self, key: str, value: Any, metadata: dict[str, Any] | None = None) -> Memory:
        """Store a memory.
        
        Args:
            key: Unique key for the memory
            value: Value to store
            metadata: Optional metadata
            
        Returns:
            The stored memory
        """
        self._ensure_initialized()
        
        now = datetime.utcnow()
        existing = self._store.get(key)
        
        memory = Memory(
            key=key,
            value=value,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            metadata=metadata or {},
        )
        
        self._store[key] = memory
        self._persist(memory)
        
        return memory

    def recall(self, key: str) -> Memory | None:
        """Recall a memory.
        
        Args:
            key: Key to recall
            
        Returns:
            The memory if found, None otherwise
        """
        self._ensure_initialized()
        return self._store.get(key) or self._load(key)

    def forget(self, key: str) -> bool:
        """Forget a memory.
        
        Args:
            key: Key to forget
            
        Returns:
            True if memory was forgotten, False if not found
        """
        self._ensure_initialized()
        
        if key in self._store:
            del self._store[key]
            self._delete(key)
            return True
        return False

    def list_memories(self, prefix: str | None = None) -> list[str]:
        """List all memory keys.
        
        Args:
            prefix: Optional prefix filter
            
        Returns:
            List of memory keys
        """
        self._ensure_initialized()
        
        keys = list(self._store.keys())
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        return keys

    def _persist(self, memory: Memory) -> None:
        """Persist memory to backend."""
        import json
        import sqlite3
        
        if self.config.backend == "sqlite":
            conn = sqlite3.connect(self.config.path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memories (key, value, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                memory.key,
                json.dumps(memory.value),
                memory.created_at.isoformat(),
                memory.updated_at.isoformat(),
                json.dumps(memory.metadata),
            ))
            conn.commit()
            conn.close()

    def _load(self, key: str) -> Memory | None:
        """Load memory from backend."""
        import json
        import sqlite3
        
        if self.config.backend == "sqlite":
            conn = sqlite3.connect(self.config.path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                memory = Memory(
                    key=row[0],
                    value=json.loads(row[1]),
                    created_at=datetime.fromisoformat(row[2]),
                    updated_at=datetime.fromisoformat(row[3]),
                    metadata=json.loads(row[4]),
                )
                self._store[key] = memory
                return memory
        
        return None

    def _delete(self, key: str) -> None:
        """Delete memory from backend."""
        import sqlite3
        
        if self.config.backend == "sqlite":
            conn = sqlite3.connect(self.config.path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE key = ?", (key,))
            conn.commit()
            conn.close()

"""Tests for Agile-PM memory management."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from agile_pm.memory.manager import MemoryManager, Memory
from agile_pm.core.config import MemoryConfig


class TestMemoryManager:
    """Tests for MemoryManager."""

    def test_store_and_recall(self):
        """Test storing and recalling memories."""
        with TemporaryDirectory() as tmpdir:
            config = MemoryConfig(path=str(Path(tmpdir) / "memory.db"))
            manager = MemoryManager(config)
            
            # Store
            memory = manager.store("test-key", {"value": 42})
            assert memory.key == "test-key"
            assert memory.value == {"value": 42}
            
            # Recall
            recalled = manager.recall("test-key")
            assert recalled is not None
            assert recalled.value == {"value": 42}

    def test_recall_nonexistent(self):
        """Test recalling nonexistent memory."""
        with TemporaryDirectory() as tmpdir:
            config = MemoryConfig(path=str(Path(tmpdir) / "memory.db"))
            manager = MemoryManager(config)
            
            recalled = manager.recall("nonexistent")
            assert recalled is None

    def test_forget(self):
        """Test forgetting memories."""
        with TemporaryDirectory() as tmpdir:
            config = MemoryConfig(path=str(Path(tmpdir) / "memory.db"))
            manager = MemoryManager(config)
            
            manager.store("forget-me", "value")
            assert manager.recall("forget-me") is not None
            
            result = manager.forget("forget-me")
            assert result is True
            assert manager.recall("forget-me") is None

    def test_list_memories(self):
        """Test listing memory keys."""
        with TemporaryDirectory() as tmpdir:
            config = MemoryConfig(path=str(Path(tmpdir) / "memory.db"))
            manager = MemoryManager(config)
            
            manager.store("project:test1", "value1")
            manager.store("project:test2", "value2")
            manager.store("other:test3", "value3")
            
            all_keys = manager.list_memories()
            assert len(all_keys) == 3
            
            project_keys = manager.list_memories(prefix="project:")
            assert len(project_keys) == 2
            assert all(k.startswith("project:") for k in project_keys)

    def test_update_memory(self):
        """Test updating existing memory."""
        with TemporaryDirectory() as tmpdir:
            config = MemoryConfig(path=str(Path(tmpdir) / "memory.db"))
            manager = MemoryManager(config)
            
            memory1 = manager.store("update-me", "original")
            memory2 = manager.store("update-me", "updated")
            
            assert memory2.value == "updated"
            assert memory2.created_at == memory1.created_at
            assert memory2.updated_at > memory1.updated_at

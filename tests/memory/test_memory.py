"""Tests for memory persistence module."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from agile_pm.memory.buffer import BufferMemory, BufferConfig
from agile_pm.memory.persistence import MemoryRecord


class TestBufferMemory:
    """Tests for BufferMemory."""

    def test_create_buffer_memory(self):
        """Test creating buffer memory."""
        memory = BufferMemory()
        assert memory.session_id is not None
        assert memory.message_count == 0
        assert memory.config.max_messages == 100

    def test_create_with_config(self):
        """Test creating with custom config."""
        config = BufferConfig(max_messages=50, memory_key="history")
        memory = BufferMemory(config=config)
        assert memory.config.max_messages == 50
        assert memory.config.memory_key == "history"

    def test_add_user_message(self):
        """Test adding user message."""
        memory = BufferMemory()
        memory.add_user_message("Hello")
        assert memory.message_count == 1
        # Check message content directly since buffer may return message objects
        assert any("Hello" in str(msg.content) for msg in memory.messages)

    def test_add_ai_message(self):
        """Test adding AI message."""
        memory = BufferMemory()
        memory.add_ai_message("Hi there!")
        assert memory.message_count == 1
        assert any("Hi there!" in str(msg.content) for msg in memory.messages)

    def test_conversation_flow(self):
        """Test full conversation flow."""
        memory = BufferMemory()
        memory.add_user_message("What is Python?")
        memory.add_ai_message("Python is a programming language.")
        memory.add_user_message("Tell me more")
        memory.add_ai_message("It's known for its simplicity.")
        
        assert memory.message_count == 4
        all_content = " ".join(str(msg.content) for msg in memory.messages)
        assert "Python" in all_content
        assert "programming language" in all_content

    def test_trim_messages(self):
        """Test message trimming when exceeding max."""
        config = BufferConfig(max_messages=5)
        memory = BufferMemory(config=config)
        
        # Add more than max messages
        for i in range(10):
            memory.add_user_message(f"Message {i}")
        
        assert memory.message_count == 5
        # Should keep most recent messages
        all_content = " ".join(str(msg.content) for msg in memory.messages)
        assert "Message 9" in all_content
        assert "Message 0" not in all_content

    def test_clear(self):
        """Test clearing memory."""
        memory = BufferMemory()
        memory.add_user_message("Test")
        memory.add_ai_message("Response")
        memory.clear()
        
        assert memory.message_count == 0

    def test_serialization(self):
        """Test to_dict and from_dict."""
        memory = BufferMemory(session_id="test-session")
        memory.add_user_message("Hello")
        memory.add_ai_message("Hi!")
        
        data = memory.to_dict()
        assert data["session_id"] == "test-session"
        assert len(data["messages"]) == 2
        
        restored = BufferMemory.from_dict(data)
        assert restored.session_id == "test-session"
        assert restored.message_count == 2

    def test_load_memory_variables(self):
        """Test loading memory variables for chain."""
        memory = BufferMemory()
        memory.add_user_message("Test input")
        memory.add_ai_message("Test output")
        
        variables = memory.load_memory_variables({})
        assert "chat_history" in variables

    def test_save_context(self):
        """Test save_context for chain integration."""
        memory = BufferMemory()
        memory.save_context(
            {"input": "What is AI?"},
            {"output": "AI is artificial intelligence."}
        )
        
        assert memory.message_count == 2


class TestMemoryRecord:
    """Tests for MemoryRecord."""

    def test_create_record(self):
        """Test creating memory record."""
        record = MemoryRecord(
            session_id="test-session",
            memory_type="buffer",
            data={"test": "data"},
        )
        
        assert record.id is not None
        assert record.session_id == "test-session"
        assert record.memory_type == "buffer"
        assert record.data == {"test": "data"}
        assert record.created_at is not None
        assert record.expires_at is None

    def test_record_with_expiration(self):
        """Test record with expiration."""
        expires = datetime.utcnow() + timedelta(hours=24)
        record = MemoryRecord(
            session_id="test-session",
            memory_type="buffer",
            data={},
            expires_at=expires,
        )
        
        assert record.expires_at == expires

    def test_record_metadata(self):
        """Test record metadata."""
        record = MemoryRecord(
            session_id="test-session",
            memory_type="buffer",
            data={},
            metadata={"role": "pm", "task": "planning"},
        )
        
        assert record.metadata["role"] == "pm"
        assert record.metadata["task"] == "planning"


# Integration tests (require database)
@pytest.mark.integration
@pytest.mark.skipif(
    True,  # Skip by default - enable with: pytest -m integration --run-integration
    reason="Integration tests require PostgreSQL database running"
)
class TestPostgresMemoryStore:
    """Integration tests for PostgreSQL store.
    
    These tests require a running PostgreSQL instance.
    Run with: pytest -m integration --run-integration
    """

    @pytest.fixture
    async def store(self):
        """Create test store."""
        from agile_pm.memory.persistence import PostgresMemoryStore
        
        # Use test database
        connection_string = "postgresql://test:test@localhost:5432/agile_pm_test"
        store = PostgresMemoryStore(connection_string)
        await store.connect()
        yield store
        await store.disconnect()

    @pytest.mark.asyncio
    async def test_save_and_load(self, store):
        """Test save and load operations."""
        record = MemoryRecord(
            session_id="test-session",
            memory_type="buffer",
            data={"messages": [{"role": "user", "content": "Hello"}]},
        )
        
        record_id = await store.save(record)
        assert record_id == record.id
        
        loaded = await store.load(record_id)
        assert loaded is not None
        assert loaded.session_id == "test-session"
        assert loaded.data == record.data

    @pytest.mark.asyncio
    async def test_load_by_session(self, store):
        """Test loading all records for a session."""
        session_id = str(uuid4())
        
        # Save multiple records
        for memory_type in ["buffer", "summary", "entity"]:
            record = MemoryRecord(
                session_id=session_id,
                memory_type=memory_type,
                data={},
            )
            await store.save(record)
        
        records = await store.load_by_session(session_id)
        assert len(records) == 3

    @pytest.mark.asyncio
    async def test_delete_expired(self, store):
        """Test deleting expired records."""
        # Create expired record
        expired_record = MemoryRecord(
            session_id="expired-session",
            memory_type="buffer",
            data={},
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        await store.save(expired_record)
        
        deleted = await store.delete_expired()
        assert deleted >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

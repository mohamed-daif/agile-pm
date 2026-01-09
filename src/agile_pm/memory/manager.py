"""Memory manager for orchestrating all memory types.

Provides unified interface for memory operations.
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, Field

from .buffer import BufferMemory, BufferConfig
from .summary import SummaryMemory, SummaryConfig
from .entity import EntityMemory, EntityConfig
from .vector_store import VectorStoreMemory, VectorStoreConfig
from .persistence import MemoryPersistence, MemoryRecord


class MemoryManagerConfig(BaseModel):
    """Configuration for memory manager."""

    enable_buffer: bool = Field(default=True)
    enable_summary: bool = Field(default=True)
    enable_entity: bool = Field(default=True)
    enable_vector: bool = Field(default=False)  # Requires embeddings
    
    buffer_config: BufferConfig = Field(default_factory=BufferConfig)
    summary_config: SummaryConfig = Field(default_factory=SummaryConfig)
    entity_config: EntityConfig = Field(default_factory=EntityConfig)
    vector_config: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    
    auto_save_interval: int = Field(default=60, description="Seconds between auto-saves")
    session_ttl_hours: int = Field(default=24, description="Session expiration hours")


class MemoryManager:
    """Unified memory manager for Agile-PM agents.
    
    Orchestrates:
    - BufferMemory: Short-term conversation buffer
    - SummaryMemory: Long-term summarization
    - EntityMemory: Entity extraction and tracking
    - VectorStoreMemory: Semantic retrieval
    - Persistence: PostgreSQL storage
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        llm: Optional[BaseChatModel] = None,
        embeddings: Optional[Embeddings] = None,
        vector_store: Optional[VectorStore] = None,
        persistence: Optional[MemoryPersistence] = None,
        config: Optional[MemoryManagerConfig] = None,
    ):
        """Initialize memory manager.
        
        Args:
            session_id: Session identifier (auto-generated if not provided)
            llm: Language model for summary/entity extraction
            embeddings: Embedding model for vector store
            vector_store: Vector store instance
            persistence: Persistence backend
            config: Manager configuration
        """
        self.session_id = session_id or str(uuid4())
        self.config = config or MemoryManagerConfig()
        self.llm = llm
        self.embeddings = embeddings
        self.persistence = persistence
        self.created_at = datetime.utcnow()
        self.last_saved_at: Optional[datetime] = None
        
        # Initialize memory components
        self._buffer: Optional[BufferMemory] = None
        self._summary: Optional[SummaryMemory] = None
        self._entity: Optional[EntityMemory] = None
        self._vector: Optional[VectorStoreMemory] = None
        
        # Initialize enabled components
        if self.config.enable_buffer:
            self._buffer = BufferMemory(
                session_id=self.session_id,
                config=self.config.buffer_config,
            )
        
        if self.config.enable_summary and llm:
            self._summary = SummaryMemory(
                llm=llm,
                session_id=self.session_id,
                config=self.config.summary_config,
            )
        
        if self.config.enable_entity and llm:
            self._entity = EntityMemory(
                llm=llm,
                session_id=self.session_id,
                config=self.config.entity_config,
            )
        
        if self.config.enable_vector and embeddings and vector_store:
            self._vector = VectorStoreMemory(
                embeddings=embeddings,
                vector_store=vector_store,
                session_id=self.session_id,
                config=self.config.vector_config,
            )
    
    @property
    def buffer(self) -> Optional[BufferMemory]:
        """Get buffer memory."""
        return self._buffer
    
    @property
    def summary(self) -> Optional[SummaryMemory]:
        """Get summary memory."""
        return self._summary
    
    @property
    def entity(self) -> Optional[EntityMemory]:
        """Get entity memory."""
        return self._entity
    
    @property
    def vector(self) -> Optional[VectorStoreMemory]:
        """Get vector store memory."""
        return self._vector
    
    async def add_interaction(
        self,
        user_message: str,
        ai_response: str,
        task_context: Optional[str] = None,
        extract_entities: bool = True,
    ) -> None:
        """Add a complete interaction to all memory types.
        
        Args:
            user_message: User's message
            ai_response: AI's response
            task_context: Optional task context
            extract_entities: Whether to extract entities
        """
        # Add to buffer
        if self._buffer:
            self._buffer.add_user_message(user_message)
            self._buffer.add_ai_message(ai_response)
        
        # Add to summary
        if self._summary:
            self._summary.save_context(
                {"input": user_message},
                {"output": ai_response},
            )
        
        # Extract and add entities
        if self._entity and extract_entities:
            combined = f"User: {user_message}\nAssistant: {ai_response}"
            await self._entity.extract_entities(combined)
        
        # Add to vector store
        if self._vector:
            await self._vector.add_conversation(
                user_message=user_message,
                ai_response=ai_response,
                task_context=task_context,
            )
        
        # Auto-save if needed
        await self._auto_save_if_needed()
    
    def get_context(self, max_tokens: int = 4000) -> dict[str, Any]:
        """Get combined context from all memory types.
        
        Args:
            max_tokens: Maximum tokens for context
            
        Returns:
            Dict with context from each memory type
        """
        context: dict[str, Any] = {}
        token_budget = max_tokens
        
        # Add buffer context (most recent, highest priority)
        if self._buffer:
            buffer_vars = self._buffer.load_memory_variables({})
            context["chat_history"] = buffer_vars.get(
                self.config.buffer_config.memory_key, []
            )
            # Rough token estimate
            token_budget -= len(str(context["chat_history"])) // 4
        
        # Add summary (compressed history)
        if self._summary and token_budget > 500:
            summary_vars = self._summary.load_memory_variables({})
            context["summary"] = summary_vars.get(
                self.config.summary_config.memory_key, ""
            )
            token_budget -= len(context["summary"]) // 4
        
        # Add entity context
        if self._entity and token_budget > 200:
            context["entities"] = self._entity.get_context_string()
            token_budget -= len(context["entities"]) // 4
        
        return context
    
    async def get_relevant_context(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> str:
        """Get relevant context for a query via semantic search.
        
        Args:
            query: Query to find context for
            max_tokens: Maximum tokens
            
        Returns:
            Relevant context string
        """
        if self._vector:
            return await self._vector.get_relevant_context(query, max_tokens)
        return ""
    
    async def save(self) -> list[str]:
        """Save all memory to persistence.
        
        Returns:
            List of saved record IDs
        """
        if not self.persistence:
            return []
        
        record_ids: list[str] = []
        expires_at = datetime.utcnow() + timedelta(
            hours=self.config.session_ttl_hours
        )
        
        # Save buffer
        if self._buffer:
            record = MemoryRecord(
                session_id=self.session_id,
                memory_type="buffer",
                data=self._buffer.to_dict(),
                expires_at=expires_at,
            )
            record_id = await self.persistence.save(record)
            record_ids.append(record_id)
        
        # Save summary
        if self._summary:
            record = MemoryRecord(
                session_id=self.session_id,
                memory_type="summary",
                data=self._summary.to_dict(),
                expires_at=expires_at,
            )
            record_id = await self.persistence.save(record)
            record_ids.append(record_id)
        
        # Save entity
        if self._entity:
            record = MemoryRecord(
                session_id=self.session_id,
                memory_type="entity",
                data=self._entity.to_dict(),
                expires_at=expires_at,
            )
            record_id = await self.persistence.save(record)
            record_ids.append(record_id)
        
        # Save vector store metadata
        if self._vector:
            record = MemoryRecord(
                session_id=self.session_id,
                memory_type="vector",
                data=self._vector.to_dict(),
                expires_at=expires_at,
            )
            record_id = await self.persistence.save(record)
            record_ids.append(record_id)
        
        self.last_saved_at = datetime.utcnow()
        return record_ids
    
    async def load(self) -> bool:
        """Load memory from persistence.
        
        Returns:
            True if any memory was loaded
        """
        if not self.persistence:
            return False
        
        records = await self.persistence.load_by_session(self.session_id)
        
        if not records:
            return False
        
        for record in records:
            if record.memory_type == "buffer" and self.config.enable_buffer:
                self._buffer = BufferMemory.from_dict(record.data)
            
            elif record.memory_type == "summary" and self.config.enable_summary and self.llm:
                self._summary = SummaryMemory.from_dict(record.data, self.llm)
            
            elif record.memory_type == "entity" and self.config.enable_entity and self.llm:
                self._entity = EntityMemory.from_dict(record.data, self.llm)
        
        return True
    
    async def clear(self, persist: bool = True) -> None:
        """Clear all memory.
        
        Args:
            persist: Whether to also clear persisted data
        """
        if self._buffer:
            self._buffer.clear()
        
        if self._summary:
            self._summary.clear()
        
        if self._entity:
            self._entity.clear()
        
        if self._vector:
            await self._vector.clear()
        
        if persist and self.persistence:
            from .persistence import PostgresMemoryStore
            if isinstance(self.persistence, PostgresMemoryStore):
                await self.persistence.delete_by_session(self.session_id)
    
    async def _auto_save_if_needed(self) -> None:
        """Auto-save if interval has elapsed."""
        if not self.persistence:
            return
        
        if self.last_saved_at is None:
            await self.save()
            return
        
        elapsed = (datetime.utcnow() - self.last_saved_at).total_seconds()
        if elapsed >= self.config.auto_save_interval:
            await self.save()
    
    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics.
        
        Returns:
            Dict with memory statistics
        """
        stats: dict[str, Any] = {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_saved_at": self.last_saved_at.isoformat() if self.last_saved_at else None,
        }
        
        if self._buffer:
            stats["buffer"] = {
                "message_count": self._buffer.message_count,
                "max_messages": self._buffer.config.max_messages,
            }
        
        if self._summary:
            stats["summary"] = {
                "summary_length": len(self._summary.summary),
                "max_tokens": self._summary.config.max_token_limit,
            }
        
        if self._entity:
            stats["entity"] = {
                "entity_count": self._entity.entity_count,
                "max_entities": self._entity.config.max_entities,
            }
        
        if self._vector:
            stats["vector"] = {
                "document_count": self._vector.document_count,
                "top_k": self._vector.config.top_k,
            }
        
        return stats
    
    @classmethod
    async def create_with_persistence(
        cls,
        connection_string: str,
        session_id: Optional[str] = None,
        llm: Optional[BaseChatModel] = None,
        embeddings: Optional[Embeddings] = None,
        vector_store: Optional[VectorStore] = None,
        config: Optional[MemoryManagerConfig] = None,
        load_existing: bool = True,
    ) -> "MemoryManager":
        """Create memory manager with PostgreSQL persistence.
        
        Args:
            connection_string: PostgreSQL connection string
            session_id: Session identifier
            llm: Language model
            embeddings: Embedding model
            vector_store: Vector store
            config: Manager configuration
            load_existing: Whether to load existing session data
            
        Returns:
            Configured MemoryManager
        """
        from .persistence import PostgresMemoryStore
        
        persistence = PostgresMemoryStore(connection_string)
        await persistence.connect()
        
        manager = cls(
            session_id=session_id,
            llm=llm,
            embeddings=embeddings,
            vector_store=vector_store,
            persistence=persistence,
            config=config,
        )
        
        if load_existing and session_id:
            await manager.load()
        
        return manager

"""Vector store memory for RAG-based retrieval.

Provides semantic search over conversation history and documents.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, Field


class VectorStoreConfig(BaseModel):
    """Configuration for vector store memory."""

    collection_name: str = Field(default="agile_pm_memory")
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class MemoryDocument(BaseModel):
    """Document stored in vector memory."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    doc_type: str = Field(description="Type: conversation, document, artifact")
    session_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VectorStoreMemory:
    """Vector store memory for semantic retrieval.
    
    Enables:
    - Semantic search over conversation history
    - Document retrieval for context
    - Cross-session knowledge retrieval
    """

    def __init__(
        self,
        embeddings: Embeddings,
        vector_store: VectorStore,
        session_id: Optional[str] = None,
        config: Optional[VectorStoreConfig] = None,
    ):
        """Initialize vector store memory.
        
        Args:
            embeddings: Embedding model for vectorization
            vector_store: Vector store instance
            session_id: Optional session identifier
            config: Memory configuration
        """
        self.session_id = session_id or str(uuid4())
        self.config = config or VectorStoreConfig()
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        self._documents: dict[str, MemoryDocument] = {}
    
    @property
    def document_count(self) -> int:
        """Get number of documents stored."""
        return len(self._documents)
    
    async def add_document(
        self,
        content: str,
        doc_type: str = "conversation",
        metadata: Optional[dict[str, Any]] = None,
    ) -> MemoryDocument:
        """Add a document to vector store.
        
        Args:
            content: Document content
            doc_type: Type of document
            metadata: Optional metadata
            
        Returns:
            Created MemoryDocument
        """
        doc = MemoryDocument(
            content=content,
            doc_type=doc_type,
            session_id=self.session_id,
            metadata=metadata or {},
        )
        
        # Create LangChain document
        lc_doc = Document(
            page_content=content,
            metadata={
                "id": doc.id,
                "doc_type": doc_type,
                "session_id": self.session_id,
                "created_at": doc.created_at.isoformat(),
                **(metadata or {}),
            },
        )
        
        # Add to vector store
        await self.vector_store.aadd_documents([lc_doc])
        self._documents[doc.id] = doc
        self.updated_at = datetime.utcnow()
        
        return doc
    
    async def add_conversation(
        self,
        user_message: str,
        ai_response: str,
        task_context: Optional[str] = None,
    ) -> MemoryDocument:
        """Add a conversation turn to vector store.
        
        Args:
            user_message: User's message
            ai_response: AI's response
            task_context: Optional task context
            
        Returns:
            Created MemoryDocument
        """
        content = f"User: {user_message}\nAssistant: {ai_response}"
        
        metadata = {}
        if task_context:
            metadata["task_context"] = task_context
        
        return await self.add_document(
            content=content,
            doc_type="conversation",
            metadata=metadata,
        )
    
    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        doc_type: Optional[str] = None,
        session_only: bool = False,
    ) -> list[Document]:
        """Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results (defaults to config)
            doc_type: Filter by document type
            session_only: Only search current session
            
        Returns:
            List of relevant documents
        """
        k = top_k or self.config.top_k
        
        # Build filter
        filter_dict: dict[str, Any] = {}
        if doc_type:
            filter_dict["doc_type"] = doc_type
        if session_only:
            filter_dict["session_id"] = self.session_id
        
        # Perform similarity search
        if filter_dict:
            results = await self.vector_store.asimilarity_search(
                query,
                k=k,
                filter=filter_dict,
            )
        else:
            results = await self.vector_store.asimilarity_search(query, k=k)
        
        return results
    
    async def search_with_scores(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> list[tuple[Document, float]]:
        """Search with relevance scores.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of (document, score) tuples
        """
        k = top_k or self.config.top_k
        results = await self.vector_store.asimilarity_search_with_score(query, k=k)
        
        # Filter by score threshold
        return [
            (doc, score)
            for doc, score in results
            if score >= self.config.score_threshold
        ]
    
    async def get_relevant_context(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> str:
        """Get relevant context for a query.
        
        Args:
            query: Query to find context for
            max_tokens: Maximum context tokens
            
        Returns:
            Concatenated relevant context
        """
        results = await self.search(query)
        
        context_parts = []
        current_tokens = 0
        
        for doc in results:
            # Rough token estimate (words * 1.3)
            doc_tokens = int(len(doc.page_content.split()) * 1.3)
            
            if current_tokens + doc_tokens <= max_tokens:
                context_parts.append(doc.page_content)
                current_tokens += doc_tokens
            else:
                break
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_document(self, doc_id: str) -> Optional[MemoryDocument]:
        """Get document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            MemoryDocument if found
        """
        return self._documents.get(doc_id)
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted
        """
        if doc_id in self._documents:
            # Delete from vector store
            await self.vector_store.adelete([doc_id])
            del self._documents[doc_id]
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all documents."""
        # Delete all documents from vector store
        doc_ids = list(self._documents.keys())
        if doc_ids:
            await self.vector_store.adelete(doc_ids)
        self._documents.clear()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.
        
        Returns:
            Dict representation (without vector store)
        """
        return {
            "session_id": self.session_id,
            "config": self.config.model_dump(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "documents": {
                doc_id: {
                    "id": doc.id,
                    "content": doc.content,
                    "doc_type": doc.doc_type,
                    "session_id": doc.session_id,
                    "metadata": doc.metadata,
                    "created_at": doc.created_at.isoformat(),
                }
                for doc_id, doc in self._documents.items()
            },
        }

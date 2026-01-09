"""Short-term buffer memory for current session.

Provides ConversationBufferMemory integration with session management.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from langchain.memory import ConversationBufferMemory as LangChainBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field


class BufferConfig(BaseModel):
    """Configuration for buffer memory."""

    max_messages: int = Field(default=100, ge=1, le=1000)
    return_messages: bool = Field(default=True)
    memory_key: str = Field(default="chat_history")
    human_prefix: str = Field(default="Human")
    ai_prefix: str = Field(default="AI")


class BufferMemory:
    """Short-term conversation buffer memory.
    
    Wraps LangChain's ConversationBufferMemory with:
    - Session management
    - Automatic trimming
    - Serialization support
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        config: Optional[BufferConfig] = None,
    ):
        """Initialize buffer memory.
        
        Args:
            session_id: Optional session identifier (auto-generated if not provided)
            config: Memory configuration
        """
        self.session_id = session_id or str(uuid4())
        self.config = config or BufferConfig()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        self._buffer = LangChainBufferMemory(
            return_messages=self.config.return_messages,
            memory_key=self.config.memory_key,
            human_prefix=self.config.human_prefix,
            ai_prefix=self.config.ai_prefix,
        )
    
    @property
    def messages(self) -> list[BaseMessage]:
        """Get all messages in buffer."""
        return self._buffer.chat_memory.messages
    
    @property
    def message_count(self) -> int:
        """Get number of messages in buffer."""
        return len(self.messages)
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the buffer.
        
        Args:
            content: Message content
        """
        self._buffer.chat_memory.add_user_message(content)
        self._trim_if_needed()
        self.updated_at = datetime.utcnow()
    
    def add_ai_message(self, content: str) -> None:
        """Add an AI message to the buffer.
        
        Args:
            content: Message content
        """
        self._buffer.chat_memory.add_ai_message(content)
        self._trim_if_needed()
        self.updated_at = datetime.utcnow()
    
    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add multiple messages to the buffer.
        
        Args:
            messages: List of messages to add
        """
        for msg in messages:
            self._buffer.chat_memory.add_message(msg)
        self._trim_if_needed()
        self.updated_at = datetime.utcnow()
    
    def get_buffer_string(self) -> str:
        """Get buffer contents as a formatted string."""
        return self._buffer.buffer
    
    def load_memory_variables(self, inputs: Optional[dict] = None) -> dict[str, Any]:
        """Load memory variables for chain execution.
        
        Args:
            inputs: Optional input dict
            
        Returns:
            Dict with memory key and contents
        """
        return self._buffer.load_memory_variables(inputs or {})
    
    def save_context(self, inputs: dict[str, Any], outputs: dict[str, str]) -> None:
        """Save context after chain execution.
        
        Args:
            inputs: Input variables
            outputs: Output variables
        """
        self._buffer.save_context(inputs, outputs)
        self._trim_if_needed()
        self.updated_at = datetime.utcnow()
    
    def clear(self) -> None:
        """Clear all messages from buffer."""
        self._buffer.clear()
        self.updated_at = datetime.utcnow()
    
    def _trim_if_needed(self) -> None:
        """Trim messages if exceeding max limit."""
        if self.message_count > self.config.max_messages:
            excess = self.message_count - self.config.max_messages
            self._buffer.chat_memory.messages = self._buffer.chat_memory.messages[excess:]
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize buffer to dictionary for persistence.
        
        Returns:
            Dict representation of buffer state
        """
        return {
            "session_id": self.session_id,
            "config": self.config.model_dump(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [
                {
                    "type": type(msg).__name__,
                    "content": msg.content,
                }
                for msg in self.messages
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BufferMemory":
        """Deserialize buffer from dictionary.
        
        Args:
            data: Dict representation
            
        Returns:
            Restored BufferMemory instance
        """
        config = BufferConfig(**data.get("config", {}))
        memory = cls(session_id=data["session_id"], config=config)
        memory.created_at = datetime.fromisoformat(data["created_at"])
        memory.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # Restore messages
        for msg_data in data.get("messages", []):
            if msg_data["type"] == "HumanMessage":
                memory.add_user_message(msg_data["content"])
            elif msg_data["type"] == "AIMessage":
                memory.add_ai_message(msg_data["content"])
        
        return memory

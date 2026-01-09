"""Long-term summary memory for cross-session context.

Provides ConversationSummaryMemory integration with persistence.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from langchain.memory import ConversationSummaryMemory as LangChainSummaryMemory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class SummaryConfig(BaseModel):
    """Configuration for summary memory."""

    max_token_limit: int = Field(default=2000, ge=100, le=10000)
    memory_key: str = Field(default="history")
    human_prefix: str = Field(default="Human")
    ai_prefix: str = Field(default="AI")
    prompt_template: Optional[str] = None


class SummaryMemory:
    """Long-term conversation summary memory.
    
    Wraps LangChain's ConversationSummaryMemory with:
    - Cross-session persistence
    - Automatic summarization
    - Token management
    """

    def __init__(
        self,
        llm: BaseChatModel,
        session_id: Optional[str] = None,
        config: Optional[SummaryConfig] = None,
    ):
        """Initialize summary memory.
        
        Args:
            llm: Language model for summarization
            session_id: Optional session identifier
            config: Memory configuration
        """
        self.session_id = session_id or str(uuid4())
        self.config = config or SummaryConfig()
        self.llm = llm
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        self._memory = LangChainSummaryMemory(
            llm=llm,
            max_token_limit=self.config.max_token_limit,
            memory_key=self.config.memory_key,
            human_prefix=self.config.human_prefix,
            ai_prefix=self.config.ai_prefix,
        )
        self._summary: str = ""
    
    @property
    def summary(self) -> str:
        """Get current conversation summary."""
        return self._memory.buffer
    
    @property
    def messages(self) -> list[BaseMessage]:
        """Get messages before summarization."""
        return self._memory.chat_memory.messages
    
    def predict_new_summary(
        self,
        messages: list[BaseMessage],
        existing_summary: str = "",
    ) -> str:
        """Generate a new summary from messages.
        
        Args:
            messages: Messages to summarize
            existing_summary: Optional existing summary to extend
            
        Returns:
            New summary string
        """
        return self._memory.predict_new_summary(messages, existing_summary)
    
    def add_user_message(self, content: str) -> None:
        """Add a user message.
        
        Args:
            content: Message content
        """
        self._memory.chat_memory.add_user_message(content)
        self.updated_at = datetime.utcnow()
    
    def add_ai_message(self, content: str) -> None:
        """Add an AI message.
        
        Args:
            content: Message content
        """
        self._memory.chat_memory.add_ai_message(content)
        self.updated_at = datetime.utcnow()
    
    def load_memory_variables(self, inputs: Optional[dict] = None) -> dict[str, Any]:
        """Load memory variables for chain execution.
        
        Args:
            inputs: Optional input dict
            
        Returns:
            Dict with memory key and summary
        """
        return self._memory.load_memory_variables(inputs or {})
    
    def save_context(self, inputs: dict[str, Any], outputs: dict[str, str]) -> None:
        """Save context after chain execution.
        
        Args:
            inputs: Input variables
            outputs: Output variables
        """
        self._memory.save_context(inputs, outputs)
        self.updated_at = datetime.utcnow()
    
    def clear(self) -> None:
        """Clear memory and summary."""
        self._memory.clear()
        self._summary = ""
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence.
        
        Returns:
            Dict representation
        """
        return {
            "session_id": self.session_id,
            "config": self.config.model_dump(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "summary": self.summary,
            "messages": [
                {
                    "type": type(msg).__name__,
                    "content": msg.content,
                }
                for msg in self.messages
            ],
        }
    
    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        llm: BaseChatModel,
    ) -> "SummaryMemory":
        """Deserialize from dictionary.
        
        Args:
            data: Dict representation
            llm: Language model for summarization
            
        Returns:
            Restored SummaryMemory instance
        """
        config = SummaryConfig(**data.get("config", {}))
        memory = cls(llm=llm, session_id=data["session_id"], config=config)
        memory.created_at = datetime.fromisoformat(data["created_at"])
        memory.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # Restore summary
        memory._memory.buffer = data.get("summary", "")
        
        # Restore messages
        for msg_data in data.get("messages", []):
            if msg_data["type"] == "HumanMessage":
                memory.add_user_message(msg_data["content"])
            elif msg_data["type"] == "AIMessage":
                memory.add_ai_message(msg_data["content"])
        
        return memory

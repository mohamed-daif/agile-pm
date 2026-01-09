"""Conversation memory management for Agile-PM agents.

This module provides memory implementations for:
- Agent session memory
- Conversation history
- Task context persistence
"""

from datetime import datetime
from typing import Any, Optional

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """Single memory entry."""

    key: str
    value: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionState(BaseModel):
    """State for an agent session."""

    session_id: str
    role_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    task_id: Optional[str] = None
    governance_mode: bool = True
    chat_history: list[dict[str, str]] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)


class AgentMemory:
    """Memory manager for Agile-PM agents."""

    def __init__(
        self,
        session_id: str,
        role_id: str,
        max_history: int = 50,
    ):
        """Initialize agent memory.

        Args:
            session_id: Unique session identifier
            role_id: Role identifier for context
            max_history: Maximum conversation history entries
        """
        self.session_id = session_id
        self.role_id = role_id
        self.max_history = max_history
        
        self._state = SessionState(
            session_id=session_id,
            role_id=role_id,
        )
        self._context: dict[str, MemoryEntry] = {}
        self._buffer = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
        )

    @property
    def state(self) -> SessionState:
        """Get current session state."""
        return self._state

    @property
    def chat_history(self) -> list[BaseMessage]:
        """Get chat history as messages."""
        return self._buffer.chat_memory.messages

    def add_user_message(self, content: str) -> None:
        """Add a user message to history.

        Args:
            content: Message content
        """
        self._buffer.chat_memory.add_user_message(content)
        self._state.chat_history.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._trim_history()

    def add_ai_message(self, content: str) -> None:
        """Add an AI message to history.

        Args:
            content: Message content
        """
        self._buffer.chat_memory.add_ai_message(content)
        self._state.chat_history.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._trim_history()

    def add_system_message(self, content: str) -> None:
        """Add a system message to history.

        Args:
            content: Message content
        """
        self._buffer.chat_memory.messages.append(SystemMessage(content=content))
        self._state.chat_history.append({
            "role": "system",
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def set_context(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Set a context value.

        Args:
            key: Context key
            value: Context value
            ttl_seconds: Optional time-to-live in seconds
        """
        self._context[key] = MemoryEntry(
            key=key,
            value=value,
            ttl_seconds=ttl_seconds,
        )
        self._state.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: Context key
            default: Default value if not found

        Returns:
            Context value or default
        """
        entry = self._context.get(key)
        if entry is None:
            return default

        # Check TTL
        if entry.ttl_seconds is not None:
            age = (datetime.utcnow() - entry.timestamp).total_seconds()
            if age > entry.ttl_seconds:
                del self._context[key]
                return default

        return entry.value

    def set_task(self, task_id: str) -> None:
        """Set the current task ID.

        Args:
            task_id: Task identifier
        """
        self._state.task_id = task_id
        self.set_context("current_task_id", task_id)

    def add_artifact(self, artifact_path: str) -> None:
        """Record a created artifact.

        Args:
            artifact_path: Path to the artifact
        """
        self._state.artifacts.append(artifact_path)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._buffer.clear()
        self._state.chat_history.clear()

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the memory state.

        Returns:
            Dictionary with memory summary
        """
        return {
            "session_id": self.session_id,
            "role_id": self.role_id,
            "started_at": self._state.started_at.isoformat(),
            "message_count": len(self._state.chat_history),
            "context_keys": list(self._context.keys()),
            "artifacts_count": len(self._state.artifacts),
            "governance_mode": self._state.governance_mode,
        }

    def _trim_history(self) -> None:
        """Trim history to max size."""
        if len(self._state.chat_history) > self.max_history:
            # Keep most recent messages
            self._state.chat_history = self._state.chat_history[-self.max_history:]


class SessionMemory:
    """Persistent memory across agent sessions."""

    def __init__(self, storage_path: str = ".serena/memories"):
        """Initialize session memory.

        Args:
            storage_path: Path to store memory files
        """
        self.storage_path = storage_path
        self._sessions: dict[str, AgentMemory] = {}

    def get_or_create(
        self,
        session_id: str,
        role_id: str,
    ) -> AgentMemory:
        """Get or create a session memory.

        Args:
            session_id: Session identifier
            role_id: Role identifier

        Returns:
            AgentMemory instance
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = AgentMemory(session_id, role_id)
        return self._sessions[session_id]

    def get(self, session_id: str) -> Optional[AgentMemory]:
        """Get session memory if it exists.

        Args:
            session_id: Session identifier

        Returns:
            AgentMemory or None
        """
        return self._sessions.get(session_id)

    def save(self, session_id: str) -> None:
        """Save session memory to disk.

        Args:
            session_id: Session identifier
        """
        import json
        import os

        memory = self._sessions.get(session_id)
        if memory is None:
            return

        os.makedirs(self.storage_path, exist_ok=True)
        filepath = os.path.join(self.storage_path, f"{session_id}.json")

        with open(filepath, "w") as f:
            json.dump(memory.state.model_dump(), f, indent=2, default=str)

    def load(self, session_id: str) -> Optional[AgentMemory]:
        """Load session memory from disk.

        Args:
            session_id: Session identifier

        Returns:
            AgentMemory or None if not found
        """
        import json
        import os

        filepath = os.path.join(self.storage_path, f"{session_id}.json")
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r") as f:
            data = json.load(f)

        memory = AgentMemory(
            session_id=data["session_id"],
            role_id=data["role_id"],
        )
        memory._state = SessionState(**data)
        self._sessions[session_id] = memory
        return memory

    def list_sessions(self) -> list[str]:
        """List all stored session IDs.

        Returns:
            List of session IDs
        """
        import os

        if not os.path.exists(self.storage_path):
            return []

        return [
            f.replace(".json", "")
            for f in os.listdir(self.storage_path)
            if f.endswith(".json")
        ]


def create_memory(
    session_id: str,
    role_id: str,
    llm: Optional[BaseChatModel] = None,
    use_summary: bool = False,
    max_history: int = 50,
) -> AgentMemory:
    """Factory function to create agent memory.

    Args:
        session_id: Session identifier
        role_id: Role identifier
        llm: Language model (required for summary memory)
        use_summary: Use summary memory instead of buffer
        max_history: Maximum history entries

    Returns:
        Configured AgentMemory
    """
    return AgentMemory(
        session_id=session_id,
        role_id=role_id,
        max_history=max_history,
    )

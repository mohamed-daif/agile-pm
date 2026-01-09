"""Inter-agent collaboration and messaging.

Provides communication protocol for multi-agent collaboration.
"""

from datetime import datetime
from typing import Any, Optional, Callable, Awaitable
from uuid import uuid4
from enum import Enum
import asyncio

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of inter-agent messages."""
    
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    DELEGATION = "delegation"
    CONSENSUS = "consensus"
    ERROR = "error"


class MessagePriority(str, Enum):
    """Message priority levels."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentMessage(BaseModel):
    """Message between agents."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MessageType
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    
    sender: str = Field(description="Sender agent role/ID")
    recipient: str = Field(description="Recipient agent role/ID, or 'broadcast'")
    
    subject: str
    content: Any
    
    correlation_id: Optional[str] = Field(
        default=None,
        description="ID to correlate request/response"
    )
    in_reply_to: Optional[str] = Field(
        default=None,
        description="Message ID this is replying to"
    )
    
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class AgentSubscription(BaseModel):
    """Subscription to message types."""

    agent_id: str
    message_types: list[MessageType] = Field(default_factory=list)
    subjects: list[str] = Field(default_factory=list)
    handler: Optional[Callable[[AgentMessage], Awaitable[None]]] = None
    
    class Config:
        arbitrary_types_allowed = True


class CollaborationHub:
    """Central hub for inter-agent communication.
    
    Provides:
    - Message routing between agents
    - Broadcast messaging
    - Request-response patterns
    - Async message handling
    """

    def __init__(self):
        """Initialize collaboration hub."""
        self._agents: dict[str, AgentSubscription] = {}
        self._message_queue: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self._pending_requests: dict[str, asyncio.Future[AgentMessage]] = {}
        self._message_history: list[AgentMessage] = []
        self._running = False
    
    def register_agent(
        self,
        agent_id: str,
        handler: Callable[[AgentMessage], Awaitable[None]],
        message_types: Optional[list[MessageType]] = None,
        subjects: Optional[list[str]] = None,
    ) -> None:
        """Register an agent with the hub.
        
        Args:
            agent_id: Unique agent identifier
            handler: Async function to handle messages
            message_types: Types to subscribe to (all if None)
            subjects: Subjects to subscribe to (all if None)
        """
        self._agents[agent_id] = AgentSubscription(
            agent_id=agent_id,
            message_types=message_types or [],
            subjects=subjects or [],
            handler=handler,
        )
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent.
        
        Args:
            agent_id: Agent to unregister
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
    
    async def send(self, message: AgentMessage) -> None:
        """Send a message.
        
        Args:
            message: Message to send
        """
        self._message_history.append(message)
        await self._message_queue.put(message)
    
    async def send_and_wait(
        self,
        message: AgentMessage,
        timeout: float = 30.0,
    ) -> AgentMessage:
        """Send a request and wait for response.
        
        Args:
            message: Request message
            timeout: Timeout in seconds
            
        Returns:
            Response message
            
        Raises:
            asyncio.TimeoutError: If no response received
        """
        if not message.correlation_id:
            message.correlation_id = message.id
        
        future: asyncio.Future[AgentMessage] = asyncio.Future()
        self._pending_requests[message.correlation_id] = future
        
        await self.send(message)
        
        try:
            response = await asyncio.wait_for(future, timeout)
            return response
        finally:
            self._pending_requests.pop(message.correlation_id, None)
    
    async def broadcast(
        self,
        sender: str,
        subject: str,
        content: Any,
        message_type: MessageType = MessageType.NOTIFICATION,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> None:
        """Broadcast a message to all agents.
        
        Args:
            sender: Sender agent ID
            subject: Message subject
            content: Message content
            message_type: Type of message
            priority: Priority level
        """
        message = AgentMessage(
            type=message_type,
            priority=priority,
            sender=sender,
            recipient="broadcast",
            subject=subject,
            content=content,
        )
        await self.send(message)
    
    async def delegate(
        self,
        sender: str,
        recipient: str,
        task: str,
        context: Any,
        timeout: float = 60.0,
    ) -> AgentMessage:
        """Delegate a task to another agent.
        
        Args:
            sender: Delegating agent
            recipient: Target agent
            task: Task description
            context: Task context
            timeout: Timeout for response
            
        Returns:
            Delegation response
        """
        message = AgentMessage(
            type=MessageType.DELEGATION,
            priority=MessagePriority.HIGH,
            sender=sender,
            recipient=recipient,
            subject=f"Delegation: {task}",
            content={
                "task": task,
                "context": context,
            },
        )
        return await self.send_and_wait(message, timeout)
    
    async def start(self) -> None:
        """Start processing messages."""
        self._running = True
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._message_queue.get(),
                    timeout=1.0,
                )
                await self._process_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                # Log error and continue
                print(f"Error processing message: {e}")
    
    async def stop(self) -> None:
        """Stop processing messages."""
        self._running = False
    
    async def _process_message(self, message: AgentMessage) -> None:
        """Process a single message.
        
        Args:
            message: Message to process
        """
        # Check if this is a response to pending request
        if message.in_reply_to and message.correlation_id:
            if message.correlation_id in self._pending_requests:
                self._pending_requests[message.correlation_id].set_result(message)
                return
        
        # Route to recipient(s)
        if message.recipient == "broadcast":
            # Send to all agents except sender
            for agent_id, subscription in self._agents.items():
                if agent_id != message.sender:
                    if self._matches_subscription(message, subscription):
                        if subscription.handler:
                            await subscription.handler(message)
        else:
            # Send to specific recipient
            subscription = self._agents.get(message.recipient)
            if subscription and subscription.handler:
                await subscription.handler(message)
    
    def _matches_subscription(
        self,
        message: AgentMessage,
        subscription: AgentSubscription,
    ) -> bool:
        """Check if message matches subscription filters.
        
        Args:
            message: Message to check
            subscription: Subscription to match against
            
        Returns:
            True if message matches
        """
        # If no filters, match all
        if not subscription.message_types and not subscription.subjects:
            return True
        
        # Check message type filter
        if subscription.message_types:
            if message.type not in subscription.message_types:
                return False
        
        # Check subject filter
        if subscription.subjects:
            if not any(s in message.subject for s in subscription.subjects):
                return False
        
        return True
    
    def get_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100,
    ) -> list[AgentMessage]:
        """Get message history.
        
        Args:
            agent_id: Filter by agent (sender or recipient)
            message_type: Filter by type
            limit: Maximum messages to return
            
        Returns:
            List of messages
        """
        filtered = self._message_history
        
        if agent_id:
            filtered = [
                m for m in filtered
                if m.sender == agent_id or m.recipient == agent_id
            ]
        
        if message_type:
            filtered = [m for m in filtered if m.type == message_type]
        
        return filtered[-limit:]
    
    def get_stats(self) -> dict[str, Any]:
        """Get hub statistics.
        
        Returns:
            Dict with statistics
        """
        return {
            "registered_agents": len(self._agents),
            "total_messages": len(self._message_history),
            "pending_requests": len(self._pending_requests),
            "queue_size": self._message_queue.qsize(),
            "message_types": {
                t.value: len([m for m in self._message_history if m.type == t])
                for t in MessageType
            },
        }

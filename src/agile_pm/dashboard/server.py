"""WebSocket server for real-time dashboard updates."""

import asyncio
import json
from datetime import datetime
from typing import Any, Optional, Callable, Awaitable
from uuid import uuid4
import logging

from pydantic import BaseModel, Field

from .events import DashboardEvent, EventType, ConnectionEvent
from .metrics import MetricsCollector, SystemMetrics


logger = logging.getLogger(__name__)


class DashboardConfig(BaseModel):
    """Configuration for dashboard server."""

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8765)
    
    # Metrics
    metrics_interval: float = Field(
        default=5.0,
        description="Seconds between metrics broadcasts"
    )
    snapshot_interval: float = Field(
        default=60.0,
        description="Seconds between metric snapshots"
    )
    
    # Connection
    max_connections: int = Field(default=100)
    ping_interval: float = Field(default=30.0)
    ping_timeout: float = Field(default=10.0)
    
    # Auth
    require_auth: bool = Field(default=False)
    auth_token: Optional[str] = None


class WebSocketClient(BaseModel):
    """Represents a connected WebSocket client."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    ip_address: Optional[str] = None
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    authenticated: bool = False
    subscriptions: list[EventType] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


class DashboardServer:
    """WebSocket server for real-time dashboard updates.
    
    Provides:
    - Real-time event streaming
    - Metrics broadcasting
    - Client subscription management
    - Authentication support
    """

    def __init__(
        self,
        config: Optional[DashboardConfig] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        """Initialize dashboard server.
        
        Args:
            config: Server configuration
            metrics_collector: Metrics collector instance
        """
        self.config = config or DashboardConfig()
        self.metrics = metrics_collector or MetricsCollector()
        
        self._clients: dict[str, WebSocketClient] = {}
        self._websockets: dict[str, Any] = {}  # Client ID -> websocket
        self._event_handlers: list[Callable[[DashboardEvent], Awaitable[None]]] = []
        self._running = False
        self._server = None
        self._tasks: list[asyncio.Task] = []
    
    async def start(self) -> None:
        """Start the WebSocket server."""
        try:
            # Import websockets here to avoid import errors if not installed
            import websockets
            
            self._running = True
            
            self._server = await websockets.serve(
                self._handle_connection,
                self.config.host,
                self.config.port,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout,
            )
            
            # Start background tasks
            self._tasks = [
                asyncio.create_task(self._metrics_broadcast_loop()),
                asyncio.create_task(self._snapshot_loop()),
            ]
            
            logger.info(
                f"Dashboard server started on ws://{self.config.host}:{self.config.port}"
            )
            
        except ImportError:
            logger.error("websockets package not installed")
            raise
    
    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self._running = False
        
        # Cancel background tasks
        for task in self._tasks:
            task.cancel()
        
        # Close all connections
        for client_id in list(self._websockets.keys()):
            await self._disconnect_client(client_id)
        
        # Close server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        logger.info("Dashboard server stopped")
    
    async def broadcast_event(self, event: DashboardEvent) -> None:
        """Broadcast an event to all subscribed clients.
        
        Args:
            event: Event to broadcast
        """
        message = json.dumps(event.model_dump(), default=str)
        
        disconnected = []
        for client_id, client in self._clients.items():
            # Check subscription
            if client.subscriptions and event.type not in client.subscriptions:
                continue
            
            ws = self._websockets.get(client_id)
            if ws:
                try:
                    await ws.send(message)
                except Exception as e:
                    logger.warning(f"Failed to send to client {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            await self._disconnect_client(client_id)
    
    async def send_to_client(self, client_id: str, event: DashboardEvent) -> bool:
        """Send an event to a specific client.
        
        Args:
            client_id: Target client ID
            event: Event to send
            
        Returns:
            True if sent successfully
        """
        ws = self._websockets.get(client_id)
        if not ws:
            return False
        
        try:
            message = json.dumps(event.model_dump(), default=str)
            await ws.send(message)
            return True
        except Exception as e:
            logger.warning(f"Failed to send to client {client_id}: {e}")
            await self._disconnect_client(client_id)
            return False
    
    def add_event_handler(
        self,
        handler: Callable[[DashboardEvent], Awaitable[None]],
    ) -> None:
        """Add an event handler.
        
        Args:
            handler: Async function to handle events
        """
        self._event_handlers.append(handler)
    
    def get_connected_clients(self) -> list[WebSocketClient]:
        """Get list of connected clients.
        
        Returns:
            List of connected clients
        """
        return list(self._clients.values())
    
    def get_connection_count(self) -> int:
        """Get number of connected clients.
        
        Returns:
            Connection count
        """
        return len(self._clients)
    
    async def _handle_connection(self, websocket, path: str) -> None:
        """Handle a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            path: Request path
        """
        # Check max connections
        if len(self._clients) >= self.config.max_connections:
            await websocket.close(1013, "Maximum connections reached")
            return
        
        # Create client
        client = WebSocketClient(
            ip_address=websocket.remote_address[0] if websocket.remote_address else None,
        )
        
        # Auth check
        if self.config.require_auth:
            try:
                auth_msg = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=10.0,
                )
                auth_data = json.loads(auth_msg)
                if auth_data.get("token") != self.config.auth_token:
                    await websocket.close(1008, "Authentication failed")
                    return
                client.authenticated = True
            except Exception:
                await websocket.close(1008, "Authentication required")
                return
        else:
            client.authenticated = True
        
        # Register client
        self._clients[client.id] = client
        self._websockets[client.id] = websocket
        
        # Send connection event
        await self.broadcast_event(ConnectionEvent(
            source="server",
            client_id=client.id,
            action="connected",
            ip_address=client.ip_address,
        ))
        
        logger.info(f"Client connected: {client.id}")
        
        try:
            # Send initial state
            await self._send_initial_state(client.id)
            
            # Handle messages
            async for message in websocket:
                await self._handle_message(client.id, message)
        
        except Exception as e:
            logger.error(f"Error handling client {client.id}: {e}")
        
        finally:
            await self._disconnect_client(client.id)
    
    async def _handle_message(self, client_id: str, message: str) -> None:
        """Handle a message from a client.
        
        Args:
            client_id: Client ID
            message: Raw message
        """
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "subscribe":
                # Update subscriptions
                event_types = data.get("events", [])
                client = self._clients.get(client_id)
                if client:
                    client.subscriptions = [
                        EventType(e) for e in event_types if e in EventType.__members__
                    ]
            
            elif action == "get_metrics":
                # Send current metrics
                metrics = self.metrics.get_system_metrics()
                ws = self._websockets.get(client_id)
                if ws:
                    await ws.send(json.dumps({
                        "type": "metrics",
                        "data": metrics.model_dump(),
                    }, default=str))
            
            elif action == "get_history":
                # Send metrics history
                minutes = data.get("minutes", 60)
                history = self.metrics.get_history(minutes)
                ws = self._websockets.get(client_id)
                if ws:
                    await ws.send(json.dumps({
                        "type": "history",
                        "data": [m.model_dump() for m in history],
                    }, default=str))
        
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
    
    async def _send_initial_state(self, client_id: str) -> None:
        """Send initial state to a new client.
        
        Args:
            client_id: Client ID
        """
        ws = self._websockets.get(client_id)
        if not ws:
            return
        
        # Send all metrics
        all_metrics = self.metrics.get_all_metrics()
        await ws.send(json.dumps({
            "type": "initial_state",
            "data": all_metrics,
        }, default=str))
    
    async def _disconnect_client(self, client_id: str) -> None:
        """Disconnect a client.
        
        Args:
            client_id: Client ID
        """
        client = self._clients.pop(client_id, None)
        ws = self._websockets.pop(client_id, None)
        
        if ws:
            try:
                await ws.close()
            except Exception:
                pass
        
        if client:
            await self.broadcast_event(ConnectionEvent(
                source="server",
                client_id=client_id,
                action="disconnected",
            ))
            logger.info(f"Client disconnected: {client_id}")
    
    async def _metrics_broadcast_loop(self) -> None:
        """Background task to broadcast metrics periodically."""
        while self._running:
            try:
                await asyncio.sleep(self.config.metrics_interval)
                
                if self._clients:
                    metrics = self.metrics.get_system_metrics()
                    message = json.dumps({
                        "type": "metrics_update",
                        "data": metrics.model_dump(),
                    }, default=str)
                    
                    for client_id, ws in list(self._websockets.items()):
                        try:
                            await ws.send(message)
                        except Exception:
                            pass
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics broadcast: {e}")
    
    async def _snapshot_loop(self) -> None:
        """Background task to take metric snapshots."""
        while self._running:
            try:
                await asyncio.sleep(self.config.snapshot_interval)
                self.metrics.snapshot()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in snapshot: {e}")


# Convenience function for quick server start
async def run_dashboard_server(
    host: str = "0.0.0.0",
    port: int = 8765,
    **kwargs,
) -> DashboardServer:
    """Run a dashboard server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        **kwargs: Additional config options
        
    Returns:
        Running DashboardServer
    """
    config = DashboardConfig(host=host, port=port, **kwargs)
    server = DashboardServer(config)
    await server.start()
    return server

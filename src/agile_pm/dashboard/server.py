"""Dashboard server implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from agile_pm.core.config import AgileConfig

if TYPE_CHECKING:
    pass


class DashboardServer:
    """Web dashboard for Agile-PM monitoring."""

    def __init__(self, config: AgileConfig) -> None:
        """Initialize dashboard server.
        
        Args:
            config: Agile-PM configuration
        """
        self.config = config
        self._app = None
        self._running = False

    def create_app(self):
        """Create the FastAPI application."""
        from fastapi import FastAPI
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates
        
        app = FastAPI(
            title="Agile-PM Dashboard",
            description="AI-powered Agile project management dashboard",
            version="0.1.0",
        )
        
        @app.get("/api/health")
        async def health():
            return {"status": "healthy"}
        
        @app.get("/api/config")
        async def get_config():
            return self.config.model_dump()
        
        @app.get("/api/crews")
        async def list_crews():
            return {"crews": ["planning", "review", "execution"]}
        
        @app.get("/api/memories")
        async def list_memories():
            # TODO: Integrate with MemoryManager
            return {"memories": []}
        
        self._app = app
        return app

    def start(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        """Start the dashboard server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        
        if self._app is None:
            self.create_app()
        
        self._running = True
        uvicorn.run(self._app, host=host, port=port)

    def stop(self) -> None:
        """Stop the dashboard server."""
        self._running = False

    @property
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._running

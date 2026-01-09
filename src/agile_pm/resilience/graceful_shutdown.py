"""Graceful Shutdown Handler."""

import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ShutdownConfig:
    """Shutdown configuration."""
    timeout: float = 30.0              # Max time to wait for cleanup
    signals: List[signal.Signals] = field(
        default_factory=lambda: [signal.SIGTERM, signal.SIGINT]
    )


class GracefulShutdown:
    """Handle graceful shutdown of services."""

    def __init__(self, config: Optional[ShutdownConfig] = None):
        self.config = config or ShutdownConfig()
        self._shutdown_event = asyncio.Event()
        self._cleanup_tasks: List[Callable] = []
        self._is_shutting_down = False

    @property
    def is_shutting_down(self) -> bool:
        """Check if shutdown is in progress."""
        return self._is_shutting_down

    def register_cleanup(self, func: Callable) -> None:
        """Register a cleanup function to run on shutdown."""
        self._cleanup_tasks.append(func)

    def _signal_handler(self, sig: signal.Signals) -> None:
        """Handle shutdown signal."""
        logger.info(f"Received signal {sig.name}, initiating graceful shutdown...")
        self._shutdown_event.set()

    def setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        for sig in self.config.signals:
            loop.add_signal_handler(sig, lambda s=sig: self._signal_handler(s))

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()

    async def shutdown(self) -> None:
        """Execute graceful shutdown."""
        if self._is_shutting_down:
            return
        
        self._is_shutting_down = True
        logger.info("Starting graceful shutdown...")
        
        # Run cleanup tasks with timeout
        for cleanup_func in reversed(self._cleanup_tasks):
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await asyncio.wait_for(
                        cleanup_func(),
                        timeout=self.config.timeout / len(self._cleanup_tasks) if self._cleanup_tasks else self.config.timeout
                    )
                else:
                    cleanup_func()
            except asyncio.TimeoutError:
                logger.warning(f"Cleanup task {cleanup_func.__name__} timed out")
            except Exception as e:
                logger.error(f"Error in cleanup task {cleanup_func.__name__}: {e}")
        
        logger.info("Graceful shutdown complete")


@asynccontextmanager
async def graceful_shutdown_context(config: Optional[ShutdownConfig] = None):
    """Context manager for graceful shutdown."""
    shutdown = GracefulShutdown(config)
    shutdown.setup_signal_handlers()
    
    try:
        yield shutdown
    finally:
        await shutdown.shutdown()

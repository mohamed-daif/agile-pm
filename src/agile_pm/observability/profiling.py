"""Performance profiling utilities."""
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager
import time
import threading
import cProfile
import pstats
import io
import tracemalloc
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ProfileResult:
    """Profiling result container."""
    name: str
    duration_ms: float
    cpu_time_ms: Optional[float] = None
    memory_delta_mb: Optional[float] = None
    call_count: Optional[int] = None
    top_functions: Optional[list] = None


class Profiler:
    """CPU and memory profiler."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._profiles: Dict[str, ProfileResult] = {}
    
    @contextmanager
    def profile(self, name: str, include_memory: bool = False):
        """Profile a code block."""
        if not self.enabled:
            yield
            return
        
        start_time = time.perf_counter()
        start_memory = None
        
        if include_memory:
            tracemalloc.start()
            start_memory = tracemalloc.get_traced_memory()[0]
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            yield
        finally:
            profiler.disable()
            end_time = time.perf_counter()
            
            memory_delta = None
            if include_memory:
                end_memory = tracemalloc.get_traced_memory()[0]
                tracemalloc.stop()
                memory_delta = (end_memory - start_memory) / 1024 / 1024  # MB
            
            # Get stats
            stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stream)
            stats.sort_stats("cumulative")
            stats.print_stats(10)
            
            result = ProfileResult(
                name=name,
                duration_ms=(end_time - start_time) * 1000,
                memory_delta_mb=memory_delta,
                call_count=profiler.getstats().__len__() if hasattr(profiler, 'getstats') else None,
                top_functions=stream.getvalue().split('\n')[:15],
            )
            
            self._profiles[name] = result
            
            logger.debug(
                "profile_complete",
                name=name,
                duration_ms=result.duration_ms,
                memory_delta_mb=result.memory_delta_mb,
            )
    
    def get_results(self) -> Dict[str, ProfileResult]:
        """Get all profiling results."""
        return self._profiles.copy()
    
    def clear(self):
        """Clear profiling results."""
        self._profiles.clear()


# Slow query logging
class SlowQueryLogger:
    """Log slow database queries."""
    
    def __init__(self, threshold_ms: float = 100):
        self.threshold_ms = threshold_ms
        self._slow_queries: list = []
    
    def log_query(self, query: str, duration_ms: float, params: Optional[dict] = None):
        """Log a query if it exceeds threshold."""
        if duration_ms > self.threshold_ms:
            entry = {
                "query": query[:500],  # Truncate long queries
                "duration_ms": duration_ms,
                "params": params,
                "timestamp": time.time(),
            }
            self._slow_queries.append(entry)
            logger.warning(
                "slow_query",
                duration_ms=duration_ms,
                query=query[:200],
            )
    
    def get_slow_queries(self, limit: int = 100) -> list:
        """Get recent slow queries."""
        return self._slow_queries[-limit:]
    
    def clear(self):
        """Clear slow query log."""
        self._slow_queries.clear()


# Global instances
_profiler = Profiler(enabled=False)  # Disabled by default
_slow_query_logger = SlowQueryLogger()


def get_profiler() -> Profiler:
    """Get the global profiler."""
    return _profiler


def get_slow_query_logger() -> SlowQueryLogger:
    """Get the slow query logger."""
    return _slow_query_logger


def enable_profiling():
    """Enable profiling globally."""
    global _profiler
    _profiler = Profiler(enabled=True)


def profile_endpoint(include_memory: bool = False):
    """Decorator to profile an endpoint."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with _profiler.profile(func.__name__, include_memory=include_memory):
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with _profiler.profile(func.__name__, include_memory=include_memory):
                return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

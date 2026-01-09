"""Retry Logic with Exponential Backoff."""

import asyncio
import logging
import random
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional, Tuple, Type, TypeVar, Union

T = TypeVar("T")
logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_attempts: int = 3
    base_delay: float = 1.0           # Initial delay in seconds
    max_delay: float = 60.0           # Maximum delay
    exponential_base: float = 2.0     # Exponential multiplier
    jitter: bool = True               # Add random jitter
    jitter_range: Tuple[float, float] = (0.5, 1.5)
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    non_retryable_exceptions: Tuple[Type[Exception], ...] = ()


def calculate_delay(
    attempt: int,
    config: RetryConfig,
) -> float:
    """Calculate delay for retry attempt."""
    delay = min(
        config.base_delay * (config.exponential_base ** attempt),
        config.max_delay,
    )
    
    if config.jitter:
        jitter_factor = random.uniform(*config.jitter_range)
        delay *= jitter_factor
    
    return delay


async def retry_async(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
    **kwargs,
) -> T:
    """Retry an async function with exponential backoff."""
    config = config or RetryConfig()
    last_exception: Optional[Exception] = None
    
    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except config.non_retryable_exceptions:
            raise
        except config.retryable_exceptions as e:
            last_exception = e
            
            if attempt == config.max_attempts - 1:
                # Last attempt, don't retry
                break
            
            delay = calculate_delay(attempt, config)
            
            logger.warning(
                f"Retry {attempt + 1}/{config.max_attempts} for {func.__name__}: "
                f"{type(e).__name__}: {e}. Retrying in {delay:.2f}s"
            )
            
            if on_retry:
                on_retry(attempt + 1, e, delay)
            
            await asyncio.sleep(delay)
    
    raise last_exception


def retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> Callable:
    """Decorator for retry with backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await retry_async(func, *args, config=config, on_retry=on_retry, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, use a simple loop
            cfg = config or RetryConfig()
            last_exc = None
            
            for attempt in range(cfg.max_attempts):
                try:
                    return func(*args, **kwargs)
                except cfg.non_retryable_exceptions:
                    raise
                except cfg.retryable_exceptions as e:
                    last_exc = e
                    if attempt < cfg.max_attempts - 1:
                        delay = calculate_delay(attempt, cfg)
                        if on_retry:
                            on_retry(attempt + 1, e, delay)
                        import time
                        time.sleep(delay)
            
            raise last_exc
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Pre-configured retry decorators
def retry_on_network_error(func: Callable) -> Callable:
    """Retry on common network errors."""
    config = RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        retryable_exceptions=(ConnectionError, TimeoutError, OSError),
    )
    return retry(config)(func)


def retry_on_rate_limit(func: Callable) -> Callable:
    """Retry on rate limit with longer delays."""
    config = RetryConfig(
        max_attempts=5,
        base_delay=5.0,
        max_delay=120.0,
        exponential_base=2.0,
    )
    return retry(config)(func)

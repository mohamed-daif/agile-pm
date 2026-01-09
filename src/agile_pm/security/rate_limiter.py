"""Rate Limiting Implementation."""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from .config import RATE_LIMIT_REQUESTS_PER_MINUTE, RATE_LIMIT_BURST


@dataclass
class RateLimitResult:
    """Result of rate limit check."""
    allowed: bool
    remaining: int
    reset_at: float
    retry_after: Optional[float] = None


class TokenBucketRateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        rate_per_minute: int = RATE_LIMIT_REQUESTS_PER_MINUTE,
        burst: int = RATE_LIMIT_BURST,
    ):
        self.rate = rate_per_minute / 60.0  # tokens per second
        self.burst = burst
        self.buckets: dict[str, dict] = defaultdict(lambda: {
            "tokens": burst,
            "last_update": time.time(),
        })
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> RateLimitResult:
        """Check if request is allowed."""
        async with self._lock:
            now = time.time()
            bucket = self.buckets[key]
            
            # Refill tokens based on time elapsed
            elapsed = now - bucket["last_update"]
            bucket["tokens"] = min(
                self.burst,
                bucket["tokens"] + elapsed * self.rate
            )
            bucket["last_update"] = now
            
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return RateLimitResult(
                    allowed=True,
                    remaining=int(bucket["tokens"]),
                    reset_at=now + (self.burst - bucket["tokens"]) / self.rate,
                )
            else:
                retry_after = (1 - bucket["tokens"]) / self.rate
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=now + retry_after,
                    retry_after=retry_after,
                )

    async def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        async with self._lock:
            self.buckets[key] = {
                "tokens": self.burst,
                "last_update": time.time(),
            }


class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""

    def __init__(
        self,
        max_requests: int = RATE_LIMIT_REQUESTS_PER_MINUTE,
        window_seconds: int = 60,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> RateLimitResult:
        """Check if request is allowed."""
        async with self._lock:
            now = time.time()
            cutoff = now - self.window_seconds
            
            # Remove expired requests
            self.requests[key] = [t for t in self.requests[key] if t > cutoff]
            
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return RateLimitResult(
                    allowed=True,
                    remaining=self.max_requests - len(self.requests[key]),
                    reset_at=now + self.window_seconds,
                )
            else:
                oldest = min(self.requests[key])
                retry_after = oldest + self.window_seconds - now
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=oldest + self.window_seconds,
                    retry_after=max(0, retry_after),
                )


# Global rate limiter instance
_rate_limiter: Optional[TokenBucketRateLimiter] = None


def get_rate_limiter() -> TokenBucketRateLimiter:
    """Get or create global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = TokenBucketRateLimiter()
    return _rate_limiter

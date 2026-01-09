"""Rate limiting implementation."""
import time
from typing import Optional
from dataclasses import dataclass

@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_at: int

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, burst: int = 10):
        self.rpm = requests_per_minute
        self.burst = burst
        self._buckets: dict = {}
    
    def check(self, key: str) -> RateLimitResult:
        now = time.time()
        window_start = int(now / 60) * 60
        
        if key not in self._buckets or self._buckets[key]["window"] != window_start:
            self._buckets[key] = {"window": window_start, "count": 0}
        
        bucket = self._buckets[key]
        bucket["count"] += 1
        remaining = max(0, self.rpm - bucket["count"])
        allowed = bucket["count"] <= self.rpm
        
        return RateLimitResult(
            allowed=allowed,
            limit=self.rpm,
            remaining=remaining,
            reset_at=window_start + 60
        )
    
    def get_headers(self, result: RateLimitResult) -> dict:
        return {
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(result.reset_at)
        }

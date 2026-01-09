"""Test rate limiting."""
import pytest
import time


class TestRateLimiter:
    """Test rate limiter."""

    def test_allows_under_limit(self):
        """Test requests under limit are allowed."""
        from agile_pm.api.limits.rate_limiter import RateLimiter
        limiter = RateLimiter(requests_per_minute=10)
        result = limiter.check("user-1")
        assert result.allowed is True
        assert result.remaining == 9

    def test_blocks_over_limit(self):
        """Test requests over limit are blocked."""
        from agile_pm.api.limits.rate_limiter import RateLimiter
        limiter = RateLimiter(requests_per_minute=3)
        for _ in range(3):
            limiter.check("user-1")
        result = limiter.check("user-1")
        assert result.allowed is False
        assert result.remaining == 0

    def test_different_keys_independent(self):
        """Test different keys have separate limits."""
        from agile_pm.api.limits.rate_limiter import RateLimiter
        limiter = RateLimiter(requests_per_minute=2)
        limiter.check("user-1")
        limiter.check("user-1")
        result = limiter.check("user-2")
        assert result.allowed is True

    def test_headers_generated(self):
        """Test rate limit headers."""
        from agile_pm.api.limits.rate_limiter import RateLimiter
        limiter = RateLimiter(requests_per_minute=10)
        result = limiter.check("user-1")
        headers = limiter.get_headers(result)
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers

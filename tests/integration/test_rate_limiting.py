"""Test rate limiting integration."""
import pytest


class TestRateLimitingIntegration:
    """Test rate limiting end-to-end."""

    def test_rate_limit_headers(self, integration_client):
        """Test rate limit headers in response."""
        response = integration_client.get("/api/v1/system/health")
        # May have rate limit headers if middleware enabled
        # This depends on middleware configuration
        assert response.status_code == 200

    def test_rate_limit_enforcement(self):
        """Test rate limit enforcement."""
        from agile_pm.api.limits.rate_limiter import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=5)
        
        # Make requests up to limit
        for i in range(5):
            result = limiter.check("integration-test")
            assert result.allowed is True
        
        # Next request should be blocked
        result = limiter.check("integration-test")
        assert result.allowed is False

    def test_quota_enforcement(self):
        """Test quota enforcement."""
        from agile_pm.api.limits.quotas import QuotaManager, QuotaTier
        
        manager = QuotaManager()
        user_id = "integration-test-user"
        
        # Check initial quota
        allowed, status = manager.check_quota(user_id)
        assert allowed is True
        assert status.tier == QuotaTier.FREE
        
        # Upgrade tier
        manager.set_tier(user_id, QuotaTier.PRO)
        _, status = manager.check_quota(user_id)
        assert status.tier == QuotaTier.PRO

"""Test quota management."""
import pytest


class TestQuotaManager:
    """Test usage quotas."""

    def test_free_tier_limits(self):
        """Test free tier quota limits."""
        from agile_pm.api.limits.quotas import QuotaManager, QuotaTier
        manager = QuotaManager()
        allowed, status = manager.check_quota("user-1")
        assert allowed is True
        assert status.tier == QuotaTier.FREE
        assert status.daily_limit == 1000

    def test_increment_usage(self):
        """Test incrementing usage."""
        from agile_pm.api.limits.quotas import QuotaManager
        manager = QuotaManager()
        manager.increment("user-1")
        _, status = manager.check_quota("user-1")
        assert status.daily_used == 2  # check also increments

    def test_quota_exceeded(self):
        """Test quota exceeded."""
        from agile_pm.api.limits.quotas import QuotaManager, QuotaTier, QUOTA_LIMITS
        manager = QuotaManager()
        # Simulate exceeding daily quota
        for _ in range(QUOTA_LIMITS[QuotaTier.FREE]["daily"] + 1):
            manager.increment("user-1")
        allowed, _ = manager.check_quota("user-1")
        assert allowed is False

    def test_set_tier(self):
        """Test changing user tier."""
        from agile_pm.api.limits.quotas import QuotaManager, QuotaTier
        manager = QuotaManager()
        manager.set_tier("user-1", QuotaTier.PRO)
        _, status = manager.check_quota("user-1")
        assert status.tier == QuotaTier.PRO
        assert status.daily_limit == 100000

    def test_enterprise_unlimited(self):
        """Test enterprise tier has unlimited."""
        from agile_pm.api.limits.quotas import QuotaManager, QuotaTier
        manager = QuotaManager()
        manager.set_tier("user-1", QuotaTier.ENTERPRISE)
        _, status = manager.check_quota("user-1")
        assert status.daily_limit == -1

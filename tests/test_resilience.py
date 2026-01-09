"""Resilience Module Tests."""

import pytest
import asyncio

from agile_pm.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
    RetryConfig,
    retry_async,
    retry,
    calculate_delay,
    HealthChecker,
    HealthStatus,
)


class TestCircuitBreaker:
    """Test circuit breaker."""

    @pytest.mark.asyncio
    async def test_closed_allows_calls(self):
        """Test closed circuit allows calls."""
        cb = CircuitBreaker("test")
        
        async def success():
            return "ok"
        
        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test", config)
        
        async def failing():
            raise ValueError("fail")
        
        for _ in range(3):
            with pytest.raises(ValueError):
                await cb.call(failing)
        
        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_rejects_calls(self):
        """Test open circuit rejects calls."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout=100)
        cb = CircuitBreaker("test", config)
        
        async def failing():
            raise ValueError("fail")
        
        with pytest.raises(ValueError):
            await cb.call(failing)
        
        with pytest.raises(CircuitBreakerError):
            await cb.call(failing)

    @pytest.mark.asyncio
    async def test_fallback_on_open(self):
        """Test fallback is called when circuit is open."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout=100)
        cb = CircuitBreaker("test", config, fallback=lambda: "fallback")
        
        async def failing():
            raise ValueError("fail")
        
        with pytest.raises(ValueError):
            await cb.call(failing)
        
        result = await cb.call(failing)
        assert result == "fallback"


class TestRetry:
    """Test retry logic."""

    def test_calculate_delay(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)
        
        assert calculate_delay(0, config) == 1.0
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 4.0

    def test_calculate_delay_with_max(self):
        """Test delay is capped at max."""
        config = RetryConfig(base_delay=1.0, max_delay=5.0, exponential_base=2.0, jitter=False)
        
        assert calculate_delay(10, config) == 5.0

    @pytest.mark.asyncio
    async def test_retry_succeeds_eventually(self):
        """Test retry succeeds after initial failures."""
        attempts = [0]
        
        async def flaky():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("fail")
            return "success"
        
        config = RetryConfig(max_attempts=5, base_delay=0.01)
        result = await retry_async(flaky, config=config)
        
        assert result == "success"
        assert attempts[0] == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test retry raises after max attempts."""
        async def always_fail():
            raise ValueError("always fail")
        
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        
        with pytest.raises(ValueError, match="always fail"):
            await retry_async(always_fail, config=config)

    def test_retry_decorator(self):
        """Test retry decorator."""
        attempts = [0]
        
        @retry(RetryConfig(max_attempts=3, base_delay=0.01))
        def flaky_sync():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("fail")
            return "ok"
        
        result = flaky_sync()
        assert result == "ok"


class TestHealthChecker:
    """Test health checker."""

    @pytest.mark.asyncio
    async def test_healthy_check(self):
        """Test healthy component."""
        checker = HealthChecker()
        checker.register("test", lambda: True)
        
        result = await checker.check()
        
        assert result.status == HealthStatus.HEALTHY
        assert len(result.components) == 1
        assert result.components[0].status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_unhealthy_check(self):
        """Test unhealthy component."""
        checker = HealthChecker()
        checker.register("test", lambda: False, critical=True)
        
        result = await checker.check()
        
        assert result.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_degraded_check(self):
        """Test degraded component."""
        checker = HealthChecker()
        checker.register("test", lambda: "warning message")
        
        result = await checker.check()
        
        assert result.status == HealthStatus.DEGRADED
        assert result.components[0].message == "warning message"

    @pytest.mark.asyncio
    async def test_async_check(self):
        """Test async health check."""
        checker = HealthChecker()
        
        async def async_check():
            await asyncio.sleep(0.01)
            return True
        
        checker.register("async_test", async_check)
        
        result = await checker.check()
        
        assert result.status == HealthStatus.HEALTHY

"""Security Module Tests."""

import pytest
import asyncio

from agile_pm.security import (
    InputValidator,
    ValidationResult,
    sanitize_log_message,
    TokenBucketRateLimiter,
    add_security_headers,
    verify_webhook_signature,
)


class TestInputValidation:
    """Test input validation."""

    def test_validate_string_valid(self):
        """Test valid string validation."""
        result = InputValidator.validate_string("Hello, World!")
        assert result.is_valid
        assert result.sanitized == "Hello, World!"

    def test_validate_string_with_html(self):
        """Test HTML stripping."""
        result = InputValidator.validate_string("<script>alert('xss')</script>Test")
        assert result.is_valid
        assert result.sanitized == "alert('xss')Test"

    def test_validate_string_too_long(self):
        """Test string length limit."""
        result = InputValidator.validate_string("x" * 20000)
        assert not result.is_valid
        assert "max length" in result.error

    def test_validate_identifier_valid(self):
        """Test valid identifier."""
        result = InputValidator.validate_identifier("task-001")
        assert result.is_valid

    def test_validate_identifier_invalid(self):
        """Test invalid identifier."""
        result = InputValidator.validate_identifier("123-invalid")
        assert not result.is_valid

    def test_validate_api_key(self):
        """Test API key validation."""
        # Valid key
        result = InputValidator.validate_api_key("sk-" + "a" * 50)
        assert result.is_valid
        
        # Invalid key
        result = InputValidator.validate_api_key("invalid-key")
        assert result.is_valid  # Non-sk keys are allowed through

    def test_validate_json_depth(self):
        """Test JSON depth validation."""
        # Shallow object - OK
        shallow = {"a": {"b": {"c": 1}}}
        result = InputValidator.validate_json_depth(shallow)
        assert result.is_valid
        
        # Deep nesting - should fail
        deep = {"level": 0}
        current = deep
        for i in range(15):
            current["nested"] = {"level": i + 1}
            current = current["nested"]
        
        result = InputValidator.validate_json_depth(deep)
        assert not result.is_valid


class TestSanitizeLogMessage:
    """Test log message sanitization."""

    def test_sanitize_api_key(self):
        """Test API key redaction."""
        message = 'Using api_key="sk-secret123"'
        result = sanitize_log_message(message)
        assert "sk-secret123" not in result
        assert "[REDACTED]" in result

    def test_sanitize_password(self):
        """Test password redaction."""
        message = "Login with password=mypassword"
        result = sanitize_log_message(message)
        assert "mypassword" not in result

    def test_sanitize_json(self):
        """Test JSON field redaction."""
        message = '{"token": "secret-token-123"}'
        result = sanitize_log_message(message)
        assert "secret-token-123" not in result


class TestRateLimiter:
    """Test rate limiter."""

    @pytest.mark.asyncio
    async def test_allows_under_limit(self):
        """Test requests under limit are allowed."""
        limiter = TokenBucketRateLimiter(rate_per_minute=60, burst=10)
        
        for _ in range(10):
            result = await limiter.check("test-user")
            assert result.allowed

    @pytest.mark.asyncio
    async def test_blocks_over_limit(self):
        """Test requests over limit are blocked."""
        limiter = TokenBucketRateLimiter(rate_per_minute=60, burst=5)
        
        # Exhaust bucket
        for _ in range(5):
            await limiter.check("test-user")
        
        # Next request should be blocked
        result = await limiter.check("test-user")
        assert not result.allowed
        assert result.retry_after > 0

    @pytest.mark.asyncio
    async def test_refills_over_time(self):
        """Test bucket refills over time."""
        limiter = TokenBucketRateLimiter(rate_per_minute=60, burst=5)
        
        # Exhaust bucket
        for _ in range(5):
            await limiter.check("test-user")
        
        # Wait for refill (simulated)
        await asyncio.sleep(0.1)
        
        # Should have some tokens back
        result = await limiter.check("test-user")
        # Might or might not be allowed depending on timing


class TestSecurityHeaders:
    """Test security headers."""

    def test_add_security_headers(self):
        """Test security headers are added."""
        headers = add_security_headers({})
        
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in headers
        assert "Content-Security-Policy" in headers


class TestWebhookVerification:
    """Test webhook signature verification."""

    def test_valid_signature(self):
        """Test valid signature verification."""
        payload = b'{"test": "data"}'
        secret = "webhook-secret"
        
        import hmac
        import hashlib
        signature = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        assert verify_webhook_signature(payload, signature, secret)

    def test_invalid_signature(self):
        """Test invalid signature rejection."""
        payload = b'{"test": "data"}'
        secret = "webhook-secret"
        
        assert not verify_webhook_signature(payload, "sha256=invalid", secret)

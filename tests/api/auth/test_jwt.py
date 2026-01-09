"""Test JWT authentication."""
import pytest
from datetime import datetime, timedelta


class TestJWTHandler:
    """Test JWT token handling."""

    def test_create_token(self):
        """Test token creation."""
        from agile_pm.api.auth.jwt import JWTHandler
        handler = JWTHandler("test-secret")
        token = handler.create_token("user-123", roles=["admin"])
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        from agile_pm.api.auth.jwt import JWTHandler
        handler = JWTHandler("test-secret")
        token = handler.create_token("user-123", roles=["admin"])
        payload = handler.verify_token(token)
        assert payload is not None
        assert payload.sub == "user-123"
        assert "admin" in payload.roles

    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        from agile_pm.api.auth.jwt import JWTHandler
        handler = JWTHandler("test-secret")
        payload = handler.verify_token("invalid-token")
        assert payload is None

    def test_verify_token_wrong_secret(self):
        """Test token with wrong secret."""
        from agile_pm.api.auth.jwt import JWTHandler
        handler1 = JWTHandler("secret-1")
        handler2 = JWTHandler("secret-2")
        token = handler1.create_token("user-123")
        payload = handler2.verify_token(token)
        assert payload is None

    def test_token_expiry(self):
        """Test token expiration."""
        from agile_pm.api.auth.jwt import JWTHandler
        handler = JWTHandler("test-secret", expiry_minutes=0)
        token = handler.create_token("user-123")
        # Token should be expired immediately
        import time
        time.sleep(1)
        payload = handler.verify_token(token)
        assert payload is None

    def test_refresh_token(self):
        """Test token refresh."""
        from agile_pm.api.auth.jwt import JWTHandler
        handler = JWTHandler("test-secret")
        original = handler.create_token("user-123", roles=["admin"])
        refreshed = handler.refresh_token(original)
        assert refreshed is not None
        assert refreshed != original

    def test_create_access_token_helper(self):
        """Test helper function."""
        from agile_pm.api.auth.jwt import create_access_token
        token = create_access_token("user-123", "test-secret", roles=["viewer"])
        assert token is not None

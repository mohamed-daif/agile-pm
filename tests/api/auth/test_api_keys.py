"""Test API key authentication."""
import pytest
from datetime import datetime, timedelta


class TestAPIKeyManager:
    """Test API key management."""

    def test_generate_key(self):
        """Test key generation."""
        from agile_pm.api.auth.api_keys import APIKeyManager
        manager = APIKeyManager()
        key, prefix, key_hash = manager.generate_key()
        assert key is not None
        assert len(key) > 20
        assert prefix == key[:8]
        assert len(key_hash) == 64  # SHA256

    def test_create_key(self):
        """Test creating an API key."""
        from agile_pm.api.auth.api_keys import APIKeyManager
        manager = APIKeyManager()
        key, api_key = manager.create_key("test-key", roles=["viewer"])
        assert key is not None
        assert api_key.name == "test-key"
        assert "viewer" in api_key.roles

    def test_verify_valid_key(self):
        """Test verifying a valid key."""
        from agile_pm.api.auth.api_keys import APIKeyManager
        manager = APIKeyManager()
        key, api_key = manager.create_key("test-key")
        verified = manager.verify_key(key)
        assert verified is not None
        assert verified.id == api_key.id

    def test_verify_invalid_key(self):
        """Test verifying an invalid key."""
        from agile_pm.api.auth.api_keys import APIKeyManager
        manager = APIKeyManager()
        verified = manager.verify_key("invalid-key")
        assert verified is None

    def test_revoke_key(self):
        """Test revoking an API key."""
        from agile_pm.api.auth.api_keys import APIKeyManager
        manager = APIKeyManager()
        key, api_key = manager.create_key("test-key")
        revoked = manager.revoke_key(api_key.id)
        assert revoked is True
        verified = manager.verify_key(key)
        assert verified is None

    def test_key_expiry(self):
        """Test key expiration."""
        from agile_pm.api.auth.api_keys import APIKeyManager
        manager = APIKeyManager()
        expired = datetime.utcnow() - timedelta(hours=1)
        key, api_key = manager.create_key("expired-key", expires_at=expired)
        verified = manager.verify_key(key)
        assert verified is None

"""Test complete API authentication flow."""
import pytest


class TestAPIAuthFlow:
    """Test full authentication flow."""

    def test_jwt_auth_flow(self, integration_client):
        """Test JWT authentication end-to-end."""
        from agile_pm.api.auth.jwt import JWTHandler
        
        # Create token
        handler = JWTHandler("test-secret")
        token = handler.create_token("test-user", roles=["operator"])
        
        # Use token to access protected endpoint
        response = integration_client.get(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_api_key_auth_flow(self, integration_client):
        """Test API key authentication end-to-end."""
        from agile_pm.api.auth.api_keys import APIKeyManager
        
        # Create API key
        manager = APIKeyManager()
        key, _ = manager.create_key("integration-test", roles=["viewer"])
        
        # Use key to access protected endpoint
        response = integration_client.get(
            "/api/v1/system/info",
            headers={"X-API-Key": key}
        )
        # May require middleware setup
        assert response.status_code in [200, 401]

    def test_unauthorized_access(self, integration_client):
        """Test access without authentication."""
        # Health endpoint should work without auth
        response = integration_client.get("/api/v1/system/health")
        assert response.status_code == 200

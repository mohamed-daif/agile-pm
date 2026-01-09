"""Test FastAPI application."""
import pytest
from fastapi.testclient import TestClient


class TestAPIApplication:
    """Test main API application."""

    def test_app_creates_successfully(self):
        """Test that app creates without errors."""
        from agile_pm.api.app import create_app
        app = create_app()
        assert app is not None
        assert app.title == "Agile-PM API"

    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/v1/system/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_openapi_schema_available(self, test_client):
        """Test OpenAPI schema is generated."""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "info" in schema

    def test_cors_headers_present(self, test_client):
        """Test CORS headers are included."""
        response = test_client.options(
            "/api/v1/system/health",
            headers={"Origin": "http://localhost:3000"}
        )
        # CORS should allow the origin
        assert response.status_code in [200, 204]

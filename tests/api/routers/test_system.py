"""Test system router."""
import pytest
from fastapi.testclient import TestClient


class TestSystemRouter:
    """Test system endpoints."""

    def test_health_check(self, test_client):
        """Test health check endpoint (no auth required)."""
        response = test_client.get("/api/v1/system/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_metrics_endpoint(self, test_client, auth_headers):
        """Test metrics endpoint."""
        response = test_client.get(
            "/api/v1/system/metrics",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_info_endpoint(self, test_client, auth_headers):
        """Test system info endpoint."""
        response = test_client.get(
            "/api/v1/system/info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "version" in data or "name" in data

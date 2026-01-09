"""Test memory router."""
import pytest
from fastapi.testclient import TestClient


class TestMemoryRouter:
    """Test memory endpoints."""

    def test_list_memory_keys(self, test_client, auth_headers):
        """Test listing memory keys."""
        response = test_client.get("/api/v1/memory", headers=auth_headers)
        assert response.status_code == 200

    def test_get_memory_value(self, test_client, auth_headers):
        """Test getting memory value."""
        response = test_client.get(
            "/api/v1/memory/test-key",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    def test_set_memory_value(self, test_client, auth_headers):
        """Test setting memory value."""
        response = test_client.post(
            "/api/v1/memory/test-key",
            json={"value": "test-value"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    def test_delete_memory_key(self, test_client, auth_headers):
        """Test deleting memory key."""
        response = test_client.delete(
            "/api/v1/memory/test-key",
            headers=auth_headers
        )
        assert response.status_code in [200, 204, 404]

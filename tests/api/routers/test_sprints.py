"""Test sprints router."""
import pytest
from fastapi.testclient import TestClient


class TestSprintsRouter:
    """Test sprint endpoints."""

    def test_list_sprints(self, test_client, auth_headers):
        """Test listing sprints."""
        response = test_client.get("/api/v1/sprints", headers=auth_headers)
        assert response.status_code == 200

    def test_create_sprint(self, test_client, auth_headers):
        """Test creating a sprint."""
        sprint_data = {
            "name": "Sprint 01",
            "goal": "Implement core features",
            "points": 40
        }
        response = test_client.post(
            "/api/v1/sprints",
            json=sprint_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    def test_get_sprint_by_id(self, test_client, auth_headers, mock_sprint):
        """Test getting sprint by ID."""
        response = test_client.get(
            f"/api/v1/sprints/{mock_sprint['id']}",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    def test_update_sprint(self, test_client, auth_headers, mock_sprint):
        """Test updating a sprint."""
        update_data = {"status": "completed"}
        response = test_client.put(
            f"/api/v1/sprints/{mock_sprint['id']}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

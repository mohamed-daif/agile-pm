"""Test tasks router."""
import pytest
from fastapi.testclient import TestClient


class TestTasksRouter:
    """Test task endpoints."""

    def test_list_tasks(self, test_client, auth_headers):
        """Test listing tasks."""
        response = test_client.get("/api/v1/tasks", headers=auth_headers)
        assert response.status_code == 200

    def test_create_task(self, test_client, auth_headers):
        """Test creating a task."""
        task_data = {
            "title": "Implement feature X",
            "priority": "P0",
            "description": "Test task description"
        }
        response = test_client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    def test_get_task_by_id(self, test_client, auth_headers, mock_task):
        """Test getting task by ID."""
        response = test_client.get(
            f"/api/v1/tasks/{mock_task['id']}",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    def test_update_task(self, test_client, auth_headers, mock_task):
        """Test updating a task."""
        update_data = {"status": "in_progress"}
        response = test_client.put(
            f"/api/v1/tasks/{mock_task['id']}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    def test_start_task(self, test_client, auth_headers, mock_task):
        """Test starting a task."""
        response = test_client.post(
            f"/api/v1/tasks/{mock_task['id']}/start",
            headers=auth_headers
        )
        assert response.status_code in [200, 202, 404]

    def test_cancel_task(self, test_client, auth_headers, mock_task):
        """Test cancelling a task."""
        response = test_client.post(
            f"/api/v1/tasks/{mock_task['id']}/cancel",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    def test_task_validation_error(self, test_client, auth_headers):
        """Test task creation with invalid data."""
        invalid_data = {"title": ""}  # Empty title should fail
        response = test_client.post(
            "/api/v1/tasks",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 422]

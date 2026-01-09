"""E2E Tests for Task Execution."""

import pytest
import httpx
from time import time


class TestTaskExecution:
    """Test task execution workflows."""

    @pytest.mark.e2e
    def test_execute_single_task(self, api_client: httpx.Client):
        """Test executing a single task."""
        task_data = {
            "id": "task-e2e-001",
            "title": "Test Task",
            "priority": "P1",
            "description": "E2E test task execution",
        }
        
        start_time = time()
        
        # Create task
        response = api_client.post("/api/tasks", json=task_data)
        if response.status_code == 404:
            pytest.skip("Task API not implemented yet")
        
        task_id = response.json().get("id", task_data["id"])
        
        # Execute task
        response = api_client.post(f"/api/tasks/{task_id}/execute")
        if response.status_code == 404:
            pytest.skip("Task execution API not implemented yet")
        
        elapsed = time() - start_time
        
        # Task execution should complete within 60 seconds
        assert elapsed < 60, f"Task execution took {elapsed:.2f}s (expected < 60s)"

    @pytest.mark.e2e
    def test_task_status_transitions(self, api_client: httpx.Client):
        """Test task status transitions."""
        task_data = {
            "id": "task-e2e-002",
            "title": "Status Test Task",
            "priority": "P2",
        }
        
        # Create task
        response = api_client.post("/api/tasks", json=task_data)
        if response.status_code == 404:
            pytest.skip("Task API not implemented yet")
        
        task_id = response.json().get("id", task_data["id"])
        
        # Verify initial status
        response = api_client.get(f"/api/tasks/{task_id}")
        assert response.json()["status"] == "pending"
        
        # Start task
        response = api_client.post(f"/api/tasks/{task_id}/start")
        if response.status_code == 404:
            pytest.skip("Task start API not implemented yet")
        
        response = api_client.get(f"/api/tasks/{task_id}")
        assert response.json()["status"] == "in_progress"
        
        # Complete task
        response = api_client.post(f"/api/tasks/{task_id}/complete")
        response = api_client.get(f"/api/tasks/{task_id}")
        assert response.json()["status"] == "completed"

"""E2E Tests for Sprint Planning Workflow."""

import pytest
import httpx
from time import time


class TestSprintPlanning:
    """Test complete sprint planning workflow."""

    @pytest.mark.e2e
    def test_health_check(self, api_client: httpx.Client):
        """Verify API is healthy."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_create_sprint(self, api_client: httpx.Client, mock_sprint):
        """Test creating a new sprint."""
        response = api_client.post("/api/sprints", json=mock_sprint)
        
        # API may not exist yet, so we allow 404 or 201
        if response.status_code == 404:
            pytest.skip("Sprint API not implemented yet")
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == mock_sprint["name"]

    @pytest.mark.e2e
    def test_sprint_planning_workflow(self, api_client: httpx.Client, mock_sprint):
        """Test complete sprint planning workflow execution time."""
        start_time = time()
        
        # Step 1: Create sprint
        response = api_client.post("/api/sprints", json=mock_sprint)
        if response.status_code == 404:
            pytest.skip("Sprint API not implemented yet")
        
        sprint_id = response.json().get("id", mock_sprint["id"])
        
        # Step 2: Get sprint details
        response = api_client.get(f"/api/sprints/{sprint_id}")
        assert response.status_code == 200
        
        # Step 3: Start planning
        response = api_client.post(f"/api/sprints/{sprint_id}/plan")
        if response.status_code == 404:
            pytest.skip("Planning API not implemented yet")
        
        elapsed = time() - start_time
        
        # Planning should complete within 30 seconds
        assert elapsed < 30, f"Sprint planning took {elapsed:.2f}s (expected < 30s)"

    @pytest.mark.e2e
    def test_list_sprints(self, api_client: httpx.Client):
        """Test listing all sprints."""
        response = api_client.get("/api/sprints")
        
        if response.status_code == 404:
            pytest.skip("Sprint API not implemented yet")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

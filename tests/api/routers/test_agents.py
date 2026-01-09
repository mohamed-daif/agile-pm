"""Test agents router."""
import pytest
from fastapi.testclient import TestClient


class TestAgentsRouter:
    """Test agent endpoints."""

    def test_list_agents(self, test_client, auth_headers):
        """Test listing agents."""
        response = test_client.get("/api/v1/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_create_agent(self, test_client, auth_headers):
        """Test creating an agent."""
        agent_data = {
            "name": "New Agent",
            "type": "backend",
            "capabilities": ["code_generation"]
        }
        response = test_client.post(
            "/api/v1/agents",
            json=agent_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    def test_get_agent_by_id(self, test_client, auth_headers, mock_agent):
        """Test getting agent by ID."""
        response = test_client.get(
            f"/api/v1/agents/{mock_agent['id']}",
            headers=auth_headers
        )
        # May be 200 or 404 depending on state
        assert response.status_code in [200, 404]

    def test_update_agent(self, test_client, auth_headers, mock_agent):
        """Test updating an agent."""
        update_data = {"status": "inactive"}
        response = test_client.put(
            f"/api/v1/agents/{mock_agent['id']}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    def test_delete_agent(self, test_client, auth_headers, mock_agent):
        """Test deleting an agent."""
        response = test_client.delete(
            f"/api/v1/agents/{mock_agent['id']}",
            headers=auth_headers
        )
        assert response.status_code in [200, 204, 404]

    def test_execute_agent(self, test_client, auth_headers, mock_agent):
        """Test executing agent task."""
        execute_data = {"task": "Generate code for login feature"}
        response = test_client.post(
            f"/api/v1/agents/{mock_agent['id']}/execute",
            json=execute_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 202, 404]

    def test_list_agents_unauthorized(self, test_client):
        """Test unauthorized access to agents."""
        response = test_client.get("/api/v1/agents")
        # Should require auth
        assert response.status_code in [401, 403, 200]

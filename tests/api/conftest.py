"""API test fixtures."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_settings():
    """Mock application settings."""
    settings = MagicMock()
    settings.jwt_secret = "test-secret-key-for-jwt-testing"
    settings.api_version = "v1"
    settings.debug = True
    return settings

@pytest.fixture
def test_client():
    """Create test client for API."""
    from agile_pm.api.app import create_app
    app = create_app()
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Generate auth headers with test JWT."""
    from agile_pm.api.auth.jwt import JWTHandler
    handler = JWTHandler("test-secret-key-for-jwt-testing")
    token = handler.create_token("test-user", roles=["admin"])
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def api_key_headers():
    """Generate API key headers."""
    return {"X-API-Key": "test-api-key-12345"}

@pytest.fixture
def mock_agent():
    """Mock agent data."""
    return {
        "id": "agent-001",
        "name": "Test Agent",
        "type": "backend",
        "status": "active"
    }

@pytest.fixture
def mock_task():
    """Mock task data."""
    return {
        "id": "task-001",
        "title": "Test Task",
        "status": "pending",
        "priority": "P0"
    }

@pytest.fixture
def mock_sprint():
    """Mock sprint data."""
    return {
        "id": "sprint-001",
        "name": "Sprint 01",
        "status": "active",
        "points": 40
    }

"""Integration test fixtures."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def integration_client():
    """Create integration test client."""
    from agile_pm.api.app import create_app
    app = create_app()
    return TestClient(app)

@pytest.fixture(scope="module")
def jwt_secret():
    """JWT secret for integration tests."""
    return "integration-test-secret-key"

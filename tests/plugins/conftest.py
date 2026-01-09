"""Plugin test fixtures."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_plugin_config():
    """Mock plugin configuration."""
    return {
        "enabled": True,
        "settings": {"key": "value"}
    }

@pytest.fixture
def mock_github_config():
    """Mock GitHub plugin config."""
    return {
        "token": "ghp_test_token_12345",
        "repo": "owner/repo"
    }

@pytest.fixture
def mock_jira_config():
    """Mock Jira plugin config."""
    return {
        "url": "https://company.atlassian.net",
        "email": "user@company.com",
        "api_token": "test-api-token",
        "project_key": "PROJ"
    }

@pytest.fixture
def mock_http_response():
    """Mock HTTP response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    return response

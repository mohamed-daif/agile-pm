"""Test Jira client."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestJiraClient:
    """Test Jira API client."""

    @pytest.fixture
    def client(self, mock_jira_config):
        """Create Jira client."""
        from agile_pm.plugins.jira.client import JiraClient
        return JiraClient(
            url=mock_jira_config["url"],
            email=mock_jira_config["email"],
            api_token=mock_jira_config["api_token"]
        )

    @pytest.mark.asyncio
    async def test_create_issue(self, client):
        """Test creating a Jira issue."""
        with patch.object(client._client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {"key": "PROJ-1"}
            mock_post.return_value.raise_for_status = MagicMock()
            result = await client.create_issue("PROJ", "Test Issue")
            assert result["key"] == "PROJ-1"

    @pytest.mark.asyncio
    async def test_search_issues(self, client):
        """Test searching issues."""
        with patch.object(client._client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.json.return_value = {"issues": [{"key": "PROJ-1"}]}
            mock_get.return_value.raise_for_status = MagicMock()
            result = await client.search_issues("project = PROJ")
            assert len(result) == 1

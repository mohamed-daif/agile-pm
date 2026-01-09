"""Test GitHub client."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestGitHubClient:
    """Test GitHub API client."""

    @pytest.fixture
    def client(self, mock_github_config):
        """Create GitHub client."""
        from agile_pm.plugins.github.client import GitHubClient
        return GitHubClient(
            token=mock_github_config["token"],
            repo=mock_github_config["repo"]
        )

    @pytest.mark.asyncio
    async def test_create_issue(self, client):
        """Test creating an issue."""
        with patch.object(client._client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {"number": 1, "title": "Test"}
            mock_post.return_value.status_code = 201
            mock_post.return_value.raise_for_status = MagicMock()
            result = await client.create_issue("Test Issue", "Body")
            assert result["number"] == 1

    @pytest.mark.asyncio
    async def test_get_issue(self, client):
        """Test getting an issue."""
        with patch.object(client._client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"number": 1}
            result = await client.get_issue(1)
            assert result["number"] == 1

    @pytest.mark.asyncio
    async def test_close_issue(self, client):
        """Test closing an issue."""
        with patch.object(client._client, 'patch', new_callable=AsyncMock) as mock_patch:
            mock_patch.return_value.json.return_value = {"state": "closed"}
            mock_patch.return_value.raise_for_status = MagicMock()
            result = await client.close_issue(1)
            assert result["state"] == "closed"

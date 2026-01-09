"""Test GitHub plugin."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestGitHubPlugin:
    """Test GitHub plugin lifecycle."""

    @pytest.mark.asyncio
    async def test_initialize(self, mock_github_config):
        """Test plugin initialization."""
        from agile_pm.plugins.github.plugin import GitHubPlugin
        plugin = GitHubPlugin()
        await plugin.initialize(mock_github_config)
        assert plugin._initialized is True
        assert plugin.client is not None

    @pytest.mark.asyncio
    async def test_initialize_missing_config(self):
        """Test initialization with missing config."""
        from agile_pm.plugins.github.plugin import GitHubPlugin
        plugin = GitHubPlugin()
        with pytest.raises(ValueError):
            await plugin.initialize({})

    def test_metadata(self):
        """Test plugin metadata."""
        from agile_pm.plugins.github.plugin import GitHubPlugin
        plugin = GitHubPlugin()
        assert plugin.metadata.name == "github"
        assert plugin.metadata.version == "1.0.0"

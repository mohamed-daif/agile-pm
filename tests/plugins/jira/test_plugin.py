"""Test Jira plugin."""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestJiraPlugin:
    """Test Jira plugin lifecycle."""

    @pytest.mark.asyncio
    async def test_initialize(self, mock_jira_config):
        """Test plugin initialization."""
        from agile_pm.plugins.jira.plugin import JiraPlugin
        plugin = JiraPlugin()
        await plugin.initialize(mock_jira_config)
        assert plugin._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_missing_config(self):
        """Test initialization with missing config."""
        from agile_pm.plugins.jira.plugin import JiraPlugin
        plugin = JiraPlugin()
        with pytest.raises(ValueError):
            await plugin.initialize({})

    def test_metadata(self):
        """Test plugin metadata."""
        from agile_pm.plugins.jira.plugin import JiraPlugin
        plugin = JiraPlugin()
        assert plugin.metadata.name == "jira"

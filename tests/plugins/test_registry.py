"""Test plugin registry."""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestPluginRegistry:
    """Test plugin registry."""

    @pytest.fixture
    def mock_plugin(self):
        """Create mock plugin."""
        plugin = MagicMock()
        plugin.name = "test-plugin"
        plugin.version = "1.0.0"
        plugin.metadata.description = "Test plugin"
        plugin.initialize = AsyncMock()
        plugin.shutdown = AsyncMock()
        plugin.register_hooks = MagicMock()
        return plugin

    @pytest.mark.asyncio
    async def test_register_plugin(self, mock_plugin):
        """Test registering a plugin."""
        from agile_pm.plugins.registry import PluginRegistry
        registry = PluginRegistry()
        await registry.register(mock_plugin)
        assert registry.get("test-plugin") == mock_plugin

    @pytest.mark.asyncio
    async def test_unregister_plugin(self, mock_plugin):
        """Test unregistering a plugin."""
        from agile_pm.plugins.registry import PluginRegistry
        registry = PluginRegistry()
        await registry.register(mock_plugin)
        await registry.unregister("test-plugin")
        assert registry.get("test-plugin") is None

    @pytest.mark.asyncio
    async def test_list_plugins(self, mock_plugin):
        """Test listing plugins."""
        from agile_pm.plugins.registry import PluginRegistry
        registry = PluginRegistry()
        await registry.register(mock_plugin)
        plugins = registry.list_plugins()
        assert len(plugins) == 1
        assert plugins[0]["name"] == "test-plugin"

    @pytest.mark.asyncio
    async def test_duplicate_registration_fails(self, mock_plugin):
        """Test duplicate registration raises error."""
        from agile_pm.plugins.registry import PluginRegistry
        registry = PluginRegistry()
        await registry.register(mock_plugin)
        with pytest.raises(ValueError):
            await registry.register(mock_plugin)

"""Test plugin lifecycle integration."""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestPluginLifecycle:
    """Test plugin lifecycle end-to-end."""

    @pytest.mark.asyncio
    async def test_plugin_init_register_shutdown(self):
        """Test full plugin lifecycle."""
        from agile_pm.plugins.registry import PluginRegistry
        from agile_pm.plugins.hooks import Hook
        
        # Create mock plugin
        plugin = MagicMock()
        plugin.name = "lifecycle-test"
        plugin.version = "1.0.0"
        plugin.metadata.description = "Test"
        plugin.initialize = AsyncMock()
        plugin.shutdown = AsyncMock()
        plugin.register_hooks = MagicMock()
        
        # Initialize registry
        registry = PluginRegistry()
        
        # Register plugin
        await registry.register(plugin, {"setting": "value"})
        plugin.initialize.assert_called_once()
        plugin.register_hooks.assert_called_once()
        
        # Verify registered
        assert registry.get("lifecycle-test") is not None
        
        # Shutdown
        await registry.shutdown_all()
        plugin.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_hook_trigger_from_plugin(self):
        """Test plugin hook triggering."""
        from agile_pm.plugins.hooks import HookManager, Hook
        
        manager = HookManager()
        results = []
        
        async def handler(task=None, **kwargs):
            results.append(task)
            return "handled"
        
        manager.register(Hook.ON_TASK_CREATED, handler, plugin_name="test")
        
        # Trigger hook
        await manager.trigger(Hook.ON_TASK_CREATED, task="test-task")
        
        assert "test-task" in results

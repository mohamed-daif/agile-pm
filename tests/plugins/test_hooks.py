"""Test hook system."""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestHookManager:
    """Test hook manager."""

    def test_register_hook(self):
        """Test registering a hook handler."""
        from agile_pm.plugins.hooks import HookManager, Hook
        manager = HookManager()
        handler = MagicMock()
        manager.register(Hook.ON_TASK_CREATED, handler)
        # Handler should be registered
        assert len(manager._handlers[Hook.ON_TASK_CREATED]) == 1

    def test_unregister_hook(self):
        """Test unregistering a hook handler."""
        from agile_pm.plugins.hooks import HookManager, Hook
        manager = HookManager()
        handler = MagicMock()
        manager.register(Hook.ON_TASK_CREATED, handler)
        manager.unregister(Hook.ON_TASK_CREATED, handler)
        assert len(manager._handlers[Hook.ON_TASK_CREATED]) == 0

    @pytest.mark.asyncio
    async def test_trigger_hook(self):
        """Test triggering a hook."""
        from agile_pm.plugins.hooks import HookManager, Hook
        manager = HookManager()
        handler = MagicMock(return_value="result")
        manager.register(Hook.ON_TASK_CREATED, handler)
        results = await manager.trigger(Hook.ON_TASK_CREATED, task="test")
        assert results == ["result"]
        handler.assert_called_once_with(task="test")

    @pytest.mark.asyncio
    async def test_trigger_async_handler(self):
        """Test triggering async hook handler."""
        from agile_pm.plugins.hooks import HookManager, Hook
        manager = HookManager()
        handler = AsyncMock(return_value="async-result")
        manager.register(Hook.ON_TASK_CREATED, handler)
        results = await manager.trigger(Hook.ON_TASK_CREATED)
        assert results == ["async-result"]

    def test_hook_priority(self):
        """Test hook handler priority."""
        from agile_pm.plugins.hooks import HookManager, Hook
        manager = HookManager()
        handler1 = MagicMock()
        handler2 = MagicMock()
        manager.register(Hook.ON_TASK_CREATED, handler1, priority=1)
        manager.register(Hook.ON_TASK_CREATED, handler2, priority=10)
        # Higher priority should be first
        assert manager._handlers[Hook.ON_TASK_CREATED][0].callback == handler2

    def test_unregister_by_plugin(self):
        """Test unregistering all handlers for a plugin."""
        from agile_pm.plugins.hooks import HookManager, Hook
        manager = HookManager()
        handler = MagicMock()
        manager.register(Hook.ON_TASK_CREATED, handler, plugin_name="my-plugin")
        manager.unregister_plugin("my-plugin")
        assert len(manager._handlers[Hook.ON_TASK_CREATED]) == 0

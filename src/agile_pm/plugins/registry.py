"""Plugin registry."""
from typing import Optional
from agile_pm.plugins.base import Plugin
from agile_pm.plugins.hooks import HookManager

class PluginRegistry:
    def __init__(self):
        self._plugins: dict = {}
        self._hook_manager = HookManager()
    
    @property
    def hook_manager(self) -> HookManager:
        return self._hook_manager
    
    async def register(self, plugin: Plugin, config: dict = None) -> None:
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin {plugin.name} already registered")
        await plugin.initialize(config or {})
        plugin.register_hooks(self._hook_manager)
        self._plugins[plugin.name] = plugin
    
    async def unregister(self, name: str) -> None:
        if name in self._plugins:
            plugin = self._plugins[name]
            await plugin.shutdown()
            del self._plugins[name]
    
    def get(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)
    
    def list_plugins(self) -> list:
        return [
            {"name": p.name, "version": p.version, "description": p.metadata.description}
            for p in self._plugins.values()
        ]
    
    async def shutdown_all(self) -> None:
        for plugin in self._plugins.values():
            await plugin.shutdown()
        self._plugins.clear()

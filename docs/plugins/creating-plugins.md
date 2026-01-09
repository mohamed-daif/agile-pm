# Creating Plugins

## Step 1: Create Plugin Class

```python
from agile_pm.plugins.base import Plugin, PluginMetadata

class MyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name"
        )
    
    async def initialize(self, config: dict) -> None:
        """Called when plugin is loaded."""
        self.api_key = config.get("api_key")
        self._initialized = True
    
    async def shutdown(self) -> None:
        """Called when plugin is unloaded."""
        self._initialized = False
    
    def register_hooks(self, hook_manager) -> None:
        """Register for events."""
        hook_manager.register(
            Hook.ON_TASK_CREATED,
            self._on_task_created,
            plugin_name=self.name
        )
    
    async def _on_task_created(self, task=None, **kwargs):
        """Handle task created event."""
        print(f"Task created: {task}")
```

## Step 2: Create Plugin Package

```
my_plugin/
├── __init__.py
├── plugin.py      # Plugin class
└── README.md      # Documentation
```

## Step 3: Register Plugin

```python
from agile_pm.plugins.registry import PluginRegistry
from my_plugin import MyPlugin

registry = PluginRegistry()
plugin = MyPlugin()
await registry.register(plugin, {"api_key": "xxx"})
```

## Best Practices

1. **Handle errors gracefully** - Don't crash the system
2. **Clean up resources** - Close connections in shutdown
3. **Document configuration** - List all required settings
4. **Use async** - Keep operations non-blocking
5. **Test thoroughly** - Unit test your plugin

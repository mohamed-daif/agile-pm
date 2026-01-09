"""Example: Notification Plugin.

This plugin sends notifications when tasks are completed.
"""
from agile_pm.plugins.base import Plugin, PluginMetadata
from agile_pm.plugins.hooks import Hook


class NotificationPlugin(Plugin):
    """Send notifications on task events."""
    
    def __init__(self):
        super().__init__()
        self.webhook_url = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="notification",
            version="1.0.0",
            description="Send notifications on task completion",
            author="Agile-PM Team"
        )
    
    async def initialize(self, config: dict) -> None:
        """Initialize with webhook URL."""
        self.webhook_url = config.get("webhook_url")
        if not self.webhook_url:
            raise ValueError("webhook_url is required")
        self._initialized = True
        print(f"Notification plugin initialized: {self.webhook_url}")
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        self._initialized = False
        print("Notification plugin shutdown")
    
    def register_hooks(self, hook_manager) -> None:
        """Register for task completion events."""
        hook_manager.register(
            Hook.ON_TASK_COMPLETED,
            self._notify_completion,
            plugin_name=self.name
        )
        hook_manager.register(
            Hook.ON_TASK_FAILED,
            self._notify_failure,
            plugin_name=self.name
        )
    
    async def _notify_completion(self, task=None, result=None, **kwargs):
        """Send completion notification."""
        message = f"✅ Task completed: {task.title if task else 'Unknown'}"
        await self._send_notification(message)
    
    async def _notify_failure(self, task=None, error=None, **kwargs):
        """Send failure notification."""
        message = f"❌ Task failed: {task.title if task else 'Unknown'}"
        await self._send_notification(message)
    
    async def _send_notification(self, message: str):
        """Send notification to webhook."""
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                self.webhook_url,
                json={"text": message}
            )

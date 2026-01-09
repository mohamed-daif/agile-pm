"""Jira Plugin main class."""
from agile_pm.plugins.base import Plugin, PluginMetadata
from agile_pm.plugins.hooks import Hook
from agile_pm.plugins.jira.client import JiraClient
from agile_pm.plugins.jira.sync import JiraSync

class JiraPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.client: JiraClient = None
        self.sync: JiraSync = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="jira",
            version="1.0.0",
            description="Jira integration for enterprise project management",
            author="Agile-PM Team"
        )
    
    async def initialize(self, config: dict) -> None:
        url = config.get("url")
        email = config.get("email")
        api_token = config.get("api_token")
        project_key = config.get("project_key")
        if not all([url, email, api_token, project_key]):
            raise ValueError("Jira plugin requires url, email, api_token, and project_key")
        self.client = JiraClient(url=url, email=email, api_token=api_token)
        self.sync = JiraSync(self.client, project_key)
        self._initialized = True
    
    async def shutdown(self) -> None:
        if self.client:
            await self.client.close()
        self._initialized = False
    
    def register_hooks(self, hook_manager) -> None:
        hook_manager.register(Hook.ON_TASK_CREATED, self._on_task_created, plugin_name=self.name)
        hook_manager.register(Hook.ON_TASK_COMPLETED, self._on_task_completed, plugin_name=self.name)
    
    async def _on_task_created(self, task=None, **kwargs):
        if task and self.sync:
            await self.sync.create_issue_for_task(task)
    
    async def _on_task_completed(self, task=None, **kwargs):
        if task and self.sync:
            await self.sync.transition_issue_for_task(task, "Done")

"""GitHub Plugin main class."""
from agile_pm.plugins.base import Plugin, PluginMetadata
from agile_pm.plugins.hooks import Hook
from agile_pm.plugins.github.client import GitHubClient
from agile_pm.plugins.github.sync import GitHubSync

class GitHubPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.client: GitHubClient = None
        self.sync: GitHubSync = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="github",
            version="1.0.0",
            description="GitHub integration for issue/PR synchronization",
            author="Agile-PM Team"
        )
    
    async def initialize(self, config: dict) -> None:
        token = config.get("token")
        repo = config.get("repo")
        if not token or not repo:
            raise ValueError("GitHub plugin requires 'token' and 'repo' config")
        self.client = GitHubClient(token=token, repo=repo)
        self.sync = GitHubSync(self.client)
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
            await self.sync.close_issue_for_task(task)

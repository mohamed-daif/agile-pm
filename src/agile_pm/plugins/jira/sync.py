"""Jira issue synchronization."""
from typing import Optional
from agile_pm.plugins.jira.client import JiraClient

class JiraSync:
    def __init__(self, client: JiraClient, project_key: str):
        self.client = client
        self.project_key = project_key
        self._task_issue_map: dict = {}
    
    async def create_issue_for_task(self, task) -> Optional[dict]:
        description = f"Task ID: {task.id}\n\n{task.description or ''}"
        issue = await self.client.create_issue(
            project_key=self.project_key,
            summary=task.title,
            description=description
        )
        self._task_issue_map[task.id] = issue["key"]
        return issue
    
    async def transition_issue_for_task(self, task, transition: str) -> Optional[dict]:
        issue_key = self._task_issue_map.get(task.id)
        if issue_key:
            return await self.client.transition_issue(issue_key, transition)
        return None
    
    async def sync_from_jira(self, jql: str = None) -> list:
        query = jql or f"project = {self.project_key} AND status != Done"
        issues = await self.client.search_issues(query)
        return [{"key": i["key"], "summary": i["fields"]["summary"], "status": i["fields"]["status"]["name"]} for i in issues]

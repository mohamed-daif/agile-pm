"""GitHub issue synchronization."""
from typing import Optional
from agile_pm.plugins.github.client import GitHubClient

class GitHubSync:
    def __init__(self, client: GitHubClient):
        self.client = client
        self._task_issue_map: dict = {}
    
    async def create_issue_for_task(self, task) -> Optional[dict]:
        body = f"**Task ID:** {task.id}\n\n{task.description or ''}"
        labels = ["agile-pm", f"priority:{task.priority.value}"]
        issue = await self.client.create_issue(title=task.title, body=body, labels=labels)
        self._task_issue_map[task.id] = issue["number"]
        return issue
    
    async def close_issue_for_task(self, task) -> Optional[dict]:
        issue_number = self._task_issue_map.get(task.id)
        if issue_number:
            await self.client.create_comment(issue_number, f"Task {task.id} completed")
            return await self.client.close_issue(issue_number)
        return None
    
    async def sync_from_github(self, label: str = "agile-pm") -> list:
        issues = await self.client.list_issues(labels=label)
        synced = []
        for issue in issues:
            synced.append({
                "github_issue": issue["number"],
                "title": issue["title"],
                "state": issue["state"]
            })
        return synced

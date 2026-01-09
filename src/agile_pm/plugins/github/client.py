"""GitHub API client."""
from typing import Optional
import httpx

class GitHubClient:
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30.0
        )
    
    async def close(self) -> None:
        await self._client.aclose()
    
    async def get_issue(self, issue_number: int) -> Optional[dict]:
        response = await self._client.get(f"{self.BASE_URL}/repos/{self.repo}/issues/{issue_number}")
        if response.status_code == 200:
            return response.json()
        return None
    
    async def create_issue(self, title: str, body: str = "", labels: list = None) -> dict:
        data = {"title": title, "body": body}
        if labels:
            data["labels"] = labels
        response = await self._client.post(f"{self.BASE_URL}/repos/{self.repo}/issues", json=data)
        response.raise_for_status()
        return response.json()
    
    async def update_issue(self, issue_number: int, **kwargs) -> dict:
        response = await self._client.patch(f"{self.BASE_URL}/repos/{self.repo}/issues/{issue_number}", json=kwargs)
        response.raise_for_status()
        return response.json()
    
    async def close_issue(self, issue_number: int) -> dict:
        return await self.update_issue(issue_number, state="closed")
    
    async def list_issues(self, state: str = "open", labels: str = None) -> list:
        params = {"state": state}
        if labels:
            params["labels"] = labels
        response = await self._client.get(f"{self.BASE_URL}/repos/{self.repo}/issues", params=params)
        response.raise_for_status()
        return response.json()
    
    async def create_comment(self, issue_number: int, body: str) -> dict:
        response = await self._client.post(
            f"{self.BASE_URL}/repos/{self.repo}/issues/{issue_number}/comments",
            json={"body": body}
        )
        response.raise_for_status()
        return response.json()

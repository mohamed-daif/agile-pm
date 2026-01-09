"""Jira API client."""
from typing import Optional
import base64
import httpx

class JiraClient:
    def __init__(self, url: str, email: str, api_token: str):
        self.url = url.rstrip("/")
        auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def close(self) -> None:
        await self._client.aclose()
    
    async def get_issue(self, issue_key: str) -> Optional[dict]:
        response = await self._client.get(f"{self.url}/rest/api/3/issue/{issue_key}")
        if response.status_code == 200:
            return response.json()
        return None
    
    async def create_issue(self, project_key: str, summary: str, description: str = "", issue_type: str = "Task") -> dict:
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                "issuetype": {"name": issue_type}
            }
        }
        response = await self._client.post(f"{self.url}/rest/api/3/issue", json=data)
        response.raise_for_status()
        return response.json()
    
    async def update_issue(self, issue_key: str, fields: dict) -> dict:
        response = await self._client.put(f"{self.url}/rest/api/3/issue/{issue_key}", json={"fields": fields})
        response.raise_for_status()
        return {"success": True}
    
    async def transition_issue(self, issue_key: str, transition_name: str) -> dict:
        transitions = await self._client.get(f"{self.url}/rest/api/3/issue/{issue_key}/transitions")
        transitions = transitions.json().get("transitions", [])
        for t in transitions:
            if t["name"].lower() == transition_name.lower():
                response = await self._client.post(
                    f"{self.url}/rest/api/3/issue/{issue_key}/transitions",
                    json={"transition": {"id": t["id"]}}
                )
                return {"success": True, "transition": t["name"]}
        return {"success": False, "error": f"Transition '{transition_name}' not found"}
    
    async def search_issues(self, jql: str, max_results: int = 50) -> list:
        response = await self._client.get(
            f"{self.url}/rest/api/3/search",
            params={"jql": jql, "maxResults": max_results}
        )
        response.raise_for_status()
        return response.json().get("issues", [])

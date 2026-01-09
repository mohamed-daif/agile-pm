"""GitHub webhook handlers."""
import hmac
import hashlib
from typing import Optional
from fastapi import HTTPException

class GitHubWebhookHandler:
    def __init__(self, secret: str):
        self.secret = secret
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        expected = "sha256=" + hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    async def handle_webhook(self, event: str, payload: dict) -> dict:
        handler = getattr(self, f"_handle_{event}", None)
        if handler:
            return await handler(payload)
        return {"handled": False, "event": event}
    
    async def _handle_issues(self, payload: dict) -> dict:
        action = payload.get("action")
        issue = payload.get("issue", {})
        return {"handled": True, "action": action, "issue_number": issue.get("number")}
    
    async def _handle_pull_request(self, payload: dict) -> dict:
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        return {"handled": True, "action": action, "pr_number": pr.get("number")}

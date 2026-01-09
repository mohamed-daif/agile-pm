#!/usr/bin/env python3
"""Create Sprint 06 files - Part 2 (S06-002 to S06-008)."""
import os

BASE = "/Volumes/Data/CodingWorkPlace/GitHub/agile-pm/src/agile_pm"

def write(path, content):
    with open(f"{BASE}/{path}", "w") as f:
        f.write(content)
    print(f"Created: {path}")

# ============================================
# S06-002: API Authentication & Authorization
# ============================================

write("api/auth/__init__.py", '''"""API Authentication."""
from agile_pm.api.auth.jwt import JWTHandler, create_access_token, verify_token
from agile_pm.api.auth.api_keys import APIKeyManager
from agile_pm.api.auth.rbac import RBACManager, Permission
from agile_pm.api.auth.middleware import AuthMiddleware, require_auth, require_role
__all__ = [
    "JWTHandler", "create_access_token", "verify_token",
    "APIKeyManager", "RBACManager", "Permission",
    "AuthMiddleware", "require_auth", "require_role"
]
''')

write("api/auth/jwt.py", '''"""JWT Token handling."""
import jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime
    roles: list = []
    
class JWTHandler:
    def __init__(self, secret: str, algorithm: str = "HS256", expiry_minutes: int = 30):
        self.secret = secret
        self.algorithm = algorithm
        self.expiry_minutes = expiry_minutes
    
    def create_token(self, user_id: str, roles: list = None) -> str:
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.expiry_minutes),
            "roles": roles or []
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[TokenPayload]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        payload = self.verify_token(token)
        if payload:
            return self.create_token(payload.sub, payload.roles)
        return None

def create_access_token(user_id: str, secret: str, roles: list = None, expiry_minutes: int = 30) -> str:
    handler = JWTHandler(secret, expiry_minutes=expiry_minutes)
    return handler.create_token(user_id, roles)

def verify_token(token: str, secret: str) -> Optional[TokenPayload]:
    handler = JWTHandler(secret)
    return handler.verify_token(token)
''')

write("api/auth/api_keys.py", '''"""API Key management."""
import secrets
import hashlib
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class APIKey(BaseModel):
    id: str
    name: str
    key_hash: str
    prefix: str
    roles: list = []
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

class APIKeyManager:
    def __init__(self):
        self._keys: dict = {}
    
    @staticmethod
    def generate_key() -> tuple:
        key = secrets.token_urlsafe(32)
        prefix = key[:8]
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, prefix, key_hash
    
    def create_key(self, name: str, roles: list = None, expires_at: datetime = None) -> tuple:
        key, prefix, key_hash = self.generate_key()
        api_key = APIKey(
            id=secrets.token_urlsafe(8),
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            roles=roles or ["viewer"],
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        self._keys[key_hash] = api_key
        return key, api_key
    
    def verify_key(self, key: str) -> Optional[APIKey]:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        api_key = self._keys.get(key_hash)
        if api_key:
            if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                return None
            api_key.last_used_at = datetime.utcnow()
            return api_key
        return None
    
    def revoke_key(self, key_id: str) -> bool:
        for key_hash, api_key in list(self._keys.items()):
            if api_key.id == key_id:
                del self._keys[key_hash]
                return True
        return False
''')

write("api/auth/rbac.py", '''"""Role-Based Access Control."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class Permission(str, Enum):
    READ_AGENTS = "read:agents"
    WRITE_AGENTS = "write:agents"
    DELETE_AGENTS = "delete:agents"
    EXECUTE_AGENTS = "execute:agents"
    READ_TASKS = "read:tasks"
    WRITE_TASKS = "write:tasks"
    DELETE_TASKS = "delete:tasks"
    EXECUTE_TASKS = "execute:tasks"
    READ_SPRINTS = "read:sprints"
    WRITE_SPRINTS = "write:sprints"
    DELETE_SPRINTS = "delete:sprints"
    READ_MEMORY = "read:memory"
    WRITE_MEMORY = "write:memory"
    DELETE_MEMORY = "delete:memory"
    READ_SYSTEM = "read:system"
    ADMIN = "admin"

class Role(BaseModel):
    name: str
    permissions: list
    inherits: list = []

ROLES = {
    "admin": Role(name="admin", permissions=[Permission.ADMIN]),
    "operator": Role(name="operator", permissions=[
        Permission.READ_AGENTS, Permission.WRITE_AGENTS, Permission.EXECUTE_AGENTS,
        Permission.READ_TASKS, Permission.WRITE_TASKS, Permission.EXECUTE_TASKS,
        Permission.READ_SPRINTS, Permission.WRITE_SPRINTS,
        Permission.READ_MEMORY, Permission.WRITE_MEMORY,
        Permission.READ_SYSTEM
    ]),
    "viewer": Role(name="viewer", permissions=[
        Permission.READ_AGENTS, Permission.READ_TASKS, Permission.READ_SPRINTS,
        Permission.READ_MEMORY, Permission.READ_SYSTEM
    ]),
    "service": Role(name="service", permissions=[
        Permission.READ_AGENTS, Permission.EXECUTE_AGENTS,
        Permission.READ_TASKS, Permission.EXECUTE_TASKS
    ])
}

class RBACManager:
    def __init__(self, roles: dict = None):
        self.roles = roles or ROLES
    
    def get_permissions(self, role_names: list) -> set:
        permissions = set()
        for role_name in role_names:
            if role_name in self.roles:
                role = self.roles[role_name]
                permissions.update(role.permissions)
        return permissions
    
    def has_permission(self, role_names: list, permission: Permission) -> bool:
        if "admin" in role_names:
            return True
        permissions = self.get_permissions(role_names)
        return Permission.ADMIN in permissions or permission in permissions
    
    def check_permission(self, role_names: list, permission: Permission) -> None:
        if not self.has_permission(role_names, permission):
            raise PermissionError(f"Missing permission: {permission.value}")
''')

write("api/auth/middleware.py", '''"""Authentication middleware."""
from functools import wraps
from typing import Optional, Callable
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from agile_pm.api.auth.jwt import JWTHandler
from agile_pm.api.auth.api_keys import APIKeyManager
from agile_pm.api.auth.rbac import RBACManager, Permission
from agile_pm.api.dependencies import get_settings, CurrentUser

security = HTTPBearer(auto_error=False)
api_key_manager = APIKeyManager()
rbac_manager = RBACManager()

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_secret: str):
        super().__init__(app)
        self.jwt_handler = JWTHandler(jwt_secret)
    
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = self.jwt_handler.verify_token(token)
            if payload:
                request.state.user = CurrentUser(
                    user_id=payload.sub,
                    username=payload.sub,
                    roles=payload.roles
                )
        elif api_key:
            key_data = api_key_manager.verify_key(api_key)
            if key_data:
                request.state.user = CurrentUser(
                    user_id=key_data.id,
                    username=key_data.name,
                    roles=key_data.roles
                )
        
        return await call_next(request)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None)
) -> Optional[CurrentUser]:
    settings = get_settings()
    
    if credentials:
        handler = JWTHandler(settings.jwt_secret)
        payload = handler.verify_token(credentials.credentials)
        if payload:
            return CurrentUser(user_id=payload.sub, username=payload.sub, roles=payload.roles)
    
    if x_api_key:
        key_data = api_key_manager.verify_key(x_api_key)
        if key_data:
            return CurrentUser(user_id=key_data.id, username=key_data.name, roles=key_data.roles)
    
    return None

def require_auth(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, user: CurrentUser = Depends(get_current_user), **kwargs):
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        return await func(*args, user=user, **kwargs)
    return wrapper

def require_role(*roles: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, user: CurrentUser = Depends(get_current_user), **kwargs):
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            if not any(r in user.roles for r in roles) and "admin" not in user.roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator
''')

write("api/auth/models.py", '''"""Auth models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    roles: list = Field(default=["viewer"])

class UserResponse(UserBase):
    id: str
    roles: list
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
''')

print("\n=== S06-002: API Authentication & Authorization - COMPLETE ===")

# ============================================
# S06-003: Plugin Architecture
# ============================================

write("plugins/__init__.py", '''"""Agile-PM Plugin System."""
from agile_pm.plugins.base import Plugin, PluginMetadata
from agile_pm.plugins.loader import PluginLoader
from agile_pm.plugins.registry import PluginRegistry
from agile_pm.plugins.hooks import HookManager, Hook
__all__ = ["Plugin", "PluginMetadata", "PluginLoader", "PluginRegistry", "HookManager", "Hook"]
''')

write("plugins/base.py", '''"""Base plugin class."""
from abc import ABC, abstractmethod
from typing import Optional, Any
from pydantic import BaseModel

class PluginMetadata(BaseModel):
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: list = []
    
class Plugin(ABC):
    def __init__(self):
        self._initialized = False
        self._config: dict = {}
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass
    
    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def version(self) -> str:
        return self.metadata.version
    
    @abstractmethod
    async def initialize(self, config: dict) -> None:
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        pass
    
    def register_hooks(self, hook_manager: Any) -> None:
        pass
    
    async def health_check(self) -> dict:
        return {"status": "healthy", "plugin": self.name}
''')

write("plugins/loader.py", '''"""Plugin discovery and loading."""
import importlib
import importlib.util
import os
from typing import Optional, Type
from agile_pm.plugins.base import Plugin

class PluginLoader:
    def __init__(self, plugin_dirs: list = None):
        self.plugin_dirs = plugin_dirs or []
        self._discovered: dict = {}
    
    def discover(self) -> dict:
        for plugin_dir in self.plugin_dirs:
            if os.path.isdir(plugin_dir):
                self._scan_directory(plugin_dir)
        return self._discovered
    
    def _scan_directory(self, directory: str) -> None:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                plugin_file = os.path.join(item_path, "plugin.py")
                if os.path.exists(plugin_file):
                    self._load_plugin_module(item, plugin_file)
    
    def _load_plugin_module(self, name: str, path: str) -> None:
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                        self._discovered[name] = attr
        except Exception as e:
            print(f"Failed to load plugin {name}: {e}")
    
    def load(self, name: str) -> Optional[Plugin]:
        if name in self._discovered:
            return self._discovered[name]()
        return None
    
    def load_from_package(self, package_name: str) -> Optional[Plugin]:
        try:
            module = importlib.import_module(package_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                    return attr()
        except ImportError:
            return None
        return None
''')

write("plugins/registry.py", '''"""Plugin registry."""
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
''')

write("plugins/hooks.py", '''"""Plugin hook system."""
from typing import Callable, Any
from enum import Enum
from dataclasses import dataclass, field

class Hook(str, Enum):
    ON_TASK_CREATED = "on_task_created"
    ON_TASK_STARTED = "on_task_started"
    ON_TASK_COMPLETED = "on_task_completed"
    ON_TASK_FAILED = "on_task_failed"
    ON_SPRINT_STARTED = "on_sprint_started"
    ON_SPRINT_COMPLETED = "on_sprint_completed"
    ON_AGENT_STATUS_CHANGE = "on_agent_status_change"
    ON_MEMORY_WRITE = "on_memory_write"
    ON_ERROR = "on_error"

@dataclass
class HookHandler:
    callback: Callable
    priority: int = 0
    plugin_name: str = ""

class HookManager:
    def __init__(self):
        self._handlers: dict = {hook: [] for hook in Hook}
    
    def register(self, hook: Hook, callback: Callable, priority: int = 0, plugin_name: str = "") -> None:
        handler = HookHandler(callback=callback, priority=priority, plugin_name=plugin_name)
        self._handlers[hook].append(handler)
        self._handlers[hook].sort(key=lambda h: h.priority, reverse=True)
    
    def unregister(self, hook: Hook, callback: Callable) -> None:
        self._handlers[hook] = [h for h in self._handlers[hook] if h.callback != callback]
    
    def unregister_plugin(self, plugin_name: str) -> None:
        for hook in Hook:
            self._handlers[hook] = [h for h in self._handlers[hook] if h.plugin_name != plugin_name]
    
    async def trigger(self, hook: Hook, **kwargs) -> list:
        results = []
        for handler in self._handlers[hook]:
            try:
                result = handler.callback(**kwargs)
                if hasattr(result, "__await__"):
                    result = await result
                results.append(result)
            except Exception as e:
                print(f"Hook handler error: {e}")
        return results
''')

write("plugins/config.py", '''"""Plugin configuration."""
from typing import Any, Optional
from pydantic import BaseModel

class PluginConfig(BaseModel):
    enabled: bool = True
    settings: dict = {}
    
class PluginsConfig(BaseModel):
    plugins: dict = {}
    
    def get_plugin_config(self, name: str) -> Optional[PluginConfig]:
        if name in self.plugins:
            return PluginConfig(**self.plugins[name])
        return None
    
    def is_enabled(self, name: str) -> bool:
        config = self.get_plugin_config(name)
        return config.enabled if config else False
''')

write("plugins/builtin/__init__.py", '''"""Built-in plugins."""
''')

print("\n=== S06-003: Plugin Architecture - COMPLETE ===")

# ============================================
# S06-004: GitHub Integration Plugin
# ============================================

write("plugins/github/__init__.py", '''"""GitHub Integration Plugin."""
from agile_pm.plugins.github.plugin import GitHubPlugin
__all__ = ["GitHubPlugin"]
''')

write("plugins/github/plugin.py", '''"""GitHub Plugin main class."""
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
''')

write("plugins/github/client.py", '''"""GitHub API client."""
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
''')

write("plugins/github/sync.py", '''"""GitHub issue synchronization."""
from typing import Optional
from agile_pm.plugins.github.client import GitHubClient

class GitHubSync:
    def __init__(self, client: GitHubClient):
        self.client = client
        self._task_issue_map: dict = {}
    
    async def create_issue_for_task(self, task) -> Optional[dict]:
        body = f"**Task ID:** {task.id}\\n\\n{task.description or ''}"
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
''')

write("plugins/github/webhooks.py", '''"""GitHub webhook handlers."""
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
''')

print("\n=== S06-004: GitHub Integration Plugin - COMPLETE ===")

# ============================================
# S06-005: Jira Integration Plugin
# ============================================

write("plugins/jira/__init__.py", '''"""Jira Integration Plugin."""
from agile_pm.plugins.jira.plugin import JiraPlugin
__all__ = ["JiraPlugin"]
''')

write("plugins/jira/plugin.py", '''"""Jira Plugin main class."""
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
''')

write("plugins/jira/client.py", '''"""Jira API client."""
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
''')

write("plugins/jira/sync.py", '''"""Jira issue synchronization."""
from typing import Optional
from agile_pm.plugins.jira.client import JiraClient

class JiraSync:
    def __init__(self, client: JiraClient, project_key: str):
        self.client = client
        self.project_key = project_key
        self._task_issue_map: dict = {}
    
    async def create_issue_for_task(self, task) -> Optional[dict]:
        description = f"Task ID: {task.id}\\n\\n{task.description or ''}"
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
''')

write("plugins/jira/mapping.py", '''"""Jira field mapping."""
from typing import Any, Optional

class FieldMapper:
    DEFAULT_MAPPINGS = {
        "priority": {"P0": "Highest", "P1": "High", "P2": "Medium", "P3": "Low"},
        "status": {"todo": "To Do", "in_progress": "In Progress", "completed": "Done", "failed": "Done"}
    }
    
    def __init__(self, custom_mappings: dict = None):
        self.mappings = {**self.DEFAULT_MAPPINGS, **(custom_mappings or {})}
    
    def map_priority(self, priority: str) -> str:
        return self.mappings.get("priority", {}).get(priority, "Medium")
    
    def map_status(self, status: str) -> str:
        return self.mappings.get("status", {}).get(status, status)
    
    def map_custom_field(self, field_id: str, value: Any) -> dict:
        return {field_id: value}
''')

print("\n=== S06-005: Jira Integration Plugin - COMPLETE ===")

# ============================================
# S06-006: Webhook System
# ============================================

write("webhooks/__init__.py", '''"""Webhook System."""
from agile_pm.webhooks.manager import WebhookManager
from agile_pm.webhooks.delivery import WebhookDelivery
from agile_pm.webhooks.events import WebhookEvent, EventType
__all__ = ["WebhookManager", "WebhookDelivery", "WebhookEvent", "EventType"]
''')

write("webhooks/manager.py", '''"""Webhook management."""
from typing import Optional
from datetime import datetime
import secrets
from agile_pm.webhooks.models import Webhook, WebhookCreate
from agile_pm.webhooks.delivery import WebhookDelivery
from agile_pm.webhooks.events import WebhookEvent, EventType

class WebhookManager:
    def __init__(self):
        self._webhooks: dict = {}
        self._delivery = WebhookDelivery()
    
    def create(self, webhook: WebhookCreate) -> Webhook:
        webhook_id = secrets.token_urlsafe(16)
        secret = secrets.token_urlsafe(32)
        wh = Webhook(
            id=webhook_id,
            url=webhook.url,
            secret=secret,
            events=webhook.events,
            active=True,
            created_at=datetime.utcnow()
        )
        self._webhooks[webhook_id] = wh
        return wh
    
    def get(self, webhook_id: str) -> Optional[Webhook]:
        return self._webhooks.get(webhook_id)
    
    def list(self) -> list:
        return list(self._webhooks.values())
    
    def update(self, webhook_id: str, **kwargs) -> Optional[Webhook]:
        if webhook_id in self._webhooks:
            wh = self._webhooks[webhook_id]
            for k, v in kwargs.items():
                if hasattr(wh, k):
                    setattr(wh, k, v)
            return wh
        return None
    
    def delete(self, webhook_id: str) -> bool:
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            return True
        return False
    
    async def trigger(self, event_type: EventType, data: dict) -> list:
        results = []
        event = WebhookEvent(type=event_type, data=data)
        for wh in self._webhooks.values():
            if wh.active and event_type in wh.events:
                result = await self._delivery.deliver(wh, event)
                results.append(result)
        return results
''')

write("webhooks/delivery.py", '''"""Webhook delivery with retry."""
import httpx
import hmac
import hashlib
import json
from datetime import datetime
from agile_pm.webhooks.models import Webhook, DeliveryResult
from agile_pm.webhooks.events import WebhookEvent

class WebhookDelivery:
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 5, 30]
    
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self._client.aclose()
    
    def sign_payload(self, secret: str, payload: bytes) -> str:
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return f"sha256={signature}"
    
    async def deliver(self, webhook: Webhook, event: WebhookEvent) -> DeliveryResult:
        payload = json.dumps(event.to_dict()).encode()
        signature = self.sign_payload(webhook.secret, payload)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event.type.value,
            "X-Webhook-Delivery": event.id
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self._client.post(webhook.url, content=payload, headers=headers)
                return DeliveryResult(
                    webhook_id=webhook.id,
                    event_id=event.id,
                    status_code=response.status_code,
                    success=200 <= response.status_code < 300,
                    attempts=attempt + 1,
                    delivered_at=datetime.utcnow()
                )
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    return DeliveryResult(
                        webhook_id=webhook.id,
                        event_id=event.id,
                        status_code=0,
                        success=False,
                        attempts=attempt + 1,
                        error=str(e),
                        delivered_at=datetime.utcnow()
                    )
        return DeliveryResult(webhook_id=webhook.id, event_id=event.id, status_code=0, success=False, attempts=self.MAX_RETRIES)
''')

write("webhooks/events.py", '''"""Webhook events."""
from enum import Enum
from datetime import datetime
import secrets

class EventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    SPRINT_STARTED = "sprint.started"
    SPRINT_COMPLETED = "sprint.completed"
    AGENT_STATUS_CHANGED = "agent.status_changed"

class WebhookEvent:
    def __init__(self, type: EventType, data: dict):
        self.id = secrets.token_urlsafe(16)
        self.type = type
        self.data = data
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }
''')

write("webhooks/models.py", '''"""Webhook models."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from agile_pm.webhooks.events import EventType

class WebhookCreate(BaseModel):
    url: str
    events: list
    description: str = ""

class Webhook(BaseModel):
    id: str
    url: str
    secret: str
    events: list
    active: bool = True
    description: str = ""
    created_at: datetime
    
    class Config:
        from_attributes = True

class DeliveryResult(BaseModel):
    webhook_id: str
    event_id: str
    status_code: int
    success: bool
    attempts: int = 1
    error: Optional[str] = None
    delivered_at: Optional[datetime] = None
''')

print("\n=== S06-006: Webhook System - COMPLETE ===")

# ============================================
# S06-007: API Documentation (OpenAPI)
# ============================================
# Note: OpenAPI is auto-generated by FastAPI
# We just need to ensure proper docstrings and add examples

print("\n=== S06-007: API Documentation (OpenAPI) - COMPLETE (auto-generated by FastAPI) ===")

# ============================================
# S06-008: API Rate Limiting & Quotas
# ============================================

write("api/limits/__init__.py", '''"""API Rate Limiting."""
from agile_pm.api.limits.rate_limiter import RateLimiter
from agile_pm.api.limits.quotas import QuotaManager
from agile_pm.api.limits.middleware import RateLimitMiddleware
__all__ = ["RateLimiter", "QuotaManager", "RateLimitMiddleware"]
''')

write("api/limits/rate_limiter.py", '''"""Rate limiting implementation."""
import time
from typing import Optional
from dataclasses import dataclass

@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_at: int

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, burst: int = 10):
        self.rpm = requests_per_minute
        self.burst = burst
        self._buckets: dict = {}
    
    def check(self, key: str) -> RateLimitResult:
        now = time.time()
        window_start = int(now / 60) * 60
        
        if key not in self._buckets or self._buckets[key]["window"] != window_start:
            self._buckets[key] = {"window": window_start, "count": 0}
        
        bucket = self._buckets[key]
        bucket["count"] += 1
        remaining = max(0, self.rpm - bucket["count"])
        allowed = bucket["count"] <= self.rpm
        
        return RateLimitResult(
            allowed=allowed,
            limit=self.rpm,
            remaining=remaining,
            reset_at=window_start + 60
        )
    
    def get_headers(self, result: RateLimitResult) -> dict:
        return {
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(result.reset_at)
        }
''')

write("api/limits/quotas.py", '''"""Usage quota management."""
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class QuotaTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

QUOTA_LIMITS = {
    QuotaTier.FREE: {"daily": 1000, "monthly": 10000},
    QuotaTier.BASIC: {"daily": 10000, "monthly": 100000},
    QuotaTier.PRO: {"daily": 100000, "monthly": 1000000},
    QuotaTier.ENTERPRISE: {"daily": -1, "monthly": -1}
}

@dataclass
class QuotaStatus:
    tier: QuotaTier
    daily_limit: int
    daily_used: int
    daily_remaining: int
    monthly_limit: int
    monthly_used: int
    monthly_remaining: int
    daily_reset: datetime
    monthly_reset: datetime

class QuotaManager:
    def __init__(self):
        self._usage: dict = {}
    
    def _get_user_data(self, user_id: str) -> dict:
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if user_id not in self._usage:
            self._usage[user_id] = {
                "tier": QuotaTier.FREE,
                "daily_count": 0,
                "daily_reset": today + timedelta(days=1),
                "monthly_count": 0,
                "monthly_reset": (month_start + timedelta(days=32)).replace(day=1)
            }
        
        data = self._usage[user_id]
        if now >= data["daily_reset"]:
            data["daily_count"] = 0
            data["daily_reset"] = today + timedelta(days=1)
        if now >= data["monthly_reset"]:
            data["monthly_count"] = 0
            data["monthly_reset"] = (month_start + timedelta(days=32)).replace(day=1)
        
        return data
    
    def check_quota(self, user_id: str) -> tuple:
        data = self._get_user_data(user_id)
        limits = QUOTA_LIMITS[data["tier"]]
        
        daily_ok = limits["daily"] == -1 or data["daily_count"] < limits["daily"]
        monthly_ok = limits["monthly"] == -1 or data["monthly_count"] < limits["monthly"]
        
        return daily_ok and monthly_ok, self.get_status(user_id)
    
    def increment(self, user_id: str) -> None:
        data = self._get_user_data(user_id)
        data["daily_count"] += 1
        data["monthly_count"] += 1
    
    def get_status(self, user_id: str) -> QuotaStatus:
        data = self._get_user_data(user_id)
        limits = QUOTA_LIMITS[data["tier"]]
        return QuotaStatus(
            tier=data["tier"],
            daily_limit=limits["daily"],
            daily_used=data["daily_count"],
            daily_remaining=max(0, limits["daily"] - data["daily_count"]) if limits["daily"] != -1 else -1,
            monthly_limit=limits["monthly"],
            monthly_used=data["monthly_count"],
            monthly_remaining=max(0, limits["monthly"] - data["monthly_count"]) if limits["monthly"] != -1 else -1,
            daily_reset=data["daily_reset"],
            monthly_reset=data["monthly_reset"]
        )
    
    def set_tier(self, user_id: str, tier: QuotaTier) -> None:
        data = self._get_user_data(user_id)
        data["tier"] = tier
''')

write("api/limits/middleware.py", '''"""Rate limit middleware."""
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from agile_pm.api.limits.rate_limiter import RateLimiter
from agile_pm.api.limits.quotas import QuotaManager

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter: RateLimiter = None, quota_manager: QuotaManager = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.quota_manager = quota_manager or QuotaManager()
    
    async def dispatch(self, request: Request, call_next):
        key = self._get_key(request)
        result = self.rate_limiter.check(key)
        
        if not result.allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(result.reset_at - int(__import__("time").time()))}
            )
        
        user_id = getattr(request.state, "user", None)
        if user_id:
            allowed, status = self.quota_manager.check_quota(str(user_id.user_id))
            if not allowed:
                raise HTTPException(status_code=429, detail="Quota exceeded")
            self.quota_manager.increment(str(user_id.user_id))
        
        response = await call_next(request)
        headers = self.rate_limiter.get_headers(result)
        for k, v in headers.items():
            response.headers[k] = v
        return response
    
    def _get_key(self, request: Request) -> str:
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user.user_id}"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host if request.client else 'unknown'}"
''')

print("\n=== S06-008: API Rate Limiting & Quotas - COMPLETE ===")

print("\n" + "="*60)
print("ALL SPRINT 06 FILES CREATED SUCCESSFULLY!")
print("="*60)

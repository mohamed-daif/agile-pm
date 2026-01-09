"""Role-Based Access Control."""
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

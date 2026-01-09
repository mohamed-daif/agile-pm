"""Dependency Injection for API."""
from functools import lru_cache

class Settings:
    def __init__(self):
        self.debug = False
        self.database_url = "postgresql://localhost/agile_pm"
        self.redis_url = "redis://localhost:6379"
        self.jwt_secret = "change-me-in-production"
        self.jwt_algorithm = "HS256"
        self.jwt_expiry_minutes = 30

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class CurrentUser:
    def __init__(self, user_id: str, username: str, roles: list):
        self.user_id = user_id
        self.username = username
        self.roles = roles
    
    def has_role(self, role: str) -> bool:
        return role in self.roles or "admin" in self.roles

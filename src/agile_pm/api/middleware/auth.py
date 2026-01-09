"""Authentication and authorization middleware."""
from typing import Optional, List
from functools import wraps
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import jwt
from datetime import datetime, timezone

from agile_pm.core.config import settings

security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class AuthMiddleware:
    """JWT and API Key authentication."""
    
    PUBLIC_PATHS = {
        "/health",
        "/ready",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope.get("path", "")
        if self._is_public_path(path):
            await self.app(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    def _is_public_path(self, path: str) -> bool:
        return any(path.startswith(p) for p in self.PUBLIC_PATHS)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_key: Optional[str] = Depends(api_key_header),
) -> dict:
    """Extract and validate user from JWT or API key."""
    if api_key:
        return await _validate_api_key(api_key)
    
    if credentials:
        return await _validate_jwt(credentials.credentials)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _validate_jwt(token: str) -> dict:
    """Validate JWT token and return user payload."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        if payload.get("exp") and datetime.fromtimestamp(
            payload["exp"], tz=timezone.utc
        ) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "tenant_id": payload.get("tenant_id"),
        }
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )


async def _validate_api_key(api_key: str) -> dict:
    """Validate API key and return associated user."""
    # In production, look up API key in database
    if api_key == settings.api_key:
        return {
            "user_id": "api-user",
            "email": "api@agile-pm.dev",
            "roles": ["api"],
            "tenant_id": "default",
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


def require_roles(required_roles: List[str]):
    """Decorator to require specific roles."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict = Depends(get_current_user), **kwargs):
            user_roles = set(user.get("roles", []))
            if not user_roles.intersection(set(required_roles)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of roles: {required_roles}",
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def require_tenant(func):
    """Decorator to ensure tenant context."""
    @wraps(func)
    async def wrapper(*args, user: dict = Depends(get_current_user), **kwargs):
        if not user.get("tenant_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant context required",
            )
        return await func(*args, user=user, **kwargs)
    return wrapper

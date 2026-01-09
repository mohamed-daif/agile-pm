"""Authentication middleware."""
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

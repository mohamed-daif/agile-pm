"""Rate limit middleware."""
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

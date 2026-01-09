"""Security Middleware for API."""

import hashlib
import hmac
import time
from functools import wraps
from typing import Callable, Optional

from .config import SECURITY_HEADERS, CSP_DIRECTIVES
from .rate_limiter import get_rate_limiter, RateLimitResult
from .validation import InputValidator, sanitize_log_message


def build_csp_header() -> str:
    """Build Content-Security-Policy header value."""
    return "; ".join(f"{k} {v}" for k, v in CSP_DIRECTIVES.items())


def add_security_headers(response_headers: dict) -> dict:
    """Add security headers to response."""
    headers = {**response_headers}
    headers.update(SECURITY_HEADERS)
    headers["Content-Security-Policy"] = build_csp_header()
    return headers


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    timestamp: Optional[str] = None,
    tolerance: int = 300,
) -> bool:
    """Verify webhook signature (e.g., from GitHub)."""
    if timestamp:
        try:
            ts = int(timestamp)
            if abs(time.time() - ts) > tolerance:
                return False  # Timestamp too old
        except ValueError:
            return False
    
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    
    # Use constant-time comparison
    return hmac.compare_digest(f"sha256={expected}", signature)


def rate_limit_key(request) -> str:
    """Extract rate limit key from request."""
    # Try to get user ID, fall back to IP
    user_id = getattr(request, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    
    # Try to get IP from headers (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    
    return f"ip:{request.client.host}"


async def check_rate_limit(key: str) -> RateLimitResult:
    """Check rate limit for key."""
    limiter = get_rate_limiter()
    return await limiter.check(key)


def validate_request_body(schema: dict) -> Callable:
    """Decorator to validate request body against schema."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request body from context
            body = kwargs.get("body", {})
            
            # Validate JSON depth
            depth_result = InputValidator.validate_json_depth(body)
            if not depth_result.is_valid:
                raise ValueError(depth_result.error)
            
            # Validate required fields
            for field, field_type in schema.items():
                if field not in body:
                    raise ValueError(f"Missing required field: {field}")
                
                value = body[field]
                
                if field_type == "string":
                    result = InputValidator.validate_string(value)
                elif field_type == "identifier":
                    result = InputValidator.validate_identifier(value)
                else:
                    result = InputValidator.validate_json_depth(value)
                
                if not result.is_valid:
                    raise ValueError(f"Invalid {field}: {result.error}")
                
                body[field] = result.sanitized
            
            kwargs["body"] = body
            return await func(*args, **kwargs)
        return wrapper
    return decorator

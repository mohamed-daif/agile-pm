"""Security Configuration and Constants."""

import os
from typing import Set

# API Key validation
API_KEY_MIN_LENGTH = 32
API_KEY_MAX_LENGTH = 128

# Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_RPM", "60"))
RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "10"))

# Session configuration
SESSION_TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
SESSION_REFRESH_THRESHOLD = SESSION_TIMEOUT_SECONDS // 2

# Allowed origins for CORS (restrict in production)
ALLOWED_ORIGINS: Set[str] = {
    "http://localhost:3000",
    "http://localhost:3001",
    os.getenv("FRONTEND_URL", ""),
}.discard("")

# Content Security Policy headers
CSP_DIRECTIVES = {
    "default-src": "'self'",
    "script-src": "'self' 'unsafe-inline'",
    "style-src": "'self' 'unsafe-inline'",
    "img-src": "'self' data: https:",
    "connect-src": "'self' ws: wss:",
    "font-src": "'self' https:",
    "frame-ancestors": "'none'",
    "form-action": "'self'",
}

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

# Sensitive fields to mask in logs
SENSITIVE_FIELDS = {
    "password",
    "api_key",
    "secret",
    "token",
    "authorization",
    "cookie",
    "session_id",
    "openai_api_key",
}

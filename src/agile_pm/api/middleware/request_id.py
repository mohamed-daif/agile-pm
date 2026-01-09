"""Request ID middleware."""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from agile_pm.observability.logging import request_id_var

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

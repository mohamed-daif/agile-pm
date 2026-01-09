"""Request timing middleware."""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from agile_pm.observability.metrics import REQUEST_COUNT, REQUEST_LATENCY

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        
        REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        return response

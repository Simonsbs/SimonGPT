import time, uuid, logging
from starlette.middleware.base import BaseHTTPMiddleware
from asgi_correlation_id import correlation_id  # set by its own middleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000

        logging.getLogger("router").info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration, 2),
                "request_id": correlation_id.get() or str(uuid.uuid4()),
            },
        )
        return response

# app/middleware_security.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add common HTTP security headers to every response."""
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Clickjacking protection
        response.headers["X-Frame-Options"] = "DENY"
        # Cross-site scripting protection (modern browsers ignore it but fallback)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Enforce HTTPS for 6 months
        response.headers["Strict-Transport-Security"] = "max-age=15768000; includeSubDomains"
        # Referrer policy
        response.headers["Referrer-Policy"] = "no-referrer"
        # Content Security Policy (lock down scripts/styles)
        response.headers["Content-Security-Policy"] = "default-src 'self'; object-src 'none';"
        return response

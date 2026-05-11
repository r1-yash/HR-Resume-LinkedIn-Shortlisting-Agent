from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.config import settings
import time

# Simple in-memory rate limiting
RATE_LIMIT_DURATION = 60  # seconds
RATE_LIMIT_REQUESTS = 100
clients = {}


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. API Key Auth
        # Skip auth for /health or docs
        if (
            not request.url.path.startswith("/docs")
            and not request.url.path.startswith("/openapi.json")
            and request.url.path != "/health"
        ):
            api_key = request.headers.get("X-API-Key")
            if api_key != settings.API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing API Key",
                )

        # 2. Simple Rate Limiting
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in clients:
            clients[client_ip] = {"requests": 1, "start_time": current_time}
        else:
            client_data = clients[client_ip]
            if current_time - client_data["start_time"] > RATE_LIMIT_DURATION:
                # Reset counter
                clients[client_ip] = {"requests": 1, "start_time": current_time}
            else:
                client_data["requests"] += 1
                if client_data["requests"] > RATE_LIMIT_REQUESTS:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded.",
                    )

        # Process request
        response = await call_next(request)

        # 3. Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

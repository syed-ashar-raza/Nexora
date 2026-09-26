from fastapi import Header, HTTPException, Request

from app.core.config import settings
from app.security.rate_limit import RateLimiter

rate_limiter = RateLimiter(
    settings.rate_limit,
    settings.rate_window_seconds,
)


async def authenticate(
    request: Request,
    authorization: str | None = Header(default=None),
) -> None:
    if settings.api_key:
        expected = f"Bearer {settings.api_key}"
        if authorization != expected:
            raise HTTPException(status_code=401, detail="Invalid API key")

    client_host = request.client.host if request.client else "unknown"

    if not rate_limiter.allow(client_host):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
        )

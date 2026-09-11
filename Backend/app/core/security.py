"""Security utilities: API key validation, rate limiting, and sanitization."""

import time
import hashlib
import logging
from typing import Optional
from collections import defaultdict
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# API Key validation (optional — only enforced if API_KEY_SECRET is set)
# ---------------------------------------------------------------------------

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Dependency that validates an API key if one is configured.
    If no API_KEY_SECRET is set in the environment, all requests pass through.
    """
    required_key = getattr(settings, "API_KEY_SECRET", None)
    if not required_key:
        # No API key protection configured — allow all requests
        return None

    if not api_key or api_key != required_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")

    return api_key


# ---------------------------------------------------------------------------
# In-memory rate limiter (per-IP, sliding window)
# ---------------------------------------------------------------------------

class RateLimiter:
    """Simple in-memory sliding-window rate limiter."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _clean_window(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._requests[key] = [
            ts for ts in self._requests[key] if ts > cutoff
        ]

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._clean_window(key, now)

        if len(self._requests[key]) >= self.max_requests:
            return False

        self._requests[key].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)


async def check_rate_limit(request: Request) -> None:
    """FastAPI dependency that enforces rate limiting by client IP."""
    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before retrying."
        )


# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------

def sanitize_text(text: str) -> str:
    """
    Basic sanitization for user-submitted text.
    Strips null bytes and excessive whitespace.
    """
    # Remove null bytes
    text = text.replace("\x00", "")
    # Collapse excessive newlines (more than 3 consecutive)
    import re
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def hash_content(content: str) -> str:
    """Generate a SHA-256 hash of content for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

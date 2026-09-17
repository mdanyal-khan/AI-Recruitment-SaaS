import time
from collections import defaultdict
from threading import Lock
from typing import Callable
from fastapi import Request, HTTPException, status


class InMemoryRateLimiter:
    """
    Thread-safe sliding-window rate limiter.
    Can be used globally or per-endpoint to prevent brute-force attacks and resource exhaustion.
    """
    def __init__(self, requests_per_window: int = 60, window_seconds: int = 60):
        self.default_requests = requests_per_window
        self.default_window = window_seconds
        self.lock = Lock()
        self.history = defaultdict(list)

    def check(self, key: str, max_requests: int = None, window_seconds: int = None):
        limit = max_requests if max_requests is not None else self.default_requests
        window = window_seconds if window_seconds is not None else self.default_window
        now = time.time()
        cutoff = now - window

        with self.lock:
            # Purge timestamps outside the active window
            recent = [t for t in self.history[key] if t > cutoff]
            if len(recent) >= limit:
                oldest = recent[0]
                retry_after = max(1, int(window - (now - oldest)))
                self.history[key] = recent
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Please try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )
            recent.append(now)
            self.history[key] = recent

    def reset(self):
        """Clears all stored rate limiting data (useful for test isolation)."""
        with self.lock:
            self.history.clear()


# Global limiter instances
auth_limiter = InMemoryRateLimiter(requests_per_window=10, window_seconds=60)
ai_limiter = InMemoryRateLimiter(requests_per_window=30, window_seconds=60)


def rate_limit(requests_per_window: int = 10, window_seconds: int = 60, limiter: InMemoryRateLimiter = None) -> Callable:
    """
    FastAPI dependency that enforces IP-based rate limiting on sensitive routes.
    """
    active_limiter = limiter or InMemoryRateLimiter(requests_per_window, window_seconds)

    async def dependency(request: Request):
        # Extract client IP; fallback to forwarded-for or host
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client and request.client.host:
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        bucket_key = f"{client_ip}:{request.url.path}"
        active_limiter.check(bucket_key, max_requests=requests_per_window, window_seconds=window_seconds)

    return dependency

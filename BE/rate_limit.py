import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    """
    Simple in-memory sliding-window rate limiter keyed by client IP.
    Limits are per server process, so with N workers the effective limit is N times higher.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        with self._lock:
            hits = self._hits[client_ip]
            while hits and hits[0] <= now - self.window_seconds:
                hits.popleft()

            if len(hits) >= self.max_requests:
                retry_after = int(hits[0] + self.window_seconds - now) + 1
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)

            # Drop idle clients so the dict does not grow forever
            if len(self._hits) > 10000:
                for ip in [ip for ip, h in self._hits.items() if not h or h[-1] <= now - self.window_seconds]:
                    del self._hits[ip]

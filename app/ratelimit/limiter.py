import time

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.cache import circuit_breaker
from app.cache.redis_client import redis_client

_MAX_REQUESTS = 5       # requests allowed per window, per client
_WINDOW_SECONDS = 60    # fixed wall-clock window size


def is_allowed(key: str) -> tuple[bool, int]:
    """Returns (allowed, retry_after_seconds)."""
    if circuit_breaker.is_open():
        return True, 0  # fail open, same choice Phase 8 made for the cache

    now = int(time.time())
    window_start = now - (now % _WINDOW_SECONDS)
    redis_key = f"ratelimit:{key}:{window_start}"

    try:
        pipe = redis_client.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, _WINDOW_SECONDS)
        count, _ = pipe.execute()
        circuit_breaker.record_success()
    except RedisError:
        circuit_breaker.record_failure()
        return True, 0

    if count > _MAX_REQUESTS:
        return False, _WINDOW_SECONDS - (now - window_start)
    return True, 0


def rate_limit_dependency(request: Request) -> None:
    client_key = request.client.host if request.client else "unknown"
    allowed, retry_after = is_allowed(client_key)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
            headers={"Retry-After": str(retry_after)},
        )
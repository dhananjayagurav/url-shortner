"""Cache-aside for URL lookups. This sits next to the repository, not
inside it. The service decides when to use the cache. The cache doesn't
know Postgres exists, and the repository doesn't know Redis exists."""
from app.cache.redis_client import redis_client

_TTL_SECONDS = 3600  # one hour -- Phase 7 looks at TTL choice properly


class UrlCache:
    def get(self, short_code: str) -> str | None:
        return redis_client.get(short_code)

    def set(self, short_code: str, original_url: str) -> None:
        redis_client.set(short_code, original_url, ex=_TTL_SECONDS)
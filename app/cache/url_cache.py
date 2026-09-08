"""Cache-aside for URL lookups. This sits next to the repository, not
inside it. The service decides when to use the cache. The cache doesn't
know Postgres exists, and the repository doesn't know Redis exists."""

import logging
from redis.exceptions import RedisError
from app.cache.redis_client import redis_client
import random

logger = logging.getLogger(__name__)
_TTL_SECONDS = 3600  # one hour -- Phase 7 looks at TTL choice properly
_TTL_JITTER_SECONDS = 300  # +/- up to 5 minutes


class UrlCache:
    def get(self, short_code: str) -> str | None:
        try:
            return redis_client.get(short_code)
        except RedisError:
            logger.warning("cache get failed for %s", short_code, exc_info=True)
            return None

    def set(self, short_code: str, original_url: str) -> None:
        try:
            ttl = _TTL_SECONDS + random.randint(-_TTL_JITTER_SECONDS, _TTL_JITTER_SECONDS)
            redis_client.set(short_code, original_url, ex=ttl)
        except RedisError:
            logger.warning("cache set failed for %s", short_code, exc_info=True)

    def delete(self, short_code: str) -> None:
        try:
            redis_client.unlink(short_code)
        except RedisError:
            logger.warning("cache set failed for %s", short_code, exc_info=True)
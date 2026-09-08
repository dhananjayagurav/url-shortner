"""Prove the stampede guard matters: many threads racing on the same cold
cache key should hit Postgres exactly once, not once per thread."""
import threading
import time

from app.cache.redis_client import redis_client
from app.cache.url_cache import UrlCache
from app.core.database import SessionLocal
from app.repositories.url_repository import UrlRepository
from app.services.url_service import UrlService


class _CountingRepository:
    """Wraps a real UrlRepository. Counts how many times Postgres is
    actually queried, and adds a small delay to widen the race window."""

    def __init__(self, real_repository: UrlRepository):
        self._real = real_repository
        self.call_count = 0
        self._count_lock = threading.Lock()

    def get_by_short_code(self, short_code: str):
        with self._count_lock:
            self.call_count += 1
        time.sleep(0.05)  # widen the race window on purpose, like Phase 5
        return self._real.get_by_short_code(short_code)


class _UnguardedUrlService(UrlService):
    """Same as UrlService, but resolve() skips the stampede guard.
    Never use outside a test -- exists only to prove the guard matters."""

    def resolve(self, short_code: str):
        cached_url = self.cache.get(short_code)
        if cached_url is not None:
            return cached_url
        url = self.repository.get_by_short_code(short_code)
        if url is None:
            return None
        self.cache.set(short_code, url.original_url)
        return url.original_url


def _hammer(service, short_code: str, count: int) -> list:
    results = [None] * count
    def _worker(i):
        results[i] = service.resolve(short_code)
    threads = [threading.Thread(target=_worker, args=(i,)) for i in range(count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_unguarded_concurrent_misses_hit_postgres_many_times():
    db = SessionLocal()
    try:
        real_repository = UrlRepository(db)
        url = real_repository.create(original_url="https://example.com/stampede-unguarded")
        redis_client.unlink(url.short_code)  # force a cold cache

        counting_repository = _CountingRepository(real_repository)
        service = _UnguardedUrlService(counting_repository, UrlCache())

        results = _hammer(service, url.short_code, count=20)

        assert all(r == url.original_url for r in results)
        assert counting_repository.call_count > 1  # the stampede
    finally:
        db.close()


def test_guarded_concurrent_misses_hit_postgres_exactly_once():
    db = SessionLocal()
    try:
        real_repository = UrlRepository(db)
        url = real_repository.create(original_url="https://example.com/stampede-guarded")
        redis_client.unlink(url.short_code)  # force a cold cache

        counting_repository = _CountingRepository(real_repository)
        service = UrlService(counting_repository, UrlCache())

        results = _hammer(service, url.short_code, count=20)

        assert all(r == url.original_url for r in results)
        assert counting_repository.call_count == 1
    finally:
        db.close()
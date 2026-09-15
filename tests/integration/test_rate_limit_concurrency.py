"""Real Redis, real Postgres, real HTTP path through FastAPI's
TestClient -- same style as test_rate_limiter.py, run concurrently."""
import concurrent.futures

from fastapi.testclient import TestClient

from app.cache.redis_client import redis_client
from app.main import app

client = TestClient(app)


def setup_function():
    for key in redis_client.scan_iter("ratelimit:*"):
        redis_client.delete(key)


def _hit_once(_: int) -> int:
    resp = client.post(
        "/api/v1/urls",
        json={"url": "https://example.com/rl-race"},
    )
    return resp.status_code


def test_concurrent_burst_allows_exactly_the_limit_through():
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        statuses = list(pool.map(_hit_once, range(20)))

    assert statuses.count(201) == 5    # exactly _MAX_REQUESTS
    assert statuses.count(429) == 15
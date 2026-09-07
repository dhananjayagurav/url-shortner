"""Real Redis, real Postgres -- same philosophy as your other
integration tests."""
from fastapi.testclient import TestClient

from app.cache.redis_client import redis_client
from app.main import app

client = TestClient(app)


def test_second_read_is_served_from_cache():
    create_resp = client.post(
        "/api/v1/urls", json={"url": "https://example.com/cache-test"}
    )
    short_code = create_resp.json()["short_code"]

    # First read: cache miss, falls through to Postgres, populates Redis.
    client.get(f"/{short_code}", follow_redirects=False)
    assert redis_client.get(short_code) == "https://example.com/cache-test"

    # Overwrite the value directly in Redis. If the next read returns
    # THIS value instead of the real one, that proves the cache path is
    # actually being used -- not silently skipped.
    redis_client.set(short_code, "https://example.com/from-cache")
    redirect_resp = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_resp.headers["location"] == "https://example.com/from-cache"
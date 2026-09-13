"""Real Redis, real Postgres, real HTTP path through FastAPI's
TestClient -- same style as Phase 6's cache test."""
from fastapi.testclient import TestClient

from app.cache.redis_client import redis_client
from app.main import app

client = TestClient(app)


def setup_function():
    for key in redis_client.scan_iter("ratelimit:*"):
        redis_client.delete(key)


def test_sixth_request_in_the_same_window_is_rejected():
    for _ in range(5):
        resp = client.post("/api/v1/urls", json={"url": "https://example.com/rl"})
        assert resp.status_code == 201

    resp = client.post("/api/v1/urls", json={"url": "https://example.com/rl"})
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers


def test_redirect_endpoint_is_not_rate_limited():
    create_resp = client.post("/api/v1/urls", json={"url": "https://example.com/rl-read"})
    short_code = create_resp.json()["short_code"]

    for _ in range(20):
        resp = client.get(f"/{short_code}", follow_redirects=False)
        assert resp.status_code == 302
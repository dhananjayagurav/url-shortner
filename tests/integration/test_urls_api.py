"""End-to-end tests against the running app + real Postgres."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_redirect():
    resp = client.post("/api/v1/urls", json={"url": "https://example.com/some/long/path"})
    assert resp.status_code == 201
    body = resp.json()
    assert "short_code" in body
    assert body["short_url"].endswith(body["short_code"])

    redirect_resp = client.get(f"/{body['short_code']}", follow_redirects=False)
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["location"] == "https://example.com/some/long/path"


def test_redirect_unknown_code_returns_404():
    resp = client.get("/doesnotexist", follow_redirects=False)
    assert resp.status_code == 404


def test_create_rejects_invalid_url():
    resp = client.post("/api/v1/urls", json={"url": "not-a-url"})
    assert resp.status_code == 422
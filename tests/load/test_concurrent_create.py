"""Needs the app actually running (uvicorn) and Postgres up -- this test
goes over real HTTP, not FastAPI's in-process TestClient."""
import concurrent.futures

import httpx

BASE_URL = "http://localhost:8000"


def _create_one(i: int) -> str:
    resp = httpx.post(
        f"{BASE_URL}/api/v1/urls",
        json={"url": f"https://example.com/load-test/{i}"},
    )
    resp.raise_for_status()
    return resp.json()["short_code"]


def test_concurrent_creates_produce_no_duplicate_short_codes():
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
        short_codes = list(pool.map(_create_one, range(300)))

    assert len(short_codes) == 300
    assert len(set(short_codes)) == 300
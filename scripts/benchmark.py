"""Phase 6: measure redirect latency. Run this BEFORE adding the cache
code above, to get a baseline. Then run it again AFTER, and compare."""
import statistics
import time

import httpx

BASE_URL = "http://localhost:8000"
REQUEST_COUNT = 200


def percentile(data: list[float], p: float) -> float:
    data_sorted = sorted(data)
    index = min(int(len(data_sorted) * p), len(data_sorted) - 1)
    return data_sorted[index]


def main() -> None:
    with httpx.Client() as client:
        create_resp = client.post(
            f"{BASE_URL}/api/v1/urls", json={"url": "https://example.com/benchmark-target"}
        )
        short_code = create_resp.json()["short_code"]

        durations_ms = []
        for _ in range(REQUEST_COUNT):
            start = time.perf_counter()
            client.get(f"{BASE_URL}/{short_code}", follow_redirects=False)
            durations_ms.append((time.perf_counter() - start) * 1000)

    print(f"requests: {REQUEST_COUNT}")
    print(f"p50:  {percentile(durations_ms, 0.50):.2f} ms")
    print(f"p95:  {percentile(durations_ms, 0.95):.2f} ms")
    print(f"p99:  {percentile(durations_ms, 0.99):.2f} ms")
    print(f"mean: {statistics.mean(durations_ms):.2f} ms")


if __name__ == "__main__":
    main()
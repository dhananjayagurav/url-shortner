"""Phase 5: prove the Snowflake generator's lock actually matters, by
removing it on purpose and watching duplicate IDs appear.

A race condition is timing-dependent -- it might not show up every run.
The tiny sleep() below is a deliberate trick to widen the unsafe window,
so the bug shows up reliably for this lesson. Real races don't need this
trick; they can hide for months without it."""
import threading
import time

from app.core.base62 import encode
from app.core.id_generators import SnowflakeGenerator


class _UnsafeSnowflakeGenerator(SnowflakeGenerator):
    """Same class. Lock removed on purpose. Never use this outside a test."""

    def generate(self) -> str:
        now = self._current_millis()
        if now == self._last_timestamp_ms:
            current_sequence = self._sequence
            time.sleep(0.001)  # widen the race window on purpose
            self._sequence = current_sequence + 1
        else:
            self._sequence = 0
        self._last_timestamp_ms = now

        timestamp_part = (now - self._EPOCH_MS) << (self._MACHINE_ID_BITS + self._SEQUENCE_BITS)
        machine_part = self._machine_id << self._SEQUENCE_BITS
        return encode((timestamp_part | machine_part | self._sequence))


def _run_concurrently(generator, count: int) -> list[str]:
    results: list[str] = [None] * count
    def _worker(i):
        results[i] = generator.generate()
    threads = [threading.Thread(target=_worker, args=(i,)) for i in range(count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_safe_generator_has_no_duplicates_under_threads():
    generator = SnowflakeGenerator(machine_id=1)
    results = _run_concurrently(generator, 200)
    assert len(set(results)) == 200


def test_unsafe_generator_produces_duplicates_under_threads():
    generator = _UnsafeSnowflakeGenerator(machine_id=1)
    results = _run_concurrently(generator, 200)
    assert len(set(results)) < 200
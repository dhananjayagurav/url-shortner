"""A simple in-process circuit breaker for calls to Redis. One shared
state per process -- same module-level pattern as Phase 7's
stampede_guard, and for the same reason: every request needs to see the
same breaker, not its own fresh copy."""
import threading
import time

_FAILURE_THRESHOLD = 5    # consecutive failures before opening
_COOLDOWN_SECONDS = 10    # how long to stay open before allowing a trial call

_lock = threading.Lock()
_consecutive_failures = 0
_opened_at: float | None = None


def is_open() -> bool:
    """True means: don't even try Redis right now."""
    global _opened_at
    with _lock:
        if _opened_at is None:
            return False
        if time.monotonic() - _opened_at >= _COOLDOWN_SECONDS:
            _opened_at = None  # cooldown elapsed -- allow one trial call through
            return False
        return True


def record_success() -> None:
    global _consecutive_failures, _opened_at
    with _lock:
        _consecutive_failures = 0
        _opened_at = None


def record_failure() -> None:
    global _consecutive_failures, _opened_at
    with _lock:
        _consecutive_failures += 1
        if _consecutive_failures >= _FAILURE_THRESHOLD and _opened_at is None:
            _opened_at = time.monotonic()
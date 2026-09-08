"""A per-key lock registry -- one process-wide dict, shared by every
request. Same shape as Phase 1.1's module-level `_urls` dict. This time
the sharing is deliberate: every request racing for the same short_code
needs to land on the exact same Lock object, or the lock protects nothing."""
import threading

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()  # protects the _locks dict itself


def get_lock(key: str) -> threading.Lock:
    with _locks_guard:
        if key not in _locks:
            _locks[key] = threading.Lock()
        return _locks[key]
"""Unit tests for the circuit breaker's state machine -- no Redis, no
network, just the logic."""
import time

from app.cache import circuit_breaker


def setup_function():
    circuit_breaker.record_success()  # reset shared module state


def test_stays_closed_below_the_failure_threshold():
    for _ in range(4):
        circuit_breaker.record_failure()
    assert circuit_breaker.is_open() is False


def test_opens_at_the_failure_threshold():
    for _ in range(5):
        circuit_breaker.record_failure()
    assert circuit_breaker.is_open() is True


def test_a_success_resets_the_failure_count():
    for _ in range(4):
        circuit_breaker.record_failure()
    circuit_breaker.record_success()
    circuit_breaker.record_failure()
    assert circuit_breaker.is_open() is False  # only 1 failure since the reset


def test_reopens_for_a_trial_call_after_cooldown(monkeypatch):
    monkeypatch.setattr(circuit_breaker, "_COOLDOWN_SECONDS", 0.05)
    for _ in range(5):
        circuit_breaker.record_failure()
    assert circuit_breaker.is_open() is True
    time.sleep(0.06)
    assert circuit_breaker.is_open() is False  # cooldown elapsed, trial allowed
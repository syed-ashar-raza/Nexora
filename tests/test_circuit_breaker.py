from app.reliability.circuit_breaker import CircuitBreaker, CircuitState


def test_opens_after_threshold():
    breaker = CircuitBreaker(threshold=2, recovery_seconds=60)
    breaker.failure()
    assert breaker.state == CircuitState.CLOSED
    breaker.failure()
    assert breaker.state == CircuitState.OPEN
    assert not breaker.allow()


def test_half_open_allows_only_one_recovery_probe(monkeypatch):
    now = 100.0
    monkeypatch.setattr(
        "app.reliability.circuit_breaker.time.monotonic",
        lambda: now,
    )

    breaker = CircuitBreaker(threshold=1, recovery_seconds=30)
    breaker.failure()

    assert breaker.state == CircuitState.OPEN
    assert not breaker.allow()

    now = 131.0

    assert breaker.allow()
    assert breaker.state == CircuitState.HALF_OPEN
    assert not breaker.allow()


def test_half_open_success_closes_circuit(monkeypatch):
    now = 100.0
    monkeypatch.setattr(
        "app.reliability.circuit_breaker.time.monotonic",
        lambda: now,
    )

    breaker = CircuitBreaker(threshold=1, recovery_seconds=30)
    breaker.failure()

    now = 131.0

    assert breaker.allow()
    breaker.success()

    assert breaker.state == CircuitState.CLOSED
    assert breaker.failures == 0
    assert breaker.allow()


def test_half_open_failure_reopens_circuit(monkeypatch):
    now = 100.0
    monkeypatch.setattr(
        "app.reliability.circuit_breaker.time.monotonic",
        lambda: now,
    )

    breaker = CircuitBreaker(threshold=1, recovery_seconds=30)
    breaker.failure()

    now = 131.0

    assert breaker.allow()
    breaker.failure()

    assert breaker.state == CircuitState.OPEN
    assert not breaker.allow()

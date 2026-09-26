from app.reliability.circuit_breaker import CircuitBreaker, CircuitState


def test_opens_after_threshold():
    breaker = CircuitBreaker(threshold=2, recovery_seconds=60)
    breaker.failure()
    assert breaker.state == CircuitState.CLOSED
    breaker.failure()
    assert breaker.state == CircuitState.OPEN
    assert not breaker.allow()

import time
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        threshold: int = 5,
        recovery_seconds: float = 30.0,
    ):
        self.threshold = threshold
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.opened_at = 0.0

    def allow(self) -> bool:
        if self.state != CircuitState.OPEN:
            return True

        if time.monotonic() - self.opened_at >= self.recovery_seconds:
            self.state = CircuitState.HALF_OPEN
            return True

        return False

    def success(self) -> None:
        self.failures = 0
        self.state = CircuitState.CLOSED

    def failure(self) -> None:
        self.failures += 1

        if self.failures >= self.threshold:
            self.state = CircuitState.OPEN
            self.opened_at = time.monotonic()

    def is_available(self) -> bool:
        return self.state != CircuitState.OPEN

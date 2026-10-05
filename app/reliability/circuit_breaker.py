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
        self._half_open_probe = False

    def allow(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.opened_at < self.recovery_seconds:
                return False

            self.state = CircuitState.HALF_OPEN
            self._half_open_probe = False

        if self.state == CircuitState.HALF_OPEN:
            if self._half_open_probe:
                return False

            self._half_open_probe = True
            return True

        return False

    def success(self) -> None:
        self.failures = 0
        self.state = CircuitState.CLOSED
        self._half_open_probe = False

    def failure(self) -> None:
        self.failures += 1
        self._half_open_probe = False

        if self.failures >= self.threshold:
            self.state = CircuitState.OPEN
            self.opened_at = time.monotonic()

    def is_available(self) -> bool:
        return self.state != CircuitState.OPEN

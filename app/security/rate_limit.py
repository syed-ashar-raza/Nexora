import time


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds

        timestamps = [
            timestamp
            for timestamp in self._requests.get(key, [])
            if timestamp > cutoff
        ]

        if len(timestamps) >= self.limit:
            self._requests[key] = timestamps
            return False

        timestamps.append(now)
        self._requests[key] = timestamps
        return True

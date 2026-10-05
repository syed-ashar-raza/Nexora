import asyncio


class BulkheadFull(Exception):
    pass


class Bulkhead:
    def __init__(self, limit: int) -> None:
        if limit < 1:
            raise ValueError("Bulkhead limit must be at least 1")
        self.limit = limit
        self._active = 0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            if self._active >= self.limit:
                raise BulkheadFull("Provider concurrency limit reached")
            self._active += 1

    async def release(self) -> None:
        async with self._lock:
            if self._active <= 0:
                raise RuntimeError("Bulkhead release without acquire")
            self._active -= 1

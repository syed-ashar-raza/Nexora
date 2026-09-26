import asyncio
from collections.abc import Awaitable, Callable

from app.providers.base import ProviderTimeout


async def with_retry[T](
    operation: Callable[[], Awaitable[T]],
    retries: int,
    timeout_seconds: float | None = None,
) -> T:
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            if timeout_seconds is None:
                return await operation()

            return await asyncio.wait_for(
                operation(),
                timeout=timeout_seconds,
            )
        except TimeoutError as exc:
            last_error = ProviderTimeout(
                f"Provider request timed out after {timeout_seconds:.2f}s"
            )
            if attempt < retries:
                continue
            raise last_error from exc
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                continue
            raise

    if last_error is not None:
        raise last_error

    raise RuntimeError("Retry operation failed unexpectedly")

import asyncio
import random
from collections.abc import Awaitable, Callable

from app.providers.base import ProviderError, ProviderTimeout


async def with_retry[T](
    operation: Callable[[], Awaitable[T]],
    retries: int,
    timeout_seconds: float | None = None,
    backoff_seconds: float = 0.0,
    max_backoff_seconds: float = 0.0,
    jitter_seconds: float = 0.0,
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
        except TimeoutError:
            last_error = ProviderTimeout(f"Provider request timed out after {timeout_seconds:.2f}s")
        except ProviderError as exc:
            last_error = exc
        except Exception:
            raise

        if attempt < retries:
            delay = min(
                backoff_seconds * (2**attempt),
                max_backoff_seconds,
            )
            if jitter_seconds > 0:
                delay += random.uniform(0.0, jitter_seconds)
            await asyncio.sleep(delay)
            continue

        raise last_error

    raise RuntimeError("Retry operation failed unexpectedly")

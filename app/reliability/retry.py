from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable

from app.providers.base import ProviderError, ProviderTimeout


async def with_retry[T](
    operation: Callable[[], Awaitable[T]],
    retries: int,
    timeout_seconds: float | None = None,
    backoff_seconds: float = 0.0,
    max_backoff_seconds: float = 0.0,
    jitter_seconds: float = 0.0,
    on_retry: Callable[[int], None] | None = None,
    retry_budget_seconds: float | None = None,
) -> T:
    last_error: Exception | None = None
    started = time.monotonic()

    for attempt in range(retries + 1):
        try:
            effective_timeout = timeout_seconds

            if retry_budget_seconds is not None:
                remaining = retry_budget_seconds - (
                    time.monotonic() - started
                )
                if remaining <= 0:
                    raise ProviderTimeout(
                        "Retry budget exhausted before provider attempt"
                    )
                effective_timeout = (
                    remaining
                    if effective_timeout is None
                    else min(effective_timeout, remaining)
                )

            return await asyncio.wait_for(
                operation(),
                timeout=effective_timeout,
            )
        except TimeoutError:
            if (
                retry_budget_seconds is not None
                and time.monotonic() - started >= retry_budget_seconds
            ):
                last_error = ProviderTimeout(
                    f"Retry budget exhausted after "
                    f"{retry_budget_seconds:.2f}s"
                )
            else:
                last_error = ProviderTimeout(
                    f"Provider request timed out after "
                    f"{timeout_seconds:.2f}s"
                )
        except ProviderTimeout as exc:
            last_error = exc
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

            if (
                retry_budget_seconds is not None
                and time.monotonic() - started + delay > retry_budget_seconds
            ):
                raise last_error

            if on_retry is not None:
                on_retry(attempt + 1)

            await asyncio.sleep(delay)
            continue

        raise last_error

    raise RuntimeError("Retry operation failed unexpectedly")


import pytest

from app.providers.base import ProviderError, ProviderTimeout
from app.reliability.retry import with_retry


@pytest.mark.asyncio
async def test_retry_retries_provider_errors():
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ProviderError("temporary failure")
        return "ok"

    assert await with_retry(operation, retries=2) == "ok"
    assert attempts == 3


@pytest.mark.asyncio
async def test_retry_does_not_retry_unexpected_errors():
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        raise ValueError("unexpected")

    with pytest.raises(ValueError):
        await with_retry(operation, retries=2)

    assert attempts == 1


@pytest.mark.asyncio
async def test_retry_timeout_raises_provider_timeout():
    async def operation():
        await __import__("asyncio").sleep(0.05)

    with pytest.raises(ProviderTimeout):
        await with_retry(
            operation,
            retries=1,
            timeout_seconds=0.01,
        )


@pytest.mark.asyncio
async def test_retry_applies_exponential_backoff(monkeypatch):
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr("app.reliability.retry.asyncio.sleep", fake_sleep)

    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ProviderError("temporary failure")
        return "ok"

    assert (
        await with_retry(
            operation,
            retries=2,
            backoff_seconds=0.1,
            max_backoff_seconds=2.0,
            jitter_seconds=0.0,
        )
        == "ok"
    )

    assert delays == [0.1, 0.2]


@pytest.mark.asyncio
async def test_retry_caps_backoff(monkeypatch):
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr("app.reliability.retry.asyncio.sleep", fake_sleep)

    async def operation():
        raise ProviderError("persistent failure")

    with pytest.raises(ProviderError):
        await with_retry(
            operation,
            retries=3,
            backoff_seconds=1.0,
            max_backoff_seconds=1.5,
            jitter_seconds=0.0,
        )

    assert delays == [1.0, 1.5, 1.5]

@pytest.mark.asyncio
async def test_retry_reports_retry_attempts():
    attempts = 0
    retry_events = []

    async def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ProviderError("temporary failure")
        return "ok"

    assert (
        await with_retry(
            operation,
            retries=2,
            on_retry=retry_events.append,
        )
        == "ok"
    )

    assert retry_events == [1, 2]


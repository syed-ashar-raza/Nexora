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

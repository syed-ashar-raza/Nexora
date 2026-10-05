
import pytest

from app.reliability.bulkhead import Bulkhead, BulkheadFull


@pytest.mark.asyncio
async def test_bulkhead_allows_up_to_limit():
    bulkhead = Bulkhead(2)

    await bulkhead.acquire()
    await bulkhead.acquire()

    with pytest.raises(BulkheadFull):
        await bulkhead.acquire()

    await bulkhead.release()
    await bulkhead.acquire()


@pytest.mark.asyncio
async def test_bulkhead_release_restores_capacity():
    bulkhead = Bulkhead(1)

    await bulkhead.acquire()
    await bulkhead.release()
    await bulkhead.acquire()

    await bulkhead.release()


def test_bulkhead_rejects_invalid_limit():
    with pytest.raises(ValueError):
        Bulkhead(0)


@pytest.mark.asyncio
async def test_bulkhead_rejects_unbalanced_release():
    bulkhead = Bulkhead(1)

    with pytest.raises(RuntimeError):
        await bulkhead.release()

from __future__ import annotations

import asyncio
import time

import pytest

from src.services.async_processor import map_async, retry


def test_map_async_and_retry_success_after_failure():
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("boom")
        return "ok"

    res = asyncio.run(retry(flaky, retries=2, base_delay=0.01))
    assert res == "ok"

    items = [1, 2, 3]

    async def double(x: int) -> int:
        await asyncio.sleep(0)
        return x * 2

    outs = asyncio.run(map_async(items, double, limit=2))
    assert outs == [2, 4, 6]


def test_retry_timeout():
    async def slow():
        await asyncio.sleep(0.05)
        return "late"

    t0 = time.time()
    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(retry(slow, retries=0, timeout=0.01))
    assert time.time() - t0 < 0.2

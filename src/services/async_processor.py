from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Iterable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def run_with_semaphore(limit: int, coros: Iterable[Awaitable[R]]) -> List[R]:
    """Run awaitables with a concurrency limit.

    Args:
        limit: Maximum concurrent tasks.
        coros: Iterable of awaitables.
    Returns:
        A list of results in the same order as input.
    """
    sem = asyncio.Semaphore(limit if limit > 0 else 1)

    async def _guarded(coro: Awaitable[R]) -> R:
        async with sem:
            return await coro

    return await asyncio.gather(*[_guarded(c) for c in coros])


async def map_async(items: Iterable[T], fn: Callable[[T], Awaitable[R]], limit: int = 5) -> List[R]:
    """Apply an async function to items concurrently with a limit."""
    return await run_with_semaphore(limit, (fn(it) for it in items))


async def retry(
    func: Callable[[], Awaitable[R]],
    retries: int = 2,
    base_delay: float = 0.5,
    timeout: float | None = None,
) -> R:
    """Retry an async function with optional timeout and exponential backoff."""
    attempt = 0
    while True:
        try:
            if timeout:
                return await asyncio.wait_for(func(), timeout=timeout)
            return await func()
        except Exception:
            attempt += 1
            if attempt > retries:
                raise
            await asyncio.sleep(base_delay * (2 ** (attempt - 1)))

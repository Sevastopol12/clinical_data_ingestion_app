"""Small async TTL cache with per-key single-flight fetching."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Hashable
from typing import TypeVar

T = TypeVar("T")


class TtlCache[T]:
    def __init__(
        self, ttl_seconds: float = 60, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._values: dict[Hashable, tuple[float, T]] = {}
        self._in_flight: dict[Hashable, asyncio.Task[T]] = {}

    async def get_or_fetch(self, key: Hashable, fetch: Callable[[], Awaitable[T]]) -> T:
        cached = self._values.get(key)
        if cached is not None:
            expires, value = cached
            if self._clock() < expires:
                return value
            del self._values[key]
        task = self._in_flight.get(key)
        if task is None:

            async def run_fetch() -> T:
                return await fetch()

            task = asyncio.create_task(run_fetch())
            self._in_flight[key] = task
        try:
            value = await task
        except BaseException:
            if self._in_flight.get(key) is task:
                del self._in_flight[key]
            raise
        if self._in_flight.get(key) is task:
            del self._in_flight[key]
            self._values[key] = (self._clock() + self._ttl_seconds, value)
        return value

    def invalidate(self, key: Hashable | None = None) -> None:
        if key is None:
            self._values.clear()
            return
        self._values.pop(key, None)

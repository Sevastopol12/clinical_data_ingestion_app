"""Small async TTL cache with per-key single-flight fetching."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Hashable
from typing import TypeVar

T = TypeVar("T")


class TtlCache[T]:
    def __init__(
        self,
        ttl_seconds: float = 60,
        clock: Callable[[], float] = time.monotonic,
        max_entries: int = 512,
    ) -> None:
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._max_entries = max_entries
        self._values: dict[Hashable, tuple[float, T]] = {}
        self._in_flight: dict[Hashable, asyncio.Task[T]] = {}

    def _purge_expired(self) -> None:
        now = self._clock()
        expired = [key for key, (expires, _) in self._values.items() if now >= expires]
        for key in expired:
            del self._values[key]

    def _evict_oldest(self) -> None:
        while len(self._values) > self._max_entries:
            oldest = next(iter(self._values))
            del self._values[oldest]

    async def get_or_fetch(self, key: Hashable, fetch: Callable[[], Awaitable[T]]) -> T:
        self._purge_expired()
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
            self._evict_oldest()
        return value

    def invalidate(
        self, key: Hashable | None = None, *, disown_in_flight: bool = False
    ) -> None:
        if key is None:
            self._values.clear()
            if disown_in_flight:
                self._in_flight.clear()
            return
        self._values.pop(key, None)
        if disown_in_flight:
            self._in_flight.pop(key, None)

    def invalidate_namespace(self, ns: str) -> None:
        for key in [
            key
            for key in self._values
            if isinstance(key, tuple) and len(key) > 0 and key[0] == ns
        ]:
            del self._values[key]
        for key in [
            key
            for key in self._in_flight
            if isinstance(key, tuple) and len(key) > 0 and key[0] == ns
        ]:
            del self._in_flight[key]

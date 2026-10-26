"""WebSocket transport for backend realtime frames (Reflex-free)."""

from __future__ import annotations

import random
from collections.abc import AsyncIterator, Callable

from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from data_managment_system.config import settings
from data_managment_system.models.realtime import (
    ServerFrame,
    SessionRefresh,
    parse_server_frame,
)


class RealtimeError(Exception):
    """Base realtime failure; messages never contain credentials."""


class Superseded(RealtimeError):
    """Another socket owns this login chain (4409)."""


class SessionExpired(RealtimeError):
    """The account session is no longer valid (4401)."""


class SessionRevoked(RealtimeError):
    """The login chain was revoked (4403)."""


class TryLater(RealtimeError):
    """The backend asks the client to reconnect later."""


class RealtimeUnavailable(RealtimeError):
    """Network, handshake, or unexpected protocol failure."""


def websocket_url() -> str:
    url = str(settings.backend_base_url).rstrip("/")
    if url.startswith("https://"):
        url = "wss://" + url[8:]
    elif url.startswith("http://"):
        url = "ws://" + url[7:]
    return f"{url}/{settings.request_realtime_ws.lstrip('/')}"


def next_backoff(
    attempt: int,
    base: float,
    maximum: float,
    rng: Callable[[float, float], float] = random.uniform,
) -> float:
    """Exponential full-jitter delay, bounded by maximum."""
    ceiling = min(maximum, base * (2 ** max(0, attempt)))
    return rng(0.0, max(0.0, ceiling))


def _map_close(code: int | None) -> RealtimeError:
    if code == 4409:
        return Superseded("realtime connection superseded")
    if code == 4401:
        return SessionExpired("session expired")
    if code == 4403:
        return SessionRevoked("session revoked")
    if code in (1013, 1001, 1009):
        return TryLater("realtime service temporarily unavailable")
    return RealtimeUnavailable("realtime connection closed")


def _close_code(exc: ConnectionClosed) -> int | None:
    close = exc.rcvd or exc.sent
    return close.code if close is not None else None


class RealtimeClient:
    """Small stateful wrapper around the websockets asyncio client."""

    def __init__(self) -> None:
        self._socket: ClientConnection | None = None

    async def connect(self, token: str) -> None:
        try:
            self._socket = await connect(
                websocket_url(),
                additional_headers={"Authorization": f"Bearer {token}"},
            )
        except ConnectionClosed as exc:
            raise _map_close(_close_code(exc)) from None
        except Exception:  # noqa: BLE001
            raise RealtimeUnavailable("realtime connection failed") from None

    async def messages(self) -> AsyncIterator[ServerFrame]:
        if self._socket is None:
            raise RealtimeUnavailable("realtime socket is not connected")
        try:
            async for message in self._socket:
                yield parse_server_frame(message)
        except ConnectionClosed as exc:
            raise _map_close(_close_code(exc)) from None

    async def receive(self) -> ServerFrame:
        """Receive one frame with close-code mapping for periodic orphan checks."""
        if self._socket is None:
            raise RealtimeUnavailable("realtime socket is not connected")
        try:
            return parse_server_frame(await self._socket.recv())
        except ConnectionClosed as exc:
            raise _map_close(_close_code(exc)) from None

    async def send_refresh(self, refresh_token: str) -> None:
        if self._socket is None:
            raise RealtimeUnavailable("realtime socket is not connected")
        try:
            await self._socket.send(
                SessionRefresh(refresh_token=refresh_token).model_dump_json()
            )
        except ConnectionClosed as exc:
            raise _map_close(_close_code(exc)) from None

    async def close(self) -> None:
        socket, self._socket = self._socket, None
        if socket is not None:
            await socket.close()


__all__ = [
    "RealtimeClient",
    "RealtimeError",
    "RealtimeUnavailable",
    "SessionExpired",
    "SessionRevoked",
    "Superseded",
    "TryLater",
    "next_backoff",
    "websocket_url",
]

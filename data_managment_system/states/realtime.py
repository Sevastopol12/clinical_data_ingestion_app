"""Per-tab background realtime connection and session lifecycle."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import reflex as rx

from data_managment_system.config import settings
from data_managment_system.models.realtime import (
    ErrorFrame,
    MetricsUpdated,
    ServerFrame,
    SessionExpiring,
    SessionRefreshed,
)
from data_managment_system.services import metrics as metrics_service
from data_managment_system.services.http import BackendError, get_client
from data_managment_system.services.realtime import (
    RealtimeClient,
    RealtimeError,
    SessionExpired,
    SessionRevoked,
    Superseded,
    next_backoff,
)
from data_managment_system.states.auth import AuthState
from data_managment_system.states.metrics import MetricsState

_RECEIVE_TIMEOUT_SECONDS = 5.0
_RELOAD_QUIET_SECONDS = 0.2
_RELOAD_MAX_DELAY_SECONDS = 1.0
_RELOAD_WAIT_SECONDS = 5.0
_REFRESH_WAIT_SECONDS = 10.0
_HEALTHY_SECONDS = 30.0

# Process-local loop bookkeeping. It is an optimisation only: the backend owns
# correctness with one socket per chain, and a new worker may always start a
# loop after a reload or a dead process.
_active: set[str] = set()
_generations: dict[str, int] = {}
_sockets: dict[str, RealtimeClient] = {}


def _next_generation(client_token: str) -> int:
    generation = _generations.get(client_token, 0) + 1
    _generations[client_token] = generation
    return generation


def _release_owner(client_token: str, generation: int) -> bool:
    """Release this loop's guard without clearing a newer generation's entry."""
    if _generations.get(client_token) != generation:
        return False
    _active.discard(client_token)
    return True


def _socket_tokens(namespace: Any) -> set[str] | None:
    """Return tokens with a live Reflex socket, or None when unknown.

    Reflex 0.9.8 keeps its TokenManager on ``app.event_namespace`` (not on
    ``App`` itself). Returning None means "cannot inspect", which must not be
    treated as a disconnect: doing so would silently disable realtime.
    """
    manager = getattr(namespace, "_token_manager", None)
    mapping = getattr(manager, "token_to_socket", None)
    if not isinstance(mapping, dict):
        return None
    return set(mapping)


def _app_socket_tokens() -> set[str] | None:
    try:
        from data_managment_system.data_managment_system import app

        namespace = app.event_namespace
    except (AttributeError, ImportError, RuntimeError):
        return None
    return _socket_tokens(namespace)


def is_newer_than_freshness(
    last_computed_at: datetime | None, freshness_iso: str
) -> bool:
    """Decide whether a reconnect must refetch metrics."""
    if last_computed_at is None:
        return False
    if not freshness_iso:
        return True
    try:
        known = datetime.fromisoformat(freshness_iso)
    except ValueError:
        return True
    if (
        known.tzinfo is None
        or known.utcoffset() is None
        or last_computed_at.tzinfo is None
        or last_computed_at.utcoffset() is None
    ):
        return True
    return last_computed_at > known


@dataclass
class _ReloadGate:
    """Small quiet-period gate that coalesces notification bursts.

    A load runs only after ``quiet`` seconds without another notification, and
    a burst can delay the first load by at most ``max_delay`` seconds.
    """

    quiet: float = _RELOAD_QUIET_SECONDS
    max_delay: float = _RELOAD_MAX_DELAY_SECONDS
    _pending: bool = field(default=False, init=False)
    _first_at: float = field(default=0.0, init=False)
    _deadline: float = field(default=0.0, init=False)

    @property
    def pending(self) -> bool:
        return self._pending

    def notify(self, now: float) -> None:
        if not self._pending:
            self._pending = True
            self._first_at = now
        self._deadline = min(now + self.quiet, self._first_at + self.max_delay)

    def due(self, now: float) -> bool:
        return self._pending and now >= self._deadline

    def remaining(self, now: float) -> float:
        return max(0.0, self._deadline - now)

    def take(self) -> None:
        self._pending = False


class RealtimeState(rx.State):
    """Own one loop per Reflex client token in this process."""

    _stop_requested: bool = False

    @rx.event
    def resume_if_visible(self, hidden: bool) -> Any:
        """Re-enter the guarded starter when a sleeping tab becomes visible."""
        if hidden:
            return None
        return RealtimeState.start

    @rx.event(background=True)
    async def start(self) -> AsyncIterator[Any]:
        async with self:
            client_token = self.router.session.client_token
            if not client_token or client_token in _active:
                return
            auth = await self.get_state(AuthState)
            if auth.current_session() is None:
                return
            generation = _next_generation(client_token)
            _active.add(client_token)
            self._stop_requested = False
        attempt = 0
        try:
            while await self._is_alive(client_token, generation):
                auth = await self._auth_state()
                if auth is None:
                    break
                session = auth.current_session()
                if session is None:
                    break
                access_expires_at = auth._access_expires_at
                if access_expires_at is not None and access_expires_at <= datetime.now(
                    UTC
                ):
                    recovery = await auth.recover_session()
                    if recovery is True:
                        session = auth.current_session()
                        if session is None:
                            break
                        attempt = 0
                    elif recovery is False:
                        yield self._unauthorized_event(skip_recovery=True)
                        break
                    else:
                        await self._backoff(attempt)
                        attempt += 1
                        continue
                if session is None:
                    break
                client = RealtimeClient()
                refresh_guard: asyncio.Lock | None = None
                refresh_deadline = 0.0
                try:
                    await client.connect(session.token)
                    _sockets[client_token] = client
                    reload_gate = _ReloadGate()
                    if await self._status_is_newer(session):
                        self._invalidate_metrics(session.sid)
                        reload_gate.notify(asyncio.get_running_loop().time())
                    healthy_at = asyncio.get_running_loop().time()
                    while await self._is_alive(client_token, generation):
                        now = asyncio.get_running_loop().time()
                        if refresh_guard is not None and now >= refresh_deadline:
                            self._release_guard(refresh_guard)
                            refresh_guard = None
                        if reload_gate.due(now):
                            reload_gate.take()
                            self._invalidate_metrics(session.sid)
                            completion = self._reload_completion(client_token)
                            completion.clear()
                            yield self._metrics_load_event()
                            await self._wait_for_reload(completion)
                            continue
                        timeout = _RECEIVE_TIMEOUT_SECONDS
                        if reload_gate.pending:
                            timeout = min(timeout, reload_gate.remaining(now))
                        if refresh_guard is not None:
                            timeout = min(timeout, max(0.0, refresh_deadline - now))
                        if timeout <= 0:
                            continue
                        try:
                            frame: ServerFrame = await asyncio.wait_for(
                                client.receive(), timeout=timeout
                            )
                        except TimeoutError:
                            continue
                        if isinstance(frame, MetricsUpdated):
                            auth = await self._auth_state()
                            facility_id = auth._facility_id if auth is not None else ""
                            if str(frame.facility_id) == facility_id:
                                reload_gate.notify(asyncio.get_running_loop().time())
                        elif isinstance(frame, SessionExpiring):
                            if refresh_guard is not None:
                                continue
                            if not await self._is_alive(client_token, generation):
                                break
                            auth = await self._auth_state()
                            if auth is None or auth.current_refresh() is None:
                                continue
                            guard = auth.refresh_guard()
                            await guard.acquire()
                            refresh_guard = guard
                            refresh_deadline = (
                                asyncio.get_running_loop().time()
                                + _REFRESH_WAIT_SECONDS
                            )
                            if not await self._is_alive(client_token, generation):
                                break
                            auth = await self._auth_state()
                            refresh_token = (
                                auth.current_refresh() if auth is not None else None
                            )
                            if refresh_token is None:
                                self._release_guard(refresh_guard)
                                refresh_guard = None
                                continue
                            await client.send_refresh(refresh_token)
                        elif isinstance(frame, SessionRefreshed):
                            yield self._apply_refresh_event(frame)
                            if refresh_guard is not None:
                                self._release_guard(refresh_guard)
                                refresh_guard = None
                        elif isinstance(frame, ErrorFrame):
                            if refresh_guard is not None:
                                self._release_guard(refresh_guard)
                                refresh_guard = None
                            if frame.code == "refresh_invalid":
                                yield self._unauthorized_event(skip_recovery=True)
                                return
                    elapsed = asyncio.get_running_loop().time() - healthy_at
                    attempt = 0 if elapsed >= _HEALTHY_SECONDS else attempt + 1
                except Superseded:
                    return
                except SessionExpired:
                    self._release_guard(refresh_guard)
                    refresh_guard = None
                    auth = await self._auth_state()
                    recovery = (
                        await auth.recover_session() if auth is not None else False
                    )
                    if recovery is True:
                        attempt = 0
                        continue
                    if recovery is False:
                        yield self._unauthorized_event(skip_recovery=True)
                        return
                    await self._backoff(attempt)
                    attempt += 1
                except SessionRevoked:
                    self._release_guard(refresh_guard)
                    refresh_guard = None
                    yield self._unauthorized_event(skip_recovery=True)
                    return
                except RealtimeError:
                    self._release_guard(refresh_guard)
                    refresh_guard = None
                    if not await self._is_alive(client_token, generation):
                        return
                    await self._backoff(attempt)
                    attempt += 1
                finally:
                    self._release_guard(refresh_guard)
                    if _sockets.get(client_token) is client:
                        _sockets.pop(client_token, None)
                    await client.close()
        finally:
            async with self:
                if _release_owner(client_token, generation):
                    self._stop_requested = False

    @rx.event(background=True)
    async def stop(self) -> None:
        """Stop this tab's loop; used by logout and terminal auth failures."""
        async with self:
            client_token = self.router.session.client_token
            if not client_token:
                return
            _next_generation(client_token)
            self._stop_requested = True
            _active.discard(client_token)
            client = _sockets.pop(client_token, None)
        if client is not None:
            await client.close()

    @rx.event(background=True)
    async def restart(self) -> AsyncIterator[Any]:
        """Replace the current socket after a successful HTTP recovery."""
        async with self:
            client_token = self.router.session.client_token
            if not client_token:
                return
            _next_generation(client_token)
            self._stop_requested = True
            _active.discard(client_token)
            client = _sockets.pop(client_token, None)
        if client is not None:
            await client.close()
        yield RealtimeState.start

    async def _is_alive(self, client_token: str, generation: int) -> bool:
        async with self:
            if self._stop_requested or _generations.get(client_token) != generation:
                return False
        live_tokens = _app_socket_tokens()
        if live_tokens is not None and client_token not in live_tokens:
            # Reflex removes this mapping asynchronously in on_disconnect.
            return False
        try:
            auth = await self._auth_state()
        except Exception:  # noqa: BLE001 - a lost state mapping is an orphan
            return False
        return auth is not None and auth.current_session() is not None

    async def _auth_state(self) -> Any:
        """Read AuthState through a short lock (background StateProxy rule)."""
        async with self:
            return await self.get_state(AuthState)

    async def _status_is_newer(self, session: Any) -> bool:
        try:
            status = await metrics_service.fetch_status(
                get_client(), access_token=session.token
            )
        except BackendError:
            return False
        async with self:
            metrics = await self.get_state(MetricsState)
            current = metrics.freshness.iso
        return is_newer_than_freshness(status.last_computed_at, current)

    @staticmethod
    def _invalidate_metrics(sid: str) -> None:
        from data_managment_system.states.metrics import _CACHE

        _CACHE.invalidate_namespace(sid)

    @staticmethod
    def _reload_completion(client_token: str) -> asyncio.Event:
        from data_managment_system.states.metrics import reload_event

        return reload_event(client_token)

    @staticmethod
    async def _wait_for_reload(completion: asyncio.Event) -> None:
        try:
            await asyncio.wait_for(completion.wait(), timeout=_RELOAD_WAIT_SECONDS)
        except TimeoutError:
            # A reload may run on another process; never block the socket forever.
            pass

    @staticmethod
    def _release_guard(guard: asyncio.Lock | None) -> None:
        """Release only a guard this loop acquired itself."""
        if guard is not None and guard.locked():
            guard.release()

    async def _backoff(self, attempt: int) -> None:
        await asyncio.sleep(
            next_backoff(
                attempt,
                settings.realtime_backoff_base_seconds,
                settings.realtime_backoff_max_seconds,
            )
        )

    @staticmethod
    def _metrics_load_event() -> Any:
        from data_managment_system.states.metrics import MetricsState

        return MetricsState.load_all(silent=True)  # type: ignore[reportCallIssue]

    @staticmethod
    def _apply_refresh_event(frame: SessionRefreshed) -> Any:
        from data_managment_system.states.auth import AuthState

        return AuthState.apply_refresh(  # type: ignore[reportCallIssue]
            frame.session_token,
            frame.refresh_token,
            frame.access_expires_at,
            frame.refresh_expires_at,
        )

    @staticmethod
    def _unauthorized_event(*, skip_recovery: bool) -> Any:
        from data_managment_system.states.auth import AuthState

        return AuthState.handle_unauthorized(  # type: ignore[reportCallIssue]
            skip_recovery=skip_recovery
        )


__all__ = [
    "RealtimeState",
    "is_newer_than_freshness",
]

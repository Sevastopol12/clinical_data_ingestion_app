"""Backend-owned session state (token lives in backend-only vars)."""

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import reflex as rx

import data_managment_system.services.auth as auth_service
from data_managment_system.copy import AUTH
from data_managment_system.models.auth import SessionInfo
from data_managment_system.services.auth import (
    AuthUnavailable,
    InvalidCredentials,
    InvalidRefresh,
    RateLimited,
)
from data_managment_system.services.http import BadPayload
from data_managment_system.utils.jwt_claims import extract_sid

_refresh_locks: dict[str, asyncio.Lock] = {}


class AuthState(rx.State):
    """Session state; token/sid/facility are backend-only."""

    is_authenticated: bool = False
    is_logging_in: bool = False
    login_error: str = ""
    retry_after: int = 0

    _access_token: str = ""
    _refresh_token: str = ""
    _sid: str = ""
    _facility_id: str = ""
    _access_expires_at: datetime | None = None
    _refresh_expires_at: datetime | None = None
    _session_expires_at: datetime | None = None

    @rx.event
    async def login(self, form_data: dict) -> AsyncIterator[Any]:
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        username = str(username).strip() if username is not None else ""
        password = str(password) if password is not None else ""
        if not username or not password:
            self.is_logging_in = False
            self.login_error = "invalid"
            self.retry_after = 0
            return
        self.is_logging_in = True
        self.login_error = ""
        self.retry_after = 0
        yield
        try:
            dto = await auth_service.login(username, password)
        except InvalidCredentials:
            self.is_logging_in = False
            self.login_error = "invalid"
            self.retry_after = 0
            return
        except RateLimited as exc:
            self.is_logging_in = False
            self.login_error = "rate_limited"
            self.retry_after = exc.retry_after
            return
        except (AuthUnavailable, BadPayload):
            self.is_logging_in = False
            self.login_error = "unavailable"
            self.retry_after = 0
            return
        try:
            sid = extract_sid(dto.session_token)
        except ValueError:
            self.is_logging_in = False
            self.login_error = "unavailable"
            self.retry_after = 0
            return
        self._access_token = dto.session_token
        self._refresh_token = dto.refresh_token
        self._sid = sid
        self._facility_id = str(dto.facility_id)
        self._access_expires_at = dto.access_expires_at
        self._refresh_expires_at = dto.refresh_expires_at
        self._session_expires_at = dto.session_expires_at
        self.is_authenticated = True
        self.is_logging_in = False
        self.login_error = ""
        self.retry_after = 0
        yield rx.redirect("/")
        return

    @rx.event
    async def logout(self) -> AsyncIterator[Any]:
        token = self._access_token
        old_sid = self._sid
        from data_managment_system.states.realtime import RealtimeState

        yield RealtimeState.stop
        if token:
            try:
                await auth_service.logout(token)
            except AuthUnavailable:
                yield rx.toast.warning(AUTH["logout_warning"])
        self.is_authenticated = False
        self.is_logging_in = False
        self.login_error = ""
        self.retry_after = 0
        self._access_token = ""
        self._refresh_token = ""
        self._sid = ""
        self._facility_id = ""
        self._access_expires_at = None
        self._refresh_expires_at = None
        self._session_expires_at = None
        if old_sid:
            from data_managment_system.states.metrics import _CACHE

            _CACHE.invalidate_namespace(old_sid)
        from data_managment_system.states.metrics import MetricsState
        from data_managment_system.states.rejections import RejectionsState
        from data_managment_system.states.upload import FileInputState

        yield MetricsState.clear_session
        yield RejectionsState.clear_session
        yield FileInputState.clear_session
        yield rx.redirect("/login")

    @rx.event
    def require_login(self) -> Any:
        if not self.is_authenticated:
            return rx.redirect("/login")
        return None

    @rx.event
    def redirect_if_authenticated(self) -> Any:
        if self.is_authenticated:
            return rx.redirect("/")
        return None

    @rx.event
    async def handle_unauthorized(
        self, skip_recovery: bool = False
    ) -> AsyncIterator[Any]:
        recovery = False if skip_recovery else await self.recover_session()
        if recovery is True:
            from data_managment_system.states.metrics import MetricsState
            from data_managment_system.states.realtime import RealtimeState

            # The socket still carries the old access token. Force a fresh
            # connection with the rotated token before the silent reload.
            yield RealtimeState.restart
            yield MetricsState.load_all(silent=True)  # type: ignore[reportCallIssue]
            return
        if recovery is None:
            # A transient refresh failure leaves the existing session and data intact.
            return
        from data_managment_system.states.realtime import RealtimeState

        yield RealtimeState.stop
        old_sid = self._sid
        self.is_authenticated = False
        self.is_logging_in = False
        self.retry_after = 0
        self._access_token = ""
        self._refresh_token = ""
        self._sid = ""
        self._facility_id = ""
        self._access_expires_at = None
        self._refresh_expires_at = None
        self._session_expires_at = None
        self.login_error = "expired"
        if old_sid:
            from data_managment_system.states.metrics import _CACHE

            _CACHE.invalidate_namespace(old_sid)
        from data_managment_system.states.metrics import MetricsState
        from data_managment_system.states.rejections import RejectionsState
        from data_managment_system.states.upload import FileInputState

        yield MetricsState.clear_session
        yield RejectionsState.clear_session
        yield FileInputState.clear_session
        yield rx.redirect("/login")

    async def recover_session(self) -> bool | None:
        """Rotate the token pair once per Reflex client session.

        Returns True on success, False when recovery is impossible/rejected, and
        None when the backend is temporarily unavailable or rate limiting.
        """
        async with self:
            refresh_token = self.current_refresh()
            if refresh_token is None:
                return False
            observed_access = self._access_token
        lock = self.refresh_guard()
        async with lock:
            async with self:
                if self._access_token != observed_access:
                    return True
                refresh_token = self.current_refresh()
                if refresh_token is None:
                    return False
            try:
                dto = await auth_service.refresh(refresh_token)
            except InvalidRefresh:
                return False
            except (RateLimited, AuthUnavailable, BadPayload):
                return None
            async with self:
                if not self.is_authenticated or self._access_token != observed_access:
                    return bool(self.is_authenticated and self._access_token)
                self._access_token = dto.session_token
                self._refresh_token = dto.refresh_token
                self._access_expires_at = dto.access_expires_at
                self._refresh_expires_at = dto.refresh_expires_at
            return True

    def refresh_guard(self) -> asyncio.Lock:
        """Shared per-tab lock for HTTP recovery and socket token rotation."""
        client_token = self.router.session.client_token
        return _refresh_locks.setdefault(client_token, asyncio.Lock())

    @rx.event
    def apply_refresh(
        self,
        session_token: str,
        refresh_token: str,
        access_expires_at: datetime,
        refresh_expires_at: datetime,
    ) -> None:
        """Replace both rotated tokens and their expiries in one state update.

        The sid is the stable 24h session and must never change on refresh.
        """
        self._access_token = session_token
        self._refresh_token = refresh_token
        self._access_expires_at = access_expires_at
        self._refresh_expires_at = refresh_expires_at

    @rx.var
    def facility_id(self) -> str:
        """Public, read-only mirror of the backend-only facility id for display."""
        return self._facility_id

    def current_session(self) -> SessionInfo | None:
        if not self.is_authenticated:
            return None
        if not self._access_token or not self._sid:
            return None
        return SessionInfo(token=self._access_token, sid=self._sid)

    def current_refresh(self) -> str | None:
        """Return the refresh token while it is valid, else ``None``."""
        if not self.is_authenticated:
            return None
        if not self._refresh_token:
            return None
        expires_at = self._refresh_expires_at
        if (
            expires_at is None
            or expires_at.tzinfo is None
            or expires_at.utcoffset() is None
        ):
            return None
        if expires_at <= datetime.now(UTC):
            return None
        return self._refresh_token

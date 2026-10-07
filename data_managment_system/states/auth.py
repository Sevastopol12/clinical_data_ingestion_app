"""Backend-owned session state (token lives in backend-only vars)."""

import logging
from collections.abc import AsyncIterator
from typing import Any

import reflex as rx

import data_managment_system.services.auth as auth_service
from data_managment_system.copy import AUTH
from data_managment_system.models.auth import SessionInfo
from data_managment_system.services.auth import (
    AuthUnavailable,
    InvalidCredentials,
    RateLimited,
)
from data_managment_system.services.http import BadPayload
from data_managment_system.utils.jwt_claims import extract_sid

logger = logging.getLogger(__name__)


class AuthState(rx.State):
    """Session state; token/sid/facility are backend-only."""

    is_authenticated: bool = False
    is_logging_in: bool = False
    login_error: str = ""
    retry_after: int = 0

    _access_token: str = ""
    _sid: str = ""
    _facility_id: str = ""

    @rx.event
    async def login(self, form_data: dict) -> Any:
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        username = str(username).strip() if username is not None else ""
        password = str(password) if password is not None else ""
        if not username or not password:
            self.is_logging_in = False
            self.login_error = "invalid"
            self.retry_after = 0
            return None
        self.is_logging_in = True
        self.login_error = ""
        self.retry_after = 0
        try:
            dto = await auth_service.login(username, password)
        except InvalidCredentials:
            logger.info("login failed: %s", type(InvalidCredentials).__name__)
            self.is_logging_in = False
            self.login_error = "invalid"
            self.retry_after = 0
            return None
        except RateLimited as exc:
            logger.info("login failed: %s", type(exc).__name__)
            self.is_logging_in = False
            self.login_error = "rate_limited"
            self.retry_after = exc.retry_after
            return None
        except (AuthUnavailable, BadPayload) as exc:
            logger.warning("login failed: %s", type(exc).__name__)
            self.is_logging_in = False
            self.login_error = "unavailable"
            self.retry_after = 0
            return None
        try:
            sid = extract_sid(dto.session_token)
        except ValueError as exc:
            logger.warning("login failed: %s", type(exc).__name__)
            self.is_logging_in = False
            self.login_error = "unavailable"
            self.retry_after = 0
            return None
        self._access_token = dto.session_token
        self._sid = sid
        self._facility_id = str(dto.facility_id)
        self.is_authenticated = True
        self.is_logging_in = False
        self.login_error = ""
        self.retry_after = 0
        return rx.redirect("/")

    @rx.event
    async def logout(self) -> AsyncIterator[Any]:
        token = self._access_token
        old_sid = self._sid
        if token:
            try:
                await auth_service.logout(token)
            except AuthUnavailable as exc:
                logger.warning("logout failed: %s", type(exc).__name__)
                yield rx.toast.warning(AUTH["logout_warning"])
        self.is_authenticated = False
        self.is_logging_in = False
        self.login_error = ""
        self.retry_after = 0
        self._access_token = ""
        self._sid = ""
        self._facility_id = ""
        if old_sid:
            from data_managment_system.states.metrics import _CACHE

            _CACHE.invalidate_namespace(old_sid)
        from data_managment_system.states.metrics import MetricsState
        from data_managment_system.states.upload import FileInputState

        yield MetricsState.clear_session
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
    async def handle_unauthorized(self) -> AsyncIterator[Any]:
        old_sid = self._sid
        self.is_authenticated = False
        self.is_logging_in = False
        self.retry_after = 0
        self._access_token = ""
        self._sid = ""
        self._facility_id = ""
        self.login_error = "expired"
        if old_sid:
            from data_managment_system.states.metrics import _CACHE

            _CACHE.invalidate_namespace(old_sid)
        from data_managment_system.states.metrics import MetricsState
        from data_managment_system.states.upload import FileInputState

        yield MetricsState.clear_session
        yield FileInputState.clear_session
        yield rx.redirect("/login")

    def current_session(self) -> SessionInfo | None:
        if not self.is_authenticated:
            return None
        if not self._access_token or not self._sid:
            return None
        return SessionInfo(token=self._access_token, sid=self._sid)

"""Backend-owned auth service (login/logout only, no Reflex)."""

from typing import Any

import httpx

from data_managment_system.config import settings
from data_managment_system.models.auth import LoginResponse
from data_managment_system.services.http import BackendError, BadPayload

_TIMEOUT_SECONDS = 15.0
_DEFAULT_RETRY_AFTER = 60


class InvalidCredentials(BackendError):
    """Username/password rejected (401) or rejected payload (422)."""


class RateLimited(BackendError):
    """Login rate limited (429)."""

    def __init__(self, retry_after: int = _DEFAULT_RETRY_AFTER) -> None:
        self.retry_after = retry_after
        super().__init__("login rate limited")


class AuthUnavailable(BackendError):
    """Auth backend unavailable (503, unexpected status, or network error)."""


def _base_url() -> httpx.URL:
    return httpx.URL(str(settings.backend_base_url))


def _login_url() -> httpx.URL:
    return _base_url().join(settings.login_path.lstrip("/"))


def _logout_url() -> httpx.URL:
    return _base_url().join(settings.logout_path.lstrip("/"))


def _parse_retry_after(value: Any) -> int:
    try:
        parsed = int(str(value).strip())
    except (ValueError, TypeError, AttributeError):
        return _DEFAULT_RETRY_AFTER
    return max(1, min(3600, parsed))


async def login(username: str, password: str) -> LoginResponse:
    """Authenticate against the backend and return the session DTO."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.post(
                _login_url(),
                json={"username": username, "password": password},
            )
    except httpx.RequestError as exc:
        raise AuthUnavailable("auth unavailable") from exc

    if response.status_code in (401, 422):
        raise InvalidCredentials("invalid credentials")
    if response.status_code == 429:
        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
        raise RateLimited(retry_after)
    if not 200 <= response.status_code < 300:
        raise AuthUnavailable("auth unavailable")

    try:
        data = response.json()
    except (ValueError, TypeError) as exc:
        raise BadPayload("invalid login payload") from exc
    try:
        return LoginResponse.model_validate(data)
    except Exception as exc:
        raise BadPayload("invalid login payload") from exc


async def logout(access_token: str) -> None:
    """Best-effort backend logout; 401 counts as success."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.post(
                _logout_url(),
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.RequestError as exc:
        raise AuthUnavailable("auth unavailable") from exc

    if 200 <= response.status_code < 300:
        return
    if response.status_code == 401:
        return
    raise AuthUnavailable("auth unavailable")

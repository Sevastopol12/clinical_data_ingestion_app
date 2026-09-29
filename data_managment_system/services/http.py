import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import httpx

from data_managment_system.config import settings

logging.getLogger("httpx").setLevel(logging.WARNING)


@dataclass(frozen=True)
class AuthContext:
    access_token: str | None
    facility_id: UUID


ContextProvider = Callable[[], AuthContext]


class BackendError(Exception):
    """Base error for backend transport and HTTP failures."""


class Unauthorized(BackendError):
    """The backend rejected the request credentials."""


class Forbidden(BackendError):
    """The backend rejected access to the resource."""


class Unavailable(BackendError):
    """The backend metrics store is unavailable."""


class BadPayload(BackendError):
    """The backend returned invalid JSON or an invalid DTO payload."""


class BackendClient:
    def __init__(
        self,
        base_url: str,
        context: ContextProvider,
        http: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = httpx.URL(base_url)
        self._context = context
        self._http = http or httpx.AsyncClient(base_url=base_url)

    async def get_json(
        self,
        path: str,
        params: Mapping[str, str] | None = None,
        *,
        scope_facility: bool = True,
    ) -> Any:
        context = self._context()
        request_params = dict(params or {})
        headers: dict[str, str] = {}
        if scope_facility:
            request_params["facility_id"] = str(context.facility_id)
        if context.access_token is not None:
            headers["Authorization"] = f"Bearer {context.access_token}"

        try:
            response = await self._http.get(
                self._base_url.join(path.lstrip("/")),
                params=request_params,
                headers=headers,
            )
        except httpx.RequestError as exc:
            raise BackendError("backend request failed") from exc

        if response.status_code == 401:
            raise Unauthorized("backend request unauthorized")
        if response.status_code == 403:
            raise Forbidden("backend request forbidden")
        if response.status_code == 503:
            raise Unavailable("backend unavailable")
        if not 200 <= response.status_code < 300:
            raise BackendError("backend request failed")

        try:
            return response.json()
        except (ValueError, TypeError) as exc:
            raise BadPayload("backend returned invalid JSON") from exc


def default_context() -> AuthContext:
    return AuthContext(None, settings.dev_facility_id)


_client: BackendClient | None = None


def get_client() -> BackendClient:
    global _client
    if _client is None:
        _client = BackendClient(settings.backend_base_url, default_context)
    return _client

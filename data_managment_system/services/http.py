from collections.abc import Mapping
from typing import Any

import httpx

from data_managment_system.config import settings


class BackendError(Exception):
    """Base error for backend transport and HTTP failures."""


class Unauthorized(BackendError):
    """The backend rejected the request credentials."""


class Forbidden(BackendError):
    """The backend rejected access to the resource."""


class NotFound(BackendError):
    """The requested backend resource does not exist."""


class Gone(BackendError):
    """The requested backend resource has expired."""


class InvalidRequest(BackendError):
    """The backend rejected the request as invalid."""


class Unavailable(BackendError):
    """The backend metrics store is unavailable."""


class BadPayload(BackendError):
    """The backend returned invalid JSON or an invalid DTO payload."""


class BackendClient:
    def __init__(
        self,
        base_url: str,
        http: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = httpx.URL(base_url)
        self._http = http or httpx.AsyncClient(base_url=base_url)

    async def get_json(
        self,
        path: str,
        params: Mapping[str, str] | None = None,
        *,
        access_token: str,
    ) -> Any:
        request_params = dict(params or {})
        headers = {"Authorization": f"Bearer {access_token}"}
        request_url = httpx.URL(f"{str(self._base_url).rstrip('/')}/{path.strip('/')}")

        try:
            response = await self._http.get(
                request_url,
                params=request_params,
                headers=headers,
            )
        except httpx.RequestError as exc:
            raise BackendError("backend request failed") from exc

        if response.status_code == 401:
            raise Unauthorized("backend request unauthorized")
        if response.status_code == 403:
            raise Forbidden("backend request forbidden")
        if response.status_code == 404:
            raise NotFound("backend resource not found")
        if response.status_code == 410:
            raise Gone("backend resource expired")
        if response.status_code == 422:
            raise InvalidRequest("backend request invalid")
        if response.status_code == 503:
            raise Unavailable("backend unavailable")
        if not 200 <= response.status_code < 300:
            raise BackendError("backend request failed")

        try:
            return response.json()
        except (ValueError, TypeError) as exc:
            raise BadPayload("backend returned invalid JSON") from exc


_client: BackendClient | None = None


def get_client() -> BackendClient:
    global _client
    if _client is None:
        _client = BackendClient(settings.backend_base_url)
    return _client

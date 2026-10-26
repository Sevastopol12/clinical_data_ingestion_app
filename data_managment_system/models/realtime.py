"""WebSocket frame DTOs mirroring the backend realtime contract.

All datetimes are ISO-8601 with a timezone (``ApiDateTime``); naive values are
rejected. Unknown frame types are forward compatible and parse to ``Ignored``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from data_managment_system.models.metrics import ApiDateTime


class _Frame(BaseModel):
    model_config = ConfigDict(extra="ignore")


class MetricsUpdated(_Frame):
    """Metrics for this socket's facility were recomputed; refetch."""

    type: Literal["metrics.updated"]
    facility_id: UUID
    computed_at: ApiDateTime


class SessionExpiring(_Frame):
    """The current access/refresh pair expires soon; send ``session.refresh``."""

    type: Literal["session.expiring"]
    expires_in: int


class SessionRefreshed(_Frame):
    """Reply to a successful refresh; replace BOTH tokens (sid unchanged)."""

    type: Literal["session.refreshed"]
    session_token: str
    refresh_token: str
    access_expires_at: ApiDateTime
    refresh_expires_at: ApiDateTime


class ErrorFrame(_Frame):
    """Non-fatal protocol error; the server may close afterwards."""

    type: Literal["error"]
    code: Literal["refresh_invalid", "unavailable"]
    message: str


class Ignored(_Frame):
    """Fallback for unknown or malformed frames."""

    type: str = ""


class SessionRefresh(_Frame):
    """Client -> server refresh request."""

    type: Literal["session.refresh"] = "session.refresh"
    refresh_token: str


KnownServerFrame = Annotated[
    MetricsUpdated | SessionExpiring | SessionRefreshed | ErrorFrame,
    Field(discriminator="type"),
]
ServerFrame = KnownServerFrame | Ignored

_KNOWN_TYPES = frozenset(
    {"metrics.updated", "session.expiring", "session.refreshed", "error"}
)
_KNOWN_FRAME_ADAPTER: TypeAdapter[KnownServerFrame] = TypeAdapter(KnownServerFrame)


def parse_server_frame(payload: Mapping[str, Any] | str | bytes) -> ServerFrame:
    """Parse one server frame without ever raising.

    Malformed JSON, non-object payloads, a missing/non-string ``type`` and unknown
    types all return ``Ignored()``. A known ``type`` whose fields fail validation
    (missing, wrong type, naive datetime) also returns ``Ignored()`` so a protocol
    bug can never tear down the socket loop. Raw frames and tokens are not logged.
    """
    data: Any = payload
    if isinstance(payload, bytes):
        try:
            data = payload.decode("utf-8")
        except UnicodeDecodeError:
            return Ignored()
    elif isinstance(payload, str):
        try:
            data = json.loads(payload)
        except (ValueError, TypeError):
            return Ignored()
    if not isinstance(data, Mapping):
        return Ignored()
    frame_type = data.get("type")
    if not isinstance(frame_type, str) or frame_type not in _KNOWN_TYPES:
        return Ignored()
    try:
        return _KNOWN_FRAME_ADAPTER.validate_python(data)
    except (ValidationError, TypeError, ValueError):
        return Ignored()


__all__ = [
    "ErrorFrame",
    "Ignored",
    "KnownServerFrame",
    "MetricsUpdated",
    "ServerFrame",
    "SessionExpiring",
    "SessionRefresh",
    "SessionRefreshed",
    "parse_server_frame",
]

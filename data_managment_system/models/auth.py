"""Auth DTOs mirroring the backend contract."""

from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from data_managment_system.models.metrics import ApiDateTime


class LoginResponse(BaseModel):
    """Successful login payload from the backend."""

    model_config = ConfigDict(extra="ignore")

    session_token: str
    refresh_token: str
    facility_id: UUID
    access_expires_at: ApiDateTime
    refresh_expires_at: ApiDateTime
    session_expires_at: ApiDateTime


class RefreshResponse(BaseModel):
    """Rotated access and refresh token pair."""

    model_config = ConfigDict(extra="ignore")

    session_token: str
    refresh_token: str
    access_expires_at: ApiDateTime
    refresh_expires_at: ApiDateTime


@dataclass(frozen=True)
class SessionInfo:
    """Backend-side session snapshot passed to services per call."""

    token: str
    sid: str

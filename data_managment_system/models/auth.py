"""Auth DTOs mirroring the backend contract."""

from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoginResponse(BaseModel):
    """Successful login payload from the backend."""

    model_config = ConfigDict(extra="ignore")

    session_token: str
    facility_id: UUID


@dataclass(frozen=True)
class SessionInfo:
    """Backend-side session snapshot passed to services per call."""

    token: str
    sid: str

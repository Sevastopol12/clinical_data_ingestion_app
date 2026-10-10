from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from data_managment_system.models.metrics import ApiDateTime


class RejectedFile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    file_id: UUID
    # The backend contract (RejectedArtifactItem in dto.py) does not send this
    # field at all — not even as null — so it must default to None rather
    # than merely allow None. build_rejection_rows() already falls back to
    # REJECTIONS["fallback_title"] when this is falsy.
    source_filename: str | None = None
    artifact_created_at: ApiDateTime | None = None
    artifact_expires_at: ApiDateTime | None = None
    rejected_row_count: int = 0
    state: str


class RejectionsPage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    items: list[RejectedFile]
    next_cursor: str | None


class RejectionDownload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    download_url: str = Field(repr=False)

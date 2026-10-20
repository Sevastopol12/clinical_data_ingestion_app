from datetime import datetime
from enum import Enum
from pathlib import Path
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, computed_field, field_validator

from data_managment_system.models.metrics import ApiDateTime

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_BATCH_FILES = 10
SUPPORTED_FORMATS: dict[str, str] = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
VIETNAM_TZ_NAME = "Asia/Ho_Chi_Minh"
VIETNAM_TZ = ZoneInfo(VIETNAM_TZ_NAME)


def now_vietnam() -> datetime:
    """Return the current aware Vietnam-local datetime."""

    return datetime.now(VIETNAM_TZ)


class FileStatus(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SUCCEED = "SUCCEED"
    ERROR = "ERROR"
    REJECTED = "REJECTED"


class RequestPresignedCreate(BaseModel):
    filename: str
    base64_hashed_digest: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        extension = Path(filename).suffix.lstrip(".").lower()
        if extension not in SUPPORTED_FORMATS:
            supported = ", ".join(f".{item}" for item in SUPPORTED_FORMATS)
            raise ValueError(
                f"Unsupported file extension '.{extension}'. Supported extensions: {supported}"
            )
        return filename

    @computed_field
    @property
    def content_type(self) -> str:
        return SUPPORTED_FORMATS[Path(self.filename).suffix.lstrip(".").lower()]


class CompleteUploadCreate(BaseModel):
    file_id: UUID
    filename: str
    size_bytes: int
    mappings: dict[str, str | None]

    @computed_field
    @property
    def created_at(self) -> str:
        return f"{now_vietnam():%Y_%m_%d}"

    @computed_field
    @property
    def object_key(self) -> str:
        return f"{self.file_id}/{self.filename}"

    @computed_field
    @property
    def content_type(self) -> str:
        return SUPPORTED_FORMATS[Path(self.filename).suffix.lstrip(".").lower()]


class RequestPresignedResponse(BaseModel):
    file_id: UUID
    presigned_url: str


class CompleteUploadResponse(BaseModel):
    file_id: UUID
    filename: str | None = None
    object_key: str
    status: FileStatus
    error_code: str | None = None
    error_message: str | None = None
    created_at: ApiDateTime


class MappingRequest(BaseModel):
    filename: str
    columns: list[str]


class MappingResponse(BaseModel):
    filename: str
    mapping: dict[str, str | None] | None = None

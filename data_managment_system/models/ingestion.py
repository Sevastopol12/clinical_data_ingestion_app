from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, field_validator

from data_managment_system.models.metrics import ApiDateTime

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_BATCH_FILES = 10
SUPPORTED_FORMATS: dict[str, str] = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class FileStatus(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SUCCEED = "SUCCEED"
    ERROR = "ERROR"


class IngestionCreate(BaseModel):
    filename: str
    content: bytes | None = Field(default=None, exclude=True)
    facility_id: UUID

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


class IngestionComplete(BaseModel):
    id: UUID
    facility_id: UUID
    content_hash: str
    size_bytes: int | None = None
    mappings: dict[str, Any] | None = None


class IngestionResponse(BaseModel):
    id: UUID
    facility_id: UUID
    filename: str | None = None
    object_key: str
    status: FileStatus

    presigned_url: str | None = None

    error_code: str | None = None
    error_message: str | None = None
    accepted_row_count: int = 0
    rejected_row_count: int = 0

    created_at: ApiDateTime


class MappingRequest(BaseModel):
    filename: str
    columns: list[str]


class MappingResponse(BaseModel):
    filename: str
    mapping: dict[str, str | None] | None = None

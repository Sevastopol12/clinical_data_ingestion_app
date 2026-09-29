from datetime import datetime
from enum import Enum
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, computed_field, field_validator

supported_format: dict[str, str] = {
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
    content: bytes | None = None
    facility_id: UUID

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        extension = Path(filename).suffix.lstrip(".").lower()
        if extension not in supported_format:
            supported = ", ".join(f".{item}" for item in supported_format)
            raise ValueError(
                f"Unsupported file extension '.{extension}'. Supported extensions: {supported}"
            )
        return filename

    @computed_field
    @property
    def content_type(self) -> str:
        return supported_format[Path(self.filename).suffix.lstrip(".").lower()]


class IngestionComplete(BaseModel):
    id: UUID
    content_hash: str
    size_bytes: int | None = None
    mappings: dict[str, str] | None = None


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

    created_at: datetime


class IngestionDetail(BaseModel):
    response: IngestionResponse
    metadata: IngestionCreate


class MappingRequest(BaseModel):
    filename: str
    columns: list[str]


class MappingResponse(BaseModel):
    filename: str
    mapping: dict[str, str | None] | None = None

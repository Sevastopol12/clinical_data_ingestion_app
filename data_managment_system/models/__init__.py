from pydantic import BaseModel, computed_field, field_validator
from pathlib import Path
from uuid import UUID
from datetime import datetime
from enum import Enum

supported_format: dict[str, str] = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class FileStatus(str, Enum):
    CREATED: str = "CREATED"
    QUEUED: str = "QUEUED"
    PROCESSING: str = "PROCESSING"
    SUCCEED: str = "SUCCEED"
    ERROR: str = "ERROR"


class IngestionCreate(BaseModel):
    filename: str
    content: bytes | None = None

    @computed_field
    @property
    def content_type(self) -> str:
        return supported_format[Path(self.filename).suffix.lstrip(".").lower()]

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, content_type: str):
        if content_type not in supported_format:
            raise ValueError(
                f"Unsupported file extension '.{content_type}'. Supported extensions are: {supported_format}"
            )
        return content_type


class IngestionComplete(BaseModel):
    id: UUID
    content_hash: str
    size_bytes: int | None = None
    mappings: dict[str, str] | None = None


class IngestionResponse(BaseModel):
    id: UUID
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


__all__ = ["IngestionCreate", "IngestionComplete", "IngestionResponse", "FileStatus", "IngestionDetail"]

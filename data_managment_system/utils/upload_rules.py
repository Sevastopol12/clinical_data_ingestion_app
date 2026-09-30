from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from data_managment_system.models.ingestion import (
    MAX_BATCH_FILES,
    MAX_FILE_BYTES,
    SUPPORTED_FORMATS,
)
from data_managment_system.utils.columns import normalize_column_name


@dataclass(frozen=True)
class IncomingFile:
    filename: str
    size: int
    oversize: bool = False


@dataclass(frozen=True)
class Admission:
    admitted: list[IncomingFile]
    rejected: dict[str, int]


class MappingRowVM(BaseModel):
    model_config = ConfigDict(frozen=True)
    source: str
    target: str = ""
    error: str = ""


class FileVM(BaseModel):
    model_config = ConfigDict(frozen=True)
    filename: str
    size_bytes: int
    size_label: str
    kind: str
    stage: str = "ready"
    failure_stage: str = ""
    mapping_pending: bool = False
    rows: list[MappingRowVM] = Field(default_factory=list)


def unique_sources(headers: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(headers))


def admit_files(existing: Sequence[str], incoming: Sequence[IncomingFile]) -> Admission:
    names = list(existing)
    admitted: list[IncomingFile] = []
    rejected: dict[str, int] = {}
    for item in incoming:
        if item.oversize or item.size > MAX_FILE_BYTES:
            reason = "oversize"
        elif item.filename.rsplit(".", 1)[-1].lower() not in SUPPORTED_FORMATS:
            reason = "bad_type"
        elif item.filename in names:
            reason = ""
        elif len(names) >= MAX_BATCH_FILES:
            reason = "batch_full"
        else:
            reason = ""
        if reason:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        admitted.append(item)
        if item.filename not in names:
            names.append(item.filename)
    return Admission(admitted, rejected)


def normalize_target(raw: str) -> str | None:
    if not raw.strip():
        return None
    return normalize_column_name(raw)


def validate_rows(rows: Sequence[MappingRowVM]) -> list[MappingRowVM]:
    normalized: list[str | None] = []
    errors: list[str] = []
    for row in rows:
        try:
            value = normalize_target(row.target)
            normalized.append(value)
            errors.append("")
        except ValueError:
            normalized.append(None)
            errors.append("empty-normalized")
    for index, value in enumerate(normalized):
        if value is not None and normalized.count(value) > 1:
            errors[index] = "duplicate-target"
    return [row.model_copy(update={"error": error}) for row, error in zip(rows, errors)]


def to_record_mappings(rows: Sequence[MappingRowVM]) -> dict[str, str | None]:
    valid = validate_rows(rows)
    return {row.source: normalize_target(row.target) for row in valid if not row.error}


def apply_suggestions(
    rows: Sequence[MappingRowVM], mapping: dict[str, str | None]
) -> list[MappingRowVM]:
    return [
        row.model_copy(update={"target": mapping[row.source] or ""})
        if row.source in mapping
        else row
        for row in rows
    ]


def format_file_size(n: int) -> str:
    if n < 1024 * 1024:
        return f"{round(n / 1024)} KB"
    return f"{n / (1024 * 1024):.1f} MB".replace(".0 MB", " MB")


__all__ = [
    "Admission",
    "FileVM",
    "IncomingFile",
    "MappingRowVM",
    "admit_files",
    "apply_suggestions",
    "format_file_size",
    "normalize_target",
    "to_record_mappings",
    "unique_sources",
    "validate_rows",
]

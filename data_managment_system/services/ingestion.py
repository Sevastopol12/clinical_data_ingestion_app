import base64
import logging
from asyncio import Semaphore, gather
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha3_256
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from data_managment_system.config import settings
from data_managment_system.models import (
    FileStatus,
    IngestionComplete,
    IngestionCreate,
    IngestionResponse,
    MappingRequest,
    MappingResponse,
)

logger = logging.getLogger(__name__)
StageCallback = Callable[[str, str], Awaitable[None]]


class FailureStage(StrEnum):
    PRESIGN = "presign"
    STORAGE = "storage"
    RECORD = "record"


@dataclass(frozen=True)
class UploadJob:
    filename: str
    content: bytes
    mappings: dict[str, str | None]
    ingestion_id: UUID | None = None


@dataclass(frozen=True)
class FileOutcome:
    filename: str
    ok: bool
    failed_stage: FailureStage | None
    ingestion_id: UUID | None


def hash_content(raw_bytes: bytes) -> str:
    encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    return sha3_256(encoded.encode("utf-8")).hexdigest()


def _headers(context: Any) -> dict[str, str]:
    token = getattr(context, "access_token", None)
    return {"Authorization": f"Bearer {token}"} if token is not None else {}


def _log_failure(stage: FailureStage, exc: BaseException, index: int) -> None:
    status = getattr(getattr(exc, "response", None), "status_code", None)
    logger.warning(
        "upload stage failed",
        extra={
            "stage": stage.value,
            "exception_type": type(exc).__name__,
            "status_code": status,
            "file_index": index,
        },
    )


async def _submit_one(
    client: httpx.AsyncClient,
    semaphore: Semaphore,
    job: UploadJob,
    context: Any,
    on_stage: StageCallback,
    index: int,
) -> FileOutcome:
    async with semaphore:
        ingestion_id = job.ingestion_id
        stage = (
            FailureStage.RECORD if ingestion_id is not None else FailureStage.PRESIGN
        )
        try:
            if ingestion_id is None:
                await on_stage(job.filename, "presigning")
                create = IngestionCreate(
                    filename=job.filename,
                    content=job.content,
                    facility_id=context.facility_id,
                )
                response = await client.post(
                    settings.request_upload,
                    json=create.model_dump(mode="json"),
                    headers=_headers(context),
                    timeout=30,
                )
                response.raise_for_status()
                presign = IngestionResponse.model_validate(response.json())
                if (
                    presign.status is not FileStatus.CREATED
                    or not presign.presigned_url
                ):
                    raise ValueError("invalid presign response")
                ingestion_id = presign.id
                stage = FailureStage.STORAGE
                await on_stage(job.filename, "uploading")
                storage = await client.put(
                    presign.presigned_url,
                    content=job.content,
                    headers={"Content-Type": create.content_type},
                    timeout=120,
                )
                storage.raise_for_status()
            stage = FailureStage.RECORD
            await on_stage(job.filename, "recording")
            complete = IngestionComplete(
                id=ingestion_id,
                facility_id=context.facility_id,
                content_hash=hash_content(job.content),
                size_bytes=len(job.content),
                mappings=job.mappings,
            )
            record = await client.post(
                settings.request_record.format(file=ingestion_id),
                json=complete.model_dump(mode="json"),
                headers=_headers(context),
                timeout=30,
            )
            record.raise_for_status()
            return FileOutcome(job.filename, True, None, ingestion_id)
        except Exception as exc:  # noqa: BLE001
            _log_failure(stage, exc, index)
            return FileOutcome(job.filename, False, stage, ingestion_id)


async def submit_batch(
    jobs: list[UploadJob],
    context: Any,
    on_stage: StageCallback,
    *,
    concurrency: int = 5,
) -> list[FileOutcome]:
    semaphore = Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        results = await gather(
            *(
                _submit_one(client, semaphore, job, context, on_stage, index)
                for index, job in enumerate(jobs)
            ),
            return_exceptions=True,
        )
    outcomes: list[FileOutcome] = []
    for index, result in enumerate(results):
        if isinstance(result, FileOutcome):
            outcomes.append(result)
        else:
            outcomes.append(
                FileOutcome(
                    jobs[index].filename,
                    False,
                    FailureStage.RECORD,
                    jobs[index].ingestion_id,
                )
            )
    return outcomes


async def _fetch_mapping_one(
    client: httpx.AsyncClient, semaphore: Semaphore, request: MappingRequest
) -> MappingResponse | None:
    async with semaphore:
        try:
            response = await client.post(
                settings.request_column_mapping.format(
                    filename=quote(request.filename, safe="")
                ),
                json=request.model_dump(mode="json"),
                timeout=15,
            )
            response.raise_for_status()
            result = MappingResponse.model_validate(response.json())
            return result if result.filename == request.filename else None
        except Exception as exc:  # noqa: BLE001
            _log_failure(FailureStage.RECORD, exc, 0)
            return None


async def fetch_mapping_suggestions(
    requests: list[MappingRequest], *, concurrency: int = 5
) -> list[MappingResponse | None]:
    semaphore = Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        results = await gather(
            *(_fetch_mapping_one(client, semaphore, request) for request in requests),
            return_exceptions=True,
        )
    return [
        result if isinstance(result, MappingResponse) else None for result in results
    ]


__all__ = [
    "FailureStage",
    "FileOutcome",
    "StageCallback",
    "UploadJob",
    "fetch_mapping_suggestions",
    "hash_content",
    "submit_batch",
]

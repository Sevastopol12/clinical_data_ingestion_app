import base64
from asyncio import Semaphore, gather
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from urllib.parse import quote
from uuid import UUID

import httpx

from data_managment_system.config import settings
from data_managment_system.models import (
    CompleteUploadCreate,
    MappingRequest,
    MappingResponse,
    RequestPresignedCreate,
    RequestPresignedResponse,
)
from data_managment_system.services.http import Unauthorized

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

    object_key: str | None = None


@dataclass(frozen=True)
class FileOutcome:
    filename: str
    ok: bool
    failed_stage: FailureStage | None
    ingestion_id: UUID | None
    status_code: int | None = None


def hash_content(raw_bytes: bytes) -> str:
    digest = sha256(raw_bytes).digest()
    return base64.b64encode(digest).decode("ascii")


def _headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _status_code(exc: BaseException) -> int | None:
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    return status if isinstance(status, int) else None


async def _submit_one(
    client: httpx.AsyncClient,
    semaphore: Semaphore,
    job: UploadJob,
    access_token: str,
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
                base64_hashed_digest = hash_content(job.content)

                create = RequestPresignedCreate(
                    filename=job.filename, base64_hashed_digest=base64_hashed_digest
                )

                response = await client.post(
                    settings.request_upload,
                    json=create.model_dump(mode="json"),
                    headers=_headers(access_token),
                    timeout=30,
                )
                response.raise_for_status()

                presign = RequestPresignedResponse.model_validate(response.json())
                ingestion_id = presign.file_id
                presigned_url = presign.presigned_url

                stage = FailureStage.STORAGE
                await on_stage(job.filename, "uploading")
                storage = await client.put(
                    presigned_url,
                    content=job.content,
                    headers={
                        "x-amz-checksum-sha256": base64_hashed_digest,
                        "Content-Type": create.content_type,
                    },
                    timeout=120,
                )
                storage.raise_for_status()

            stage = FailureStage.RECORD

            await on_stage(job.filename, "recording")
            complete = CompleteUploadCreate(
                file_id=ingestion_id,
                filename=job.filename,
                size_bytes=len(job.content),
                mappings=job.mappings,
            )
            record = await client.post(
                settings.request_record.format(file=ingestion_id),
                json=complete.model_dump(mode="json"),
                headers=_headers(access_token),
                timeout=30,
            )
            record.raise_for_status()
            return FileOutcome(job.filename, True, None, ingestion_id)
        except Exception as exc:  # noqa: BLE001
            return FileOutcome(
                job.filename, False, stage, ingestion_id, _status_code(exc)
            )


async def submit_batch(
    jobs: list[UploadJob],
    access_token: str,
    on_stage: StageCallback,
    *,
    concurrency: int = 5,
) -> list[FileOutcome]:
    semaphore = Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        results = await gather(
            *(
                _submit_one(client, semaphore, job, access_token, on_stage, index)
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
                    _status_code(result) if isinstance(result, BaseException) else None,
                )
            )
    return outcomes


async def _fetch_mapping_one(
    client: httpx.AsyncClient,
    semaphore: Semaphore,
    request: MappingRequest,
    access_token: str,
) -> MappingResponse | None:
    async with semaphore:
        try:
            response = await client.post(
                settings.request_column_mapping.format(
                    filename=quote(request.filename, safe="")
                ),
                json=request.model_dump(mode="json"),
                headers=_headers(access_token),
                timeout=15,
            )
            response.raise_for_status()
            result = MappingResponse.model_validate(response.json())
            return result if result.filename == request.filename else None
        except Exception as exc:
            if _status_code(exc) == 401:
                raise Unauthorized("mapping request unauthorized") from exc
            return None


async def fetch_mapping_suggestions(
    requests: list[MappingRequest],
    access_token: str,
    *,
    concurrency: int = 5,
) -> list[MappingResponse | None]:
    semaphore = Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        results = await gather(
            *(
                _fetch_mapping_one(client, semaphore, request, access_token)
                for request in requests
            ),
            return_exceptions=True,
        )
    for result in results:
        if isinstance(result, Unauthorized):
            raise result
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

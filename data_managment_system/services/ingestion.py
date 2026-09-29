import base64
from asyncio import Semaphore, create_task, gather
from hashlib import sha3_256
from typing import cast

from httpx import AsyncClient, HTTPError, HTTPStatusError, Response

from data_managment_system.config import settings
from data_managment_system.models import (
    FileStatus,
    IngestionComplete,
    IngestionCreate,
    IngestionResponse,
    MappingRequest,
    MappingResponse,
)


def encode_content(raw_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(raw_bytes).decode("utf-8")


# TODO(verify D5): content_hash contract
def hash_content(encoded_bytes: str) -> str:
    sha_object = sha3_256()
    sha_object.update(encoded_bytes.encode())
    return sha_object.hexdigest()


# Request presigned url
async def request_presigned_url(
    client: AsyncClient, file: IngestionCreate
) -> IngestionResponse:
    response = await client.post(
        url=settings.request_upload,
        # TODO(verify D6): facility_id remains out of this HTTP body.
        json={"filename": file.filename, "content_type": file.content_type},
        timeout=30,
    )
    response.raise_for_status()
    return IngestionResponse.model_validate(response.json())


async def storage_upload(
    client: AsyncClient, connection_response: IngestionResponse, file: IngestionCreate
) -> IngestionResponse:
    # Load file
    try:
        result = await client.put(
            connection_response.presigned_url or "",
            content=file.content,
            headers={"Content-Type": file.content_type},
            timeout=120,
        )

        result.raise_for_status()

    except HTTPStatusError as exc:
        connection_response.status = FileStatus.ERROR
        connection_response.error_code = str(
            exc.response.status_code
        )  # TODO(B4): error_code is typed as str
        connection_response.error_message = str(exc)

    except HTTPError as exc:
        connection_response.status = FileStatus.ERROR
        connection_response.error_code = None
        connection_response.error_message = str(exc)

    finally:  # TODO(B4): do not return from finally
        return connection_response  # noqa: B012


async def keep_upload_record(client: AsyncClient, file: IngestionComplete) -> Response:
    # Record file load
    response = await client.post(
        url=settings.request_record.format(file=file.id),
        json=file.model_dump(mode="json"),
        timeout=30,
    )

    return response


async def fetch_column_mapping(
    client: AsyncClient, request: MappingRequest
) -> MappingResponse:
    response = await client.post(
        url=settings.request_column_mapping.format(filename=request.filename),
        json=request.model_dump(),
        timeout=15,
    )
    response.raise_for_status()
    return MappingResponse.model_validate(response.json())


async def _load_to_storage(
    files: list[IngestionCreate],
) -> list[IngestionResponse | Exception]:
    async with (  # noqa: SIM117
        Semaphore(  # TODO(B4): acquire the semaphore inside each task
            5
        )
    ):
        async with AsyncClient() as client:
            connection_requests = [
                request_presigned_url(client=client, file=file) for file in files
            ]
            connection_responses = (
                await gather(  # TODO(B4): preserve per-file exceptions
                    *connection_requests
                )
            )
            upload_tasks = [
                storage_upload(client=client, file=file, connection_response=response)
                for file, response in zip(files, connection_responses)
            ]
            results = await gather(*upload_tasks, return_exceptions=True)

    return [
        result if isinstance(result, Exception) else cast(IngestionResponse, result)
        for result in results
    ]


async def _record_file(files: list[IngestionComplete]) -> None:
    async with Semaphore(5), AsyncClient() as client:
        tasks = [
            create_task(keep_upload_record(client=client, file=file)) for file in files
        ]
        await gather(*tasks)  # TODO(B4): preserve per-file exceptions


async def _fetch_all_column_mappings(
    map_requests: list[MappingRequest],
) -> list[MappingResponse]:
    semaphore = Semaphore(5)

    async with AsyncClient() as client:

        async def fetch(request: MappingRequest) -> MappingResponse:
            async with semaphore:
                return await fetch_column_mapping(client, request)

        responses = await gather(
            *(fetch(request) for request in map_requests),
            return_exceptions=True,
        )

    results: list[MappingResponse] = []
    for result in responses:
        if isinstance(result, MappingResponse):
            results.append(result)
    return results


__all__ = [
    "_fetch_all_column_mappings",
    "_load_to_storage",
    "_record_file",
    "encode_content",
    "fetch_column_mapping",
    "hash_content",
    "keep_upload_record",
    "request_presigned_url",
    "storage_upload",
]

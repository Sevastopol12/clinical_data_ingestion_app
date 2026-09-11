import os
from httpx import AsyncClient
from requests import Response
from dotenv import load_dotenv
from data_managment_system.models import FileStatus
from httpx import HTTPStatusError, HTTPError

from data_managment_system.models import (
    IngestionCreate,
    IngestionComplete,
    IngestionResponse,
)

load_dotenv()


# Request presigned url
async def request_presigned_url(
    client: AsyncClient, file: IngestionCreate
) -> IngestionResponse:
    response = await client.post(
        url=os.getenv("REQUEST_UPLOAD"),
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
            connection_response.presigned_url,
            content=file.content,
            headers={"Content-Type": file.content_type},
            timeout=120,
        )

        result.raise_for_status()

    except HTTPStatusError as exc:
        connection_response.status = FileStatus.ERROR
        connection_response.error_code = exc.response.status_code
        connection_response.error_message = str(exc)

    except HTTPError as exc:
        connection_response.status = FileStatus.ERROR
        connection_response.error_code = None
        connection_response.error_message = str(exc)

    finally:
        return connection_response


async def keep_upload_record(client: AsyncClient, file: IngestionComplete) -> Response:
    # Record file load
    response = await client.post(
        url=os.getenv("REQUEST_RECORD").format(file=file.id),
        json=file.model_dump(mode="json"),
        timeout=30,
    )

    return response


__all__ = ["request_presigned_url", "storage_upload", "keep_upload_record"]

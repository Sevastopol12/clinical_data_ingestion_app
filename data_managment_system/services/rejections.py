from typing import Any

from pydantic import ValidationError

from data_managment_system.config import settings
from data_managment_system.models.rejections import (
    RejectionDownload,
    RejectionsPage,
)
from data_managment_system.services.http import BackendClient, BadPayload


def _parse_model(payload: Any, model: type[Any]) -> Any:
    try:
        return model.model_validate(payload)
    except (ValidationError, TypeError, ValueError) as exc:
        raise BadPayload("backend returned an invalid DTO payload") from exc


async def fetch_rejections(
    client: BackendClient,
    *,
    access_token: str,
    limit: int | None = None,
    cursor: str | None = None,
    state: str | None = None,
) -> RejectionsPage:
    params = {
        key: str(value)
        for key, value in {"limit": limit, "cursor": cursor, "state": state}.items()
        if value is not None
    }
    payload = await client.get_json(
        settings.request_rejection_artifact, params, access_token=access_token
    )
    return _parse_model(payload, RejectionsPage)


async def fetch_download(
    client: BackendClient, file_id: str, *, access_token: str
) -> RejectionDownload:
    payload = await client.get_json(
        f"{settings.request_rejection_artifact}/{file_id}/download",
        {"redirect": "false"},
        access_token=access_token,
    )
    return _parse_model(payload, RejectionDownload)

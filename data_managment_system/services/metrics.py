from typing import Any

from pydantic import ValidationError

from data_managment_system.models.metrics import (
    ComorbidityMetric,
    DataQualityMetric,
    Grain,
    MetricsStatus,
    PatientStateMetric,
    PeriodSummaryMetric,
)
from data_managment_system.services.http import BackendClient, BadPayload

PREFIX = "/metrics/v1"


def _parse_list(payload: Any, model: type[Any]) -> list[Any]:
    if not isinstance(payload, list):
        raise BadPayload("backend returned an invalid list payload")
    try:
        return [model.model_validate(item) for item in payload]
    except (ValidationError, TypeError, ValueError) as exc:
        raise BadPayload("backend returned an invalid DTO payload") from exc


async def fetch_period_summary(
    client: BackendClient, grain: Grain
) -> list[PeriodSummaryMetric]:
    rows = _parse_list(
        await client.get_json(f"{PREFIX}/period-summary", {"grain": grain}),
        PeriodSummaryMetric,
    )
    return sorted(rows, key=lambda row: row.period_start)


async def fetch_comorbidity(
    client: BackendClient, grain: Grain
) -> list[ComorbidityMetric]:
    rows = _parse_list(
        await client.get_json(f"{PREFIX}/comorbidity", {"grain": grain}),
        ComorbidityMetric,
    )
    return sorted(rows, key=lambda row: row.period_start)


async def fetch_data_quality(
    client: BackendClient, grain: Grain
) -> list[DataQualityMetric]:
    rows = _parse_list(
        await client.get_json(f"{PREFIX}/data-quality", {"grain": grain}),
        DataQualityMetric,
    )
    return sorted(rows, key=lambda row: row.period_start)


async def fetch_out_of_control(client: BackendClient) -> list[PatientStateMetric]:
    return _parse_list(
        await client.get_json(f"{PREFIX}/patient-state/out-of-control"),
        PatientStateMetric,
    )


async def fetch_status(client: BackendClient) -> MetricsStatus:
    payload = await client.get_json(f"{PREFIX}/status", scope_facility=False)
    try:
        return MetricsStatus.model_validate(payload)
    except (ValidationError, TypeError, ValueError) as exc:
        raise BadPayload("backend returned an invalid status payload") from exc

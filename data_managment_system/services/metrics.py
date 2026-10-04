from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

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


@dataclass(frozen=True)
class MetricsScope:
    kind: Literal["all", "rollup", "facility"]
    facility_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.kind == "facility":
            if self.facility_id is None:
                raise ValueError("facility scope requires facility_id")
        elif self.facility_id is not None:
            raise ValueError(f"{self.kind} scope must not include facility_id")

    @classmethod
    def all_facilities(cls) -> "MetricsScope":
        return cls(kind="all")

    @classmethod
    def rollup(cls) -> "MetricsScope":
        return cls(kind="rollup")

    @classmethod
    def facility(cls, facility_id: UUID) -> "MetricsScope":
        return cls(kind="facility", facility_id=facility_id)

    @property
    def token(self) -> str:
        if self.kind == "facility":
            return f"facility:{self.facility_id}"
        return self.kind

    def to_query_params(self) -> dict[str, str]:
        if self.kind == "all":
            return {}
        if self.kind == "rollup":
            return {"facility_id": "ALL"}
        return {"facility_id": str(self.facility_id)}


def _parse_list(payload: Any, model: type[Any]) -> list[Any]:
    if not isinstance(payload, list):
        raise BadPayload("backend returned an invalid list payload")
    try:
        return [model.model_validate(item) for item in payload]
    except (ValidationError, TypeError, ValueError) as exc:
        raise BadPayload("backend returned an invalid DTO payload") from exc


async def fetch_period_summary(
    client: BackendClient, scope: MetricsScope, grain: Grain
) -> list[PeriodSummaryMetric]:
    params = {**scope.to_query_params(), "grain": grain}
    rows = _parse_list(
        await client.get_json(f"{PREFIX}/period-summary", params),
        PeriodSummaryMetric,
    )
    return sorted(rows, key=lambda row: row.period_start)


async def fetch_comorbidity(
    client: BackendClient, scope: MetricsScope, grain: Grain
) -> list[ComorbidityMetric]:
    params = {**scope.to_query_params(), "grain": grain}
    rows = _parse_list(
        await client.get_json(f"{PREFIX}/comorbidity", params),
        ComorbidityMetric,
    )
    return sorted(rows, key=lambda row: row.period_start)


async def fetch_data_quality(
    client: BackendClient, scope: MetricsScope, grain: Grain
) -> list[DataQualityMetric]:
    params = {**scope.to_query_params(), "grain": grain}
    rows = _parse_list(
        await client.get_json(f"{PREFIX}/data-quality", params),
        DataQualityMetric,
    )
    return sorted(rows, key=lambda row: row.period_start)


async def fetch_out_of_control(
    client: BackendClient, scope: MetricsScope
) -> list[PatientStateMetric]:
    if scope.kind == "rollup":
        raise ValueError("patient-state does not accept rollup scope")
    return _parse_list(
        await client.get_json(
            f"{PREFIX}/patient-state/out-of-control",
            scope.to_query_params(),
        ),
        PatientStateMetric,
    )


async def fetch_status(client: BackendClient) -> MetricsStatus:
    payload = await client.get_json(f"{PREFIX}/status")
    try:
        return MetricsStatus.model_validate(payload)
    except (ValidationError, TypeError, ValueError) as exc:
        raise BadPayload("backend returned an invalid status payload") from exc

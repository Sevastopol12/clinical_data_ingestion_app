from datetime import datetime
from typing import Annotated, Literal, get_args
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _require_tz(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must include a timezone")
    return value


# Every nullable field below must set `default=None` explicitly. Pydantic v2 does
# NOT give `X | None` an implicit default the way v1 did — without `default=None`
# the field is required, and an omitted (not merely null) key raises ValidationError
# -> BadPayload -> the generic "Couldn't load this card" state. See the same fix
# already applied to `source_filename` in models/rejections.py.
ApiDateTime = Annotated[datetime, AfterValidator(_require_tz)]
Grain = Literal["TODAY", "3D", "2W", "3M", "6M", "ALL"]
GRAINS: tuple[Grain, ...] = get_args(Grain)


class IssueCodeCount(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: str
    count: int


class PeriodSummaryMetric(BaseModel):
    model_config = ConfigDict(extra="ignore")

    facility_id: UUID
    period_grain: Grain
    period_start: ApiDateTime
    period_end: ApiDateTime
    visit_count: int
    unique_patient_count: int
    new_patient_count: int
    returning_patient_count: int
    repeat_visit_ratio: float | None = Field(default=None, allow_inf_nan=False)
    pct_tha: float | None = Field(default=None, allow_inf_nan=False)
    pct_dtd: float | None = Field(default=None, allow_inf_nan=False)
    pct_comorbid: float | None = Field(default=None, allow_inf_nan=False)
    bp_control_rate: float | None = Field(default=None, allow_inf_nan=False)
    bp_stage_normal_count: int
    bp_stage_elevated_count: int
    bp_stage_1_count: int
    bp_stage_2_count: int
    bp_stage_severe_count: int
    glycemic_control_rate: float | None = Field(default=None, allow_inf_nan=False)
    avg_glucose: float | None = Field(default=None, allow_inf_nan=False)
    median_glucose: float | None = Field(default=None, allow_inf_nan=False)
    avg_hba1c: float | None = Field(default=None, allow_inf_nan=False)
    median_hba1c: float | None = Field(default=None, allow_inf_nan=False)
    computed_at: ApiDateTime


class ComorbidityMetric(BaseModel):
    model_config = ConfigDict(extra="ignore")

    facility_id: UUID
    period_grain: Grain
    period_start: ApiDateTime
    diagnosis_label: str
    patient_count: int
    computed_at: ApiDateTime


class PatientStateMetric(BaseModel):
    model_config = ConfigDict(extra="ignore")

    patient_key: str
    facility_id: UUID
    ho_ten: str | None
    sdt: str | None
    dia_chi: str | None
    last_visit_date: ApiDateTime | None
    last_systolic: float | None = Field(default=None, allow_inf_nan=False)
    last_diastolic: float | None = Field(default=None, allow_inf_nan=False)
    last_glucose: float | None = Field(default=None, allow_inf_nan=False)
    last_hba1c: float | None = Field(default=None, allow_inf_nan=False)
    is_bp_controlled: bool | None
    is_bp_severe: bool | None
    is_hba1c_controlled: bool | None
    is_out_of_control: bool | None
    has_contact: bool
    first_visit_date: ApiDateTime | None
    visit_count: int
    computed_at: ApiDateTime


class DataQualityMetric(BaseModel):
    model_config = ConfigDict(extra="ignore")

    facility_id: UUID
    period_grain: Grain
    period_start: ApiDateTime
    period_end: ApiDateTime
    files_processed: int
    avg_mapping_coverage_ratio: float | None = Field(default=None, allow_inf_nan=False)
    total_rows_seen: int
    accepted_rows: int
    rejected_rows: int
    ignored_duplicate_row_count: int
    top_issue_codes: list[IssueCodeCount]
    computed_at: ApiDateTime


class MetricsStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    last_computed_at: ApiDateTime | None

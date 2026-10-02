from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, Field


def _require_tz(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must include a timezone")
    return value


ApiDateTime = Annotated[datetime, AfterValidator(_require_tz)]
Grain = Literal["1D", "3D", "1W", "2W", "1M"]


class IssueCodeCount(BaseModel):
    code: str
    count: int


class PeriodSummaryMetric(BaseModel):
    facility_id: UUID | None
    period_grain: str
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
    bp_stage_1_count: int
    bp_stage_2_count: int
    bp_stage_crisis_count: int
    glycemic_control_rate: float | None = Field(default=None, allow_inf_nan=False)
    avg_glucose: float | None = Field(default=None, allow_inf_nan=False)
    median_glucose: float | None = Field(default=None, allow_inf_nan=False)
    avg_hba1c: float | None = Field(default=None, allow_inf_nan=False)
    median_hba1c: float | None = Field(default=None, allow_inf_nan=False)
    uploaded_date: ApiDateTime


class ComorbidityMetric(BaseModel):
    facility_id: UUID | None
    period_grain: str
    period_start: ApiDateTime
    diagnosis_label: str
    patient_count: int
    uploaded_date: ApiDateTime


class PatientStateMetric(BaseModel):
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
    is_bp_crisis: bool | None
    is_hba1c_controlled: bool | None
    is_out_of_control: bool | None
    has_contact: bool
    first_visit_date: ApiDateTime | None
    visit_count: int
    uploaded_date: ApiDateTime


class DataQualityMetric(BaseModel):
    facility_id: UUID | None
    period_grain: str
    period_start: ApiDateTime
    period_end: ApiDateTime
    files_processed: int
    avg_coverage_ratio: float | None = Field(default=None, allow_inf_nan=False)
    total_rows_seen: int
    accepted_rows: int
    flagged_rows: int
    rejected_rows: int
    top_issue_codes: list[IssueCodeCount]
    uploaded_date: ApiDateTime


class MetricsStatus(BaseModel):
    last_computed_at: ApiDateTime | None = None

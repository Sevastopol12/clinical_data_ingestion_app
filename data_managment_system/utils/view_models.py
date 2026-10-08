"""Frozen, display-ready shapes used by dashboard components."""

from pydantic import BaseModel, ConfigDict, Field


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class FieldVM(_FrozenModel):
    label: str
    value: str
    pct: int | None = None


class TileVM(_FrozenModel):
    label: str
    value: str
    tone: str
    width_pct: int = 0


class KpiCardVM(_FrozenModel):
    fields: list[FieldVM]
    tiles: list[TileVM]
    empty_note: str


class BarRowVM(_FrozenModel):
    label: str
    value: str
    width_pct: int


class RankingCardVM(_FrozenModel):
    rows: list[BarRowVM]


class IssueRowVM(_FrozenModel):
    title: str
    field: str
    field_hint: str
    count: str
    width_pct: int


class DataQualityVM(_FrozenModel):
    coverage_fields: list[FieldVM] = Field(default_factory=list)
    row_fields: list[FieldVM] = Field(default_factory=list)
    issues: list[IssueRowVM] = Field(default_factory=list)


class BadgeVM(_FrozenModel):
    label: str
    tone: str


class PatientRowVM(_FrozenModel):
    patient_key: str
    name: str
    phone: str
    address: str
    last_visit: str
    bp: str
    glucose: str
    hba1c: str
    badges: list[BadgeVM]


class FreshnessVM(_FrozenModel):
    state: str
    iso: str
    absolute: str

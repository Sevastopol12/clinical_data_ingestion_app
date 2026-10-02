"""Frozen, display-ready shapes used by dashboard components."""

from pydantic import BaseModel, ConfigDict


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class FieldVM(_FrozenModel):
    label: str
    value: str


class TileVM(_FrozenModel):
    label: str
    value: str
    tone: str


class KpiCardVM(_FrozenModel):
    period_label: str
    fields: list[FieldVM]
    tiles: list[TileVM]
    empty_note: str


class BarRowVM(_FrozenModel):
    label: str
    value: str
    width_pct: int


class RankingCardVM(_FrozenModel):
    period_label: str
    rows: list[BarRowVM]


class IssueRowVM(_FrozenModel):
    label: str
    code: str
    count: str


class DataQualityVM(_FrozenModel):
    period_label: str
    fields: list[FieldVM]
    issues: list[IssueRowVM]


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

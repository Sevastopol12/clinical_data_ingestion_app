"""Small, typed dashboard fixtures used by the temporary dashboard route."""

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.utils.view_models import (
    BadgeVM,
    BarRowVM,
    DataQualityVM,
    FieldVM,
    FreshnessVM,
    IssueRowVM,
    KpiCardVM,
    PatientRowVM,
    RankingCardVM,
    TileVM,
)


def _kpi(*fields: tuple[str, str], tiles: list[TileVM] | None = None) -> KpiCardVM:
    return KpiCardVM(
        period_label="29 Sep 2026",
        fields=[FieldVM(label=label, value=value) for label, value in fields],
        tiles=tiles or [],
        empty_note=COMMON["no_visits"],
    )


FIXTURE_CARDS = {
    "visits": _kpi(
        (DASHBOARD["unique_patients"], "18"),
        (DASHBOARD["new_patients"], "6"),
        (DASHBOARD["returning_patients"], "12"),
        (DASHBOARD["repeat_visit_ratio"], "66.7%"),
    ),
    "patient_mix": _kpi(
        (DASHBOARD["hypertension"], "72.2%"),
        (DASHBOARD["diabetes"], "44.4%"),
        (DASHBOARD["comorbid"], "27.8%"),
    ),
    "clinical_control": _kpi(
        (DASHBOARD["bp_control"], "61.1%"),
        (DASHBOARD["glycemic_control"], "55.6%"),
        tiles=[
            TileVM(label=DASHBOARD["normal"], value="11", tone="normal"),
            TileVM(label=DASHBOARD["stage_1"], value="4", tone="stage1"),
            TileVM(label=DASHBOARD["stage_2"], value="2", tone="stage2"),
            TileVM(label=DASHBOARD["crisis"], value="1", tone="crisis"),
        ],
    ),
    "glucose_hba1c": _kpi(
        (DASHBOARD["average_glucose"], "7.8 mmol/L"),
        (DASHBOARD["median_glucose"], "7.2 mmol/L"),
        (DASHBOARD["average_hba1c"], "7.1 %"),
        (DASHBOARD["median_hba1c"], "6.8 %"),
    ),
    "comorbidity": RankingCardVM(
        period_label="22 Sep - 28 Sep 2026",
        rows=[
            BarRowVM(label="Hypertension + Diabetes", value="8", width_pct=100),
            BarRowVM(label="Hypertension + CKD", value="4", width_pct=50),
            BarRowVM(label="Diabetes + CKD", value="2", width_pct=25),
        ],
    ),
    "data_quality": DataQualityVM(
        period_label="29 Sep 2026",
        fields=[
            FieldVM(label=DASHBOARD["files_processed"], value="4"),
            FieldVM(label=DASHBOARD["average_coverage"], value="96.5%"),
            FieldVM(label=DASHBOARD["rows_seen"], value="125"),
            FieldVM(label=DASHBOARD["rows_accepted"], value="118"),
            FieldVM(label=DASHBOARD["rows_flagged"], value="5"),
            FieldVM(label=DASHBOARD["rows_rejected"], value="2"),
        ],
        issues=[
            IssueRowVM(
                label="Missing required field", code="MISSING_REQUIRED_FIELD", count="3"
            ),
            IssueRowVM(label="Invalid phone", code="INVALID_PHONE", count="2"),
        ],
    ),
}

FIXTURE_FRESHNESS = FreshnessVM(
    state="ok", iso="2026-09-29T08:30:00+07:00", absolute="29 Sep 2026, 08:30"
)

FIXTURE_PATIENTS = [
    PatientRowVM(
        patient_key=f"patient-{index}",
        name=f"Nguyen Thi Patient {index}",
        phone=f"09000000{index:02d}",
        address=f"{index} Main Street",
        last_visit="28 Sep 2026",
        bp="148/92",
        glucose="8.1 mmol/L",
        hba1c="7.4 %",
        badges=(
            [BadgeVM(label=DASHBOARD["badge_no_contact"], tone="muted")]
            if index == 2
            else (
                [BadgeVM(label=DASHBOARD["badge_crisis"], tone="crisis")]
                if index == 1
                else []
            )
        ),
    )
    for index in range(1, 26)
]

__all__ = ["FIXTURE_CARDS", "FIXTURE_FRESHNESS", "FIXTURE_PATIENTS"]

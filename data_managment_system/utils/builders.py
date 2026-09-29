"""Pure builders for metric DTOs and display-ready view models."""

from collections.abc import Sequence

from data_managment_system import copy
from data_managment_system.models.metrics import (
    ComorbidityMetric,
    DataQualityMetric,
    Grain,
    MetricsStatus,
    PeriodSummaryMetric,
)
from data_managment_system.utils.format import (
    bucket_label,
    format_count,
    format_datetime_abs,
    format_glucose,
    format_hba1c,
    format_percent,
)
from data_managment_system.utils.view_models import (
    BarRowVM,
    DataQualityVM,
    FieldVM,
    FreshnessVM,
    IssueRowVM,
    KpiCardVM,
    RankingCardVM,
    TileVM,
)


def _latest[MetricT: (PeriodSummaryMetric, ComorbidityMetric, DataQualityMetric)](
    rows: Sequence[MetricT],
) -> MetricT | None:
    return max(rows, key=lambda row: row.period_start) if rows else None


def _period_label(
    row: PeriodSummaryMetric | ComorbidityMetric | DataQualityMetric, grain: Grain
) -> str:
    end = getattr(row, "period_end", None)
    return bucket_label(grain, row.period_start, end)


def build_visits(rows: Sequence[PeriodSummaryMetric], grain: Grain) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    return KpiCardVM(
        period_label=_period_label(row, grain),
        fields=[
            FieldVM(
                label=copy.DASHBOARD["visits"],
                value=format_count(None if empty else row.visit_count),
            ),
            FieldVM(
                label=copy.DASHBOARD["unique_patients"],
                value=format_count(None if empty else row.unique_patient_count),
            ),
            FieldVM(
                label=copy.DASHBOARD["new_patients"],
                value=format_count(None if empty else row.new_patient_count),
            ),
            FieldVM(
                label=copy.DASHBOARD["returning_patients"],
                value=format_count(None if empty else row.returning_patient_count),
            ),
            FieldVM(
                label=copy.DASHBOARD["repeat_visit_ratio"],
                value=format_percent(None if empty else row.repeat_visit_ratio),
            ),
        ],
        tiles=[],
        empty_note=copy.COMMON["no_visits"] if empty else "",
    )


def build_patient_mix(
    rows: Sequence[PeriodSummaryMetric], grain: Grain
) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    return KpiCardVM(
        period_label=_period_label(row, grain),
        fields=[
            FieldVM(
                label=copy.DASHBOARD["hypertension"],
                value=format_percent(None if empty else row.pct_tha),
            ),
            FieldVM(
                label=copy.DASHBOARD["diabetes"],
                value=format_percent(None if empty else row.pct_dtd),
            ),
            FieldVM(
                label=copy.DASHBOARD["comorbid"],
                value=format_percent(None if empty else row.pct_comorbid),
            ),
        ],
        tiles=[],
        empty_note=copy.COMMON["no_visits"] if empty else "",
    )


def build_clinical_control(
    rows: Sequence[PeriodSummaryMetric], grain: Grain
) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    return KpiCardVM(
        period_label=_period_label(row, grain),
        fields=[
            FieldVM(
                label=copy.DASHBOARD["bp_control"],
                value=format_percent(None if empty else row.bp_control_rate),
            ),
            FieldVM(
                label=copy.DASHBOARD["glycemic_control"],
                value=format_percent(None if empty else row.glycemic_control_rate),
            ),
        ],
        tiles=[
            TileVM(
                label=copy.DASHBOARD["normal"],
                value=format_count(None if empty else row.bp_stage_normal_count),
                tone="normal",
            ),
            TileVM(
                label=copy.DASHBOARD["stage_1"],
                value=format_count(None if empty else row.bp_stage_1_count),
                tone="stage1",
            ),
            TileVM(
                label=copy.DASHBOARD["stage_2"],
                value=format_count(None if empty else row.bp_stage_2_count),
                tone="stage2",
            ),
            TileVM(
                label=copy.DASHBOARD["crisis"],
                value=format_count(None if empty else row.bp_stage_crisis_count),
                tone="crisis",
            ),
        ],
        empty_note=copy.COMMON["no_visits"] if empty else "",
    )


def build_glucose_hba1c(
    rows: Sequence[PeriodSummaryMetric], grain: Grain
) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    return KpiCardVM(
        period_label=_period_label(row, grain),
        fields=[
            FieldVM(
                label=copy.DASHBOARD["average_glucose"],
                value=format_glucose(None if empty else row.avg_glucose),
            ),
            FieldVM(
                label=copy.DASHBOARD["median_glucose"],
                value=format_glucose(None if empty else row.median_glucose),
            ),
            FieldVM(
                label=copy.DASHBOARD["average_hba1c"],
                value=format_hba1c(None if empty else row.avg_hba1c),
            ),
            FieldVM(
                label=copy.DASHBOARD["median_hba1c"],
                value=format_hba1c(None if empty else row.median_hba1c),
            ),
        ],
        tiles=[],
        empty_note=copy.COMMON["no_visits"] if empty else "",
    )


def build_comorbidity(
    rows: Sequence[ComorbidityMetric], grain: Grain
) -> RankingCardVM | None:
    if not rows:
        return None
    latest_start = max(row.period_start for row in rows)
    latest_rows = sorted(
        (row for row in rows if row.period_start == latest_start),
        key=lambda row: (-row.patient_count, row.diagnosis_label),
    )
    maximum = max((row.patient_count for row in latest_rows), default=0)
    return RankingCardVM(
        period_label=bucket_label(grain, latest_start, None),
        rows=[
            BarRowVM(
                label=row.diagnosis_label,
                value=format_count(row.patient_count),
                width_pct=round(row.patient_count / maximum * 100) if maximum else 0,
            )
            for row in latest_rows
        ],
    )


def build_data_quality(
    rows: Sequence[DataQualityMetric], grain: Grain
) -> DataQualityVM | None:
    row = _latest(rows)
    if row is None:
        return None
    return DataQualityVM(
        period_label=_period_label(row, grain),
        fields=[
            FieldVM(
                label=copy.DASHBOARD["files_processed"],
                value=format_count(row.files_processed),
            ),
            FieldVM(
                label=copy.DASHBOARD["average_coverage"],
                value=format_percent(row.avg_coverage_ratio),
            ),
            FieldVM(
                label=copy.DASHBOARD["rows_seen"],
                value=format_count(row.total_rows_seen),
            ),
            FieldVM(
                label=copy.DASHBOARD["rows_accepted"],
                value=format_count(row.accepted_rows),
            ),
            FieldVM(
                label=copy.DASHBOARD["rows_flagged"],
                value=format_count(row.flagged_rows),
            ),
            FieldVM(
                label=copy.DASHBOARD["rows_rejected"],
                value=format_count(row.rejected_rows),
            ),
        ],
        issues=[
            IssueRowVM(
                label=copy.ISSUE_CODE_LABELS.get(issue.code, issue.code),
                code=issue.code,
                count=format_count(issue.count),
            )
            for issue in row.top_issue_codes
        ],
    )


def build_freshness(status: MetricsStatus | None, failed: bool) -> FreshnessVM:
    if failed:
        return FreshnessVM(state="error", iso="", absolute="")
    if status is None or status.last_computed_at is None:
        return FreshnessVM(state="never", iso="", absolute="")
    return FreshnessVM(
        state="ok",
        iso=status.last_computed_at.isoformat(),
        absolute=format_datetime_abs(status.last_computed_at),
    )

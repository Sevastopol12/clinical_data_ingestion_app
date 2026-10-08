"""Pure builders for metric DTOs and display-ready view models."""

from collections.abc import Sequence

from data_managment_system import copy
from data_managment_system.models.metrics import (
    ComorbidityMetric,
    DataQualityMetric,
    MetricsStatus,
    PeriodSummaryMetric,
)
from data_managment_system.utils.format import (
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


def _display_pct(rate: float | None) -> int | None:
    """Display-only 0-100 fraction of a 0-1 backend rate; None stays None."""
    if rate is None:
        return None
    return max(0, min(100, round(rate * 100)))


def _stage_widths(counts: Sequence[int | None]) -> list[int]:
    """Scale stage counts to the largest count; 0 when all are 0/None."""
    values = [0 if count is None else count for count in counts]
    maximum = max(values, default=0)
    if maximum <= 0:
        return [0] * len(values)
    return [round(value / maximum * 100) for value in values]


def build_visits(rows: Sequence[PeriodSummaryMetric]) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    repeat_rate = None if empty else row.repeat_visit_ratio
    return KpiCardVM(
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
                value=format_percent(repeat_rate),
                pct=_display_pct(repeat_rate),
            ),
        ],
        tiles=[],
        empty_note="",
    )


def build_patient_mix(rows: Sequence[PeriodSummaryMetric]) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    tha = None if empty else row.pct_tha
    dtd = None if empty else row.pct_dtd
    comorbid = None if empty else row.pct_comorbid
    return KpiCardVM(
        fields=[
            FieldVM(
                label=copy.DASHBOARD["hypertension"],
                value=format_percent(tha),
                pct=_display_pct(tha),
            ),
            FieldVM(
                label=copy.DASHBOARD["diabetes"],
                value=format_percent(dtd),
                pct=_display_pct(dtd),
            ),
            FieldVM(
                label=copy.DASHBOARD["comorbid"],
                value=format_percent(comorbid),
                pct=_display_pct(comorbid),
            ),
        ],
        tiles=[],
        empty_note="",
    )


def build_clinical_control(
    rows: Sequence[PeriodSummaryMetric],
) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    bp_rate = None if empty else row.bp_control_rate
    glycemic_rate = None if empty else row.glycemic_control_rate
    stage_counts: list[int | None] = [
        None if empty else row.bp_stage_normal_count,
        None if empty else row.bp_stage_elevated_count,
        None if empty else row.bp_stage_1_count,
        None if empty else row.bp_stage_2_count,
        None if empty else row.bp_stage_severe_count,
    ]
    widths = _stage_widths(stage_counts)
    return KpiCardVM(
        fields=[
            FieldVM(
                label=copy.DASHBOARD["bp_control"],
                value=format_percent(bp_rate),
                pct=_display_pct(bp_rate),
            ),
            FieldVM(
                label=copy.DASHBOARD["glycemic_control"],
                value=format_percent(glycemic_rate),
                pct=_display_pct(glycemic_rate),
            ),
        ],
        tiles=[
            TileVM(
                label=copy.DASHBOARD["normal"],
                value=format_count(stage_counts[0]),
                tone="normal",
                width_pct=widths[0],
            ),
            TileVM(
                label=copy.DASHBOARD["elevated"],
                value=format_count(stage_counts[1]),
                tone="elevated",
                width_pct=widths[1],
            ),
            TileVM(
                label=copy.DASHBOARD["stage_1"],
                value=format_count(stage_counts[2]),
                tone="stage1",
                width_pct=widths[2],
            ),
            TileVM(
                label=copy.DASHBOARD["stage_2"],
                value=format_count(stage_counts[3]),
                tone="stage2",
                width_pct=widths[3],
            ),
            TileVM(
                label=copy.DASHBOARD["severe"],
                value=format_count(stage_counts[4]),
                tone="severe",
                width_pct=widths[4],
            ),
        ],
        empty_note="",
    )


def build_glucose_hba1c(rows: Sequence[PeriodSummaryMetric]) -> KpiCardVM | None:
    row = _latest(rows)
    if row is None:
        return None
    empty = row.visit_count == 0
    return KpiCardVM(
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
        empty_note="",
    )


def build_comorbidity(rows: Sequence[ComorbidityMetric]) -> RankingCardVM | None:
    if not rows:
        return None
    latest_start = max(row.period_start for row in rows)
    latest_rows = sorted(
        (row for row in rows if row.period_start == latest_start),
        key=lambda row: (-row.patient_count, row.diagnosis_label),
    )
    maximum = max((row.patient_count for row in latest_rows), default=0)
    return RankingCardVM(
        rows=[
            BarRowVM(
                label=row.diagnosis_label,
                value=format_count(row.patient_count),
                width_pct=round(row.patient_count / maximum * 100) if maximum else 0,
            )
            for row in latest_rows
        ],
    )


def build_data_quality(rows: Sequence[DataQualityMetric]) -> DataQualityVM | None:
    row = _latest(rows)
    if row is None:
        return None
    coverage_fields = [
        FieldVM(
            label=copy.DASHBOARD["files_processed"],
            value=format_count(row.files_processed),
        ),
        FieldVM(
            label=copy.DASHBOARD["average_mapping_coverage"],
            value=format_percent(row.avg_mapping_coverage_ratio),
        ),
    ]
    row_fields = [
        FieldVM(
            label=copy.DASHBOARD["rows_seen"],
            value=format_count(row.total_rows_seen),
        ),
        FieldVM(
            label=copy.DASHBOARD["rows_clean"],
            value=format_count(row.accepted_clean_rows),
        ),
        FieldVM(
            label=copy.DASHBOARD["rows_with_flags"],
            value=format_count(row.accepted_with_flags_rows),
        ),
        FieldVM(
            label=copy.DASHBOARD["rows_rejected"],
            value=format_count(row.rejected_rows),
        ),
    ]
    maximum = max((issue.count for issue in row.top_issue_codes), default=0)
    issues: list[IssueRowVM] = []
    for issue in row.top_issue_codes:
        issue_type, separator, column = issue.code.partition(":")
        issues.append(
            IssueRowVM(
                title=copy.ISSUE_CODE_LABELS.get(
                    issue_type,
                    issue_type.replace("_", " ").capitalize(),
                ),
                field=copy.FIELD_LABELS.get(column, column) if separator else "",
                field_hint=column if separator else "",
                count=format_count(issue.count),
                width_pct=round(issue.count / maximum * 100) if maximum else 0,
            )
        )
    return DataQualityVM(
        coverage_fields=coverage_fields,
        row_fields=row_fields,
        issues=issues,
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

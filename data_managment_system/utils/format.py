"""Pure formatting helpers for display-ready dashboard values."""

from __future__ import annotations

from datetime import datetime

from data_managment_system import copy
from data_managment_system.models.metrics import Grain

DISPLAY_TZ = "Asia/Ho_Chi_Minh"
MISSING = "—"


def format_percent(x: float | None) -> str:
    return MISSING if x is None else f"{x * 100:.1f}%"


def format_count(n: int | None) -> str:
    return MISSING if n is None else f"{n:,}"


def format_glucose(x: float | None) -> str:
    return MISSING if x is None else f"{x:.1f} mmol/L"


def format_hba1c(x: float | None) -> str:
    return MISSING if x is None else f"{x:.1f} %"


def format_date(dt: datetime | None) -> str:
    return MISSING if dt is None else f"{dt.day} {dt:%b %Y}"


def format_datetime_abs(dt: datetime | None) -> str:
    return MISSING if dt is None else f"{dt.day} {dt:%b %Y, %H:%M}"


def _month_year(dt: datetime) -> str:
    return f"{dt:%b %Y}"


def bucket_label(
    grain: Grain, start: datetime | None, end: datetime | None = None
) -> str:
    """Wording-only period label for a card header (never backend boundaries)."""
    if grain == "TODAY":
        return format_date(start) if start is not None else MISSING
    if grain == "ALL":
        return copy.PERIOD_LABELS["ALL"]
    if grain in ("3M", "6M"):
        if start is None:
            return MISSING
        if end is None:
            return f"From {_month_year(start)}"
        return f"{_month_year(start)} – {_month_year(end)}"
    # 3D, 2W: date range, or "From ..." when there is no period end.
    if start is None:
        return MISSING
    if end is None:
        return f"From {format_date(start)}"
    return f"{format_date(start)} – {format_date(end)}"

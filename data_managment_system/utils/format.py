"""Pure formatting helpers for display-ready dashboard values."""

from datetime import datetime
from typing import Literal

DISPLAY_TZ = "Asia/Ho_Chi_Minh"
Grain = Literal["1D", "3D", "1W", "2W", "1M"]
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


def bucket_label(grain: Grain, start: datetime, end: datetime | None) -> str:
    if grain == "1D":
        return format_date(start)
    if grain == "1M":
        return start.strftime("%b %Y")
    if end is None:
        return f"From {format_date(start)}"
    return f"{format_date(start)} – {format_date(end)}"

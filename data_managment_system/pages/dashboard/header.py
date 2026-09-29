"""Dashboard header and freshness indicator."""

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.states.metrics import MetricsState

DISPLAY_TZ = "Asia/Ho_Chi_Minh"


def _freshness_chip() -> rx.Component:
    moment = rx.moment(
        MetricsState.freshness.iso,
        from_now=True,
        interval=60000,
        tz=DISPLAY_TZ,
    )
    chip = rx.match(
        MetricsState.freshness.state,
        ("ok", rx.hstack(rx.text(COMMON["updated"]), moment, spacing="1")),
        ("never", rx.text(COMMON["not_computed"])),
        ("error", rx.text(COMMON["status_unavailable"])),
        rx.text(COMMON["loading"]),
    )
    return rx.tooltip(
        rx.badge(chip),
        content=MetricsState.freshness.absolute,
    )


def header() -> rx.Component:
    return rx.hstack(
        rx.heading(DASHBOARD["title"], size="7"),
        _freshness_chip(),
        justify="between",
        align="center",
        width="100%",
        gap="3",
        flex_wrap="wrap",
    )


__all__ = ["header"]

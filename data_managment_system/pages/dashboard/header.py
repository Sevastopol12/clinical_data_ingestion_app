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
        ("ok", rx.hstack(rx.text(COMMON["updated"]), moment, gap="0.25em")),
        ("never", rx.text(COMMON["not_computed"])),
        ("error", rx.text(COMMON["status_unavailable"])),
        rx.text(COMMON["loading"]),
    )
    return rx.tooltip(
        rx.badge(
            rx.hstack(rx.icon("refresh-cw", size=14), chip, gap="0.25em"),
            variant="surface",
            _hover={"cursor": "pointer"},
            on_click=MetricsState.refresh,
        ),
        content=MetricsState.freshness.absolute,
    )


def header() -> rx.Component:
    return rx.hstack(
        rx.heading(DASHBOARD["title"], size="6", weight="bold"),
        _freshness_chip(),
        justify="between",
        align="center",
        width="100%",
        gap="0.75em",
        flex_wrap="wrap",
        margin_bottom="0.5em",
    )


__all__ = ["header"]

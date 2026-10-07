"""Dashboard header and freshness indicator."""

import reflex as rx

from data_managment_system.copy import AUTH, COMMON, DASHBOARD
from data_managment_system.states.auth import AuthState
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import DESKTOP_HEADER_GAP, responsive

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
            size="1",
            _hover={"cursor": "pointer"},
            on_click=MetricsState.refresh,
        ),
        content=MetricsState.freshness.absolute,
    )


def _logout_button() -> rx.Component:
    return rx.tooltip(
        rx.icon_button(
            rx.icon("log-out"),
            aria_label=AUTH["logout_label"],
            variant="ghost",
            on_click=AuthState.logout,
            _hover={"cursor": "pointer"},
        ),
        content=AUTH["logout_tooltip"],
    )


def header() -> rx.Component:
    return rx.hstack(
        rx.heading(
            DASHBOARD["title"],
            size="7",
            weight="bold",
            letter_spacing="-0.02em",
        ),
        rx.hstack(
            _freshness_chip(),
            _logout_button(),
            gap="0.5em",
            align="center",
        ),
        justify="between",
        align="center",
        width="100%",
        gap="0.75em",
        flex_wrap="wrap",
        margin_bottom=responsive("0.5em", lg=DESKTOP_HEADER_GAP),
    )


__all__ = ["header"]

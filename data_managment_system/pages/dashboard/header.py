"""Dashboard top bar and hero."""

import reflex as rx

from data_managment_system.copy import AUTH, COMMON, DASHBOARD
from data_managment_system.pages.rejections import rejections_button
from data_managment_system.states.auth import AuthState
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    DESKTOP_HEADER_GAP,
    DESKTOP_PAGE_PADDING_X,
    PANEL_ICON_TILE,
    TEXT_MUTED,
    TEXT_SIZE_1,
    TEXT_SIZE_2,
    TEXT_SIZE_7,
    TEXT_SIZE_8,
    TOPBAR_STYLE,
    responsive,
)

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
            font_size=TEXT_SIZE_1,
            _hover={"cursor": "pointer"},
            on_click=MetricsState.refresh,
        ),
        content=MetricsState.freshness.absolute,
    )


def _logout_button() -> rx.Component:
    return rx.tooltip(
        rx.icon_button(
            rx.hstack(
                rx.text(AUTH["logout_label"]),
                rx.icon("log-out"),
                width="100%",
                align="center",
                justify="center",
            ),
            aria_label=AUTH["logout_label"],
            variant="solid",
            width="7em",
            on_click=AuthState.logout,
            _hover={"cursor": "pointer"},
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
        ),
        content=AUTH["logout_tooltip"],
    )


def topbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.icon("activity", size=16),
                    style=PANEL_ICON_TILE,
                ),
                rx.text(AUTH["brand"], font_size=TEXT_SIZE_2, weight="medium"),
                gap="0.6em",
                align="center",
            ),
            rx.hstack(
                rx.hstack(
                    _freshness_chip(),
                    rejections_button(),
                    gap="0.5em",
                    align="center",
                ),
                rx.cond(
                    AuthState.facility_id != "",
                    rx.badge(
                        rx.hstack(
                            rx.icon("building-2", size=12),
                            rx.text(AuthState.facility_id),
                            gap="0.3em",
                            align="center",
                        ),
                        variant="soft",
                        font_size=TEXT_SIZE_1,
                    ),
                ),
                _logout_button(),
                position="relative",
                gap="3em",
                align="center",
                justify="end",
                flex_wrap="wrap",
            ),
            justify="between",
            align="center",
            width="100%",
            gap="0.75em",
            flex_wrap="wrap",
        ),
        position="sticky",
        top="0",
        z_index="20",
        width="100%",
        style=TOPBAR_STYLE,
        padding_left=responsive("1em", md="1.5em", lg=DESKTOP_PAGE_PADDING_X),
        padding_right="1em",
        padding_y="0.6em",
    )


def hero() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.box(
                    background="var(--accent-9)",
                    border_radius="1em",
                    width="0.4em",
                    height="0.4em",
                ),
                rx.text(
                    DASHBOARD["eyebrow"],
                    font_size=TEXT_SIZE_1,
                    color=TEXT_MUTED,
                    letter_spacing="0.14em",
                    style={"text_transform": "uppercase"},
                ),
                direction="row",
                align="center",
                gap="0.5em",
                border="1px solid var(--gray-a5)",
                border_radius="1em",
                background="var(--gray-a2)",
                padding_x="0.8em",
                padding_y="0.4em",
            ),
            rx.heading(
                DASHBOARD["title"],
                as_="h1",
                font_size=responsive(TEXT_SIZE_7, lg=TEXT_SIZE_8),
                letter_spacing="-0.03em",
                line_height="1.05",
                padding_bottom="0.2em",
                color="var(--gray-12)",
                style={"font_weight": "600"},
            ),
            direction="column",
            align="start",
            gap="1em",
            width="100%",
        ),
        width="100%",
        margin_bottom=responsive("0.5em", lg=DESKTOP_HEADER_GAP),
    )


def header() -> rx.Component:
    return rx.fragment(topbar(), hero())


__all__ = ["header", "hero", "topbar"]

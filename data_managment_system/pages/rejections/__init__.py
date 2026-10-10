"""Rejected-files entry point and dialog for the dashboard top bar."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import REJECTIONS
from data_managment_system.states.rejections import RejectionsState
from data_managment_system.theme import TEXT_SIZE_1, TEXT_SIZE_2, TEXT_SIZE_5


def rejections_button() -> rx.Component:
    """Build the topbar ghost button that opens the dialog."""
    return rx.tooltip(
        rx.button(
            rx.icon("file-x", size=16),
            rx.text(REJECTIONS["button_label_short"]),
            aria_label=REJECTIONS["button_label"],
            variant="outline",
            color_scheme="gray",
            gap="0.4em",
            on_click=RejectionsState.open_dialog,
            _hover={"cursor": "pointer"},
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
        ),
        content=REJECTIONS["button_tooltip"],
    )


def _retry_button() -> rx.Component:
    return rx.tooltip(
        rx.icon_button(
            rx.icon("rotate-ccw", size=16),
            variant="ghost",
            font_size=TEXT_SIZE_1,
            color_scheme="gray",
            aria_label=REJECTIONS["retry"],
            on_click=RejectionsState.refresh,
            _hover={"cursor": "pointer"},
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
        ),
        content=REJECTIONS["retry"],
    )


def _skeleton_rows() -> rx.Component:
    return rx.vstack(
        rx.skeleton(width="100%", height="1em", class_name="dash-shimmer"),
        rx.skeleton(width="100%", height="1em", class_name="dash-shimmer"),
        rx.skeleton(width="100%", height="1em", class_name="dash-shimmer"),
        align="stretch",
        gap="0.75em",
        width="100%",
    )


def _error_block(message: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("circle-alert"),
            rx.text(message),
            _retry_button(),
            gap="0.75em",
            align="center",
        ),
        background="var(--gray-a2)",
        border="1px solid var(--gray-a4)",
        border_radius="0.5em",
        padding="0.75em",
        width="100%",
        box_sizing="border-box",
    )


def _file_icon(kind: Any) -> rx.Component:
    """Same file-type tile used by the upload dialog's file cards."""
    is_csv = kind == "CSV"
    is_xlsx = kind == "XLSX"
    return rx.box(
        rx.icon(
            "file-text",
            size=20,
            color=rx.cond(
                is_csv,
                rx.color("blue", 11),
                rx.cond(is_xlsx, rx.color("tomato", 11), rx.color("gray", 11)),
            ),
        ),
        width="2.5em",
        height="2.5em",
        border_radius="0.625em",
        background=rx.cond(
            is_csv,
            rx.color("blue", 3),
            rx.cond(is_xlsx, rx.color("tomato", 3), rx.color("gray", 3)),
        ),
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


def _rejection_row(row: Any) -> rx.Component:
    is_downloading = RejectionsState.downloading_id == row.file_id
    badge = cast(
        rx.Component,
        rx.match(
            row.state,
            (
                "available",
                rx.badge(
                    REJECTIONS["badge_available"],
                    color_scheme="jade",
                    variant="soft",
                ),
            ),
            (
                "expired",
                rx.badge(
                    REJECTIONS["badge_expired"],
                    color_scheme="gray",
                    variant="soft",
                ),
            ),
            rx.badge(row.state, color_scheme="gray", variant="soft"),
        ),
    )
    download_button = rx.tooltip(
        rx.button(
            rx.icon("download", size=14),
            rx.cond(
                is_downloading,
                rx.text(REJECTIONS["downloading"]),
                rx.text(REJECTIONS["download"]),
            ),
            aria_label=REJECTIONS["download"],
            variant="soft",
            color_scheme="gray",
            font_size=TEXT_SIZE_1,
            loading=is_downloading,
            disabled=(~row.can_download) | is_downloading,
            on_click=RejectionsState.download(row.file_id),
            _hover={"cursor": "pointer"},
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
        ),
        content=REJECTIONS["download"],
    )
    return rx.box(
        rx.flex(
            _file_icon(row.kind),
            rx.vstack(
                rx.text(row.title, font_size=TEXT_SIZE_2, weight="medium"),
                rx.hstack(
                    rx.text(
                        row.created_label,
                        font_size=TEXT_SIZE_1,
                        color=rx.color("gray", 11),
                    ),
                    rx.text(
                        row.expiry_label,
                        font_size=TEXT_SIZE_1,
                        color=rx.color("gray", 11),
                    ),
                    gap="0.5em",
                    flex_wrap="wrap",
                ),
                rx.text(
                    row.rows_label,
                    font_size=TEXT_SIZE_1,
                    color=rx.color("gray", 11),
                ),
                align="start",
                gap="0.25em",
                min_width="0",
                flex="1",
            ),
            rx.hstack(
                badge,
                download_button,
                gap="0.5em",
                align="center",
                flex_wrap="wrap",
            ),
            gap="0.75em",
            align="center",
            justify="between",
            flex_wrap="wrap",
            width="100%",
        ),
        background="var(--gray-a2)",
        border="1px solid var(--gray-a4)",
        border_radius="0.5em",
        padding="0.75em",
        width="100%",
        box_sizing="border-box",
    )


def _ready_list() -> rx.Component:
    return rx.vstack(
        rx.foreach(RejectionsState.rows, _rejection_row),
        align="stretch",
        gap="0.75em",
        width="100%",
    )


def _dialog_body() -> rx.Component:
    return cast(
        rx.Component,
        rx.match(
            RejectionsState.status,
            ("idle", _skeleton_rows()),
            ("loading", _skeleton_rows()),
            ("ready", _ready_list()),
            (
                "empty",
                rx.hstack(
                    rx.icon("info"),
                    rx.text(REJECTIONS["empty"]),
                    gap="0.75em",
                    align="center",
                ),
            ),
            ("503", _error_block(REJECTIONS["unavailable"])),
            ("error", _error_block(REJECTIONS["error"])),
            _skeleton_rows(),
        ),
    )


def _dialog_footer() -> rx.Component:
    return rx.cond(
        RejectionsState.has_more,
        rx.box(
            rx.button(
                rx.icon("chevron-down", size=14),
                REJECTIONS["load_more"],
                variant="soft",
                color_scheme="gray",
                font_size=TEXT_SIZE_2,
                loading=(RejectionsState.status == "loading"),
                disabled=(RejectionsState.status == "loading"),
                on_click=RejectionsState.load_more,
                _hover={"cursor": "pointer"},
                _focus_visible={
                    "outline": "2px solid var(--accent-8)",
                    "outline_offset": "1px",
                },
            ),
            width="100%",
            display="flex",
            justify_content="center",
            padding="0.75em 1.5em",
            border_top=f"1px solid {rx.color('gray', 5)}",
        ),
        rx.fragment(),
    )


def rejections_dialog() -> rx.Component:
    """Build the controlled rejected-files dialog used by the dashboard."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.icon("file-x", size=20, color=rx.color("accent", 11)),
                        rx.dialog.title(
                            REJECTIONS["dialog_title"],
                            font_size=TEXT_SIZE_5,
                            weight="bold",
                            margin="0",
                        ),
                        gap="0.6em",
                        align="center",
                    ),
                    rx.hstack(
                        rx.tooltip(
                            rx.icon_button(
                                rx.icon("refresh-cw"),
                                aria_label=REJECTIONS["refresh_label"],
                                variant="ghost",
                                color_scheme="gray",
                                font_size=TEXT_SIZE_2,
                                on_click=RejectionsState.refresh,
                                _hover={"cursor": "pointer"},
                                _focus_visible={
                                    "outline": "2px solid var(--accent-8)",
                                    "outline_offset": "1px",
                                },
                            ),
                            content=REJECTIONS["refresh_label"],
                        ),
                        rx.dialog.close(
                            rx.icon_button(
                                rx.icon("x"),
                                aria_label=REJECTIONS["close_label"],
                                variant="ghost",
                                color_scheme="gray",
                                font_size=TEXT_SIZE_2,
                                on_click=RejectionsState.close_dialog,
                                _hover={"cursor": "pointer"},
                                _focus_visible={
                                    "outline": "2px solid var(--accent-8)",
                                    "outline_offset": "1px",
                                },
                            )
                        ),
                        gap="1em",
                        align="center",
                        justify="end",
                    ),
                    align="center",
                    justify="between",
                    width="100%",
                    padding="1.5em 1.5em 1.25em",
                    border_bottom=f"1px solid {rx.color('gray', 5)}",
                ),
                rx.box(
                    _dialog_body(),
                    flex="1",
                    min_height="0",
                    overflow_y="auto",
                    width="100%",
                    padding="1.25em 1.5em",
                ),
                _dialog_footer(),
                align="stretch",
                width="100%",
                min_height="0",
                height="100%",
                flex_direction="column",
            ),
            padding="0",
            background="var(--gray-a2)",
            backdrop_filter="blur(1em)",
            style={"-webkit-backdrop-filter": "blur(1em)"},
            border="1px solid var(--gray-a5)",
            border_radius="1em",
            box_shadow="var(--shadow-6)",
            overflow="hidden",
            display="flex",
            flex_direction="column",
            max_width="42em",
            height="min(88vh, 52em)",
            max_height="88vh",
        ),
        open=RejectionsState.is_open,
        on_open_change=RejectionsState.close_dialog,
    )


__all__ = ["rejections_button", "rejections_dialog"]

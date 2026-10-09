"""Responsive out-of-control patient table (console panel)."""

from typing import Any

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.pages.dashboard.components import state_block
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    PANEL_ICON_TILE,
    PANEL_STYLE,
    PATIENT_ROW_MAX_HEIGHT,
    TABLE_CELL_PADDING_Y,
    TEXT_SIZE_1,
    TEXT_SIZE_4,
    responsive,
)

COLUMN_WIDTHS = ("15%", "29%", "11%", "21%", "24%")
PATIENT_PAGE_SIZE = 10

MOBILE_CARD_STYLE = {
    "background": "var(--gray-a2)",
    "border": "1px solid var(--gray-a4)",
    "border_radius": "0.75em",
    "padding": "0.75em",
    "box_sizing": "border-box",
}


def _badges(row: rx.Var) -> rx.Component:
    row_any: Any = row

    def badge(item: rx.Var) -> rx.Component:
        item_any: Any = item
        return rx.badge(
            item_any.label,
            variant="soft",
            font_size=TEXT_SIZE_1,
            color_scheme=item_any.tone,
        )

    return rx.hstack(
        rx.foreach(row_any.badges, badge),
        gap="0.25em",
        flex_wrap="wrap",
    )


def _readings(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.vstack(
        rx.hstack(
            rx.text(COMMON["readings_bp"], color="gray", font_size=TEXT_SIZE_1),
            rx.text(row_any.bp, font_size=TEXT_SIZE_1),
        ),
        rx.hstack(
            rx.text(COMMON["readings_glucose"], color="gray", font_size=TEXT_SIZE_1),
            rx.text(row_any.glucose, font_size=TEXT_SIZE_1),
        ),
        rx.hstack(
            rx.text(COMMON["readings_hba1c"], color="gray", font_size=TEXT_SIZE_1),
            rx.text(row_any.hba1c, font_size=TEXT_SIZE_1),
        ),
        align="start",
        gap="0.1em",
        line_height="1.3",
    )


def _desktop_row(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.table.row(
        rx.table.cell(
            rx.text(
                row_any.name,
                weight="bold",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                custom_attrs={"title": row_any.name},
            ),
            padding_y=TABLE_CELL_PADDING_Y,
            vertical_align="middle",
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(
                    row_any.phone,
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                rx.text(
                    row_any.address,
                    color="gray",
                    font_size=TEXT_SIZE_1,
                    custom_attrs={"title": row_any.address},
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                align="start",
                width="100%",
            ),
            padding_y=TABLE_CELL_PADDING_Y,
            vertical_align="middle",
        ),
        rx.table.cell(
            row_any.last_visit,
            padding_y=TABLE_CELL_PADDING_Y,
            vertical_align="middle",
        ),
        rx.table.cell(
            _readings(row),
            padding_y=TABLE_CELL_PADDING_Y,
            vertical_align="middle",
        ),
        rx.table.cell(
            _badges(row),
            padding_y=TABLE_CELL_PADDING_Y,
            vertical_align="middle",
        ),
        style={
            "height": f"min(var(--patient-row-fill), {PATIENT_ROW_MAX_HEIGHT})",
            "border_bottom": "1px solid var(--gray-a3)",
            "transition": "background 150ms ease",
            "_hover": {"background": "var(--accent-a2)"},
        },
    )


def _mobile_card(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(row_any.name, weight="bold"),
                _badges(row),
                justify="between",
                width="100%",
            ),
            rx.text(row_any.phone),
            rx.text(row_any.address),
            rx.text(row_any.last_visit),
            _readings(row),
            align="stretch",
            gap="0.4em",
        ),
        style=MOBILE_CARD_STYLE,
        width="100%",
    )


def _pager() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("chevron-left", size=15),
            variant="ghost",
            font_size=TEXT_SIZE_1,
            aria_label=COMMON["prev"],
            disabled=MetricsState.patient_page == 0,
            on_click=MetricsState.previous_patient_page,
            border="1px solid var(--gray-a5)",
            border_radius="10em",
            _hover={"cursor": "pointer", "background": "var(--accent-a3)"},
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
        ),
        rx.text(
            MetricsState.patient_range_label,
            flex="1",
            text_align="center",
        ),
        rx.button(
            rx.icon("chevron-right", size=15),
            variant="ghost",
            font_size=TEXT_SIZE_1,
            aria_label=COMMON["next"],
            disabled=MetricsState.patient_page >= MetricsState.patient_page_count - 1,
            on_click=MetricsState.next_patient_page,
            border="1px solid var(--gray-a5)",
            border_radius="10em",
            _hover={"cursor": "pointer", "background": "var(--accent-a3)"},
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
        ),
        justify="between",
        align="center",
        width="100%",
        flex_wrap="wrap",
        gap="0.5em",
        margin_top="auto",
    )


def patient_table() -> rx.Component:
    patient_rows_remaining = (
        MetricsState.patient_total - MetricsState.patient_page * PATIENT_PAGE_SIZE
    )
    headers = [
        DASHBOARD["patient_name"],
        DASHBOARD["patient_phone_address"],
        DASHBOARD["patient_last_visit"],
        DASHBOARD["patient_latest_readings"],
        DASHBOARD["patient_status"],
    ]
    desktop = rx.table.root(
        rx.table.header(
            rx.table.row(
                *[
                    rx.table.column_header_cell(
                        rx.text(
                            item,
                            font_size=TEXT_SIZE_1,
                            color="gray",
                            style={"fontWeight": "600"},
                            text_transform="uppercase",
                            letter_spacing="0.08em",
                        ),
                        width=width,
                        padding_y=TABLE_CELL_PADDING_Y,
                        vertical_align="middle",
                    )
                    for item, width in zip(headers, COLUMN_WIDTHS, strict=True)
                ]
            )
        ),
        rx.table.body(rx.foreach(MetricsState.patient_page_rows, _desktop_row)),
        variant="ghost",
        width="100%",
        style={
            "table_layout": "fixed",
            "height": "100%",
            "& table": {"height": "100%"},
        },
    )
    content = rx.box(
        rx.box(
            desktop,
            display=responsive("none", md="block"),
            flex="1 1 auto",
            style={
                "--patient-row-fill": rx.cond(
                    patient_rows_remaining < PATIENT_PAGE_SIZE,
                    PATIENT_ROW_MAX_HEIGHT,
                    f"calc(100% / {PATIENT_PAGE_SIZE})",
                )
            },
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.foreach(MetricsState.patient_page_rows, _mobile_card),
                gap="0.75em",
                width="100%",
            ),
            display=responsive("block", md="none"),
            width="100%",
        ),
        _pager(),
        rx.cond(
            MetricsState.patient_is_truncated,
            rx.text(MetricsState.patient_truncated_note, color="gray"),
            rx.fragment(),
        ),
        display="flex",
        flex="1",
        flex_direction="column",
        gap="0.75em",
        width="100%",
    )
    body = rx.box(
        rx.match(
            MetricsState.patients_status,
            (
                "loading",
                rx.vstack(
                    rx.skeleton(height="2.25em"),
                    rx.skeleton(height="2.25em"),
                    rx.skeleton(height="2.25em"),
                    rx.skeleton(height="2.25em"),
                    rx.skeleton(height="2.25em"),
                ),
            ),
            ("empty", rx.text(COMMON["no_patients"])),
            (
                "error",
                state_block(
                    "error",
                    COMMON["couldnt_load_card"],
                    MetricsState.retry_patients,
                ),
            ),
            (
                "503",
                state_block(
                    "503",
                    COMMON["metrics_unavailable"],
                    MetricsState.retry_patients,
                ),
            ),
            ("ready", content),
            state_block(
                "error", COMMON["couldnt_load_card"], MetricsState.retry_patients
            ),
        ),
        display="flex",
        flex_direction="column",
        flex="1",
        width="100%",
    )
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon("clipboard-list", size=18),
                style=PANEL_ICON_TILE,
            ),
            rx.heading(DASHBOARD["patient_table_title"], font_size=TEXT_SIZE_4),
            rx.badge(MetricsState.patient_total, variant="surface"),
            align="center",
            gap="0.5em",
            width="100%",
        ),
        rx.box(
            border_bottom="1px solid var(--gray-a5)",
            width="100%",
        ),
        body,
        style=PANEL_STYLE,
        width="100%",
        display="flex",
        flex_direction="column",
        gap="0.75em",
    )


__all__ = ["patient_table"]

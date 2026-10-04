"""Responsive out-of-control patient table."""

from typing import Any

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.pages.dashboard.components import state_block
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    DASHBOARD_CARD_STYLE,
    PATIENT_ROW_MAX_HEIGHT,
    TABLE_CELL_PADDING_Y,
    responsive,
)

COLUMN_WIDTHS = ("15%", "29%", "11%", "21%", "24%")
PATIENT_PAGE_SIZE = 10


def _badges(row: rx.Var) -> rx.Component:
    row_any: Any = row

    def badge(item: rx.Var) -> rx.Component:
        item_any: Any = item
        return rx.badge(
            item_any.label,
            variant="soft",
            size="1",
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
            rx.text(COMMON["readings_bp"], color="gray", size="1"),
            rx.text(row_any.bp, size="1"),
        ),
        rx.hstack(
            rx.text(COMMON["readings_glucose"], color="gray", size="1"),
            rx.text(row_any.glucose, size="1"),
        ),
        rx.hstack(
            rx.text(COMMON["readings_hba1c"], color="gray", size="1"),
            rx.text(row_any.hba1c, size="1"),
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
                    size="1",
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
        style={"height": f"min(var(--patient-row-fill), {PATIENT_ROW_MAX_HEIGHT})"},
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
        style=DASHBOARD_CARD_STYLE,
        width="100%",
    )


def _pager() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("chevron-left", size=15),
            variant="outline",
            size="1",
            aria_label=COMMON["prev"],
            disabled=MetricsState.patient_page == 0,
            on_click=MetricsState.previous_patient_page,
            _hover={"cursor": "pointer"},
        ),
        rx.text(
            MetricsState.patient_range_label,
            flex="1",
            text_align="center",
        ),
        rx.button(
            rx.icon("chevron-right", size=15),
            variant="outline",
            size="1",
            aria_label=COMMON["next"],
            disabled=MetricsState.patient_page >= MetricsState.patient_page_count - 1,
            on_click=MetricsState.next_patient_page,
            _hover={"cursor": "pointer"},
        ),
        justify="between",
        width="100%",
        flex_wrap="wrap",
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
                            size="1",
                            color="gray",
                            style={"fontWeight": "600"},
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
            rx.heading(DASHBOARD["patient_table_title"], size="4"),
            rx.badge(MetricsState.patient_total),
            align="center",
            gap="0.5em",
            width="100%",
        ),
        body,
        style=DASHBOARD_CARD_STYLE,
        width="100%",
        display="flex",
        flex_direction="column",
    )


__all__ = ["patient_table"]

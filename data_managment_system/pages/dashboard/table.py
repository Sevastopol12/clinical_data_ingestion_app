"""Responsive out-of-control patient table."""

from typing import Any

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.pages.dashboard.components import state_block
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import CARD_STYLE


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

    return rx.hstack(rx.foreach(row_any.badges, badge), gap="0.5em", wrap="wrap")


def _readings(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.vstack(
        rx.hstack(rx.text(COMMON["readings_bp"], color="gray"), row_any.bp),
        rx.hstack(rx.text(COMMON["readings_glucose"], color="gray"), row_any.glucose),
        rx.hstack(rx.text(COMMON["readings_hba1c"], color="gray"), row_any.hba1c),
        align="start",
        gap="0.25em",
    )


def _desktop_row(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.table.row(
        rx.table.cell(
            rx.text(row_any.name, weight="bold"), style={"verticalAlign": "middle"}
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(row_any.phone),
                rx.text(row_any.address, color="gray"),
                align="start",
            ),
            style={"verticalAlign": "middle"},
        ),
        rx.table.cell(row_any.last_visit, style={"verticalAlign": "middle"}),
        rx.table.cell(_readings(row)),
        rx.table.cell(_badges(row)),
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
            gap="0.5em",
        ),
        style=CARD_STYLE,
        width="100%",
    )


def _pager() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("chevron-left", size=15),
            variant="outline",
            size="1",
            disabled=MetricsState.patient_page == 0,
            on_click=MetricsState.previous_patient_page,
            _hover={"cursor": "pointer"},
        ),
        rx.text(MetricsState.patient_range_label),
        rx.button(
            rx.icon("chevron-right", size=15),
            variant="outline",
            size="1",
            disabled=MetricsState.patient_page >= MetricsState.patient_page_count - 1,
            on_click=MetricsState.next_patient_page,
            _hover={"cursor": "pointer"},
        ),
        justify="between",
        width="100%",
        flex_wrap="wrap",
    )


def patient_table() -> rx.Component:
    headers = [
        DASHBOARD["patient_name"],
        DASHBOARD["patient_phone_address"],
        DASHBOARD["patient_last_visit"],
        DASHBOARD["patient_latest_readings"],
        DASHBOARD["patient_status"],
    ]
    desktop = rx.table.root(
        rx.table.header(
            rx.table.row(*[rx.table.column_header_cell(item) for item in headers])
        ),
        rx.table.body(rx.foreach(MetricsState.patient_page_rows, _desktop_row)),
        variant="ghost",
        width="100%",
    )
    content = rx.fragment(
        rx.box(desktop, display={"initial": "none", "md": "block"}),
        rx.vstack(
            rx.foreach(MetricsState.patient_page_rows, _mobile_card),
            display={"initial": "flex", "md": "none"},
            width="100%",
        ),
        _pager(),
    )
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(DASHBOARD["patient_table_title"], size="5"),
                rx.badge(MetricsState.patient_total),
                align="center",
                gap="0.5em",
                width="100%",
            ),
            rx.match(
                MetricsState.patients_status,
                (
                    "loading",
                    rx.vstack(
                        rx.skeleton(height="4"),
                        rx.skeleton(height="4"),
                        rx.skeleton(height="4"),
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
            rx.cond(
                MetricsState.patient_is_truncated,
                rx.text(MetricsState.patient_truncated_note, color="gray"),
                rx.fragment(),
            ),
            align="stretch",
            gap="1em",
            width="100%",
        ),
        style=CARD_STYLE,
        width="100%",
    )


__all__ = ["patient_table"]

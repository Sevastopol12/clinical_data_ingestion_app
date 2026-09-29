"""Responsive out-of-control patient table."""

from typing import Any

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import BADGE_TONES


def _badges(row: rx.Var) -> rx.Component:
    row_any: Any = row

    def badge(item: rx.Var) -> rx.Component:
        item_any: Any = item
        return rx.badge(
            item_any.label,
            color=rx.match(
                item_any.tone,
                ("crisis", BADGE_TONES["crisis"]),
                BADGE_TONES["muted"],
            ),
        )

    return rx.hstack(rx.foreach(row_any.badges, badge), spacing="2", wrap="wrap")


def _readings(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.vstack(
        rx.text(row_any.bp),
        rx.text(row_any.glucose),
        rx.text(row_any.hba1c),
        align="start",
        spacing="1",
    )


def _desktop_row(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.table.row(
        rx.table.cell(row_any.name),
        rx.table.cell(rx.vstack(row_any.phone, row_any.address, align="start")),
        rx.table.cell(row_any.last_visit),
        rx.table.cell(_readings(row)),
        rx.table.cell(_badges(row)),
    )


def _mobile_card(row: rx.Var) -> rx.Component:
    row_any: Any = row
    return rx.card(
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
            spacing="2",
        ),
        width="100%",
    )


def _pager() -> rx.Component:
    return rx.hstack(
        rx.button(COMMON["prev"], on_click=MetricsState.previous_patient_page),
        rx.text(MetricsState.patient_range_label),
        rx.button(COMMON["next"], on_click=MetricsState.next_patient_page),
        rx.cond(
            MetricsState.patient_is_truncated,
            rx.text(MetricsState.patient_truncated_note),
            rx.fragment(),
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
        width="100%",
    )
    return rx.card(
        rx.vstack(
            rx.heading(DASHBOARD["patient_table_title"], size="5"),
            rx.cond(
                MetricsState.patient_total == 0,
                rx.text(COMMON["no_patients"]),
                rx.fragment(
                    rx.box(desktop, display={"initial": "none", "md": "block"}),
                    rx.vstack(
                        rx.foreach(MetricsState.patient_page_rows, _mobile_card),
                        display={"initial": "flex", "md": "none"},
                        width="100%",
                    ),
                    _pager(),
                ),
            ),
            align="stretch",
            spacing="4",
            width="100%",
        ),
        width="100%",
    )


__all__ = ["patient_table"]

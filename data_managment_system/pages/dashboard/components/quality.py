"""Data quality card."""

from typing import Any

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.states.auth import AuthState
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    CARD_BODY_GAP,
    DQ_ISSUE_COLUMN_GAP,
    TEXT_MUTED,
    TEXT_SIZE_1,
    TEXT_SIZE_3,
    TEXT_SIZE_4,
    TEXT_SIZE_6,
    responsive,
)
from data_managment_system.utils.view_models import DataQualityVM

from .shell import card_shell
from .states import _card_state


def _dq_tile(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.vstack(
        rx.text(field_any.label, font_size=TEXT_SIZE_1, color=TEXT_MUTED),
        rx.text(
            field_any.value,
            font_size=TEXT_SIZE_6,
            weight="bold",
            font_variant_numeric="tabular-nums",
        ),
        align="start",
        gap="0.2em",
        background="var(--gray-a2)",
        border="1px solid var(--gray-a4)",
        border_radius="0.6em",
        padding="0.75em",
        width="100%",
        box_sizing="border-box",
    )


def _issue_row(item: rx.Var) -> rx.Component:
    item_any: Any = item
    return rx.hstack(
        rx.text(
            item_any.title,
            font_size=TEXT_SIZE_4,
            weight="bold",
            flex="1",
            min_width="0",
        ),
        rx.hstack(
            rx.badge(
                item_any.count,
                color_scheme="gray",
                variant="soft",
                font_size=TEXT_SIZE_3,
            ),
            rx.cond(
                (item_any.field != "")
                & (item_any.field != "text")
                & (item_any.field != "Text"),
                rx.badge(
                    item_any.field,
                    variant="soft",
                    font_size=TEXT_SIZE_3,
                    radius="large",
                    title=item_any.field_hint,
                    font_family=rx.cond(
                        item_any.field == item_any.field_hint,
                        "monospace",
                        "inherit",
                    ),
                ),
                rx.fragment(),
            ),
            align="center",
            wrap="wrap",
            gap="0.4em",
        ),
        align="center",
        justify="between",
        gap="0.75em",
        background="var(--gray-a2)",
        border="1px solid var(--gray-a4)",
        border_radius="0.6em",
        padding="0.75em",
        width="100%",
        flex_wrap="wrap",
        box_sizing="border-box",
    )


def data_quality_card(
    title: str, card_id: str, vm: DataQualityVM, on_retry: rx.EventHandler | None = None
) -> rx.Component:
    expanded = MetricsState.data_quality_expanded

    coverage = rx.box(
        rx.text(
            DASHBOARD["dq_group_coverage"],
            font_size=TEXT_SIZE_1,
            color=TEXT_MUTED,
            text_transform="uppercase",
        ),
        rx.grid(
            rx.foreach(vm.coverage_fields, _dq_tile),
            columns="repeat(2, minmax(0, 1fr))",
            gap=CARD_BODY_GAP,
        ),
        display="flex",
        flex_direction="column",
        gap="0.75em",
    )
    rows = rx.box(
        rx.text(
            DASHBOARD["dq_group_rows"],
            font_size=TEXT_SIZE_1,
            color=TEXT_MUTED,
            text_transform="uppercase",
        ),
        rx.grid(
            rx.foreach(vm.row_fields, _dq_tile),
            columns=rx.breakpoints(initial="2", sm="4"),
            gap=CARD_BODY_GAP,
        ),
        display="flex",
        flex_direction="column",
        gap="0.75em",
    )
    summary = rx.grid(
        rx.box(
            coverage,
            grid_column=responsive("1 / -1", md="span 2"),
            padding_bottom=responsive(CARD_BODY_GAP, md="0"),
            border_bottom=responsive("1px solid var(--gray-a4)", md="0"),
        ),
        rx.box(
            rows,
            grid_column=responsive("1 / -1", md="span 4"),
            border_left=responsive("0", md="1px solid var(--gray-a4)"),
            padding_left=responsive("0", md=CARD_BODY_GAP),
        ),
        columns="repeat(6, minmax(0, 1fr))",
        column_gap=CARD_BODY_GAP,
        row_gap=CARD_BODY_GAP,
        align_items="stretch",
    )

    details = rx.vstack(
        rx.text(COMMON["top_issues"], weight="bold"),
        rx.cond(
            vm.issues,
            rx.grid(
                rx.foreach(vm.issues, _issue_row),
                columns=responsive("1", lg="2"),
                column_gap=responsive(CARD_BODY_GAP, lg=DQ_ISSUE_COLUMN_GAP),
                row_gap=CARD_BODY_GAP,
            ),
            rx.text(COMMON["no_data"]),
        ),
        gap="0.75em",
        align="stretch",
    )

    ready = rx.vstack(
        summary,
        rx.cond(expanded, details, rx.fragment()),
        gap=CARD_BODY_GAP,
        align="stretch",
    )

    toggle_label = rx.cond(expanded, DASHBOARD["dq_less"], DASHBOARD["dq_more"])
    chevron = rx.cond(
        expanded,
        rx.icon("chevron-up", size=14),
        rx.icon("chevron-down", size=14),
    )
    toggle_btn = rx.el.button(
        rx.hstack(
            rx.text(toggle_label, font_size=TEXT_SIZE_1),
            chevron,
            gap="0.25em",
            align="center",
        ),
        type="button",
        height="1.9em",
        padding="0",
        border="1px solid transparent",
        border_radius="0.45em",
        background="transparent",
        appearance="none",
        color="var(--gray-11)",
        font_family="inherit",
        transition="background 150ms ease",
        on_click=MetricsState.toggle_data_quality,
        _hover={"background": "var(--gray-a4)", "cursor": "pointer"},
        _focus_visible={
            "outline": "2px solid var(--accent-8)",
            "outline_offset": "1px",
        },
        aria_label=toggle_label,
    )
    footer_toggle = rx.cond(
        MetricsState.card_status[card_id] == "ready",
        rx.hstack(toggle_btn, padding_x="0.35em", align="center"),
        rx.fragment(),
    )

    facility_badge = rx.cond(
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
        rx.fragment(),
    )

    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, rx.text(COMMON["no_data"]), on_retry),
        footer_start=footer_toggle,
        icon="shield-check",
        header_extra=facility_badge,
    )

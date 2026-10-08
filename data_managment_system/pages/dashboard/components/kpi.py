"""KPI cards for dashboard."""

from typing import Any, Literal

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.theme import (
    BP_STAGE_COLORS,
    CARD_BODY_GAP,
    KPI_MIN_HEIGHT,
    TEXT_MUTED,
)
from data_managment_system.utils.view_models import KpiCardVM

from .shell import card_shell
from .states import _card_state


def _field(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.hstack(
        rx.text(field_any.label),
        rx.text(field_any.value, weight="bold", font_variant_numeric="tabular-nums"),
        justify="between",
        width="100%",
        min_height="2.25em",
        border_bottom="1px solid var(--gray-a3)",
    )


def _stat(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.vstack(
        rx.text(field_any.label, size="1", color="var(--gray-11)"),
        rx.text(
            field_any.value,
            size="5",
            weight="bold",
            font_variant_numeric="tabular-nums",
        ),
        align="start",
    )


def _tile(tile: rx.Var) -> rx.Component:
    tile_any: Any = tile
    border = rx.match(
        tile_any.tone,
        ("normal", f"3px solid {BP_STAGE_COLORS['normal']}"),
        ("elevated", f"3px solid {BP_STAGE_COLORS['elevated']}"),
        ("stage1", f"3px solid {BP_STAGE_COLORS['stage1']}"),
        ("stage2", f"3px solid {BP_STAGE_COLORS['stage2']}"),
        f"3px solid {BP_STAGE_COLORS['severe']}",
    )
    return rx.hstack(
        rx.text(tile_any.label),
        rx.text(tile_any.value, weight="bold", font_variant_numeric="tabular-nums"),
        justify="between",
        width="100%",
        border_left=border,
        padding_left="0.6em",
    )


def _row(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.hstack(
        rx.text(field_any.label, size="2", color=TEXT_MUTED),
        rx.text(
            field_any.value,
            size="3",
            weight="bold",
            font_variant_numeric="tabular-nums",
        ),
        justify="between",
        align="center",
        width="100%",
        min_height="2.25em",
        border_bottom="1px solid var(--gray-a3)",
    )


def _split_stat(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.vstack(
        rx.text(field_any.label, size="1", color=TEXT_MUTED),
        rx.text(
            field_any.value,
            size="5",
            weight="bold",
            font_variant_numeric="tabular-nums",
        ),
        align="start",
    )


def kpi_card(
    title: str,
    card_id: str,
    vm: KpiCardVM,
    stats: int = 0,
    on_retry: rx.EventHandler | None = None,
    layout: Literal["default", "rows", "split"] = "default",
) -> rx.Component:
    if layout == "rows":
        ready = rx.vstack(rx.foreach(vm.fields, _row), gap=CARD_BODY_GAP)
    elif layout == "split":
        ready = rx.grid(
            rx.vstack(rx.foreach(vm.fields, _split_stat), gap=CARD_BODY_GAP),
            rx.vstack(
                rx.text(DASHBOARD["stage_breakdown"], size="1", color=TEXT_MUTED),
                rx.vstack(rx.foreach(vm.tiles, _tile), gap=CARD_BODY_GAP),
                gap=CARD_BODY_GAP,
            ),
            columns=rx.breakpoints(initial="1", sm="2"),
            gap=CARD_BODY_GAP,
        )
    else:
        ready = rx.vstack(
            rx.grid(
                rx.foreach(vm.fields[:stats], _stat),
                columns=f"repeat({max(stats, 1)}, minmax(0, 1fr))",
                gap=CARD_BODY_GAP,
            ),
            rx.foreach(vm.fields[stats:], _field),
            rx.grid(
                rx.foreach(vm.tiles, _tile),
                columns="repeat(2, minmax(0, 1fr))",
                gap=CARD_BODY_GAP,
            ),
            gap=CARD_BODY_GAP,
        )
    empty = rx.vstack(
        rx.text(COMMON["missing"], size="6", weight="bold"),
        rx.text(COMMON["no_visits"]),
    )
    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, empty, on_retry),
        min_height=KPI_MIN_HEIGHT,
    )

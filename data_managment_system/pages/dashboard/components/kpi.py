"""KPI cards for dashboard."""

from typing import Any, Literal

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.theme import (
    BP_STAGE_COLORS,
    CARD_BODY_GAP,
    KPI_MIN_HEIGHT,
    TEXT_MUTED,
    TEXT_SIZE_1,
    TEXT_SIZE_2,
    TEXT_SIZE_3,
    TEXT_SIZE_5,
    TEXT_SIZE_6,
    TEXT_SIZE_8,
)
from data_managment_system.utils.view_models import KpiCardVM

from .gauge import bar, ring_gauge
from .shell import CARD_ICONS, card_shell
from .states import _card_state

_MISSING = COMMON["missing"]


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
        rx.text(field_any.label, font_size=TEXT_SIZE_1, color="var(--gray-11)"),
        rx.text(
            field_any.value,
            font_size=TEXT_SIZE_8,
            weight="bold",
            font_variant_numeric="tabular-nums",
            padding_bottom="0.2em",
            color="var(--gray-12)",
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
    fill: Any = rx.match(
        tile_any.tone,
        ("normal", BP_STAGE_COLORS["normal"]),
        ("elevated", BP_STAGE_COLORS["elevated"]),
        ("stage1", BP_STAGE_COLORS["stage1"]),
        ("stage2", BP_STAGE_COLORS["stage2"]),
        BP_STAGE_COLORS["severe"],
    )
    return rx.vstack(
        rx.hstack(
            rx.text(tile_any.label),
            rx.text(tile_any.value, weight="bold", font_variant_numeric="tabular-nums"),
            justify="between",
            width="100%",
        ),
        rx.cond(
            tile_any.value != _MISSING,
            bar(tile_any.width_pct, fill),
            rx.fragment(),
        ),
        align="stretch",
        gap="0.35em",
        width="100%",
        border_left=border,
        padding_left="0.6em",
    )


def _row(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.hstack(
        rx.text(field_any.label, font_size=TEXT_SIZE_2, color=TEXT_MUTED),
        rx.text(
            field_any.value,
            font_size=TEXT_SIZE_3,
            weight="bold",
            font_variant_numeric="tabular-nums",
        ),
        justify="between",
        align="center",
        width="100%",
        min_height="2.25em",
        border_bottom="1px solid var(--gray-a3)",
    )


def _mix_row(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.vstack(
        rx.hstack(
            rx.text(field_any.label, font_size=TEXT_SIZE_2, color=TEXT_MUTED),
            rx.text(
                field_any.value,
                font_size=TEXT_SIZE_3,
                weight="bold",
                font_variant_numeric="tabular-nums",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        rx.cond(
            field_any.value != _MISSING,
            bar(field_any.pct),
            rx.fragment(),
        ),
        align="stretch",
        gap="0.35em",
        width="100%",
        min_height="2.25em",
        border_bottom="1px solid var(--gray-a3)",
        padding_bottom="0.4em",
    )


def _split_stat(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.hstack(
        rx.cond(
            field_any.value != _MISSING,
            ring_gauge(field_any.pct),
            rx.fragment(),
        ),
        rx.vstack(
            rx.text(field_any.label, font_size=TEXT_SIZE_1, color=TEXT_MUTED),
            rx.text(
                field_any.value,
                font_size=TEXT_SIZE_5,
                weight="bold",
                font_variant_numeric="tabular-nums",
            ),
            align="start",
            gap="0.1em",
        ),
        align="center",
        gap="0.75em",
        width="100%",
    )


def kpi_card(
    title: str,
    card_id: str,
    vm: KpiCardVM,
    stats: int = 0,
    on_retry: rx.EventHandler | None = None,
    layout: Literal["default", "rows", "split"] = "default",
    icon: str | None = None,
) -> rx.Component:
    resolved_icon = icon if icon is not None else CARD_ICONS.get(card_id, "activity")
    if layout == "rows":
        row_fn = _mix_row if card_id == "patient_mix" else _row
        ready = rx.vstack(rx.foreach(vm.fields, row_fn), gap=CARD_BODY_GAP)
    elif layout == "split":
        ready = rx.grid(
            rx.vstack(rx.foreach(vm.fields, _split_stat), gap=CARD_BODY_GAP),
            rx.vstack(
                rx.text(
                    DASHBOARD["stage_breakdown"],
                    font_size=TEXT_SIZE_1,
                    color=TEXT_MUTED,
                ),
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
        rx.text(COMMON["missing"], font_size=TEXT_SIZE_6, weight="bold"),
        rx.text(COMMON["no_visits"]),
    )
    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, empty, on_retry),
        min_height=KPI_MIN_HEIGHT,
        icon=resolved_icon,
    )

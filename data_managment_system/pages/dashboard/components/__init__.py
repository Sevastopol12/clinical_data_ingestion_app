"""Reusable reactive dashboard cards and period controls."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import COMMON
from data_managment_system.states.metrics import VALID_GRAINS, MetricsState
from data_managment_system.theme import CARD_STYLE, SEVERITY_RAMP, TEXT_MUTED
from data_managment_system.utils.view_models import (
    DataQualityVM,
    KpiCardVM,
    RankingCardVM,
)


def period_selector(card_id: str) -> rx.Component:
    def button(grain: str) -> rx.Component:
        selected = MetricsState.grain_by_card[card_id] == grain
        return rx.button(
            grain,
            variant="outline",
            size="1",
            radius="none",
            color_scheme=rx.cond(selected, "violet", "gray"),
            background=rx.cond(selected, "var(--accent-a5)", "transparent"),
            _hover={"background": "var(--accent-a3)", "cursor": "pointer"},
            on_click=MetricsState.set_grain(card_id, grain),
        )

    return rx.hstack(
        *[button(grain) for grain in VALID_GRAINS],
        gap="0.25em",
        flex_shrink="0",
    )


def _retry(on_retry: rx.EventHandler | None) -> rx.Component:
    return rx.tooltip(
        rx.icon_button(
            rx.icon("rotate-ccw", size=16),
            variant="ghost",
            size="1",
            color_scheme="gray",
            aria_label=COMMON["retry"],
            on_click=on_retry,
            _hover={"cursor": "pointer"},
        ),
        content=COMMON["retry"],
    )


def state_block(
    kind: rx.Var[str] | str,
    message: rx.Var[str] | str,
    on_retry: Any,
) -> rx.Component:
    retry = _retry(on_retry)
    return cast(
        rx.Component,
        rx.match(
            kind,
            (
                "loading",
                rx.vstack(
                    rx.skeleton(width="100%", height="1rem"),
                    rx.skeleton(width="100%", height="1rem"),
                    rx.skeleton(width="100%", height="1rem"),
                    align="stretch",
                    gap="0.75em",
                ),
            ),
            (
                "503",
                rx.hstack(
                    rx.icon("triangle-alert"), rx.text(message), retry, gap="0.75em"
                ),
            ),
            (
                "error",
                rx.hstack(
                    rx.icon("circle-alert"), rx.text(message), retry, gap="0.75em"
                ),
            ),
            rx.hstack(rx.icon("info"), rx.text(message), gap="0.75em"),
        ),
    )


def card_shell(
    title: str,
    card_id: str,
    body: rx.Component,
    period_label: rx.Var[str] | str,
    min_height: str = "0em",
) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.hstack(
                rx.text(title, size="3", weight="medium"),
                rx.text(period_label, size="1", color=TEXT_MUTED),
                justify="between",
                align="center",
                width="100%",
                wrap="wrap",
                gap="0.5em",
            ),
            rx.box(body, flex="1", width="100%"),
            rx.hstack(period_selector(card_id), justify="end", width="100%"),
            direction="column",
            gap="1em",
            flex="1",
            width="100%",
        ),
        style=CARD_STYLE,
        display="flex",
        flex_direction="column",
        width="100%",
        min_height=min_height,
    )


def _field(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.hstack(
        rx.text(field_any.label),
        rx.text(field_any.value, weight="bold", font_variant_numeric="tabular-nums"),
        justify="between",
        width="100%",
    )


def _stat(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.vstack(
        rx.text(field_any.label, size="1", color="var(--gray-11)"),
        rx.text(
            field_any.value,
            size="6",
            weight="bold",
            font_variant_numeric="tabular-nums",
        ),
        align="start",
    )


def _tile(tile: rx.Var) -> rx.Component:
    tile_any: Any = tile
    border = rx.match(
        tile_any.tone,
        ("normal", f"3px solid {SEVERITY_RAMP['green']}"),
        ("stage1", f"3px solid {SEVERITY_RAMP['amber']}"),
        ("stage2", f"3px solid {SEVERITY_RAMP['orange']}"),
        f"3px solid {SEVERITY_RAMP['red']}",
    )
    return rx.vstack(
        rx.text(tile_any.label),
        rx.text(tile_any.value, weight="bold", font_variant_numeric="tabular-nums"),
        align="start",
        border_left=border,
        padding_left="0.75em",
    )


def _card_state(
    card_id: str,
    ready: rx.Component,
    empty: rx.Component,
    on_retry: rx.EventHandler | None,
) -> rx.Component:
    retry = on_retry or MetricsState.retry(card_id)
    status = MetricsState.card_status[card_id]
    return cast(
        rx.Component,
        rx.match(
            status,
            ("loading", state_block(status, COMMON["loading"], retry)),
            ("empty", empty),
            ("503", state_block(status, COMMON["metrics_unavailable"], retry)),
            ("error", state_block(status, COMMON["couldnt_load_card"], retry)),
            ready,
        ),
    )


def kpi_card(
    title: str,
    card_id: str,
    vm: KpiCardVM,
    stats: int = 0,
    on_retry: rx.EventHandler | None = None,
) -> rx.Component:
    ready = rx.vstack(
        rx.grid(
            rx.foreach(vm.fields[:stats], _stat),
            columns=f"repeat({max(stats, 1)}, minmax(0, 1fr))",
            gap="1em",
        ),
        rx.foreach(vm.fields[stats:], _field),
        rx.grid(
            rx.foreach(vm.tiles, _tile),
            columns="repeat(2, minmax(0, 1fr))",
            gap="0.75em",
        ),
        gap="0.75em",
    )
    empty = rx.vstack(
        rx.text(COMMON["missing"], size="6", weight="bold"),
        rx.text(vm.empty_note),
    )
    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, empty, on_retry),
        vm.period_label,
        min_height="13em",
    )


def ranking_card(
    title: str, card_id: str, vm: RankingCardVM, on_retry: rx.EventHandler | None = None
) -> rx.Component:
    def row(item: rx.Var) -> rx.Component:
        item_any: Any = item
        return rx.vstack(
            rx.hstack(
                rx.text(item_any.label),
                rx.text(item_any.value, font_variant_numeric="tabular-nums"),
                justify="between",
                width="100%",
            ),
            rx.box(
                rx.box(
                    width=item_any.width_pct.to_string() + "%",
                    height="100%",
                    background="var(--accent-9)",
                    border_radius="999em",
                ),
                width="100%",
                height="0.4em",
                background="var(--gray-a4)",
                border_radius="999em",
            ),
            width="100%",
            align="stretch",
            gap="0.5em",
        )

    ready = rx.scroll_area(
        rx.vstack(rx.foreach(vm.rows, row), gap="0.75em"), max_height="20em"
    )
    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, rx.text(COMMON["no_data"]), on_retry),
        vm.period_label,
    )


def data_quality_card(
    title: str, card_id: str, vm: DataQualityVM, on_retry: rx.EventHandler | None = None
) -> rx.Component:
    def issue(item: rx.Var) -> rx.Component:
        item_any: Any = item
        return rx.hstack(
            rx.text(item_any.label),
            rx.text(item_any.count, weight="bold", font_variant_numeric="tabular-nums"),
            justify="between",
        )

    ready = rx.vstack(
        rx.text(vm.period_label, size="1", color="var(--gray-11)"),
        rx.grid(
            rx.foreach(vm.fields, _field),
            columns=cast(Any, {"initial": "2", "md": "3"}),
            gap="0.75em",
        ),
        rx.grid(
            rx.vstack(
                rx.text(COMMON["top_issues"], weight="bold"),
                rx.foreach(vm.issues, issue),
                gap="0.5em",
            ),
            columns=cast(Any, {"initial": "1", "lg": "2"}),
            gap="1em",
        ),
        gap="0.75em",
    )
    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, rx.text(COMMON["no_data"]), on_retry),
        vm.period_label,
    )


__all__ = [
    "card_shell",
    "data_quality_card",
    "kpi_card",
    "period_selector",
    "ranking_card",
    "state_block",
]

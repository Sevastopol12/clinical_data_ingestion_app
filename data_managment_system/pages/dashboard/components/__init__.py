"""Reusable reactive dashboard cards and period controls."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import COMMON
from data_managment_system.states.metrics import VALID_GRAINS, MetricsState
from data_managment_system.theme import SEVERITY_RAMP
from data_managment_system.utils.view_models import (
    DataQualityVM,
    KpiCardVM,
    RankingCardVM,
)


def period_selector(card_id: str) -> rx.Component:
    buttons = [
        rx.button(
            grain,
            variant=rx.cond(
                MetricsState.grain_by_card[card_id] == grain, "solid", "ghost"
            ),
            on_click=MetricsState.set_grain(card_id, grain),
            _hover={"opacity": "0.85"},
        )
        for grain in VALID_GRAINS
    ]
    return rx.fragment(
        rx.hstack(*buttons, spacing="2", display={"initial": "none", "md": "flex"}),
        rx.select(
            list(VALID_GRAINS),
            value=MetricsState.grain_by_card[card_id],
            on_change=lambda grain: MetricsState.set_grain(card_id, grain),
            display={"initial": "flex", "md": "none"},
        ),
    )


def _retry(on_retry: rx.EventHandler | None) -> rx.Component:
    return rx.button(COMMON["retry"], variant="ghost", on_click=on_retry)


def _card_states(
    status: rx.Var[str] | str,
    ready: rx.Component,
    empty: rx.Component,
    on_retry: rx.EventHandler | None,
) -> rx.Component:
    return cast(
        rx.Component,
        rx.match(
            status,
            ("loading", rx.skeleton(width="100%", height="4rem")),
            ("empty", empty),
            (
                "503",
                rx.vstack(
                    rx.text(COMMON["metrics_unavailable"]),
                    _retry(on_retry),
                    spacing="3",
                ),
            ),
            (
                "error",
                rx.vstack(
                    rx.text(COMMON["couldnt_load_card"]), _retry(on_retry), spacing="3"
                ),
            ),
            ready,
        ),
    )


def _field(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.hstack(
        rx.text(field_any.label),
        rx.text(field_any.value, weight="bold"),
        justify="between",
    )


def _tile(tile: rx.Var) -> rx.Component:
    tile_any: Any = tile
    tone = rx.match(
        tile_any.tone,
        ("normal", SEVERITY_RAMP["green"]),
        ("stage1", SEVERITY_RAMP["amber"]),
        ("stage2", SEVERITY_RAMP["orange"]),
        SEVERITY_RAMP["red"],
    )
    return rx.vstack(
        rx.text(tile_any.label),
        rx.text(tile_any.value, weight="bold"),
        color=tone,
        align="start",
    )


def _card_frame(title: str, card_id: str, body: rx.Component) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(title, weight="bold"),
                period_selector(card_id),
                justify="between",
                width="100%",
            ),
            body,
            align="stretch",
            spacing="4",
            width="100%",
        ),
        width="100%",
    )


def kpi_card(
    title: str, card_id: str, vm: KpiCardVM, on_retry: rx.EventHandler | None = None
) -> rx.Component:
    ready = rx.vstack(
        rx.text(vm.period_label, size="1"),
        rx.foreach(vm.fields, _field),
        rx.grid(
            rx.foreach(vm.tiles, _tile), columns="repeat(2, minmax(0, 1fr))", gap="3"
        ),
        spacing="3",
    )
    empty = rx.vstack(
        rx.text(COMMON["missing"], size="6", weight="bold"), rx.text(vm.empty_note)
    )
    return _card_frame(
        title,
        card_id,
        _card_states(MetricsState.card_status[card_id], ready, empty, on_retry),
    )


def ranking_card(
    title: str, card_id: str, vm: RankingCardVM, on_retry: rx.EventHandler | None = None
) -> rx.Component:
    def row(item: rx.Var) -> rx.Component:
        item_any: Any = item
        return rx.vstack(
            rx.hstack(
                rx.text(item_any.label), rx.text(item_any.value), justify="between"
            ),
            rx.box(
                width=item_any.width_pct.to_string() + "%",
                height="0.4rem",
                bg="var(--accent-9)",
            ),
            width="100%",
            align="stretch",
        )

    ready = rx.vstack(
        rx.text(vm.period_label, size="1"),
        rx.scroll_area(rx.foreach(vm.rows, row), max_height="18rem"),
        spacing="3",
    )
    return _card_frame(
        title,
        card_id,
        _card_states(
            MetricsState.card_status[card_id],
            ready,
            rx.text(COMMON["no_data"]),
            on_retry,
        ),
    )


def data_quality_card(
    title: str, card_id: str, vm: DataQualityVM, on_retry: rx.EventHandler | None = None
) -> rx.Component:
    def issue(item: rx.Var) -> rx.Component:
        item_any: Any = item
        return rx.hstack(
            rx.text(item_any.label),
            rx.text(item_any.count, weight="bold"),
            justify="between",
        )

    ready = rx.vstack(
        rx.text(vm.period_label, size="1"),
        rx.foreach(vm.fields, _field),
        rx.foreach(vm.issues, issue),
        spacing="3",
    )
    return _card_frame(
        title,
        card_id,
        _card_states(
            MetricsState.card_status[card_id],
            ready,
            rx.text(COMMON["no_data"]),
            on_retry,
        ),
    )


__all__ = ["data_quality_card", "kpi_card", "period_selector", "ranking_card"]

"""Reusable reactive dashboard cards and period controls."""

from typing import Any, Literal, cast

import reflex as rx

from data_managment_system.copy import (
    COMMON,
    DASHBOARD,
    PERIOD_CHIP_LABELS,
    PERIOD_LABELS,
)
from data_managment_system.states.metrics import VALID_GRAINS, MetricsState
from data_managment_system.theme import (
    BP_STAGE_COLORS,
    CARD_BODY_GAP,
    DASHBOARD_CARD_STYLE,
    DQ_ISSUE_COLUMN_GAP,
    FLOAT_SHADOW,
    FLOAT_SHADOW_SELECTED,
    KPI_MIN_HEIGHT,
    PERIOD_IDLE_BG,
    PERIOD_SELECTED_BG,
    RANKING_MAX_HEIGHT,
    TEXT_MUTED,
    responsive,
)
from data_managment_system.utils.view_models import (
    DataQualityVM,
    KpiCardVM,
    RankingCardVM,
)


def period_selector(card_id: str) -> rx.Component:
    def chip(grain: str) -> rx.Component:
        selected = MetricsState.grain_by_card[card_id] == grain
        return rx.el.button(
            rx.text(
                PERIOD_CHIP_LABELS[grain],
                size="1",
                weight="medium",
                line_height="1",
                font_variant_numeric="tabular-nums",
            ),
            type="button",
            min_width="2.4em",
            height="1.9em",
            padding_x="0.55em",
            display="inline-flex",
            align_items="center",
            justify_content="center",
            border_radius="0.45em",
            appearance="none",
            font_family="inherit",
            cursor="pointer",
            flex_shrink="0",
            background=rx.cond(selected, PERIOD_SELECTED_BG, PERIOD_IDLE_BG),
            border="1px solid transparent",
            border_color=rx.cond(selected, "var(--accent-a8)", "transparent"),
            color=rx.cond(selected, "var(--accent-11)", "var(--gray-11)"),
            box_shadow=rx.cond(selected, FLOAT_SHADOW_SELECTED, FLOAT_SHADOW),
            transform=rx.cond(selected, "translateY(-1px)", "none"),
            transition="all 150ms ease",
            _hover={
                "background": "var(--gray-a5)",
                "border_color": "var(--gray-a7)",
                "color": "var(--gray-12)",
                "cursor": "pointer",
            },
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
            aria_label=DASHBOARD["period_aria"].format(label=PERIOD_LABELS[grain]),
            custom_attrs={"aria-pressed": selected},
            on_click=MetricsState.set_grain(card_id, grain),
        )

    chips = [chip(grain) for grain in VALID_GRAINS]
    return rx.hstack(
        *chips,
        gap="0.3em",
        flex_wrap="wrap",
        flex_shrink="0",
        margin_left="auto",
        custom_attrs={"role": "group", "aria-label": DASHBOARD["period_group"]},
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
                    rx.skeleton(width="100%", height="1em"),
                    rx.skeleton(width="100%", height="1em"),
                    rx.skeleton(width="100%", height="1em"),
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
    min_height: str = "0em",
    footer_start: rx.Component | None = None,
    period_note: str | None = None,
) -> rx.Component:
    period_label = rx.match(
        MetricsState.grain_by_card[card_id],
        *((grain, label) for grain, label in PERIOD_LABELS.items()),
        PERIOD_LABELS["TODAY"],
    )
    header_period = rx.hstack(
        rx.text(period_label, size="1", color=TEXT_MUTED),
        rx.cond(
            period_note is not None,
            rx.text(f" Â· {period_note}", size="1", color=TEXT_MUTED),
            rx.fragment(),
        ),
        gap="0em",
        align="center",
    )
    footer = rx.hstack(
        footer_start if footer_start is not None else rx.box(),
        rx.box(period_selector(card_id), margin_left="auto"),
        align="center",
        width="100%",
    )
    return rx.box(
        rx.flex(
            rx.hstack(
                rx.text(title, size="3", weight="bold"),
                header_period,
                justify="between",
                align="center",
                width="100%",
                wrap="wrap",
                gap="0.5em",
            ),
            rx.box(body, flex="1", width="100%"),
            footer,
            direction="column",
            gap=CARD_BODY_GAP,
            flex="1",
            width="100%",
        ),
        style=DASHBOARD_CARD_STYLE,
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


def ranking_card(
    title: str,
    card_id: str,
    vm: RankingCardVM,
    on_retry: rx.EventHandler | None = None,
    period_note: str = DASHBOARD["latest_period_note"],
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
                height="0.3em",
                background="var(--gray-a4)",
                border_radius="999em",
            ),
            width="100%",
            align="stretch",
            gap="0.35em",
        )

    ready = rx.scroll_area(
        rx.vstack(rx.foreach(vm.rows, row), gap="0.55em"), max_height=RANKING_MAX_HEIGHT
    )
    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, rx.text(COMMON["no_data"]), on_retry),
        period_note=period_note,
    )


def _dq_tile(field: rx.Var) -> rx.Component:
    field_any: Any = field
    return rx.vstack(
        rx.text(field_any.label, size="1", color=TEXT_MUTED),
        rx.text(
            field_any.value,
            size="6",
            weight="bold",
            font_variant_numeric="tabular-nums",
        ),
        align="start",
        gap="0.2em",
    )


def _issue_row(item: rx.Var) -> rx.Component:
    item_any: Any = item
    return rx.vstack(
        rx.hstack(
            rx.hstack(
                rx.text(item_any.title, weight="medium", size="2"),
                rx.cond(
                    item_any.field != "",
                    rx.badge(
                        item_any.field,
                        variant="soft",
                        size="1",
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
                align="start",
                wrap="wrap",
                gap="0.4em",
                min_width="0",
                flex="1",
            ),
            rx.text(
                item_any.count,
                weight="bold",
                font_variant_numeric="tabular-nums",
                flex_shrink="0",
            ),
            justify="between",
            align="start",
            width="100%",
            column_gap="1em",
        ),
        rx.box(
            rx.box(
                width=item_any.width_pct.to_string() + "%",
                height="100%",
                background="var(--accent-9)",
                border_radius="999em",
            ),
            width="100%",
            height="0.3em",
            background="var(--gray-a4)",
            border_radius="999em",
        ),
        align="stretch",
        gap="0.35em",
    )


def data_quality_card(
    title: str, card_id: str, vm: DataQualityVM, on_retry: rx.EventHandler | None = None
) -> rx.Component:
    expanded = MetricsState.data_quality_expanded

    coverage = rx.box(
        rx.text(
            DASHBOARD["dq_group_coverage"],
            size="1",
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
            size="1",
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
            rx.text(toggle_label, size="1"),
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

    return card_shell(
        title,
        card_id,
        _card_state(card_id, ready, rx.text(COMMON["no_data"]), on_retry),
        footer_start=footer_toggle,
    )


__all__ = [
    "card_shell",
    "data_quality_card",
    "kpi_card",
    "period_selector",
    "ranking_card",
    "state_block",
]

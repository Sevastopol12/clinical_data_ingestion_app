"""Shared card shell for dashboard cards."""

import reflex as rx

from data_managment_system.copy import PERIOD_LABELS
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    CARD_BODY_GAP,
    PANEL_ICON_TILE,
    PANEL_STYLE,
    TEXT_MUTED,
    TEXT_SIZE_1,
    TEXT_SIZE_3,
)

from .period import period_selector

CARD_ICONS = {
    "visits": "users",
    "patient_mix": "pie-chart",
    "clinical_control": "heart-pulse",
    "glucose_hba1c": "droplet",
    "comorbidity": "layers",
    "data_quality": "shield-check",
}


def _tick(position: str) -> rx.Component:
    if position == "top-left":
        return rx.box(
            class_name="dash-tick",
            aria_hidden="true",
            position="absolute",
            width="0.6em",
            height="0.6em",
            top="0.35em",
            left="0.35em",
            border_top="1px solid var(--accent-a7)",
            border_left="1px solid var(--accent-a7)",
            pointer_events="none",
        )
    if position == "top-right":
        return rx.box(
            class_name="dash-tick",
            aria_hidden="true",
            position="absolute",
            width="0.6em",
            height="0.6em",
            top="0.35em",
            right="0.35em",
            border_top="1px solid var(--accent-a7)",
            border_right="1px solid var(--accent-a7)",
            pointer_events="none",
        )
    if position == "bottom-left":
        return rx.box(
            class_name="dash-tick",
            aria_hidden="true",
            position="absolute",
            width="0.6em",
            height="0.6em",
            bottom="0.35em",
            left="0.35em",
            border_bottom="1px solid var(--accent-a7)",
            border_left="1px solid var(--accent-a7)",
            pointer_events="none",
        )
    return rx.box(
        class_name="dash-tick",
        aria_hidden="true",
        position="absolute",
        width="0.6em",
        height="0.6em",
        bottom="0.35em",
        right="0.35em",
        border_bottom="1px solid var(--accent-a7)",
        border_right="1px solid var(--accent-a7)",
        pointer_events="none",
    )


def card_shell(
    title: str,
    card_id: str,
    body: rx.Component,
    min_height: str = "0em",
    footer_start: rx.Component | None = None,
    period_note: str | None = None,
    icon: str = "activity",
) -> rx.Component:
    period_label = rx.match(
        MetricsState.grain_by_card[card_id],
        *((grain, label) for grain, label in PERIOD_LABELS.items()),
        PERIOD_LABELS["TODAY"],
    )
    header_period = rx.hstack(
        rx.text(period_label, font_size=TEXT_SIZE_1, color=TEXT_MUTED),
        rx.cond(
            period_note is not None,
            rx.text(f" · {period_note}", font_size=TEXT_SIZE_1, color=TEXT_MUTED),
            rx.fragment(),
        ),
        gap="0em",
        align="center",
    )
    header = rx.hstack(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=16),
                style=PANEL_ICON_TILE,
            ),
            rx.text(title, font_size=TEXT_SIZE_3, weight="bold"),
            gap="0.6em",
            align="center",
            min_width="0",
        ),
        header_period,
        justify="between",
        align="center",
        width="100%",
        wrap="wrap",
        gap="0.5em",
    )
    divider = rx.box(
        border_bottom="1px solid var(--gray-a4)",
        width="100%",
    )
    footer = rx.hstack(
        footer_start if footer_start is not None else rx.box(),
        rx.box(period_selector(card_id), margin_left="auto"),
        align="center",
        width="100%",
        flex_wrap="wrap",
        gap="0.5em",
    )
    content = rx.flex(
        header,
        divider,
        rx.box(body, flex="1", width="100%"),
        footer,
        direction="column",
        gap=CARD_BODY_GAP,
        flex="1",
        width="100%",
        position="relative",
        z_index="1",
    )
    decorations: list[rx.Component] = []
    decorations.append(_tick("top-left"))
    decorations.append(_tick("top-right"))
    decorations.append(_tick("bottom-left"))
    decorations.append(_tick("bottom-right"))
    style = dict(PANEL_STYLE)
    return rx.box(
        *decorations,
        content,
        style=style,
        class_name="dash-panel dash-rise",
        display="flex",
        flex_direction="column",
        width="100%",
        min_height=min_height,
    )

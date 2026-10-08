"""Shared card shell for dashboard cards."""

import reflex as rx

from data_managment_system.copy import PERIOD_LABELS
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    CARD_BODY_GAP,
    DASHBOARD_CARD_STYLE,
    TEXT_MUTED,
)

from .period import period_selector


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
            rx.text(f" · {period_note}", size="1", color=TEXT_MUTED),
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

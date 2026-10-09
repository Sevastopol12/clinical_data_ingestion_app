"""Loading / empty / error states for dashboard cards."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import COMMON
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import TEXT_SIZE_1


def _retry(on_retry: rx.EventHandler | None) -> rx.Component:
    return rx.tooltip(
        rx.icon_button(
            rx.icon("rotate-ccw", size=16),
            variant="ghost",
            font_size=TEXT_SIZE_1,
            color_scheme="gray",
            aria_label=COMMON["retry"],
            on_click=on_retry,
            _hover={"cursor": "pointer"},
            _focus_visible={
                "outline": "2px solid var(--accent-8)",
                "outline_offset": "1px",
            },
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
                    rx.skeleton(width="100%", height="1em", class_name="dash-shimmer"),
                    rx.skeleton(width="100%", height="1em", class_name="dash-shimmer"),
                    rx.skeleton(width="100%", height="1em", class_name="dash-shimmer"),
                    align="stretch",
                    gap="0.75em",
                    width="100%",
                ),
            ),
            (
                "503",
                rx.box(
                    rx.hstack(
                        rx.icon("triangle-alert"),
                        rx.text(message),
                        retry,
                        gap="0.75em",
                        align="center",
                    ),
                    background="var(--gray-a2)",
                    border="1px solid var(--gray-a4)",
                    border_radius="0.5em",
                    padding="0.75em",
                    width="100%",
                    box_sizing="border-box",
                ),
            ),
            (
                "error",
                rx.box(
                    rx.hstack(
                        rx.icon("circle-alert"),
                        rx.text(message),
                        retry,
                        gap="0.75em",
                        align="center",
                    ),
                    background="var(--gray-a2)",
                    border="1px solid var(--gray-a4)",
                    border_radius="0.5em",
                    padding="0.75em",
                    width="100%",
                    box_sizing="border-box",
                ),
            ),
            rx.hstack(rx.icon("info"), rx.text(message), gap="0.75em"),
        ),
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

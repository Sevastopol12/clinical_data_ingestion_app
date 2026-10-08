"""Period selector chips for dashboard cards."""

import reflex as rx

from data_managment_system.copy import DASHBOARD, PERIOD_CHIP_LABELS
from data_managment_system.states.metrics import VALID_GRAINS, MetricsState
from data_managment_system.theme import (
    FLOAT_SHADOW,
    FLOAT_SHADOW_SELECTED,
    PERIOD_IDLE_BG,
    PERIOD_SELECTED_BG,
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
            aria_label=DASHBOARD["period_aria"].format(label=grain),
            custom_attrs={"aria-pressed": selected},
            on_click=MetricsState.set_grain(card_id, grain),
        )

    chips = [chip(grain) for grain in VALID_GRAINS]
    return rx.hstack(
        *chips,
        gap="0.3em",
        flex_wrap="nowrap",
        flex_shrink="0",
        margin_left="auto",
        custom_attrs={"role": "group", "aria-label": DASHBOARD["period_group"]},
    )

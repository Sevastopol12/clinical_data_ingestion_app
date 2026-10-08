"""Comorbidity ranking card."""

from typing import Any

import reflex as rx

from data_managment_system.copy import COMMON, DASHBOARD
from data_managment_system.theme import RANKING_MAX_HEIGHT
from data_managment_system.utils.view_models import RankingCardVM

from .shell import card_shell
from .states import _card_state


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

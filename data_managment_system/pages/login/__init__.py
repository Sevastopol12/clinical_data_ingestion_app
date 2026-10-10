"""Login page (username + password, no signup links)."""

import reflex as rx

from data_managment_system.pages.login.backdrop import login_backdrop
from data_managment_system.pages.login.components import (
    CARD_FOOTER_GAP,
    brand_bar,
    footer_note,
    hero_scrim,
    login_card,
)
from data_managment_system.pages.login.instruments import login_instruments
from data_managment_system.states.auth import AuthState
from data_managment_system.theme import PAGE_BACKGROUND


@rx.page(route="/login", on_load=AuthState.redirect_if_authenticated)
def index() -> rx.Component:
    return rx.box(
        login_backdrop(),
        login_instruments(),
        hero_scrim(),
        brand_bar(),
        rx.flex(
            login_card(),
            footer_note(),
            direction="column",
            align="center",
            justify="center",
            gap=CARD_FOOTER_GAP,
            width="100%",
            max_width="36em",
            padding_x="1.25em",
            padding_y="1em",
            margin_x="auto",
            flex="1",
            position="relative",
            z_index="2",
        ),
        display="flex",
        flex_direction="column",
        position="relative",
        min_height="100vh",
        style={"minHeight": "100dvh"},
        background=PAGE_BACKGROUND,
        overflow_x="hidden",
        width="100%",
    )


__all__ = ["index"]

"""Login page (username + password, no signup links)."""

import reflex as rx

from data_managment_system.pages.login.backdrop import login_left_panel
from data_managment_system.pages.login.components import (
    login_loading_overlay,
    login_right_panel,
)
from data_managment_system.states.auth import AuthState
from data_managment_system.theme import PAGE_BACKGROUND, responsive


@rx.page(route="/login", on_load=AuthState.redirect_if_authenticated)
def index() -> rx.Component:
    return rx.flex(
        rx.box(
            login_left_panel(),
            # Let the panel's own 45% width participate directly in the row.
            display=responsive("none", lg="contents"),
        ),
        rx.box(
            login_right_panel(),
            display="flex",
            align_items="center",
            justify_content="center",
            flex="1",
            min_width="0",
        ),
        login_loading_overlay(),
        direction=responsive("column", lg="row"),
        align="stretch",
        width="100%",
        min_height="100vh",
        style={"minHeight": "100dvh"},
        position="relative",
        background=PAGE_BACKGROUND,
        overflow_x="hidden",
    )


__all__ = ["index"]

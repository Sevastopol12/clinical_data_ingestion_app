"""Route gate: hide protected UI until the session is known."""

import reflex as rx

from data_managment_system.copy import AUTH
from data_managment_system.states.auth import AuthState


def gated(content: rx.Component) -> rx.Component:
    """Show `content` only when authenticated, else a loading indicator."""
    loading = rx.box(
        rx.hstack(
            rx.spinner(),
            rx.text(AUTH["loading"]),
            gap="0.5em",
            align="center",
            justify="center",
        ),
        width="100%",
        min_height="20em",
        padding="2em",
        display="flex",
        align_items="center",
        justify_content="center",
    )
    return rx.cond(AuthState.is_authenticated, content, loading)


__all__ = ["gated"]

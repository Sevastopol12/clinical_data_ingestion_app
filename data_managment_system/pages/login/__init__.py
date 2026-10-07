"""Login page (username + password, no signup links)."""

from typing import cast

import reflex as rx

from data_managment_system.copy import AUTH
from data_managment_system.states.auth import AuthState
from data_managment_system.theme import CARD_STYLE, PAGE_GLOW

_RATE_PREFIX, _RATE_SUFFIX = AUTH["err_rate_limited"].split("{seconds}")


def _login_error() -> rx.Component:
    return cast(
        rx.Component,
        rx.match(
            AuthState.login_error,
            (
                "invalid",
                rx.callout(
                    AUTH["err_invalid"],
                    icon="triangle-alert",
                    color_scheme="red",
                ),
            ),
            (
                "rate_limited",
                rx.callout(
                    rx.text(_RATE_PREFIX, AuthState.retry_after, _RATE_SUFFIX),
                    icon="triangle-alert",
                    color_scheme="red",
                ),
            ),
            (
                "unavailable",
                rx.callout(
                    AUTH["err_unavailable"],
                    icon="triangle-alert",
                    color_scheme="red",
                ),
            ),
            (
                "expired",
                rx.callout(
                    AUTH["err_expired"],
                    icon="triangle-alert",
                    color_scheme="red",
                ),
            ),
            rx.fragment(),
        ),
    )


@rx.page(route="/login", on_load=AuthState.redirect_if_authenticated)
def index() -> rx.Component:
    return rx.box(
        rx.box(
            rx.vstack(
                rx.heading(AUTH["title"], size="6"),
                _login_error(),
                rx.form(
                    rx.vstack(
                        rx.vstack(
                            rx.text(AUTH["username_label"], size="2", weight="medium"),
                            rx.input(
                                name="username",
                                custom_attrs={"autocomplete": "username"},
                                width="100%",
                            ),
                            gap="0.25em",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text(AUTH["password_label"], size="2", weight="medium"),
                            rx.input(
                                name="password",
                                type="password",
                                custom_attrs={"autocomplete": "current-password"},
                                width="100%",
                            ),
                            gap="0.25em",
                            width="100%",
                        ),
                        rx.button(
                            rx.cond(
                                AuthState.is_logging_in,
                                AUTH["signing_in"],
                                AUTH["sign_in"],
                            ),
                            type="submit",
                            disabled=AuthState.is_logging_in,
                            width="100%",
                            _hover={"cursor": "pointer"},
                        ),
                        gap="0.75em",
                        width="100%",
                    ),
                    on_submit=AuthState.login,
                    reset_on_submit=False,
                    width="100%",
                ),
                gap="1em",
                width="100%",
            ),
            style=CARD_STYLE,
            width="100%",
            max_width="26em",
        ),
        width="100%",
        min_height="100vh",
        padding="1em",
        display="flex",
        align_items="center",
        justify_content="center",
        background=PAGE_GLOW,
    )


__all__ = ["index"]

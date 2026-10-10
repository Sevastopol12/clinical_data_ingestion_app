"""Login right-panel components (brand, card form, fields, CTA)."""

from typing import Literal, cast

import reflex as rx

from data_managment_system.copy import AUTH
from data_managment_system.states.auth import AuthState
from data_managment_system.states.login_ui import LoginUiState
from data_managment_system.theme import (
    LOGIN_BUTTON_MIN_HEIGHT,
    LOGIN_TITLE_SIZE,
    TEXT_MUTED,
    TEXT_SIZE_1,
    TEXT_SIZE_2,
    TEXT_SIZE_3,
    responsive,
)

_RATE_PREFIX, _RATE_SUFFIX = AUTH["err_rate_limited"].split("{seconds}")

CARD_PADDING_MOBILE = "3.5em"
CARD_PADDING_DESKTOP = "4em"
RIGHT_PANEL_MAX_WIDTH = "30em"
RIGHT_PANEL_GAP = "1.5em"
BRAND_MARK_GAP = "0.6em"
CARD_TITLE_GAP = "2em"
LABEL_GAP = "0.5em"
FIELD_GAP = "1.75em"
FORM_BUTTON_GAP = "2.25em"
CALLOUT_GAP = "1.25em"


def _callout(*children: object) -> rx.Component:
    """Red alert callout shared by all login error states."""
    return rx.callout(
        *children,
        icon="triangle-alert",
        color_scheme="red",
        custom_attrs={"role": "alert"},
    )


def error_callout() -> rx.Component:
    """Login error callouts with unchanged semantics."""
    return cast(
        rx.Component,
        rx.match(
            AuthState.login_error,
            ("invalid", _callout(AUTH["err_invalid"])),
            (
                "rate_limited",
                _callout(rx.text(_RATE_PREFIX, AuthState.retry_after, _RATE_SUFFIX)),
            ),
            ("unavailable", _callout(AUTH["err_unavailable"])),
            ("expired", _callout(AUTH["err_expired"])),
            rx.fragment(),
        ),
    )


def _password_toggle() -> rx.Component:
    """Show/hide password icon button bound to LoginUiState."""
    show = LoginUiState.show_password
    return rx.icon_button(
        rx.icon(rx.cond(show, "eye-off", "eye"), size=15),
        variant="ghost",
        type="button",
        aria_label=rx.cond(show, AUTH["hide_password"], AUTH["show_password"]),
        on_click=LoginUiState.toggle_password,
        _hover={"cursor": "pointer"},
    )


def field(
    label: str,
    name: str,
    icon: str,
    autocomplete: str,
    field_type: Literal["text", "password"] = "text",
) -> rx.Component:
    """Labelled input; the password field gets a show/hide toggle."""
    slots: list[rx.Component] = [rx.input.slot(rx.icon(icon))]
    if name == "password":
        slots.append(rx.input.slot(_password_toggle()))
    input_type = (
        rx.cond(LoginUiState.show_password, "text", "password")
        if name == "password"
        else field_type
    )
    control = rx.input(
        *slots,
        name=name,
        font_size=TEXT_SIZE_3,
        variant="surface",
        width="100%",
        type=input_type,
        custom_attrs={"autocomplete": autocomplete},
    )
    return rx.vstack(
        rx.text(label, font_size=TEXT_SIZE_2, weight="medium"),
        control,
        gap=LABEL_GAP,
        width="100%",
        align_items="stretch",
    )


def submit_button() -> rx.Component:
    """Full-width glowing pill CTA with a loading state."""
    return rx.button(
        rx.cond(
            AuthState.is_logging_in,
            rx.fragment(rx.spinner(), rx.text(AUTH["signing_in"])),
            rx.text(AUTH["sign_in"]),
        ),
        type="submit",
        size="4",
        radius="full",
        width="100%",
        min_height=LOGIN_BUTTON_MIN_HEIGHT,
        display="flex",
        align_items="center",
        justify_content="center",
        disabled=AuthState.is_logging_in,
        box_shadow="0 0 2em var(--accent-a5)",
        transition="box-shadow 150ms ease, transform 150ms ease",
        _hover={"cursor": "pointer", "box_shadow": "0 0 3em var(--accent-a7)"},
    )


def login_card() -> rx.Component:
    """Sign-in card with the login form (default card styling)."""
    return rx.card(
        rx.flex(
            rx.heading(AUTH["title"], as_="h2", font_size=LOGIN_TITLE_SIZE),
            rx.flex(
                error_callout(),
                rx.form(
                    rx.flex(
                        rx.flex(
                            field(
                                AUTH["username_label"],
                                "username",
                                "user",
                                "username",
                            ),
                            field(
                                AUTH["password_label"],
                                "password",
                                "lock",
                                "current-password",
                            ),
                            direction="column",
                            gap=FIELD_GAP,
                            width="100%",
                        ),
                        submit_button(),
                        direction="column",
                        gap=FORM_BUTTON_GAP,
                        width="100%",
                    ),
                    on_submit=AuthState.login,
                    reset_on_submit=False,
                    width="100%",
                ),
                direction="column",
                gap=CALLOUT_GAP,
                width="100%",
            ),
            direction="column",
            gap=CARD_TITLE_GAP,
            width="100%",
        ),
        size="3",
        width="100%",
        max_width="26em",
        padding=responsive(CARD_PADDING_MOBILE, sm=CARD_PADDING_DESKTOP),
        class_name="login-rise login-rise-2",
    )


def brand_mark() -> rx.Component:
    """Small brand row shown above the sign-in card."""
    return rx.flex(
        rx.icon("activity", size=15),
        rx.text(AUTH["brand"], font_size=TEXT_SIZE_2, weight="medium"),
        direction="row",
        align="center",
        justify="center",
        gap=BRAND_MARK_GAP,
        width="100%",
    )


def login_right_panel() -> rx.Component:
    """Centered right-panel stack: brand row, sign-in card, footer note."""
    return rx.flex(
        brand_mark(),
        login_card(),
        footer_note(),
        direction="column",
        align="center",
        justify="center",
        gap=RIGHT_PANEL_GAP,
        width="100%",
        max_width=RIGHT_PANEL_MAX_WIDTH,
        margin_x="auto",
        padding_x="1.25em",
        padding_y="1em",
    )


def footer_note() -> rx.Component:
    """Muted authorized-staff-only footer line."""
    return rx.box(
        rx.text(
            AUTH["footer"], font_size=TEXT_SIZE_1, color=TEXT_MUTED, text_align="center"
        ),
        width="100%",
        display="flex",
        justify_content="center",
        class_name="login-rise login-rise-3",
    )


__all__ = [
    "BRAND_MARK_GAP",
    "CALLOUT_GAP",
    "CARD_PADDING_DESKTOP",
    "CARD_PADDING_MOBILE",
    "CARD_TITLE_GAP",
    "FIELD_GAP",
    "FORM_BUTTON_GAP",
    "LABEL_GAP",
    "RIGHT_PANEL_GAP",
    "RIGHT_PANEL_MAX_WIDTH",
    "brand_mark",
    "error_callout",
    "field",
    "footer_note",
    "login_card",
    "login_right_panel",
    "submit_button",
]

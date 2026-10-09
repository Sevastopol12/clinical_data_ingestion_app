"""Login layout components (brand bar, glass card, fields, CTA)."""

from typing import Literal, cast

import reflex as rx

from data_managment_system.copy import AUTH
from data_managment_system.states.auth import AuthState
from data_managment_system.states.login_ui import LoginUiState
from data_managment_system.theme import (
    LOGIN_BUTTON_MIN_HEIGHT,
    LOGIN_CARD_HOVER,
    TEXT_MUTED,
    TEXT_SIZE_1,
    TEXT_SIZE_2,
    TEXT_SIZE_3,
    TEXT_SIZE_5,
    responsive,
)

_RATE_PREFIX, _RATE_SUFFIX = AUTH["err_rate_limited"].split("{seconds}")

CARD_PADDING_MOBILE = "1.5em"
CARD_PADDING_DESKTOP = "2em"
CARD_TITLE_GAP = "2em"
LABEL_GAP = "0.5em"
FIELD_GAP = "1.75em"
FORM_BUTTON_GAP = "2.25em"
CALLOUT_GAP = "1.25em"
CARD_FOOTER_GAP = "1.25em"
BRAND_PADDING_Y = "0.5em"
BRAND_PADDING_X_MOBILE = "1.25em"
BRAND_PADDING_X_DESKTOP = "3em"
SCRIM_WIDTH = "46em"
SCRIM_HEIGHT = "40em"
SCRIM_BACKGROUND = (
    "radial-gradient(ellipse at center, var(--black-a7), transparent 70%)"
)


def hero_scrim() -> rx.Component:
    """Soft dark scrim behind the card (decor only)."""
    return rx.box(
        position="absolute",
        left="50%",
        top="50%",
        width=SCRIM_WIDTH,
        height=SCRIM_HEIGHT,
        max_width="100vw",
        background=SCRIM_BACKGROUND,
        z_index="1",
        pointer_events="none",
        aria_hidden="true",
        style={"transform": "translate(-50%, -50%)"},
    )


def brand_bar() -> rx.Component:
    """Left-aligned brand row anchored to the viewport frame."""
    return rx.flex(
        rx.box(
            rx.icon("activity"),
            background="var(--accent-a3)",
            border="1px solid var(--accent-a6)",
            border_radius="0.6em",
            padding="0.5em",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        rx.text(AUTH["brand"], font_size=TEXT_SIZE_2, weight="medium"),
        direction="row",
        align="center",
        justify="start",
        gap="0.6em",
        width="100%",
        padding_x=responsive(BRAND_PADDING_X_MOBILE, md=BRAND_PADDING_X_DESKTOP),
        padding_y=BRAND_PADDING_Y,
        position="relative",
        z_index="2",
    )


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
        rx.icon(rx.cond(show, "eye-off", "eye")),
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
            rx.fragment(rx.text(AUTH["sign_in"]), rx.icon("arrow-right")),
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
    """Glass sign-in card with the login form."""
    return rx.box(
        rx.flex(
            rx.heading(AUTH["title"], as_="h2", font_size=TEXT_SIZE_5),
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
        background="var(--black-a8)",
        backdrop_filter="blur(1.25em)",
        style={"-webkit-backdrop-filter": "blur(1.25em)"},
        border="1px solid var(--gray-a5)",
        box_shadow="inset 0 1px 0 var(--gray-a4), 0 2em 5em var(--black-a9)",
        border_radius="1em",
        padding=responsive(CARD_PADDING_MOBILE, sm=CARD_PADDING_DESKTOP),
        width="100%",
        max_width="26em",
        _focus_within={"border_color": "var(--accent-a8)"},
        _hover=LOGIN_CARD_HOVER,
        class_name="login-rise login-rise-2",
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
    "BRAND_PADDING_X_DESKTOP",
    "BRAND_PADDING_X_MOBILE",
    "BRAND_PADDING_Y",
    "CALLOUT_GAP",
    "CARD_FOOTER_GAP",
    "CARD_PADDING_DESKTOP",
    "CARD_PADDING_MOBILE",
    "CARD_TITLE_GAP",
    "FIELD_GAP",
    "FORM_BUTTON_GAP",
    "LABEL_GAP",
    "SCRIM_BACKGROUND",
    "SCRIM_HEIGHT",
    "SCRIM_WIDTH",
    "brand_bar",
    "error_callout",
    "field",
    "footer_note",
    "hero_scrim",
    "login_card",
    "submit_button",
]

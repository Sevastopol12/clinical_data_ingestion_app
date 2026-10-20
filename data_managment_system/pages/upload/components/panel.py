"""The upload panel: drop zone, file cards, and the sticky footer actions."""

from typing import Any

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.states.upload import FileInputState
from data_managment_system.theme import (
    FLOAT_HOVER,
    FLOAT_SHADOW,
    FLOAT_TRANSITION,
    TEXT_SIZE_2,
    TEXT_SIZE_3,
    TEXT_SIZE_4,
    responsive,
)

from .dropzone import drop_zone
from .file_card import file_card


def _floating_style(blocked: rx.Var[bool], *, shadow: bool = False) -> dict[str, Any]:
    """Return the lifted-button hover style, inert while the action is blocked."""
    style: dict[str, Any] = {
        "transform": rx.cond(blocked, "none", FLOAT_HOVER["transform"]),
        "border_color": rx.cond(blocked, "transparent", FLOAT_HOVER["border_color"]),
    }
    if shadow:
        style["box_shadow"] = rx.cond(blocked, "none", FLOAT_HOVER["box_shadow"])
    return style


def footer() -> rx.Component:
    """Build the sticky footer with the file count and the batch actions."""
    blocked_clear = FileInputState.is_submitting | ~FileInputState.has_files
    blocked_submit = FileInputState.is_submitting | ~FileInputState.can_submit
    return rx.flex(
        rx.text(FileInputState.count_label, font_size=TEXT_SIZE_2, weight="medium"),
        rx.spacer(),
        rx.hstack(
            rx.button(
                UPLOAD["clear_all"],
                variant="soft",
                color_scheme="gray",
                font_size=TEXT_SIZE_3,
                radius="full",
                disabled=blocked_clear,
                on_click=FileInputState.clear_all,
                box_shadow=rx.cond(blocked_clear, "none", FLOAT_SHADOW),
                transition=FLOAT_TRANSITION,
                _hover={
                    "cursor": rx.cond(blocked_clear, "not-allowed", "pointer"),
                    **_floating_style(blocked_clear),
                },
            ),
            rx.button(
                rx.icon("upload"),
                UPLOAD["upload"],
                variant="solid",
                font_size=TEXT_SIZE_4,
                radius="full",
                loading=FileInputState.is_submitting,
                disabled=blocked_submit,
                on_click=FileInputState.submit_uploads,
                box_shadow=rx.cond(blocked_submit, "none", FLOAT_SHADOW),
                transition=FLOAT_TRANSITION,
                _hover={
                    "cursor": rx.cond(blocked_submit, "not-allowed", "pointer"),
                    **_floating_style(blocked_submit, shadow=True),
                },
                width=responsive("100%", sm="auto"),
            ),
            gap="0.5em",
            width=responsive("100%", sm="auto"),
            flex_wrap="wrap",
        ),
        width="100%",
        align="center",
        gap="1em",
        flex_wrap="wrap",
        flex_direction=responsive("column", sm="row"),
        padding="1em 1.5em",
        background=rx.color("gray", 2),
        border_top=f"1px solid {rx.color('gray', 5)}",
        position="sticky",
        bottom="0",
    )


def upload_panel() -> rx.Component:
    """Build the file picker, mapping editors, and submit controls."""
    return rx.vstack(
        rx.vstack(
            drop_zone(),
            rx.foreach(FileInputState.files, file_card),
            align="stretch",
            gap="1.25em",
            padding="1.25em 1.5em",
            flex="1",
            min_height="0",
            width="100%",
        ),
        footer(),
        align="stretch",
        min_height="100%",
        width="100%",
        flex_direction="column",
    )


__all__ = ["footer", "upload_panel"]

"""Fixed dashboard button that opens the upload dialog."""

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.states.upload import FileInputState
from data_managment_system.theme import (
    FLOAT_HOVER,
    FLOAT_SHADOW,
    FLOAT_TRANSITION,
    TEXT_SIZE_4,
)


def upload_fab() -> rx.Component:
    """Build the fixed dashboard button that opens the upload dialog."""
    return rx.button(
        rx.icon("upload", size=18),
        UPLOAD["upload"],
        gap="0.5em",
        aria_label=UPLOAD["fab_label"],
        on_click=FileInputState.open_dialog,
        position="fixed",
        bottom="1.5em",
        right="1.5em",
        radius="full",
        variant="solid",
        font_size=TEXT_SIZE_4,
        z_index=10,
        box_shadow=FLOAT_SHADOW,
        transition=FLOAT_TRANSITION,
        _hover={
            **FLOAT_HOVER,
            "cursor": "pointer",
        },
        _focus_visible={
            "outline": "2px solid var(--accent-8)",
            "outline_offset": "1px",
        },
    )


__all__ = ["upload_fab"]

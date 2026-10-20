"""Upload dialog: the controlled modal and its header row."""

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.pages.upload.components import upload_panel
from data_managment_system.states.upload import FileInputState
from data_managment_system.theme import TEXT_SIZE_2, TEXT_SIZE_5


def _dialog_header() -> rx.Component:
    """Build the dialog header: icon tile, title and description, close button."""
    return rx.hstack(
        rx.hstack(
            rx.box(
                rx.icon("upload", size=20, color=rx.color("accent", 11)),
                width="2.75em",
                height="2.75em",
                border_radius="0.75em",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.vstack(
                rx.dialog.title(
                    UPLOAD["dialog_title"],
                    font_size=TEXT_SIZE_5,
                    weight="bold",
                    margin="0",
                ),
                rx.dialog.description(
                    UPLOAD["dialog_description"],
                    font_size=TEXT_SIZE_2,
                    color=rx.color("gray", 11),
                    margin="0",
                ),
                align="start",
                gap="0.25em",
            ),
            align="center",
        ),
        rx.dialog.close(
            rx.icon_button(
                rx.icon("x"),
                aria_label=UPLOAD["close_label"],
                variant="ghost",
                color_scheme="gray",
                font_size=TEXT_SIZE_2,
                _hover={"cursor": "pointer"},
                _focus_visible={
                    "outline": "2px solid var(--accent-8)",
                    "outline_offset": "1px",
                },
            )
        ),
        align="center",
        justify="between",
        width="100%",
        padding="1.5em 1.5em 1.25em",
        border_bottom=f"1px solid {rx.color('gray', 5)}",
    )


def upload_dialog() -> rx.Component:
    """Build the controlled upload dialog used by the dashboard."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                _dialog_header(),
                rx.box(
                    upload_panel(),
                    flex="1",
                    min_height="0",
                    overflow_y="auto",
                    width="100%",
                ),
                align="stretch",
                width="100%",
                min_height="0",
                height="100%",
                flex_direction="column",
            ),
            padding="0",
            background="var(--gray-a2)",
            backdrop_filter="blur(1em)",
            style={"-webkit-backdrop-filter": "blur(1em)"},
            border="1px solid var(--gray-a5)",
            border_radius="1em",
            box_shadow="var(--shadow-6)",
            overflow="hidden",
            display="flex",
            flex_direction="column",
            max_width="42em",
            height="min(88vh, 52em)",
            max_height="88vh",
        ),
        open=FileInputState.dialog_open,
        on_open_change=FileInputState.set_dialog_open,
    )


__all__ = ["upload_dialog"]

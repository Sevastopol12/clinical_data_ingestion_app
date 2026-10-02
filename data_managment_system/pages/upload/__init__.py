"""Upload dialog and dashboard upload entry point."""

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.pages.upload.components import upload_panel
from data_managment_system.states.upload import FileInputState


def upload_dialog() -> rx.Component:
    """Build the controlled upload dialog used by the dashboard."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("upload", size=20, color=rx.color("accent", 11)),
                            width="2.75em",
                            height="2.75em",
                            border_radius="0.75em",
                            background=rx.color("accent", 3),
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),
                        rx.vstack(
                            rx.dialog.title(
                                UPLOAD["dialog_title"],
                                size="5",
                                weight="bold",
                                margin="0",
                            ),
                            rx.dialog.description(
                                UPLOAD["dialog_description"],
                                size="2",
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
                            size="2",
                            _hover={"cursor": "pointer"},
                        )
                    ),
                    align="center",
                    justify="between",
                    width="100%",
                    padding="1.5em 1.5em 1.25em",
                    border_bottom=f"1px solid {rx.color('gray', 5)}",
                ),
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
            border_radius="1.25em",
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


def upload_fab() -> rx.Component:
    """Build the fixed dashboard button that opens the upload dialog."""
    return rx.icon_button(
        rx.icon("upload"),
        aria_label=UPLOAD["fab_label"],
        on_click=FileInputState.open_dialog,
        position="fixed",
        bottom="1.5em",
        right="1.5em",
        radius="full",
        z_index=10,
        _hover={"cursor": "pointer"},
    )


__all__ = ["upload_dialog", "upload_fab"]

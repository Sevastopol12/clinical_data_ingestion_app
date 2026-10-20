"""Components for editing a file's source-to-target column mapping."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.states.upload import FileInputState
from data_managment_system.theme import TEXT_SIZE_1


def mapping_row(
    filename: rx.Var[str], row: rx.Var[Any], mapping_pending: rx.Var[bool]
) -> rx.Component:
    """Build one editable source-to-target mapping row."""
    row_any: Any = row
    file_any: Any = filename
    return rx.vstack(
        rx.grid(
            rx.code(
                row_any.source,
                color=rx.color("gray", 11),
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
            ),
            rx.icon("arrow-right", size=14, color=rx.color("gray", 10)),
            rx.input(
                value=row_any.target,
                placeholder=UPLOAD["target_placeholder"],
                color_scheme=rx.cond(
                    row_any.error != "",
                    "red",
                    rx.cond(row_any.warning != "", "yellow", "gray"),
                ),
                disabled=FileInputState.is_submitting | mapping_pending,
                on_change=lambda value: FileInputState.set_target(
                    file_any, row_any.source, value
                ),
                on_blur=FileInputState.blur_target(file_any, row_any.source),
                width="100%",
            ),
            columns=cast(Any, {"initial": "1fr", "sm": "1fr auto 1fr"}),
            gap="0.5em",
            align="center",
            width="100%",
        ),
        rx.match(
            row_any.error,
            (
                "empty-normalized",
                rx.text(
                    UPLOAD["err_target_empty"],
                    color=rx.color("red", 11),
                    font_size=TEXT_SIZE_1,
                ),
            ),
            rx.match(
                row_any.warning,
                (
                    "duplicate-target",
                    rx.text(
                        UPLOAD["warn_target_duplicate"],
                        color=rx.color("yellow", 11),
                        font_size=TEXT_SIZE_1,
                    ),
                ),
                rx.fragment(),
            ),
        ),
        width="100%",
        gap="0.25em",
    )


def mapping_block(file_any: Any) -> rx.Component:
    """Build the collapsible mapping editor for one file."""
    return rx.box(
        rx.hstack(
            rx.text(
                UPLOAD["source_column"],
                font_size=TEXT_SIZE_1,
                color=rx.color("gray", 10),
            ),
            rx.spacer(),
            rx.text(
                UPLOAD["target_column"],
                font_size=TEXT_SIZE_1,
                color=rx.color("gray", 10),
            ),
            width="100%",
        ),
        rx.cond(
            file_any.mapping_pending,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text(
                    UPLOAD["mapping_pending"],
                    font_size=TEXT_SIZE_1,
                    color=rx.color("gray", 11),
                ),
                gap="0.5em",
                align="center",
            ),
            rx.vstack(
                rx.foreach(
                    file_any.rows,
                    lambda row: mapping_row(
                        file_any.filename, row, file_any.mapping_pending
                    ),
                ),
                width="100%",
                gap="0.5em",
            ),
        ),
        background=rx.color("gray", 2),
        border=f"1px solid {rx.color('gray', 4)}",
        border_radius="0.75em",
        padding="0.75em",
        width="100%",
        on_click=rx.stop_propagation,
        _hover={"cursor": "pointer"},
    )


__all__ = ["mapping_block", "mapping_row"]

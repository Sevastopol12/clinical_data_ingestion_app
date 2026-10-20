"""Components for the per-file upload cards and their progress state."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.states.upload import FileInputState
from data_managment_system.theme import TEXT_SIZE_1, TEXT_SIZE_2

from .mapping import mapping_block


def progress_row(stage: rx.Var[str]) -> rx.Component:
    """Build the staged progress bar shown while a file is uploaded."""
    width = rx.match(
        stage,
        ("presigning", "33%"),
        ("uploading", "66%"),
        ("recording", "100%"),
        "0%",
    )
    label = rx.match(
        stage,
        ("presigning", UPLOAD["stage_presigning"]),
        ("uploading", UPLOAD["stage_uploading"]),
        ("recording", UPLOAD["stage_recording"]),
        "",
    )
    return rx.vstack(
        rx.text(label, font_size=TEXT_SIZE_1, color=rx.color("gray", 11)),
        rx.box(
            rx.box(
                width=width,
                height="100%",
                background="var(--accent-9)",
                border_radius="inherit",
                transition="width 300ms ease",
            ),
            width="100%",
            height="0.3em",
            overflow="hidden",
            border_radius="1em",
            background="var(--gray-a5)",
            background_image="linear-gradient(to right, transparent 32.7%, var(--gray-a2) 32.7%, var(--gray-a2) 33.3%, transparent 33.3%, transparent 66%, var(--gray-a2) 66%, var(--gray-a2) 66.6%, transparent 66.6%)",
        ),
        width="100%",
        gap="0.25em",
    )


def stage_badge(stage: rx.Var[str]) -> rx.Component:
    """Build the badge that names the current stage of a file."""
    return cast(
        rx.Component,
        rx.match(
            stage,
            (
                "ready",
                rx.badge(UPLOAD["stage_ready"], color_scheme="gray", variant="soft"),
            ),
            *[
                (
                    active_stage,
                    rx.fragment(),
                )
                for active_stage in ("presigning", "uploading", "recording")
            ],
            (
                "failed",
                rx.badge(UPLOAD["failed_record"], color_scheme="red", variant="soft"),
            ),
            rx.badge(UPLOAD["stage_ready"], color_scheme="gray", variant="soft"),
        ),
    )


def failure_label(stage: rx.Var[str]) -> rx.Component:
    """Build the reason label shown for a file that failed to upload."""
    return cast(
        rx.Component,
        rx.match(
            stage,
            (
                "presign",
                rx.text(
                    UPLOAD["failed_presign"],
                    color=rx.color("red", 11),
                    font_size=TEXT_SIZE_1,
                ),
            ),
            (
                "storage",
                rx.text(
                    UPLOAD["failed_storage"],
                    color=rx.color("red", 11),
                    font_size=TEXT_SIZE_1,
                ),
            ),
            (
                "record",
                rx.text(
                    UPLOAD["failed_record"],
                    color=rx.color("red", 11),
                    font_size=TEXT_SIZE_1,
                ),
            ),
            rx.fragment(),
        ),
    )


def file_card(file: rx.Var[Any]) -> rx.Component:
    """Build one uploaded file's card, including its column mapping."""
    file_any: Any = file
    is_csv = file_any.kind == "CSV"
    expanded_files: Any = FileInputState.expanded_files
    is_expanded = expanded_files.contains(file_any.filename)
    return rx.box(
        rx.flex(
            rx.box(
                rx.icon(
                    "file-text",
                    size=20,
                    color=rx.cond(is_csv, rx.color("blue", 11), rx.color("green", 11)),
                ),
                width="2.5em",
                height="2.5em",
                border_radius="0.625em",
                background=rx.cond(is_csv, rx.color("blue", 3), rx.color("green", 3)),
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(
                    file_any.filename,
                    font_size=TEXT_SIZE_2,
                    weight="medium",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    min_width="0",
                    width="100%",
                ),
                rx.hstack(
                    rx.text(
                        file_any.size_label,
                        font_size=TEXT_SIZE_1,
                        color=rx.color("gray", 11),
                    ),
                    rx.text(
                        rx.cond(is_csv, UPLOAD["kind_csv"], UPLOAD["kind_xlsx"]),
                        font_size=TEXT_SIZE_1,
                        color=rx.color("gray", 11),
                    ),
                    gap="0.5em",
                ),
                rx.cond(
                    (file_any.stage == "presigning")
                    | (file_any.stage == "uploading")
                    | (file_any.stage == "recording"),
                    progress_row(file_any.stage),
                    rx.fragment(),
                ),
                align="start",
                min_width="0",
                flex="1",
                gap="0.25em",
            ),
            stage_badge(file_any.stage),
            rx.icon_button(
                rx.cond(
                    is_expanded,
                    rx.icon("chevron-up"),
                    rx.icon("chevron-down"),
                ),
                aria_label=rx.cond(
                    is_expanded, UPLOAD["hide_mapping"], UPLOAD["show_mapping"]
                ),
                variant="ghost",
                color_scheme="gray",
                _hover={"cursor": "pointer"},
            ),
            rx.icon_button(
                rx.icon("trash-2"),
                aria_label=UPLOAD["remove_file"],
                variant="ghost",
                color_scheme="gray",
                disabled=FileInputState.is_submitting,
                on_click=FileInputState.remove_file(file_any.filename).stop_propagation,
                _hover={"cursor": "pointer", "color": rx.color("red", 11)},
            ),
            align="center",
            gap="0.75em",
            width="100%",
            min_width="0",
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
                rx.text(
                    UPLOAD["columns_count"].format(count=file_any.rows.length()),
                    font_size=TEXT_SIZE_1,
                    color=rx.color("gray", 11),
                ),
                rx.cond(
                    ~is_expanded & (file_any.warning_count > 0),
                    rx.text(
                        UPLOAD["warn_columns_shared"].format(
                            count=file_any.warning_count
                        ),
                        font_size=TEXT_SIZE_1,
                        color=rx.color("yellow", 11),
                    ),
                    rx.fragment(),
                ),
                gap="0.25em",
                align="start",
            ),
        ),
        rx.cond(is_expanded, mapping_block(file_any), rx.fragment()),
        failure_label(file_any.failure_stage),
        background="var(--gray-a2)",
        border="1px solid var(--gray-a5)",
        border_radius="0.875em",
        padding="1em",
        width="100%",
        display="flex",
        flex_direction="column",
        gap="1em",
        on_click=FileInputState.toggle_mapping(file_any.filename),
        _hover={"cursor": "pointer"},
    )


__all__ = ["failure_label", "file_card", "progress_row", "stage_badge"]

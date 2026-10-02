"""Components for selecting files and editing their column mappings."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.models.ingestion import (
    MAX_BATCH_FILES,
    MAX_FILE_BYTES,
    SUPPORTED_FORMATS,
)
from data_managment_system.states.upload import FileInputState

UPLOAD_ID = "upload_files"


def _stage_text(stage: str) -> str:
    return {
        "presigning": UPLOAD["stage_presigning"],
        "uploading": UPLOAD["stage_uploading"],
        "recording": UPLOAD["stage_recording"],
    }[stage]


def _stage_badge(stage: rx.Var[str]) -> rx.Component:
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
                    rx.badge(
                        rx.hstack(
                            rx.spinner(size="1"),
                            _stage_text(active_stage),
                            gap="0.25em",
                            align="center",
                        ),
                        color_scheme="violet",
                        variant="soft",
                    ),
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


def _failure_label(stage: rx.Var[str]) -> rx.Component:
    return cast(
        rx.Component,
        rx.match(
            stage,
            (
                "presign",
                rx.text(UPLOAD["failed_presign"], color=rx.color("red", 11), size="1"),
            ),
            (
                "storage",
                rx.text(UPLOAD["failed_storage"], color=rx.color("red", 11), size="1"),
            ),
            (
                "record",
                rx.text(UPLOAD["failed_record"], color=rx.color("red", 11), size="1"),
            ),
            rx.fragment(),
        ),
    )


def _mapping_row(
    filename: rx.Var[str], row: rx.Var[Any], mapping_pending: rx.Var[bool]
) -> rx.Component:
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
                color_scheme=rx.cond(row_any.error != "", "red", "gray"),
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
        rx.text(
            rx.match(
                row_any.error,
                ("empty-normalized", UPLOAD["err_target_empty"]),
                ("duplicate-target", UPLOAD["err_target_duplicate"]),
                "",
            ),
            color=rx.color("red", 11),
            size="1",
        ),
        width="100%",
        gap="0.25em",
    )


def _mapping_block(file_any: Any) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text(UPLOAD["source_column"], size="1", color=rx.color("gray", 10)),
            rx.spacer(),
            rx.text(UPLOAD["target_column"], size="1", color=rx.color("gray", 10)),
            width="100%",
        ),
        rx.cond(
            file_any.mapping_pending,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text(
                    UPLOAD["mapping_pending"], size="1", color=rx.color("gray", 11)
                ),
                gap="0.5em",
                align="center",
            ),
            rx.vstack(
                rx.foreach(
                    file_any.rows,
                    lambda row: _mapping_row(
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
    )


def _file_card(file: rx.Var[Any]) -> rx.Component:
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
                    size="2",
                    weight="medium",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    min_width="0",
                    width="100%",
                ),
                rx.hstack(
                    rx.text(file_any.size_label, size="1", color=rx.color("gray", 11)),
                    rx.text(
                        rx.cond(is_csv, UPLOAD["kind_csv"], UPLOAD["kind_xlsx"]),
                        size="1",
                        color=rx.color("gray", 11),
                    ),
                    gap="0.5em",
                ),
                align="start",
                min_width="0",
                flex="1",
                gap="0.25em",
            ),
            _stage_badge(file_any.stage),
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
                on_click=FileInputState.toggle_mapping(file_any.filename),
                _hover={"cursor": "pointer"},
            ),
            rx.icon_button(
                rx.icon("trash-2"),
                aria_label=UPLOAD["remove_file"],
                variant="ghost",
                color_scheme="gray",
                disabled=FileInputState.is_submitting,
                on_click=FileInputState.remove_file(file_any.filename),
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
                    UPLOAD["mapping_pending"], size="1", color=rx.color("gray", 11)
                ),
                gap="0.5em",
                align="center",
            ),
            rx.text(
                UPLOAD["columns_count"].format(count=file_any.rows.length()),
                size="1",
                color=rx.color("gray", 11),
            ),
        ),
        rx.cond(is_expanded, _mapping_block(file_any), rx.fragment()),
        _failure_label(file_any.failure_stage),
        border=f"1px solid {rx.color('gray', 4)}",
        border_radius="0.875em",
        padding="1em",
        width="100%",
        display="flex",
        flex_direction="column",
        gap="1em",
    )


def upload_panel() -> rx.Component:
    """Build the file picker, mapping editors, and submit controls."""
    drop_content = rx.vstack(
        rx.box(
            rx.icon("upload", size=24, color=rx.color("accent", 11)),
            width="3.5em",
            height="3.5em",
            border_radius="50%",
            background=rx.color("accent", 3),
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        rx.text(UPLOAD["drop_zone"], size="3", weight="medium", text_align="center"),
        rx.text(
            UPLOAD["supports_files"],
            size="1",
            color=rx.color("gray", 11),
            text_align="center",
        ),
        align="center",
        gap="0.5em",
        width="100%",
    )
    upload = rx.upload(
        rx.cond(FileInputState.has_files, drop_content, drop_content),
        multiple=True,
        id=UPLOAD_ID,
        accept=cast(Any, SUPPORTED_FORMATS),
        max_files=MAX_BATCH_FILES,
        max_size=MAX_FILE_BYTES,
        disabled=FileInputState.is_submitting,
        on_drop=FileInputState.upload_files(
            cast(Any, rx.upload_files_chunk(upload_id=UPLOAD_ID))
        ),
        on_drop_rejected=cast(Any, FileInputState.reject_files),
        flex=rx.cond(FileInputState.has_files, "0", "1"),
        min_height=rx.cond(FileInputState.has_files, "7em", "14em"),
        padding="1.25em",
        border=f"1.5px dashed {rx.color('accent', 7)}",
        border_radius="1em",
        background=rx.color("accent", 2),
        transition="0.15s",
        _hover={
            "cursor": "pointer",
            "border_color": rx.color("accent", 9),
            "background": rx.color("accent", 3),
        },
        width="100%",
        display="flex",
        align_items="center",
        justify_content="center",
    )

    footer = rx.flex(
        rx.text(FileInputState.count_label, size="2", weight="medium"),
        rx.spacer(),
        rx.hstack(
            rx.button(
                UPLOAD["clear_all"],
                variant="soft",
                color_scheme="gray",
                size="3",
                disabled=FileInputState.is_submitting | ~FileInputState.has_files,
                on_click=FileInputState.clear_all,
                _hover={"cursor": "pointer"},
            ),
            rx.button(
                rx.icon("upload"),
                UPLOAD["upload"],
                variant="classic",
                size="4",
                loading=FileInputState.is_submitting,
                disabled=FileInputState.is_submitting | ~FileInputState.can_submit,
                on_click=FileInputState.submit_uploads,
                _hover={"cursor": "pointer"},
                width={"initial": "100%", "sm": "auto"},
            ),
            gap="0.5em",
            width={"initial": "100%", "sm": "auto"},
            flex_wrap="wrap",
        ),
        width="100%",
        align="center",
        gap="1em",
        flex_wrap="wrap",
        flex_direction={"initial": "column", "sm": "row"},
        padding="1em 1.5em",
        background=rx.color("gray", 2),
        border_top=f"1px solid {rx.color('gray', 5)}",
        position="sticky",
        bottom="0",
    )

    return rx.vstack(
        rx.vstack(
            upload,
            rx.foreach(FileInputState.files, _file_card),
            align="stretch",
            gap="1.25em",
            padding="1.25em 1.5em",
            flex="1",
            min_height="0",
            width="100%",
        ),
        footer,
        align="stretch",
        min_height="100%",
        width="100%",
        flex_direction="column",
    )


__all__ = ["upload_panel"]

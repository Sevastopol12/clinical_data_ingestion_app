"""The drag-and-drop file picker for the upload dialog."""

from typing import Any, cast

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.models.ingestion import (
    MAX_BATCH_FILES,
    MAX_FILE_BYTES,
    SUPPORTED_FORMATS,
)
from data_managment_system.states.upload import FileInputState
from data_managment_system.theme import (
    FLOAT_HOVER,
    TEXT_SIZE_1,
    TEXT_SIZE_3,
    UPLOAD_DROP_CSS,
)

UPLOAD_ID = "upload_files"


def drop_zone() -> rx.Component:
    """Build the drag-and-drop file picker."""
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
        rx.text(
            UPLOAD["drop_zone"],
            font_size=TEXT_SIZE_3,
            weight="medium",
            text_align="center",
        ),
        rx.text(
            UPLOAD["supports_files"],
            font_size=TEXT_SIZE_1,
            color=rx.color("gray", 11),
            text_align="center",
        ),
        align="center",
        gap="0.5em",
        width="100%",
    )
    return rx.upload(
        rx.el.style(UPLOAD_DROP_CSS),
        drop_content,
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
        border="1px dashed var(--gray-a6)",
        border_radius="1em",
        background="var(--gray-a2)",
        box_shadow="none",
        transition="transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease",
        class_name="upload-dropzone",
        drag_active_style=rx.Style(
            {
                "border": "4px solid transparent",
                "background_image": "linear-gradient(var(--gray-a2), var(--gray-a2)) padding-box, repeating-conic-gradient(from var(--upload-border-angle), var(--accent-9) 0 12deg, transparent 12deg 30deg) border-box",
                "animation": "upload-border-spin 1.6s linear infinite",
                "transform": "scale(1.02)",
            }
        ),
        _hover={
            **FLOAT_HOVER,
            "cursor": "pointer",
            "background": rx.color("accent", 3),
        },
        width="100%",
        display="flex",
        align_items="center",
        justify_content="center",
    )


__all__ = ["UPLOAD_ID", "drop_zone"]

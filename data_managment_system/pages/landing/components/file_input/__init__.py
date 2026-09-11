import reflex as rx
from .state import FileInputState


def upload_file_area() -> rx.Component:
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.button(
                    "Select files",
                ),
                rx.text("Drag and drop files here or click to select files"),
                width="100%",
                spacing="3",
            ),
            id="upload_section",
            multiple=True,
            _hover={"cursor": "pointer"},
            on_drop=FileInputState.dump_files(
                rx.upload_files_chunk(upload_id="upload_section")
            ),
        ),
        rx.button(
            "Upload",
        ),
        rx.vstack(
            rx.foreach(
                FileInputState.get_uploaded_files, lambda x: uploaded_file_card(x)
            ),
            width="100%",
        ),
    )


def uploaded_file_card(filename: rx.Var[str]) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.text(filename),
            rx.spacer(),
            rx.button(
                rx.icon("x"),
                variant="ghost",
                on_click=FileInputState.remove_file(filename),
            ),
            width="100%",
        ),
        width="100%",
    )


__all__ = ["upload_file_area"]

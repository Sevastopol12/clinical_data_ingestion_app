import reflex as rx
from .state import FileInputState


def upload_file_area() -> rx.Component:
    return rx.vstack(
        rx.upload("upload"),
        on_click=FileInputState.read_files(rx.upload_files("upload")),
        width="100%",
    )


__all__ = ["upload_file_area"]

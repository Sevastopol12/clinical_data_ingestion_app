import reflex as rx
from data_managment_system.styles.background import create_background
from .components import upload_file_area

@rx.page(route="/")
def index() -> rx.Component:
    return rx.fragment(
        create_background(),
        rx.container(
            rx.center(
                upload_file_area(),
                width="100%",
                align="center",
            ),
            # width="50vw",
            padding="12em 6em",
        ),
    )

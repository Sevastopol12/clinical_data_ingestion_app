import reflex as rx
from data_managment_system.styles.background import create_background


@rx.page(route="/")
def index() -> rx.Component:
    return rx.fragment(
        create_background(),
        rx.container(
            rx.center(
                rx.heading("Nuhuh"),
                width="100%",
                align="center",
                font_size="10em",
            ),
            min_width="100vw",
            padding="12em 6em",
        ),
    )

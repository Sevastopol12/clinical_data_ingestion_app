import reflex as rx

from .pages import landing_index

app = rx.App(
    style={"font_family": "Cabin"},
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Cabin:ital,wght@0,400..700;1,400..700&family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&display=swap"
    ],
)

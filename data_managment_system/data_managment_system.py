import reflex as rx

from . import pages  # noqa: F401
from .theme import FONT_FAMILY, PAGE_BACKGROUND, STYLESHEETS, TEXT_PRIMARY, THEME

app = rx.App(
    theme=THEME,
    style={
        "font_family": FONT_FAMILY,
        "background_color": PAGE_BACKGROUND,
        "color": TEXT_PRIMARY,
    },
    stylesheets=STYLESHEETS,
)

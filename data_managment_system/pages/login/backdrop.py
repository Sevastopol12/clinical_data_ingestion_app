"""Login left panel (Neon-style): heart-pulse icon + confined ECG sweep."""

import reflex as rx

from data_managment_system.copy import AUTH
from data_managment_system.theme import (
    FONT_FAMILY,
    LOGIN_CARO_LINE,
    LOGIN_CARO_PATTERN,
    LOGIN_CSS,
    LOGIN_ECG_BRIGHT_DATA_URI,
    LOGIN_ECG_DATA_URI,
    LOGIN_PANEL_LIGHTS,
    LOGIN_SWEEP_MASK,
    PAGE_BACKGROUND,
)

PANEL_BACKGROUND = f"{LOGIN_PANEL_LIGHTS}, {PAGE_BACKGROUND}"

# Panel-confined sweep: the sweep window is 22% of the ECG band width and
# travels from just off the left edge (-100% of its own width) to the right
# edge of the band (~455% of its own width). The bright inner trace is 455%
# wide (i.e. one full band width) and counter-moves from +22% to -100% so it
# stays aligned with the dim base trace, exactly mirroring the old
# viewport-wide (-22vw/100vw) geometry. Defined after LOGIN_CSS so these
# keyframes win; class names and timings are unchanged, so LOGIN_CSS's
# prefers-reduced-motion handling still applies.
PANEL_SWEEP_CSS = """
@keyframes login-sweep {
    from { transform: translateX(-100%); }
    to { transform: translateX(455%); }
}
@keyframes login-sweep-inner {
    from { transform: translateX(22%); }
    to { transform: translateX(-100%); }
}
"""


def login_left_panel() -> rx.Component:
    """Return the decorative left login panel (icon, ECG sweep, and dim caro rails)."""

    def caro_rail(position: str) -> rx.Component:
        return rx.box(
            position="absolute",
            left="0",
            top="0" if position == "top" else "auto",
            bottom="0" if position == "bottom" else "auto",
            width="100%",
            height="50%",
            background_image=LOGIN_CARO_PATTERN,
            background_size="2.5em 1.32em",
            border_top=f"1.2px solid {LOGIN_CARO_LINE}"
            if position == "top"
            else "none",
            border_bottom=f"1.2px solid {LOGIN_CARO_LINE}"
            if position == "bottom"
            else "none",
            pointer_events="none",
            aria_hidden="true",
        )

    icon = rx.box(
        rx.icon(
            "heart-pulse",
            size=95,
            color="var(--accent-9)",
            style={"width": "100%", "height": "100%"},
        ),
        width="5.95em",
        height="5.95em",
        display="flex",
        align_items="center",
        justify_content="center",
        position="absolute",
        top="30%",
        left="50%",
        style={"transform": "translateX(-50%)"},
        z_index="1",
        pointer_events="none",
        aria_hidden="true",
    )
    title = rx.text(
        AUTH["panel_title"],
        position="absolute",
        top="43%",
        left="50%",
        width="100%",
        text_align="center",
        font_family=FONT_FAMILY,
        font_size="1.875em",
        font_weight="600",
        color="#ffffff",
        style={"transform": "translateX(-50%)"},
        z_index="1",
        aria_hidden="true",
    )
    ecg_base = rx.box(
        position="absolute",
        inset="0",
        width="100%",
        height="100%",
        background_image=LOGIN_ECG_DATA_URI,
        background_repeat="no-repeat",
        background_size="100% 100%",
        opacity="0.5",
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
        class_name="login-ecg",
    )
    sweep_inner = rx.box(
        position="absolute",
        left="0",
        top="0",
        width="455%",
        height="100%",
        background_image=LOGIN_ECG_BRIGHT_DATA_URI,
        background_repeat="no-repeat",
        background_size="100% 100%",
        pointer_events="none",
        aria_hidden="true",
        class_name="login-sweep-inner",
    )
    sweep_layer = rx.box(
        sweep_inner,
        position="absolute",
        left="0",
        top="0",
        width="22%",
        height="100%",
        overflow="hidden",
        mask_image=LOGIN_SWEEP_MASK,
        style={"-webkit-mask-image": LOGIN_SWEEP_MASK},
        pointer_events="none",
        aria_hidden="true",
        class_name="login-sweep",
    )
    ecg_band = rx.box(
        ecg_base,
        sweep_layer,
        position="absolute",
        left="0",
        top="70%",
        width="100%",
        height="12em",
        overflow="hidden",
        style={"transform": "translateY(-50%)"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    return rx.flex(
        rx.el.style(LOGIN_CSS),
        rx.el.style(PANEL_SWEEP_CSS),
        caro_rail("top"),
        caro_rail("bottom"),
        icon,
        title,
        ecg_band,
        direction="column",
        align="center",
        justify_content="center",
        position="relative",
        width="45%",
        min_height="100vh",
        style={"minHeight": "100dvh"},
        overflow="hidden",
        background=PANEL_BACKGROUND,
        pointer_events="none",
        aria_hidden="true",
    )


__all__ = ["login_left_panel"]

"""Dashboard decorative backdrop (static, data-free).

Layers (back to front), all decor-only:
- masked ECG-paper grid: z 0
- top aurora glow: z 0
- hero-right ECG trace (lg+ only): z 1

Page content must use ``z_index >= 2``.
"""

import reflex as rx

from data_managment_system.theme import (
    DASH_ECG_DATA_URI,
    DASH_ECG_MASK,
    DASH_GLOW,
    DASH_GRID_BG,
    DASH_GRID_BG_SIZE,
    DASH_GRID_MASK,
)


def dashboard_backdrop() -> rx.Component:
    """Return the decorative dashboard backdrop fragment."""
    grid_layer = rx.box(
        position="fixed",
        inset="0",
        width="100%",
        height="100%",
        max_width="100vw",
        overflow="hidden",
        background_image=DASH_GRID_BG,
        background_size=DASH_GRID_BG_SIZE,
        background_repeat="no-repeat",
        mask_image=DASH_GRID_MASK,
        style={"-webkit-mask-image": DASH_GRID_MASK},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    glow_layer = rx.box(
        position="fixed",
        inset="0",
        width="100%",
        height="100%",
        max_width="100vw",
        overflow="hidden",
        background_image=DASH_GLOW,
        background_repeat="no-repeat",
        background_size="100% 100%",
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    ecg_layer = rx.box(
        position="fixed",
        right="0",
        top="16vh",
        width="42em",
        max_width="45vw",
        height="10em",
        overflow="hidden",
        background_image=DASH_ECG_DATA_URI,
        background_size="100% 100%",
        background_position="center",
        background_repeat="no-repeat",
        mask_image=DASH_ECG_MASK,
        style={"-webkit-mask-image": DASH_ECG_MASK},
        display={"initial": "none", "lg": "block"},
        z_index="1",
        pointer_events="none",
        aria_hidden="true",
    )
    return rx.fragment(grid_layer, glow_layer, ecg_layer)


__all__ = ["dashboard_backdrop"]

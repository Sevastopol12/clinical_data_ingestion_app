"""Login backdrop layers.

Layer z-indexes (back to front):
- masked grid: 0
- login glow: 0
- radar rings and ping: 0
- HUD brackets, rulers, timeline, traces, crosshairs: 0
- aurora blobs from ``create_background()``: 1
- ECG trace and monitor sweep: 1

Page content must use ``z_index >= 2`` so it stays above all decorative layers.
"""

import reflex as rx

from data_managment_system.theme import (
    LOGIN_BLOB_OPACITY,
    LOGIN_CROSSHAIR,
    LOGIN_CSS,
    LOGIN_ECG_BRIGHT_DATA_URI,
    LOGIN_ECG_DATA_URI,
    LOGIN_GLOW,
    LOGIN_GRID_BG,
    LOGIN_GRID_BG_SIZE,
    LOGIN_GRID_MASK,
    LOGIN_HUD_LINE,
    LOGIN_HUD_TICK,
    LOGIN_PPG_DATA_URI,
    LOGIN_RADAR_BG,
    LOGIN_RESP_DATA_URI,
    LOGIN_RING_LINE,
    LOGIN_RULER_MAJOR_BG,
    LOGIN_RULER_MASK,
    LOGIN_RULER_MINOR_BG,
    LOGIN_STAGE_MASK,
    LOGIN_SWEEP_MASK,
    LOGIN_TIMELINE_MAJOR_BG,
    LOGIN_TIMELINE_MASK,
    LOGIN_TIMELINE_MINOR_BG,
    create_background,
)


def _solid(token: str) -> str:
    return f"linear-gradient({token}, {token})"


def login_backdrop() -> rx.Component:
    """Return the decorative login backdrop fragment."""
    grid_layer = rx.box(
        position="fixed",
        inset="0",
        width="100%",
        height="100%",
        max_width="100vw",
        overflow="hidden",
        background_image=LOGIN_GRID_BG,
        background_size=LOGIN_GRID_BG_SIZE,
        background_repeat="no-repeat",
        mask_image=LOGIN_GRID_MASK,
        style={"-webkit-mask-image": LOGIN_GRID_MASK},
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
        background_image=LOGIN_GLOW,
        background_repeat="no-repeat",
        background_size="100% 100%",
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    radar_layer = rx.box(
        position="fixed",
        left="50%",
        top="42%",
        width="60em",
        height="60em",
        max_width="100vw",
        overflow="hidden",
        background_image=LOGIN_RADAR_BG,
        background_repeat="no-repeat",
        background_position="center",
        display={"initial": "none", "md": "block"},
        style={"transform": "translate(-50%, -50%)"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    ping_layer = rx.box(
        position="fixed",
        left="50%",
        top="42%",
        width="32em",
        height="32em",
        max_width="100vw",
        border=f"1px solid {LOGIN_RING_LINE}",
        border_radius="50%",
        display={"initial": "none", "md": "block"},
        style={"transform": "translate(-50%, -50%)"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
        class_name="login-ping",
    )
    hud_images = ", ".join([_solid(LOGIN_HUD_LINE)] * 8 + [_solid(LOGIN_HUD_TICK)] * 8)
    hud_sizes = (
        "1px 2.5em, 2.5em 1px, 1px 2.5em, 2.5em 1px, "
        "1px 2.5em, 2.5em 1px, 1px 2.5em, 2.5em 1px, "
        "0.6em 1px, 1px 0.6em, 0.6em 1px, 1px 0.6em, "
        "0.6em 1px, 1px 0.6em, 0.6em 1px, 1px 0.6em"
    )
    hud_positions = (
        "1.5em 1.5em, 1.5em 1.5em, "
        "calc(100% - 1.5em) 1.5em, calc(100% - 4em) 1.5em, "
        "1.5em calc(100% - 4em), 1.5em calc(100% - 1.5em), "
        "calc(100% - 1.5em) calc(100% - 4em), "
        "calc(100% - 4em) calc(100% - 1.5em), "
        "1.5em 4.5em, 4.5em 1.5em, "
        "calc(100% - 2.1em) 4.5em, calc(100% - 5.1em) 1.5em, "
        "1.5em calc(100% - 5.1em), 4.5em calc(100% - 2.1em), "
        "calc(100% - 2.1em) calc(100% - 5.1em), "
        "calc(100% - 5.1em) calc(100% - 2.1em)"
    )
    hud_layer = rx.box(
        position="fixed",
        inset="0",
        width="100%",
        height="100%",
        max_width="100vw",
        overflow="hidden",
        background_image=hud_images,
        background_size=hud_sizes,
        background_position=hud_positions,
        background_repeat="no-repeat",
        display={"initial": "none", "md": "block"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    ruler_images = (
        f"{LOGIN_RULER_MINOR_BG}, {LOGIN_RULER_MAJOR_BG}, "
        f"{LOGIN_RULER_MINOR_BG}, {LOGIN_RULER_MAJOR_BG}"
    )
    ruler_layer = rx.box(
        position="fixed",
        inset="0",
        width="100%",
        height="100%",
        max_width="100vw",
        overflow="hidden",
        background_image=ruler_images,
        background_size="0.5em 70%, 1em 70%, 0.5em 70%, 1em 70%",
        background_position=(
            "1.5em center, 1.5em center, "
            "calc(100% - 2em) center, calc(100% - 2.5em) center"
        ),
        background_repeat="no-repeat",
        mask_image=LOGIN_RULER_MASK,
        style={"-webkit-mask-image": LOGIN_RULER_MASK},
        display={"initial": "none", "lg": "block"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    timeline_layer = rx.box(
        position="fixed",
        left="2em",
        right="2em",
        bottom="1.5em",
        height="1em",
        overflow="hidden",
        background_image=f"{LOGIN_TIMELINE_MINOR_BG}, {LOGIN_TIMELINE_MAJOR_BG}",
        background_size="100% 0.5em, 100% 1em",
        background_position="0 0, 0 0",
        background_repeat="no-repeat",
        mask_image=LOGIN_TIMELINE_MASK,
        style={"-webkit-mask-image": LOGIN_TIMELINE_MASK},
        display={"initial": "none", "md": "block"},
        z_index="0",
        pointer_events="none",
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
        z_index="1",
        pointer_events="none",
        aria_hidden="true",
        class_name="login-ecg",
    )
    sweep_inner = rx.box(
        position="absolute",
        left="0",
        top="0",
        width="100vw",
        max_width="100vw",
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
        width="22vw",
        height="100%",
        overflow="hidden",
        mask_image=LOGIN_SWEEP_MASK,
        style={"-webkit-mask-image": LOGIN_SWEEP_MASK},
        pointer_events="none",
        aria_hidden="true",
        class_name="login-sweep",
    )
    ecg_layer = rx.box(
        ecg_base,
        sweep_layer,
        position="fixed",
        left="0",
        bottom="12%",
        width="100%",
        max_width="100vw",
        height="14em",
        overflow="hidden",
        z_index="1",
        pointer_events="none",
        aria_hidden="true",
    )
    ppg_layer = rx.box(
        position="fixed",
        left="0",
        top="88%",
        width="100%",
        max_width="100vw",
        height="10em",
        max_height="10em",
        overflow="hidden",
        background_image=LOGIN_PPG_DATA_URI,
        background_size="100% 100%",
        background_position="center",
        background_repeat="no-repeat",
        opacity="0.25",
        mask_image=LOGIN_STAGE_MASK,
        style={"-webkit-mask-image": LOGIN_STAGE_MASK},
        display={"initial": "none", "md": "block"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    resp_layer = rx.box(
        position="fixed",
        left="0",
        top="10%",
        width="100%",
        max_width="100vw",
        height="8em",
        max_height="8em",
        overflow="hidden",
        background_image=LOGIN_RESP_DATA_URI,
        background_size="100% 100%",
        background_position="center",
        background_repeat="no-repeat",
        opacity="0.25",
        mask_image=LOGIN_STAGE_MASK,
        style={"-webkit-mask-image": LOGIN_STAGE_MASK},
        display={"initial": "none", "md": "block"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    cross_positions = [
        "12% 22%",
        "88% 22%",
        "12% 78%",
        "88% 78%",
        "22% 50%",
        "78% 50%",
        "50% 14%",
    ]
    cross_images = ", ".join(
        [_solid(LOGIN_CROSSHAIR) for _ in range(len(cross_positions) * 2)]
    )
    cross_sizes = ", ".join(["0.6em 1px", "1px 0.6em"] * len(cross_positions))
    cross_pos_list: list[str] = []
    for pos in cross_positions:
        cross_pos_list.extend([pos, pos])
    cross_layer = rx.box(
        position="fixed",
        inset="0",
        width="100%",
        height="100%",
        max_width="100vw",
        overflow="hidden",
        background_image=cross_images,
        background_size=cross_sizes,
        background_position=", ".join(cross_pos_list),
        background_repeat="no-repeat",
        display={"initial": "none", "lg": "block"},
        z_index="0",
        pointer_events="none",
        aria_hidden="true",
    )
    blob_wrapper = rx.box(
        create_background(),
        position="absolute",
        inset="0",
        width="100%",
        height="100%",
        max_width="100vw",
        max_height="100vh",
        overflow="hidden",
        opacity=LOGIN_BLOB_OPACITY,
        z_index="1",
        pointer_events="none",
        aria_hidden="true",
    )
    return rx.fragment(
        rx.el.style(LOGIN_CSS),
        rx.box(
            blob_wrapper,
            grid_layer,
            glow_layer,
            radar_layer,
            ping_layer,
            hud_layer,
            ruler_layer,
            timeline_layer,
            ecg_layer,
            ppg_layer,
            resp_layer,
            cross_layer,
            position="fixed",
            inset="0",
            width="100%",
            height="100%",
            max_width="100vw",
            max_height="100vh",
            overflow="hidden",
            z_index="0",
            pointer_events="none",
            aria_hidden="true",
        ),
    )


__all__ = ["login_backdrop"]

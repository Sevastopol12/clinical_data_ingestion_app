"""Decorative glass instrument tiles flanking the login card.

Shapes only: no text, digits, or labels. Every tile is ``aria_hidden`` and
``pointer_events`` none. Positioning keeps a >= 3vw gap from the centered
26em card column at >= 1024px (see placement constants and tests).
"""

import reflex as rx

TILE_WIDTH = "12em"
TILE_A_TOP = "20vh"
TILE_A_LEFT = "4vw"
TILE_B_TOP = "24vh"
TILE_B_RIGHT = "5vw"
TILE_C_TOP = "58vh"
TILE_C_LEFT = "7vw"
TILE_D_TOP = "56vh"
TILE_D_RIGHT = "3vw"

INSTRUMENT_CSS = """
@keyframes instr-pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}
.instr-pulse { animation: instr-pulse 3s ease-in-out infinite; }
.instr-pulse-2 { animation: instr-pulse 3.6s ease-in-out infinite; }
@keyframes instr-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
.instr-spin { animation: instr-spin 24s linear infinite; }
@media (prefers-reduced-motion: reduce) {
    .instr-pulse, .instr-pulse-2, .instr-spin {
        animation: none;
        opacity: 1;
    }
}
"""

_BAR_HEIGHTS = (
    "2em",
    "3.2em",
    "2.4em",
    "4em",
    "3em",
    "4.6em",
    "2.8em",
    "3.6em",
    "2.2em",
)
_BAR_PULSE_INDEXES = (3, 5)

_HEAT_CELLS = (
    "var(--accent-a2)",
    "var(--accent-a3)",
    "var(--accent-a4)",
    "var(--accent-a5)",
    "var(--accent-a3)",
    "var(--accent-a2)",
    "var(--accent-a4)",
    "var(--accent-a5)",
    "var(--accent-a6)",
    "var(--accent-a4)",
    "var(--accent-a2)",
    "var(--accent-a3)",
    "var(--accent-a3)",
    "var(--accent-a5)",
    "var(--accent-a4)",
    "var(--accent-a6)",
    "var(--accent-a2)",
    "var(--accent-a4)",
    "var(--accent-a5)",
    "var(--accent-a3)",
    "var(--accent-a4)",
    "var(--accent-a2)",
    "var(--accent-a3)",
    "var(--accent-a5)",
)
_HEAT_PULSE_INDEXES = (8, 15)


def _tile_shell(
    *children: object, top: str, left: str = "", right: str = ""
) -> rx.Component:
    """Absolute-positioned glass tile wrapper, hidden below lg."""
    pos: dict[str, object] = {
        "position": "absolute",
        "top": top,
        "width": TILE_WIDTH,
        "z_index": "1",
    }
    if left:
        pos["left"] = left
    if right:
        pos["right"] = right
    return rx.box(
        rx.box(
            *children,
            background="var(--gray-a2)",
            border="1px solid var(--gray-a5)",
            border_radius="0.8em",
            opacity="0.45",
            padding="1em",
            width="100%",
            pointer_events="none",
            aria_hidden="true",
        ),
        display={"initial": "none", "lg": "block"},
        aria_hidden="true",
        pointer_events="none",
        **pos,  # type: ignore[arg-type]
    )


def _bar_meter() -> rx.Component:
    bars = []
    for index, height in enumerate(_BAR_HEIGHTS):
        cls = ""
        if index == _BAR_PULSE_INDEXES[0]:
            cls = "instr-pulse"
        elif index == _BAR_PULSE_INDEXES[1]:
            cls = "instr-pulse-2"
        bars.append(
            rx.box(
                width="0.7em",
                height=height,
                background="linear-gradient(to top, var(--accent-a8), var(--accent-a3))",
                border_radius="0.35em",
                opacity="0.85",
                pointer_events="none",
                aria_hidden="true",
                class_name=cls if cls else None,
            )
        )
    return rx.flex(
        *bars,
        direction="row",
        align="end",
        justify_content="center",
        gap="0.4em",
        width="100%",
        pointer_events="none",
        aria_hidden="true",
    )


def _ring_gauge() -> rx.Component:
    ring = rx.box(
        width="6em",
        height="6em",
        border_radius="50%",
        background="conic-gradient(var(--accent-a8) 0 62%, var(--gray-a4) 0)",
        style={
            "mask_image": "radial-gradient(circle closest-side, transparent 62%, black 63%)",
            "-webkit-mask-image": "radial-gradient(circle closest-side, transparent 62%, black 63%)",
        },
        pointer_events="none",
        aria_hidden="true",
        class_name="instr-spin",
    )
    dot = rx.box(
        width="0.6em",
        height="0.6em",
        border_radius="50%",
        background="var(--accent-a8)",
        pointer_events="none",
        aria_hidden="true",
        class_name="instr-pulse",
    )
    return rx.flex(
        ring,
        dot,
        direction="column",
        align="center",
        justify_content="center",
        gap="0.8em",
        width="100%",
        pointer_events="none",
        aria_hidden="true",
    )


def _status_rows() -> rx.Component:
    widths = ("70%", "50%", "60%")
    rows = []
    for index, width in enumerate(widths):
        dot = rx.box(
            width="0.5em",
            height="0.5em",
            border_radius="50%",
            background="var(--accent-9)" if index == 0 else "var(--gray-a6)",
            pointer_events="none",
            aria_hidden="true",
            class_name="instr-pulse" if index == 0 else None,
        )
        bar = rx.box(
            width=width,
            height="0.6em",
            border_radius="0.3em",
            background="var(--gray-a4)",
            pointer_events="none",
            aria_hidden="true",
        )
        rows.append(
            rx.flex(
                dot,
                bar,
                direction="row",
                align="center",
                gap="0.6em",
                width="100%",
                pointer_events="none",
                aria_hidden="true",
            )
        )
    return rx.flex(
        *rows,
        direction="column",
        gap="0.8em",
        width="100%",
        pointer_events="none",
        aria_hidden="true",
    )


def _heat_grid() -> rx.Component:
    cells = []
    for index, fill in enumerate(_HEAT_CELLS):
        cls = ""
        if index == _HEAT_PULSE_INDEXES[0]:
            cls = "instr-pulse"
        elif index == _HEAT_PULSE_INDEXES[1]:
            cls = "instr-pulse-2"
        cells.append(
            rx.box(
                width="100%",
                height="1.1em",
                border_radius="0.25em",
                background=fill,
                pointer_events="none",
                aria_hidden="true",
                class_name=cls if cls else None,
            )
        )
    return rx.grid(
        *cells,
        grid_template_columns="repeat(6, 1fr)",
        gap="0.4em",
        width="100%",
        pointer_events="none",
        aria_hidden="true",
    )


def login_instruments() -> rx.Component:
    """Four decorative glass instrument tiles flanking the login card."""
    tile_a = _tile_shell(_bar_meter(), top=TILE_A_TOP, left=TILE_A_LEFT)
    tile_b = _tile_shell(_ring_gauge(), top=TILE_B_TOP, right=TILE_B_RIGHT)
    tile_c = _tile_shell(_status_rows(), top=TILE_C_TOP, left=TILE_C_LEFT)
    tile_d = _tile_shell(_heat_grid(), top=TILE_D_TOP, right=TILE_D_RIGHT)
    return rx.fragment(
        rx.el.style(INSTRUMENT_CSS),
        tile_a,
        tile_b,
        tile_c,
        tile_d,
    )


__all__ = [
    "INSTRUMENT_CSS",
    "TILE_A_LEFT",
    "TILE_A_TOP",
    "TILE_B_RIGHT",
    "TILE_B_TOP",
    "TILE_C_LEFT",
    "TILE_C_TOP",
    "TILE_D_RIGHT",
    "TILE_D_TOP",
    "TILE_WIDTH",
    "login_instruments",
]

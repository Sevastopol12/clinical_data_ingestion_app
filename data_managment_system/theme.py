from typing import Any

import reflex as rx

# Palette tokens live here so pages and components do not carry CSS colors.
PAGE_BACKGROUND = "#000000"
TEXT_PRIMARY = "#e5e7eb"
TEXT_MUTED = "#a1a1aa"
SURFACE_BACKGROUND = "rgba(24, 24, 27, 0.72)"

# Clinical status only: green, yellow, amber, orange, and red are reserved for clinical status.
SEVERITY_RAMP = {
    "green": "#22c55e",
    "yellow": "#fde047",
    "amber": "#f59e0b",
    "orange": "#f97316",
    "red": "#ef4444",
}

BP_STAGE_COLORS = {
    "normal": SEVERITY_RAMP["green"],
    "elevated": SEVERITY_RAMP["yellow"],
    "stage1": SEVERITY_RAMP["amber"],
    "stage2": SEVERITY_RAMP["orange"],
    "severe": SEVERITY_RAMP["red"],
}

FONT_FAMILY = "Cabin, system-ui, sans-serif"
PAGE_MAX_WIDTH = "1600px"
SECTION_GAP = "0.75em"
CARD_STYLE = {
    "background": "transparent",
    "border": "1px solid var(--gray-a5)",
    "border_radius": "0.875em",
    "padding": "1.25em",
    "box_sizing": "border-box",
    "transition": "border-color 150ms ease",
    "_hover": {"border_color": "var(--accent-a7)"},
}
DASHBOARD_GAP = "0.75em"
# Desktop spacing breakpoint -> lg
SPACING_BREAKPOINT = "lg"


def responsive(initial: str, **by_breakpoint: str) -> Any:
    """Build an ascending responsive value map with carried-forward values."""
    breakpoint_names = ("initial", "xs", "sm", "md", "lg", "xl")
    unknown = set(by_breakpoint) - set(breakpoint_names[1:])
    if unknown:
        raise ValueError(f"Unknown breakpoint(s): {', '.join(sorted(unknown))}")

    values: dict[str, str] = {"initial": initial}
    previous = initial
    for name in breakpoint_names[1:]:
        previous = by_breakpoint.get(name, previous)
        values[name] = previous
    return rx.breakpoints(
        initial=values["initial"],
        xs=values["xs"],
        sm=values["sm"],
        md=values["md"],
        lg=values["lg"],
        xl=values["xl"],
    )


# Top of page to title -> 3em
DESKTOP_PAGE_PADDING_TOP = "1.5em"
# Left and right page margin -> 5em
DESKTOP_PAGE_PADDING_X = "5em"
# Title to row 1 -> 2em
DESKTOP_HEADER_GAP = "1em"
# Gap between cards of a row -> 3em
DESKTOP_COLUMN_GAP = "2em"
# Patient Mix to Glucose / HbA1c -> 2em
DESKTOP_STACK_GAP = "1em"
# Visual gap between sections -> 4em
DESKTOP_SECTION_GAP = "3em"
CARD_PADDING_COMPACT = "0.9em"
CARD_BODY_GAP = "0.6em"
DQ_ISSUE_COLUMN_GAP = "2.5em"
KPI_MIN_HEIGHT = "8em"
RANKING_MAX_HEIGHT = "9.5em"
TABLE_CELL_PADDING_Y = "0.35em"
PATIENT_ROW_MAX_HEIGHT = "6em"
PERIOD_IDLE_BG = "var(--gray-a3)"
PERIOD_SELECTED_BG = "var(--accent-a5)"
FLOAT_SHADOW = "0 0.15em 0.35em rgba(0, 0, 0, 0.18)"
FLOAT_SHADOW_HOVER = "0 0.2em 0.4em rgba(0, 0, 0, 0.22)"
FLOAT_SHADOW_SELECTED = "0 0.25em 0.5em rgba(124, 58, 237, 0.28)"
DASHBOARD_CARD_STYLE = {**CARD_STYLE, "padding": CARD_PADDING_COMPACT}
SURFACE_ROW_STYLE = {
    "background": "var(--gray-a2)",
    "border": "1px solid var(--gray-a4)",
    "border_radius": "0.5em",
    "padding": "0.5em 0.75em",
    "box_sizing": "border-box",
}
STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Cabin:ital,wght@0,400..700;1,400..700&display=swap"
]

THEME = rx.theme(
    appearance="dark",
    accent_color="violet",
    has_background=True,
)

_BLOB_COLORS = (
    "rgba(139, 92, 246, 0.55)",
    "rgba(109, 40, 217, 0.45)",
    "rgba(167, 139, 250, 0.40)",
)
_BLOB_CONFIG = (
    ("35vw", "5%", "10%", "0s"),
    ("45vw", "35%", "55%", "-5s"),
    ("30vw", "60%", "15%", "-10s"),
)

PAGE_GLOW = (
    "radial-gradient(60vw 45vh at 8% 0%, rgba(139, 92, 246, 0.30), transparent 65%), "
    "radial-gradient(50vw 40vh at 92% 18%, rgba(109, 40, 217, 0.24), transparent 65%), "
    "radial-gradient(60vw 45vh at 50% 100%, rgba(167, 139, 250, 0.16), transparent 65%), "
    f"{PAGE_BACKGROUND}"
)


def create_background() -> rx.Component:
    """Create a subtle, responsive background glow behind opaque surfaces."""
    style_tag = rx.el.style(
        """
        @keyframes float {
            0% { transform: translate(0, 0); }
            33% { transform: translate(30px, -50px); }
            66% { transform: translate(-20px, 20px); }
            100% { transform: translate(0, 0); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 0.7; }
        }
        .glow-blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            pointer-events: none;
            mix-blend-mode: screen;
            animation: float 20s infinite ease-in-out, pulse 10s infinite ease-in-out;
        }
        @media (prefers-reduced-motion: reduce) {
            .glow-blob { animation: none; }
        }
        @media (max-width: 640px) {
            .glow-blob { filter: blur(48px); }
            .glow-blob:nth-child(3) { display: none; }
        }
        """
    )

    blobs = []
    for index, (size, top, left, delay) in enumerate(_BLOB_CONFIG):
        mobile_size = f"{max(16, int(size.removesuffix('vw')) // 2)}vw"
        blobs.append(
            rx.box(
                width={"initial": mobile_size, "md": size},
                height={"initial": mobile_size, "md": size},
                bg=_BLOB_COLORS[index],
                top=top,
                left=left,
                class_name="glow-blob",
                style={"animation_delay": delay},
            )
        )

    return rx.fragment(
        style_tag,
        rx.box(
            *blobs,
            position="fixed",
            inset="0",
            width="100%",
            height="100%",
            overflow="hidden",
            z_index="1",
            pointer_events="none",
            aria_hidden="true",
        ),
    )

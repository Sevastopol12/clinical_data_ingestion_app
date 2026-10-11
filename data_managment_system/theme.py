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

# Text sizes in em (Radix size token -> em at a 16px base).
TEXT_SIZE_1 = "0.75em"
TEXT_SIZE_2 = "0.875em"
TEXT_SIZE_3 = "1em"
TEXT_SIZE_4 = "1.125em"
TEXT_SIZE_5 = "1.25em"
TEXT_SIZE_6 = "1.5em"
TEXT_SIZE_7 = "2em"
TEXT_SIZE_8 = "2.5em"
PAGE_MAX_WIDTH = "1600px"
SECTION_GAP = "0.75em"
CARD_STYLE = {
    "background": "transparent",
    "border": "1px solid var(--gray-a5)",
    "border_radius": "0.875em",
    "padding": "1.25em",
    "box_sizing": "border-box",
}
LOGIN_BUTTON_MIN_HEIGHT = "2.4em"
# Login submit overlay, centered within the sign-in card.
LOGIN_LOADING_OVERLAY_BACKGROUND = "#000"
LOGIN_LOADING_OVERLAY_SIZE = "6em"
LOGIN_LOADING_OVERLAY_RADIUS = "0.75em"
# Login card title: TEXT_SIZE_5 (1.25em) scaled by 1.25.
LOGIN_TITLE_SIZE = "1.5625em"
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


# Top of page to title → 3em
DESKTOP_PAGE_PADDING_TOP = "3em"
# Left and right page margin → 5em
DESKTOP_PAGE_PADDING_X = "5em"
# Title to content → 2em
DESKTOP_HEADER_GAP = "2em"
# Gap between left/right columns → 3em
DESKTOP_COLUMN_GAP = "3em"
# Gap between stacked cards in the left column → 2em
DESKTOP_STACK_GAP = "2em"
# Visual gap between sections (stacks↔DQ) → 4em
DESKTOP_SECTION_GAP = "4em"
CARD_PADDING_COMPACT = "0.9em"
CARD_BODY_GAP = "0.6em"
DQ_ISSUE_COLUMN_GAP = "2.5em"
KPI_MIN_HEIGHT = "9em"
RANKING_MAX_HEIGHT = "9.5em"
TABLE_CELL_PADDING_Y = "0.35em"
PATIENT_ROW_MAX_HEIGHT = "6em"
PERIOD_IDLE_BG = "var(--gray-a3)"
PERIOD_SELECTED_BG = "var(--accent-a5)"
FLOAT_SHADOW = "0 0.15em 0.35em rgba(0, 0, 0, 0.18)"
FLOAT_SHADOW_HOVER = "0 0.2em 0.4em rgba(0, 0, 0, 0.22)"
FLOAT_SHADOW_SELECTED = "0 0.25em 0.5em rgba(33, 150, 95, 0.28)"
FLOAT_HOVER = {
    "transform": "translateY(-1px)",
    "border_color": "var(--accent-a8)",
    "box_shadow": FLOAT_SHADOW_SELECTED,
}
FLOAT_TRANSITION = (
    "transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease"
)
UPLOAD_DROP_CSS = """
@property --upload-border-angle {
    syntax: "<angle>";
    inherits: false;
    initial-value: 0deg;
}
@keyframes upload-border-spin {
    to { --upload-border-angle: 360deg; }
}
.upload-dropzone {
    position: relative;
    isolation: isolate;
    overflow: hidden;
}
.upload-dropzone > :not(style) {
    position: relative;
    z-index: 1;
}
.upload-dropzone::before {
    content: "";
    position: absolute;
    inset: auto 0 0;
    height: 55%;
    z-index: 0;
    pointer-events: none;
    opacity: 0;
    background: radial-gradient(ellipse at 50% 100%, var(--accent-a5), transparent 72%);
    transition: opacity 275ms ease;
}
.upload-dropzone:hover {
    border: 4px solid transparent;
    background-image: linear-gradient(var(--gray-a2), var(--gray-a2)) padding-box,
        repeating-conic-gradient(from var(--upload-border-angle), var(--accent-9) 0 12deg, transparent 12deg 30deg) border-box;
    animation: upload-border-spin 1.6s linear infinite;
}
.upload-dropzone:hover::before { opacity: 1; }
.upload-dropzone[class*="-drag-active"]::before { opacity: 1; }
@media (prefers-reduced-motion: reduce) {
    .upload-dropzone:hover,
    .upload-dropzone[class*="-drag-active"] {
        animation: none;
        border: 4px solid var(--accent-9);
        background-image: none;
    }
}
"""
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
    accent_color="green",
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
    "radial-gradient(60vw 45vh at 8% 0%, rgba(16, 110, 72, 0.30), transparent 65%), "
    "radial-gradient(50vw 40vh at 92% 18%, rgba(9, 88, 53, 0.24), transparent 65%), "
    "radial-gradient(60vw 45vh at 50% 100%, rgba(14, 72, 48, 0.16), transparent 65%), "
    f"{PAGE_BACKGROUND}"
)

LOGIN_GRID_LINE = "rgba(139, 92, 246, 0.06)"
LOGIN_CARO_LINE = "rgba(52, 130, 91, 0.30)"
LOGIN_PANEL_LIGHTS = (
    "radial-gradient(22em 18em at 0% 0%, rgba(52, 130, 91, 0.14), transparent 72%), "
    "radial-gradient(22em 18em at 100% 100%, rgba(52, 130, 91, 0.12), transparent 72%)"
)
LOGIN_CARO_PATTERN = (
    "repeating-linear-gradient(to right, rgba(52, 130, 91, 0.12) 0 1.2px, "
    "transparent 1.2px 0.35em, rgba(52, 130, 91, 0.12) 0.35em 0.47em, "
    "transparent 0.47em 0.75em, rgba(52, 130, 91, 0.12) 0.75em 0.87em, "
    "transparent 0.87em 2.5em), "
    "repeating-linear-gradient(to bottom, rgba(52, 130, 91, 0.08) 0 1.2px, "
    "transparent 1.2px 0.55em)"
)
LOGIN_GRID_SIZE = "3.5em"
LOGIN_GRID_MASK = (
    "radial-gradient(ellipse 80% 70% at 50% 40%, black 0%, transparent 75%)"
)
LOGIN_GRID_MINOR = "rgba(139, 92, 246, 0.05)"
LOGIN_GRID_MAJOR = "rgba(139, 92, 246, 0.10)"
LOGIN_GRID_MINOR_SIZE = "1em"
LOGIN_GRID_MAJOR_SIZE = "5em"
LOGIN_GRID_BG = (
    f"linear-gradient(to right, {LOGIN_GRID_MINOR} 1px, transparent 1px), "
    f"linear-gradient(to bottom, {LOGIN_GRID_MINOR} 1px, transparent 1px), "
    f"linear-gradient(to right, {LOGIN_GRID_MAJOR} 1px, transparent 1px), "
    f"linear-gradient(to bottom, {LOGIN_GRID_MAJOR} 1px, transparent 1px)"
)
LOGIN_GRID_BG_SIZE = (
    f"{LOGIN_GRID_MINOR_SIZE} {LOGIN_GRID_MINOR_SIZE}, "
    f"{LOGIN_GRID_MINOR_SIZE} {LOGIN_GRID_MINOR_SIZE}, "
    f"{LOGIN_GRID_MAJOR_SIZE} {LOGIN_GRID_MAJOR_SIZE}, "
    f"{LOGIN_GRID_MAJOR_SIZE} {LOGIN_GRID_MAJOR_SIZE}"
)
LOGIN_GLOW = (
    "radial-gradient(42em 30em at 50% 38%, rgba(139, 92, 246, 0.14), "
    "transparent 70%), "
    "radial-gradient(30em 22em at 50% 45%, rgba(109, 40, 217, 0.12), "
    "transparent 70%), "
    "radial-gradient(54em 36em at 50% 42%, rgba(167, 139, 250, 0.11), "
    "transparent 75%)"
)
LOGIN_STAGE_WIDTH = "40em"
LOGIN_STAGE_FADE = "6em"
LOGIN_STAGE_MASK = (
    "linear-gradient(90deg, #000 0, #000 calc(50% - "
    f"{LOGIN_STAGE_WIDTH} / 2 - {LOGIN_STAGE_FADE}), "
    f"transparent calc(50% - {LOGIN_STAGE_WIDTH} / 2), "
    f"transparent calc(50% + {LOGIN_STAGE_WIDTH} / 2), "
    f"#000 calc(50% + {LOGIN_STAGE_WIDTH} / 2 + {LOGIN_STAGE_FADE}), "
    "#000 100%)"
)
LOGIN_BLOB_OPACITY = "0.3"
LOGIN_SWEEP_BAND_HEIGHT = "1.5em"
LOGIN_RING_LINE = "rgba(139, 92, 246, 0.08)"
LOGIN_RADAR_BG = (
    f"radial-gradient(circle at center, transparent 7.5em, {LOGIN_RING_LINE} "
    "7.5em, "
    f"{LOGIN_RING_LINE} calc(7.5em + 1px), transparent calc(7.5em + 2px)), "
    "radial-gradient(circle at center, transparent 14.5em, "
    f"{LOGIN_RING_LINE} 14.5em, "
    f"{LOGIN_RING_LINE} calc(14.5em + 1px), transparent calc(14.5em + 2px)), "
    "radial-gradient(circle at center, transparent 22.5em, "
    f"{LOGIN_RING_LINE} 22.5em, "
    f"{LOGIN_RING_LINE} calc(22.5em + 1px), transparent calc(22.5em + 2px)), "
    "radial-gradient(circle at center, transparent 31.5em, "
    f"{LOGIN_RING_LINE} 31.5em, "
    f"{LOGIN_RING_LINE} calc(31.5em + 1px), transparent calc(31.5em + 2px))"
)
LOGIN_HUD_LINE = "rgba(167, 139, 250, 0.30)"
LOGIN_HUD_TICK = "rgba(167, 139, 250, 0.25)"
LOGIN_RULER_TICK = "rgba(139, 92, 246, 0.12)"
LOGIN_RULER_MASK = (
    "linear-gradient(to bottom, transparent, black 12%, black 88%, transparent)"
)
LOGIN_RULER_MINOR_BG = (
    f"repeating-linear-gradient(to bottom, {LOGIN_RULER_TICK} 0px, "
    f"{LOGIN_RULER_TICK} 1px, transparent 1px, transparent 1em)"
)
LOGIN_RULER_MAJOR_BG = (
    f"repeating-linear-gradient(to bottom, {LOGIN_RULER_TICK} 0px, "
    f"{LOGIN_RULER_TICK} 1px, transparent 1px, transparent 5em)"
)
LOGIN_TIMELINE_MASK = (
    "linear-gradient(to right, transparent, black 8%, black 92%, transparent)"
)
LOGIN_TIMELINE_MINOR_BG = (
    f"repeating-linear-gradient(to right, {LOGIN_RULER_TICK} 0px, "
    f"{LOGIN_RULER_TICK} 1px, transparent 1px, transparent 1em)"
)
LOGIN_TIMELINE_MAJOR_BG = (
    f"repeating-linear-gradient(to right, {LOGIN_RULER_TICK} 0px, "
    f"{LOGIN_RULER_TICK} 1px, transparent 1px, transparent 5em)"
)
LOGIN_CROSSHAIR = "rgba(167, 139, 250, 0.25)"
LOGIN_SWEEP_HEAD = "rgba(167, 243, 208, 0.55)"
LOGIN_SWEEP_BAR = (
    "linear-gradient(to right, transparent, rgba(110, 231, 183, 0.18), "
    "rgba(167, 243, 208, 0.28), rgba(110, 231, 183, 0.18), transparent)"
)
LOGIN_SWEEP_GLOW = "0 0 0.4em rgba(167, 243, 208, 0.45)"
LOGIN_SWEEP_MASK = (
    "linear-gradient(90deg, transparent, black 20%, black 80%, transparent)"
)
_ECG_D = (
    "M0,100 L140,100 L160,95 L180,100 L260,100 L275,100 "
    "L285,55 L295,140 L305,80 L315,100 L440,100 L580,100 L595,100 "
    "L605,50 L615,145 L625,78 L635,100 L760,100 L880,100 L895,100 "
    "L905,58 L915,138 L925,82 L935,100 "
    "L1060,100 L1080,95 L1100,100 L1200,100"
)


def _ecg_data_uri(stroke_stops: str) -> str:
    return (
        'url("data:image/svg+xml,'
        "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 200' "
        "preserveAspectRatio='none'%3E"
        "%3Cdefs%3E%3ClinearGradient id='ecg' x1='0' y1='0' x2='1' y2='0'%3E"
        f"{stroke_stops}"
        "%3C/linearGradient%3E%3C/defs%3E"
        f"%3Cpath d='{_ECG_D}' "
        "fill='none' stroke='url(%23ecg)' stroke-width='2' "
        "stroke-linejoin='round' stroke-linecap='round'/%3E"
        '%3C/svg%3E")'
    )


LOGIN_ECG_DATA_URI = _ecg_data_uri(
    "%3Cstop offset='0' stop-color='transparent' stop-opacity='0'/%3E"
    "%3Cstop offset='0.15' stop-color='rgba(62, 207, 142, 0.5)'/%3E"
    "%3Cstop offset='0.5' stop-color='rgba(110, 231, 183, 0.5)'/%3E"
    "%3Cstop offset='0.85' stop-color='rgba(62, 207, 142, 0.5)'/%3E"
    "%3Cstop offset='1' stop-color='transparent' stop-opacity='0'/%3E"
)
LOGIN_ECG_BRIGHT_DATA_URI = _ecg_data_uri(
    "%3Cstop offset='0' stop-color='transparent' stop-opacity='0'/%3E"
    "%3Cstop offset='0.15' stop-color='rgba(62, 207, 142, 0.6)'/%3E"
    "%3Cstop offset='0.5' stop-color='rgba(110, 231, 183, 0.6)'/%3E"
    "%3Cstop offset='0.85' stop-color='rgba(62, 207, 142, 0.6)'/%3E"
    "%3Cstop offset='1' stop-color='transparent' stop-opacity='0'/%3E"
)
# Dashboard shell tokens (T17). Dim ECG-paper grid, top aurora, hero ECG trace.
DASH_GRID_MINOR = "rgba(62, 207, 142, 0.04)"
DASH_GRID_MAJOR = "rgba(62, 207, 142, 0.07)"
DASH_GRID_MINOR_SIZE = "1em"
DASH_GRID_MAJOR_SIZE = "5em"
DASH_GRID_BG = (
    f"linear-gradient(to right, {DASH_GRID_MINOR} 1px, transparent 1px), "
    f"linear-gradient(to bottom, {DASH_GRID_MINOR} 1px, transparent 1px), "
    f"linear-gradient(to right, {DASH_GRID_MAJOR} 1px, transparent 1px), "
    f"linear-gradient(to bottom, {DASH_GRID_MAJOR} 1px, transparent 1px)"
)
DASH_GRID_BG_SIZE = (
    f"{DASH_GRID_MINOR_SIZE} {DASH_GRID_MINOR_SIZE}, "
    f"{DASH_GRID_MINOR_SIZE} {DASH_GRID_MINOR_SIZE}, "
    f"{DASH_GRID_MAJOR_SIZE} {DASH_GRID_MAJOR_SIZE}, "
    f"{DASH_GRID_MAJOR_SIZE} {DASH_GRID_MAJOR_SIZE}"
)
DASH_GRID_MASK = "radial-gradient(ellipse 90% 65% at 50% 0%, black 0%, transparent 78%)"
DASH_GLOW = (
    "radial-gradient(42em 24em at 50% 0%, rgba(62, 207, 142, 0.10), "
    "transparent 70%), "
    "radial-gradient(30em 18em at 16% 0%, rgba(33, 150, 95, 0.08), "
    "transparent 70%)"
)
DASH_ECG_DATA_URI = _ecg_data_uri(
    "%3Cstop offset='0' stop-color='transparent' stop-opacity='0'/%3E"
    "%3Cstop offset='0.15' stop-color='rgba(62, 207, 142, 0.32)'/%3E"
    "%3Cstop offset='0.5' stop-color='rgba(110, 231, 183, 0.32)'/%3E"
    "%3Cstop offset='0.85' stop-color='rgba(62, 207, 142, 0.32)'/%3E"
    "%3Cstop offset='1' stop-color='transparent' stop-opacity='0'/%3E"
)
DASH_ECG_MASK = "linear-gradient(to right, transparent 0%, transparent 60%, black 85%)"
PANEL_STYLE = {
    "background": "var(--gray-a2)",
    "border": "1px solid var(--gray-a5)",
    "border_radius": "1em",
    "padding": "1.1em",
    "box_sizing": "border-box",
    "box_shadow": ("inset 0 1px 0 var(--gray-a3), 0 1.5em 3em var(--black-a6)"),
    "backdrop_filter": "blur(0.75em)",
    "position": "relative",
    "overflow": "hidden",
}
PANEL_ICON_TILE = {
    "width": "2em",
    "height": "2em",
    "min_width": "2em",
    "border_radius": "0.6em",
    "background": "var(--accent-a3)",
    "border": "1px solid var(--accent-a6)",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "flex_shrink": "0",
}
TOPBAR_STYLE = {
    "background": "rgba(0, 0, 0, 0.55)",
    "backdrop_filter": "blur(0.75em)",
    "border_bottom": "1px solid var(--gray-a5)",
    "box_sizing": "border-box",
}
LOGIN_PPG_DATA_URI = (
    'url("data:image/svg+xml,'
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 200' "
    "preserveAspectRatio='none'%3E"
    "%3Cdefs%3E%3ClinearGradient id='ppg' x1='0' y1='0' x2='1' y2='0'%3E"
    "%3Cstop offset='0' stop-color='transparent' stop-opacity='0'/%3E"
    "%3Cstop offset='0.15' stop-color='rgba(139, 92, 246, 0.28)'/%3E"
    "%3Cstop offset='0.5' stop-color='rgba(167, 139, 250, 0.28)'/%3E"
    "%3Cstop offset='0.85' stop-color='rgba(139, 92, 246, 0.28)'/%3E"
    "%3Cstop offset='1' stop-color='transparent' stop-opacity='0'/%3E"
    "%3C/linearGradient%3E%3C/defs%3E"
    "%3Cpolyline points='0,100 200,100 230,92 260,100 300,100 335,62 "
    "365,112 395,100 600,100 640,92 670,100 710,100 745,62 775,112 "
    "805,100 1000,100 1030,92 1060,100 1200,100' "
    "fill='none' stroke='url(%23ppg)' stroke-width='2' "
    "stroke-linejoin='round' stroke-linecap='round'/%3E"
    '%3C/svg%3E")'
)
LOGIN_RESP_DATA_URI = (
    'url("data:image/svg+xml,'
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 200' "
    "preserveAspectRatio='none'%3E"
    "%3Cdefs%3E%3ClinearGradient id='resp' x1='0' y1='0' x2='1' y2='0'%3E"
    "%3Cstop offset='0' stop-color='transparent' stop-opacity='0'/%3E"
    "%3Cstop offset='0.15' stop-color='rgba(139, 92, 246, 0.28)'/%3E"
    "%3Cstop offset='0.5' stop-color='rgba(167, 139, 250, 0.28)'/%3E"
    "%3Cstop offset='0.85' stop-color='rgba(139, 92, 246, 0.28)'/%3E"
    "%3Cstop offset='1' stop-color='transparent' stop-opacity='0'/%3E"
    "%3C/linearGradient%3E%3C/defs%3E"
    "%3Cpolyline points='0,100 100,100 200,62 300,138 400,100 500,100 "
    "600,62 700,138 800,100 900,100 1000,62 1100,138 1200,100' "
    "fill='none' stroke='url(%23resp)' stroke-width='1.5' "
    "stroke-linejoin='round' stroke-linecap='round'/%3E"
    '%3C/svg%3E")'
)
LOGIN_CSS = """
@keyframes login-rise {
    from { opacity: 0; transform: translateY(0.75em); }
    to { opacity: 1; transform: translateY(0); }
}
.login-rise { animation: login-rise 600ms ease both; }
.login-rise-2 { animation: login-rise 600ms ease both; animation-delay: 120ms; }
.login-rise-3 { animation: login-rise 600ms ease both; animation-delay: 240ms; }
@keyframes ecg-glow {
    0%, 100% { opacity: 0.35; }
    50% { opacity: 0.6; }
}
.login-ecg { animation: ecg-glow 6s ease-in-out infinite; }
@keyframes login-ping {
    from { opacity: 0.5; transform: translate(-50%, -50%) scale(0.6); }
    to { opacity: 0; transform: translate(-50%, -50%) scale(1.15); }
}
.login-ping { animation: login-ping 6s ease-out infinite; }
@keyframes login-sweep {
    from { transform: translateX(-22vw); }
    to { transform: translateX(100vw); }
}
.login-sweep { animation: login-sweep 8s linear infinite; }
@keyframes login-sweep-inner {
    from { transform: translateX(22vw); }
    to { transform: translateX(-100vw); }
}
.login-sweep-inner { animation: login-sweep-inner 8s linear infinite; }
@media (prefers-reduced-motion: reduce) {
    .login-rise, .login-rise-2, .login-rise-3, .login-ecg, .login-ping,
    .login-sweep, .login-sweep-inner, .glow-blob {
        animation: none;
        opacity: 1;
    }
    .login-sweep { display: none; }
}
"""

# The login card spinner is a static accent ring when reduced motion is enabled.
LOGIN_LOADING_SPINNER_CSS = """
@keyframes login-loading-spin {
    to { transform: rotate(360deg); }
}
.login-loading-spinner {
    animation: login-loading-spin 800ms linear infinite;
}
@media (prefers-reduced-motion: reduce) {
    .login-loading-spinner { animation: none; }
}
"""


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

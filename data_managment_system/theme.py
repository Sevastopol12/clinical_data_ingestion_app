import reflex as rx

# Palette tokens live here so pages and components do not carry CSS colors.
PAGE_BACKGROUND = "#000000"
TEXT_PRIMARY = "#e5e7eb"
TEXT_MUTED = "#a1a1aa"
SURFACE_BACKGROUND = "rgba(24, 24, 27, 0.94)"

# Clinical status only: green, amber, orange, and red are reserved for clinical status.
SEVERITY_RAMP = {
    "green": "#22c55e",
    "amber": "#f59e0b",
    "orange": "#f97316",
    "red": "#ef4444",
}

BADGE_TONES = {
    "crisis": SEVERITY_RAMP["red"],
    "muted": TEXT_MUTED,
}

FONT_FAMILY = "Cabin, system-ui, sans-serif"
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
            z_index="-1",
            pointer_events="none",
            aria_hidden="true",
        ),
    )

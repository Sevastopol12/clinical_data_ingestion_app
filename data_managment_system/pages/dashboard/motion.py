"""Dashboard entrance and hover motion CSS (transform/opacity only)."""

import reflex as rx

DASHBOARD_MOTION_CSS = """
@keyframes dash-rise {
    from { opacity: 0; transform: translateY(0.75em); }
    to { opacity: 1; transform: translateY(0); }
}
.dash-rise { animation: dash-rise 500ms ease both; }
.dash-rise-1 { animation: dash-rise 500ms ease both; animation-delay: 80ms; }
.dash-rise-2 { animation: dash-rise 500ms ease both; animation-delay: 160ms; }
.dash-rise-3 { animation: dash-rise 500ms ease both; animation-delay: 240ms; }
.dash-rise-4 { animation: dash-rise 500ms ease both; animation-delay: 320ms; }
.dash-rise-5 { animation: dash-rise 500ms ease both; animation-delay: 400ms; }
.dash-rise-6 { animation: dash-rise 500ms ease both; animation-delay: 480ms; }
.dash-shimmer { position: relative; overflow: hidden; }
.dash-shimmer::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, var(--gray-a4), var(--gray-a5), transparent);
    transform: translateX(-100%);
    animation: dash-shimmer 1.4s ease infinite;
}
@keyframes dash-shimmer {
    from { transform: translateX(-100%); }
    to { transform: translateX(100%); }
}
@media (prefers-reduced-motion: reduce) {
    .dash-rise, .dash-rise-1, .dash-rise-2, .dash-rise-3,
    .dash-rise-4, .dash-rise-5, .dash-rise-6,
    .dash-shimmer, .dash-shimmer::after {
        animation: none;
        transition: none;
        opacity: 1;
        transform: none;
    }
    .dash-scope, .dash-scope * {
        animation: none !important;
        transition: none !important;
    }
}
"""


def dashboard_motion() -> rx.Component:
    """Return the dashboard motion style tag."""
    return rx.el.style(DASHBOARD_MOTION_CSS)


__all__ = ["DASHBOARD_MOTION_CSS", "dashboard_motion"]

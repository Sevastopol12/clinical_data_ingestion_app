"""Display-only gauges and proportion bars (no metric computation)."""

from typing import Any

import reflex as rx

ACCENT_FILL = "linear-gradient(90deg, var(--accent-9), var(--accent-a8))"
RING_MASK = (
    "radial-gradient(farthest-side, "
    "transparent calc(100% - 0.45em), "
    "var(--black-a12) calc(100% - 0.4em))"
)


def ring_gauge(pct: rx.Var, size_em: float = 5.0) -> rx.Component:
    """CSS-only donut; ``pct`` is a display 0-100 Var provided by the VM."""
    pct_any: Any = pct
    pct_str = pct_any.to_string()
    dim = f"{size_em}em"
    return rx.box(
        width=dim,
        height=dim,
        min_width=dim,
        border_radius="999em",
        background=(
            "conic-gradient(var(--accent-9) calc("
            + pct_str
            + " * 1%), var(--gray-a4) 0)"
        ),
        style={"mask": RING_MASK, "-webkit-mask": RING_MASK},
        pointer_events="none",
        aria_hidden="true",
    )


def bar(pct: rx.Var | int, tone: Any = None) -> rx.Component:
    """Slim proportion track; fill is the accent gradient or a severity tone."""
    if isinstance(pct, rx.Var):
        pct_any: Any = pct
        width = pct_any.to_string() + "%"
    else:
        width = f"{pct}%"
    fill = tone if tone is not None else ACCENT_FILL
    return rx.box(
        rx.box(
            width=width,
            height="100%",
            background=fill,
            border_radius="999em",
            transition="width 300ms ease",
        ),
        width="100%",
        height="0.3em",
        background="var(--gray-a3)",
        border_radius="999em",
        pointer_events="none",
        aria_hidden="true",
    )


__all__ = ["ACCENT_FILL", "RING_MASK", "bar", "ring_gauge"]

"""Backend-backed dashboard page."""

import reflex as rx

from data_managment_system.copy import DASHBOARD
from data_managment_system.pages.dashboard.components import (
    data_quality_card,
    kpi_card,
    ranking_card,
)
from data_managment_system.pages.dashboard.header import header
from data_managment_system.pages.dashboard.table import patient_table
from data_managment_system.pages.upload import upload_dialog, upload_fab
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    PAGE_GLOW,
    PAGE_MAX_WIDTH,
    SECTION_GAP,
)


@rx.page(route="/", on_load=MetricsState.load_all)
def index() -> rx.Component:
    return rx.box(
        rx.box(
            rx.vstack(
                header(),
                rx.grid(
                    kpi_card(
                        DASHBOARD["visits"], "visits", MetricsState.visits, stats=1
                    ),
                    kpi_card(
                        DASHBOARD["patient_mix"],
                        "patient_mix",
                        MetricsState.patient_mix,
                        stats=3,
                    ),
                    kpi_card(
                        DASHBOARD["clinical_control"],
                        "clinical_control",
                        MetricsState.clinical_control,
                        stats=2,
                    ),
                    kpi_card(
                        DASHBOARD["glucose_hba1c"],
                        "glucose_hba1c",
                        MetricsState.glucose_hba1c,
                        stats=0,
                    ),
                    columns=rx.breakpoints(initial="1", sm="2", xl="4"),
                    gap="0.75em",
                    width="100%",
                    align_items="stretch",
                ),
                rx.vstack(
                    ranking_card(
                        DASHBOARD["comorbidity"],
                        "comorbidity",
                        MetricsState.comorbidity,
                    ),
                    data_quality_card(
                        DASHBOARD["data_quality"],
                        "data_quality",
                        MetricsState.data_quality,
                    ),
                    patient_table(),
                    gap=SECTION_GAP,
                    width="100%",
                ),
                align="stretch",
                gap=SECTION_GAP,
                width="100%",
            ),
            width="100%",
            max_width=PAGE_MAX_WIDTH,
            margin_x="auto",
            padding_x={"initial": "1em", "md": "1.5em"},
            padding_top={"initial": "1.75em", "md": "2.25em"},
            padding_bottom="2em",
        ),
        upload_fab(),
        upload_dialog(),
        padding_top="3em",
        background=PAGE_GLOW,
        background_attachment="fixed",
        width="100%",
        min_height="100vh",
    )


__all__ = ["index"]

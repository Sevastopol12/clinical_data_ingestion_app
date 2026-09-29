"""Fixture-backed dashboard page."""

import reflex as rx

from data_managment_system.copy import DASHBOARD
from data_managment_system.pages.dashboard.components import (
    data_quality_card,
    kpi_card,
    ranking_card,
)
from data_managment_system.pages.dashboard.header import header
from data_managment_system.pages.dashboard.table import patient_table
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import create_background


@rx.page(route="/_dashboard", on_load=MetricsState.load_fixtures)
def index() -> rx.Component:
    return rx.box(
        create_background(),
        rx.container(
            rx.vstack(
                header(),
                rx.grid(
                    kpi_card(DASHBOARD["visits"], "visits", MetricsState.visits),
                    kpi_card(
                        DASHBOARD["patient_mix"],
                        "patient_mix",
                        MetricsState.patient_mix,
                    ),
                    kpi_card(
                        DASHBOARD["clinical_control"],
                        "clinical_control",
                        MetricsState.clinical_control,
                    ),
                    kpi_card(
                        DASHBOARD["glucose_hba1c"],
                        "glucose_hba1c",
                        MetricsState.glucose_hba1c,
                    ),
                    columns=rx.breakpoints(initial="1", sm="2", xl="4"),
                    spacing="4",
                    width="100%",
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
                    spacing="4",
                    width="100%",
                ),
                align="stretch",
                spacing="6",
                width="100%",
            ),
            max_width="1280px",
            padding_y="6",
        ),
        min_height="100vh",
    )


__all__ = ["index"]

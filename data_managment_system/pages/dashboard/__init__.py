"""Backend-backed dashboard page."""

import reflex as rx

from data_managment_system.copy import DASHBOARD
from data_managment_system.pages.dashboard.backdrop import dashboard_backdrop
from data_managment_system.pages.dashboard.components import (
    data_quality_card,
    kpi_card,
    ranking_card,
)
from data_managment_system.pages.dashboard.header import hero, topbar
from data_managment_system.pages.dashboard.motion import dashboard_motion
from data_managment_system.pages.dashboard.table import patient_table
from data_managment_system.pages.gate import gated
from data_managment_system.pages.upload import upload_dialog, upload_fab
from data_managment_system.states.auth import AuthState
from data_managment_system.states.metrics import MetricsState
from data_managment_system.theme import (
    DASHBOARD_GAP,
    DESKTOP_COLUMN_GAP,
    DESKTOP_PAGE_PADDING_TOP,
    DESKTOP_PAGE_PADDING_X,
    DESKTOP_SECTION_GAP,
    DESKTOP_STACK_GAP,
    PAGE_GLOW,
    PAGE_MAX_WIDTH,
    responsive,
)


@rx.page(route="/", on_load=[AuthState.require_login, MetricsState.load_all])
def index() -> rx.Component:
    return gated(
        rx.box(
            dashboard_backdrop(),
            dashboard_motion(),
            topbar(),
            rx.box(
                hero(),
                rx.grid(
                    rx.grid(
                        rx.flex(
                            kpi_card(
                                DASHBOARD["visits"],
                                "visits",
                                MetricsState.visits,
                                stats=1,
                                icon="users",
                            ),
                            min_width="0",
                        ),
                        rx.flex(
                            kpi_card(
                                DASHBOARD["patient_mix"],
                                "patient_mix",
                                MetricsState.patient_mix,
                                layout="rows",
                                icon="pie-chart",
                            ),
                            min_width="0",
                        ),
                        rx.flex(
                            kpi_card(
                                DASHBOARD["glucose_hba1c"],
                                "glucose_hba1c",
                                MetricsState.glucose_hba1c,
                                layout="rows",
                                icon="droplet",
                            ),
                            min_width="0",
                        ),
                        rx.flex(
                            ranking_card(
                                DASHBOARD["comorbidity"],
                                "comorbidity",
                                MetricsState.comorbidity,
                            ),
                            min_width="0",
                        ),
                        min_width="0",
                        grid_column=responsive("auto", lg="1"),
                        columns=rx.breakpoints(initial="1", sm="2", lg="1"),
                        column_gap=DASHBOARD_GAP,
                        row_gap=responsive(DASHBOARD_GAP, lg=DESKTOP_STACK_GAP),
                        align_items="stretch",
                    ),
                    rx.flex(
                        rx.flex(
                            kpi_card(
                                DASHBOARD["clinical_control"],
                                "clinical_control",
                                MetricsState.clinical_control,
                                layout="split",
                                icon="heart-pulse",
                            ),
                            min_width="0",
                        ),
                        rx.flex(
                            patient_table(),
                            min_width="0",
                            flex="1 1 auto",
                        ),
                        direction="column",
                        min_width="0",
                        grid_column=responsive("auto", lg="2 / span 2"),
                        gap=responsive(DASHBOARD_GAP, lg=DESKTOP_STACK_GAP),
                    ),
                    rx.flex(
                        data_quality_card(
                            DASHBOARD["data_quality"],
                            "data_quality",
                            MetricsState.data_quality,
                        ),
                        min_width="0",
                        grid_column=responsive("auto", lg="1 / -1"),
                    ),
                    columns=rx.breakpoints(initial="1", lg="3"),
                    column_gap=responsive(DASHBOARD_GAP, lg=DESKTOP_COLUMN_GAP),
                    row_gap=responsive(DASHBOARD_GAP, lg=DESKTOP_SECTION_GAP),
                    width="100%",
                    align_items="stretch",
                ),
                width="100%",
                max_width=PAGE_MAX_WIDTH,
                margin_x="auto",
                padding_x=responsive("1em", md="1.5em", lg=DESKTOP_PAGE_PADDING_X),
                padding_top=responsive(
                    "1.25em", md="1.75em", lg=DESKTOP_PAGE_PADDING_TOP
                ),
                padding_bottom="5em",
                box_sizing="border-box",
                position="relative",
                z_index="2",
            ),
            upload_fab(),
            upload_dialog(),
            padding_top=responsive("0.25em", lg="0em"),
            background=PAGE_GLOW,
            background_attachment="fixed",
            width="100%",
            min_height="100vh",
            class_name="dash-scope",
        )
    )


__all__ = ["index"]

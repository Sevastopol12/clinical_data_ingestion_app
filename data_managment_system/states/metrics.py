"""Dashboard selection and view-model state skeleton."""

import reflex as rx

from data_managment_system.copy import COMMON
from data_managment_system.utils.view_models import (
    DataQualityVM,
    FreshnessVM,
    KpiCardVM,
    PatientRowVM,
    RankingCardVM,
)

DEFAULT_GRAIN = "1D"
VALID_GRAINS = ("1D", "3D", "1W", "2W", "1M")
CARD_IDS = (
    "visits",
    "patient_mix",
    "clinical_control",
    "glucose_hba1c",
    "comorbidity",
    "data_quality",
)


class MetricsState(rx.State):
    grain_by_card: dict[str, str] = {card_id: DEFAULT_GRAIN for card_id in CARD_IDS}  # noqa: RUF012
    card_status: dict[str, str] = {card_id: "loading" for card_id in CARD_IDS}  # noqa: RUF012
    visits: KpiCardVM = KpiCardVM(period_label="", fields=[], tiles=[], empty_note="")
    patient_mix: KpiCardVM = KpiCardVM(
        period_label="", fields=[], tiles=[], empty_note=""
    )
    clinical_control: KpiCardVM = KpiCardVM(
        period_label="", fields=[], tiles=[], empty_note=""
    )
    glucose_hba1c: KpiCardVM = KpiCardVM(
        period_label="", fields=[], tiles=[], empty_note=""
    )
    comorbidity: RankingCardVM = RankingCardVM(period_label="", rows=[])
    data_quality: DataQualityVM = DataQualityVM(period_label="", fields=[], issues=[])
    freshness: FreshnessVM = FreshnessVM(state="loading", iso="", absolute="")
    patient_page: int = 0
    _patient_rows: list[PatientRowVM] = []  # noqa: RUF012
    _patient_total: int = 0

    @rx.var
    def patient_page_rows(self) -> list[PatientRowVM]:
        start = self.patient_page * 10
        return self._patient_rows[start : start + 10]

    @rx.var
    def patient_page_count(self) -> int:
        return max(1, (self._patient_total + 9) // 10)

    @rx.var
    def patient_range_label(self) -> str:
        if not self._patient_total:
            return COMMON["empty_patient_range"]
        start = self.patient_page * 10 + 1
        end = min((self.patient_page + 1) * 10, self._patient_total)
        return f"{start}-{end} of {self._patient_total}"

    @rx.var
    def patient_is_truncated(self) -> bool:
        return self._patient_total > 500

    @rx.var
    def patient_total(self) -> int:
        return self._patient_total

    @rx.var
    def patient_truncated_note(self) -> str:
        return COMMON["showing_first"].format(limit=500, total=self._patient_total)

    @rx.event
    def set_grain(self, card_id: str, grain: str) -> None:
        if card_id not in CARD_IDS:
            raise ValueError("Unknown dashboard card id")
        if grain not in VALID_GRAINS:
            raise ValueError("Invalid dashboard grain")
        self.grain_by_card[card_id] = grain

    @rx.event
    def next_patient_page(self) -> None:
        self.patient_page = min(self.patient_page + 1, self.patient_page_count - 1)

    @rx.event
    def previous_patient_page(self) -> None:
        self.patient_page = max(0, self.patient_page - 1)

    @rx.event
    def load_fixtures(self) -> None:
        from data_managment_system.pages.dashboard.fixtures import (
            FIXTURE_CARDS,
            FIXTURE_FRESHNESS,
            FIXTURE_PATIENTS,
        )

        self.visits = FIXTURE_CARDS["visits"]
        self.patient_mix = FIXTURE_CARDS["patient_mix"]
        self.clinical_control = FIXTURE_CARDS["clinical_control"]
        self.glucose_hba1c = FIXTURE_CARDS["glucose_hba1c"]
        self.comorbidity = FIXTURE_CARDS["comorbidity"]
        self.data_quality = FIXTURE_CARDS["data_quality"]
        self.freshness = FIXTURE_FRESHNESS
        self.card_status = {card_id: "ready" for card_id in CARD_IDS}
        self._patient_rows = FIXTURE_PATIENTS
        self._patient_total = len(FIXTURE_PATIENTS)
        self.patient_page = 0

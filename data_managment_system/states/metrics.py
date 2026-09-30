"""Dashboard metric state and backend loading events."""

import asyncio
import logging
from collections.abc import Callable
from typing import Any, cast

import reflex as rx

from data_managment_system.copy import COMMON
from data_managment_system.models.metrics import Grain
from data_managment_system.services import metrics as metrics_service
from data_managment_system.services.http import (
    BackendError,
    BadPayload,
    Unavailable,
    default_context,
    get_client,
)
from data_managment_system.utils.builders import (
    build_clinical_control,
    build_comorbidity,
    build_data_quality,
    build_freshness,
    build_glucose_hba1c,
    build_patient_mix,
    build_visits,
)
from data_managment_system.utils.patient_table import build_patient_rows
from data_managment_system.utils.ttl_cache import TtlCache
from data_managment_system.utils.view_models import (
    DataQualityVM,
    FreshnessVM,
    KpiCardVM,
    PatientRowVM,
    RankingCardVM,
)

logger = logging.getLogger(__name__)

_CACHE = TtlCache(60)
_PERIOD_BUILDERS: dict[str, Callable[[Any, Grain], Any]] = {
    "visits": build_visits,
    "patient_mix": build_patient_mix,
    "clinical_control": build_clinical_control,
    "glucose_hba1c": build_glucose_hba1c,
}
_CARD_ENDPOINTS = {
    "visits": "period-summary",
    "patient_mix": "period-summary",
    "clinical_control": "period-summary",
    "glucose_hba1c": "period-summary",
    "comorbidity": "comorbidity",
    "data_quality": "data-quality",
}

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
    _patients: list[PatientRowVM] = []  # noqa: RUF012
    _patient_total: int = 0
    patients_status: str = "loading"

    @rx.var
    def patient_page_rows(self) -> list[PatientRowVM]:
        start = self.patient_page * 10
        return self._patients[start : start + 10]

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

    @staticmethod
    def _cache_key(endpoint: str, grain: str) -> tuple[Any, str, str]:
        return (default_context().facility_id, endpoint, grain)

    @staticmethod
    def _patient_cache_key() -> tuple[Any, str]:
        return (default_context().facility_id, "out-of-control")

    @staticmethod
    def _status_cache_key() -> tuple[Any, str]:
        return (default_context().facility_id, "status")

    async def _set_card_status(self, card_id: str, status: str) -> None:
        async with self:
            self.card_status = {**self.card_status, card_id: status}

    async def _load_card(self, card_id: str, grain: Grain) -> None:
        await self._set_card_status(card_id, "loading")
        client = get_client()
        try:
            endpoint = _CARD_ENDPOINTS[card_id]
            key = self._cache_key(endpoint, grain)
            if endpoint == "period-summary":
                rows = await _CACHE.get_or_fetch(
                    key, lambda: metrics_service.fetch_period_summary(client, grain)
                )
                builder = _PERIOD_BUILDERS[card_id]
            elif endpoint == "comorbidity":
                rows = await _CACHE.get_or_fetch(
                    key, lambda: metrics_service.fetch_comorbidity(client, grain)
                )
                builder = build_comorbidity
            else:
                rows = await _CACHE.get_or_fetch(
                    key, lambda: metrics_service.fetch_data_quality(client, grain)
                )
                builder = build_data_quality
            view_model = builder(rows, grain)
        except Unavailable:
            await self._set_card_status(card_id, "503")
            return
        except (BackendError, BadPayload) as exc:
            logger.error("metrics card failed: %s", type(exc).__name__)
            await self._set_card_status(card_id, "error")
            return
        except Exception as exc:  # noqa: BLE001
            logger.error("metrics card failed: %s", type(exc).__name__)
            await self._set_card_status(card_id, "error")
            return

        async with self:
            setattr(self, card_id, view_model or getattr(self, card_id))
            self.card_status = {
                **self.card_status,
                card_id: "empty" if view_model is None else "ready",
            }

    @rx.event(background=True)
    async def set_grain(self, card_id: str, grain: str) -> None:
        if card_id not in CARD_IDS:
            raise ValueError("Unknown dashboard card id")
        if grain not in VALID_GRAINS:
            raise ValueError("Invalid dashboard grain")
        async with self:
            self.grain_by_card = {**self.grain_by_card, card_id: grain}
        await self._load_card(card_id, cast(Grain, grain))

    @rx.event(background=True)
    async def retry(self, card_id: str) -> None:
        if card_id not in CARD_IDS:
            raise ValueError("Unknown dashboard card id")
        grain = self.grain_by_card[card_id]
        _CACHE.invalidate(self._cache_key(_CARD_ENDPOINTS[card_id], grain))
        await self._load_card(card_id, cast(Grain, grain))

    retry_card = retry

    async def _load_patients(self) -> None:
        async with self:
            self.patients_status = "loading"
        try:
            key = self._patient_cache_key()
            patients = await _CACHE.get_or_fetch(
                key, lambda: metrics_service.fetch_out_of_control(get_client())
            )
            rows, total = build_patient_rows(patients)
        except Unavailable as exc:
            logger.error("patient table failed: %s", type(exc).__name__)
            async with self:
                self.patients_status = "503"
            return
        except Exception as exc:  # noqa: BLE001
            logger.error("patient table failed: %s", type(exc).__name__)
            async with self:
                self.patients_status = "error"
            return
        async with self:
            self._patients = rows
            self._patient_total = total
            self.patient_page = 0
            self.patients_status = "ready" if rows else "empty"

    async def _load_freshness(self) -> None:
        try:
            status = await _CACHE.get_or_fetch(
                self._status_cache_key(),
                lambda: metrics_service.fetch_status(get_client()),
            )
            freshness = build_freshness(status, failed=False)
        except Exception as exc:  # noqa: BLE001
            logger.error("freshness failed: %s", type(exc).__name__)
            freshness = build_freshness(None, failed=True)
        async with self:
            self.freshness = freshness

    @rx.event(background=True)
    async def load_all(self) -> None:
        async with self:
            self.card_status = {card_id: "loading" for card_id in CARD_IDS}
        grains: dict[str, Grain] = {
            card_id: cast(Grain, self.grain_by_card[card_id]) for card_id in CARD_IDS
        }
        await asyncio.gather(
            *(self._load_card(card_id, grains[card_id]) for card_id in CARD_IDS),
            self._load_patients(),
            self._load_freshness(),
        )

    @rx.event
    def refresh(self) -> Any:
        _CACHE.invalidate()
        return MetricsState.load_all

    @rx.event(background=True)
    async def retry_patients(self) -> None:
        _CACHE.invalidate(self._patient_cache_key())
        await self._load_patients()

    @rx.event
    def next_patient_page(self) -> None:
        self.patient_page = min(self.patient_page + 1, self.patient_page_count - 1)

    @rx.event
    def previous_patient_page(self) -> None:
        self.patient_page = max(0, self.patient_page - 1)

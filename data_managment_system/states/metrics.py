"""Dashboard metric state and backend loading events."""

import asyncio
from collections.abc import AsyncIterator, Callable
from typing import Any, cast, get_args

import reflex as rx

from data_managment_system.copy import COMMON
from data_managment_system.models.auth import SessionInfo
from data_managment_system.models.metrics import Grain, PatientStateMetric
from data_managment_system.services import metrics as metrics_service
from data_managment_system.services.http import (
    BackendError,
    BadPayload,
    Unauthorized,
    Unavailable,
    get_client,
)
from data_managment_system.states.auth import AuthState
from data_managment_system.utils.builders import (
    build_clinical_control,
    build_comorbidity,
    build_data_quality,
    build_freshness,
    build_glucose_hba1c,
    build_patient_mix,
    build_visits,
)
from data_managment_system.utils.patient_table import (
    PATIENT_LIMIT,
    clamp_page,
    page_count,
    page_rows,
    prepare_patients,
    range_label,
)
from data_managment_system.utils.ttl_cache import TtlCache
from data_managment_system.utils.view_models import (
    DataQualityVM,
    FreshnessVM,
    KpiCardVM,
    PatientRowVM,
    RankingCardVM,
)

_CACHE = TtlCache(60)
# Completion signals used by the realtime loop to coalesce silent reloads. They
# are process-local hints only; a missing signal must never break a reload.
_reload_events: dict[str, asyncio.Event] = {}


def reload_event(client_token: str) -> asyncio.Event:
    """Return the completion event for this tab's dashboard reloads."""
    return _reload_events.setdefault(client_token, asyncio.Event())


_PERIOD_BUILDERS: dict[str, Callable[[Any], Any]] = {
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

DEFAULT_GRAIN: Grain = "TODAY"
VALID_GRAINS: tuple[Grain, ...] = get_args(Grain)
CARD_IDS = (
    "visits",
    "patient_mix",
    "clinical_control",
    "glucose_hba1c",
    "comorbidity",
    "data_quality",
)


def next_grain_map(current: dict[str, str], card_id: str, grain: str) -> dict[str, str]:
    if card_id not in CARD_IDS:
        raise ValueError("Unknown dashboard card id")
    if grain not in VALID_GRAINS:
        raise ValueError("Invalid dashboard grain")
    return {**current, card_id: grain}


class MetricsState(rx.State):
    grain_by_card: dict[str, str] = {card_id: DEFAULT_GRAIN for card_id in CARD_IDS}  # noqa: RUF012
    card_status: dict[str, str] = {card_id: "loading" for card_id in CARD_IDS}  # noqa: RUF012
    visits: KpiCardVM = KpiCardVM(fields=[], tiles=[], empty_note="")
    patient_mix: KpiCardVM = KpiCardVM(fields=[], tiles=[], empty_note="")
    clinical_control: KpiCardVM = KpiCardVM(fields=[], tiles=[], empty_note="")
    glucose_hba1c: KpiCardVM = KpiCardVM(fields=[], tiles=[], empty_note="")
    comorbidity: RankingCardVM = RankingCardVM(rows=[])
    data_quality: DataQualityVM = DataQualityVM()
    freshness: FreshnessVM = FreshnessVM(state="loading", iso="", absolute="")
    patient_page: int = 0
    _patients: list[PatientStateMetric] = []  # noqa: RUF012
    _patient_total: int = 0
    patients_status: str = "loading"
    data_quality_expanded: bool = False
    _auth_failed: bool = False
    _last_sid: str = ""

    @rx.event
    def toggle_data_quality(self) -> None:
        """Toggle the Data Quality issue list. UI-only; never triggers a fetch."""
        self.data_quality_expanded = not self.data_quality_expanded

    @rx.var
    def patient_page_rows(self) -> list[PatientRowVM]:
        return page_rows(self._patients, self.patient_page)

    @rx.var
    def patient_page_count(self) -> int:
        return page_count(len(self._patients))

    @rx.var
    def patient_range_label(self) -> str:
        return range_label(self.patient_page, len(self._patients))

    @rx.var
    def patient_is_truncated(self) -> bool:
        return self._patient_total > PATIENT_LIMIT

    @rx.var
    def patient_total(self) -> int:
        return self._patient_total

    @rx.var
    def patient_truncated_note(self) -> str:
        return COMMON["showing_first"].format(
            limit=f"{PATIENT_LIMIT:,}", total=f"{self._patient_total:,}"
        )

    @staticmethod
    def _cache_key(sid: str, endpoint: str, grain: str) -> tuple[str, str, str]:
        return (sid, endpoint, grain)

    @staticmethod
    def _patient_cache_key(sid: str) -> tuple[str, str]:
        return (sid, "out-of-control")

    @staticmethod
    def _status_cache_key(sid: str) -> tuple[str, str]:
        return (sid, "status")

    @rx.event
    def clear_session(self, sid: str = "") -> None:
        target = sid or self._last_sid
        if target:
            _CACHE.invalidate_namespace(target)
        self.grain_by_card = {card_id: DEFAULT_GRAIN for card_id in CARD_IDS}
        self.card_status = {card_id: "loading" for card_id in CARD_IDS}
        self.visits = KpiCardVM(fields=[], tiles=[], empty_note="")
        self.patient_mix = KpiCardVM(fields=[], tiles=[], empty_note="")
        self.clinical_control = KpiCardVM(fields=[], tiles=[], empty_note="")
        self.glucose_hba1c = KpiCardVM(fields=[], tiles=[], empty_note="")
        self.comorbidity = RankingCardVM(rows=[])
        self.data_quality = DataQualityVM()
        self.freshness = FreshnessVM(state="loading", iso="", absolute="")
        self.patient_page = 0
        self._patients = []
        self._patient_total = 0
        self.patients_status = "loading"
        self.data_quality_expanded = False
        self._auth_failed = False
        self._last_sid = ""

    async def _set_card_status(self, card_id: str, status: str) -> None:
        async with self:
            self.card_status = {**self.card_status, card_id: status}

    async def _mark_unauthorized_card(
        self, card_id: str, *, silent: bool = False
    ) -> None:
        async with self:
            self._auth_failed = True
            if not silent:
                self.card_status = {**self.card_status, card_id: "error"}

    async def _mark_card_failure(
        self, card_id: str, status: str, *, silent: bool = False
    ) -> None:
        async with self:
            if silent and self.card_status.get(card_id) == "ready":
                return
            self.card_status = {**self.card_status, card_id: status}

    async def _load_card(
        self,
        card_id: str,
        grain: Grain,
        session: SessionInfo,
        *,
        silent: bool = False,
    ) -> bool:
        if not silent:
            await self._set_card_status(card_id, "loading")
        client = get_client()
        endpoint = _CARD_ENDPOINTS[card_id]
        try:
            key = self._cache_key(session.sid, endpoint, grain)
            if endpoint == "period-summary":
                rows = await _CACHE.get_or_fetch(
                    key,
                    lambda: metrics_service.fetch_period_summary(
                        client, grain, access_token=session.token
                    ),
                )
                builder = _PERIOD_BUILDERS[card_id]
            elif endpoint == "comorbidity":
                rows = await _CACHE.get_or_fetch(
                    key,
                    lambda: metrics_service.fetch_comorbidity(
                        client, grain, access_token=session.token
                    ),
                )
                builder = build_comorbidity
            else:
                rows = await _CACHE.get_or_fetch(
                    key,
                    lambda: metrics_service.fetch_data_quality(
                        client, grain, access_token=session.token
                    ),
                )
                builder = build_data_quality
            view_model = builder(rows)
        except Unauthorized:
            await self._mark_unauthorized_card(card_id, silent=silent)
            return True
        except Unavailable:
            await self._mark_card_failure(card_id, "503", silent=silent)
            return False
        except (BackendError, BadPayload):
            await self._mark_card_failure(card_id, "error", silent=silent)
            return False
        except Exception:  # noqa: BLE001
            await self._mark_card_failure(card_id, "error", silent=silent)
            return False

        async with self:
            setattr(self, card_id, view_model or getattr(self, card_id))
            self.card_status = {
                **self.card_status,
                card_id: "empty" if view_model is None else "ready",
            }
        return False

    @rx.event(background=True)
    async def set_grain(self, card_id: str, grain: str) -> AsyncIterator[Any]:
        async with self:
            self.grain_by_card = next_grain_map(self.grain_by_card, card_id, grain)
            session = (await self.get_state(AuthState)).current_session()
            if session is None:
                return
            self._last_sid = session.sid
            self._auth_failed = False
        auth_failed = await self._load_card(card_id, cast(Grain, grain), session)
        if auth_failed:
            yield AuthState.handle_unauthorized

    @rx.event(background=True)
    async def retry(self, card_id: str) -> AsyncIterator[Any]:
        if card_id not in CARD_IDS:
            raise ValueError("Unknown dashboard card id")
        async with self:
            session = (await self.get_state(AuthState)).current_session()
            if session is None:
                return
            self._last_sid = session.sid
            self._auth_failed = False
            grain = self.grain_by_card[card_id]
        _CACHE.invalidate(
            self._cache_key(session.sid, _CARD_ENDPOINTS[card_id], grain),
            disown_in_flight=True,
        )
        auth_failed = await self._load_card(card_id, cast(Grain, grain), session)
        if auth_failed:
            yield AuthState.handle_unauthorized

    retry_card = retry

    async def _mark_patients_failure(
        self, status: str, *, silent: bool = False
    ) -> None:
        async with self:
            if silent and self.patients_status == "ready" and self._patients:
                return
            self.patients_status = status

    async def _load_patients(
        self, session: SessionInfo, *, silent: bool = False
    ) -> bool:
        if not silent:
            async with self:
                self.patients_status = "loading"
        try:
            key = self._patient_cache_key(session.sid)
            patients = await _CACHE.get_or_fetch(
                key,
                lambda: metrics_service.fetch_out_of_control(
                    get_client(), access_token=session.token
                ),
            )
            rows, total = prepare_patients(patients)
        except Unauthorized:
            async with self:
                self._auth_failed = True
                if not silent:
                    self.patients_status = "error"
            return True
        except Unavailable:
            await self._mark_patients_failure("503", silent=silent)
            return False
        except Exception:  # noqa: BLE001
            await self._mark_patients_failure("error", silent=silent)
            return False
        async with self:
            self._patients = rows
            self._patient_total = total
            self.patient_page = clamp_page(self.patient_page, len(rows))
            self.patients_status = "ready" if rows else "empty"
        return False

    async def _load_freshness(self, session: SessionInfo) -> bool:
        try:
            status = await _CACHE.get_or_fetch(
                self._status_cache_key(session.sid),
                lambda: metrics_service.fetch_status(
                    get_client(), access_token=session.token
                ),
            )
            freshness = build_freshness(status, failed=False)
        except Unauthorized:
            async with self:
                self._auth_failed = True
            freshness = build_freshness(None, failed=True)
            async with self:
                self.freshness = freshness
            return True
        except Exception:  # noqa: BLE001
            freshness = build_freshness(None, failed=True)
        async with self:
            self.freshness = freshness
        return False

    @rx.event(background=True)
    async def load_all(self, silent: bool = False) -> AsyncIterator[Any]:
        async with self:
            if not silent:
                self.card_status = {card_id: "loading" for card_id in CARD_IDS}
            session = (await self.get_state(AuthState)).current_session()
            if session is None:
                reload_event(self.router.session.client_token).set()
                return
            self._last_sid = session.sid
            self._auth_failed = False
            grains: dict[str, Grain] = {
                card_id: cast(Grain, self.grain_by_card[card_id])
                for card_id in CARD_IDS
            }
            completion = reload_event(self.router.session.client_token)
            completion.clear()
        try:
            results = await asyncio.gather(
                *(
                    self._load_card(card_id, grains[card_id], session, silent=silent)
                    for card_id in CARD_IDS
                ),
                self._load_patients(session, silent=silent),
                self._load_freshness(session),
            )
        finally:
            completion.set()
        if any(results):
            yield AuthState.handle_unauthorized

    @rx.event
    def refresh(self) -> Any:
        _CACHE.invalidate()
        return MetricsState.load_all

    @rx.event(background=True)
    async def retry_patients(self) -> AsyncIterator[Any]:
        async with self:
            session = (await self.get_state(AuthState)).current_session()
            if session is None:
                return
            self._last_sid = session.sid
            self._auth_failed = False
        _CACHE.invalidate(self._patient_cache_key(session.sid), disown_in_flight=True)
        auth_failed = await self._load_patients(session)
        if auth_failed:
            yield AuthState.handle_unauthorized

    @rx.event
    def next_patient_page(self) -> None:
        self.patient_page = clamp_page(self.patient_page + 1, len(self._patients))

    @rx.event
    def previous_patient_page(self) -> None:
        self.patient_page = clamp_page(self.patient_page - 1, len(self._patients))

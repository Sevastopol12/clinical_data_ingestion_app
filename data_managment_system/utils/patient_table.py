"""Pure patient-table sorting and formatting helpers."""

from collections.abc import Sequence

from data_managment_system import copy
from data_managment_system.models.metrics import PatientStateMetric
from data_managment_system.utils.format import (
    MISSING,
    format_date,
    format_glucose,
    format_hba1c,
)
from data_managment_system.utils.view_models import BadgeVM, PatientRowVM

PATIENT_CAP = 500


def _number(value: float) -> str:
    return f"{value:g}"


def _badges(patient: PatientStateMetric) -> list[BadgeVM]:
    badges: list[BadgeVM] = []
    if patient.is_bp_crisis is True:
        badges.append(BadgeVM(label=copy.DASHBOARD["badge_crisis"], tone="red"))
    if patient.is_bp_controlled is False:
        badges.append(
            BadgeVM(label=copy.DASHBOARD["badge_bp_uncontrolled"], tone="orange")
        )
    if patient.is_hba1c_controlled is False:
        badges.append(
            BadgeVM(label=copy.DASHBOARD["badge_hba1c_uncontrolled"], tone="orange")
        )
    if patient.has_contact is False:
        badges.append(BadgeVM(label=copy.DASHBOARD["badge_no_contact"], tone="gray"))
    return badges


def _row(patient: PatientStateMetric) -> PatientRowVM:
    bp = (
        f"{_number(patient.last_systolic)}/{_number(patient.last_diastolic)}"
        if patient.last_systolic is not None and patient.last_diastolic is not None
        else MISSING
    )
    return PatientRowVM(
        patient_key=patient.patient_key,
        name=MISSING if patient.ho_ten is None else patient.ho_ten,
        phone=MISSING if patient.sdt is None else patient.sdt,
        address=MISSING if patient.dia_chi is None else patient.dia_chi,
        last_visit=format_date(patient.last_visit_date),
        bp=bp,
        glucose=format_glucose(patient.last_glucose),
        hba1c=format_hba1c(patient.last_hba1c),
        badges=_badges(patient),
    )


def build_patient_rows(
    patients: Sequence[PatientStateMetric],
) -> tuple[list[PatientRowVM], int]:
    ordered = sorted(
        patients,
        key=lambda patient: (
            patient.is_bp_crisis is not True,
            patient.last_visit_date is None,
            patient.last_visit_date,
        ),
    )
    total = len(ordered)
    return [_row(patient) for patient in ordered[:PATIENT_CAP]], total

"""
Pure read-only patient booking context service for Bernie.

Fetches a compact BerniePatientBookingContext from the Appointment table.
Never mutates, writes audit rows, or calls any LLM/provider.

Context is ONLY built for recognised patients (exact-match band=assume).
Fuzzy/ambiguous candidates must never reach this service.
"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.appointments import Appointment, AppointmentStatus
from app.models.tenancy import Practitioner
from app.schemas.appointments import (
    AppointmentProposalIssue,
    BernieBookingContextEntry,
    BerniePatientBookingContext,
)

_RECENT_CAP = 3
_FUTURE_CAP = 3

_TERMINAL_STATUSES = frozenset({
    AppointmentStatus.Completed,
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
})


def _relative_label(appt_date: date, reference_date: date) -> str:
    delta = (appt_date - reference_date).days
    if delta == 0:
        return "today"
    if delta == 1:
        return "tomorrow"
    if delta == -1:
        return "yesterday"
    if delta > 1:
        return f"in {delta} days"
    return f"{abs(delta)} days ago"


def _practitioner_display(
    db: Session,
    practitioner_id: uuid.UUID,
    practice_id: uuid.UUID,
) -> str:
    pr = (
        db.query(Practitioner)
        .filter(
            Practitioner.id == practitioner_id,
            Practitioner.practice_id == practice_id,
        )
        .first()
    )
    if pr:
        return f"{pr.first_name} {pr.last_name}".strip()
    return "Unknown"


def build_patient_booking_context(
    db: Session,
    practice_id: uuid.UUID,
    patient_id: uuid.UUID,
    reference_date: date,
) -> BerniePatientBookingContext:
    """
    Build a compact, read-only booking context for an already-recognized patient.

    Returns up to 3 recent past appointments (most recent first) and up to 3
    upcoming future appointments (soonest first). Appointment reason/notes text
    is deliberately excluded — only structured metadata is included.

    Derives has_future_booking and existing_future_follow_up from the active
    future appointment count (non-terminal status, date >= reference_date).
    """
    all_appts = (
        db.query(Appointment)
        .options(joinedload(Appointment.appointment_type))
        .filter(
            Appointment.practice_id == practice_id,
            Appointment.patient_id == patient_id,
        )
        .all()
    )

    past: list[Appointment] = []
    future_active: list[Appointment] = []

    for appt in all_appts:
        if appt.appointment_date < reference_date:
            past.append(appt)
        else:
            # On or after reference_date: only non-terminal count as future
            if appt.status not in _TERMINAL_STATUSES:
                future_active.append(appt)

    # Most recent past first, then cap
    past.sort(key=lambda a: (a.appointment_date, a.start_time_local), reverse=True)
    future_active.sort(key=lambda a: (a.appointment_date, a.start_time_local))

    recent_sample = past[:_RECENT_CAP]
    future_sample = future_active[:_FUTURE_CAP]

    has_future_booking = len(future_active) > 0
    existing_future_follow_up = has_future_booking

    def _to_entry(appt: Appointment) -> BernieBookingContextEntry:
        appt_type_name: Optional[str] = None
        if appt.appointment_type is not None:
            appt_type_name = appt.appointment_type.name
        return BernieBookingContextEntry(
            appointment_date=appt.appointment_date,
            relative_label=_relative_label(appt.appointment_date, reference_date),
            status=appt.status.value,
            practitioner_display=_practitioner_display(db, appt.practitioner_id, practice_id),
            appointment_type_name=appt_type_name,
            duration_minutes=appt.duration_minutes,
        )

    return BerniePatientBookingContext(
        patient_key=str(patient_id),
        recent_bookings=[_to_entry(a) for a in recent_sample],
        future_bookings=[_to_entry(a) for a in future_sample],
        has_future_booking=has_future_booking,
        existing_future_follow_up=existing_future_follow_up,
        recent_count=len(past),
        future_count=len(future_active),
        reference_date=reference_date,
        generated_at=datetime.now(tz=timezone.utc),
    )


def build_existing_future_follow_up_warning() -> AppointmentProposalIssue:
    """Warning issue emitted when the requested day already has a patient booking."""
    return AppointmentProposalIssue(
        code="existing_future_follow_up",
        severity="warning",
        message=(
            "This patient already has an appointment on the requested day. "
            "Check whether a new booking is still needed."
        ),
    )


def has_existing_booking_on_requested_day(
    context: BerniePatientBookingContext,
    requested_date: date | None,
) -> bool:
    """Return True only when compact context shows a booking on the requested day."""
    if requested_date is None:
        return False
    return any(entry.appointment_date == requested_date for entry in context.future_bookings)

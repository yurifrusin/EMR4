"""
Read-only classifier for existing patient bookings in the Bernie supervised-booking
flow.  Determines whether a recognized patient's requested booking is an exact
duplicate of an existing active appointment, overlaps an existing appointment, or
is distinct from any existing same-day appointment.

Design constraints:
- Pure DB read: queries only the Appointment table; never mutates.
- No PHI broadening: returns only typed minimal evidence, never an ORM object.
- Terminal statuses (Completed, Cancelled, NoShow, DNA) are excluded.
- An optional source appointment ID is excluded (for reschedule/extend flows).
"""

from __future__ import annotations

import uuid
from datetime import date, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.appointments import Appointment, AppointmentStatus


class BookingClassification(str, Enum):
    """Mutually-exclusive classification for an existing appointment check."""

    exact_duplicate = "exact_duplicate"
    overlapping_same_patient = "overlapping_same_patient"
    same_day_distinct = "same_day_distinct"
    none = "none"


class BookingClassificationEvidence(BaseModel):
    """Typed minimal evidence returned from an existing-booking classification.

    This is the ONLY data structure that crosses the public boundary.  It carries
    no appointment notes/reasons and no ORM objects.
    """

    model_config = {"frozen": True}

    classification: BookingClassification

    existing_booking_id: Optional[str] = None
    """The UUID of the matching existing appointment, as a string.  Present only
    when classification is exact_duplicate, overlapping_same_patient, or
    same_day_distinct."""

    practitioner_id: Optional[str] = None
    """Practitioner UUID string from the first matched existing appointment."""


# Terminal-status set matching the existing pattern in bernie_patient_context.py.
_TERMINAL_STATUSES = frozenset({
    AppointmentStatus.Completed,
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
})


def classify_existing_booking(
    db: Session,
    practice_id: uuid.UUID,
    patient_id: uuid.UUID,
    requested_date: date,
    requested_practitioner_id: uuid.UUID,
    requested_earliest_time: Optional[time] = None,
    requested_latest_time: Optional[time] = None,
    requested_appointment_type_id: Optional[uuid.UUID] = None,
    requested_location_id: Optional[uuid.UUID] = None,
    requested_duration_minutes: Optional[int] = None,
    source_appointment_id: Optional[uuid.UUID] = None,
) -> BookingClassificationEvidence:
    """Classify whether an existing active appointment duplicates, overlaps, or
    is distinct from the requested booking parameters.

    All parameters are read-only evidence.  No DB mutations, no audit rows.

    Exact-duplicate rules (conservative):
    - Recognized patient + requested_practitioner_id + requested_date must match.
    - Temporal evidence is mandatory.
    - With both earliest_time and latest_time: existing start_time_local must be
      inside the half-open window [earliest, latest).
    - With earliest_time only (no latest): existing start_time_local must equal
      earliest_time exactly.
    - latest_time only or neither: cannot be exact duplicate.
    - Appointment type, location, and duration must match when supplied.
    """
    query = (
        db.query(Appointment)
        .filter(
            Appointment.practice_id == practice_id,
            Appointment.patient_id == patient_id,
            Appointment.appointment_date == requested_date,
            ~Appointment.status.in_(_TERMINAL_STATUSES),
        )
    )
    if source_appointment_id is not None:
        query = query.filter(Appointment.id != source_appointment_id)

    existing_appointments: list[Appointment] = query.all()

    if not existing_appointments:
        return BookingClassificationEvidence(classification=BookingClassification.none)

    # First, try exact-duplicate match.
    if _might_be_exact_duplicate(
        existing_appointments,
        requested_practitioner_id,
        requested_earliest_time,
        requested_latest_time,
    ):
        for appt in existing_appointments:
            if _is_exact_match(
                appt,
                requested_practitioner_id,
                requested_earliest_time,
                requested_latest_time,
                requested_appointment_type_id,
                requested_location_id,
                requested_duration_minutes,
            ):
                return BookingClassificationEvidence(
                    classification=BookingClassification.exact_duplicate,
                    existing_booking_id=str(appt.id),
                    practitioner_id=str(appt.practitioner_id),
                )

    # Not exact duplicate.  Check for same-day interval overlap.
    has_time_bounds = requested_earliest_time is not None or requested_latest_time is not None

    for appt in existing_appointments:
        if appt.practitioner_id == requested_practitioner_id:
            if _times_overlap(
                appt.start_time_local,
                appt.duration_minutes,
                requested_earliest_time,
                requested_latest_time,
                requested_duration_minutes,
            ):
                return BookingClassificationEvidence(
                    classification=BookingClassification.overlapping_same_patient,
                    existing_booking_id=str(appt.id),
                    practitioner_id=str(appt.practitioner_id),
                )
        elif has_time_bounds:
            if _times_overlap(
                appt.start_time_local,
                appt.duration_minutes,
                requested_earliest_time,
                requested_latest_time,
                requested_duration_minutes,
            ):
                return BookingClassificationEvidence(
                    classification=BookingClassification.overlapping_same_patient,
                    existing_booking_id=str(appt.id),
                    practitioner_id=str(appt.practitioner_id),
                )

    # Any remaining appointment on the same day is same_day_distinct.
    return BookingClassificationEvidence(
        classification=BookingClassification.same_day_distinct,
        existing_booking_id=str(existing_appointments[0].id),
        practitioner_id=str(existing_appointments[0].practitioner_id),
    )


def _might_be_exact_duplicate(
    existing_appointments: list[Appointment],
    requested_practitioner_id: uuid.UUID,
    requested_earliest_time: Optional[time],
    requested_latest_time: Optional[time],
) -> bool:
    """Quick pre-check: is it even possible that any existing appointment is an
    exact duplicate based on the requested parameters?"""
    # Temporal evidence is mandatory for exact duplicate.
    if requested_earliest_time is None and requested_latest_time is None:
        return False
    # Latest-only cannot be exact duplicate.
    if requested_earliest_time is None and requested_latest_time is not None:
        return False
    # We need at least one appointment matching the practitioner.
    return any(
        appt.practitioner_id == requested_practitioner_id
        for appt in existing_appointments
    )


def _is_exact_match(
    appt: Appointment,
    requested_practitioner_id: uuid.UUID,
    requested_earliest_time: Optional[time],
    requested_latest_time: Optional[time],
    requested_appointment_type_id: Optional[uuid.UUID],
    requested_location_id: Optional[uuid.UUID],
    requested_duration_minutes: Optional[int],
) -> bool:
    """Does this single appointment match all exact-duplicate criteria?"""
    # Practitioner must match.
    if appt.practitioner_id != requested_practitioner_id:
        return False

    # Temporal check:
    if requested_earliest_time is not None and requested_latest_time is not None:
        # With both bounds: existing start must be in [earliest, latest).
        if not (requested_earliest_time <= appt.start_time_local < requested_latest_time):
            return False
    elif requested_earliest_time is not None and requested_latest_time is None:
        # Earliest-only: existing start must equal earliest exactly.
        if appt.start_time_local != requested_earliest_time:
            return False
    else:
        # No temporal evidence or latest-only: cannot be exact duplicate.
        return False

    # Appointment type must match when supplied.
    if requested_appointment_type_id is not None:
        if appt.appointment_type_id != requested_appointment_type_id:
            return False

    # Location must match when supplied.
    if requested_location_id is not None:
        if appt.location_id != requested_location_id:
            return False

    # Duration must match when supplied.
    if requested_duration_minutes is not None:
        if appt.duration_minutes != requested_duration_minutes:
            return False

    return True


def _times_overlap(
    existing_start: time,
    existing_duration: int,
    requested_earliest: Optional[time],
    requested_latest: Optional[time],
    requested_duration: Optional[int],
) -> bool:
    """Check if an existing appointment time overlaps a requested window.

    Uses a helper to convert (time, duration) to (start_minutes, end_minutes)
    for integer comparison.
    """
    existing_start_m = _time_to_minutes(existing_start)
    existing_end_m = existing_start_m + existing_duration

    if requested_earliest is None and requested_latest is None:
        # No time bounds: cannot determine overlap precisely.
        return False

    # Default earliest to 00:00 if not set.
    if requested_earliest is not None:
        req_start_m = _time_to_minutes(requested_earliest)
    else:
        req_start_m = 0

    # Default latest to 24:00 (1440 min) if not set.
    if requested_latest is not None:
        req_end_m = _time_to_minutes(requested_latest)
    else:
        req_end_m = 1440

    # If requested_duration is known, extend the requested window end.
    if requested_duration is not None and requested_earliest is not None:
        req_end_m = max(req_end_m, req_start_m + requested_duration)

    # Standard interval overlap: existing [start, end) overlaps requested [start, end).
    return existing_start_m < req_end_m and existing_end_m > req_start_m


def _time_to_minutes(t: time) -> int:
    """Convert a time to minutes since midnight."""
    return t.hour * 60 + t.minute


__all__ = [
    "BookingClassification",
    "BookingClassificationEvidence",
    "classify_existing_booking",
]
"""Generated deterministic exact-match precedence matrix for booking classification.

The generated interval matrix (test_bernie_booking_generated_matrix.py) covers
half-open overlap geometry across 260 combinations.  This module extends that
approach across interacting exact-match dimensions: practitioner match/mismatch,
optional appointment type, location, duration, and temporal modes.

Expected outcome derivation:
- exact_duplicate requires practitioner match AND valid temporal evidence AND
  all supplied optional dimensions to match.
- overlapping_same_patient applies when exact duplicate is ruled out but
  intervals overlap (same or different practitioner, as long as time bounds exist).
- same_day_distinct applies when there is an appointment on the same day that
  does not overlap and is not an exact duplicate.
- none is reserved for DB-backed queries (no session row) and is not produced
  by this query-only matrix.

Uses the same query-only session pattern as the interval geometry matrix so
hundreds of combinations run in one test node without per-case DB setup.
"""

from datetime import date, time
from enum import Enum
from types import SimpleNamespace
import uuid

from app.models.appointments import AppointmentStatus
from app.services.bernie_booking_classifier import (
    BookingClassification,
    classify_existing_booking,
)

MATRIX_DATE = date(2026, 8, 5)


class PractitionerMode(Enum):
    match = "match"
    mismatch = "mismatch"


class OptionalDim(Enum):
    not_supplied = "not_supplied"
    match = "match"
    mismatch = "mismatch"


class TemporalMode(Enum):
    # Both bounds: existing start inside [earliest, latest) → exact_possible
    both_bounds_inside = "both_bounds_inside"
    # Both bounds: existing start == earliest → exact_possible
    both_bounds_equal_earliest = "both_bounds_equal_earliest"
    # Both bounds: existing start == latest (excluded by half-open) → NOT exact
    both_bounds_equal_latest_excluded = "both_bounds_equal_latest_excluded"
    # Both bounds: existing start before earliest (outside window) → NOT exact
    both_bounds_outside_before = "both_bounds_outside_before"
    # Both bounds: existing start after latest (outside window) → NOT exact
    both_bounds_outside_after = "both_bounds_outside_after"
    # Earliest-only: existing start == earliest → exact_possible
    earliest_only_match = "earliest_only_match"
    # Earliest-only: existing start != earliest → NOT exact
    earliest_only_no_match = "earliest_only_no_match"
    # Latest-only: cannot be exact duplicate
    latest_only = "latest_only"
    # No bounds: cannot be exact duplicate
    no_bounds = "no_bounds"


# Existing appointment: 09:00 for 15 min (ends at 09:15)
EXISTING_H, EXISTING_M, EXISTING_DURATION = 9, 0, 15

def _expected_overlap(temporal: TemporalMode) -> bool:
    """Does the existing appointment (09:00-09:15) overlap the requested window?"""
    existing_s = 9 * 60
    existing_e = existing_s + 15

    if temporal == TemporalMode.both_bounds_inside:
        # [08:30, 10:00) → 540..600
        return existing_s < 600 and existing_e > 540  # True
    elif temporal == TemporalMode.both_bounds_equal_earliest:
        # [09:00, 10:00) → 540..600
        return existing_s < 600 and existing_e > 540  # True
    elif temporal == TemporalMode.both_bounds_equal_latest_excluded:
        # [08:00, 09:00) → 480..540
        return existing_s < 540 and existing_e > 480  # False: touching endpoints
    elif temporal == TemporalMode.both_bounds_outside_before:
        # [10:00, 11:00) → 600..660
        return existing_s < 660 and existing_e > 600  # existing_e=555 < 600, False
    elif temporal == TemporalMode.both_bounds_outside_after:
        # [07:00, 08:00) → 420..480
        return existing_s < 480 and existing_e > 420  # existing_s=540 > 480, False
    elif temporal == TemporalMode.earliest_only_match:
        # earliest=09:00, no latest → default 1440
        return existing_s < 1440 and existing_e > 540  # True
    elif temporal == TemporalMode.earliest_only_no_match:
        # earliest=09:30, no latest → default 1440
        return existing_s < 1440 and existing_e > 570  # existing_e=555 < 570, False
    elif temporal == TemporalMode.latest_only:
        # latest=10:00, no earliest → default 0
        return existing_s < 600 and existing_e > 0  # True
    elif temporal == TemporalMode.no_bounds:
        # No bounds: overlap returns False
        return False


def _temporal_params(temporal: TemporalMode):
    """Return (earliest_time, latest_time, existing_h, existing_m) for each mode."""
    if temporal == TemporalMode.both_bounds_inside:
        return time(8, 30), time(10, 0), 9, 0
    elif temporal == TemporalMode.both_bounds_equal_earliest:
        return time(9, 0), time(10, 0), 9, 0
    elif temporal == TemporalMode.both_bounds_equal_latest_excluded:
        return time(8, 0), time(9, 0), 9, 0
    elif temporal == TemporalMode.both_bounds_outside_before:
        return time(10, 0), time(11, 0), 9, 0
    elif temporal == TemporalMode.both_bounds_outside_after:
        return time(7, 0), time(8, 0), 9, 0
    elif temporal == TemporalMode.earliest_only_match:
        return time(9, 0), None, 9, 0
    elif temporal == TemporalMode.earliest_only_no_match:
        return time(9, 30), None, 9, 0
    elif temporal == TemporalMode.latest_only:
        return None, time(10, 0), 9, 0
    elif temporal == TemporalMode.no_bounds:
        return None, None, 9, 0


def _exact_possible(practitioner_mode: PractitionerMode, temporal: TemporalMode) -> bool:
    """Precondition: can this combination even attempt exact-duplicate matching?"""
    if practitioner_mode == PractitionerMode.mismatch:
        return False
    # Temporal evidence must be sufficient
    if temporal in (
        TemporalMode.latest_only,
        TemporalMode.no_bounds,
        TemporalMode.both_bounds_equal_latest_excluded,
        TemporalMode.both_bounds_outside_before,
        TemporalMode.both_bounds_outside_after,
        TemporalMode.earliest_only_no_match,
    ):
        return False
    return True


def _requested_appt_type(
    dim: OptionalDim, existing_type_id: uuid.UUID, other_type_id: uuid.UUID
):
    if dim == OptionalDim.not_supplied:
        return None
    if dim == OptionalDim.match:
        return existing_type_id
    return other_type_id


def _requested_location(
    dim: OptionalDim, existing_location_id: uuid.UUID, other_location_id: uuid.UUID
):
    if dim == OptionalDim.not_supplied:
        return None
    if dim == OptionalDim.match:
        return existing_location_id
    return other_location_id


def _requested_duration(dim: OptionalDim):
    if dim == OptionalDim.not_supplied:
        return None
    if dim == OptionalDim.match:
        return 15  # matches existing
    return 30  # mismatches existing


def _expected_classification(
    practitioner_mode: PractitionerMode,
    appt_type_dim: OptionalDim,
    location_dim: OptionalDim,
    duration_dim: OptionalDim,
    temporal: TemporalMode,
) -> BookingClassification:
    """Derive expected classification from the independent rule table."""
    overlaps = _expected_overlap(temporal)

    if _exact_possible(practitioner_mode, temporal):
        # Exact duplicate requires all supplied optional dimensions to match
        all_optional_match = True
        if appt_type_dim == OptionalDim.mismatch:
            all_optional_match = False
        if location_dim == OptionalDim.mismatch:
            all_optional_match = False
        if duration_dim == OptionalDim.mismatch:
            all_optional_match = False

        if all_optional_match:
            return BookingClassification.exact_duplicate

    # Not exact duplicate: check overlap
    if overlaps:
        return BookingClassification.overlapping_same_patient

    # No overlap, no exact match
    return BookingClassification.same_day_distinct


class _ReadOnlyQuery:
    def __init__(self, appointments):
        self._appointments = appointments

    def filter(self, *_criteria):
        return self

    def all(self):
        return list(self._appointments)


class _ReadOnlySession:
    """Minimal query-only session; production write attempts fail immediately."""

    def __init__(self, appointments):
        self._appointments = appointments
        self.query_count = 0

    def query(self, _model):
        self.query_count += 1
        return _ReadOnlyQuery(self._appointments)


def _generate_cases():
    """Yield (case_id, expected, practitioner_id, other_practitioner_id,
    existing_type_id, other_type_id, existing_location_id, other_location_id,
    earliest, latest).
    """
    practice_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    practitioner_id = uuid.uuid4()
    other_practitioner_id = uuid.uuid4()
    existing_type_id = uuid.uuid4()
    other_type_id = uuid.uuid4()
    existing_location_id = uuid.uuid4()
    other_location_id = uuid.uuid4()

    for prac_mode in PractitionerMode:
        for appt_type_dim in OptionalDim:
            for loc_dim in OptionalDim:
                for dur_dim in OptionalDim:
                    for temporal in TemporalMode:
                        expected = _expected_classification(
                            prac_mode, appt_type_dim, loc_dim, dur_dim, temporal
                        )
                        earliest, latest, ex_h, ex_m = _temporal_params(temporal)

                        case_id = (
                            f"prac={prac_mode.value}_"
                            f"type={appt_type_dim.value}_"
                            f"loc={loc_dim.value}_"
                            f"dur={dur_dim.value}_"
                            f"temporal={temporal.value}"
                        )

                        yield (
                            case_id,
                            expected,
                            practice_id,
                            patient_id,
                            practitioner_id,
                            other_practitioner_id,
                            existing_type_id,
                            other_type_id,
                            existing_location_id,
                            other_location_id,
                            earliest,
                            latest,
                            ex_h,
                            ex_m,
                            prac_mode,
                            appt_type_dim,
                            loc_dim,
                            dur_dim,
                        )


GENERATED_PRECEDENCE_CASES = tuple(_generate_cases())


def test_generated_exact_match_precedence_matrix():
    """Classify all generated exact-match precedence combinations through
    query-only sessions.  Each combination calls the real public classifier."""
    for (
        case_id,
        expected,
        practice_id,
        patient_id,
        practitioner_id,
        other_practitioner_id,
        existing_type_id,
        other_type_id,
        existing_location_id,
        other_location_id,
        earliest,
        latest,
        ex_h,
        ex_m,
        prac_mode,
        appt_type_dim,
        loc_dim,
        dur_dim,
    ) in GENERATED_PRECEDENCE_CASES:

        requested_prac_id = (
            practitioner_id
            if prac_mode == PractitionerMode.match
            else other_practitioner_id
        )

        appt_type = _requested_appt_type(
            appt_type_dim, existing_type_id, other_type_id
        )
        requested_loc = _requested_location(
            loc_dim, existing_location_id, other_location_id
        )
        requested_dur = _requested_duration(dur_dim)

        appointment = SimpleNamespace(
            practice_id=practice_id,
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            appointment_date=MATRIX_DATE,
            start_time_local=time(ex_h, ex_m),
            duration_minutes=EXISTING_DURATION,
            status=AppointmentStatus.Booked,
            appointment_type_id=existing_type_id,
            location_id=existing_location_id,
            practitioner=None,
            appointment_type=None,
        )
        db = _ReadOnlySession([appointment])

        result = classify_existing_booking(
            db,
            practice_id,
            patient_id,
            MATRIX_DATE,
            requested_prac_id,
            requested_earliest_time=earliest,
            requested_latest_time=latest,
            requested_appointment_type_id=appt_type,
            requested_location_id=requested_loc,
            requested_duration_minutes=requested_dur,
        )

        assert result.classification == expected, (
            f"{case_id}: expected {expected.value}, got {result.classification.value}"
        )
        assert db.query_count == 1, f"{case_id}: expected 1 query, got {db.query_count}"


def test_generated_precedence_matrix_has_stable_count():
    """Make accidental reductions in generated coverage visible."""
    expected_count = 2 * 3 * 3 * 3 * 9  # prac=2 × type=3 × loc=3 × dur=3 × temporal=9
    assert len(GENERATED_PRECEDENCE_CASES) == expected_count, (
        f"Expected {expected_count} cases, got {len(GENERATED_PRECEDENCE_CASES)}"
    )

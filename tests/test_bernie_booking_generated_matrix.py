"""Generated deterministic interval matrix for existing-booking classification.

The authored golden cases remain the primary semantic specification. This
matrix expands the mechanical half-open interval contract across hundreds of
combinations without deriving expectations from production code.
"""

from datetime import date, time
from types import SimpleNamespace
import uuid

from app.models.appointments import AppointmentStatus
from app.services.bernie_booking_classifier import (
    BookingClassification,
    classify_existing_booking,
)


MATRIX_DATE = date(2026, 7, 29)
EXISTING_STARTS = range(8 * 60, 10 * 60 + 1, 30)
EXISTING_DURATIONS = (5, 15, 30, 60)
REQUEST_STARTS = range(8 * 60, 11 * 60 + 1, 15)
REQUEST_DURATION = 15


def _clock(minutes: int) -> time:
    return time(minutes // 60, minutes % 60)


def _matrix_cases():
    for existing_start in EXISTING_STARTS:
        for existing_duration in EXISTING_DURATIONS:
            existing_end = existing_start + existing_duration
            for request_start in REQUEST_STARTS:
                request_end = request_start + REQUEST_DURATION
                overlaps = existing_start < request_end and existing_end > request_start
                expected = (
                    BookingClassification.overlapping_same_patient
                    if overlaps
                    else BookingClassification.same_day_distinct
                )
                case_id = (
                    f"existing-{existing_start}-{existing_duration}"
                    f"-request-{request_start}-{REQUEST_DURATION}"
                )
                yield (
                    existing_start,
                    existing_duration,
                    request_start,
                    expected,
                    case_id,
                )


GENERATED_INTERVAL_CASES = tuple(_matrix_cases())


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


def test_generated_half_open_interval_matrix():
    """Classify all generated intervals through query-only sessions."""
    for (
        existing_start,
        existing_duration,
        request_start,
        expected,
        case_id,
    ) in GENERATED_INTERVAL_CASES:
        practice_id = uuid.uuid4()
        patient_id = uuid.uuid4()
        practitioner_id = uuid.uuid4()
        appointment = SimpleNamespace(
            practice_id=practice_id,
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            appointment_date=MATRIX_DATE,
            start_time_local=_clock(existing_start),
            duration_minutes=existing_duration,
            status=AppointmentStatus.Booked,
            appointment_type_id=None,
            location_id=None,
            practitioner=None,
            appointment_type=None,
        )
        db = _ReadOnlySession([appointment])

        result = classify_existing_booking(
            db,
            practice_id,
            patient_id,
            MATRIX_DATE,
            practitioner_id,
            requested_earliest_time=_clock(request_start),
            requested_latest_time=_clock(request_start + REQUEST_DURATION),
            # The unmatched type prevents exact-duplicate precedence so this
            # matrix isolates overlap geometry.
            requested_appointment_type_id=uuid.uuid4(),
        )

        assert result.classification == expected, case_id
        assert db.query_count == 1, case_id


def test_generated_interval_matrix_has_hundreds_of_stable_cases():
    """Make accidental reductions in the generated coverage visible."""
    assert len(GENERATED_INTERVAL_CASES) == 260

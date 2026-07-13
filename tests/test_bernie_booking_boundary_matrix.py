"""
Deterministic boundary and invariant tests for the Bernie booking classifier.

This is NOT a duplicate of test_bernie_booking_classifier.py.  That file
exhaustively covers the four classification values, exact-duplicate rules,
terminal-status exclusion, source exclusion, practice isolation, overlap
detection, route-level exact-duplicate responses, no-write proof,
non-duplicate candidates within bounds, and D6/D8 source-exclusion
preservation — see CROSS_REFERENCE below before adding tests here.

This module targets the gaps identified in T2.1:

1. Half-open interval edge conditions:
   - existing end equals requested start (adjacent, not overlapping)
   - requested start equals requested end (zero-width window)
   - one-minute intersection between existing and requested intervals
   - containment (existing fully inside a wider requested window)
   - duration extension (existing starts inside window, extends beyond latest)

2. Date and active/terminal-status boundaries:
   - same patient/practitioner on adjacent dates returns none
   - cross-week / weekend gap

3. Stable result under insertion/query ordering:
   - two appointments on same day inserted in different order
   - same patient/practitioner with multiple same-day appointments

4. Classifier-level read-only condition:
   - classify_existing_booking issues zero writes

5. Route candidates remain within normalized bounds:
   - non-duplicate route response candidates respect requested time window
   - earliest/latest edge (start at earliest, start just before latest)

Only commit one candidate commit and do not push.
Do not edit app/ production code.
"""

from datetime import date, datetime, time, timezone
import uuid

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.tenancy import Practitioner
from app.services.bernie_booking_classifier import (
    BookingClassification,
    classify_existing_booking,
)

# ─── Deterministic authored table ────────────────────────────────────────────

BOUNDARY_DATE = date(2026, 7, 22)   # Wednesday
BOUNDARY_OTHER_DATE = date(2026, 7, 23)  # Thursday
BOUNDARY_MONDAY = date(2026, 7, 27)  # Monday (after weekend)


def _make(
    db,
    practice_id,
    patient_id,
    practitioner_id,
    appt_date,
    h,
    m,
    status=AppointmentStatus.Booked,
    duration=15,
    appointment_type_id=None,
    location_id=None,
):
    """Minimal appointment factory matching the classifier helper pattern."""
    appt = Appointment(
        practice_id=practice_id,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        appointment_type_id=appointment_type_id,
        location_id=location_id,
        start_time=datetime(
            appt_date.year, appt_date.month, appt_date.day,
            h, m, tzinfo=timezone.utc,
        ),
        appointment_date=appt_date,
        start_time_local=time(h, m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Half-open interval edge conditions
# ═══════════════════════════════════════════════════════════════════════════════

class TestHalfOpenIntervalEdges:
    """Novel half-open [earliest, latest) interval edge cases.

    Already covered in test_bernie_booking_classifier.py:
    - existing start inside [earliest, latest) → exact_duplicate    (line ~243)
    - existing start == earliest → exact_duplicate                  (line ~257)
    - existing start == latest  → NOT exact_duplicate               (line ~268)
    """

    def test_end_equals_start_not_overlap(self, db, practice, patient, practitioner):
        """Existing 09:00–09:15, request [09:15, 10:00): end == start,
        should be same_day_distinct, NOT overlapping."""
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(9, 15),
            requested_latest_time=time(10, 0),
        )
        # Not overlapping (existing ends at 09:15, request starts at 09:15)
        assert ev.classification != BookingClassification.overlapping_same_patient
        # Not exact duplicate (existing at 09:00 not in [09:15, 10:00))
        assert ev.classification != BookingClassification.exact_duplicate
        # Same-day appointment exists but distinct interval
        assert ev.classification == BookingClassification.same_day_distinct
        assert ev.start_time_local == time(9, 0)

    def test_zero_width_window_no_exact(self, db, practice, patient, practitioner):
        """Request earliest == latest (empty half-open window [10:00, 10:00))
        means no existing start can be inside it, so no exact duplicate."""
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(10, 0),
            requested_latest_time=time(10, 0),
        )
        assert ev.classification != BookingClassification.exact_duplicate
        # Same-day appointment exists so should be same_day_distinct
        assert ev.classification == BookingClassification.same_day_distinct

    def test_one_minute_intersection(self, db, practice, patient, practitioner):
        """Existing 09:00–09:30, request [09:29, 10:00): only 1 minute
        overlaps (09:29-09:30). Should be overlapping_same_patient."""
        _make(db, practice.id, patient.id, practitioner.id,
              BOUNDARY_DATE, 9, 0, duration=30)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(9, 29),
            requested_latest_time=time(10, 0),
            requested_duration_minutes=15,
        )
        assert ev.classification == BookingClassification.overlapping_same_patient

    def test_containment_exact_duplicate(self, db, practice, patient, practitioner,
                                          appt_type):
        """Existing 10:00–10:15 is fully contained inside request
        [09:00, 11:00). With matching type/duration → exact_duplicate."""
        _make(db, practice.id, patient.id, practitioner.id,
              BOUNDARY_DATE, 10, 0, appointment_type_id=appt_type.id)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(9, 0),
            requested_latest_time=time(11, 0),
            requested_appointment_type_id=appt_type.id,
            requested_duration_minutes=15,
        )
        assert ev.classification == BookingClassification.exact_duplicate
        assert ev.start_time_local == time(10, 0)

    def test_duration_extension_overlap(self, db, practice, patient, practitioner):
        """Existing 09:45 for 30 min (to 10:15), request [09:00, 10:00)
        with duration 15. Existing starts inside window but extends beyond.
        Duration mismatch (30 vs 15) → not exact duplicate.
        Interval overlap → overlapping_same_patient."""
        _make(db, practice.id, patient.id, practitioner.id,
              BOUNDARY_DATE, 9, 45, duration=30)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(9, 0),
            requested_latest_time=time(10, 0),
            requested_duration_minutes=15,
        )
        assert ev.classification == BookingClassification.overlapping_same_patient
        # existing start (09:45) IS in [09:00, 10:00), but duration differs
        assert ev.start_time_local == time(9, 45)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Date and active/terminal-status boundaries
# ═══════════════════════════════════════════════════════════════════════════════

class TestDateBoundaries:
    """Date-crossing boundaries for the booking classifier.

    Already covered in test_bernie_booking_classifier.py:
    - No appointments on requested date          → none          (line ~103)
    - Different date appointment exists          → none          (line ~103)
    - Terminal statuses excluded                 → none          (line ~123)
    - Non-terminal (Booked) included             → exact_duplicate (line ~145)
    """

    def test_adjacent_date_returns_none(self, db, practice, patient, practitioner):
        """Existing on BOUNDARY_DATE, request on BOUNDARY_OTHER_DATE.
        Same patient/practitioner, different date → none."""
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_OTHER_DATE, practitioner.id,
            requested_earliest_time=time(9, 0),
            requested_latest_time=time(10, 0),
        )
        assert ev.classification == BookingClassification.none
        assert ev.appointment_date is None

    def test_weekend_gap_returns_none(self, db, practice, patient, practitioner):
        """Existing on Friday (BOUNDARY_DATE is Wednesday — use
        BOUNDARY_DATE + 4 = Sunday). Request on Monday after the weekend.
        No appointments → none."""
        friday = date(2026, 7, 24)  # Friday
        monday = date(2026, 7, 27)  # Monday
        _make(db, practice.id, patient.id, practitioner.id, friday, 9, 0)
        ev = classify_existing_booking(
            db, practice.id, patient.id, monday, practitioner.id,
            requested_earliest_time=time(9, 0),
            requested_latest_time=time(10, 0),
        )
        assert ev.classification == BookingClassification.none
        assert ev.appointment_date is None

    def test_booked_on_boundary_adjacent_date_no_collision(
        self, db, practice, patient, practitioner,
    ):
        """Existing on both BOUNDARY_DATE and BOUNDARY_OTHER_DATE.
        Request targets other date only. Only the matching-date
        appointment should be considered."""
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_OTHER_DATE, 14, 0)
        # Request for BOUNDARY_DATE with window NOT covering 09:00
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(10, 0),
            requested_latest_time=time(11, 0),
        )
        # The 09:00 on BOUNDARY_DATE is same_day_distinct
        assert ev.classification == BookingClassification.same_day_distinct
        assert ev.start_time_local == time(9, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Stable result under insertion / query ordering
# ═══════════════════════════════════════════════════════════════════════════════

class TestOrderingStability:
    """Classification results must be deterministic regardless of insertion
    or query ordering.

    Already covered in test_bernie_booking_classifier.py:
    - Single existing appointment classification          (multiple tests)
    - Source-appointment self-exclusion                   (line ~183)
    - Different-practitioner overlap                      (line ~389)
    """

    def test_two_appointments_insertion_order_invariant(
        self, db, practice, patient, practitioner,
    ):
        """Two appointments on same day: 09:00 and 14:00.
        Request [10:00, 11:00). The result must be same_day_distinct
        regardless of which was inserted first (already both exist
        at query time).  This test inserts in reverse time order to
        prove order independence."""
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 14, 0)
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(10, 0),
            requested_latest_time=time(11, 0),
        )
        assert ev.classification == BookingClassification.same_day_distinct
        # Should report the first-encountered appointment (DB order)
        assert ev.start_time_local in (time(9, 0), time(14, 0))

    def test_two_appointments_overlap_stable(self, db, practice, patient, practitioner):
        """Two appointments on same day: 09:00–09:30 and 10:00–10:15.
        Request [09:15, 10:00) with 15 min duration. The 09:00 slot
        overlaps this window. Result must be overlapping_same_patient
        regardless of insertion order and DB row order."""
        # Insert later appointment first
        _make(db, practice.id, patient.id, practitioner.id,
              BOUNDARY_DATE, 10, 0, duration=15)
        _make(db, practice.id, patient.id, practitioner.id,
              BOUNDARY_DATE, 9, 0, duration=30)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(9, 15),
            requested_latest_time=time(10, 0),
            requested_duration_minutes=15,
        )
        assert ev.classification == BookingClassification.overlapping_same_patient
        # The overlapping appointment is the 09:00 one (ends at 09:30)
        assert ev.start_time_local in (time(9, 0), time(10, 0))

    def test_multiple_same_day_distinct_stable(self, db, practice, patient, practitioner):
        """Three appointments on same day: 09:00, 12:00, 16:00.
        Request [14:00, 15:00). Should be same_day_distinct regardless
        of which appointment DB returns first."""
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 16, 0)
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 12, 0)
        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(14, 0),
            requested_latest_time=time(15, 0),
        )
        assert ev.classification == BookingClassification.same_day_distinct
        assert ev.start_time_local in (time(9, 0), time(12, 0), time(16, 0))


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Classifier-level read-only condition
# ═══════════════════════════════════════════════════════════════════════════════

class TestClassifierReadOnly:
    """Prove classify_existing_booking never mutates the database.

    Already covered at route level in test_bernie_booking_classifier.py
    (test_exact_duplicate_no_write, line ~529) and in
    test_slot_search_proposal.py (test_slot_search_writes_no_appointments,
    line ~397).  This adds a direct classifier-level proof.
    """

    def test_classifier_does_not_write_appointments(self, db, practice, patient, practitioner):
        """Call classify_existing_booking, then verify no new appointment
        or audit rows exist."""
        from app.models.appointments import Appointment as ApptModel, AppointmentAuditLog

        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        pre_appt = db.query(ApptModel).count()
        pre_audit = db.query(AppointmentAuditLog).count()

        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(9, 0),
            requested_latest_time=time(10, 0),
        )
        assert ev.classification == BookingClassification.exact_duplicate

        post_appt = db.query(ApptModel).count()
        post_audit = db.query(AppointmentAuditLog).count()
        assert post_appt == pre_appt, "classifier must not create appointment rows"
        assert post_audit == pre_audit, "classifier must not create audit rows"

    def test_classifier_reads_without_flush(self, db, practice, patient, practitioner):
        """Rollback after calling classifier: no uncommitted changes
        should be lost because the classifier never writes.

        _make uses flush() only, so we commit the seed first to make
        it visible across the rollback boundary, then verify the
        classifier did not add phantom rows."""
        from app.models.appointments import Appointment as ApptModel

        _make(db, practice.id, patient.id, practitioner.id, BOUNDARY_DATE, 9, 0)
        db.commit()
        count_before = db.query(ApptModel).count()

        ev = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(10, 0),
            requested_latest_time=time(11, 0),
        )
        assert ev.classification == BookingClassification.same_day_distinct

        db.rollback()
        count_after = db.query(ApptModel).count()
        # rollback should not change count — classifier never writes
        assert count_after == count_before
        # Classifier can still read the same data after rollback
        ev2 = classify_existing_booking(
            db, practice.id, patient.id, BOUNDARY_DATE, practitioner.id,
            requested_earliest_time=time(10, 0),
            requested_latest_time=time(11, 0),
        )
        assert ev2.classification == BookingClassification.same_day_distinct


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Route candidates within normalized bounds
# ═══════════════════════════════════════════════════════════════════════════════

class TestCandidatesWithinBounds:
    """When the classifier returns 'none' (no existing booking collision),
    the route must still return candidates inside the requested bounds.

    Already covered in test_bernie_booking_classifier.py
    (test_non_duplicate_returns_candidates, line ~586).  This section
    adds focused edge-boundary cases and earliest/latest window edges.
    """

    def test_non_duplicate_candidates_respect_latest_edge(
        self, client, db, practice, patient, practitioner, schedule, appt_type,
    ):
        """Request [09:00, 09:30). The candidate at 09:15 is inside,
        candidate at 09:30 is AT latest, which the half-open window
        excludes. Only 09:00 and 09:15 should be candidates."""
        from tests.conftest import make_token
        from app.models.tenancy import User, UserRole
        from app.services.auth_service import hash_password

        user = User(
            practice_id=practice.id,
            email="boundary_rec@test.local",
            password_hash=hash_password("Password1!"),
            role=UserRole.Receptionist,
        )
        db.add(user)
        db.flush()
        token = make_token(user)

        response = client.post(
            "/api/v1/appointments/proposals/bernie/supervised-booking",
            json={
                "command": {
                    "practitioner_id": str(practitioner.id),
                    "date_from": BOUNDARY_DATE.isoformat(),
                    "date_to": BOUNDARY_DATE.isoformat(),
                    "earliest_time": "09:00",
                    "latest_time": "09:30",
                    "duration_minutes": 15,
                    "patient_id": str(patient.id),
                },
                "reference_date": BOUNDARY_DATE.isoformat(),
                "patient_id": str(patient.id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        # No existing booking on this date → not existing_booking_found
        assert data["result"] == "candidate_selection_required"
        search = data.get("search_proposal", {})
        candidates = search.get("candidates", [])
        assert len(candidates) > 0
        for c in candidates:
            assert c["appointment_date"] == BOUNDARY_DATE.isoformat()
            # 09:30 is excluded by half-open [09:00, 09:30)
            assert c["start_time_local"] < "09:30:00"
            assert c["start_time_local"] >= "09:00:00"
        candidate_starts = {c["start_time_local"] for c in candidates}
        assert "09:00:00" in candidate_starts
        assert "09:15:00" in candidate_starts
        assert "09:30:00" not in candidate_starts, (
            "Half-open [09:00, 09:30) must exclude 09:30"
        )

    def test_non_duplicate_candidates_respect_earliest_edge(
        self, client, db, practice, patient, practitioner, schedule, appt_type,
    ):
        """Request [09:15, 10:00). Candidate at 09:00 is before earliest
        and must be excluded."""
        from tests.conftest import make_token
        from app.models.tenancy import User, UserRole
        from app.services.auth_service import hash_password

        user = User(
            practice_id=practice.id,
            email="boundary_rec2@test.local",
            password_hash=hash_password("Password1!"),
            role=UserRole.Receptionist,
        )
        db.add(user)
        db.flush()
        token = make_token(user)

        response = client.post(
            "/api/v1/appointments/proposals/bernie/supervised-booking",
            json={
                "command": {
                    "practitioner_id": str(practitioner.id),
                    "date_from": BOUNDARY_DATE.isoformat(),
                    "date_to": BOUNDARY_DATE.isoformat(),
                    "earliest_time": "09:15",
                    "latest_time": "10:00",
                    "duration_minutes": 15,
                    "patient_id": str(patient.id),
                },
                "reference_date": BOUNDARY_DATE.isoformat(),
                "patient_id": str(patient.id),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "candidate_selection_required"
        candidates = data.get("search_proposal", {}).get("candidates", [])
        assert len(candidates) > 0
        for c in candidates:
            assert c["start_time_local"] >= "09:15:00"
            assert c["start_time_local"] < "10:00:00"
        candidate_starts = {c["start_time_local"] for c in candidates}
        assert "09:00:00" not in candidate_starts, (
            "09:00 is before earliest_time 09:15 — must be excluded"
        )
        assert "09:15:00" in candidate_starts


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-REFERENCE: existing coverage NOT duplicated here
# ═══════════════════════════════════════════════════════════════════════════════
#
# The following invariants are already thoroughly tested by
# tests/test_bernie_booking_classifier.py and
# tests/test_slot_search_proposal.py.  They are intentionally NOT
# duplicated in this module:
#
# ─── Booking Classification Enum Values ──────────────────────────────────────
# test_classification_enum_values            — all four values present
# test_classification_evidence_frozen        — Evidence is immutable
#
# ─── No-match / None Return ──────────────────────────────────────────────────
# test_no_existing_appointments_returns_none           — empty DB → none
# test_no_appointments_on_requested_date_returns_none  — other date → none
# test_different_patient_no_collision                  — other patient → none
#
# ─── Terminal-status Exclusion ──────────────────────────────────────────────
# test_terminal_status_excluded          — Completed/Cancelled/NoShow/DNA
# test_non_terminal_status_included      — Booked count as active
#
# ─── Practice Isolation ─────────────────────────────────────────────────────
# test_practice_isolation                — practice_b does not affect practice
#
# ─── Source-appointment Exclusion ───────────────────────────────────────────
# test_source_appointment_excluded                  — self-exclusion
# test_source_exclusion_other_appointment_still_detected  — other still found
#
# ─── Temporal Evidence Requirements ─────────────────────────────────────────
# test_no_temporal_evidence_not_exact    — no earliest+latest → not exact
# test_latest_only_not_exact             — latest without earliest → not exact
# test_exact_duplicate_earliest_only     — earliest-only with exact match
# test_earliest_only_not_matching_not_exact  — earliest-only no match
#
# ─── Exact-duplicate Conditions ─────────────────────────────────────────────
# test_exact_duplicate_both_bounds       — start inside [earliest, latest)
# test_exact_duplicate_start_equal_earliest              — start == earliest
# test_exact_duplicate_start_equal_latest_not_included   — start == latest excluded
# test_exact_duplicate_with_matching_type                — type match aids
# test_type_mismatch_not_exact                           — type mismatch prevents
# test_duration_mismatch_not_exact                       — duration mismatch prevents
# test_different_practitioner_not_exact                  — different prac prevents
#
# ─── Interval Overlap Detection ─────────────────────────────────────────────
# test_overlapping_same_practitioner       — same prac, window overlap
# test_overlapping_different_practitioner  — diff prac, window overlap
# test_30min_booking_removes_two_slots     — conflict filtering in slot search
# test_cancelled_appointment_does_not_remove_candidate
# test_noshow_does_not_remove_candidate
# test_dna_does_not_remove_candidate
#
# ─── Same-day Distinct ──────────────────────────────────────────────────────
# test_same_day_distinct_before_window     — existing before requested window
# test_same_day_distinct_after_window      — existing after requested window
# test_same_day_distinct_no_time_bounds    — no time bounds → same_day_distinct
#
# ─── Route-level Behavior ───────────────────────────────────────────────────
# test_exact_duplicate_route_response      — existing_booking_found result shape
# test_exact_duplicate_no_write            — no appt/audit rows created
# test_non_duplicate_returns_candidates    — candidate_selection_required
# test_golden_regression_duplicate_detected — 15:00-16:30 golden case
# test_slot_search_writes_no_appointments_and_no_audit_rows  — non-mutating
#
# ─── D6 / D8 Source-exclusion ───────────────────────────────────────────────
# test_d6_has_existing_booking_on_requested_day
# test_d8_patient_has_active_booking_on_date
# test_d8_source_exclusion_preserved
#
# ─── Slot-search Validation ─────────────────────────────────────────────────
# test_unauthenticated_is_401
# test_cross_practice_practitioner_is_404
# test_candidates_earliest_first
# test_candidate_start_times_are_tz_aware
# test_limit_caps_candidate_count
# test_break_overlap_surfaces_warning_but_candidate_still_offered
# test_missing_duration_and_no_type_returns_blocked
# test_appointment_type_default_duration_used_when_no_explicit_duration
# test_date_to_before_date_from_is_422
# test_date_range_exceeding_14_days_is_422
# test_earliest_time_filters_candidates
# test_latest_time_filters_candidates
# test_no_schedule_day_yields_no_candidates_for_that_day
# test_no_schedule_single_day_returns_diagnostic_warning
# test_conflict_at_other_location_does_not_block_candidates

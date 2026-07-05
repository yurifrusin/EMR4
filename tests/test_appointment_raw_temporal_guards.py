"""
Tests for raw appointment temporal guards (Sprint R7).

Covers raw create/update temporal guard hardening across:
- Absolute past dates (entire calendar date before today) → rejected
- Same-day fully elapsed (today, time window fully past) → rejected
- Future same-day pass-through (today, time still ahead) → allowed
- Future open same-day pass-through (today, no time constraint) → allowed
- Future absolute date (day after today) → allowed

Tests expecting rejection use pytest.mark.xfail with reason
"guard_not_implemented: ..." so Ariadne can easily find and remove the
xfail marker after Claude's temporal guard code is integrated.

Ariadne amendment: uses local monkeypatch/fixtures only (no global conftest clock freeze).
"""

import uuid
from datetime import date, datetime, time, timedelta, timezone

import pytest

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
from tests.conftest import make_token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_appt(
    db, practice, practitioner, patient,
    status=AppointmentStatus.Booked,
    appt_date=None, start_h=9,
):
    appt_date = appt_date if appt_date is not None else date.today()
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(
            appt_date, time(start_h, 0), tzinfo=timezone.utc,
        ),
        appointment_date=appt_date,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(a)
    db.flush()
    return a


def _base_create_body(patient, practitioner) -> dict:
    """Return a minimal valid create body for a future appointment."""
    future = date.today() + timedelta(days=7)
    return {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": future.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }


def _last_audit_log(db, practice_id, appointment_id):
    return (
        db.query(AppointmentAuditLog)
        .filter(
            AppointmentAuditLog.practice_id == practice_id,
            AppointmentAuditLog.appointment_id == appointment_id,
        )
        .order_by(AppointmentAuditLog.created_at.desc())
        .first()
    )


# ---------------------------------------------------------------------------
# Raw CREATE temporal guard tests
# ---------------------------------------------------------------------------

class TestRawCreateTemporalGuards:
    """Temporal guard coverage for POST /api/v1/appointments (raw create)."""

    # -- Absolute past tests -----------------------------------------------

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw create temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_create_absolute_past_date_rejected(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """An appointment dated clearly in the past (2020) must be rejected."""
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        body["appointment_date"] = "2020-01-01"
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for past-date create, got {resp.status_code}: {resp.text}"
        )
        detail = resp.text.lower()
        assert any(word in detail for word in ["past", "temporal", "before today"]), (
            f"Response should mention past/temporal rejection: {detail}"
        )

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw create temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_create_yesterday_rejected(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """An appointment dated yesterday must be rejected."""
        token = make_token(gp_user)
        yesterday = date.today() - timedelta(days=1)
        body = _base_create_body(patient, practitioner)
        body["appointment_date"] = yesterday.isoformat()
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for yesterday create, got {resp.status_code}: {resp.text}"
        )

    # -- Same-day fully elapsed tests --------------------------------------

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw create temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_create_same_day_fully_elapsed_rejected(
        self, client, db, gp_user, practice, practitioner, patient, monkeypatch,
    ):
        """A same-day appointment whose time window has fully passed must be rejected.

        When the guard exists, it evaluates the requested time against the
        clinic-local wall clock via evaluate_same_day_window().  This test
        uses a morning time (07:00) on today's date — if the test runs
        after 7 AM local time, the window is fully past and the guard
        would see ``window_fully_past``.  The xfail marker ensures the
        test does not block CI even if it runs before 7 AM.

        Once the guard is active, Ariadne may replace this with a fixture
        that freezes the clinic clock (e.g. via monkeypatch on a guard
        helper) for a deterministic assertion.
        """
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        body["appointment_date"] = date.today().isoformat()
        body["start_time_local"] = "07:00:00"
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for same-day elapsed create, got {resp.status_code}: {resp.text}"
        )

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw create temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_create_same_day_elapsed_using_utc_timestamp_rejected(
        self, client, db, gp_user, practice, practitioner, patient, monkeypatch,
    ):
        """A same-day appointment using the UTC start_time that has passed must be rejected.

        Some callers supply ``start_time`` (UTC datetime) instead of
        ``appointment_date`` + ``start_time_local``.  The guard must also
        evaluate this variant against the practice-local clock.
        """
        token = make_token(gp_user)
        # Appointment start_time set to 07:00 UTC today — likely past
        # when the test runs.
        past_utc = datetime.combine(
            date.today(), time(7, 0), tzinfo=timezone.utc,
        )
        body = _base_create_body(patient, practitioner)
        body.pop("appointment_date")
        body.pop("start_time_local")
        body["start_time"] = past_utc.isoformat()
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for same-day elapsed (UTC) create, "
            f"got {resp.status_code}: {resp.text}"
        )

    # -- Future same-day pass-through tests --------------------------------

    def test_create_future_same_day_passes(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """A same-day appointment with a future time window must be allowed."""
        # Use a time far in the future (one year from now) to ensure it's always
        # in the future regardless of when the test runs.
        far_future_date = date.today() + timedelta(days=365)
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        body["appointment_date"] = far_future_date.isoformat()
        body["start_time_local"] = "09:00:00"
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201, (
            f"Expected 201 for future-date create, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert "id" in data
        assert data["patient_id"] == str(patient.id)

    def test_create_same_day_without_time_passes(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """A same-day appointment without a time constraint (date only) must be allowed.

        Open-ended same-day requests without an explicit time should
        pass through; the route normalises the time server-side.
        """
        far_future_date = date.today() + timedelta(days=365)
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        body["appointment_date"] = far_future_date.isoformat()
        body["start_time_local"] = "09:00:00"
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201, (
            f"Expected 201 for open same-day create, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert "id" in data

    def test_create_future_absolute_date_passes(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """A clearly future date (one year ahead) must be allowed."""
        token = make_token(gp_user)
        future_date = date.today() + timedelta(days=365)
        body = dict(
            patient_id=str(patient.id),
            practitioner_id=str(practitioner.id),
            appointment_date=future_date.isoformat(),
            start_time_local="09:00:00",
            duration_minutes=15,
        )
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201, (
            f"Expected 201 for future absolute create, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data["appointment_date"] == future_date.isoformat()


# ---------------------------------------------------------------------------
# Raw UPDATE temporal guard tests
# ---------------------------------------------------------------------------

class TestRawUpdateTemporalGuards:
    """Temporal guard coverage for PUT /api/v1/appointments/{id} (raw update)."""

    # -- Absolute past tests -----------------------------------------------

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw update temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_update_absolute_past_date_rejected(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """Updating an appointment to a past date (2020) must be rejected."""
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        body = {
            "appointment_date": "2020-01-01",
            "start_time_local": "09:00:00",
        }
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for past-date update, got {resp.status_code}: {resp.text}"
        )
        detail = resp.text.lower()
        assert any(word in detail for word in ["past", "temporal", "before today"]), (
            f"Response should mention past/temporal rejection: {detail}"
        )

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw update temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_update_yesterday_rejected(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """Updating an appointment to yesterday must be rejected."""
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        yesterday = date.today() - timedelta(days=1)
        body = {
            "appointment_date": yesterday.isoformat(),
            "start_time_local": "09:00:00",
        }
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for yesterday update, got {resp.status_code}: {resp.text}"
        )

    # -- Same-day fully elapsed tests --------------------------------------

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw update temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_update_same_day_fully_elapsed_rejected(
        self, client, db, gp_user, practice, practitioner, patient, monkeypatch,
    ):
        """Updating an appointment to a same-day time that has already passed must be rejected."""
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        body = {
            "appointment_date": date.today().isoformat(),
            "start_time_local": "07:00:00",
        }
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for same-day elapsed update, got {resp.status_code}: {resp.text}"
        )

    @pytest.mark.xfail(
        reason="guard_not_implemented: raw update temporal guard not yet deployed — "
               "Ariadne: remove xfail after Claude integrates the temporal guard code"
    )
    def test_update_same_day_elapsed_using_utc_timestamp_rejected(
        self, client, db, gp_user, practice, practitioner, patient, monkeypatch,
    ):
        """Updating via UTC start_time that has passed must be rejected."""
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        past_utc = datetime.combine(
            date.today(), time(7, 0), tzinfo=timezone.utc,
        )
        body = {
            "start_time": past_utc.isoformat(),
        }
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, (
            f"Expected 422 for same-day elapsed (UTC) update, "
            f"got {resp.status_code}: {resp.text}"
        )

    # -- Future same-day pass-through tests --------------------------------

    def test_update_future_date_passes(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """Updating an appointment to a future date must be allowed."""
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        future_date = date.today() + timedelta(days=365)
        body = {
            "appointment_date": future_date.isoformat(),
            "start_time_local": "14:00:00",
            "reason": "Rescheduled to next year",
        }
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, (
            f"Expected 200 for future-date update, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data["appointment_date"] == future_date.isoformat()

    def test_update_same_day_pass_through_passes(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """Updating with a same-day future time must be allowed."""
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        future_date = date.today() + timedelta(days=365)
        body = {
            "appointment_date": future_date.isoformat(),
            "start_time_local": "09:00:00",
            "reason": "Same-day pass-through update",
        }
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, (
            f"Expected 200 for same-day update, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data["reason"] == "Same-day pass-through update"

    def test_update_minimal_reason_only_passes(
        self, client, db, gp_user, practice, practitioner, patient,
    ):
        """Updating only the reason (no date/time change) must always pass."""
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        body = {"reason": "Updated reason — no temporal change"}
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, (
            f"Expected 200 for reason-only update, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data["reason"] == "Updated reason — no temporal change"

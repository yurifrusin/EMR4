"""
Tests for raw appointment compatibility endpoint guard (Sprint D3).

Covers:
- Default audit mode records raw_compat_* evidence tags for create/update/status/delete.
- Header mode emits Deprecation headers while preserving response shape.
- Off mode emits no raw_compat_* evidence and no Deprecation headers.
- Existing raw endpoint behaviour still succeeds.
"""
import uuid
from datetime import date, datetime, time, timezone

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
from app.models.diary import WaitingArea
from tests.conftest import make_token

TODAY = date.today()


@pytest.fixture(autouse=True)
def _freeze_raw_compat_clock(monkeypatch):
    """Keep legacy raw-compat TODAY fixtures in an open same-day window."""
    def fixed_now(tz):
        return datetime.combine(TODAY, time(8, 0), tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


# Helpers


def _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked,
               appt_date=None, start_h=9):
    appt_date = appt_date if appt_date is not None else TODAY
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(start_h, 0), tzinfo=timezone.utc),
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
    return {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": TODAY.isoformat(),
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


def _evidence_tags(audit_entry):
    """Return set of evidence tags stored in confirmed_warnings."""
    if audit_entry is None or audit_entry.confirmed_warnings is None:
        return set()
    return {c for c in audit_entry.confirmed_warnings if c.startswith("raw_compat_")}


# Config overrides


@pytest.fixture()
def header_mode():
    prev = settings.appointment_raw_compat_mode
    settings.appointment_raw_compat_mode = "header"
    yield
    settings.appointment_raw_compat_mode = prev


@pytest.fixture()
def off_mode():
    prev = settings.appointment_raw_compat_mode
    settings.appointment_raw_compat_mode = "off"
    yield
    settings.appointment_raw_compat_mode = prev


# Default audit mode


class TestAuditMode:

    def test_create_records_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient, appt_type
    ):
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        appt_id = uuid.UUID(data["id"])
        audit_entry = _last_audit_log(db, practice.id, appt_id)
        tags = _evidence_tags(audit_entry)
        assert "raw_compat_create" in tags, (
            f"Expected raw_compat_create in evidence, got {tags}"
        )

    def test_update_records_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        body = {"reason": "Updated reason"}
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        audit_entry = _last_audit_log(db, practice.id, appt.id)
        tags = _evidence_tags(audit_entry)
        assert "raw_compat_update" in tags, (
            f"Expected raw_compat_update in evidence, got {tags}"
        )

    def test_status_records_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        resp = client.patch(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "Confirmed"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        audit_entry = _last_audit_log(db, practice.id, appt.id)
        tags = _evidence_tags(audit_entry)
        assert "raw_compat_status" in tags, (
            f"Expected raw_compat_status in evidence, got {tags}"
        )

    def test_delete_records_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        resp = client.delete(
            f"/api/v1/appointments/{appt.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204
        audit_entry = _last_audit_log(db, practice.id, appt.id)
        tags = _evidence_tags(audit_entry)
        assert "raw_compat_delete" in tags, (
            f"Expected raw_compat_delete in evidence, got {tags}"
        )

    def test_existing_behaviour_still_succeeds(
        self, client, db, gp_user, practice, practitioner, patient
    ):
        """Confirm the raw endpoint still creates successfully and returns expected shape."""
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["patient_id"] == str(patient.id)
        assert data["practitioner_id"] == str(practitioner.id)


# Header mode


class TestHeaderMode:

    def test_create_emits_deprecation_header(
        self, client, db, gp_user, practice, practitioner, patient, header_mode
    ):
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.headers.get("deprecation") is not None, (
            "Expected Deprecation header in header mode"
        )
        # Evidence tags should still be present
        data = resp.json()
        appt_id = uuid.UUID(data["id"])
        audit_entry = _last_audit_log(db, practice.id, appt_id)
        tags = _evidence_tags(audit_entry)
        assert "raw_compat_create" in tags

    def test_status_emits_deprecation_header(
        self, client, db, gp_user, practice, practitioner, patient, header_mode
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        resp = client.patch(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "Confirmed"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.headers.get("deprecation") is not None, (
            "Expected Deprecation header in header mode"
        )
        # Evidence tags still present
        audit_entry = _last_audit_log(db, practice.id, appt.id)
        tags = _evidence_tags(audit_entry)
        assert "raw_compat_status" in tags

    def test_delete_emits_deprecation_header(
        self, client, db, gp_user, practice, practitioner, patient, header_mode
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        resp = client.delete(
            f"/api/v1/appointments/{appt.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204
        assert resp.headers.get("deprecation") is not None, (
            "Expected Deprecation header in header mode"
        )


# Off mode


class TestOffMode:

    def test_create_no_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient, off_mode
    ):
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        # Deprecation header should be absent
        deprecation = resp.headers.get("deprecation")
        assert deprecation is None, (
            f"Expected no Deprecation header in off mode, got {deprecation!r}"
        )
        # No raw_compat_* evidence tags
        data = resp.json()
        appt_id = uuid.UUID(data["id"])
        audit_entry = _last_audit_log(db, practice.id, appt_id)
        tags = _evidence_tags(audit_entry)
        assert len(tags) == 0, (
            f"Expected no raw_compat_* evidence in off mode, got {tags}"
        )

    def test_update_no_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient, off_mode
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"reason": "Updated reason"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        deprecation = resp.headers.get("deprecation")
        assert deprecation is None
        audit_entry = _last_audit_log(db, practice.id, appt.id)
        tags = _evidence_tags(audit_entry)
        assert len(tags) == 0

    def test_status_no_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient, off_mode
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        resp = client.patch(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "Confirmed"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        deprecation = resp.headers.get("deprecation")
        assert deprecation is None
        audit_entry = _last_audit_log(db, practice.id, appt.id)
        tags = _evidence_tags(audit_entry)
        assert len(tags) == 0

    def test_delete_no_raw_compat_evidence(
        self, client, db, gp_user, practice, practitioner, patient, off_mode
    ):
        token = make_token(gp_user)
        appt = _make_appt(db, practice, practitioner, patient)
        resp = client.delete(
            f"/api/v1/appointments/{appt.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204
        deprecation = resp.headers.get("deprecation")
        assert deprecation is None
        audit_entry = _last_audit_log(db, practice.id, appt.id)
        tags = _evidence_tags(audit_entry)
        assert len(tags) == 0

    def test_create_still_succeeds(
        self, client, db, gp_user, practice, practitioner, patient, off_mode
    ):
        """Off mode must not break the raw endpoint behaviour."""
        token = make_token(gp_user)
        body = _base_create_body(patient, practitioner)
        resp = client.post(
            "/api/v1/appointments",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data

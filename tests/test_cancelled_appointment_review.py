"""
GET /api/v1/appointments?status=Cancelled

Proves that the existing list endpoint correctly exposes cancellation_reason
for staff review of cancelled appointments, enforces practice isolation, and
requires authentication.  No new routes or schemas are added; the contract is
already correct — these tests lock it in.
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.tenancy import Practitioner
from tests.conftest import make_token

TODAY = date.today()
LIST_URL = "/api/v1/appointments"


def _make_appt(db, practice, practitioner, patient, start_h=9):
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(TODAY, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=TODAY,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(a)
    db.flush()
    return a


def _cancel_with_reason(client, token, appt_id, reason=None):
    kwargs = {"headers": {"Authorization": f"Bearer {token}"}}
    if reason is not None:
        kwargs["json"] = {"cancellation_reason": reason}
    return client.request("DELETE", f"/api/v1/appointments/{appt_id}", **kwargs)


def _list_cancelled(client, token):
    return client.get(
        LIST_URL,
        params={"status": "Cancelled"},
        headers={"Authorization": f"Bearer {token}"},
    )


# ─── Auth gate ────────────────────────────────────────────────────────────────

def test_cancelled_list_requires_auth(client):
    resp = client.get(LIST_URL, params={"status": "Cancelled"})
    assert resp.status_code == 401


# ─── Reason visibility ────────────────────────────────────────────────────────

def test_cancelled_list_includes_cancellation_reason(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    r = _cancel_with_reason(client, token, appt.id, reason="Patient requested")
    assert r.status_code == 204

    resp = _list_cancelled(client, token)
    assert resp.status_code == 200
    rows = {row["id"]: row for row in resp.json()}
    assert str(appt.id) in rows
    assert rows[str(appt.id)]["cancellation_reason"] == "Patient requested"


def test_cancelled_list_reason_null_when_not_given(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=10)
    token = make_token(gp_user)

    r = _cancel_with_reason(client, token, appt.id)  # no reason
    assert r.status_code == 204

    resp = _list_cancelled(client, token)
    assert resp.status_code == 200
    rows = {row["id"]: row for row in resp.json()}
    assert str(appt.id) in rows
    assert rows[str(appt.id)]["cancellation_reason"] is None


# ─── Status filter isolation ──────────────────────────────────────────────────

def test_cancelled_status_filter_excludes_active(
        client, db, gp_user, practice, practitioner, patient):
    active = _make_appt(db, practice, practitioner, patient, start_h=11)
    cancelled = _make_appt(db, practice, practitioner, patient, start_h=12)
    token = make_token(gp_user)

    _cancel_with_reason(client, token, cancelled.id, reason="DNA")

    resp = _list_cancelled(client, token)
    assert resp.status_code == 200
    ids = [row["id"] for row in resp.json()]
    assert str(cancelled.id) in ids
    assert str(active.id) not in ids


# ─── Cross-practice isolation ─────────────────────────────────────────────────

def test_cancelled_cross_practice_isolation(
        client, db, gp_user, practice_b, patient_b):
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Other",
        last_name="Doctor",
        ahpra_number="MED0007771234",
    )
    db.add(prac_b)
    db.flush()

    appt_b = Appointment(
        practice_id=practice_b.id,
        patient_id=patient_b.id,
        practitioner_id=prac_b.id,
        start_time=datetime.combine(TODAY, time(9, 0), tzinfo=timezone.utc),
        appointment_date=TODAY,
        start_time_local=time(9, 0),
        duration_minutes=15,
        status=AppointmentStatus.Cancelled,
        cancellation_reason="Cancelled by other practice",
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt_b)
    db.flush()

    token = make_token(gp_user)  # belongs to practice A
    resp = _list_cancelled(client, token)
    assert resp.status_code == 200
    ids = [row["id"] for row in resp.json()]
    assert str(appt_b.id) not in ids

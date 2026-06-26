"""
Appointment audit warning-summary contract tests.

Covers:
- confirmed_warnings codes are persisted on create/update/status_change/delete.
- Empty confirmed_warnings list stores NULL (not an empty JSON array).
- confirmed_warnings is returned in GET /{id}/audit as a list of strings.
- Proposal (non-mutating) endpoints never write confirmed_warnings.
- confirmed_warnings contains only codes, not human-readable text or PHI.
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import (
    Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel,
)
from tests.conftest import make_token

TODAY = date.today()
APPT_URL = "/api/v1/appointments"


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


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_body(practitioner, patient, start_h=10, confirmed_warnings=None):
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": TODAY.isoformat(),
        "start_time_local": f"{start_h:02d}:00:00",
        "duration_minutes": 15,
    }
    if confirmed_warnings is not None:
        body["confirmed_warnings"] = confirmed_warnings
    return body


# ─── confirmed_warnings persisted on create ──────────────────────────────────

def test_create_stores_confirmed_warnings(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(practitioner, patient, confirmed_warnings=["break_overlap", "provisional_patient"]),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt_id
    ).one()
    assert entry.confirmed_warnings == ["break_overlap", "provisional_patient"]


def test_create_without_warnings_stores_null(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(practitioner, patient),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt_id
    ).one()
    assert entry.confirmed_warnings is None


def test_create_with_empty_warnings_stores_null(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(practitioner, patient, confirmed_warnings=[]),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt_id
    ).one()
    assert entry.confirmed_warnings is None


# ─── confirmed_warnings persisted on update ──────────────────────────────────

def test_update_stores_confirmed_warnings(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.put(
        f"{APPT_URL}/{appt.id}",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_date": TODAY.isoformat(),
            "start_time_local": "09:00:00",
            "duration_minutes": 30,
            "confirmed_warnings": ["provisional_patient"],
        },
        headers=_auth(token),
    )
    assert resp.status_code == 200

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).one()
    assert entry.confirmed_warnings == ["provisional_patient"]


# ─── confirmed_warnings persisted on status change ───────────────────────────

def test_status_change_stores_confirmed_warnings(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Confirmed", "confirmed_warnings": ["waiting_area_cleared"]},
        headers=_auth(token),
    )
    assert resp.status_code == 200

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).one()
    assert entry.confirmed_warnings == ["waiting_area_cleared"]


def test_status_change_without_warnings_stores_null(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Confirmed"},
        headers=_auth(token),
    )
    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).one()
    assert entry.confirmed_warnings is None


# ─── confirmed_warnings persisted on delete ──────────────────────────────────

def test_delete_stores_confirmed_warnings(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.request(
        "DELETE",
        f"{APPT_URL}/{appt.id}",
        json={"cancellation_reason": "Patient request", "confirmed_warnings": ["waiting_area_cleared"]},
        headers=_auth(token),
    )
    assert resp.status_code == 204

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).one()
    assert entry.confirmed_warnings == ["waiting_area_cleared"]


def test_delete_without_body_stores_null(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.delete(f"{APPT_URL}/{appt.id}", headers=_auth(make_token(receptionist_user)))
    assert resp.status_code == 204

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).one()
    assert entry.confirmed_warnings is None


# ─── confirmed_warnings exposed in GET /{id}/audit ───────────────────────────

def test_audit_endpoint_returns_confirmed_warnings(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(practitioner, patient, confirmed_warnings=["break_overlap"]),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    audit_resp = client.get(f"{APPT_URL}/{appt_id}/audit", headers=_auth(token))
    assert audit_resp.status_code == 200
    entries = audit_resp.json()
    assert len(entries) == 1
    assert entries[0]["confirmed_warnings"] == ["break_overlap"]


def test_audit_endpoint_returns_empty_list_when_no_warnings(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(practitioner, patient),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    audit_resp = client.get(f"{APPT_URL}/{appt_id}/audit", headers=_auth(token))
    assert audit_resp.status_code == 200
    entries = audit_resp.json()
    assert len(entries) == 1
    assert entries[0]["confirmed_warnings"] == []


# ─── confirmed_warnings are code-only (no PHI, no human text) ────────────────

def test_confirmed_warnings_are_string_codes_only(
    client, db, practice, practitioner, patient, receptionist_user
):
    """Codes must be short identifiers, not human-readable sentences or PHI."""
    token = make_token(receptionist_user)
    codes = ["break_overlap", "provisional_patient", "waiting_area_cleared"]
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(practitioner, patient, confirmed_warnings=codes),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt_id
    ).one()
    for code in entry.confirmed_warnings:
        assert isinstance(code, str)
        # Codes should not be long human-readable messages
        assert len(code) < 100
        assert " " not in code or "_" in code  # snake_case or single word


def test_unknown_warning_codes_are_not_persisted(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(
            practitioner,
            patient,
            confirmed_warnings=[
                "break_overlap",
                "Margaret Thompson has transport trouble",
                "<script>alert(1)</script>",
                "break_overlap",
            ],
        ),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    entry = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt_id
    ).one()
    assert entry.confirmed_warnings == ["break_overlap"]


# ─── Proposal endpoints never write confirmed_warnings ───────────────────────

def test_proposal_create_does_not_write_audit_with_warnings(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    client.post(
        f"{APPT_URL}/proposals/create",
        json=_create_body(practitioner, patient),
        headers=_auth(token),
    )
    assert db.query(AppointmentAuditLog).count() == 0

"""
Appointment proposal audit contract tests.

Covers:
- Proposal (non-mutating) endpoints do NOT create audit entries.
- Confirmed create (POST /) writes a 'create' audit entry.
- Confirmed update (PUT /{id}) writes an 'update' audit entry.
- Confirmed status change (PATCH /{id}/status) writes a 'status_change' entry.
- Confirmed delete (DELETE /{id}) writes a 'delete' entry with cancellation_reason.
- Blocked proposals (e.g. conflict) do NOT create audit entries.
- GET /{id}/audit returns entries in order, practice-scoped.
- Cross-practice GET /{id}/audit returns 404.
- Unauthenticated GET /{id}/audit returns 401.
- Multiple mutations produce multiple ordered entries.
"""
import json
from datetime import date, datetime, time, timedelta, timezone

import pytest

from app.models.appointments import (
    Appointment, AppointmentAuditLog, AppointmentAuditAction, AppointmentStatus,
    BookingChannel,
)
from tests.conftest import make_token

TODAY = date.today() + timedelta(days=14)
APPT_URL = "/api/v1/appointments"
DELETE_CONFIRM_URL = f"{APPT_URL}/proposals/delete-confirm"


def _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked, start_h=9):
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(TODAY, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=TODAY,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(a)
    db.flush()
    return a


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_body(practitioner, patient, start_h=10):
    return {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": TODAY.isoformat(),
        "start_time_local": f"{start_h:02d}:00:00",
        "duration_minutes": 15,
    }


# ─── Proposal endpoints are non-mutating (no audit rows) ─────────────────────

def test_proposal_create_does_not_write_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    client.post(
        f"{APPT_URL}/proposals/create",
        json=_create_body(practitioner, patient),
        headers=_auth(token),
    )
    assert db.query(AppointmentAuditLog).count() == 0


def test_proposal_update_does_not_write_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    client.post(
        f"{APPT_URL}/proposals/update/{appt.id}",
        json={"duration_minutes": 30},
        headers=_auth(token),
    )
    assert db.query(AppointmentAuditLog).count() == 0


def test_proposal_status_does_not_write_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    client.post(
        f"{APPT_URL}/proposals/status/{appt.id}",
        json={"status": "Confirmed"},
        headers=_auth(token),
    )
    assert db.query(AppointmentAuditLog).count() == 0


def test_proposal_delete_does_not_write_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    client.post(
        f"{APPT_URL}/proposals/delete/{appt.id}",
        json={"cancellation_reason": "Patient request"},
        headers=_auth(token),
    )
    assert db.query(AppointmentAuditLog).count() == 0


# ─── Blocked proposal does not write audit ───────────────────────────────────

def test_blocked_proposal_does_not_write_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    # Seed a conflicting appointment so the proposal is blocked
    _make_appt(db, practice, practitioner, patient, start_h=10)
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}/proposals/create",
        json=_create_body(practitioner, patient, start_h=10),
        headers=_auth(token),
    )
    assert resp.json()["autonomy_tier"] == "blocked"
    assert db.query(AppointmentAuditLog).count() == 0


# ─── Confirmed create writes audit ───────────────────────────────────────────

def test_confirmed_create_writes_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    token = make_token(receptionist_user)
    resp = client.post(
        f"{APPT_URL}",
        json=_create_body(practitioner, patient, start_h=10),
        headers=_auth(token),
    )
    assert resp.status_code == 201
    appt_id = resp.json()["id"]

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt_id
    ).all()
    assert len(entries) == 1
    e = entries[0]
    assert e.action == AppointmentAuditAction.create
    assert e.status_before is None
    assert e.status_after == AppointmentStatus.Booked
    assert e.confirmed_by_user_id == receptionist_user.id
    assert e.practice_id == practice.id
    assert e.cancellation_reason is None


# ─── Confirmed update writes audit ───────────────────────────────────────────

def test_confirmed_update_writes_audit(
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
        },
        headers=_auth(token),
    )
    assert resp.status_code == 200

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    e = entries[0]
    assert e.action == AppointmentAuditAction.update
    assert e.status_before == AppointmentStatus.Booked
    assert e.status_after is None
    assert e.confirmed_by_user_id == receptionist_user.id


# ─── Confirmed status change writes audit ────────────────────────────────────

def test_confirmed_status_change_writes_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Confirmed"},
        headers=_auth(token),
    )
    assert resp.status_code == 200

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    e = entries[0]
    assert e.action == AppointmentAuditAction.status_change
    assert e.status_before == AppointmentStatus.Booked
    assert e.status_after == AppointmentStatus.Confirmed
    assert e.confirmed_by_user_id == receptionist_user.id


# ─── Confirmed delete writes audit ───────────────────────────────────────────

def test_confirmed_delete_writes_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.request(
        "DELETE",
        f"{APPT_URL}/{appt.id}",
        json={"cancellation_reason": "Patient request"},
        headers=_auth(token),
    )
    assert resp.status_code == 204

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    e = entries[0]
    assert e.action == AppointmentAuditAction.delete
    assert e.status_before == AppointmentStatus.Booked
    assert e.status_after == AppointmentStatus.Cancelled
    assert e.cancellation_reason == "Patient request"
    assert e.confirmed_by_user_id == receptionist_user.id


def test_confirmed_delete_without_reason_writes_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.delete(
        f"{APPT_URL}/{appt.id}",
        headers=_auth(token),
    )
    assert resp.status_code == 204

    e = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).one()
    assert e.action == AppointmentAuditAction.delete
    assert e.cancellation_reason is None


def test_signed_delete_confirm_writes_delete_audit_evidence(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    proposal_resp = client.post(
        f"{APPT_URL}/proposals/delete/{appt.id}",
        json={"cancellation_reason": "Patient request"},
        headers=_auth(token),
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    confirm_resp = client.post(
        DELETE_CONFIRM_URL,
        json=payload,
        headers=_auth(token),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True
    assert data["audit_evidence"] == [
        "diary_confirm_delete_proposal",
        "source_delete_proposal",
        "source_current_appointment_state",
        "delete_signed_confirmation_evidence_verified",
    ]
    e = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).one()
    assert e.action == AppointmentAuditAction.delete
    assert e.status_before == AppointmentStatus.Booked
    assert e.status_after == AppointmentStatus.Cancelled
    assert e.cancellation_reason == "Patient request"
    assert e.confirmed_warnings == [
        "diary_confirm_delete_proposal",
        "source_delete_proposal",
        "source_current_appointment_state",
        "delete_signed_confirmation_evidence_verified",
    ]


# ─── GET /{id}/audit ─────────────────────────────────────────────────────────

def test_get_audit_requires_auth(
    client, db, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.get(f"{APPT_URL}/{appt.id}/audit")
    assert resp.status_code == 401


def test_get_audit_returns_entries_in_order(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)

    # Two mutations in sequence
    client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Confirmed"},
        headers=_auth(token),
    )
    client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Arrived"},
        headers=_auth(token),
    )

    resp = client.get(f"{APPT_URL}/{appt.id}/audit", headers=_auth(token))
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) == 2
    assert entries[0]["action"] == "status_change"
    assert entries[0]["status_before"] == "Booked"
    assert entries[0]["status_after"] == "Confirmed"
    assert entries[0]["confirmed_by_display"] == "rec"
    assert entries[0]["confirmed_by_role"] == "Receptionist"
    assert entries[1]["status_before"] == "Confirmed"
    assert entries[1]["status_after"] == "Arrived"
    assert entries[1]["confirmed_by_display"] == "rec"
    assert entries[1]["confirmed_by_role"] == "Receptionist"


def test_get_audit_uses_practitioner_name_for_clinician_actor(
    client, db, practice, practitioner, patient, gp_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Confirmed"},
        headers=_auth(token),
    )

    resp = client.get(f"{APPT_URL}/{appt.id}/audit", headers=_auth(token))
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) == 1
    assert entries[0]["confirmed_by_user_id"] == str(gp_user.id)
    assert entries[0]["confirmed_by_display"] == "Alex Shera"
    assert entries[0]["confirmed_by_role"] == "GP"


def test_get_audit_cross_practice_returns_404(
    client, db, practice, practitioner, patient,
    practice_b, gp_user_b, receptionist_user,
):
    appt = _make_appt(db, practice, practitioner, patient)
    # Write an audit entry for practice A
    client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Confirmed"},
        headers=_auth(make_token(receptionist_user)),
    )

    # Practice B user tries to read practice A audit trail
    token_b = make_token(gp_user_b)
    resp = client.get(f"{APPT_URL}/{appt.id}/audit", headers=_auth(token_b))
    assert resp.status_code == 404


def test_get_audit_empty_for_fresh_appointment(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)
    resp = client.get(f"{APPT_URL}/{appt.id}/audit", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_delete_preserves_cancellation_reason_on_appointment_and_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    reason = "Patient request"
    token = make_token(receptionist_user)

    resp = client.request(
        "DELETE",
        f"{APPT_URL}/{appt.id}",
        json={"cancellation_reason": reason},
        headers=_auth(token),
    )
    assert resp.status_code == 204

    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "Cancelled"
    assert resp.json()["cancellation_reason"] == reason

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].action == AppointmentAuditAction.delete
    assert entries[0].status_before == AppointmentStatus.Booked
    assert entries[0].status_after == AppointmentStatus.Cancelled
    assert entries[0].cancellation_reason == reason


@pytest.mark.parametrize("status", ["Cancelled", "NoShow", "DNA"])
def test_patch_status_does_not_set_cancellation_reason(
    status, client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(receptionist_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": status},
        headers=_auth(token),
    )
    assert resp.status_code == 200

    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["status"] == status
    assert resp.json()["cancellation_reason"] is None

    resp = client.get(f"{APPT_URL}/{appt.id}/audit", headers=_auth(token))
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) == 1
    assert entries[0]["action"] == "status_change"
    assert entries[0]["status_before"] == "Booked"
    assert entries[0]["status_after"] == status
    assert entries[0]["cancellation_reason"] is None


def test_delete_confirm_preserves_cancellation_reason_on_appointment_and_audit(
    client, db, practice, practitioner, patient, receptionist_user
):
    appt = _make_appt(db, practice, practitioner, patient)
    reason = "Moved to another clinic"
    token = make_token(receptionist_user)

    resp = client.post(
        f"{APPT_URL}/proposals/delete/{appt.id}",
        json={"cancellation_reason": reason},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    payload = resp.json()["confirm_payload"]
    payload["confirmed"] = True

    resp = client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth(token))
    assert resp.status_code == 200

    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "Cancelled"
    assert resp.json()["cancellation_reason"] == reason

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].action == AppointmentAuditAction.delete
    assert entries[0].status_before == AppointmentStatus.Booked
    assert entries[0].status_after == AppointmentStatus.Cancelled
    assert entries[0].cancellation_reason == reason

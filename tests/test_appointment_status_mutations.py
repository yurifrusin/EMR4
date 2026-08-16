"""
PATCH /api/v1/appointments/{appointment_id}/status
DELETE /api/v1/appointments/{appointment_id}
POST /api/v1/appointments/proposals/delete/{appointment_id}

Covers:
- Auth gate (401 without token)
- Non-existent appointment → 404
- Cross-practice mutation → 404
- All valid statuses accepted (200 + updated status in response)
- Invalid status value → 422
- Waiting-room inclusion/exclusion after mutation
- Response embeds patient, practitioner, appointment_type
- DELETE soft-cancels, clears waiting_area_id, row remains in DB
- proposals/delete surfaces waiting_area side-effects before the write
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
from app.models.diary import WaitingArea
from app.models.tenancy import Practitioner
from tests.conftest import make_token

TODAY = date.today()
PAST_DATE = date(2026, 4, 15)


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


def _patch_status(client, token, appt_id, new_status: str):
    return client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": new_status},
        headers={"Authorization": f"Bearer {token}"},
    )


_status_proposal_key_counter = 0


def _post_status_proposal(client, token, appt_id, payload: dict):
    global _status_proposal_key_counter
    _status_proposal_key_counter += 1
    return client.post(
        f"/api/v1/appointments/proposals/status/{appt_id}",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": f"status-prop-test-{_status_proposal_key_counter}",
        },
    )


_status_confirm_key_counter = 0


def _status_confirm_headers(token: str, prefix: str = "status-confirm-test") -> dict[str, str]:
    global _status_confirm_key_counter
    _status_confirm_key_counter += 1
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": f"{prefix}-{_status_confirm_key_counter}",
    }


_delete_confirm_key_counter = 0
_delete_proposal_key_counter = 0


def _delete_confirm_headers(token: str, prefix: str = "delete-confirm-test") -> dict[str, str]:
    global _delete_confirm_key_counter
    _delete_confirm_key_counter += 1
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": f"{prefix}-{_delete_confirm_key_counter}",
    }


def _delete_proposal_headers(token: str) -> dict[str, str]:
    global _delete_proposal_key_counter
    _delete_proposal_key_counter += 1
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": f"delete-proposal-test-{_delete_proposal_key_counter}",
    }


def _confirm_status_proposal(client, token, proposal: dict, *, confirmed: bool = True):
    payload = proposal["confirm_payload"]
    payload["confirmed"] = confirmed
    return client.post(
        "/api/v1/appointments/proposals/status/confirm",
        json=payload,
        headers=_status_confirm_headers(token),
    )


# ─── Auth gate ─────────────────────────────────────────────────────────────────

def test_status_mutation_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Confirmed"},
    )
    assert resp.status_code == 401


def test_status_mutation_rejects_unknown_role_token(client, db, practice, practitioner, patient):
    """A token with no mutating appointment role cannot patch appointment status."""
    from app.services.auth_service import create_access_token

    appt = _make_appt(db, practice, practitioner, patient)
    bad_token = create_access_token({
        "sub": str(appt.id),
        "practice_id": str(practice.id),
        "role": "UnknownRole",
    })
    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Confirmed"},
        headers={"Authorization": f"Bearer {bad_token}"},
    )
    assert resp.status_code in (401, 403)


# ─── Not found ─────────────────────────────────────────────────────────────────

def test_status_mutation_nonexistent_appointment_returns_404(client, gp_user):
    import uuid
    token = make_token(gp_user)
    resp = _patch_status(client, token, uuid.uuid4(), "Confirmed")
    assert resp.status_code == 404


# ─── Cross-practice isolation ──────────────────────────────────────────────────

def test_status_mutation_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    """A user from practice A cannot mutate practice B's appointment."""
    from app.models.tenancy import Practitioner
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Other",
        ahpra_number="MED0008888888",
    )
    db.add(prac_b)
    db.flush()
    appt_b = _make_appt(db, practice_b, prac_b, patient_b)

    token = make_token(gp_user)  # belongs to practice A
    resp = _patch_status(client, token, appt_b.id, "Confirmed")
    assert resp.status_code == 404


# ─── Valid statuses ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("new_status", [
    "Booked", "Confirmed", "Arrived", "InConsult",
    "Completed", "Cancelled", "NoShow", "DNA",
])
def test_status_mutation_all_valid_statuses_accepted(
        new_status, client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, new_status)
    assert resp.status_code == 200
    assert resp.json()["status"] == new_status


# ─── Invalid status ────────────────────────────────────────────────────────────

def test_status_mutation_invalid_status_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, "NotAStatus")
    assert resp.status_code == 422


# ─── Response shape ────────────────────────────────────────────────────────────

def test_status_mutation_response_embeds_patient_and_practitioner(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, "Confirmed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Confirmed"
    assert data["patient"]["first_name"] == "Margaret"
    assert data["practitioner"]["ahpra_number"] == "MED0001234567"
    assert "end_time" in data
    assert "start_time_local" in data


def test_status_mutation_response_embeds_appointment_type(
        client, db, gp_user, practice, practitioner, patient, appt_type):
    appt = _make_appt(db, practice, practitioner, patient)
    appt.appointment_type_id = appt_type.id
    db.flush()
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, "Arrived")
    assert resp.status_code == 200
    assert resp.json()["appointment_type"]["name"] == "Standard"


# ─── Waiting-room interaction ──────────────────────────────────────────────────

@pytest.mark.parametrize("active_status", [
    "Booked", "Confirmed", "Arrived", "InConsult",
])
def test_mutation_to_active_status_appears_in_waiting_room(
        active_status, client, db, gp_user, practice, practitioner, patient):
    """After mutating to an active status, appointment appears in the waiting room."""
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.Completed)
    token = make_token(gp_user)
    _patch_status(client, token, appt.id, active_status)

    wr = client.get("/api/v1/appointments/waiting-room",
                    headers={"Authorization": f"Bearer {token}"})
    ids = [e["id"] for e in wr.json()]
    assert str(appt.id) in ids


@pytest.mark.parametrize("terminal_status", [
    "Completed", "Cancelled", "NoShow", "DNA",
])
def test_mutation_to_terminal_status_disappears_from_waiting_room(
        terminal_status, client, db, gp_user, practice, practitioner, patient):
    """After mutating to a terminal status, appointment is gone from the waiting room."""
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.Arrived)
    token = make_token(gp_user)
    _patch_status(client, token, appt.id, terminal_status)

    wr = client.get("/api/v1/appointments/waiting-room",
                    headers={"Authorization": f"Bearer {token}"})
    ids = [e["id"] for e in wr.json()]
    assert str(appt.id) not in ids


# ─── DELETE soft-cancel ────────────────────────────────────────────────────────

def _make_area(db, practice):
    area = WaitingArea(practice_id=practice.id, name="Main Waiting Room")
    db.add(area)
    db.flush()
    return area


def _delete(client, token, appt_id):
    return client.delete(
        f"/api/v1/appointments/{appt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )


DELETE_PROPOSAL_URL = "/api/v1/appointments/proposals/delete/{}"
DELETE_CONFIRM_URL = "/api/v1/appointments/proposals/delete-confirm"


def test_delete_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.delete(f"/api/v1/appointments/{appt.id}")
    assert resp.status_code == 401


def test_delete_soft_cancels_appointment(client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)
    assert resp.status_code == 204
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Cancelled


def test_delete_clears_waiting_area_on_cancel(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    appt.waiting_area_id = area.id
    db.commit()

    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)
    assert resp.status_code == 204
    db.refresh(appt)
    assert appt.waiting_area_id is None


def test_delete_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Other",
        ahpra_number="MED0009999999",
    )
    db.add(prac_b)
    db.flush()
    appt_b = _make_appt(db, practice_b, prac_b, patient_b)
    token = make_token(gp_user)  # belongs to practice A
    resp = _delete(client, token, appt_b.id)
    assert resp.status_code == 404


def test_delete_proposal_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.post(DELETE_PROPOSAL_URL.format(appt.id))
    assert resp.status_code == 401


def test_delete_proposal_warns_waiting_area_cleared(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    appt.waiting_area_id = area.id
    db.commit()

    token = make_token(gp_user)
    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        headers=_delete_proposal_headers(token),

    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["requires_confirmation"] is True
    assert data["command"]["clears_waiting_area"] is True
    assert any(w["code"] == "waiting_area_cleared" for w in data["warnings"])
    assert data["blocks"] == []
    # Row must not be mutated by the proposal
    db.refresh(appt)
    assert appt.waiting_area_id == area.id


def test_delete_proposal_blocked_already_cancelled(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Cancelled,
    )
    token = make_token(gp_user)
    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        headers=_delete_proposal_headers(token),

    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert len(data["blocks"]) >= 1
    assert data["blocks"][0]["code"] == "already_in_status"


# ─── Cancellation reason ───────────────────────────────────────────────────────

def test_delete_with_reason_persists(client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)  # no body first; then repeat with reason
    # Use a fresh appointment for the reason test
    appt2 = _make_appt(db, practice, practitioner, patient, start_h=10)
    resp = client.request(
        "DELETE",
        f"/api/v1/appointments/{appt2.id}",
        json={"cancellation_reason": "Patient called to cancel"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
    db.refresh(appt2)
    assert appt2.cancellation_reason == "Patient called to cancel"
    assert appt2.status == AppointmentStatus.Cancelled


def test_delete_without_reason_is_null(client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=11)
    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)
    assert resp.status_code == 204
    db.refresh(appt)
    assert appt.cancellation_reason is None


def test_delete_proposal_echoes_reason_in_command(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=12)
    token = make_token(gp_user)
    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Practitioner unavailable"},
        headers=_delete_proposal_headers(token),

    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["command"]["cancellation_reason"] == "Practitioner unavailable"
    # Row must not be mutated by the proposal
    db.refresh(appt)
    assert appt.cancellation_reason is None
    assert appt.status == AppointmentStatus.Booked



# ─── Delete proposal idempotency-key tests ──────────────────────────────────


def test_delete_proposal_requires_idempotency_key(
        client, db, gp_user, practice, practitioner, patient):
    """Missing Idempotency-Key on delete proposal returns 400."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(Appointment).count() == before


def test_delete_proposal_blank_idempotency_key_is_missing(
        client, db, gp_user, practice, practitioner, patient):
    """Whitespace-only Idempotency-Key on delete proposal returns 400."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Test"},
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "   ",
        },
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(Appointment).count() == before


def test_delete_proposal_valid_key_reaches_evaluation(
        client, db, gp_user, practice, practitioner, patient):
    """Nonblank Idempotency-Key on delete proposal reaches normal evaluation."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Patient request"},
        headers=_delete_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "delete_appointment"
    assert data["safe"] is True
    # DB row unchanged
    db.refresh(appt)
    assert appt.status.value == "Booked"


def test_delete_proposal_returns_signed_confirm_payload(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, start_h=13)
    appt.waiting_area_id = area.id
    db.flush()
    token = make_token(gp_user)

    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Patient request"},
        headers=_status_confirm_headers(token, "tampered-past-status"),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["confirm_endpoint"] == "/api/v1/appointments/proposals/delete/confirm"
    assert data["delete_proposal_freshness_id"]
    assert data["delete_proposal_version_binding"]["schema_version"] == "raisa.delete_proposal_version_binding.v1"
    assert data["delete_proposal_version_binding"]["source_version"] == 1
    assert data["signed_confirmation_evidence_required"] is True
    assert data["signed_confirmation_evidence"]["purpose"] == "diary_confirm_delete_proposal"
    assert data["confirm_payload"]["confirmed"] is False
    assert data["confirm_payload"]["delete_proposal"]["command"]["appointment_id"] == str(appt.id)
    assert data["confirm_payload"]["delete_proposal"]["command"]["clears_waiting_area"] is True
    assert data["confirm_payload"]["delete_proposal"]["command"]["cancellation_reason"] == "Patient request"
    assert data["confirm_payload"]["delete_proposal_freshness_id"] == data["delete_proposal_freshness_id"]
    assert data["confirm_payload"]["delete_proposal_version_binding"] == data["delete_proposal_version_binding"]
    assert data["confirm_payload"]["signed_confirmation_evidence"] == data["signed_confirmation_evidence"]
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert appt.waiting_area_id == area.id


def test_delete_confirm_requires_confirmed_true_without_write(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=14)
    token = make_token(gp_user)
    proposal_resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        headers=_delete_proposal_headers(token),

    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        DELETE_CONFIRM_URL,
        json=payload,
        headers=_delete_confirm_headers(token, "delete-unconfirmed"),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "explicit_confirmation_required" for block in data["blocks"])
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert db.query(AppointmentAuditLog).count() == before_audits


def test_delete_confirm_blocks_tampered_signed_evidence_without_write(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=15)
    token = make_token(gp_user)
    proposal_resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Original reason"},
        headers=_delete_proposal_headers(token),

    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    payload["delete_proposal"]["command"]["cancellation_reason"] = "Tampered reason"
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        DELETE_CONFIRM_URL,
        json=payload,
        headers=_delete_confirm_headers(token, "delete-tampered"),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert any(
        block["code"] == "stale_delete_proposal_freshness_id"
        for block in data["blocks"]
    )
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert appt.cancellation_reason is None
    assert db.query(AppointmentAuditLog).count() == before_audits


def test_delete_confirm_blocks_stale_freshness_without_write(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=16)
    token = make_token(gp_user)
    proposal_resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        headers=_delete_proposal_headers(token),

    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    payload["delete_proposal_freshness_id"] = "stale-delete-proposal"
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        DELETE_CONFIRM_URL,
        json=payload,
        headers=_delete_confirm_headers(token, "delete-stale"),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "stale_delete_proposal_freshness_id" for block in data["blocks"])
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert db.query(AppointmentAuditLog).count() == before_audits


def test_delete_confirm_soft_cancels_once_with_signed_evidence(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, start_h=17)
    appt.waiting_area_id = area.id
    db.flush()
    token = make_token(gp_user)
    proposal_resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Patient had transport issues"},
        headers=_delete_proposal_headers(token),

    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        DELETE_CONFIRM_URL,
        json=payload,
        headers=_delete_confirm_headers(token, "delete-success"),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["receipt"]["status"] == "Cancelled"
    assert data["receipt"]["waiting_area_id"] is None
    assert data["receipt"]["cancellation_reason"] == "Patient had transport issues"
    assert "delete_product_adapter_v1" in data["audit_evidence"]
    assert "delete_signed_confirmation_evidence_verified" in data["audit_evidence"]
    assert "delete_current_authority_rechecked" in data["audit_evidence"]
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Cancelled
    assert appt.waiting_area_id is None
    assert appt.cancellation_reason == "Patient had transport issues"
    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id,
    ).all()
    assert db.query(AppointmentAuditLog).count() == before_audits + 1
    assert len(entries) == 1
    assert entries[0].confirmed_warnings == ["waiting_area_cleared"]
    assert entries[0].audit_evidence_codes == [
        "delete_product_adapter_v1",
        "delete_signed_confirmation_evidence_verified",
        "delete_current_authority_rechecked",
    ]


def test_delete_reason_too_long_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=13)
    token = make_token(gp_user)
    resp = client.request(
        "DELETE",
        f"/api/v1/appointments/{appt.id}",
        json={"cancellation_reason": "x" * 501},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_status_proposal_returns_signed_confirm_payload(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = _post_status_proposal(client, token, appt.id, {"status": "Confirmed"})

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["confirm_endpoint"] == "/api/v1/appointments/proposals/status/confirm"
    assert data["confirm_payload"]["confirmed"] is False
    assert data["confirm_payload"]["status_proposal_freshness_id"] == data["status_proposal_freshness_id"]
    assert data["signed_confirmation_evidence_required"] is True
    assert data["status_proposal_version_binding"]["source_version"] == 1
    assert data["confirm_payload"]["status_proposal_version_binding"] == data["status_proposal_version_binding"]
    assert data["signed_confirmation_evidence"]["purpose"] == "diary_confirm_status_proposal"
    assert data["command"]["waiting_area_id_supplied"] is False


def test_status_confirm_route_writes_once_with_signed_evidence(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    proposal_resp = _post_status_proposal(client, token, appt.id, {"status": "Confirmed"})
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = _confirm_status_proposal(client, token, proposal)

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["appointment"]["status"] == "Confirmed"
    assert "status_product_adapter_v1" in data["audit_evidence"]
    assert "status_signed_confirmation_evidence_verified" in data["audit_evidence"]
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


def test_status_confirm_route_blocks_tampered_status_without_write(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    proposal_resp = _post_status_proposal(client, token, appt.id, {"status": "Confirmed"})
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    payload["status_proposal"]["command"]["status"] = "Arrived"
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        "/api/v1/appointments/proposals/status-confirm",
        json=payload,
        headers=_status_confirm_headers(token, "tampered-status"),
    )

    assert confirm_resp.status_code == 403, confirm_resp.text
    assert confirm_resp.json()["detail"]["code"] == "authenticated_status_context_unavailable"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert db.query(AppointmentAuditLog).count() == before_audits


def test_status_confirm_preserves_waiting_area_when_field_omitted(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    appt.waiting_area_id = area.id
    db.commit()
    token = make_token(gp_user)
    proposal_resp = _post_status_proposal(client, token, appt.id, {"status": "Arrived"})
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    assert proposal["command"]["waiting_area_id_supplied"] is False
    db.commit()

    confirm_resp = _confirm_status_proposal(client, token, proposal)

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True, data["blocks"]
    assert data["appointment"]["status"] == "Arrived"
    assert data["appointment"]["waiting_area_id"] == str(area.id)


def test_status_confirm_clears_waiting_area_when_null_supplied(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    appt.waiting_area_id = area.id
    db.commit()
    token = make_token(gp_user)
    proposal_resp = _post_status_proposal(client, token, appt.id, {
        "status": "Arrived",
        "waiting_area_id": None,
    })
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    assert proposal["command"]["waiting_area_id_supplied"] is True
    db.commit()

    confirm_resp = _confirm_status_proposal(client, token, proposal)

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True, data["blocks"]
    assert data["appointment"]["waiting_area_id"] is None


def test_r9_status_proposal_allows_past_date_without_temporal_block(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE)
    token = make_token(gp_user)

    resp = _post_status_proposal(client, token, appt.id, {"status": "Completed"})

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    block_codes = {block["code"] for block in data["blocks"]}
    assert "appointment_in_past" not in block_codes
    assert "same_day_window_elapsed" not in block_codes
    assert data["signed_confirmation_evidence_required"] is True


def test_r9_status_proposal_allows_elapsed_same_day_without_temporal_block(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=TODAY, start_h=9)
    token = make_token(gp_user)

    resp = _post_status_proposal(client, token, appt.id, {"status": "Confirmed"})

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    block_codes = {block["code"] for block in data["blocks"]}
    assert "appointment_in_past" not in block_codes
    assert "same_day_window_elapsed" not in block_codes


def test_r9_patch_status_allows_past_date_with_audit(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE)
    token = make_token(gp_user)
    before_audits = db.query(AppointmentAuditLog).count()

    resp = _patch_status(client, token, appt.id, "Completed")

    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "Completed"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Completed
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


def test_r9_status_confirm_allows_past_date_with_signed_evidence_and_audit(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE)
    token = make_token(gp_user)
    proposal_resp = _post_status_proposal(client, token, appt.id, {"status": "Completed"})
    assert proposal_resp.status_code == 200, proposal_resp.text
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = _confirm_status_proposal(client, token, proposal_resp.json())

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["appointment"]["status"] == "Completed"
    assert "status_product_adapter_v1" in data["audit_evidence"]
    assert "status_signed_confirmation_evidence_verified" in data["audit_evidence"]
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Completed
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


def test_r9_status_confirm_past_date_blocks_tampered_status_without_write(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE)
    token = make_token(gp_user)
    proposal_resp = _post_status_proposal(client, token, appt.id, {"status": "Completed"})
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    payload["status_proposal"]["command"]["status"] = "NoShow"
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        "/api/v1/appointments/proposals/status-confirm",
        json=payload,
        headers=_status_confirm_headers(token, "tampered-past-status"),
    )

    assert confirm_resp.status_code == 403, confirm_resp.text
    assert confirm_resp.json()["detail"]["code"] == "authenticated_status_context_unavailable"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert db.query(AppointmentAuditLog).count() == before_audits


def test_r9_delete_proposal_allows_past_date_without_temporal_block(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE)
    token = make_token(gp_user)

    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Historical patient cancellation"},
        headers=_delete_proposal_headers(token),

    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    block_codes = {block["code"] for block in data["blocks"]}
    assert "appointment_in_past" not in block_codes
    assert "same_day_window_elapsed" not in block_codes
    assert data["signed_confirmation_evidence_required"] is True


def test_r9_delete_confirm_allows_past_date_with_signed_evidence_and_audit(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE, start_h=10)
    token = make_token(gp_user)
    proposal_resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Historical correction"},
        headers=_delete_proposal_headers(token),

    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        DELETE_CONFIRM_URL,
        json=payload,
        headers=_delete_confirm_headers(token, "delete-past-success"),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["receipt"]["status"] == "Cancelled"
    assert "delete_product_adapter_v1" in data["audit_evidence"]
    assert "delete_signed_confirmation_evidence_verified" in data["audit_evidence"]
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Cancelled
    assert appt.cancellation_reason == "Historical correction"
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


def test_r9_delete_confirm_past_date_blocks_stale_freshness_without_write(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE, start_h=11)
    token = make_token(gp_user)
    proposal_resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        headers=_delete_proposal_headers(token),

    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    payload["delete_proposal_freshness_id"] = "stale-delete-proposal"
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        DELETE_CONFIRM_URL,
        json=payload,
        headers=_delete_confirm_headers(token, "delete-past-stale"),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "stale_delete_proposal_freshness_id" for block in data["blocks"])
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert db.query(AppointmentAuditLog).count() == before_audits

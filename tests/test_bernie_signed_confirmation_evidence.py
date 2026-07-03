"""Sprint S1 signed Bernie confirmation evidence.

These tests prove that the new signed confirmation path is server-owned and
fail-closed, while legacy unsigned confirmation remains an explicitly named
compatibility lane.
"""

from copy import deepcopy

from app.models.appointments import Appointment, AppointmentAuditLog
from app.services.bernie import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_CONFIRMATION_EVIDENCE_VERSION,
    mint_signed_confirmation_evidence,
    verify_signed_confirmation_evidence,
)
from tests.conftest import make_token


WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
REFERENCE_DATE = "2026-06-22"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _row_counts(db) -> tuple[int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )


def _signed_confirm_payload(client, token: str, practitioner, patient) -> dict:
    resp = client.post(
        WRAPPER_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": "today",
                "duration_minutes": "15",
                "patient_id": str(patient.id),
            },
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": "Signed evidence test",
        },
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "confirmation_ready"
    payload = data["staff_review"]["confirm_payload"]
    assert payload["signed_confirmation_evidence_required"] is True
    assert payload["signed_confirmation_evidence"]["schema_version"] == SIGNED_CONFIRMATION_EVIDENCE_VERSION
    assert payload["signed_confirmation_evidence"]["purpose"] == SIGNED_CONFIRMATION_EVIDENCE_PURPOSE
    payload["confirmed"] = True
    return payload


def test_signed_evidence_helper_verifies_and_rejects_tamper():
    payload = {
        "practice_id": "practice-1",
        "staff_user_id": "user-1",
        "appointment_date": REFERENCE_DATE,
    }
    evidence = mint_signed_confirmation_evidence(payload, secret="test-secret")

    verified = verify_signed_confirmation_evidence(evidence, payload, secret="test-secret")
    assert verified.verified is True

    tampered = deepcopy(evidence)
    tampered["payload"]["appointment_date"] = "2026-06-23"
    result = verify_signed_confirmation_evidence(tampered, payload, secret="test-secret")
    assert result.verified is False
    assert result.code == "signed_evidence_tampered"


def test_signed_confirmation_success_writes_and_audits_signed_evidence(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _signed_confirm_payload(client, token, practitioner, patient)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert "bernie_signed_confirmation_evidence_verified" in data["audit_evidence"]
    assert "legacy_unsigned_confirmation_compat" not in data["audit_evidence"]
    assert _row_counts(db) == (before[0] + 1, before[1] + 1)
    audit = db.query(AppointmentAuditLog).order_by(AppointmentAuditLog.created_at.desc()).first()
    assert audit is not None
    assert "bernie_signed_confirmation_evidence_verified" in audit.confirmed_warnings
    assert "legacy_unsigned_confirmation_compat" not in audit.confirmed_warnings


def test_missing_required_signed_evidence_blocks_without_mutation(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _signed_confirm_payload(client, token, practitioner, patient)
    payload["signed_confirmation_evidence"] = None
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(block["code"] == "signed_evidence_missing" for block in data["blocks"])
    assert _row_counts(db) == before


def test_tampered_signed_evidence_blocks_without_mutation(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _signed_confirm_payload(client, token, practitioner, patient)
    payload["signed_confirmation_evidence"]["payload"]["duration_minutes"] = 30
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "signed_evidence_tampered" for block in data["blocks"])
    assert _row_counts(db) == before


def test_valid_signature_for_wrong_payload_blocks_without_mutation(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _signed_confirm_payload(client, token, practitioner, patient)
    wrong_payload = deepcopy(payload["signed_confirmation_evidence"]["payload"])
    wrong_payload["duration_minutes"] = 30
    payload["signed_confirmation_evidence"] = mint_signed_confirmation_evidence(wrong_payload)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "signed_evidence_mismatch" for block in data["blocks"])
    assert _row_counts(db) == before

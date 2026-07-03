"""Sprint S1 signed Bernie confirmation evidence.

These tests prove that the new signed confirmation path is server-owned and
fail-closed, while legacy unsigned confirmation remains an explicitly named
compatibility lane.
"""

from copy import deepcopy
from datetime import date

from app.models.appointments import Appointment, AppointmentAuditLog
from app.routers.appointments import _BERNIE_SESSION_STORE
from app.services.bernie import (
    BernieSessionState,
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_CONFIRMATION_EVIDENCE_VERSION,
    build_session_confirmation_binding,
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


def _bind_payload_to_server_session(payload: dict, gp_user, *, revision: int = 7) -> dict:
    selection = payload["selection_proposal"]
    candidate = selection["selected_candidate"]
    command = selection["create_proposal"]["command"]
    candidate_id = payload["candidate_freshness_id"] or candidate["candidate_freshness_id"]
    proposal_id = payload["proposal_freshness_id"] or selection["proposal_freshness_id"]

    session = _BERNIE_SESSION_STORE.create_session(
        practice_id=gp_user.practice_id,
        user_id=gp_user.id,
        surface_id=f"diary-test-{candidate_id[:8]}",
        request_reference_date=gp_user.created_at.date() if getattr(gp_user, "created_at", None) else None,
    )
    session = session.model_copy(update={
        "state": BernieSessionState.proposal_preview,
        "revision": revision,
        "patient_id": command["patient_id"],
        "practitioner_id": command["practitioner_id"],
        "candidate_freshness_ids": [candidate_id],
        "staged_proposal_freshness_id": proposal_id,
    })
    _BERNIE_SESSION_STORE._sessions[session.session_id] = session

    binding = build_session_confirmation_binding(
        session,
        candidate_freshness_id=candidate_id,
        proposal_freshness_id=proposal_id,
        appointment_date=date.fromisoformat(candidate["appointment_date"]),
        start_time_local=candidate["start_time_local"],
        duration_minutes=candidate["duration_minutes"],
    )
    signed_payload = deepcopy(payload["signed_confirmation_evidence"]["payload"])
    signed_payload["session_binding"] = binding
    payload["session_binding"] = binding
    payload["signed_confirmation_evidence"] = mint_signed_confirmation_evidence(signed_payload)
    return payload


def test_session_bound_signed_confirmation_success_writes_and_audits_binding(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bind_payload_to_server_session(
        _signed_confirm_payload(client, token, practitioner, patient),
        gp_user,
    )
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert "bernie_signed_confirmation_evidence_verified" in data["audit_evidence"]
    assert "bernie_session_binding_verified" in data["audit_evidence"]
    assert _row_counts(db) == (before[0] + 1, before[1] + 1)


def test_signed_session_binding_mismatch_blocks_without_mutation(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bind_payload_to_server_session(
        _signed_confirm_payload(client, token, practitioner, patient),
        gp_user,
        revision=4,
    )
    tampered_binding = deepcopy(payload["session_binding"])
    tampered_binding["session_revision"] = 3
    signed_payload = deepcopy(payload["signed_confirmation_evidence"]["payload"])
    signed_payload["session_binding"] = tampered_binding
    payload["session_binding"] = tampered_binding
    payload["signed_confirmation_evidence"] = mint_signed_confirmation_evidence(signed_payload)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "session_binding_session_revision_mismatch" for block in data["blocks"])
    assert _row_counts(db) == before

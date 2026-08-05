"""B4.1 Davida default-location command runtime deterministic acceptance.

The suite exercises the three mounted routes through the real FastAPI/PostgreSQL
test client and the B4 persistence tables. It is provider-free and uses only
authored-synthetic practice data. No raw idempotency key, session credential,
patient field, provider output or free text is ever stored or asserted.
"""

from __future__ import annotations

import ast
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import text

import app.services.practice.practice_administration_default_location_command as service
from app.config import settings
from app.models.practice_administration_commands import (
    PracticeAdministrationAuditEvent,
    PracticeAdministrationCommandIdempotency,
    PracticeAdministrationConfirmationEvidence,
    PracticeAdministrationOutboxEvent,
)
from app.models.tenancy import Practice, PracticeLocation, Practitioner, User, UserRole
from app.schemas.practice_administration_default_location_command import (
    REJECTION_CODES,
)
from app.services.auth_service import create_access_token, hash_password

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = (
    ROOT
    / "docs/api-spine/openapi/"
    "practice-administration-default-location-commands.yaml"
)

PROPOSAL_PATH = (
    "/api/v1/practice-administration/"
    "practitioners/default-location/proposals"
)
EVIDENCE_PATH = (
    "/api/v1/practice-administration/"
    "practitioners/default-location/proposals/{proposal_id}/confirmation-evidence"
)
CONFIRM_PATH = (
    "/api/v1/practice-administration/"
    "practitioners/default-location/proposals/{proposal_id}/confirm"
)

B4_SECRET = "test-b4-command-secret-0123456789"
PROPOSAL_REQUEST_SCHEMA = (
    "emr4.practice_administration.default_location.proposal_request.v1"
)
EVIDENCE_REQUEST_SCHEMA = (
    "emr4.practice_administration.default_location.confirmation_evidence_request.v1"
)
CONFIRM_COMMAND_SCHEMA = (
    "emr4.practice_administration.default_location.confirmation_command.v1"
)
B4_TABLES = (
    "practice_administration_confirmation_evidence",
    "practice_administration_command_idempotency",
    "practice_administration_audit_events",
    "practice_administration_outbox_events",
)


def _token(user: User) -> str:
    return create_access_token(
        {
            "sub": str(user.id),
            "practice_id": str(user.practice_id),
            "role": user.role.value,
        }
    )


def _enable_gate(monkeypatch, practice: Practice) -> None:
    monkeypatch.setattr(
        settings, "b4_default_location_command_runtime_enabled", True
    )
    monkeypatch.setattr(
        settings,
        "b4_default_location_command_synthetic_practice_ids",
        str(practice.id),
    )
    monkeypatch.setattr(
        settings,
        "b4_default_location_command_secret",
        B4_SECRET,
    )


def _set_practice_context(db, practice: Practice) -> None:
    db.execute(
        text("SELECT set_config('app.current_practice_id', :pid, true)"),
        {"pid": str(practice.id)},
    )


def _practice_ref(practice: Practice) -> str:
    return f"practice_{practice.id.hex}"


def _actor_ref(user: User) -> str:
    return f"user_{user.id.hex}"


def _correlation() -> str:
    return f"corr-{uuid.uuid4().hex[:24]}"


def _idem_key(prefix: str = "idem") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:24]}"


def _headers(user: User, correlation_id: str, idem_key: str | None = None):
    headers = {
        "Authorization": f"Bearer {_token(user)}",
        "Idempotency-Key": idem_key or _idem_key(),
        "X-Correlation-Id": correlation_id,
    }
    return headers


def _location_refs(db, practice_id: uuid.UUID) -> dict[uuid.UUID, str]:
    registry = service._build_registry(
        db,
        practice_id=practice_id,
        practice_ref=f"practice_{practice_id.hex}",
        secret=B4_SECRET.encode("utf-8"),
    )
    return registry.ref_by_location


def _practitioner_refs(db, practice_id: uuid.UUID) -> dict[uuid.UUID, str]:
    registry = service._build_registry(
        db,
        practice_id=practice_id,
        practice_ref=f"practice_{practice_id.hex}",
        secret=B4_SECRET.encode("utf-8"),
    )
    return registry.ref_by_practitioner


@pytest.fixture
def b4_data(db):
    practice = Practice(name="B4 Practice")
    db.add(practice)
    db.flush()
    location_a = PracticeLocation(
        practice_id=practice.id, name="Location A", is_active=True
    )
    location_b = PracticeLocation(
        practice_id=practice.id, name="Location B", is_active=True
    )
    db.add_all([location_a, location_b])
    db.flush()
    practitioner = Practitioner(
        practice_id=practice.id,
        first_name="Ada",
        last_name="Lovelace",
        is_active=True,
        default_location_id=location_a.id,
        aggregate_version=0,
    )
    db.add(practitioner)
    db.flush()
    admin = User(
        practice_id=practice.id,
        email="admin@b4.test",
        password_hash=hash_password("Password1!"),
        role=UserRole.Admin,
        is_active=True,
    )
    owner = User(
        practice_id=practice.id,
        email="owner@b4.test",
        password_hash=hash_password("Password1!"),
        role=UserRole.PracticeOwner,
        is_active=True,
    )
    gp = User(
        practice_id=practice.id,
        email="gp@b4.test",
        password_hash=hash_password("Password1!"),
        role=UserRole.GP,
        is_active=True,
    )
    rec = User(
        practice_id=practice.id,
        email="rec@b4.test",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
        is_active=True,
    )
    nurse = User(
        practice_id=practice.id,
        email="nurse@b4.test",
        password_hash=hash_password("Password1!"),
        role=UserRole.Nurse,
        is_active=True,
    )
    db.add_all([admin, owner, gp, rec, nurse])
    db.flush()
    loc_refs = _location_refs(db, practice.id)
    prac_refs = _practitioner_refs(db, practice.id)
    # Route-level rollback is correct for a request transaction. Commit the
    # authored-synthetic fixture first so a rejected request cannot roll back
    # the identities and resources used by a later request in the same test.
    db.commit()
    return {
        "practice": practice,
        "location_a": location_a,
        "location_b": location_b,
        "practitioner": practitioner,
        "admin": admin,
        "owner": owner,
        "gp": gp,
        "rec": rec,
        "nurse": nurse,
        "practitioner_ref": prac_refs[practitioner.id],
        "location_a_ref": loc_refs[location_a.id],
        "location_b_ref": loc_refs[location_b.id],
    }


def _binding(data: dict[str, Any], user: User, role: str, correlation_id: str) -> dict[str, Any]:
    return {
        "practice_ref": _practice_ref(data["practice"]),
        "actor": {
            "actor_ref": _actor_ref(user),
            "actor_type": "human_user",
            "role": role,
        },
        "source_surface": "practice_administration_console",
        "correlation_id": correlation_id,
        "requested_at": "2026-08-05T00:00:00+00:00",
    }


def _default_dry_run_expires_at() -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()


def _proposal_body(
    data: dict[str, Any],
    user: User,
    role: str,
    correlation_id: str,
    *,
    requested_loc_ref: str | None = None,
    expected_version: int = 0,
    dry_run_expires_at: str | None = None,
    tamper: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "schema_version": PROPOSAL_REQUEST_SCHEMA,
        "operation": "PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
        "binding": _binding(data, user, role, correlation_id),
        "practitioner_ref": data["practitioner_ref"],
        "requested_default_location_ref": requested_loc_ref or data["location_b_ref"],
        "expected_aggregate_version": expected_version,
        "dry_run_proposal_hash": "0" * 64,
        "dry_run_context_revision": "1" * 64,
        "dry_run_expires_at": dry_run_expires_at or _default_dry_run_expires_at(),
    }
    if tamper:
        body.update(tamper)
    return body


def _propose(
    client,
    data: dict[str, Any],
    user: User,
    role: str,
    correlation_id: str,
    idem_key: str | None = None,
    **kwargs: Any,
):
    body = _proposal_body(data, user, role, correlation_id, **kwargs)
    return client.post(
        PROPOSAL_PATH,
        json=body,
        headers=_headers(user, correlation_id, idem_key),
    )


def _evidence_body(
    data: dict[str, Any],
    user: User,
    role: str,
    correlation_id: str,
    proposal: dict[str, Any],
    *,
    tamper: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "schema_version": EVIDENCE_REQUEST_SCHEMA,
        "operation": "CONFIRM_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
        "confirmed": True,
        "binding": _binding(data, user, role, correlation_id),
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["proposal_hash"],
        "proposal_expires_at": proposal["expires_at"],
        "practitioner_ref": data["practitioner_ref"],
        "requested_default_location_ref": data["location_b_ref"],
        "expected_aggregate_version": proposal["expected_aggregate_version"],
    }
    if tamper:
        body.update(tamper)
    return body


def _issue_evidence(
    client,
    data: dict[str, Any],
    user: User,
    role: str,
    correlation_id: str,
    proposal: dict[str, Any],
    idem_key: str | None = None,
    **kwargs: Any,
):
    body = _evidence_body(data, user, role, correlation_id, proposal, **kwargs)
    return client.post(
        EVIDENCE_PATH.format(proposal_id=proposal["proposal_id"]),
        json=body,
        headers=_headers(user, correlation_id, idem_key),
    )


def _confirm_body(
    data: dict[str, Any],
    user: User,
    role: str,
    correlation_id: str,
    proposal: dict[str, Any],
    evidence: dict[str, Any],
    *,
    tamper: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "schema_version": CONFIRM_COMMAND_SCHEMA,
        "operation": "CONFIRM_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
        "confirmed": True,
        "binding": _binding(data, user, role, correlation_id),
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["proposal_hash"],
        "proposal_expires_at": proposal["expires_at"],
        "practitioner_ref": data["practitioner_ref"],
        "requested_default_location_ref": data["location_b_ref"],
        "expected_aggregate_version": proposal["expected_aggregate_version"],
        "confirmation_evidence_ref": evidence["confirmation_evidence_ref"],
    }
    if tamper:
        body.update(tamper)
    return body


def _confirm(
    client,
    data: dict[str, Any],
    user: User,
    role: str,
    correlation_id: str,
    proposal: dict[str, Any],
    evidence: dict[str, Any],
    idem_key: str | None = None,
    **kwargs: Any,
):
    body = _confirm_body(data, user, role, correlation_id, proposal, evidence, **kwargs)
    return client.post(
        CONFIRM_PATH.format(proposal_id=proposal["proposal_id"]),
        json=body,
        headers=_headers(user, correlation_id, idem_key),
    )


def _happy_flow(
    client,
    data: dict[str, Any],
    user: User,
    role: str,
    correlation_id: str,
):
    proposal_resp = _propose(client, data, user, role, correlation_id)
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    evidence_resp = _issue_evidence(client, data, user, role, correlation_id, proposal)
    assert evidence_resp.status_code == 200, evidence_resp.text
    evidence = evidence_resp.json()
    confirm_resp = _confirm(
        client, data, user, role, correlation_id, proposal, evidence
    )
    return proposal, evidence, confirm_resp


def _b4_table_counts(db, practice: Practice) -> dict[str, int]:
    counts: dict[str, int] = {}
    _set_practice_context(db, practice)
    for table in B4_TABLES:
        counts[table] = db.execute(text(f"SELECT count(*) FROM {table}")).scalar()
    return counts


def test_default_off_rejects_before_lookup(client, b4_data, db) -> None:
    corr = _correlation()
    body = _proposal_body(b4_data, b4_data["admin"], "practice_manager", corr)
    resp = client.post(
        PROPOSAL_PATH,
        json=body,
        headers=_headers(b4_data["admin"], corr),
    )
    assert resp.status_code == 403
    assert resp.json()["status"] == "rejected"
    assert resp.json()["reason_code"] == "not_authorized"
    assert _b4_table_counts(db, b4_data["practice"]) == {
        table: 0 for table in B4_TABLES
    }


def test_non_allowlisted_practice_rejects_before_lookup(
    monkeypatch, client, b4_data
) -> None:
    monkeypatch.setattr(settings, "b4_default_location_command_runtime_enabled", True)
    monkeypatch.setattr(
        settings,
        "b4_default_location_command_synthetic_practice_ids",
        str(uuid.uuid4()),
    )
    monkeypatch.setattr(settings, "b4_default_location_command_secret", B4_SECRET)
    corr = _correlation()
    resp = _propose(client, b4_data, b4_data["admin"], "practice_manager", corr)
    assert resp.status_code == 403
    assert resp.json()["reason_code"] == "not_authorized"


def test_missing_or_invalid_secret_fails_closed(
    monkeypatch, client, b4_data
) -> None:
    monkeypatch.setattr(settings, "b4_default_location_command_runtime_enabled", True)
    monkeypatch.setattr(
        settings,
        "b4_default_location_command_synthetic_practice_ids",
        str(b4_data["practice"].id),
    )
    for secret in ("", "short"):
        monkeypatch.setattr(settings, "b4_default_location_command_secret", secret)
        corr = _correlation()
        resp = _propose(client, b4_data, b4_data["admin"], "practice_manager", corr)
        assert resp.status_code == 403
        assert resp.json()["reason_code"] == "not_authorized"


@pytest.mark.parametrize(
    "role_attr",
    ["gp", "rec", "nurse"],
)
def test_unauthorized_roles_reject_before_disclosure(
    monkeypatch, client, b4_data, role_attr
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data[role_attr]
    corr = _correlation()
    # The body assertion is a permitted enum value; the server must still
    # reject the non-Admin/PracticeOwner session before any resource lookup.
    resp = _propose(client, b4_data, user, "practice_manager", corr)
    assert resp.status_code == 403
    assert resp.json()["reason_code"] == "confirmer_not_authorized"


@pytest.mark.parametrize(
    "role_attr,expected_role",
    [("admin", "practice_manager"), ("owner", "practice_owner")],
)
def test_exact_allowed_roles_propose(
    monkeypatch, client, b4_data, role_attr, expected_role
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data[role_attr]
    corr = _correlation()
    resp = _propose(client, b4_data, user, expected_role, corr)
    assert resp.status_code == 200, resp.text
    envelope = resp.json()
    assert envelope["status"] == "proposal_only"
    assert envelope["applies_change"] is False
    assert envelope["davida_can_confirm"] is False
    assert envelope["maximum_lifetime_seconds"] == 120
    assert envelope["permitted_confirmer_roles"] == [
        "practice_manager",
        "practice_owner",
    ]


def test_exact_server_role_mapping_body_mismatch(
    monkeypatch, client, b4_data
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    corr = _correlation()
    # Admin maps to practice_manager; sending practice_owner must reject.
    resp = _propose(
        client, b4_data, b4_data["admin"], "practice_owner", corr
    )
    assert resp.status_code == 403
    assert resp.json()["reason_code"] == "practice_scope_mismatch"


def test_required_bounded_headers(monkeypatch, client, b4_data) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    body = _proposal_body(b4_data, user, "practice_manager", corr)

    missing_key = client.post(
        PROPOSAL_PATH,
        json=body,
        headers={"Authorization": f"Bearer {_token(user)}", "X-Correlation-Id": corr},
    )
    assert missing_key.status_code == 422
    assert missing_key.json()["reason_code"] == "invalid_envelope"

    missing_corr = client.post(
        PROPOSAL_PATH,
        json=body,
        headers={"Authorization": f"Bearer {_token(user)}", "Idempotency-Key": _idem_key()},
    )
    assert missing_corr.status_code == 422
    assert missing_corr.json()["reason_code"] == "invalid_envelope"

    short_key = client.post(
        PROPOSAL_PATH,
        json=body,
        headers=_headers(user, corr, idem_key="ab"),
    )
    assert short_key.status_code == 422
    assert short_key.json()["reason_code"] == "invalid_envelope"


def test_correlation_mismatch_rejects(monkeypatch, client, b4_data) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    other_corr = _correlation()
    body = _proposal_body(b4_data, user, "practice_manager", other_corr)
    resp = client.post(
        PROPOSAL_PATH,
        json=body,
        headers=_headers(user, corr),
    )
    assert resp.status_code == 403
    assert resp.json()["reason_code"] == "practice_scope_mismatch"


def test_zero_write_proposal(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    before_practitioner = b4_data["practitioner"]
    before_counts = _b4_table_counts(db, b4_data["practice"])
    resp = _propose(client, b4_data, user, "practice_manager", corr)
    assert resp.status_code == 200, resp.text
    after_counts = _b4_table_counts(db, b4_data["practice"])
    assert after_counts == before_counts == {table: 0 for table in B4_TABLES}
    db.refresh(before_practitioner)
    assert before_practitioner.default_location_id == b4_data["location_a"].id
    assert before_practitioner.aggregate_version == 0


def test_no_op_rejected(monkeypatch, client, b4_data) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    corr = _correlation()
    resp = _propose(
        client,
        b4_data,
        b4_data["admin"],
        "practice_manager",
        corr,
        requested_loc_ref=b4_data["location_a_ref"],
    )
    assert resp.status_code == 409
    assert resp.json()["reason_code"] == "no_change"


def test_stale_aggregate_version_rejected(monkeypatch, client, b4_data) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    corr = _correlation()
    resp = _propose(
        client,
        b4_data,
        b4_data["admin"],
        "practice_manager",
        corr,
        expected_version=7,
    )
    assert resp.status_code == 409
    assert resp.json()["reason_code"] == "aggregate_version_mismatch"


def test_inactive_and_foreign_resource_rejected(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    # Foreign/unresolvable practitioner ref rejects before disclosure.
    resp = client.post(
        PROPOSAL_PATH,
        json=_proposal_body(
            b4_data, user, "practice_manager", corr, requested_loc_ref="prac_synth_9999"
        ),
        headers=_headers(user, corr),
    )
    assert resp.status_code == 403
    assert resp.json()["reason_code"] == "resource_scope_mismatch"

    # Inactive location is not resolvable.
    b4_data["location_b"].is_active = False
    db.flush()
    resp2 = _propose(client, b4_data, user, "practice_manager", corr)
    assert resp2.status_code == 403
    assert resp2.json()["reason_code"] == "resource_scope_mismatch"


def test_tampered_proposal_signature_rejected(
    monkeypatch, client, b4_data
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    tampered = dict(proposal)
    tampered["proposal_id"] = proposal["proposal_id"][:-1] + (
        "A" if proposal["proposal_id"][-1] != "A" else "B"
    )
    resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, tampered)
    assert resp.status_code == 409
    assert resp.json()["reason_code"] == "proposal_hash_mismatch"


def test_expired_proposal_rejected(monkeypatch, client, b4_data) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    now = datetime(2026, 8, 5, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(service, "_now", lambda: now)
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(
        client,
        b4_data,
        user,
        "practice_manager",
        corr,
        dry_run_expires_at="2026-08-05T00:05:00+00:00",
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    monkeypatch.setattr(service, "_now", lambda: now + timedelta(minutes=3))
    resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    assert resp.status_code == 410
    assert resp.json()["reason_code"] == "proposal_expired"


def test_current_state_drift_before_state_conflict(
    monkeypatch, client, b4_data, db
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    location_c = PracticeLocation(
        practice_id=b4_data["practice"].id, name="Location C", is_active=True
    )
    db.add(location_c)
    db.flush()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    # Drift current truth so the proposal's before-state no longer matches.
    b4_data["practitioner"].default_location_id = location_c.id
    db.flush()
    resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    assert resp.status_code == 409
    assert resp.json()["reason_code"] == "before_state_conflict"


def test_evidence_exact_retry_returns_same_reference(
    monkeypatch, client, b4_data
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    first = _issue_evidence(
        client, b4_data, user, "practice_manager", corr, proposal, idem_key=_idem_key("idem-ev")
    )
    assert first.status_code == 200, first.text
    second = _issue_evidence(
        client, b4_data, user, "practice_manager", corr, proposal, idem_key=_idem_key("idem-ev")
    )
    assert second.status_code == 200, second.text
    assert (
        first.json()["confirmation_evidence_ref"]
        == second.json()["confirmation_evidence_ref"]
    )


def test_evidence_changed_payload_conflicts(monkeypatch, client, b4_data) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    body = _evidence_body(b4_data, user, "practice_manager", corr, proposal)
    body["binding"]["requested_at"] = "2026-08-05T00:01:00+00:00"
    resp = client.post(
        EVIDENCE_PATH.format(proposal_id=proposal["proposal_id"]),
        json=body,
        headers=_headers(user, corr),
    )
    assert resp.status_code == 409
    assert resp.json()["reason_code"] == "idempotency_conflict"


def test_evidence_consumed_requires_fresh_attestation(
    monkeypatch, client, b4_data
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal, _evidence, confirm_resp = _happy_flow(
        client, b4_data, user, "practice_manager", corr
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    assert resp.status_code == 409
    assert resp.json()["reason_code"] == "confirmation_replay_rejected"


def test_confirm_expired_evidence(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    now = datetime(2026, 8, 5, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(service, "_now", lambda: now)
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    assert ev_resp.status_code == 200, ev_resp.text
    evidence = ev_resp.json()
    _set_practice_context(db, b4_data["practice"])
    row = (
        db.query(PracticeAdministrationConfirmationEvidence)
        .filter(
            PracticeAdministrationConfirmationEvidence.nonce
            == evidence["confirmation_evidence_ref"]
        )
        .one()
    )
    row.expires_at = now + timedelta(seconds=1)
    db.commit()
    monkeypatch.setattr(service, "_now", lambda: now + timedelta(seconds=2))
    confirm_resp = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence
    )
    assert confirm_resp.status_code == 410
    assert confirm_resp.json()["reason_code"] == "confirmation_evidence_expired"


def test_confirm_success_aggregate_version_audit_outbox_readback(
    monkeypatch, client, b4_data, db
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal, evidence, confirm_resp = _happy_flow(
        client, b4_data, user, "practice_manager", corr
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    result = confirm_resp.json()
    receipt = result["receipt"]
    assert receipt["outcome"] == "practitioner_default_location_updated"
    assert receipt["expected_aggregate_version"] == 0
    assert receipt["resulting_aggregate_version"] == 1
    assert receipt["before_location_ref"] == b4_data["location_a_ref"]
    assert receipt["after_location_ref"] == b4_data["location_b_ref"]
    assert receipt["confirmed_by_role"] == "practice_manager"
    assert receipt["verification"]["publication_after_commit_only"] is True

    db.refresh(b4_data["practitioner"])
    assert b4_data["practitioner"].default_location_id == b4_data["location_b"].id
    assert b4_data["practitioner"].aggregate_version == 1

    _set_practice_context(db, b4_data["practice"])
    audit = db.query(PracticeAdministrationAuditEvent).one()
    outbox = db.query(PracticeAdministrationOutboxEvent).one()
    assert audit.action == "practitioner_default_location_changed"
    assert audit.before_location_id == b4_data["location_a"].id
    assert audit.after_location_id == b4_data["location_b"].id
    assert audit.expected_aggregate_version == 0
    assert audit.resulting_aggregate_version == 1
    assert audit.proposal_hash == proposal["proposal_hash"]
    assert outbox.event_type == "practice.practitioner_default_location_changed"
    assert (
        outbox.schema_version
        == "practice.practitioner_default_location_changed.v1"
    )
    assert outbox.source_system == "emr4-practice-administration"
    assert outbox.published is False
    assert outbox.payload["practitioner_id"] == str(b4_data["practitioner"].id)
    assert outbox.payload["before_location_id"] == str(b4_data["location_a"].id)
    assert outbox.payload["after_location_id"] == str(b4_data["location_b"].id)
    assert outbox.payload["aggregate_version"] == 1
    assert outbox.payload["reason_codes"] == [
        "practitioner_default_location_changed"
    ]
    idem_row = db.query(PracticeAdministrationCommandIdempotency).one()
    assert idem_row.state == "completed"
    assert idem_row.result_kind == "practitioner_default_location_updated"
    assert idem_row.receipt_id == receipt["receipt_id"]
    assert idem_row.audit_event_id == audit.id
    assert idem_row.outbox_event_id == outbox.id
    assert idem_row.confirmation_evidence_id is not None


def test_same_key_replay_returns_stored_receipt(
    monkeypatch, client, b4_data, db
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    evidence = ev_resp.json()
    key = _idem_key("idem-cf")
    first = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence,
        idem_key=key,
    )
    assert first.status_code == 200, first.text
    second = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence,
        idem_key=key,
    )
    assert second.status_code == 200, second.text
    assert second.headers.get("Idempotent-Replayed") == "true"
    assert second.json() == first.json()
    _set_practice_context(db, b4_data["practice"])
    assert db.query(PracticeAdministrationAuditEvent).count() == 1
    assert db.query(PracticeAdministrationOutboxEvent).count() == 1


def test_same_key_changed_fingerprint_conflicts(
    monkeypatch, client, b4_data
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    evidence = ev_resp.json()
    key = _idem_key("idem-cf")
    first = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence,
        idem_key=key,
    )
    assert first.status_code == 200, first.text
    changed_body = _confirm_body(
        b4_data, user, "practice_manager", corr, proposal, evidence
    )
    changed_body["binding"]["requested_at"] = "2026-08-05T00:02:00+00:00"
    second = client.post(
        CONFIRM_PATH.format(proposal_id=proposal["proposal_id"]),
        json=changed_body,
        headers=_headers(user, corr, idem_key=key),
    )
    assert second.status_code == 409
    assert second.json()["reason_code"] == "idempotency_conflict"


def test_in_progress_denial(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    evidence = ev_resp.json()
    key = _idem_key("idem-cf")
    body = _confirm_body(
        b4_data, user, "practice_manager", corr, proposal, evidence
    )
    canonical_request_hash = service._sha256(
        service.DefaultLocationConfirmationCommand.model_validate(body).model_dump(
            mode="json"
        )
    )
    proposal_hash = proposal["proposal_hash"]
    fingerprint = service._sha256(
        {
            "canonical_request_hash": canonical_request_hash,
            "proposal_hash": proposal_hash,
        }
    )
    idem_hash = service.hash_idempotency_key(key, B4_SECRET.encode())
    _set_practice_context(db, b4_data["practice"])
    db.add(
        PracticeAdministrationCommandIdempotency(
            practice_id=b4_data["practice"].id,
            actor_user_id=user.id,
            actor_role="practice_manager",
            operation_id="confirmPractitionerDefaultLocationChange",
            route_family="practice_administration_default_location",
            idempotency_key_hash=idem_hash,
            request_body_hash=fingerprint,
            canonical_request_hash=canonical_request_hash,
            proposal_hash=proposal_hash,
            state="in_progress",
        )
    )
    db.flush()
    resp = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence,
        idem_key=key,
    )
    assert resp.status_code == 409
    assert resp.json()["reason_code"] == "idempotency_in_progress"


def test_different_key_evidence_replay_rejected(
    monkeypatch, client, b4_data
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal, evidence, confirm_resp = _happy_flow(
        client, b4_data, user, "practice_manager", corr
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    replay = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence
    )
    assert replay.status_code == 409
    assert replay.json()["reason_code"] == "confirmation_replay_rejected"


def test_concurrent_distinct_keys_single_winner(
    monkeypatch, client, b4_data
) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    evidence = ev_resp.json()
    winner = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence,
        idem_key=_idem_key("idem-cf"),
    )
    assert winner.status_code == 200, winner.text
    loser = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence,
        idem_key=_idem_key("idem-cf"),
    )
    assert loser.status_code == 409
    assert loser.json()["reason_code"] == "confirmation_replay_rejected"


def test_rollback_on_commit_failure(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    evidence = ev_resp.json()

    def boom() -> None:
        raise RuntimeError("injected commit failure")

    monkeypatch.setattr(db, "commit", boom)
    resp = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence
    )
    assert resp.status_code == 500
    assert resp.json()["reason_code"] == "atomic_transaction_failed"

    _set_practice_context(db, b4_data["practice"])
    db.expire_all()
    assert b4_data["practitioner"].aggregate_version == 0
    assert b4_data["practitioner"].default_location_id == b4_data["location_a"].id
    assert db.query(PracticeAdministrationAuditEvent).count() == 0
    assert db.query(PracticeAdministrationOutboxEvent).count() == 0
    assert db.query(PracticeAdministrationCommandIdempotency).count() == 0
    evidence_row = db.query(PracticeAdministrationConfirmationEvidence).one()
    assert evidence_row.state == "live"


def test_rollback_on_audit_append_failure(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    evidence = ev_resp.json()

    def boom(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("injected audit append failure")

    monkeypatch.setattr(service, "PracticeAdministrationAuditEvent", boom)
    resp = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence
    )
    assert resp.status_code == 500
    assert resp.json()["reason_code"] == "atomic_transaction_failed"

    _set_practice_context(db, b4_data["practice"])
    db.expire_all()
    assert b4_data["practitioner"].aggregate_version == 0
    assert b4_data["practitioner"].default_location_id == b4_data["location_a"].id
    assert db.query(PracticeAdministrationAuditEvent).count() == 0
    assert db.query(PracticeAdministrationOutboxEvent).count() == 0
    assert db.query(PracticeAdministrationCommandIdempotency).count() == 0
    evidence_row = db.query(PracticeAdministrationConfirmationEvidence).one()
    assert evidence_row.state == "live"


def test_rollback_on_outbox_append_failure(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal_resp = _propose(client, b4_data, user, "practice_manager", corr)
    proposal = proposal_resp.json()
    ev_resp = _issue_evidence(client, b4_data, user, "practice_manager", corr, proposal)
    evidence = ev_resp.json()

    def boom(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("injected outbox append failure")

    monkeypatch.setattr(service, "PracticeAdministrationOutboxEvent", boom)
    resp = _confirm(
        client, b4_data, user, "practice_manager", corr, proposal, evidence
    )
    assert resp.status_code == 500
    assert resp.json()["reason_code"] == "atomic_transaction_failed"

    _set_practice_context(db, b4_data["practice"])
    db.expire_all()
    assert b4_data["practitioner"].aggregate_version == 0
    assert b4_data["practitioner"].default_location_id == b4_data["location_a"].id
    assert db.query(PracticeAdministrationAuditEvent).count() == 0
    assert db.query(PracticeAdministrationOutboxEvent).count() == 0
    assert db.query(PracticeAdministrationCommandIdempotency).count() == 0
    evidence_row = db.query(PracticeAdministrationConfirmationEvidence).one()
    assert evidence_row.state == "live"


def test_migration_enforces_forced_rls_cross_practice_denial() -> None:
    migration = (
        ROOT
        / "alembic"
        / "versions"
        / "v1w2x3y4z5b6_add_b4_default_location_runtime.py"
    ).read_text(encoding="utf-8")
    tables = (
        "practice_administration_confirmation_evidence",
        "practice_administration_command_idempotency",
        "practice_administration_audit_events",
        "practice_administration_outbox_events",
    )
    assert "ENABLE ROW LEVEL SECURITY" in migration
    assert "FORCE ROW LEVEL SECURITY" in migration
    assert "USING ({_PRACTICE_CONTEXT}) WITH CHECK ({_PRACTICE_CONTEXT})" in migration
    assert migration.count("_enable_all_practice_policy(") == 5
    for table in tables:
        assert f'        "{table}",' in migration
        assert "current_setting('app.current_practice_id', true)" in migration


def test_migration_enforces_append_only_audit_and_outbox() -> None:
    migration = (
        ROOT
        / "alembic"
        / "versions"
        / "v1w2x3y4z5b6_add_b4_default_location_runtime.py"
    ).read_text(encoding="utf-8")
    assert (
        "BEFORE UPDATE OR DELETE ON practice_administration_audit_events"
        in migration
    )
    assert (
        "BEFORE UPDATE OR DELETE ON practice_administration_outbox_events"
        in migration
    )
    assert "emr4_reject_b4_audit_mutation" in migration
    assert "emr4_reject_b4_outbox_mutation" in migration
    assert "append-only" in migration


def test_outbox_unpublished_event(monkeypatch, client, b4_data, db) -> None:
    _enable_gate(monkeypatch, b4_data["practice"])
    user = b4_data["admin"]
    corr = _correlation()
    proposal, evidence, confirm_resp = _happy_flow(
        client, b4_data, user, "practice_manager", corr
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    _set_practice_context(db, b4_data["practice"])
    outbox = db.query(PracticeAdministrationOutboxEvent).one()
    assert outbox.published is False
    assert outbox.event_type == "practice.practitioner_default_location_changed"
    assert (
        outbox.schema_version
        == "practice.practitioner_default_location_changed.v1"
    )


def test_no_raw_secrets_patient_or_provider_stored() -> None:
    models = (
        PracticeAdministrationConfirmationEvidence,
        PracticeAdministrationCommandIdempotency,
        PracticeAdministrationAuditEvent,
        PracticeAdministrationOutboxEvent,
    )
    forbidden_columns = (
        "idempotency_key",
        "session_secret",
        "password",
        "patient_id",
        "patient_name",
        "provider_output",
        "free_text",
        "display_name",
        "clinical",
        "token",
        "nonce_plaintext",
    )
    for model in models:
        column_names = {column.name for column in model.__table__.columns}
        for forbidden in forbidden_columns:
            assert forbidden not in column_names, (
                model.__tablename__,
                forbidden,
            )
    idem_columns = {
        column.name for column in PracticeAdministrationCommandIdempotency.__table__.columns
    }
    assert "idempotency_key_hash" in idem_columns
    assert "request_body_hash" in idem_columns
    assert "canonical_request_hash" in idem_columns
    assert "response_body_json" in idem_columns


def test_zero_product_provider_calls() -> None:
    source = (
        ROOT
        / "app/services/practice/"
        "practice_administration_default_location_command.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("google", "vertex", "openai", "anthropic", "requests", "httpx")
    for item in imported:
        lowered = item.lower()
        for token in forbidden:
            assert token not in lowered, (item, token)


def test_openapi_three_route_parity() -> None:
    yaml = pytest.importorskip("yaml")
    api = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    expected_paths = {
        "/practice-administration/practitioners/default-location/proposals",
        "/practice-administration/practitioners/default-location/proposals/{proposal_id}/confirmation-evidence",
        "/practice-administration/practitioners/default-location/proposals/{proposal_id}/confirm",
    }
    assert set(api["paths"]) == expected_paths
    assert api["x-emr4-boundary"]["status"] == "authorized_local_runtime"
    assert api["x-emr4-boundary"]["actual_command_implementation_authorized"] is True
    assert api["x-emr4-boundary"]["actual_write_authority"] is True
    assert api["components"]["schemas"]["SignedProposalRef"]["maxLength"] == 4096
    assert PracticeAdministrationConfirmationEvidence.__table__.c.proposal_id.type.length == 4096

    openapi_rejection_codes = api["components"]["schemas"]["Rejection"]["properties"][
        "reason_code"
    ]["enum"]
    assert openapi_rejection_codes == list(REJECTION_CODES)

    # Every route carries the bounded headers.
    for path in expected_paths:
        parameters = api["paths"][path]["post"]["parameters"]
        names = {
            (
                api["components"]["parameters"][
                    parameter["$ref"].rsplit("/", 1)[-1]
                ]["name"]
                if "$ref" in parameter
                else parameter["name"]
            )
            for parameter in parameters
        }
        assert {"Idempotency-Key", "X-Correlation-Id"} <= names

    evidence = api["paths"][
        "/practice-administration/practitioners/default-location/proposals/{proposal_id}/confirmation-evidence"
    ]["post"]
    assert evidence["x-emr4-effect"] == "none"
    assert evidence["x-emr4-zero-domain-mutation"] is True
    assert evidence["x-emr4-role-normalization"]["server_enum_to_runtime_role"] == {
        "Admin": "practice_manager",
        "PracticeOwner": "practice_owner",
    }
    assert evidence["x-emr4-role-normalization"]["aliases"] is False

    # Mounted FastAPI routes match the YAML paths and operation ids.
    from app.main import app

    openapi = app.openapi()
    mounted = {
        path: openapi["paths"][path]["post"]["operationId"]
        for path in openapi["paths"]
        if path.startswith("/api/v1/practice-administration")
    }
    assert set(mounted) == {"/api/v1" + path for path in expected_paths}
    for path in expected_paths:
        operation_id = api["paths"][path]["post"]["operationId"]
        assert mounted["/api/v1" + path] == operation_id


def test_one_alembic_head() -> None:
    import alembic.config
    import alembic.script

    cfg = alembic.config.Config(str(ROOT / "alembic.ini"))
    script = alembic.script.ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    assert heads == ["v1w2x3y4z5b6"], heads

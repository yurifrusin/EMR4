"""Provider-free focused route tests for the delete-confirm HTTP route convergence.

Runs with ``--noconftest`` using in-memory dependency/adapter stubs and no
database connection. The accepted delete product adapter is stubbed at the route
boundary so the transport contract (one adapter call, server-owned ingress,
canonical public bytes, never private stored bytes, hidden alias) is verified.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies import get_command_session_factory, get_current_user
from app.models.tenancy import UserRole
from app.routers.appointments import router as appointments_router
from app.schemas.appointments import (
    AppointmentConfirmDeleteProposalOut,
    AppointmentDeleteProposalConfirmationIn,
)
from app.services.appointment_delete_composition import (
    DeleteConfirmCompositionResult,
    canonical_delete_confirm_envelope_bytes,
    delete_confirm_envelope_projection,
)
from app.services.appointment_delete_product_adapter import (
    mint_delete_proposal_version_binding,
)
from app.services.bernie_turn_evidence import (
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    mint_signed_confirmation_evidence,
)

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_URL = "/api/v1/appointments/proposals/delete/confirm"
ALIAS_URL = "/api/v1/appointments/proposals/delete-confirm"

APP = FastAPI()
APP.include_router(appointments_router)


def _stub_user() -> SimpleNamespace:
    return SimpleNamespace(
        id="11111111-1111-4111-8111-111111111111",
        practice_id="22222222-2222-4222-8222-222222222222",
        role=UserRole.GP,
        is_active=True,
        authority_generation=1,
    )


def _client() -> TestClient:
    APP.dependency_overrides[get_current_user] = _stub_user
    APP.dependency_overrides[get_command_session_factory] = lambda: (lambda: None)
    # Do not re-raise unhandled endpoint exceptions so a hostile serialization
    # failure is observable as a 500 without private bytes.
    return TestClient(APP, raise_server_exceptions=False)


def _domain_secret(purpose: str) -> bytes:
    import hashlib
    import hmac

    from app.config import settings

    return hmac.new(
        settings.secret_key.encode("utf-8"),
        f"emr4.delete-confirm.{purpose}.v1".encode("utf-8"),
        hashlib.sha256,
    ).digest()


def _evidence_secret() -> str:
    return _domain_secret("evidence").hex()


def _signed_request_body() -> dict:
    from app.schemas.appointments import (
        AppointmentDeleteCommand,
        AppointmentDeleteProposalOut,
    )
    from app.services.appointment_delete_product_adapter import (
        delete_proposal_freshness_id,
    )

    appointment_id = "33333333-3333-4333-8333-333333333333"
    command = AppointmentDeleteCommand(
        appointment_id=appointment_id,
        clears_waiting_area=False,
        cancellation_reason=None,
        status_reason_code="PATIENT_TRANSPORT",
    )
    current_state = {
        "appointment_id": appointment_id,
        "status": "Booked",
        "waiting_area_id": None,
        "status_reason_code": "PATIENT_TRANSPORT",
        "cancellation_reason": None,
    }
    freshness_id = delete_proposal_freshness_id(command, current_state)
    signed_payload = {
        "practice_id": "22222222-2222-4222-8222-222222222222",
        "staff_user_id": "11111111-1111-4111-8111-111111111111",
        "current_state": current_state,
        "command": {
            "kind": "delete",
            "appointment_id": appointment_id,
            "clears_waiting_area": False,
            "cancellation_reason": None,
            "status_reason_code": "PATIENT_TRANSPORT",
        },
        "delete_proposal_freshness_id": freshness_id,
    }
    evidence = mint_signed_confirmation_evidence(
        signed_payload,
        evidence_purpose=SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
        secret=_evidence_secret(),
    )
    binding = mint_delete_proposal_version_binding(
        evidence,
        source_version=1,
        secret=_domain_secret("proposal-version"),
    )
    proposal = AppointmentDeleteProposalOut(
        intent="delete_appointment",
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Cancel appointment.",
        command=command,
        warnings=[],
        blocks=[],
        confirm_endpoint=CANONICAL_URL,
        delete_proposal_freshness_id=freshness_id,
        delete_proposal_version_binding=binding,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )
    body = AppointmentDeleteProposalConfirmationIn(
        confirmed=True,
        delete_proposal=proposal,
        confirmed_warnings=[],
        delete_proposal_freshness_id=freshness_id,
        delete_proposal_version_binding=binding,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )
    return body.model_dump(mode="json")


def _public_body() -> dict:
    from app.services.appointment_delete_physical import (
        canonical_delete_confirm_response_bytes,
    )

    private = canonical_delete_confirm_response_bytes(
        appointment_id="33333333-3333-4333-8333-333333333333",
        status_reason_code="PATIENT_TRANSPORT",
        cancellation_reason=None,
        warning_codes=[],
    )
    return delete_confirm_envelope_projection(private)


def _auth_headers(token: str = "test-bearer-token") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Idempotency-Key": "route-test-idem-key"}


# ── DHC-S02 / DHC-S04 / DHC-S10 route transport tests ───────────────────────

def test_route_calls_accepted_adapter_exactly_once_with_server_owned_ingress():
    client = _client()
    body = _signed_request_body()
    public_body = _public_body()
    stored = json.dumps({"private": "receipt"}).encode("utf-8")
    result = DeleteConfirmCompositionResult("committed", 200, public_body, stored)

    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
        return_value=result,
    ) as mocked:
        response = client.post(CANONICAL_URL, json=body, headers=_auth_headers())

    assert response.status_code == 200, response.text
    assert mocked.call_count == 1
    call = mocked.call_args
    assert call.kwargs["authenticated_bearer_token"] == "test-bearer-token"
    assert call.kwargs["idempotency_key"] == "route-test-idem-key"
    assert call.kwargs["proposal_version_binding"] == body["delete_proposal_version_binding"]
    assert call.kwargs["authenticated_user"].role is UserRole.GP
    assert call.kwargs["command_session_factory"] is not None
    assert set(call.kwargs) >= {
        "authenticated_session_secret",
        "proposal_version_binding_secret",
        "idempotency_secret",
        "session_binding_secret",
        "evidence_secret",
    }


def test_success_delivers_canonical_public_bytes_never_private_stored_bytes():
    client = _client()
    body = _signed_request_body()
    public_body = _public_body()
    public_bytes = canonical_delete_confirm_envelope_bytes(public_body)
    stored_bytes = json.dumps({"private": "receipt"}).encode("utf-8")
    result = DeleteConfirmCompositionResult("committed", 200, public_body, stored_bytes)

    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
        return_value=result,
    ):
        response = client.post(CANONICAL_URL, json=body, headers=_auth_headers())

    assert response.status_code == 200
    assert response.content == public_bytes
    assert response.content != stored_bytes
    assert response.json() == public_body
    assert "receipt" in response.json()


def test_committed_and_replay_return_byte_identical_public_bytes():
    client = _client()
    body = _signed_request_body()
    public_body = _public_body()
    public_bytes = canonical_delete_confirm_envelope_bytes(public_body)

    for kind, stored in (
        ("committed", json.dumps({"private": "a"}).encode("utf-8")),
        ("replay", json.dumps({"private": "b"}).encode("utf-8")),
    ):
        result = DeleteConfirmCompositionResult(kind, 200, public_body, stored)
        with patch(
            "app.routers.appointments.compose_product_delete_confirm",
            return_value=result,
        ):
            response = client.post(CANONICAL_URL, json=body, headers=_auth_headers())
        assert response.status_code == 200
        assert response.content == public_bytes


def test_alias_reaches_same_handler_and_returns_same_public_bytes():
    client = _client()
    body = _signed_request_body()
    public_body = _public_body()
    public_bytes = canonical_delete_confirm_envelope_bytes(public_body)
    result = DeleteConfirmCompositionResult("replay", 200, public_body, b"private")

    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
        return_value=result,
    ) as mocked:
        canonical_resp = client.post(CANONICAL_URL, json=body, headers=_auth_headers())
        alias_resp = client.post(ALIAS_URL, json=body, headers=_auth_headers())

    assert canonical_resp.status_code == 200
    assert alias_resp.status_code == 200
    assert alias_resp.content == public_bytes
    assert mocked.call_count == 2


def test_generated_openapi_contains_only_canonical_delete_confirm_path():
    paths = APP.openapi()["paths"]

    assert CANONICAL_URL in paths
    assert ALIAS_URL not in paths
    response_schema = paths[CANONICAL_URL]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert response_schema["$ref"].endswith("AppointmentConfirmDeleteProposalOut")


def test_blocked_outcome_returns_exact_adapter_status_and_body_no_fallback():
    client = _client()
    body = _signed_request_body()
    blocked_body = {
        "schema_version": "raisa.delete_confirm_public_envelope.v1",
        "intent": "confirm_delete_appointment",
        "safe": False,
        "requires_confirmation": True,
        "autonomy_tier": "blocked",
        "summary": "Cannot confirm delete proposal.",
        "receipt": None,
        "warnings": [],
        "blocks": [{"code": "explicit_confirmation_required", "severity": "blocked", "message": "x"}],
        "audit_evidence": [],
    }
    result = DeleteConfirmCompositionResult("blocked", 200, blocked_body, None)

    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
        return_value=result,
    ):
        response = client.post(CANONICAL_URL, json=body, headers=_auth_headers())

    assert response.status_code == 200
    assert response.json() == blocked_body


def test_error_outcome_returns_exact_adapter_status_and_body_no_fallback():
    client = _client()
    body = _signed_request_body()
    error_body = {"detail": {"code": "idempotency_key_required", "message": "x"}}
    result = DeleteConfirmCompositionResult("error", 409, error_body, None)

    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
        return_value=result,
    ):
        response = client.post(CANONICAL_URL, json=body, headers=_auth_headers())

    assert response.status_code == 409
    assert response.json() == error_body


def test_missing_idempotency_key_is_rejected_before_adapter_call():
    client = _client()
    body = _signed_request_body()
    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
    ) as mocked:
        response = client.post(
            CANONICAL_URL,
            json=body,
            headers={"Authorization": "Bearer test-bearer-token"},
        )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "idempotency_key_required"
    assert mocked.call_count == 0


def test_serialization_failure_of_bad_public_body_releases_no_private_bytes():
    client = _client()
    body = _signed_request_body()
    bad_public_body = {"not": "canonical"}
    stored = json.dumps({"private": "secret"}).encode("utf-8")
    result = DeleteConfirmCompositionResult("committed", 200, bad_public_body, stored)

    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
        return_value=result,
    ):
        response = client.post(CANONICAL_URL, json=body, headers=_auth_headers())

    assert response.status_code == 500
    assert b"private" not in response.content


@pytest.mark.parametrize(
    ("kind", "stored_response_bytes"),
    (("committed", None), ("error", b'{"private":"secret"}')),
)
def test_private_receipt_presence_is_exact_success_invariant(
    kind: str,
    stored_response_bytes: bytes | None,
):
    client = _client()
    body = _signed_request_body()
    public_body = _public_body()
    result = DeleteConfirmCompositionResult(
        kind,
        200,
        public_body,
        stored_response_bytes,
    )

    with patch(
        "app.routers.appointments.compose_product_delete_confirm",
        return_value=result,
    ):
        response = client.post(CANONICAL_URL, json=body, headers=_auth_headers())

    assert response.status_code == 500
    assert b"private" not in response.content


# ── DHC-S05 minimal public schema ────────────────────────────────────────────

def test_public_schema_forbids_extra_and_appointment_fields():
    from pydantic import ValidationError

    public_body = _public_body()
    assert AppointmentConfirmDeleteProposalOut.model_validate(public_body)

    for forbidden in ("appointment", "patient", "practitioner", "schedule", "notes", "audit_identity"):
        hostile = dict(public_body)
        hostile[forbidden] = {"leak": True}
        with pytest.raises(ValidationError):
            AppointmentConfirmDeleteProposalOut.model_validate(hostile)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("unknown", True),
        ("waiting_area_id", "44444444-4444-4444-8444-444444444444"),
        ("status_reason_code", None),
        ("status_reason_code", "UNKNOWN"),
        ("cancellation_reason", "x" * 501),
        ("warning_codes", ["unknown"]),
        ("warning_codes", ["waiting_area_cleared", "waiting_area_cleared"]),
    ),
)
def test_public_schema_rejects_widened_nested_receipt(field: str, value: object):
    from pydantic import ValidationError

    public_body = _public_body()
    public_body["receipt"][field] = value

    with pytest.raises(ValidationError):
        AppointmentConfirmDeleteProposalOut.model_validate(public_body)


def test_public_schema_rejects_unknown_or_partial_audit_labels():
    from pydantic import ValidationError

    for audit_evidence in (
        ["unknown_audit_label"],
        ["delete_product_adapter_v1"],
    ):
        public_body = _public_body()
        public_body["audit_evidence"] = audit_evidence
        with pytest.raises(ValidationError):
            AppointmentConfirmDeleteProposalOut.model_validate(public_body)


# ── DHC-S12 raw DELETE isolation ─────────────────────────────────────────────

def test_raw_delete_and_non_delete_families_unchanged():
    router_text = (ROOT / "app" / "routers" / "appointments.py").read_text(encoding="utf-8")
    assert 'def cancel_appointment(' in router_text
    assert '"raw_compat_delete"' in router_text
    assert 'def confirm_create_proposal_route(' in router_text
    assert 'def confirm_update_proposal_route(' in router_text
    assert 'def confirm_status_proposal_route(' in router_text

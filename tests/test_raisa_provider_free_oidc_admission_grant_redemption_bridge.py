from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.routers.application_auth import router
from app.schemas.application_identity_oidc_transport import (
    OIDCAdmissionGrantRedeemRequest,
)
from app.services.application_identity_oidc_redemption_database_role import (
    REDEMPTION_FUNCTION,
    create_redemption_capability_statements,
    create_redemption_login_statements,
)
from scripts.raisa_provider_free_oidc_admission_grant_redemption_bridge_acceptance import (
    RESULT,
    run_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "alembic/versions/t9u0v1w2x3y4_add_oidc_grant_redemption_bridge.py"
)
MODEL = ROOT / "app/models/application_auth.py"
FEDERATION_MODEL = ROOT / "app/models/application_identity_federation.py"
SERVICE = ROOT / "app/services/application_identity_oidc_redemption.py"
API_SPINE = (
    ROOT
    / "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml"
)
EVIDENCE = (
    ROOT
    / "orchestration/continuity/"
    "raisa-provider-free-oidc-admission-grant-redemption-bridge/"
    "live-local-http-backend-postgres-redemption-evidence.json"
)
RECEIPT = (
    ROOT
    / "orchestration/agent_inbox/codex/"
    "raisa-provider-free-oidc-admission-grant-redemption-bridge-"
    "rehydration-receipt.json"
)
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


def test_redemption_request_is_exact_and_strict() -> None:
    request = OIDCAdmissionGrantRedeemRequest(
        admission_grant="A" * 43,
        surface="word_online",
    )
    assert request.surface.value == "word_online"
    with pytest.raises(ValidationError):
        OIDCAdmissionGrantRedeemRequest(
            admission_grant="short",
            surface="word_online",
        )
    with pytest.raises(ValidationError):
        OIDCAdmissionGrantRedeemRequest(
            admission_grant="A" * 43,
            surface="word_online",
            return_url="https://foreign.invalid",
        )


def test_redemption_route_remains_default_off() -> None:
    application = FastAPI()
    application.include_router(router)
    response = TestClient(application).post(
        "/api/v1/application-auth/federation/session/redeem",
        json={"admission_grant": "A" * 43, "surface": "word_online"},
        headers={
            "Origin": "https://word-edit.officeapps.live.com",
            "X-EMR4-CSRF": "csrf." + "c" * 43,
        },
        cookies={"__Host-emr4-application-csrf": "csrf." + "c" * 43},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "application_auth_transport_unavailable"}
    assert "set-cookie" not in response.headers


def test_migration_encodes_atomic_lock_freshness_and_audit() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    assert "SECURITY DEFINER" in migration
    assert "SET search_path = ''" in migration
    assert "REVOKE ALL ON FUNCTION" in migration
    assert "FOR UPDATE" in migration
    assert migration.count("FOR KEY SHARE") == 2
    assert "WITH CHECK (false)" in migration
    assert "binding.version = v_grant.binding_version" in migration
    assert "binding.user_ref = v_grant.user_ref" in migration
    assert "binding.practice_ref = v_grant.practice_ref" in migration
    assert "truth.membership_active" in migration
    assert "truth.practitioner_link_active" in migration
    assert "federation.admission_grant_consumed" in migration
    assert "federation.admission_grant_rejected" in migration
    assert "SET status = 'consumed', version = 2" in migration
    assert "FORCE ROW LEVEL SECURITY" in migration


def test_roles_separate_execution_owner_and_session_dml() -> None:
    capabilities = "\n".join(
        create_redemption_capability_statements(
            call_role="emr4_oidc_redemption_call_12345678",
            owner_role="emr4_oidc_redemption_owner_12345678",
        )
    )
    login = "\n".join(
        create_redemption_login_statements(
            "emr4_oidc_redemption_login_12345678",
            call_role="emr4_oidc_redemption_call_12345678",
            connection_limit=2,
        )
    )
    assert f"ALTER FUNCTION {REDEMPTION_FUNCTION} OWNER TO" in capabilities
    assert (
        "GRANT UPDATE (status, version, consumed_at) ON TABLE "
        'public."application_identity_federation_admission_grants"'
        in capabilities
    )
    assert (
        "GRANT UPDATE (updated_at) ON TABLE "
        'public."application_identity_federation_bindings", '
        'public."application_auth_synthetic_principal_truth"'
        in capabilities
    )
    assert (
        "GRANT SELECT, INSERT, UPDATE ON TABLE "
        'public."application_auth_principal_generations"'
        in capabilities
    )
    assert "NOINHERIT" in login
    assert "NOBYPASSRLS" in login
    assert "redemption_owner" not in login


def test_source_and_api_spine_keep_real_identity_and_product_closed() -> None:
    model = MODEL.read_text(encoding="utf-8")
    federation_model = FEDERATION_MODEL.read_text(encoding="utf-8")
    service = SERVICE.read_text(encoding="utf-8")
    api = API_SPINE.read_text(encoding="utf-8")
    assert "application_auth_synthetic_principal_truth" in model
    assert "authored_synthetic" in model
    assert "raw_grant" not in model
    assert "federation.admission_grant_consumed" in federation_model
    assert "patient" not in service.lower()
    assert "appointment" not in service.lower()
    assert "0.5.0-provider-free-redemption" in api
    assert "provider_free_atomic_redemption_mounted_default_off" in api
    assert "csrf_token" in api
    assert "callback_sets_session_cookie: false" in api
    assert "product_access" in api


def test_committed_evidence_is_sanitized_and_exact() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["passed"] is True
    assert evidence["result"] == RESULT
    assert evidence["evidence_sensitive_match_count"] == 0
    assert evidence["cleanup"]["passed"] is True
    assert evidence["side_effect_counts"]["provider_calls"] == 0
    assert evidence["side_effect_counts"]["product_or_clinical_reads"] == 0
    assert evidence["atomic_redemption_contract"]["concurrency_exactly_one"] is True


def test_live_local_acceptance_replays_with_complete_cleanup(tmp_path: Path) -> None:
    result = run_acceptance(output_path=tmp_path / "evidence.json")
    assert result["passed"] is True
    assert result["result"] == RESULT
    assert result["cleanup"]["passed"] is True
    assert result["evidence_sensitive_match_count"] == 0


def test_five_source_rehydration_receipt_is_exact_and_passed() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES

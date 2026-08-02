from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from cryptography.fernet import Fernet

from app.services.application_identity_oidc_adapter import (
    EncryptedAuthorizationAttemptStore,
    InMemoryOIDCAdapterAuditSink,
    MicrosoftOIDCAdapterConfig,
    OIDCTemporarilyUnavailable,
    Surface,
    TwoComponentOIDCAdapter,
)
from app.services.application_identity_oidc_admission_grant import (
    AdmissionGrantDigestKey,
    OIDCAdmissionGrant,
)
from app.services.application_identity_oidc_binding_database_role import (
    RESOLVER_SIGNATURE,
    create_binding_admission_capability_statements,
    create_binding_admission_login_statements,
)
from app.services.application_identity_oidc_transport import (
    OIDCStartCallbackTransport,
    OIDCTransportUnavailable,
)
from scripts.raisa_provider_free_oidc_binding_admission_grant_boundary_acceptance import (
    RESULT,
    run_acceptance,
)
from scripts.raisa_provider_free_oidc_start_callback_transport_boundary_acceptance import (
    CALLBACK,
    CLIENT,
    ORIGINS,
    TENANT,
    _Protocol,
    _Verifier,
)


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "alembic/versions/s8t9u0v1w2x3_add_federation_admission_grants.py"
)
MODEL = ROOT / "app/models/application_identity_federation.py"
API_SPINE = (
    ROOT
    / "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml"
)
RECEIPT = (
    ROOT
    / "orchestration/agent_inbox/codex/"
    "raisa-provider-free-oidc-binding-admission-grant-boundary-rehydration-receipt.json"
)
NOW = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)
RAW_GRANT = base64.urlsafe_b64encode(b"G" * 32).rstrip(b"=").decode("ascii")
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


class _GrantPort:
    def __init__(self, *, available: bool = True, ttl_seconds: int = 60) -> None:
        self.available = available
        self.ttl_seconds = ttl_seconds
        self.calls = 0

    def issue(self, *, completed, now: datetime) -> OIDCAdmissionGrant:
        self.calls += 1
        if not self.available:
            raise OIDCTemporarilyUnavailable("required_grant_dependency_unavailable")
        return OIDCAdmissionGrant(
            raw_grant=RAW_GRANT,
            expires_at=now + timedelta(seconds=self.ttl_seconds),
            surface=completed.surface,
            origin=completed.origin,
            return_target=completed.return_target,
        )


def _transport(port: _GrantPort) -> tuple[OIDCStartCallbackTransport, _Protocol]:
    protocol = _Protocol()
    adapter = TwoComponentOIDCAdapter(
        config=MicrosoftOIDCAdapterConfig(
            tenant_id=TENANT,
            client_id=CLIENT,
            redirect_uri=CALLBACK,
            surface_origins=ORIGINS,
            enabled=True,
        ),
        protocol_client=protocol,
        verifier=_Verifier(),
        attempt_store=EncryptedAuthorizationAttemptStore(
            encryption_key=Fernet.generate_key(),
            digest_key=b"binding-admission-attempt-digest-key-01",
        ),
        audit_sink=InMemoryOIDCAdapterAuditSink(),
    )
    return (
        OIDCStartCallbackTransport(
            adapter=adapter,
            surface_origins=ORIGINS,
            idempotency_hmac_key=b"binding-admission-idempotency-key-001",
            admission_service=port,
            nonce_source=lambda: "N" * 43,
        ),
        protocol,
    )


def _complete(transport: OIDCStartCallbackTransport) -> str:
    started = transport.start(
        surface=Surface.WORD_ONLINE,
        return_target="clinician_one",
        origin=ORIGINS[Surface.WORD_ONLINE],
        csrf_cookie="csrf." + "c" * 43,
        csrf_header="csrf." + "c" * 43,
        idempotency_key="idem." + "i" * 43,
        now=NOW,
    )
    state = parse_qs(urlsplit(started.authorization_uri).query)["state"][0]
    return transport.complete(
        body=urlencode({"code": "authored-code", "state": state}).encode("ascii"),
        content_type="application/x-www-form-urlencoded",
        now=NOW,
    ).html


def test_injected_admission_port_releases_only_exact_origin_grant_message() -> None:
    port = _GrantPort()
    transport, protocol = _transport(port)
    page = _complete(transport)
    assert port.calls == protocol.redeem_calls == 1
    assert '"status":"admission_grant_issued"' in page
    assert page.count(RAW_GRANT) == 1
    assert ORIGINS[Surface.WORD_ONLINE] in page
    assert "authentication_verified" not in page
    assert "Set-Cookie" not in page


def test_injected_admission_failure_cannot_fall_back_to_verified_success() -> None:
    port = _GrantPort(available=False)
    transport, _ = _transport(port)
    with pytest.raises(OIDCTemporarilyUnavailable):
        _complete(transport)
    assert port.calls == 1


def test_injected_port_cannot_extend_the_frozen_grant_lifetime() -> None:
    port = _GrantPort(ttl_seconds=61)
    transport, _ = _transport(port)
    with pytest.raises(OIDCTransportUnavailable):
        _complete(transport)
    assert port.calls == 1


def test_grant_digest_is_versioned_hmac_of_exact_256_bit_bearer() -> None:
    digest = AdmissionGrantDigestKey(
        key_id="grant-v1",
        key=b"separate-authored-synthetic-grant-key",
    )
    reference = digest.reference(RAW_GRANT)
    assert reference.startswith("hmac-sha256:grant-v1:")
    assert RAW_GRANT not in reference
    with pytest.raises(ValueError):
        digest.reference("short")


def test_migration_and_roles_encode_exact_least_authority_boundary() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    assert "SECURITY DEFINER" in migration
    assert "SET search_path = ''" in migration
    assert "REVOKE ALL ON FUNCTION" in migration
    assert "subject_reference_hmac = p_subject_reference_hmac" in migration
    assert "federation.binding_rejected" in migration
    assert "federation.admission_grant_issued" in migration
    assert "trg_app_id_fed_grant_required_audit" in migration
    assert "expires_at = issued_at + INTERVAL '60 seconds'" in migration
    assert "FORCE ROW LEVEL SECURITY" in migration

    capabilities = "\n".join(
        create_binding_admission_capability_statements(
            resolver_call_role="emr4_oidc_binding_resolver_call_12345678",
            resolver_owner_role="emr4_oidc_binding_resolver_owner_12345678",
            grant_issuer_role="emr4_oidc_grant_issuer_12345678",
        )
    )
    login = "\n".join(
        create_binding_admission_login_statements(
            "emr4_oidc_binding_login_12345678",
            resolver_call_role="emr4_oidc_binding_resolver_call_12345678",
            grant_issuer_role="emr4_oidc_grant_issuer_12345678",
            connection_limit=2,
        )
    )
    assert f"ALTER FUNCTION {RESOLVER_SIGNATURE} OWNER TO" in capabilities
    assert "GRANT SELECT ON TABLE public.\"application_identity_federation_bindings\"" in capabilities
    assert "GRANT SELECT, INSERT ON TABLE public.\"application_identity_federation_admission_grants\"" in capabilities
    assert "GRANT INSERT ON TABLE public.\"application_identity_federation_audit_events\"" in capabilities
    issuer_lines = [
        line
        for line in capabilities.splitlines()
        if "emr4_oidc_grant_issuer_12345678" in line
    ]
    assert not any(
        "application_identity_federation_audit_events" in line
        for line in issuer_lines
    )
    assert "NOINHERIT" in login
    assert "NOBYPASSRLS" in login


def test_schema_and_api_spine_keep_raw_identity_session_and_product_closed() -> None:
    model = MODEL.read_text(encoding="utf-8")
    api = API_SPINE.read_text(encoding="utf-8")
    assert "raw_grant" not in model
    assert "raw_id_token" not in model
    assert "patient" not in model.lower()
    assert "provider_free_binding_grant_mounted_default_off" in api
    assert "session_cookies_issued: 0" in api
    assert "callback_sets_session_cookie: false" in api
    assert "product_access" in api


def test_live_local_acceptance_replays_with_complete_cleanup(tmp_path: Path) -> None:
    result = run_acceptance(output_path=tmp_path / "evidence.json")
    assert result["passed"] is True
    assert result["result"] == RESULT
    assert result["cleanup"]["passed"] is True
    assert result["evidence_sensitive_match_count"] == 0
    assert result["no_authority_contract"] == {
        "application_session_rows": 0,
        "attempt_rows_after_callback": 0,
        "product_reads": 0,
        "provider_calls": 0,
        "real_identities": 0,
        "session_cookies": 0,
    }


def test_five_source_rehydration_receipt_is_exact_and_passed() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES

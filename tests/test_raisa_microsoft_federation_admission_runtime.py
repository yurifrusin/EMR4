from __future__ import annotations

import ast
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.services.application_identity_federation import (
    ExternalIdentityBinding,
    FederationDecision,
    FederationReferenceHasher,
    FederationRuntimeConfig,
    InMemoryExternalIdentityBindingStore,
    InMemoryFederationAuditSink,
    InMemoryInternalPrincipalStore,
    MicrosoftFederationAdmissionRuntime,
    SyntheticAuthorizationAttemptEvidence,
    SyntheticInternalPrincipal,
    SyntheticMicrosoftAssertionEvidence,
)
from scripts.raisa_microsoft_federation_admission_runtime_acceptance import (
    HMAC_KEY,
    run_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app" / "services" / "application_identity_federation.py"
PLAN = ROOT / "docs" / "raisa-microsoft-federation-admission-runtime-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-microsoft-federation-admission-runtime-threat-model-delta.md"
)


def _fixture(*, enabled: bool = True, audit_available: bool = True):
    now = datetime(2026, 8, 1, 4, 0, tzinfo=timezone.utc)
    config = FederationRuntimeConfig(
        tenant_id="synthetic-tenant-001",
        issuer="https://login.microsoftonline.invalid/synthetic-tenant-001/v2.0",
        audience="synthetic-client-001",
        enabled=enabled,
    )
    binding = ExternalIdentityBinding(
        provider="microsoft_entra",
        tenant_id="synthetic-tenant-001",
        object_id="synthetic-object-001",
        binding_ref="synthetic-binding-001",
        user_ref="synthetic-user-001",
        practice_ref="synthetic-practice-001",
    )
    principal = SyntheticInternalPrincipal(
        user_ref="synthetic-user-001",
        practice_ref="synthetic-practice-001",
        user_active=True,
        practice_active=True,
    )
    audit = InMemoryFederationAuditSink(available=audit_available)
    runtime = MicrosoftFederationAdmissionRuntime(
        config=config,
        binding_store=InMemoryExternalIdentityBindingStore([binding]),
        principal_store=InMemoryInternalPrincipalStore([principal]),
        audit_sink=audit,
        reference_hasher=FederationReferenceHasher(HMAC_KEY),
    )
    assertion = SyntheticMicrosoftAssertionEvidence(
        data_class="authored_synthetic",
        verifier="synthetic_oidc_verifier",
        provider="microsoft_entra",
        authority_mode="tenant_specific_v2",
        account_type="organisational",
        signature_valid=True,
        algorithm_allowed=True,
        signing_key_trusted=True,
        issuer=config.issuer,
        audience=config.audience,
        tenant_id=config.tenant_id,
        object_id="synthetic-object-001",
        subject="synthetic-subject-001",
        issued_at=now - timedelta(minutes=1),
        not_before=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=5),
        display_email="not-authority@example.invalid",
        office_signed_in=True,
    )
    attempt = SyntheticAuthorizationAttemptEvidence(
        exists=True,
        consumed=False,
        expires_at=now + timedelta(minutes=3),
        state_matches=True,
        nonce_matches=True,
        pkce_method="S256",
        pkce_matches=True,
    )
    return now, runtime, assertion, attempt, audit


def test_exact_prebound_assertion_returns_only_bounded_candidate_after_audit() -> None:
    now, runtime, assertion, attempt, audit = _fixture()
    result = runtime.admit(
        assertion=assertion,
        attempt=attempt,
        now=now,
        correlation_ref="synthetic-correlation-001",
    )
    assert result.decision is FederationDecision.ADMIT
    assert result.audit_recorded is True
    assert len(audit.events) == 1
    candidate = result.principal_candidate
    assert candidate is not None
    assert candidate.user_ref == "synthetic-user-001"
    assert candidate.practice_ref == "synthetic-practice-001"
    assert candidate.authorization_granted is False
    assert candidate.session_created is False
    assert not hasattr(candidate, "role")
    assert result.session_created is False
    assert result.product_data_released is False


def test_default_off_denies_and_records_generic_failure() -> None:
    now, runtime, assertion, attempt, audit = _fixture(enabled=False)
    result = runtime.admit(
        assertion=assertion,
        attempt=attempt,
        now=now,
        correlation_ref="synthetic-correlation-disabled",
    )
    assert result.decision is FederationDecision.DENY
    assert result.reason_code == "federation_disabled"
    assert result.external_error == "authentication_failed"
    assert result.principal_candidate is None
    assert audit.events[0].principal_released is False


def test_audit_failure_overrides_otherwise_valid_admission() -> None:
    now, runtime, assertion, attempt, _audit = _fixture(audit_available=False)
    result = runtime.admit(
        assertion=assertion,
        attempt=attempt,
        now=now,
        correlation_ref="synthetic-correlation-audit-failure",
    )
    assert result.decision is FederationDecision.ERROR
    assert result.http_status == 503
    assert result.reason_code == "required_audit_unavailable"
    assert result.audit_recorded is False
    assert result.principal_candidate is None


def test_audit_contains_no_raw_external_identity_or_display_value() -> None:
    now, runtime, assertion, attempt, audit = _fixture()
    runtime.admit(
        assertion=assertion,
        attempt=attempt,
        now=now,
        correlation_ref="synthetic-correlation-audit-privacy",
    )
    rendered = json.dumps(asdict(audit.events[0]), default=str, sort_keys=True)
    for forbidden in (
        assertion.tenant_id,
        assertion.object_id,
        assertion.subject,
        assertion.display_email,
    ):
        assert forbidden not in rendered
    assert "hmac-sha256:synthetic-v1:" in rendered


def test_hmac_reference_is_keyed_domain_separated_and_validated() -> None:
    hasher = FederationReferenceHasher(HMAC_KEY)
    first = hasher.reference(
        provider="microsoft_entra",
        tenant_id="synthetic-tenant-001",
        object_id="synthetic-object-001",
    )
    assert first == hasher.reference(
        provider="microsoft_entra",
        tenant_id="synthetic-tenant-001",
        object_id="synthetic-object-001",
    )
    assert first != hasher.reference(
        provider="microsoft_entra",
        tenant_id="synthetic-tenant-002",
        object_id="synthetic-object-001",
    )
    assert "synthetic-tenant-001" not in first
    with pytest.raises(ValueError, match="at least 32 bytes"):
        FederationReferenceHasher(b"short")


def test_ambiguous_binding_denies_instead_of_taking_first() -> None:
    now, _runtime, assertion, attempt, audit = _fixture()
    duplicate = [
        ExternalIdentityBinding(
            provider="microsoft_entra",
            tenant_id="synthetic-tenant-001",
            object_id="synthetic-object-001",
            binding_ref=f"synthetic-binding-{index:03d}",
            user_ref=f"synthetic-user-{index:03d}",
            practice_ref="synthetic-practice-001",
        )
        for index in (1, 2)
    ]
    principals = [
        SyntheticInternalPrincipal(
            user_ref=item.user_ref,
            practice_ref=item.practice_ref,
            user_active=True,
            practice_active=True,
        )
        for item in duplicate
    ]
    runtime = MicrosoftFederationAdmissionRuntime(
        config=FederationRuntimeConfig(
            tenant_id="synthetic-tenant-001",
            issuer="https://login.microsoftonline.invalid/synthetic-tenant-001/v2.0",
            audience="synthetic-client-001",
            enabled=True,
        ),
        binding_store=InMemoryExternalIdentityBindingStore(duplicate),
        principal_store=InMemoryInternalPrincipalStore(principals),
        audit_sink=audit,
        reference_hasher=FederationReferenceHasher(HMAC_KEY),
    )
    result = runtime.admit(
        assertion=assertion,
        attempt=attempt,
        now=now,
        correlation_ref="synthetic-correlation-ambiguous",
    )
    assert result.decision is FederationDecision.DENY
    assert result.reason_code == "binding_ambiguous"
    assert result.principal_candidate is None


def test_all_parent_cases_match_runtime_with_zero_external_side_effects() -> None:
    evidence = run_acceptance()
    assert evidence["result"] == "pass"
    assert evidence["case_count"] == evidence["matched_expected_count"] == 22
    assert evidence["mismatches"] == []
    assert evidence["admitted_case_count"] == 1
    assert evidence["audit_raw_value_matches"] == []
    assert set(evidence["authority_and_side_effects"].values()) == {0}


def test_module_is_route_free_and_imports_no_external_runtime() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported.isdisjoint(
        {
            "requests",
            "httpx",
            "socket",
            "sqlalchemy",
            "fastapi",
            "msal",
            "jwt",
            "subprocess",
        }
    )
    router_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "app" / "routers").rglob("*.py")
    )
    assert "application_identity_federation" not in router_source
    assert "MicrosoftFederationAdmissionRuntime" not in router_source


def test_plan_and_threat_delta_preserve_non_wiring_claim() -> None:
    combined = (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).lower()
    for required in (
        "default-off",
        "route-free",
        "provider-free",
        "authored-synthetic",
        "required audit",
        "no role",
        "database",
        "application session",
    ):
        assert required in combined

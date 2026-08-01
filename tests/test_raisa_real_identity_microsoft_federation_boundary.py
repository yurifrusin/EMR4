from __future__ import annotations

import ast
import json
from pathlib import Path

import jsonschema

from scripts.raisa_real_identity_microsoft_federation_boundary_acceptance import (
    CASES_PATH,
    DECISION_SCHEMA_PATH,
    POLICY_PATH,
    POLICY_SCHEMA_PATH,
    run_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-real-identity-microsoft-federation-boundary-plan.md"
DESIGN = ROOT / "docs" / "raisa-real-identity-microsoft-federation-boundary-design.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-real-identity-microsoft-federation-boundary-threat-model-delta.md"
)
SCRIPT = ROOT / "scripts" / "raisa_real_identity_microsoft_federation_boundary_acceptance.py"
RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-real-identity-microsoft-federation-three-tranche-rehydration-receipt.json"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_policy_and_decision_schemas_validate() -> None:
    policy_schema = _json(POLICY_SCHEMA_PATH)
    decision_schema = _json(DECISION_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(policy_schema)
    jsonschema.Draft202012Validator.check_schema(decision_schema)
    jsonschema.Draft202012Validator(policy_schema).validate(_json(POLICY_PATH))


def test_policy_freezes_tenant_specific_prebound_identity() -> None:
    policy = _json(POLICY_PATH)
    assert policy["authority_owner"] == "emr4_backend"
    assert policy["provider"] == "microsoft_entra"
    assert policy["account_scope"]["tenant_mode"] == "one_explicit_organisational_tenant"
    assert policy["account_scope"]["rejected_authorities"] == [
        "common",
        "organizations",
        "consumers",
        "personal_microsoft_account",
    ]
    assert policy["validation"]["external_identity_key"] == "tenant_id_plus_object_id"
    assert policy["identity_binding"]["jit_provisioning"] is False
    assert policy["identity_binding"]["email_or_domain_linking"] is False
    assert policy["identity_binding"]["role_mapping"] == "forbidden"


def test_protocol_requires_code_pkce_oidc_and_rollover_handling() -> None:
    policy = _json(POLICY_PATH)
    protocol = policy["protocol"]
    assert protocol["flow"] == "authorization_code"
    assert protocol["oidc"] is True
    assert protocol["pkce_method"] == "S256"
    assert protocol["single_use_state"] is True
    assert protocol["single_use_nonce"] is True
    assert policy["validation"]["metadata"] == "tenant_specific_discovery_and_jwks"
    assert policy["validation"]["signing_keys"] == "multiple_current_keys_and_rollover_supported"
    assert policy["validation"]["unknown_key"] == "bounded_metadata_refresh_then_deny"


def test_all_architecture_cases_match_and_release_no_session_or_data() -> None:
    evidence = run_acceptance()
    manifest = _json(CASES_PATH)
    assert evidence["result"] == "pass"
    assert evidence["case_count"] == len(manifest["cases"]) == 22
    assert evidence["matched_expected_count"] == 22
    assert evidence["mismatches"] == []
    assert evidence["admitted_case_count"] == 1
    assert all(item["session_created"] is False for item in evidence["decisions"])
    assert all(item["product_data_released"] is False for item in evidence["decisions"])
    assert all(item["provider_calls"] == 0 for item in evidence["decisions"])


def test_email_office_context_and_foreign_tenant_never_create_authority() -> None:
    decisions = {item["case_id"]: item for item in run_acceptance()["decisions"]}
    assert decisions["deny-email-only-match"]["reason_codes"] == ["immutable_subject_required"]
    assert decisions["deny-tenant-mismatch"]["reason_codes"] == ["tenant_mismatch"]
    assert decisions["deny-personal-microsoft-account"]["decision"] == "deny"
    assert all(item["email_or_office_identity_used"] is False for item in decisions.values())


def test_required_audit_failure_releases_nothing() -> None:
    decision = next(
        item
        for item in run_acceptance()["decisions"]
        if item["case_id"] == "error-required-audit-unavailable"
    )
    assert decision["decision"] == "error"
    assert decision["http_status"] == 503
    assert decision["audit_recorded"] is False
    assert decision["principal_candidate_released"] is False


def test_architecture_acceptance_has_no_external_or_product_side_effects() -> None:
    side_effects = run_acceptance()["authority_and_side_effects"]
    assert side_effects
    assert set(side_effects.values()) == {0}


def test_acceptance_script_imports_no_network_database_or_product_runtime() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    forbidden = {
        "requests",
        "httpx",
        "socket",
        "sqlalchemy",
        "fastapi",
        "msal",
        "jwt",
        "app",
    }
    assert imported.isdisjoint(forbidden)


def test_docs_freeze_identity_as_authentication_not_authorization() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT)
    ).lower()
    for required in (
        "authorization code",
        "pkce",
        "tenant-specific",
        "keyed hmac",
        "email",
        "audit",
        "fail closed",
        "authentication is not authorization",
    ):
        assert required in combined
    assert "none of those runtime steps is authorized" not in combined
    assert "no live entra app registration" in combined


def test_rehydration_receipt_names_all_five_sources_and_blocks_dispatch() -> None:
    receipt = _json(RECEIPT)
    expected = [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert receipt["rehydration_sources"] == expected
    assert set(receipt["source_evidence"]) == set(expected)
    assert receipt["worker_dispatch_permitted"] is False

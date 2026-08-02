from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from scripts.raisa_two_component_oidc_verifier_architecture_acceptance import (
    CASES_PATH,
    OPENAPI_PATH,
    POLICY_PATH,
    POLICY_SCHEMA_PATH,
    run_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]
TRANCHE = "raisa-two-component-oidc-verifier-architecture-revision"
HARDENING = ROOT / "docs" / "security" / "hardening" / "raisa-two-component-oidc-verifier"
RECEIPT = ROOT / "orchestration" / "agent_inbox" / "codex" / "raisa-two-component-oidc-verifier-architecture-rehydration-receipt.json"
PREACCEPTANCE_RECEIPT = ROOT / "orchestration" / "agent_inbox" / "codex" / "raisa-two-component-oidc-verifier-architecture-preacceptance-receipt.json"
PRECOMMIT_RECEIPT = ROOT / "orchestration" / "agent_inbox" / "codex" / "raisa-two-component-oidc-verifier-architecture-precommit-receipt.json"
DEPENDENCY_EVIDENCE = ROOT / "orchestration" / "continuity" / TRANCHE / "dependency-review-evidence.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_policy_schema_and_frozen_ownership_validate() -> None:
    schema = _json(POLICY_SCHEMA_PATH)
    policy = _json(POLICY_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(policy)
    assert policy["protocol_client"] == {
        "package": "msal",
        "version": "1.37.0",
        "authority": "tenant_specific_v2",
        "requested_scopes": [],
        "effective_scopes": ["openid", "profile"],
        "excluded_scopes": ["offline_access"],
        "pkce": "S256",
        "response_mode": "form_post",
        "claims_authoritative": False,
    }
    verifier = policy["id_token_verifier"]
    assert verifier["algorithms"] == ["RS256"]
    assert verifier["unknown_kid_refresh_attempts"] == 1
    assert verifier["fallback"] == "forbidden"
    assert "runtime_adapter" in policy["closed"]


def test_exact_reviewed_dependencies_are_pinned() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert requirements.count("msal==1.37.0") == 1
    assert requirements.count("Authlib==1.7.2") == 1
    assert requirements.count("joserfc==1.7.4") == 1
    evidence = _json(DEPENDENCY_EVIDENCE)
    assert evidence["result"] == "pass"
    assert evidence["verification"]["pip_check"] == "no_broken_requirements"
    assert evidence["verification"]["pip_audit_result"] == "no_known_vulnerabilities"
    assert [item["name"] for item in evidence["selected"]] == ["msal", "Authlib", "joserfc"]


def test_non_mounted_api_contract_uses_form_post() -> None:
    document = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert document["servers"] == []
    assert document["x-emr4-authority"]["status"] == "architecture_only_not_mounted"
    assert document["x-emr4-authority"]["dependencies_added"] == 3
    callback = document["paths"]["/api/v1/application-auth/federation/microsoft/callback"]
    assert "post" in callback and "get" not in callback
    content = callback["post"]["requestBody"]["content"]
    assert set(content) == {"application/x-www-form-urlencoded"}
    assert document["x-emr4-federation-components"]["protocol_client"]["identity_admission_from_msal_claims"] == "forbidden"


def test_provider_free_signed_token_matrix_passes() -> None:
    evidence = run_acceptance()
    assert evidence["result"] == "pass"
    assert evidence["dependency_versions"] == {"msal": "1.37.0", "Authlib": "1.7.2", "joserfc": "1.7.4"}
    expected_ids = {case["id"] for case in _json(CASES_PATH)["cases"]}
    assert {case["case_id"] for case in evidence["cases"]} == expected_ids
    assert all(case["matched"] for case in evidence["cases"])
    assert all(value == 0 for value in evidence["side_effects"].values())


def test_authorised_application_adapter_remains_route_free() -> None:
    adapter = ROOT / "app" / "services" / "application_identity_oidc_adapter.py"
    adapter_text = adapter.read_text(encoding="utf-8")
    assert "from msal import" in adapter_text
    assert "from authlib" in adapter_text
    assert "id_token_claims" not in adapter_text
    runtime_paths = [ROOT / "main.py", *(ROOT / "app" / "routers").rglob("*.py")]
    assert all(
        "application_identity_oidc_adapter" not in path.read_text(encoding="utf-8")
        for path in runtime_paths
    )
    assert "federation/microsoft/callback" not in "\n".join(
        path.read_text(encoding="utf-8") for path in runtime_paths
    )


def test_hardening_portfolio_is_complete_and_evidence_bound() -> None:
    required = [
        HARDENING / "context.md",
        HARDENING / "hardening.json",
        HARDENING / "hardening.md",
        HARDENING / "proposals" / "separate-protocol-and-signature-verification.md",
        HARDENING / "diagrams" / "separate-protocol-and-signature-verification-before.mmd",
        HARDENING / "diagrams" / "separate-protocol-and-signature-verification-after-tls-only-msal.mmd",
        HARDENING / "diagrams" / "separate-protocol-and-signature-verification-after-msal-authlib-verifier.mmd",
        HARDENING / "diagrams" / "separate-protocol-and-signature-verification-after-single-full-oidc-client.mmd",
        HARDENING / "diagrams" / "separate-protocol-and-signature-verification-after-custom-pyjwt-jwks.mmd",
        HARDENING / "implementation" / "msal-authlib-verifier.md",
    ]
    assert all(path.is_file() for path in required)
    portfolio = _json(HARDENING / "hardening.json")
    assert portfolio["collection"]["artifact_count"] == 10
    assert portfolio["collection"]["source_drift"] == "none_observed"
    assert portfolio["sourceEvidence"]["artifactCount"] == 10
    assert portfolio["sourceEvidence"]["sourceDrift"] == "none_observed"
    opportunity = portfolio["opportunities"][0]
    assert opportunity["recommendation"] == "msal-authlib-verifier"
    assert {option["id"] for option in opportunity["options"]} == {
        "tls-only-msal",
        "msal-authlib-verifier",
        "single-full-oidc-client",
        "custom-pyjwt-jwks",
    }
    for option in opportunity["options"]:
        assert all(option[key] for key in ("security", "performance", "memory", "reliability", "operability", "migration"))


def test_rehydration_receipt_names_all_five_sources() -> None:
    expected = {
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    }
    for path in (RECEIPT, PREACCEPTANCE_RECEIPT, PRECOMMIT_RECEIPT):
        receipt = _json(path)
        assert receipt["status"] == "passed"
        assert set(receipt["rehydration_sources"]) == expected

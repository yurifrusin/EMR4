from __future__ import annotations

import ast
import json
from pathlib import Path

import jsonschema
import yaml

from scripts.raisa_maintained_oidc_verifier_session_bridge_architecture_acceptance import (
    CASES_PATH,
    DECISION_SCHEMA_PATH,
    OPENAPI_PATH,
    POLICY_PATH,
    POLICY_SCHEMA_PATH,
    run_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "raisa-maintained-oidc-verifier-session-bridge-architecture-plan.md"
)
DESIGN = (
    ROOT
    / "docs"
    / "raisa-maintained-oidc-verifier-session-bridge-architecture-design.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-maintained-oidc-verifier-session-bridge-threat-model-delta.md"
)
SCRIPT = (
    ROOT
    / "scripts"
    / "raisa_maintained_oidc_verifier_session_bridge_architecture_acceptance.py"
)
RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-oidc-verifier-session-bridge-architecture-rehydration-receipt.json"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_policy_and_decision_schemas_validate() -> None:
    policy_schema = _json(POLICY_SCHEMA_PATH)
    decision_schema = _json(DECISION_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(policy_schema)
    jsonschema.Draft202012Validator.check_schema(decision_schema)
    jsonschema.Draft202012Validator(policy_schema).validate(_json(POLICY_PATH))


def test_policy_selects_msal_without_adding_a_dependency() -> None:
    policy = _json(POLICY_PATH)
    library = policy["library_boundary"]
    assert library == {
        "selected_library": "msal_python",
        "reviewed_baseline": "1.37.0",
        "client_type": "confidential_client",
        "flow_apis": [
            "ConfidentialClientApplication.initiate_auth_code_flow",
            "ConfidentialClientApplication.acquire_token_by_auth_code_flow",
        ],
        "custom_jwt_verifier": False,
        "dependency_added": False,
    }
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "msal==" not in requirements


def test_protocol_is_tenant_specific_minimal_and_fail_closed() -> None:
    protocol = _json(POLICY_PATH)["protocol"]
    assert protocol["authority"] == "one_tenant_specific_v2_authority"
    assert protocol["flow"] == "authorization_code_oidc"
    assert protocol["scopes"] == ["openid", "profile"]
    assert protocol["pkce"] == "S256"
    assert protocol["attempt_ttl_seconds"] == 300
    assert protocol["attempt_consumption"] == (
        "atomic_before_single_provider_exchange"
    )
    assert "trusted_signing_key" in protocol["required_verified_facts"]
    assert {"common", "organizations", "consumers"}.issubset(
        protocol["forbidden_authorities"]
    )
    assert {"offline_access", "microsoft_graph"}.issubset(
        protocol["forbidden_scopes"]
    )


def test_bootstrap_is_execute_only_hmac_rls_and_not_owner_runtime() -> None:
    bootstrap = _json(POLICY_PATH)["database_bootstrap"]
    assert bootstrap["login_role"] == "LOGIN_NOINHERIT_no_table_grants"
    assert bootstrap["bootstrap_role"] == (
        "NOLOGIN_NOBYPASSRLS_execute_exact_resolver_only"
    )
    assert bootstrap["routine_owner"] == (
        "NOLOGIN_non_table_owner_minimum_select_insert"
    )
    assert bootstrap["public_execute"] is False
    assert bootstrap["direct_table_grants"] is False
    assert bootstrap["search_path"] == (
        "pg_catalog_only_schema_qualified_application_objects"
    )
    assert bootstrap["rls"] == "forced_exact_transaction_local_hmac_context"
    assert bootstrap["input"] == "fixed_length_versioned_hmac_references_only"
    assert bootstrap["audit_before_return"] is True


def test_grant_reconciles_cookie_partitions_without_callback_cookie() -> None:
    policy = _json(POLICY_PATH)
    grant = policy["admission_grant"]
    assert grant["entropy_bits"] == 256
    assert grant["ttl_seconds"] == 60
    assert grant["stored_form"] == "digest_only"
    assert grant["callback_sets_session_cookie"] is False
    assert grant["transport"] == "exact_origin_message_body_not_url"
    assert grant["browser_storage"] is False
    assert policy["cookie_contract"]["partitioned"] is True
    assert policy["cookie_contract"]["raw_parent_in_client"] is False


def test_redemption_rechecks_current_truth_and_commits_before_cookie() -> None:
    redemption = _json(POLICY_PATH)["redemption"]
    assert redemption["repeat_binding_resolution"] is True
    assert redemption["fresh_internal_load"] == [
        "user",
        "practice",
        "role",
        "practitioner_relationship",
    ]
    assert redemption["atomic_commit"] == [
        "grant_consumption",
        "parent_session",
        "surface_session",
        "required_audit",
    ]
    assert redemption["cookie_after_commit"] is True
    assert redemption["concurrent_success_maximum"] == 1
    assert redemption["product_reads"] == 0


def test_all_authored_synthetic_architecture_cases_match() -> None:
    manifest = _json(CASES_PATH)
    evidence = run_acceptance()
    assert evidence["result"] == "pass"
    assert evidence["case_count"] == len(manifest["cases"]) == 33
    assert evidence["matched_expected_count"] == 33
    assert evidence["mismatches"] == []
    assert evidence["admitted_architecture_case_count"] == 3
    assert all(item["admission_grant_released"] is False for item in evidence["decisions"])
    assert all(item["session_created"] is False for item in evidence["decisions"])
    assert all(item["cookie_issued"] is False for item in evidence["decisions"])
    assert all(item["product_data_released"] is False for item in evidence["decisions"])


def test_high_risk_cases_deny_at_the_intended_boundary() -> None:
    decisions = {item["case_id"]: item for item in run_acceptance()["decisions"]}
    expected = {
        "deny-custom-jwt-fallback": "custom_jwt_verifier_forbidden",
        "deny-common-authority": "tenant_specific_authority_required",
        "deny-email-office-authority": "mutable_external_context_forbidden",
        "deny-owner-runtime-connection": "runtime_owner_connection_forbidden",
        "deny-bootstrap-without-forced-rls": "forced_hmac_rls_required",
        "deny-callback-cookie": "callback_must_not_issue_session_cookie",
        "deny-cross-origin-grant": "exact_origin_body_handoff_required",
        "deny-stale-binding-at-redeem": "fresh_binding_resolution_required",
        "deny-non-atomic-session": "atomic_session_audit_required",
        "deny-cookie-before-commit": "cookie_after_commit_required",
        "deny-product-read-during-bridge": "bridge_product_read_forbidden",
    }
    assert {case_id: decisions[case_id]["reason"] for case_id in expected} == expected
    assert decisions["error-required-audit-unavailable"]["outcome"] == (
        "error_architecture"
    )
    assert decisions["error-required-audit-unavailable"]["audit_recorded"] is False


def test_acceptance_has_exactly_zero_external_or_runtime_side_effects() -> None:
    side_effects = run_acceptance()["authority_and_side_effects"]
    assert side_effects
    assert set(side_effects.values()) == {0}


def test_openapi_is_non_mounted_rest_only_and_sets_cookie_after_commit() -> None:
    contract = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert contract["openapi"] == "3.1.0"
    assert contract["servers"] == []
    assert contract["x-emr4-authority"]["status"] == "architecture_only_not_mounted"
    assert contract["x-emr4-api-spine"]["graphql_mutation"] == "forbidden"
    assert set(contract["paths"]) == {
        "/api/v1/application-auth/federation/microsoft/start",
        "/api/v1/application-auth/federation/microsoft/callback",
        "/api/v1/application-auth/federation/session/redeem",
    }
    cookie = contract["x-emr4-session-cookie-contract"]
    assert cookie["callback_sets_session_cookie"] is False
    assert cookie["cookie_after_database_commit_only"] is True


def test_acceptance_imports_no_network_provider_database_or_app_runtime() -> None:
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
    import_name = "raisa_maintained_oidc_verifier_session_bridge"
    for router in (ROOT / "app" / "routers").glob("*.py"):
        assert import_name not in router.read_text(encoding="utf-8")


def test_docs_cover_required_threat_and_api_spine_boundaries() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT)
    ).lower()
    for required in (
        "msal python",
        "authorization code",
        "s256",
        "tenant-specific",
        "security definer",
        "pg_catalog",
        "forced rls",
        "one-use admission grant",
        "cookie after commit",
        "freshly reloads",
        "authentication is not authorization",
        "non-enumerating",
        "product read",
    ):
        assert required in combined
    assert "graphql mutation" not in combined


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


def test_architecture_artifacts_exclude_branding_paths() -> None:
    artifacts = {
        POLICY_PATH,
        POLICY_SCHEMA_PATH,
        DECISION_SCHEMA_PATH,
        CASES_PATH,
        OPENAPI_PATH,
        PLAN,
        DESIGN,
        THREAT,
        SCRIPT,
        RECEIPT,
    }
    assert all("docs/branding/" not in path.as_posix() for path in artifacts)

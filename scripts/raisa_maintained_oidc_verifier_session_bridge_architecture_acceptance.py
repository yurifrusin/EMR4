from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-maintained-oidc-verifier-session-bridge-architecture"
)
POLICY_PATH = EVIDENCE_DIR / "architecture-policy.json"
POLICY_SCHEMA_PATH = EVIDENCE_DIR / "architecture-policy.schema.json"
DECISION_SCHEMA_PATH = EVIDENCE_DIR / "architecture-decision.schema.json"
CASES_PATH = EVIDENCE_DIR / "acceptance-cases.json"
OPENAPI_PATH = (
    ROOT
    / "docs"
    / "api-spine"
    / "openapi"
    / "application-identity-federation-session-bridge.yaml"
)
DEFAULT_OUTPUT = EVIDENCE_DIR / "provider-free-acceptance-evidence.json"
EVIDENCE_RECORDED_AT = "2026-08-02T00:00:00Z"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _decision(
    *,
    case_id: str,
    outcome: str,
    reason: str,
    audit_recorded: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.oidc-session-bridge-architecture-decision.v1",
        "case_id": case_id,
        "outcome": outcome,
        "reason": reason,
        "architecture_admitted": outcome == "admit_architecture",
        "audit_required": True,
        "audit_recorded": audit_recorded,
        "admission_grant_released": False,
        "session_created": False,
        "cookie_issued": False,
        "product_data_released": False,
        "provider_calls": 0,
        "database_writes": 0,
    }


def evaluate_case(*, case_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """Evaluate architecture facts only; perform no protocol or runtime work."""

    audit_available = bool(context["audit"].get("available"))

    def deny(reason: str) -> dict[str, Any]:
        return _decision(
            case_id=case_id,
            outcome="deny_architecture",
            reason=reason,
            audit_recorded=audit_available,
        )

    if context.get("mode") != "architecture_only":
        return deny("architecture_only_mode_required")

    library = context["library"]
    if (
        library.get("selected") != "msal_python"
        or library.get("reviewed_baseline") != "1.37.0"
        or library.get("confidential_client") is not True
        or library.get("maintained_flow_apis") is not True
    ):
        return deny("maintained_msal_boundary_required")
    if library.get("custom_jwt_verifier") is not False:
        return deny("custom_jwt_verifier_forbidden")
    if library.get("dependency_added") is not False:
        return deny("architecture_only_dependency_change_forbidden")

    protocol = context["protocol"]
    if (
        protocol.get("tenant_specific_v2") is not True
        or protocol.get("authority_allowlisted") is not True
    ):
        return deny("tenant_specific_authority_required")
    if protocol.get("redirect_exact") is not True:
        return deny("exact_redirect_required")
    if protocol.get("flow") != "authorization_code_oidc" or protocol.get(
        "scopes"
    ) != ["openid", "profile"]:
        return deny("minimal_authorization_code_oidc_required")
    if protocol.get("state_matches") is not True:
        return deny("state_correlation_required")
    if protocol.get("nonce_matches") is not True:
        return deny("nonce_correlation_required")
    if protocol.get("pkce_method") != "S256" or protocol.get("pkce_matches") is not True:
        return deny("s256_pkce_required")
    if (
        protocol.get("attempt_exists") is not True
        or protocol.get("attempt_unexpired") is not True
        or protocol.get("attempt_consumed_before_exchange") is not True
        or protocol.get("single_provider_exchange") is not True
    ):
        return deny("single_use_attempt_required")

    verification = context["verification"]
    required_verification = (
        "library_verified",
        "signature_valid",
        "algorithm_allowed",
        "issuer_exact",
        "audience_exact",
        "tenant_exact",
        "object_id_present",
        "subject_present",
        "times_valid",
        "trusted_signing_key",
        "rollover_supported",
    )
    if not all(verification.get(key) is True for key in required_verification):
        return deny("maintained_library_verification_required")
    if verification.get("raw_token_parsed_by_emr4") is not False:
        return deny("custom_jwt_verifier_forbidden")
    if verification.get("email_or_office_used") is not False:
        return deny("mutable_external_context_forbidden")

    bootstrap = context["bootstrap"]
    if bootstrap.get("owner_connection_used") is not False:
        return deny("runtime_owner_connection_forbidden")
    if (
        bootstrap.get("login_noinherit_no_table_grants") is not True
        or bootstrap.get("bootstrap_nologin_nobypassrls") is not True
        or bootstrap.get("execute_exact_function_only") is not True
    ):
        return deny("execute_only_bootstrap_required")
    if not all(
        bootstrap.get(key) is expected
        for key, expected in (
            ("routine_owner_not_table_owner", True),
            ("minimum_select_insert", True),
            ("security_definer", True),
            ("search_path_pg_catalog", True),
            ("schema_qualified", True),
            ("dynamic_sql", False),
            ("public_execute_revoked", True),
        )
    ):
        return deny("constrained_security_definer_required")
    if bootstrap.get("forced_rls_exact_hmac_context") is not True:
        return deny("forced_hmac_rls_required")
    if bootstrap.get("hmac_only_input") is not True:
        return deny("hmac_only_bootstrap_required")
    if bootstrap.get("bounded_output") is not True:
        return deny("bounded_bootstrap_output_required")
    if (
        bootstrap.get("match_count") != 1
        or bootstrap.get("binding_active") is not True
        or bootstrap.get("binding_version_matches") is not True
    ):
        return deny("one_active_binding_required")
    if bootstrap.get("audit_before_return") is not True:
        return deny("bootstrap_audit_before_return_required")

    handoff = context["handoff"]
    if handoff.get("callback_cookie_issued") is not False:
        return deny("callback_must_not_issue_session_cookie")
    if (
        handoff.get("entropy_bits", 0) < 256
        or not 0 < handoff.get("ttl_seconds", 0) <= 60
        or handoff.get("digest_only_persistence") is not True
        or handoff.get("surface_bound") is not True
        or handoff.get("origin_bound") is not True
        or handoff.get("audience_bound") is not True
        or handoff.get("return_target_allowlisted") is not True
    ):
        return deny("bounded_admission_grant_required")
    if (
        handoff.get("message_exact_origin") is not True
        or handoff.get("credential_in_url") is not False
        or handoff.get("browser_storage_used") is not False
        or handoff.get("no_store_headers") is not True
    ):
        return deny("exact_origin_body_handoff_required")

    redemption = context["redemption"]
    if redemption.get("csrf_cookie_header_match") is not True:
        return deny("redemption_csrf_required")
    if not all(
        redemption.get(key) is True
        for key in (
            "grant_locked",
            "grant_unexpired",
            "grant_unused",
            "surface_matches",
            "origin_matches",
        )
    ):
        return deny("one_use_bound_grant_required")
    if redemption.get("binding_reresolved") is not True:
        return deny("fresh_binding_resolution_required")
    if not all(
        redemption.get(key) is True
        for key in (
            "internal_user_fresh",
            "internal_practice_fresh",
            "internal_role_fresh",
            "practitioner_relationship_fresh",
        )
    ):
        return deny("fresh_internal_principal_required")
    if redemption.get("internal_principal_active") is not True:
        return deny("active_internal_principal_required")
    if (
        redemption.get("atomic_grant_session_audit") is not True
        or redemption.get("concurrent_success_maximum") != 1
    ):
        return deny("atomic_session_audit_required")
    if redemption.get("cookie_after_commit") is not True:
        return deny("cookie_after_commit_required")
    if redemption.get("raw_parent_released") is not False:
        return deny("raw_parent_session_forbidden")
    if redemption.get("product_reads") != 0:
        return deny("bridge_product_read_forbidden")

    privacy = context["privacy"]
    if (
        privacy.get("raw_provider_material_persisted") is not False
        or privacy.get("raw_provider_material_logged") is not False
        or privacy.get("raw_identity_persisted") is not False
    ):
        return deny("raw_authentication_material_forbidden")
    if privacy.get("errors_non_enumerating") is not True:
        return deny("non_enumerating_errors_required")

    if context["audit"].get("required") is not True or not audit_available:
        return _decision(
            case_id=case_id,
            outcome="error_architecture",
            reason="required_audit_unavailable",
            audit_recorded=False,
        )

    non_wiring = context["non_wiring"]
    if any(value != 0 for value in non_wiring.values()):
        return deny("architecture_non_wiring_required")

    return _decision(
        case_id=case_id,
        outcome="admit_architecture",
        reason="architecture_contract_complete",
        audit_recorded=True,
    )


def run_acceptance() -> dict[str, Any]:
    policy_schema = _read_json(POLICY_SCHEMA_PATH)
    policy = _read_json(POLICY_PATH)
    decision_schema = _read_json(DECISION_SCHEMA_PATH)
    manifest = _read_json(CASES_PATH)
    openapi = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator.check_schema(policy_schema)
    jsonschema.Draft202012Validator(policy_schema).validate(policy)
    jsonschema.Draft202012Validator.check_schema(decision_schema)
    decision_validator = jsonschema.Draft202012Validator(decision_schema)
    if not isinstance(openapi, dict) or openapi.get("openapi") != "3.1.0":
        raise ValueError("OpenAPI architecture contract must be a 3.1 object")

    decisions: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for case in manifest["cases"]:
        context = _deep_merge(manifest["base_context"], case["overrides"])
        result = evaluate_case(case_id=case["id"], context=context)
        decision_validator.validate(result)
        decisions.append(result)
        if any(result.get(key) != value for key, value in case["expected"].items()):
            mismatches.append(case["id"])

    admitted = [item for item in decisions if item["architecture_admitted"]]
    passed = not mismatches and len(admitted) == 3
    return {
        "schema_version": "emr4.oidc-session-bridge-architecture-acceptance-evidence.v1",
        "recorded_at": EVIDENCE_RECORDED_AT,
        "result": "pass" if passed else "fail",
        "mode": "repository_local_provider_free_architecture_acceptance",
        "data_class": manifest["data_class"],
        "source_hashes": {
            "policy": _sha256(POLICY_PATH),
            "policy_schema": _sha256(POLICY_SCHEMA_PATH),
            "decision_schema": _sha256(DECISION_SCHEMA_PATH),
            "acceptance_cases": _sha256(CASES_PATH),
            "openapi": _sha256(OPENAPI_PATH),
        },
        "case_count": len(decisions),
        "matched_expected_count": len(decisions) - len(mismatches),
        "mismatches": mismatches,
        "admitted_architecture_case_count": len(admitted),
        "decisions": decisions,
        "authority_and_side_effects": {
            "provider_calls": 0,
            "real_identity_values": 0,
            "database_reads": 0,
            "database_writes": 0,
            "database_migrations": 0,
            "database_roles_created": 0,
            "routes_mounted": 0,
            "dependencies_added": 0,
            "application_sessions_created": 0,
            "product_data_reads": 0,
            "patient_or_clinical_fields": 0,
            "cloud_or_iam_mutations": 0,
            "deployments": 0,
            "protected_ref_movements": 0,
        },
        "claim_boundary": {
            "proves": [
                "MSAL Python is the sole future maintained tenant-specific authorization-code/OIDC protocol and verification boundary.",
                "An execute-only HMAC resolver can replace runtime table-owner access while auditing zero-match and matched lookups.",
                "A short-lived one-use admission grant reconciles native and Office cookie partitions without a callback session cookie.",
                "Redemption repeats binding resolution, loads fresh internal truth and atomically couples grant consumption, session creation and audit before cookies.",
            ],
            "does_not_prove": [
                "A package installation, Microsoft request, discovery/JWKS exchange, token validation or live callback.",
                "A database role/function/RLS implementation, real identity, application session, product read, deployment, production fitness or release.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run provider-free OIDC verifier/session-bridge architecture acceptance."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = run_acceptance()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "cases": evidence["case_count"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

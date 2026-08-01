from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-real-identity-microsoft-federation-boundary"
)
POLICY_PATH = EVIDENCE_DIR / "federation-policy.json"
POLICY_SCHEMA_PATH = EVIDENCE_DIR / "federation-policy.schema.json"
DECISION_SCHEMA_PATH = EVIDENCE_DIR / "federation-admission-decision.schema.json"
CASES_PATH = EVIDENCE_DIR / "acceptance-cases.json"
DEFAULT_OUTPUT = EVIDENCE_DIR / "provider-free-acceptance-evidence.json"
EVIDENCE_RECORDED_AT = "2026-08-01T04:00:00Z"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


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
    decision: str,
    reason: str,
    audit_recorded: bool,
) -> dict[str, Any]:
    admitted = decision == "admit"
    is_error = decision == "error"
    return {
        "schema_version": "emr4.federation-admission-decision.v1",
        "case_id": case_id,
        "policy_version": "microsoft-entra-single-tenant-prebound.v1",
        "authority_source": "emr4_backend",
        "provider": "microsoft_entra",
        "decision": decision,
        "http_status": 503 if is_error else (200 if admitted else 401),
        "external_error": (
            "authentication_temporarily_unavailable"
            if is_error
            else (None if admitted else "authentication_failed")
        ),
        "reason_codes": [reason],
        "evaluated_at": EVIDENCE_RECORDED_AT,
        "audit_required": True,
        "audit_recorded": audit_recorded,
        "principal_candidate_released": admitted,
        "session_created": False,
        "product_data_released": False,
        "email_or_office_identity_used": False,
        "provider_calls": 0,
    }


def evaluate_case(*, case_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """Evaluate authored-synthetic architecture facts without verifying a token.

    This oracle is deliberately not a protocol implementation. Boolean validation
    facts model the required outputs of a future maintained OIDC library.
    """

    audit = context["audit"]

    def denied(reason: str) -> dict[str, Any]:
        return _decision(
            case_id=case_id,
            decision="deny",
            reason=reason,
            audit_recorded=bool(audit.get("available")),
        )

    configuration = context["configuration"]
    if configuration.get("enabled") is not True:
        return denied("federation_disabled")

    assertion = context["assertion"]
    if assertion.get("data_class") != "authored_synthetic":
        return denied("authored_synthetic_assertion_required")
    if assertion.get("provider") != "microsoft_entra":
        return denied("provider_mismatch")
    if assertion.get("authority_mode") != "tenant_specific_v2":
        return denied("tenant_specific_authority_required")
    if assertion.get("account_type") not in {
        "organisational",
        "prebound_tenant_guest",
    }:
        return denied("organisational_account_required")

    attempt = context["attempt"]
    now = _parse_time(context["now"])
    if attempt.get("exists") is not True:
        return denied("authorization_attempt_required")
    if attempt.get("consumed") is True:
        return denied("authorization_attempt_consumed")
    if now >= _parse_time(attempt["expires_at"]):
        return denied("authorization_attempt_expired")
    if attempt.get("state_matches") is not True:
        return denied("state_mismatch")
    if attempt.get("nonce_matches") is not True:
        return denied("nonce_mismatch")
    if attempt.get("pkce_method") != "S256" or attempt.get("pkce_matches") is not True:
        return denied("pkce_mismatch")

    if assertion.get("signature_valid") is not True:
        return denied("token_signature_invalid")
    if assertion.get("algorithm_allowed") is not True:
        return denied("token_algorithm_invalid")
    if assertion.get("signing_key_trusted") is not True:
        return denied("signing_key_untrusted")
    if assertion.get("issuer") != configuration.get("issuer"):
        return denied("issuer_mismatch")
    if assertion.get("audience") != configuration.get("audience"):
        return denied("audience_mismatch")
    if assertion.get("tenant_id") != configuration.get("tenant_id"):
        return denied("tenant_mismatch")
    if not assertion.get("object_id") or not assertion.get("subject"):
        return denied("immutable_subject_required")
    if now >= _parse_time(assertion["expires_at"]):
        return denied("token_expired")
    if now < _parse_time(assertion["not_before"]):
        return denied("token_not_yet_valid")
    if _parse_time(assertion["issued_at"]) > now:
        return denied("token_issued_in_future")

    binding = context["binding"]
    match_count = binding.get("match_count")
    if match_count != 1:
        return denied("binding_ambiguous" if match_count and match_count > 1 else "active_binding_required")
    if binding.get("status") != "active":
        return denied("active_binding_required")
    if not all(
        binding.get(key)
        for key in ("binding_ref", "user_ref", "practice_ref")
    ):
        return denied("active_binding_required")

    principal = context["internal_principal"]
    if principal.get("user_active") is not True or principal.get("practice_active") is not True:
        return denied("active_internal_principal_required")

    if audit.get("required") is not True or audit.get("available") is not True:
        return _decision(
            case_id=case_id,
            decision="error",
            reason="required_audit_unavailable",
            audit_recorded=False,
        )
    return _decision(
        case_id=case_id,
        decision="admit",
        reason="federation_admitted",
        audit_recorded=True,
    )


def run_acceptance() -> dict[str, Any]:
    policy_schema = _read_json(POLICY_SCHEMA_PATH)
    policy = _read_json(POLICY_PATH)
    decision_schema = _read_json(DECISION_SCHEMA_PATH)
    manifest = _read_json(CASES_PATH)

    jsonschema.Draft202012Validator.check_schema(policy_schema)
    jsonschema.Draft202012Validator(policy_schema).validate(policy)
    jsonschema.Draft202012Validator.check_schema(decision_schema)
    decision_validator = jsonschema.Draft202012Validator(
        decision_schema,
        format_checker=jsonschema.FormatChecker(),
    )

    decisions: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for case in manifest["cases"]:
        context = _deep_merge(manifest["base_context"], case["overrides"])
        result = evaluate_case(case_id=case["id"], context=context)
        decision_validator.validate(result)
        decisions.append(result)
        if any(result.get(key) != value for key, value in case["expected"].items()):
            mismatches.append(case["id"])

    passed = not mismatches
    return {
        "schema_version": "emr4.real-identity-microsoft-federation-acceptance-evidence.v1",
        "recorded_at": EVIDENCE_RECORDED_AT,
        "result": "pass" if passed else "fail",
        "mode": "repository_local_provider_free_architecture_acceptance",
        "data_class": manifest["data_class"],
        "source_hashes": {
            "policy": _sha256(POLICY_PATH),
            "policy_schema": _sha256(POLICY_SCHEMA_PATH),
            "decision_schema": _sha256(DECISION_SCHEMA_PATH),
            "acceptance_cases": _sha256(CASES_PATH),
        },
        "case_count": len(decisions),
        "matched_expected_count": len(decisions) - len(mismatches),
        "mismatches": mismatches,
        "admitted_case_count": sum(item["decision"] == "admit" for item in decisions),
        "decisions": decisions,
        "authority_and_side_effects": {
            "provider_calls": 0,
            "identity_provider_calls": 0,
            "microsoft_graph_or_office_identity_calls": 0,
            "backend_calls": 0,
            "database_reads": 0,
            "database_writes": 0,
            "product_data_reads": 0,
            "patient_or_clinical_data_fields": 0,
            "application_sessions_created": 0,
            "cloud_or_iam_mutations": 0,
            "deployments": 0,
        },
        "claim_boundary": {
            "proves": [
                "One tenant-specific organisational Microsoft Entra architecture requires exact protocol and immutable subject facts.",
                "Only one active pre-provisioned binding can release a principal candidate after required audit.",
                "Email, domain and Office signed-in state never participate in admission.",
                "All unknown, replayed, ambiguous or unauditable states fail before session or product-data release.",
            ],
            "does_not_prove": [
                "A live Microsoft request, token signature, discovery document, signing-key rollover or browser callback.",
                "A real identity binding, EMR4 session, product read, deployment, production fitness or release readiness.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run provider-free Raisa Microsoft-federation boundary acceptance."
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

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-clinician-role-boundary"
)
POLICY_PATH = EVIDENCE_DIR / "auth-boundary-policy.json"
POLICY_SCHEMA_PATH = EVIDENCE_DIR / "auth-boundary-policy.schema.json"
AUTH_DECISION_SCHEMA_PATH = EVIDENCE_DIR / "authorization-decision.schema.json"
EXCHANGE_DECISION_SCHEMA_PATH = (
    EVIDENCE_DIR / "cross-surface-exchange-decision.schema.json"
)
CASES_PATH = EVIDENCE_DIR / "acceptance-cases.json"
DEFAULT_OUTPUT = EVIDENCE_DIR / "provider-free-acceptance-evidence.json"
EVIDENCE_RECORDED_AT = "2026-07-31T12:00:00Z"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if (
            isinstance(value, dict)
            and isinstance(merged.get(key), dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _authorization_result(
    *,
    case_id: str,
    context: dict[str, Any],
    policy: dict[str, Any],
    decision: str,
    http_status: int,
    reason_code: str,
) -> dict[str, Any]:
    principal = context.get("server_principal") or {}
    request = context.get("request") or {}
    principal_practice = principal.get("practice_id")
    resource_practice = request.get("resource_practice_id")
    if not principal_practice or not resource_practice:
        practice_scope = "unknown"
    elif principal_practice == resource_practice:
        practice_scope = "same_practice"
    else:
        practice_scope = "mismatch"

    audit = context.get("audit") or {}
    return {
        "schema_version": "emr4.backend-authorization-decision.v1",
        "decision_id": f"decision-{case_id}",
        "correlation_id": f"correlation-{case_id}",
        "case_id": case_id,
        "authority_source": "emr4_backend",
        "policy_version": policy["policy_version"],
        "surface": context.get("surface", "unknown"),
        "action": request.get("action", policy["clinician_policy"]["action"]),
        "resource_type": request.get(
            "resource_type",
            policy["clinician_policy"]["resource_type"],
        ),
        "decision": decision,
        "http_status": http_status,
        "reason_codes": [reason_code],
        "current_backend_role": principal.get("current_role"),
        "practice_scope": practice_scope,
        "evaluated_at": context["now"],
        "validity": "current_request_only",
        "audit_required": True,
        "audit_recorded": bool(audit.get("available")),
        "office_identity_used": False,
        "client_claims_used": False,
        "evaluated_before_data_access": True,
        "product_data_released": False,
    }


def evaluate_authorization(
    *,
    case_id: str,
    context: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate the frozen metadata-only clinician read policy.

    This is an acceptance oracle, not a runtime authorizer. It deliberately
    accepts no database, token, cookie, Office identity, patient, document or
    clinical content input.
    """

    def result(decision: str, status: int, reason: str) -> dict[str, Any]:
        return _authorization_result(
            case_id=case_id,
            context=context,
            policy=policy,
            decision=decision,
            http_status=status,
            reason_code=reason,
        )

    now = _parse_time(context["now"])
    surface = context.get("surface")
    if surface not in policy["surfaces"]:
        return result("deny", 401, "surface_not_allowed")

    session = context.get("application_session") or {}
    if not session.get("exists"):
        return result("deny", 401, "application_session_required")
    if session.get("status") == "revoked":
        return result("deny", 401, "application_session_revoked")
    if session.get("status") != "active":
        return result("deny", 401, "application_session_inactive")
    if now >= _parse_time(session["expires_at"]):
        return result("deny", 401, "application_session_expired")
    if now >= _parse_time(session["idle_expires_at"]):
        return result("deny", 401, "application_session_idle_expired")

    binding = context.get("surface_binding") or {}
    if not binding.get("exists"):
        return result("deny", 401, "surface_session_required")
    if binding.get("status") != "active":
        return result("deny", 401, "surface_session_inactive")
    if binding.get("parent_session_id") != session.get("session_id"):
        return result("deny", 401, "surface_session_parent_mismatch")
    if binding.get("parent_generation") != session.get("generation"):
        return result("deny", 401, "surface_session_generation_mismatch")
    if binding.get("surface") != surface:
        return result("deny", 401, "surface_session_surface_mismatch")
    if binding.get("origin") != context.get("request_origin"):
        return result("deny", 401, "surface_session_origin_mismatch")
    if binding.get("audience") != context.get("request_audience"):
        return result("deny", 401, "surface_session_audience_mismatch")
    if now >= _parse_time(binding["expires_at"]):
        return result("deny", 401, "surface_session_expired")
    if now >= _parse_time(binding["idle_expires_at"]):
        return result("deny", 401, "surface_session_idle_expired")
    if _parse_time(binding["expires_at"]) > _parse_time(session["expires_at"]):
        return result("deny", 401, "surface_session_exceeds_parent_expiry")

    principal = context.get("server_principal") or {}
    if not principal.get("active"):
        return result("deny", 401, "user_inactive")
    if (
        session.get("user_id") != principal.get("user_id")
        or session.get("practice_id") != principal.get("practice_id")
    ):
        return result("deny", 401, "session_principal_mismatch")

    request = context.get("request") or {}
    clinician = policy["clinician_policy"]
    if (
        request.get("action") != clinician["action"]
        or request.get("resource_type") != clinician["resource_type"]
    ):
        return result("deny", 403, "server_policy_mismatch")
    if request.get("resource_practice_id") != principal.get("practice_id"):
        return result("deny", 403, "resource_practice_mismatch")
    if principal.get("current_role") not in clinician["allowed_current_backend_roles"]:
        return result("deny", 403, "clinician_role_required")
    if (
        not principal.get("practitioner_id")
        or principal.get("practitioner_active") is not True
        or principal.get("practitioner_practice_id") != principal.get("practice_id")
    ):
        return result(
            "deny",
            403,
            "active_same_practice_practitioner_required",
        )

    audit = context.get("audit") or {}
    if audit.get("required") is not True or audit.get("available") is not True:
        return result("error", 503, "required_audit_unavailable")
    return result("allow", 200, "authorized")


def _exchange_result(
    *,
    case_id: str,
    context: dict[str, Any],
    admitted: bool,
    reason_code: str,
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.cross-surface-exchange-decision.v1",
        "decision_id": f"exchange-decision-{case_id}",
        "correlation_id": f"exchange-correlation-{case_id}",
        "case_id": case_id,
        "authority_source": "emr4_backend",
        "source_surface": context.get("source_surface", "unknown"),
        "target_surface": context.get("target_surface", "unknown"),
        "decision": "admit" if admitted else "deny",
        "http_status": 200 if admitted else 401,
        "reason_codes": [reason_code],
        "evaluated_at": context["now"],
        "grant_consumed": admitted,
        "surface_session_created": admitted,
        "bearer_material_transported": False,
        "office_identity_used": False,
        "product_data_released": False,
    }


def evaluate_exchange(
    *,
    case_id: str,
    context: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate the frozen one-use cross-surface exchange contract."""

    def denied(reason: str) -> dict[str, Any]:
        return _exchange_result(
            case_id=case_id,
            context=context,
            admitted=False,
            reason_code=reason,
        )

    surfaces = policy["surfaces"]
    source_surface = context.get("source_surface")
    target_surface = context.get("target_surface")
    if source_surface not in surfaces:
        return denied("exchange_source_surface_not_allowed")
    if target_surface not in surfaces:
        return denied("exchange_target_surface_not_allowed")

    now = _parse_time(context["now"])
    parent = context.get("parent_session") or {}
    if parent.get("status") != "active":
        return denied("exchange_parent_session_inactive")
    if now >= _parse_time(parent["expires_at"]):
        return denied("exchange_parent_session_expired")

    grant = context.get("grant") or {}
    if not grant.get("exists") or grant.get("status") != "issued":
        return denied("exchange_grant_required")
    if grant.get("parent_session_id") != parent.get("session_id"):
        return denied("exchange_parent_session_mismatch")
    if grant.get("parent_generation") != parent.get("generation"):
        return denied("exchange_parent_generation_mismatch")
    if grant.get("source_surface") != source_surface:
        return denied("exchange_source_surface_mismatch")
    if grant.get("target_surface") != target_surface:
        return denied("exchange_target_surface_mismatch")
    if grant.get("source_origin") != context.get("source_origin"):
        return denied("exchange_source_origin_mismatch")
    if grant.get("target_origin") != context.get("target_origin"):
        return denied("exchange_target_origin_mismatch")
    if grant.get("audience") != context.get("audience"):
        return denied("exchange_audience_mismatch")
    if now >= _parse_time(grant["expires_at"]):
        return denied("exchange_expired")
    if grant.get("used") is True:
        return denied("exchange_already_consumed")

    redemption = context.get("redemption") or {}
    if grant.get("pkce_method") != "S256" or redemption.get("pkce_method") != "S256":
        return denied("exchange_pkce_method_mismatch")
    if grant.get("pkce_challenge") != redemption.get("pkce_challenge"):
        return denied("exchange_pkce_mismatch")
    if grant.get("state_hash") != redemption.get("state_hash"):
        return denied("exchange_state_mismatch")
    if grant.get("nonce_hash") != redemption.get("nonce_hash"):
        return denied("exchange_nonce_mismatch")

    return _exchange_result(
        case_id=case_id,
        context=context,
        admitted=True,
        reason_code="exchange_admitted",
    )


def _outcome_matches(
    decision: dict[str, Any],
    expected: dict[str, Any],
) -> bool:
    return all(decision.get(key) == value for key, value in expected.items())


def run_acceptance() -> dict[str, Any]:
    policy = _read_json(POLICY_PATH)
    manifest = _read_json(CASES_PATH)

    authorization_decisions: list[dict[str, Any]] = []
    authorization_mismatches: list[str] = []
    for case in manifest["authorization_cases"]:
        context = _deep_merge(
            manifest["base_authorization_context"],
            case["overrides"],
        )
        decision = evaluate_authorization(
            case_id=case["id"],
            context=context,
            policy=policy,
        )
        authorization_decisions.append(decision)
        if not _outcome_matches(decision, case["expected"]):
            authorization_mismatches.append(case["id"])

    exchange_decisions: list[dict[str, Any]] = []
    exchange_mismatches: list[str] = []
    for case in manifest["exchange_cases"]:
        context = _deep_merge(
            manifest["base_exchange_context"],
            case["overrides"],
        )
        decision = evaluate_exchange(
            case_id=case["id"],
            context=context,
            policy=policy,
        )
        exchange_decisions.append(decision)
        if not _outcome_matches(decision, case["expected"]):
            exchange_mismatches.append(case["id"])

    allowed = [
        item for item in authorization_decisions if item["decision"] == "allow"
    ]
    admitted = [
        item for item in exchange_decisions if item["decision"] == "admit"
    ]
    allowed_surfaces = sorted({item["surface"] for item in allowed})
    expected_surfaces = sorted(policy["surfaces"].keys())
    surface_equivalence = (
        allowed_surfaces == expected_surfaces
        and len({item["policy_version"] for item in allowed}) == 1
        and all(item["authority_source"] == "emr4_backend" for item in allowed)
    )
    office_separation = all(
        item["office_identity_used"] is False
        and item["client_claims_used"] is False
        for item in authorization_decisions
    ) and all(item["office_identity_used"] is False for item in exchange_decisions)

    result = (
        "pass"
        if not authorization_mismatches
        and not exchange_mismatches
        and surface_equivalence
        and office_separation
        else "fail"
    )
    return {
        "schema_version": "emr4.shared-application-auth-acceptance-evidence.v1",
        "recorded_at": EVIDENCE_RECORDED_AT,
        "result": result,
        "mode": "repository_local_provider_free_architecture_acceptance",
        "data_class": manifest["data_class"],
        "source_hashes": {
            "policy": _sha256(POLICY_PATH),
            "policy_schema": _sha256(POLICY_SCHEMA_PATH),
            "authorization_decision_schema": _sha256(
                AUTH_DECISION_SCHEMA_PATH
            ),
            "cross_surface_exchange_decision_schema": _sha256(
                EXCHANGE_DECISION_SCHEMA_PATH
            ),
            "acceptance_cases": _sha256(CASES_PATH),
        },
        "authorization": {
            "case_count": len(authorization_decisions),
            "matched_expected_count": (
                len(authorization_decisions) - len(authorization_mismatches)
            ),
            "mismatches": authorization_mismatches,
            "allowed_surfaces": allowed_surfaces,
            "single_backend_policy_equivalent_across_surfaces": surface_equivalence,
            "microsoft_office_identity_used": False,
            "client_claims_used": False,
            "decisions": authorization_decisions,
        },
        "cross_surface_exchange": {
            "case_count": len(exchange_decisions),
            "matched_expected_count": len(exchange_decisions) - len(exchange_mismatches),
            "mismatches": exchange_mismatches,
            "admitted_case_count": len(admitted),
            "all_admitted_grants_single_use_consumed": all(
                item["grant_consumed"] is True for item in admitted
            ),
            "bearer_material_transported": False,
            "decisions": exchange_decisions,
        },
        "authority_and_side_effects": {
            "provider_calls": 0,
            "identity_provider_calls": 0,
            "microsoft_graph_or_office_identity_calls": 0,
            "cloud_or_iam_mutations": 0,
            "backend_calls": 0,
            "database_reads": 0,
            "database_writes": 0,
            "product_data_reads": 0,
            "patient_or_clinical_data_fields": 0,
            "appointment_commands": 0,
            "microphone_accesses": 0,
            "document_mutations": 0,
            "deployments": 0,
        },
        "claim_boundary": {
            "proves": [
                "One typed backend-owned clinician-read policy is equivalent across desktop Word, Word Online and the native Diary.",
                "Microsoft or Office signed-in state and client role/practice hints cannot create or alter an allow decision.",
                "Session, practice, clinician linkage, expiry, revocation, exchange and required-audit failures close before data access.",
                "Word-to-Diary trust uses a one-use metadata-only exchange contract without bearer transport."
            ],
            "does_not_prove": [
                "Live EMR4 authentication, cookies, federation or database-backed session revocation.",
                "Safety for product-derived, patient, health or clinical data.",
                "Organisational Office deployment, cloud identity configuration, production fitness or release readiness."
            ]
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the provider-free Raisa shared-auth boundary acceptance."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    evidence = run_acceptance()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "result": evidence["result"],
        "authorization_cases": evidence["authorization"]["case_count"],
        "exchange_cases": evidence["cross_surface_exchange"]["case_count"],
        "output": str(args.output),
    }, sort_keys=True))
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

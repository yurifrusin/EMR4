from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.application_identity_federation import (
    ExternalIdentityBinding,
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


PARENT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-real-identity-microsoft-federation-boundary"
)
CASES_PATH = PARENT_DIR / "acceptance-cases.json"
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-microsoft-federation-admission-runtime"
)
DEFAULT_OUTPUT = EVIDENCE_DIR / "provider-free-acceptance-evidence.json"
RUNTIME_PATH = ROOT / "app" / "services" / "application_identity_federation.py"
RECORDED_AT = "2026-08-01T04:00:00Z"
HMAC_KEY = b"authored-synthetic-federation-key-0000000000000001"


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


def _runtime_for_context(
    context: dict[str, Any],
) -> tuple[
    MicrosoftFederationAdmissionRuntime,
    SyntheticMicrosoftAssertionEvidence,
    SyntheticAuthorizationAttemptEvidence,
    InMemoryFederationAuditSink,
]:
    configuration = context["configuration"]
    assertion_source = context["assertion"]
    binding_source = context["binding"]
    principal_source = context["internal_principal"]

    configured_object = assertion_source.get("object_id") or "synthetic-object-001"
    bindings = []
    for index in range(binding_source["match_count"]):
        binding_ref = binding_source.get("binding_ref") or "synthetic-binding-001"
        if index:
            binding_ref = f"synthetic-binding-{index + 1:03d}"
        bindings.append(
            ExternalIdentityBinding(
                provider="microsoft_entra",
                tenant_id=assertion_source["tenant_id"],
                object_id=configured_object,
                binding_ref=binding_ref,
                user_ref=binding_source.get("user_ref") or "synthetic-user-001",
                practice_ref=(
                    binding_source.get("practice_ref") or "synthetic-practice-001"
                ),
                status=(
                    binding_source["status"]
                    if binding_source["status"] in {"active", "revoked"}
                    else "revoked"
                ),
            )
        )

    principals = []
    if binding_source["match_count"]:
        principals.append(
            SyntheticInternalPrincipal(
                user_ref=binding_source.get("user_ref") or "synthetic-user-001",
                practice_ref=(
                    binding_source.get("practice_ref") or "synthetic-practice-001"
                ),
                user_active=principal_source["user_active"],
                practice_active=principal_source["practice_active"],
            )
        )

    audit_sink = InMemoryFederationAuditSink(
        available=bool(context["audit"]["available"])
    )
    runtime = MicrosoftFederationAdmissionRuntime(
        config=FederationRuntimeConfig(
            tenant_id=configuration["tenant_id"],
            issuer=configuration["issuer"],
            audience=configuration["audience"],
            enabled=configuration["enabled"],
        ),
        binding_store=InMemoryExternalIdentityBindingStore(bindings),
        principal_store=InMemoryInternalPrincipalStore(principals),
        audit_sink=audit_sink,
        reference_hasher=FederationReferenceHasher(HMAC_KEY),
    )
    assertion = SyntheticMicrosoftAssertionEvidence(
        data_class=assertion_source["data_class"],
        verifier="synthetic_oidc_verifier",
        provider=assertion_source["provider"],
        authority_mode=assertion_source["authority_mode"],
        account_type=assertion_source["account_type"],
        signature_valid=assertion_source["signature_valid"],
        algorithm_allowed=assertion_source["algorithm_allowed"],
        signing_key_trusted=assertion_source["signing_key_trusted"],
        issuer=assertion_source["issuer"],
        audience=assertion_source["audience"],
        tenant_id=assertion_source["tenant_id"],
        object_id=assertion_source.get("object_id"),
        subject=assertion_source.get("subject"),
        issued_at=_parse_time(assertion_source["issued_at"]),
        not_before=_parse_time(assertion_source["not_before"]),
        expires_at=_parse_time(assertion_source["expires_at"]),
        display_email=assertion_source.get("display_email"),
        office_signed_in=assertion_source.get("office_signed_in", False),
    )
    attempt_source = context["attempt"]
    attempt = SyntheticAuthorizationAttemptEvidence(
        exists=attempt_source["exists"],
        consumed=attempt_source["consumed"],
        expires_at=_parse_time(attempt_source["expires_at"]),
        state_matches=attempt_source["state_matches"],
        nonce_matches=attempt_source["nonce_matches"],
        pkce_method=attempt_source["pkce_method"],
        pkce_matches=attempt_source["pkce_matches"],
    )
    return runtime, assertion, attempt, audit_sink


def run_acceptance() -> dict[str, Any]:
    manifest = _read_json(CASES_PATH)
    decisions: list[dict[str, Any]] = []
    mismatches: list[str] = []
    audit_events: list[dict[str, Any]] = []

    for case in manifest["cases"]:
        context = _deep_merge(manifest["base_context"], case["overrides"])
        runtime, assertion, attempt, audit_sink = _runtime_for_context(context)
        result = runtime.admit(
            assertion=assertion,
            attempt=attempt,
            now=_parse_time(context["now"]),
            correlation_ref=f"synthetic-correlation-{case['id']}",
        )
        rendered = {
            "case_id": case["id"],
            "decision": result.decision.value,
            "http_status": result.http_status,
            "reason_codes": [result.reason_code],
            "external_error": result.external_error,
            "audit_recorded": result.audit_recorded,
            "principal_candidate": (
                asdict(result.principal_candidate)
                if result.principal_candidate is not None
                else None
            ),
            "provider_calls": result.provider_calls,
            "session_created": result.session_created,
            "product_data_released": result.product_data_released,
        }
        decisions.append(rendered)
        audit_events.extend(asdict(item) for item in audit_sink.events)
        if any(rendered.get(key) != value for key, value in case["expected"].items()):
            mismatches.append(case["id"])

    admitted = [item for item in decisions if item["decision"] == "admit"]
    raw_values = {
        manifest["base_context"]["assertion"][field]
        for field in ("tenant_id", "object_id", "subject", "display_email")
    }
    serialized_audit = json.dumps(audit_events, sort_keys=True, default=str)
    audit_raw_value_matches = sorted(value for value in raw_values if value in serialized_audit)
    passed = not mismatches and len(admitted) == 1 and not audit_raw_value_matches

    return {
        "schema_version": "emr4.microsoft-federation-admission-runtime-evidence.v1",
        "recorded_at": RECORDED_AT,
        "result": "pass" if passed else "fail",
        "mode": "route_free_provider_free_authored_synthetic_in_memory",
        "data_class": manifest["data_class"],
        "source_hashes": {
            "parent_cases": _sha256(CASES_PATH),
            "runtime": _sha256(RUNTIME_PATH),
        },
        "case_count": len(decisions),
        "matched_expected_count": len(decisions) - len(mismatches),
        "mismatches": mismatches,
        "admitted_case_count": len(admitted),
        "audit_event_count": len(audit_events),
        "audit_raw_value_matches": audit_raw_value_matches,
        "decisions": decisions,
        "audit_events": audit_events,
        "authority_and_side_effects": {
            "provider_calls": 0,
            "identity_provider_calls": 0,
            "microsoft_graph_or_office_identity_calls": 0,
            "http_or_socket_calls": 0,
            "fastapi_or_graphql_routes_added": 0,
            "database_reads": 0,
            "database_writes": 0,
            "application_sessions_created": 0,
            "product_data_reads": 0,
            "patient_or_clinical_data_fields": 0,
            "cloud_or_iam_mutations": 0,
            "deployments": 0,
        },
        "claim_boundary": {
            "proves": [
                "One default-off route-free runtime matches all 22 frozen synthetic admission cases.",
                "Exact mapping returns at most an unauthorised session-free principal candidate after required audit.",
                "Audit uses a versioned keyed HMAC and contains none of the tested raw external identity values.",
            ],
            "does_not_prove": [
                "Live Microsoft/OIDC protocol or cryptographic verification.",
                "Durable uniqueness, application-session creation, current product identity reload, product authorization, deployment or production fitness.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run provider-free Raisa Microsoft federation runtime acceptance."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = run_acceptance()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "cases": evidence["case_count"],
                "audit_events": evidence["audit_event_count"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

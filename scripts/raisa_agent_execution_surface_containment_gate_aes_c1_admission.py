"""Pure provider-free AES-C1 admission rehearsal over authored-synthetic objects.

This module evaluates the exact frozen AES-C1 scenario catalogue against the
accepted AES-C0 contract. It never starts a runtime, never calls a provider,
never touches an adapter, database, source, tool or command, and never executes
an admitted operation. The evaluator clock and the current-generation /
current-authority control states are authored-synthetic trusted harness inputs,
never candidate content.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_agent_execution_surface_containment_gate_aes_c0_acceptance import (
    ALWAYS_DENIED,
    BUDGET_DIMENSIONS,
    CONTRACT_PATH as AES_C0_CONTRACT_PATH,
    SCHEMA_PATH as AES_C0_SCHEMA_PATH,
    _ceiling_pairs,
    _load,
    validate_instance,
)

BASE = (
    ROOT
    / "orchestration/continuity/"
    "raisa-agent-execution-surface-containment-gate-aes-c1"
)
CONTRACT_PATH = BASE / "admission-rehearsal-contract.json"
SCHEMA_PATH = BASE / "admission-rehearsal-contract.schema.json"
SCENARIOS_PATH = BASE / "authored-synthetic-admission-scenarios.json"
EVIDENCE_PATH = BASE / "provider-free-admission-evidence.json"

AES_C0_CONTRACT = _load(AES_C0_CONTRACT_PATH)
AES_C0_SCHEMA = _load(AES_C0_SCHEMA_PATH)

BROKER_REASON_CODES = [
    "manifest_grant_and_current_authority",
    "manifest_grant_missing",
    "lease_invalid",
    "authority_changed",
    "proofreader_not_admitted",
    "budget_exhausted",
    "operation_identity_candidate_controlled",
    "forbidden_capability_class",
    "generation_superseded",
    "supply_chain_identity_mismatch",
    "external_kill_switch",
]
EVIDENCE_REASON_CODES = [code.replace("_", "-") for code in BROKER_REASON_CODES]
COUNTER_KEYS = [
    counter for counters in BUDGET_DIMENSIONS.values() for counter in counters
]

ZERO_HEX = "0" * 64
SENTINEL = "sha256:" + ZERO_HEX
WRONG_DIGEST = "sha256:" + "9" * 64
AUTHORITY_DIGEST = (
    "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
)
SUPPLY_DIGESTS = {
    "runtime_image_digest": (
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    ),
    "model_provider_contract_digest": (
        "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    ),
    "system_contract_digest": (
        "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    ),
    "adapter_artifact_digest": (
        "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    ),
    "generation_manifest_digest": "PLACEHOLDER_DIGEST",
}
ISSUED_AT = "2026-08-11T00:00:00Z"
EXPIRES_AT = "2026-08-11T00:05:00Z"
EVALUATION_CLOCK = "2026-08-11T00:00:01Z"
ISSUED_AT_NOW = "2026-08-11T00:00:00Z"

FORBIDDEN_CANDIDATE_KEYS = set(
    AES_C0_CONTRACT["candidate_influence_policy"]["candidate_must_not_supply"]
)

_STOP_TERMINAL_STATE = {
    "budget_exhausted": "exhausted",
    "generation_superseded": "superseded",
    "external_kill_switch": "revoked",
    "supply_chain_identity_mismatch": "quarantined",
    "authority_changed": "superseded",
    "lease_invalid": "exhausted",
}

# Authoritative 45-scenario catalogue: scenario_id -> (decision, reason_codes, after_terminal)
SCENARIO_EXPECTATIONS: dict[str, tuple[str, list[str], bool]] = {
    "exact-inert-intersection-allow": (
        "allow", ["manifest_grant_and_current_authority"], False),
    "exact-inert-second-within-budget-allow": (
        "allow", ["manifest_grant_and_current_authority"], True),
    "grant-missing-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-class-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-operation-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-adapter-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-destination-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-method-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-media-type-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-audience-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-source-class-mismatch-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-input-field-overreach-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-output-field-overreach-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-call-limit-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-request-byte-limit-deny": ("deny", ["manifest_grant_missing"], False),
    "grant-response-byte-limit-deny": ("deny", ["manifest_grant_missing"], False),
    "candidate-operation-identity-deny": (
        "deny", ["operation_identity_candidate_controlled"], False),
    "proofreader-not-admitted-deny": ("deny", ["proofreader_not_admitted"], False),
    "forbidden-capability-class-deny": (
        "deny", ["forbidden_capability_class"], False),
    "lease-state-inactive-deny": ("deny", ["lease_invalid"], False),
    "lease-manifest-mismatch-deny": ("deny", ["lease_invalid"], False),
    "lease-generation-mismatch-deny": ("deny", ["lease_invalid"], False),
    "lease-capability-mismatch-deny": ("deny", ["lease_invalid"], False),
    "lease-class-mismatch-deny": ("deny", ["lease_invalid"], False),
    "lease-audience-mismatch-deny": ("deny", ["lease_invalid"], False),
    "lease-authority-mismatch-deny": ("deny", ["lease_invalid"], False),
    "lease-outlives-manifest-stop": ("stop", ["lease_invalid"], True),
    "lease-expired-stop": ("stop", ["lease_invalid"], True),
    "manifest-expired-stop": ("stop", ["authority_changed"], True),
    "manifest-content-digest-mismatch-stop": (
        "stop", ["supply_chain_identity_mismatch"], True),
    "generation-superseded-stop": ("stop", ["generation_superseded"], True),
    "cross-generation-replay-stop": ("stop", ["generation_superseded"], True),
    "authority-binding-changed-stop": ("stop", ["authority_changed"], True),
    "authority-purpose-changed-stop": ("stop", ["authority_changed"], True),
    "authority-bureau-changed-stop": ("stop", ["authority_changed"], True),
    "authority-work-cell-changed-stop": ("stop", ["authority_changed"], True),
    "authority-stale-stop": ("stop", ["authority_changed"], True),
    "supply-chain-identity-mismatch-stop": (
        "stop", ["supply_chain_identity_mismatch"], True),
    "existing-revocation-stop": ("stop", ["external_kill_switch"], True),
    "external-kill-switch-stop": ("stop", ["external_kill_switch"], True),
    "cumulative-budget-already-exhausted-stop": (
        "stop", ["budget_exhausted"], True),
    "prospective-budget-overflow-stop": ("stop", ["budget_exhausted"], True),
    "zero-disabled-capability-stop": ("stop", ["budget_exhausted"], True),
    "denial-ceiling-reached-after-deny": (
        "deny", ["manifest_grant_missing"], True),
    "attempt-after-denial-ceiling-stop": ("stop", ["budget_exhausted"], True),
}


def canonical_json(value: Any) -> bytes:
    """Return canonical JSON bytes (UTF-8, sorted keys, compact separators)."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest_of(value: Any) -> str:
    """Return the sha256 digest of canonical JSON of value."""
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _flatten_ceilings(budgets: dict[str, Any]) -> dict[str, int]:
    return dict(_ceiling_pairs(budgets))


def _sentinel_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(manifest)
    value["manifest_digest"] = SENTINEL
    value["supply_chain_identity"]["generation_manifest_digest"] = SENTINEL
    return value


def compute_manifest_digest(manifest: dict[str, Any]) -> str:
    """Sentinel-normalized canonical manifest SHA-256 rule."""
    return digest_of(_sentinel_manifest(manifest))


def _set_path(value: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> None:
    target: Any = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


def _del_path(value: dict[str, Any], path: tuple[Any, ...]) -> None:
    target: Any = value
    for part in path[:-1]:
        target = target[part]
    del target[path[-1]]


def _forbidden_keys(value: Any, forbidden: set[str], path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden:
                errors.append(f"{path}:forbidden:{key}")
            errors.extend(_forbidden_keys(child, forbidden, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_forbidden_keys(child, forbidden, f"{path}[{index}]"))
    return errors


def _supply_chain_mismatch(
    manifest_supply: dict[str, Any], current_supply: dict[str, Any]
) -> bool:
    return any(
        manifest_supply[key] != current_supply[key]
        for key in (
            "runtime_image_digest",
            "model_provider_contract_digest",
            "system_contract_digest",
            "adapter_artifact_digest",
            "generation_manifest_digest",
        )
    )


def _grant_mismatch(grant: dict[str, Any], observed_op: dict[str, Any]) -> bool:
    prospective = observed_op["prospective"]
    return not (
        grant["capability_class"] == observed_op["capability_class"]
        and grant["operation_id"] == observed_op["operation_id"]
        and grant["adapter_id"] == observed_op["adapter_id"]
        and grant["destination_id"] == observed_op["destination_id"]
        and grant["method"] == observed_op["method"]
        and grant["media_type"] == observed_op["media_type"]
        and grant["audience"] == observed_op["audience"]
        and grant["source_class"] == observed_op["source_class"]
        and set(observed_op["source_fields"]) <= set(grant["allowed_input_fields"])
        and set(observed_op["output_fields"]) <= set(grant["allowed_output_fields"])
        and prospective["request_count"] <= grant["max_calls"]
        and prospective["request_bytes"] <= grant["max_request_bytes"]
        and prospective["response_bytes"] <= grant["max_response_bytes"]
    )


def _lease_manifest_identity_match(
    lease: dict[str, Any], manifest: dict[str, Any]
) -> bool:
    return (
        lease["manifest_id"] == manifest["manifest_id"]
        and lease["generation_id"] == manifest["generation_id"]
        and lease["authority_binding_digest"] == manifest["authority_binding_digest"]
    )


def _lease_matches_grant(
    lease: dict[str, Any], manifest: dict[str, Any], grant: dict[str, Any]
) -> bool:
    return (
        _lease_manifest_identity_match(lease, manifest)
        and lease["state"] == "active"
        and lease["capability_id"] == grant["capability_id"]
        and lease["capability_class"] == grant["capability_class"]
        and lease["audience"] == grant["audience"]
    )


def _budget_stop(
    ceilings: dict[str, int],
    observed: dict[str, int],
    prospective: dict[str, int],
) -> str | None:
    for key in COUNTER_KEYS:
        ceiling = ceilings[key]
        if ceiling > 0 and observed[key] >= ceiling:
            return "budget_exhausted"
        if prospective[key] > 0:
            if ceiling == 0:
                return "budget_exhausted"
            if observed[key] + prospective[key] > ceiling:
                return "budget_exhausted"
    return None


def _revocation_state(
    attempt: dict[str, Any], decision: str, reason_code: str
) -> str:
    if attempt.get("revocation_record") is not None:
        return "revoked"
    if decision == "stop":
        if reason_code in ("generation_superseded", "authority_changed"):
            return "superseded"
        if reason_code == "supply_chain_identity_mismatch":
            return "quarantined"
        if reason_code == "external_kill_switch":
            return "revoked"
    return "not_revoked"


def validate_attempt(attempt: dict[str, Any]) -> list[str]:
    """Validate a closed AdmissionAttempt and its embedded AES-C0 messages."""
    schema = _load(SCHEMA_PATH)
    errors = list(
        validate_instance(
            attempt,
            schema["$defs"]["AdmissionAttempt"],
            root_schema=schema,
            path="$",
        )
    )
    manifest = attempt.get("generation_manifest")
    lease = attempt.get("capability_lease")
    budget_state = attempt.get("budget_state")
    current_generation_state = attempt.get("current_generation_state")
    if not (
        isinstance(manifest, dict)
        and isinstance(lease, dict)
        and isinstance(budget_state, dict)
        and isinstance(current_generation_state, dict)
    ):
        return sorted(set(errors))
    errors.extend(
        validate_instance(
            manifest,
            AES_C0_SCHEMA["$defs"]["GenerationManifest"],
            root_schema=AES_C0_SCHEMA,
            path="$.generation_manifest",
        )
    )
    errors.extend(
        validate_instance(
            lease,
            AES_C0_SCHEMA["$defs"]["CapabilityLease"],
            root_schema=AES_C0_SCHEMA,
            path="$.capability_lease",
        )
    )
    errors.extend(
        validate_instance(
            budget_state,
            AES_C0_SCHEMA["$defs"]["BudgetState"],
            root_schema=AES_C0_SCHEMA,
            path="$.budget_state",
        )
    )
    supply = current_generation_state.get("supply_chain_identity")
    if not isinstance(supply, dict):
        errors.append("$.current_generation_state.supply_chain_identity:type")
        return sorted(set(errors))
    errors.extend(
        validate_instance(
            supply,
            AES_C0_SCHEMA["$defs"]["SupplyChainIdentity"],
            root_schema=AES_C0_SCHEMA,
            path="$.current_generation_state.supply_chain_identity",
        )
    )
    revocation = attempt.get("revocation_record")
    if revocation is not None:
        if not isinstance(revocation, dict):
            errors.append("$.revocation_record:type")
        else:
            errors.extend(
                validate_instance(
                    revocation,
                    AES_C0_SCHEMA["$defs"]["RevocationRecord"],
                    root_schema=AES_C0_SCHEMA,
                    path="$.revocation_record",
                )
            )
            if revocation.get("generation_id") != manifest.get("generation_id"):
                errors.append("$.revocation_record.generation_id:cross_record_mismatch")
    if budget_state.get("manifest_id") != manifest.get("manifest_id"):
        errors.append("$.budget_state.manifest_id:cross_record_mismatch")
    if budget_state.get("generation_id") != manifest.get("generation_id"):
        errors.append("$.budget_state.generation_id:cross_record_mismatch")
    if budget_state.get("ceilings") != manifest.get("budgets"):
        errors.append("$.budget_state.ceilings:cross_record_mismatch")
    return sorted(set(errors))


def validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = list(validate_instance(contract, schema, root_schema=schema))
    if contract.get("broker_reason_vocabulary") != BROKER_REASON_CODES:
        errors.append("broker_reason_vocabulary:not_exact")
    if contract.get("evidence_reason_vocabulary") != EVIDENCE_REASON_CODES:
        errors.append("evidence_reason_vocabulary:not_exact")
    expected_inherited = {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/authored-synthetic-contract-examples.json",
    }
    if set(contract.get("inherited_artifact_digests", {})) != expected_inherited:
        errors.append("inherited_artifact_digests:not_exact")
    registry = contract.get("scenario_registry", [])
    if len(registry) != len(SCENARIO_EXPECTATIONS):
        errors.append("scenario_registry:count")
    registry_ids = [entry.get("scenario_id") for entry in registry]
    if len(set(registry_ids)) != len(registry_ids):
        errors.append("scenario_registry:duplicates")
    if set(registry_ids) != set(SCENARIO_EXPECTATIONS):
        errors.append("scenario_registry:ids_not_exact")
    for entry in registry:
        scenario_id = entry.get("scenario_id")
        if scenario_id not in SCENARIO_EXPECTATIONS:
            continue
        decision, reasons, after_terminal = SCENARIO_EXPECTATIONS[scenario_id]
        if entry.get("decision") != decision:
            errors.append(f"scenario_registry:{scenario_id}:decision")
        if entry.get("reason_codes") != reasons:
            errors.append(f"scenario_registry:{scenario_id}:reason_codes")
        if entry.get("expected_after_terminal") != after_terminal:
            errors.append(f"scenario_registry:{scenario_id}:after_terminal")
    boundary = contract.get("zero_runtime_boundary", {})
    for key in (
        "runtime_started",
        "provider_calls",
        "adapters_executed",
        "network_operations",
        "database_operations",
        "source_operations",
        "tool_operations",
        "command_operations",
    ):
        if boundary.get(key) is not False and boundary.get(key) != 0:
            errors.append(f"zero_runtime_boundary:{key}:opening_detected")
    if boundary.get("product_or_patient_data") is not False:
        errors.append("zero_runtime_boundary:product_or_patient_data")
    return sorted(set(errors))


def validate_scenario_packet(
    packet: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if packet.get("schema_version") != "emr4.aes_c1.authored_synthetic_admission_scenarios.v1":
        errors.append("scenarios:schema_version")
    if packet.get("evidence_mode") != "authored_synthetic_provider_free_unmounted":
        errors.append("scenarios:evidence_mode")
    scenarios = packet.get("scenarios", [])
    if not isinstance(scenarios, list) or len(scenarios) != len(SCENARIO_EXPECTATIONS):
        errors.append("scenarios:count")
        return sorted(set(errors))
    ids = [scenario.get("scenario_id") for scenario in scenarios]
    if len(set(ids)) != len(ids):
        errors.append("scenarios:duplicate_ids")
    if set(ids) != set(SCENARIO_EXPECTATIONS):
        errors.append("scenarios:undeclared_ids")
    for attempt in scenarios:
        errors.extend(validate_attempt(attempt))
    return sorted(set(errors))


def _finish(
    attempt: dict[str, Any],
    grant: dict[str, Any] | None,
    ceilings: dict[str, int],
    observed: dict[str, int],
    prospective: dict[str, int],
    decision: str,
    reason_code: str,
) -> dict[str, Any]:
    manifest = attempt["generation_manifest"]
    lease = attempt["capability_lease"]
    budget_state = attempt["budget_state"]
    observed_op = attempt["broker_observed_operation"]
    proof = attempt["proofreader_result"]
    candidate = attempt["candidate"]
    clock = attempt["evaluation_clock"]
    scenario_id = attempt["scenario_id"]

    if decision == "allow":
        after_observed = {
            key: observed[key] + prospective[key] for key in COUNTER_KEYS
        }
        terminal = any(
            ceilings[key] > 0 and after_observed[key] >= ceilings[key]
            for key in COUNTER_KEYS
        )
        terminal_state = "exhausted" if terminal else "active"
        next_permitted = not terminal
    elif decision == "deny":
        after_observed = dict(observed)
        after_observed["denied_operations"] += 1
        if reason_code in (
            "forbidden_capability_class",
            "operation_identity_candidate_controlled",
        ):
            after_observed["boundary_probes"] += 1
        terminal = any(
            ceilings[key] > 0 and after_observed[key] >= ceilings[key]
            for key in ("denied_operations", "boundary_probes", "repeated_failures")
        )
        terminal_state = "exhausted" if terminal else "active"
        next_permitted = not terminal
    else:
        after_observed = dict(observed)
        terminal = True
        terminal_state = _STOP_TERMINAL_STATE.get(reason_code, "exhausted")
        next_permitted = False

    candidate_digest = digest_of(candidate)
    budget_before_digest = digest_of(
        {"ceilings": budget_state["ceilings"], "observed": observed}
    )
    budget_after_digest = digest_of(
        {
            "ceilings": budget_state["ceilings"],
            "observed": after_observed,
            "terminal_state": terminal_state,
            "next_operation_permitted": next_permitted,
        }
    )

    manifest_and_lease_match = (
        _lease_matches_grant(lease, manifest, grant)
        if grant is not None
        else _lease_manifest_identity_match(lease, manifest)
    )
    return _finish_build(
        attempt, observed_op, proof, candidate, clock, scenario_id, decision,
        reason_code, after_observed, terminal_state, next_permitted,
        candidate_digest, budget_before_digest, budget_after_digest,
        manifest_and_lease_match,
    )


def _finish_build(
    attempt: dict[str, Any],
    observed_op: dict[str, Any],
    proof: dict[str, Any],
    candidate: dict[str, Any],
    clock: str,
    scenario_id: str,
    decision: str,
    reason_code: str,
    after_observed: dict[str, int],
    terminal_state: str,
    next_permitted: bool,
    candidate_digest: str,
    budget_before_digest: str,
    budget_after_digest: str,
    manifest_and_lease_match: bool,
) -> dict[str, Any]:
    manifest = attempt["generation_manifest"]
    lease = attempt["capability_lease"]

    broker_decision = {
        "schema_version": "emr4.aes_c0.broker_decision.v1",
        "decision_id": f"decision-{scenario_id}",
        "generation_id": manifest["generation_id"],
        "manifest_digest": manifest["manifest_digest"],
        "lease_id": lease["lease_id"],
        "capability_id": observed_op["capability_id"],
        "capability_class": observed_op["capability_class"],
        "candidate_digest": candidate_digest,
        "decision": decision,
        "reason_codes": [reason_code],
        "proofreader_admitted": proof["admitted"],
        "current_authority_checked": True,
        "manifest_and_lease_match": manifest_and_lease_match,
        "operation_identity_broker_resolved": True,
        "candidate_supplied_operation_identity": False,
        "budget_before_digest": budget_before_digest,
        "budget_after_digest": budget_after_digest,
        "command_authority": False,
        "recorded_at": clock,
    }

    revocation_state = _revocation_state(attempt, decision, reason_code)
    evidence = {
        "schema_version": "emr4.aes_c0.audit_evidence.v1",
        "evidence_id": f"evidence-{scenario_id}",
        "generation_id": manifest["generation_id"],
        "manifest_digest": manifest["manifest_digest"],
        "correlation_id": f"correlation-{scenario_id}",
        "recorded_at": clock,
        "decision": decision,
        "reason_codes": [reason_code.replace("_", "-")],
        "cumulative_counts": after_observed,
        "artifact_digests": [
            candidate_digest,
            budget_before_digest,
            budget_after_digest,
        ],
        "revocation_state": revocation_state,
        "contains_sensitive_values": False,
    }

    return {
        "scenario_id": scenario_id,
        "decision": decision,
        "reason_codes": [reason_code],
        "after_observed": after_observed,
        "after_terminal_state": terminal_state,
        "after_next_operation_permitted": next_permitted,
        "broker_decision": broker_decision,
        "evidence": evidence,
    }


def evaluate_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one closed AdmissionAttempt with the fixed ordered precedence."""
    manifest = attempt["generation_manifest"]
    lease = attempt["capability_lease"]
    budget_state = attempt["budget_state"]
    observed_op = attempt["broker_observed_operation"]
    proof = attempt["proofreader_result"]
    candidate = attempt["candidate"]
    now = _dt(attempt["evaluation_clock"])

    ceilings = _flatten_ceilings(budget_state["ceilings"])
    observed = dict(budget_state["observed"])
    prospective = observed_op["prospective"]

    grant: dict[str, Any] | None = None
    for item in manifest["capability_grants"]:
        if item["capability_id"] == observed_op["capability_id"]:
            grant = item
            break

    # Step 3: external kill, revocation, supersession, manifest/digest and
    # supply-chain mismatch.
    if attempt["external_kill_switch_active"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "external_kill_switch",
        )
    revocation = attempt.get("revocation_record")
    if revocation is not None and _dt(revocation["effective_at"]) <= now:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "external_kill_switch",
        )
    cg = attempt["current_generation_state"]
    if cg["current_generation_id"] != manifest["generation_id"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "generation_superseded",
        )
    if cg["current_manifest_id"] != manifest["manifest_id"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "generation_superseded",
        )
    if cg["current_manifest_digest"] != manifest["manifest_digest"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "supply_chain_identity_mismatch",
        )
    if compute_manifest_digest(manifest) != manifest["manifest_digest"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "supply_chain_identity_mismatch",
        )
    if _supply_chain_mismatch(
        manifest["supply_chain_identity"], cg["supply_chain_identity"]
    ):
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "supply_chain_identity_mismatch",
        )

    # Step 4: temporal validity of manifest and lease.
    if not (_dt(manifest["issued_at"]) <= now <= _dt(manifest["expires_at"])):
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "authority_changed",
        )
    if not (_dt(lease["issued_at"]) <= now <= _dt(lease["expires_at"])):
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop", "lease_invalid",
        )
    if _dt(lease["expires_at"]) > _dt(manifest["expires_at"]):
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop", "lease_invalid",
        )

    # Step 5: current authority equality.
    ca = attempt["current_authority_state"]
    if ca["is_stale"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "authority_changed",
        )
    if ca["authority_binding_digest"] != manifest["authority_binding_digest"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "authority_changed",
        )
    if ca["purpose_code"] != manifest["purpose_code"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "authority_changed",
        )
    if ca["bureau_id"] != manifest["bureau_id"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "authority_changed",
        )
    if ca["work_cell_id"] != manifest["work_cell_id"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop",
            "authority_changed",
        )

    # Step 6: forbidden capability class / exact manifest grant.
    if observed_op["requested_capability_class"] in ALWAYS_DENIED:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "deny",
            "forbidden_capability_class",
        )
    if grant is None or _grant_mismatch(grant, observed_op):
        return _finish(
            attempt, grant, ceilings, observed, prospective, "deny",
            "manifest_grant_missing",
        )

    # Step 7: lease intersection.
    if not _lease_matches_grant(lease, manifest, grant):
        return _finish(
            attempt, grant, ceilings, observed, prospective, "deny", "lease_invalid",
        )

    # Step 8: candidate-controlled operation identity / proofreader rejection.
    if _forbidden_keys(candidate, FORBIDDEN_CANDIDATE_KEYS):
        return _finish(
            attempt, grant, ceilings, observed, prospective, "deny",
            "operation_identity_candidate_controlled",
        )
    if not proof["admitted"]:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "deny",
            "proofreader_not_admitted",
        )

    # Step 9: budgets.
    budget_reason = _budget_stop(ceilings, observed, prospective)
    if budget_reason is not None:
        return _finish(
            attempt, grant, ceilings, observed, prospective, "stop", budget_reason,
        )

    # Step 10: allow the broker-observed operation without executing it.
    return _finish(
        attempt, grant, ceilings, observed, prospective, "allow",
        "manifest_grant_and_current_authority",
    )


# ---------------------------------------------------------------------------
# Authored-synthetic scenario authoring
# ---------------------------------------------------------------------------

def _canonical_grant() -> dict[str, Any]:
    return {
        "capability_id": "capability-synthetic-inert",
        "capability_class": "inert_tool_adapter",
        "operation_id": "render-inert-adapter",
        "adapter_id": "synthetic-inert-adapter",
        "destination_id": "synthetic-inert-destination",
        "method": "POST",
        "media_type": "application/json",
        "audience": "synthetic-inert-audience",
        "source_class": "authored_synthetic",
        "allowed_input_fields": ["scenario-code", "typed-context"],
        "allowed_output_fields": ["candidate-code", "explanation-code"],
        "max_calls": 2,
        "max_request_bytes": 8192,
        "max_response_bytes": 4096,
        "candidate_selects_operation_identity": False,
        "provider_executed_tools": False,
        "command_authority": False,
    }


def _canonical_budgets() -> dict[str, Any]:
    return {
        "reasoning": {"max_model_calls": 2, "max_model_tokens": 4096},
        "information": {
            "max_input_bytes": 8192,
            "max_output_bytes": 4096,
            "max_source_count": 2,
        },
        "egress": {
            "max_requests": 2,
            "max_request_bytes": 8192,
            "max_response_bytes": 4096,
            "max_total_bytes": 12288,
            "max_distinct_destinations": 1,
            "max_redirects": 0,
        },
        "action": {
            "max_broker_operations": 2,
            "max_inert_tool_operations": 2,
            "max_product_mutations": 0,
            "max_command_confirmations": 0,
        },
        "denial": {
            "max_denials": 3,
            "max_boundary_probes": 2,
            "max_repeated_failures": 2,
        },
        "time": {"max_elapsed_ms": 30000},
    }


def _canonical_manifest() -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c0.generation_manifest.v1",
        "manifest_id": "manifest-synthetic-001",
        "manifest_digest": "PLACEHOLDER_DIGEST",
        "generation_id": "generation-synthetic-001",
        "bureau_id": "bureau-synthetic",
        "work_cell_id": "work-cell-synthetic-001",
        "authority_binding_digest": AUTHORITY_DIGEST,
        "purpose_code": "admission-rehearsal",
        "issued_at": ISSUED_AT,
        "expires_at": EXPIRES_AT,
        "immutable": True,
        "capability_grants": [_canonical_grant()],
        "budgets": _canonical_budgets(),
        "stop_conditions": [
            "reasoning-budget-exhausted",
            "information-budget-exhausted",
            "egress-budget-exhausted",
            "action-budget-exhausted",
            "denial-budget-exhausted",
            "elapsed-time-exhausted",
            "boundary-probe-detected",
            "authority-changed",
            "generation-superseded",
            "supply-chain-identity-mismatch",
            "external-kill-switch",
        ],
        "supply_chain_identity": dict(SUPPLY_DIGESTS),
        "command_authority": False,
    }


def _canonical_lease() -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c0.capability_lease.v1",
        "lease_id": "lease-synthetic-001",
        "manifest_id": "manifest-synthetic-001",
        "generation_id": "generation-synthetic-001",
        "capability_id": "capability-synthetic-inert",
        "capability_class": "inert_tool_adapter",
        "audience": "synthetic-inert-audience",
        "broker_id": "broker-synthetic",
        "authority_binding_digest": AUTHORITY_DIGEST,
        "issued_at": ISSUED_AT,
        "expires_at": EXPIRES_AT,
        "state": "active",
        "presented_to_work_cell": False,
        "reusable_credential": False,
        "command_authority": False,
    }


ZERO_OBSERVED = {counter: 0 for counter in COUNTER_KEYS}


def _canonical_budget_state(
    observed: dict[str, int] | None = None,
    terminal_state: str = "active",
    next_operation_permitted: bool = True,
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c0.budget_state.v1",
        "manifest_id": "manifest-synthetic-001",
        "generation_id": "generation-synthetic-001",
        "ceilings": _canonical_budgets(),
        "observed": dict(ZERO_OBSERVED if observed is None else observed),
        "counts_cumulative": True,
        "terminal_state": terminal_state,
        "next_operation_permitted": next_operation_permitted,
    }


def _canonical_prospective() -> dict[str, int]:
    return {
        "model_calls": 0,
        "model_tokens": 0,
        "input_bytes": 1024,
        "output_bytes": 256,
        "source_count": 1,
        "request_count": 1,
        "request_bytes": 1024,
        "response_bytes": 256,
        "total_bytes": 1280,
        "distinct_destinations": 0,
        "redirects": 0,
        "broker_operations": 1,
        "inert_tool_operations": 1,
        "product_mutations": 0,
        "command_confirmations": 0,
        "denied_operations": 0,
        "boundary_probes": 0,
        "repeated_failures": 0,
        "elapsed_ms": 500,
    }


def _canonical_current_generation_state() -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.current_generation_state.v1",
        "current_generation_id": "generation-synthetic-001",
        "current_manifest_id": "manifest-synthetic-001",
        "current_manifest_digest": "PLACEHOLDER_DIGEST",
        "supply_chain_identity": dict(SUPPLY_DIGESTS),
    }


def _canonical_current_authority_state() -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.current_authority_state.v1",
        "authority_binding_digest": AUTHORITY_DIGEST,
        "purpose_code": "admission-rehearsal",
        "bureau_id": "bureau-synthetic",
        "work_cell_id": "work-cell-synthetic-001",
        "checked_at": ISSUED_AT_NOW,
        "is_stale": False,
    }


def _canonical_proofreader() -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.proofreader_result.v1",
        "admitted": True,
        "reasons": ["closed-typed-candidate"],
    }


def _canonical_candidate(scenario_id: str) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.closed_candidate.v1",
        "candidate_id": f"candidate-{scenario_id}",
        "typed_arguments": {
            "scenario-code": scenario_id,
            "typed-context": "authored-synthetic",
        },
        "proposal_fields": {"proposal-code": "proposal-synthetic-001"},
        "explanation_codes": ["closed-typed-candidate"],
    }


def _canonical_observed_operation(
    scenario_id: str, prospective: dict[str, int] | None = None
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.broker_observed_operation.v1",
        "capability_id": "capability-synthetic-inert",
        "capability_class": "inert_tool_adapter",
        "requested_capability_class": "inert_tool_adapter",
        "operation_id": "render-inert-adapter",
        "adapter_id": "synthetic-inert-adapter",
        "destination_id": "synthetic-inert-destination",
        "method": "POST",
        "media_type": "application/json",
        "audience": "synthetic-inert-audience",
        "source_class": "authored_synthetic",
        "source_fields": ["scenario-code", "typed-context"],
        "output_fields": ["candidate-code", "explanation-code"],
        "prospective": dict(_canonical_prospective() if prospective is None else prospective),
    }


def _base_attempt(scenario_id: str) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.admission_attempt.v1",
        "attempt_id": f"attempt-{scenario_id}",
        "scenario_id": scenario_id,
        "evaluation_clock": EVALUATION_CLOCK,
        "external_kill_switch_active": False,
        "current_generation_state": _canonical_current_generation_state(),
        "current_authority_state": _canonical_current_authority_state(),
        "generation_manifest": _canonical_manifest(),
        "capability_lease": _canonical_lease(),
        "budget_state": _canonical_budget_state(),
        "revocation_record": None,
        "proofreader_result": _canonical_proofreader(),
        "candidate": _canonical_candidate(scenario_id),
        "broker_observed_operation": _canonical_observed_operation(scenario_id),
    }


def _finalize_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    manifest = attempt["generation_manifest"]
    digest = compute_manifest_digest(manifest)
    manifest["manifest_digest"] = digest
    manifest["supply_chain_identity"]["generation_manifest_digest"] = digest
    attempt["current_generation_state"]["current_manifest_digest"] = digest
    attempt["current_generation_state"]["supply_chain_identity"][
        "generation_manifest_digest"
    ] = digest
    return attempt


def _sample_revocation(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c0.revocation_record.v1",
        "revocation_id": "revocation-synthetic-001",
        "generation_id": manifest["generation_id"],
        "manifest_digest": manifest["manifest_digest"],
        "initiated_by": "external_operator",
        "reason_code": "external_stop",
        "effective_at": ISSUED_AT_NOW,
        "all_leases_revoked": True,
        "all_aliases_invalidated": True,
        "all_tokens_invalidated": True,
        "all_writable_caches_quarantined": True,
        "all_further_calls_blocked": True,
        "conversation_clear_is_cleanup": False,
        "model_influenced_revocation": False,
        "evidence_digest": (
            "sha256:4444444444444444444444444444444444444444444444444444444444444444"
        ),
    }


def _build_scenarios() -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []

    def add(
        scenario_id: str,
        mutate: Callable[[dict[str, Any]], None],
        *,
        finalize: bool = True,
    ) -> None:
        attempt = _base_attempt(scenario_id)
        mutate(attempt)
        if finalize:
            _finalize_attempt(attempt)
        revocation = attempt.get("revocation_record")
        if revocation is not None:
            revocation["manifest_digest"] = attempt["generation_manifest"][
                "manifest_digest"
            ]
        attempts.append(attempt)

    # 1-2: allow scenarios.
    add("exact-inert-intersection-allow", lambda a: None)

    def sc2(a: dict[str, Any]) -> None:
        prospective = _canonical_prospective()
        after_first = {
            key: ZERO_OBSERVED[key] + prospective[key] for key in COUNTER_KEYS
        }
        a["budget_state"]["observed"] = after_first

    add("exact-inert-second-within-budget-allow", sc2)

    # 3-16: manifest-grant denials.
    add(
        "grant-missing-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "capability_id"),
                           "capability-synthetic-absent"),
    )
    def sc4(a: dict[str, Any]) -> None:
        _set_path(a, ("broker_observed_operation", "capability_class"),
                  "authoritative_read")
        _set_path(a, ("broker_observed_operation", "requested_capability_class"),
                  "authoritative_read")

    add("grant-class-mismatch-deny", sc4)
    add(
        "grant-operation-mismatch-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "operation_id"),
                           "read-authoritative-context"),
    )
    add(
        "grant-adapter-mismatch-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "adapter_id"),
                           "synthetic-other-adapter"),
    )
    add(
        "grant-destination-mismatch-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "destination_id"),
                           "synthetic-other-destination"),
    )
    add(
        "grant-method-mismatch-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "method"), "GET"),
    )
    add(
        "grant-media-type-mismatch-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "media_type"),
                           "text/plain"),
    )
    add(
        "grant-audience-mismatch-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "audience"),
                           "synthetic-other-audience"),
    )
    add(
        "grant-source-class-mismatch-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "source_class"),
                           "authorized_product_read"),
    )
    add(
        "grant-input-field-overreach-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "source_fields"),
                           ["scenario-code", "typed-context", "extra-field"]),
    )
    add(
        "grant-output-field-overreach-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "output_fields"),
                           ["candidate-code", "explanation-code", "extra-field"]),
    )

    def sc14(a: dict[str, Any]) -> None:
        _set_path(a, ("generation_manifest", "capability_grants", 0, "max_calls"), 1)
        _set_path(a, ("broker_observed_operation", "prospective", "request_count"), 2)

    add("grant-call-limit-deny", sc14)
    add(
        "grant-request-byte-limit-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "prospective",
                                "request_bytes"), 16384),
    )
    add(
        "grant-response-byte-limit-deny",
        lambda a: _set_path(a, ("broker_observed_operation", "prospective",
                                "response_bytes"), 8192),
    )

    # 17-19: candidate identity, proofreader, forbidden class.
    def sc17(a: dict[str, Any]) -> None:
        _set_path(a, ("candidate", "typed_arguments", "operation_id"),
                  "candidate-forged-operation")

    add("candidate-operation-identity-deny", sc17)

    def sc18(a: dict[str, Any]) -> None:
        _set_path(a, ("proofreader_result", "admitted"), False)
        _set_path(a, ("proofreader_result", "reasons"), ["unbounded-candidate-field"])

    add("proofreader-not-admitted-deny", sc18)
    add(
        "forbidden-capability-class-deny",
        lambda a: _set_path(a, ("broker_observed_operation",
                                "requested_capability_class"), "generic_network"),
    )

    # 20-26: lease denials.
    add(
        "lease-state-inactive-deny",
        lambda a: _set_path(a, ("capability_lease", "state"), "revoked"),
    )
    add(
        "lease-manifest-mismatch-deny",
        lambda a: _set_path(a, ("capability_lease", "manifest_id"),
                           "manifest-synthetic-999"),
    )
    add(
        "lease-generation-mismatch-deny",
        lambda a: _set_path(a, ("capability_lease", "generation_id"),
                           "generation-synthetic-999"),
    )
    add(
        "lease-capability-mismatch-deny",
        lambda a: _set_path(a, ("capability_lease", "capability_id"),
                           "capability-synthetic-other"),
    )
    add(
        "lease-class-mismatch-deny",
        lambda a: _set_path(a, ("capability_lease", "capability_class"),
                           "authoritative_read"),
    )
    add(
        "lease-audience-mismatch-deny",
        lambda a: _set_path(a, ("capability_lease", "audience"),
                           "synthetic-other-audience"),
    )
    add(
        "lease-authority-mismatch-deny",
        lambda a: _set_path(a, ("capability_lease", "authority_binding_digest"),
                           WRONG_DIGEST),
    )

    # 27-29: temporal stops.
    add(
        "lease-outlives-manifest-stop",
        lambda a: _set_path(a, ("capability_lease", "expires_at"),
                           "2026-08-11T00:10:00Z"),
    )
    add(
        "lease-expired-stop",
        lambda a: _set_path(a, ("capability_lease", "expires_at"),
                           "2026-08-11T00:00:00Z"),
    )

    def sc29(a: dict[str, Any]) -> None:
        _set_path(a, ("generation_manifest", "expires_at"), "2026-08-11T00:00:00Z")
        _set_path(a, ("capability_lease", "expires_at"), "2026-08-11T00:00:00Z")

    add("manifest-expired-stop", sc29)

    # 30: manifest content digest mismatch (intentionally wrong digest, no finalize).
    def sc30(a: dict[str, Any]) -> None:
        _set_path(a, ("generation_manifest", "manifest_digest"), WRONG_DIGEST)
        _set_path(a, ("generation_manifest", "supply_chain_identity",
                      "generation_manifest_digest"), WRONG_DIGEST)
        _set_path(a, ("current_generation_state", "current_manifest_digest"),
                  WRONG_DIGEST)
        _set_path(a, ("current_generation_state", "supply_chain_identity",
                      "generation_manifest_digest"), WRONG_DIGEST)

    add("manifest-content-digest-mismatch-stop", sc30, finalize=False)

    # 31: generation superseded.
    add(
        "generation-superseded-stop",
        lambda a: _set_path(a, ("current_generation_state", "current_generation_id"),
                           "generation-synthetic-002"),
    )

    # 32: cross-generation replay (records from a non-current generation).
    def sc32(a: dict[str, Any]) -> None:
        _set_path(a, ("generation_manifest", "generation_id"),
                  "generation-synthetic-002")
        _set_path(a, ("generation_manifest", "manifest_id"), "manifest-synthetic-002")
        _set_path(a, ("capability_lease", "generation_id"), "generation-synthetic-002")
        _set_path(a, ("capability_lease", "manifest_id"), "manifest-synthetic-002")
        _set_path(a, ("budget_state", "generation_id"), "generation-synthetic-002")
        _set_path(a, ("budget_state", "manifest_id"), "manifest-synthetic-002")

    add("cross-generation-replay-stop", sc32)

    # 33-37: authority changes and stale authority.
    add(
        "authority-binding-changed-stop",
        lambda a: _set_path(a, ("current_authority_state", "authority_binding_digest"),
                           WRONG_DIGEST),
    )
    add(
        "authority-purpose-changed-stop",
        lambda a: _set_path(a, ("current_authority_state", "purpose_code"),
                           "different-purpose"),
    )
    add(
        "authority-bureau-changed-stop",
        lambda a: _set_path(a, ("current_authority_state", "bureau_id"),
                           "bureau-different"),
    )
    add(
        "authority-work-cell-changed-stop",
        lambda a: _set_path(a, ("current_authority_state", "work_cell_id"),
                           "work-cell-different"),
    )
    add(
        "authority-stale-stop",
        lambda a: _set_path(a, ("current_authority_state", "is_stale"), True),
    )

    # 38: supply-chain identity mismatch.
    add(
        "supply-chain-identity-mismatch-stop",
        lambda a: _set_path(a, ("current_generation_state", "supply_chain_identity",
                                "runtime_image_digest"), WRONG_DIGEST),
    )

    # 39: existing revocation.
    def sc39(a: dict[str, Any]) -> None:
        a["revocation_record"] = _sample_revocation(a["generation_manifest"])

    add("existing-revocation-stop", sc39)

    # 40: external kill switch.
    add(
        "external-kill-switch-stop",
        lambda a: _set_path(a, ("external_kill_switch_active",), True),
    )

    # 41: cumulative budget already exhausted.
    def sc41(a: dict[str, Any]) -> None:
        observed = {key: 0 for key in COUNTER_KEYS}
        observed["request_count"] = 2
        a["budget_state"]["observed"] = observed
        a["budget_state"]["terminal_state"] = "exhausted"
        a["budget_state"]["next_operation_permitted"] = False

    add("cumulative-budget-already-exhausted-stop", sc41)

    # 42: prospective budget overflow.
    def sc42(a: dict[str, Any]) -> None:
        observed = {key: 0 for key in COUNTER_KEYS}
        observed["request_count"] = 1
        a["budget_state"]["observed"] = observed
        prospective = _canonical_prospective()
        prospective["request_count"] = 2
        a["broker_observed_operation"]["prospective"] = prospective

    add("prospective-budget-overflow-stop", sc42)

    # 43: zero-disabled capability.
    def sc43(a: dict[str, Any]) -> None:
        budgets = _canonical_budgets()
        budgets["action"]["max_inert_tool_operations"] = 0
        a["generation_manifest"]["budgets"] = budgets
        a["budget_state"]["ceilings"] = budgets

    add("zero-disabled-capability-stop", sc43)

    # 44: denial ceiling reached after a deny.
    def sc44(a: dict[str, Any]) -> None:
        observed = {key: 0 for key in COUNTER_KEYS}
        observed["denied_operations"] = 2
        a["budget_state"]["observed"] = observed
        _set_path(a, ("broker_observed_operation", "capability_id"),
                  "capability-synthetic-absent")

    add("denial-ceiling-reached-after-deny", sc44)

    # 45: following attempt after the denial ceiling is reached.
    def sc45(a: dict[str, Any]) -> None:
        observed = {key: 0 for key in COUNTER_KEYS}
        observed["denied_operations"] = 3
        a["budget_state"]["observed"] = observed
        a["budget_state"]["terminal_state"] = "exhausted"
        a["budget_state"]["next_operation_permitted"] = False

    add("attempt-after-denial-ceiling-stop", sc45)

    return attempts


def _hostile_mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    return [
        ("missing_attempt_id", lambda a: _del_path(a, ("attempt_id",))),
        ("missing_candidate", lambda a: _del_path(a, ("candidate",))),
        ("extra_attempt_field", lambda a: _set_path(a, ("forged_field",), "forged")),
        ("wrong_type_scenario_id", lambda a: _set_path(a, ("scenario_id",), 7)),
        ("wrong_type_kill_switch", lambda a: _set_path(
            a, ("external_kill_switch_active",), "yes")),
        ("missing_generation_manifest", lambda a: _del_path(
            a, ("generation_manifest",))),
        ("wrong_type_budget_counter", lambda a: _set_path(
            a, ("budget_state", "observed", "request_count"), "2")),
        ("wrong_type_prospective", lambda a: _set_path(
            a, ("broker_observed_operation", "prospective"), [1, 2])),
        ("candidate_forged_operation_id", lambda a: _set_path(
            a, ("candidate", "typed_arguments", "operation_id"), "forged")),
        ("candidate_forged_url", lambda a: _set_path(
            a, ("candidate", "proposal_fields", "url"), "https://forged")),
        ("candidate_forged_credential", lambda a: _set_path(
            a, ("candidate", "typed_arguments", "credential"), "secret")),
        ("candidate_forged_sql", lambda a: _set_path(
            a, ("candidate", "typed_arguments", "sql"), "SELECT 1")),
        ("over_budget_prospective", lambda a: _set_path(
            a, ("broker_observed_operation", "prospective", "request_count"), 3)),
        ("forbidden_requested_class", lambda a: _set_path(
            a, ("broker_observed_operation", "requested_capability_class"),
            "shell_or_process")),
        ("stale_authority", lambda a: _set_path(
            a, ("current_authority_state", "is_stale"), True)),
        ("revocation_present", lambda a: a.__setitem__(
            "revocation_record", _sample_revocation(a["generation_manifest"]))),
        ("kill_switch_active", lambda a: _set_path(
            a, ("external_kill_switch_active",), True)),
        ("lease_state_revoked", lambda a: _set_path(
            a, ("capability_lease", "state"), "revoked")),
        ("manifest_digest_tampered", lambda a: _set_path(
            a, ("generation_manifest", "manifest_digest"), WRONG_DIGEST)),
        ("cross_generation_replay", lambda a: _set_path(
            a, ("current_generation_state", "current_generation_id"),
            "generation-synthetic-002")),
        ("supply_chain_tampered", lambda a: _set_path(
            a, ("current_generation_state", "supply_chain_identity",
                "system_contract_digest"), WRONG_DIGEST)),
        ("budget_ceiling_tampered", lambda a: _set_path(
            a, ("budget_state", "ceilings", "egress", "max_requests"), 99)),
    ]


def validate_hostile_mutations() -> tuple[list[str], list[str]]:
    """Apply independent hostile mutations; zero may be admitted."""
    base = _base_attempt("mutation-base")
    _finalize_attempt(base)
    rejected: list[str] = []
    admitted: list[str] = []
    for name, mutate in _hostile_mutations():
        candidate = copy.deepcopy(base)
        mutate(candidate)
        errors = validate_attempt(candidate)
        if errors:
            rejected.append(name)
            continue
        result = evaluate_attempt(candidate)
        if result["decision"] == "allow":
            admitted.append(name)
        else:
            rejected.append(name)
    return rejected, admitted


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    packet = _load(SCENARIOS_PATH)

    reasons: list[str] = []
    reasons.extend(validate_contract(contract, schema))
    reasons.extend(validate_scenario_packet(packet, schema))

    inherited = contract["inherited_artifact_digests"]
    for rel, expected in inherited.items():
        if _digest(ROOT / rel) != expected:
            reasons.append(f"inherited_artifact_digest_mismatch:{rel}")

    scenario_results: list[dict[str, Any]] = []
    allow_count = 0
    deny_count = 0
    stop_count = 0
    for attempt in packet["scenarios"]:
        scenario_id = attempt["scenario_id"]
        result = evaluate_attempt(attempt)
        expected_decision, expected_reasons, expected_after_terminal = (
            SCENARIO_EXPECTATIONS[scenario_id]
        )
        if result["decision"] != expected_decision:
            reasons.append(f"scenario:{scenario_id}:decision")
        if result["reason_codes"] != expected_reasons:
            reasons.append(f"scenario:{scenario_id}:reason_codes")
        if expected_after_terminal is not (
            result["after_next_operation_permitted"] is False
        ):
            reasons.append(f"scenario:{scenario_id}:after_terminal")
        broker_errors = validate_instance(
            result["broker_decision"],
            AES_C0_SCHEMA["$defs"]["BrokerDecision"],
            root_schema=AES_C0_SCHEMA,
            path=f"$.scenarios[{scenario_id}].broker_decision",
        )
        evidence_errors = validate_instance(
            result["evidence"],
            AES_C0_SCHEMA["$defs"]["AuditEvidenceEnvelope"],
            root_schema=AES_C0_SCHEMA,
            path=f"$.scenarios[{scenario_id}].evidence",
        )
        if broker_errors:
            reasons.append(f"scenario:{scenario_id}:broker_decision_invalid")
        if evidence_errors:
            reasons.append(f"scenario:{scenario_id}:evidence_invalid")
        if result["decision"] == "allow":
            allow_count += 1
        elif result["decision"] == "deny":
            deny_count += 1
        else:
            stop_count += 1
        scenario_results.append(
            {
                "scenario_id": scenario_id,
                "decision": result["decision"],
                "reason_codes": result["reason_codes"],
                "broker_decision_digest": digest_of(result["broker_decision"]),
                "evidence_envelope_digest": digest_of(result["evidence"]),
                "after_terminal_state": result["after_terminal_state"],
                "after_next_operation_permitted": result[
                    "after_next_operation_permitted"
                ],
                "broker_decision": result["broker_decision"],
                "evidence": result["evidence"],
            }
        )

    rejected, admitted = validate_hostile_mutations()
    if admitted:
        reasons.append("hostile_mutations_admitted:" + ",".join(admitted))

    status = "passed" if not reasons else "revision_required"
    return {
        "schema_version": "emr4.aes_c1.admission_report.v1",
        "status": status,
        "evidence_mode": "authored_synthetic_provider_free_unmounted",
        "runtime_started": False,
        "provider_calls": 0,
        "adapters_executed": 0,
        "network_operations": 0,
        "database_operations": 0,
        "source_operations": 0,
        "tool_operations": 0,
        "command_operations": 0,
        "product_or_patient_data": False,
        "inherited_artifact_digests": inherited,
        "scenario_count": len(scenario_results),
        "allow_count": allow_count,
        "deny_count": deny_count,
        "stop_count": stop_count,
        "scenario_results": scenario_results,
        "mutation_count": len(_hostile_mutations()),
        "mutation_rejected_count": len(rejected),
        "mutation_admitted": admitted,
        "reasons": sorted(set(reasons)),
        "artifact_digests": {
            CONTRACT_PATH.relative_to(ROOT).as_posix(): _digest(CONTRACT_PATH),
            SCHEMA_PATH.relative_to(ROOT).as_posix(): _digest(SCHEMA_PATH),
            SCENARIOS_PATH.relative_to(ROOT).as_posix(): _digest(SCENARIOS_PATH),
        },
    }


def generate_scenarios() -> dict[str, Any]:
    attempts = _build_scenarios()
    return {
        "schema_version": "emr4.aes_c1.authored_synthetic_admission_scenarios.v1",
        "evidence_mode": "authored_synthetic_provider_free_unmounted",
        "scenarios": attempts,
    }


def _write_lf(path: Path, content: str) -> None:
    """Write text with explicit LF line endings for deterministic Git output."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generate-scenarios",
        action="store_true",
        help="Regenerate the authored-synthetic scenario packet.",
    )
    args = parser.parse_args()
    if args.generate_scenarios:
        packet = generate_scenarios()
        _write_lf(
            SCENARIOS_PATH,
            json.dumps(packet, indent=2, sort_keys=True) + "\n",
        )
        print(
            "wrote",
            SCENARIOS_PATH.relative_to(ROOT).as_posix(),
            "with",
            len(packet["scenarios"]),
            "scenarios",
        )
        return 0
    report = build_report()
    _write_lf(EVIDENCE_PATH, json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

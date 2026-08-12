from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-conditional-command-admission-rehearsal"
)
SCENARIOS_PATH = PACKET_DIR / "scenarios.json"
SCHEMA_PATH = PACKET_DIR / "scenarios.schema.json"
ARCHITECTURE_CONTRACT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
    / "architecture-contract.json"
)

EXPECTED_CONTRACT_HASH = (
    "sha256:01f0e193d44cfadcfd105d5b824909b397d451dc195260c46f7da47a1fa2c81f"
)
EXPECTED_OPERATIONS = {"create", "update", "status", "delete"}
EXPECTED_OUTCOMES = {
    "committed",
    "idempotent_replay",
    "stale_precondition",
    "schedule_conflict",
    "authority_revoked",
    "confirmation_required",
    "validation_rejected",
    "idempotency_conflict",
}
EXPECTED_SCENARIO_IDS = {f"ccar-{number:03d}-" for number in range(1, 38)}

LOCK_PLANS = {
    "create": ["practice", "schedule_conflict_domain", "idempotency_record"],
    "update": [
        "practice",
        "schedule_conflict_domain",
        "appointment",
        "idempotency_record",
    ],
    "status": ["practice", "appointment", "idempotency_record"],
    "delete": ["practice", "appointment", "idempotency_record"],
}
LOCK_VARIANTS = {
    "canonical": None,
    "missing_schedule_domain": ["practice", "idempotency_record"],
    "missing_appointment": [
        "practice",
        "schedule_conflict_domain",
        "idempotency_record",
    ],
    "reordered": [
        "appointment",
        "schedule_conflict_domain",
        "practice",
        "idempotency_record",
    ],
    "extra_schedule_domain": [
        "practice",
        "schedule_conflict_domain",
        "appointment",
        "idempotency_record",
    ],
}
BINDING_REASONS = {
    "practice_mismatch": "binding_practice_mismatch",
    "actor_mismatch": "binding_actor_mismatch",
    "purpose_mismatch": "binding_purpose_mismatch",
    "operation_mismatch": "binding_operation_mismatch",
    "target_mismatch": "binding_target_mismatch",
    "conflict_domain_mismatch": "binding_conflict_domain_mismatch",
    "command_digest_mismatch": "binding_command_digest_mismatch",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if not scenario["token_authentic"]:
        reasons.append("token_authenticity_invalid")
    if not scenario["token_version_supported"]:
        reasons.append("token_version_unsupported")
    if scenario["token_expired"]:
        reasons.append("token_expired")
    if not scenario["nonce_unused"]:
        reasons.append("nonce_reused")
    binding = scenario["binding_variant"]
    if binding != "exact":
        reasons.append(BINDING_REASONS[binding])
    if scenario["target_shape"] != "valid":
        reasons.append("target_shape_invalid")

    operation = scenario["operation"]
    expected_lock_plan = LOCK_PLANS[operation]
    variant = scenario["lock_plan_variant"]
    observed_lock_plan = (
        expected_lock_plan if variant == "canonical" else LOCK_VARIANTS[variant]
    )
    if observed_lock_plan != expected_lock_plan:
        reasons.append("lock_plan_invalid")

    event_evidence = scenario["event_evidence"]
    if event_evidence == "asserts_current_truth":
        reasons.append("event_cannot_assert_current_truth")
    elif event_evidence == "asserts_command_success":
        reasons.append("event_cannot_assert_command_success")

    if reasons:
        return {
            "scenario_id": scenario["id"],
            "admission": "admission_rejected",
            "outcome": None,
            "reason_codes": sorted(reasons),
            "planned_mutation": False,
            "receipt_disposition": "none",
            "effect_performed": False,
        }

    if not scenario["current_authority"]:
        outcome = "authority_revoked"
    elif scenario["confirmation_required"] and not scenario["confirmation_valid"]:
        outcome = "confirmation_required"
    elif scenario["idempotency_state"] == "same_digest":
        outcome = "idempotent_replay"
    elif scenario["idempotency_state"] == "different_digest":
        outcome = "idempotency_conflict"
    elif scenario["source_state"] == "stale" or scenario["conflict_state"] == "stale":
        outcome = "stale_precondition"
    elif scenario["schedule_conflict"]:
        outcome = "schedule_conflict"
    elif (
        not scenario["domain_valid"]
        or (operation != "create" and not scenario["target_exists"])
        or (operation == "create" and scenario["target_exists"])
    ):
        outcome = "validation_rejected"
    else:
        outcome = "committed"

    return {
        "scenario_id": scenario["id"],
        "admission": "admitted",
        "outcome": outcome,
        "reason_codes": [],
        "planned_mutation": outcome == "committed",
        "receipt_disposition": (
            "planned_new_receipt"
            if outcome == "committed"
            else "original_receipt_reference"
            if outcome == "idempotent_replay"
            else "none"
        ),
        "effect_performed": False,
    }


def semantic_errors(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    binding = packet["contract_binding"]
    if _file_hash(ARCHITECTURE_CONTRACT_PATH) != EXPECTED_CONTRACT_HASH:
        errors.append("architecture_contract_file_hash_mismatch")
    if binding["contract_sha256"] != EXPECTED_CONTRACT_HASH:
        errors.append("packet_contract_hash_mismatch")

    scenarios = packet["scenarios"]
    ids = [scenario["id"] for scenario in scenarios]
    if len(ids) != len(set(ids)):
        errors.append("scenario_id_duplicate")
    prefixes = {scenario_id[:9] for scenario_id in ids}
    if prefixes != EXPECTED_SCENARIO_IDS:
        errors.append("scenario_census_mismatch")
    if {scenario["operation"] for scenario in scenarios} != EXPECTED_OPERATIONS:
        errors.append("operation_census_mismatch")

    observed_outcomes: set[str] = set()
    observed_reasons: set[str] = set()
    for scenario in scenarios:
        result = evaluate_scenario(scenario)
        expected = {
            "admission": scenario["expected_admission"],
            "outcome": scenario["expected_outcome"],
            "reason_codes": sorted(scenario["expected_reason_codes"]),
            "planned_mutation": scenario["expected_planned_mutation"],
        }
        actual = {key: result[key] for key in expected}
        if actual != expected:
            errors.append(f"scenario_expectation_mismatch:{scenario['id']}")
        if result["outcome"] is not None:
            observed_outcomes.add(result["outcome"])
        observed_reasons.update(result["reason_codes"])
        if result["admission"] == "admission_rejected" and result["outcome"] is not None:
            errors.append(f"rejection_has_outcome:{scenario['id']}")
        if result["planned_mutation"] != (result["outcome"] == "committed"):
            errors.append(f"planned_mutation_not_commit_only:{scenario['id']}")
        if result["effect_performed"]:
            errors.append(f"effect_performed:{scenario['id']}")

    if observed_outcomes != EXPECTED_OUTCOMES:
        errors.append("outcome_census_mismatch")
    expected_reason_families = {
        "token_authenticity_invalid",
        "token_version_unsupported",
        "token_expired",
        "nonce_reused",
        *BINDING_REASONS.values(),
        "target_shape_invalid",
        "lock_plan_invalid",
        "event_cannot_assert_current_truth",
        "event_cannot_assert_command_success",
    }
    if observed_reasons != expected_reason_families:
        errors.append("rejection_reason_census_mismatch")
    if any(packet["effect_boundary"].values()):
        errors.append("effect_boundary_not_zero")
    return sorted(set(errors))


def validate_packet(packet: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    Draft202012Validator.check_schema(schema)
    schema_errors = sorted(
        error.message for error in Draft202012Validator(schema).iter_errors(packet)
    )
    if schema_errors:
        return schema_errors
    return semantic_errors(packet)


def hostile_mutations(packet: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutate(name: str, path: tuple[Any, ...], value: Any) -> None:
        candidate = copy.deepcopy(packet)
        cursor: Any = candidate
        for component in path[:-1]:
            cursor = cursor[component]
        cursor[path[-1]] = value
        mutations.append((name, candidate))

    mutate("contract_hash", ("contract_binding", "contract_sha256"), "sha256:" + "0" * 64)
    mutate("effect_runtime", ("effect_boundary", "runtime_started"), True)
    mutate("effect_database", ("effect_boundary", "database_opened"), True)
    mutate("effect_route", ("effect_boundary", "route_imported"), True)
    mutate("effect_event", ("effect_boundary", "event_consumed"), True)
    mutate("effect_provider", ("effect_boundary", "provider_calls"), 1)
    mutate("effect_command", ("effect_boundary", "command_executed"), True)
    mutate("effect_mutation", ("effect_boundary", "mutation_performed"), True)
    mutate("effect_audit", ("effect_boundary", "audit_or_receipt_written"), True)
    mutate("effect_data", ("effect_boundary", "patient_or_product_data"), True)
    mutate("commit_claims_no_plan", ("scenarios", 0, "expected_planned_mutation"), False)
    mutate("commit_claims_replay", ("scenarios", 0, "expected_outcome"), "idempotent_replay")
    mutate("replay_claims_mutation", ("scenarios", 4, "expected_planned_mutation"), True)
    mutate("replay_claims_commit", ("scenarios", 4, "expected_outcome"), "committed")
    mutate("stale_claims_commit", ("scenarios", 6, "expected_outcome"), "committed")
    mutate("conflict_claims_commit", ("scenarios", 8, "expected_outcome"), "committed")
    mutate("revoked_claims_replay", ("scenarios", 9, "expected_outcome"), "idempotent_replay")
    mutate("confirmation_claims_stale", ("scenarios", 10, "expected_outcome"), "stale_precondition")
    mutate("invalid_token_admitted", ("scenarios", 13, "expected_admission"), "admitted")
    mutate("invalid_token_gets_outcome", ("scenarios", 13, "expected_outcome"), "committed")
    mutate("expired_token_no_reason", ("scenarios", 15, "expected_reason_codes"), [])
    mutate("binding_wrong_reason", ("scenarios", 17, "expected_reason_codes"), ["binding_actor_mismatch"])
    mutate("create_without_fence_admitted", ("scenarios", 24, "expected_admission"), "admitted")
    mutate("missing_row_lock_admitted", ("scenarios", 25, "expected_admission"), "admitted")
    mutate("reordered_locks_admitted", ("scenarios", 27, "expected_admission"), "admitted")
    mutate("event_truth_admitted", ("scenarios", 30, "expected_admission"), "admitted")
    mutate("event_success_admitted", ("scenarios", 31, "expected_admission"), "admitted")
    mutate("authority_loses_precedence", ("scenarios", 32, "expected_outcome"), "stale_precondition")
    mutate("confirmation_loses_precedence", ("scenarios", 33, "expected_outcome"), "stale_precondition")
    mutate("replay_loses_precedence", ("scenarios", 34, "expected_outcome"), "stale_precondition")
    mutate("stale_loses_precedence", ("scenarios", 35, "expected_outcome"), "schedule_conflict")
    mutate("conflict_loses_precedence", ("scenarios", 36, "expected_outcome"), "validation_rejected")
    return mutations


def build_report() -> dict[str, Any]:
    packet = _load(SCENARIOS_PATH)
    schema = _load(SCHEMA_PATH)
    errors = validate_packet(packet, schema)
    results = [evaluate_scenario(scenario) for scenario in packet["scenarios"]]
    admitted_mutations = [
        name
        for name, mutation in hostile_mutations(packet)
        if not validate_packet(mutation, schema)
    ]
    return {
        "status": "passed" if not errors and not admitted_mutations else "failed",
        "canonical_errors": errors,
        "scenario_count": len(results),
        "admission_rejected_count": sum(
            result["admission"] == "admission_rejected" for result in results
        ),
        "hostile_mutation_count": len(hostile_mutations(packet)),
        "admitted_mutations": admitted_mutations,
        "outcome_counts": {
            outcome: sum(result["outcome"] == outcome for result in results)
            for outcome in sorted(EXPECTED_OUTCOMES)
        },
        "effect_boundary": packet["effect_boundary"],
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())


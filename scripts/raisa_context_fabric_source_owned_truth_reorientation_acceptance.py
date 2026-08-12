from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
)
CONTRACT_PATH = PACKET_DIR / "architecture-contract.json"
SCHEMA_PATH = PACKET_DIR / "architecture-contract.schema.json"

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


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def semantic_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    planes = contract["authority_planes"]
    source = planes["authoritative_source"]
    fabric = planes["context_fabric"]
    event = planes["event_watcher"]
    command = planes["command_service"]

    if not source["owns_current_truth"] or not source["owns_mutation_serialization"]:
        errors.append("source_must_own_truth_and_serialization")
    if source["depends_on_cue_delivery_for_correctness"]:
        errors.append("correctness_must_not_depend_on_cue_delivery")
    if not fabric["read_only"] or not fabric["expiring"] or fabric["may_mint_write_authority"]:
        errors.append("fabric_must_remain_expiring_read_only_evidence")
    if event != {
        "authority": "acceleration_hint_only",
        "fresh_authorized_read_required": True,
        "may_assert_current_truth": False,
        "may_assert_command_success": False,
    }:
        errors.append("event_must_be_cue_only")
    if set(command.values()) != {True}:
        errors.append("command_service_must_own_all_command_checks")

    packet = contract["conditional_command_packet"]
    if packet["client_may_mint_or_amend"]:
        errors.append("client_must_not_mint_precondition")
    if packet["token_alone_closes_toctou"]:
        errors.append("token_cannot_close_toctou")
    if not packet["current_authority_checked_in_transaction"]:
        errors.append("current_authority_must_be_checked_in_transaction")
    if set(packet["separate_evidence"]) != {
        "human_or_policy_confirmation",
        "idempotency_identity",
        "audit_attribution",
    }:
        errors.append("confirmation_idempotency_audit_must_be_separate")

    transaction = contract["transaction_policy"]
    if transaction["canonical_lock_order"] != [
        "practice",
        "schedule_conflict_domain",
        "appointment",
        "idempotency_record",
    ]:
        errors.append("lock_order_mismatch")
    for key in (
        "short_transaction_required",
        "final_database_invariant_check_required",
        "skip_unneeded_locks_without_reordering",
    ):
        if not transaction[key]:
            errors.append(f"transaction_policy_false:{key}")

    operations = {item["operation"]: item for item in contract["operation_families"]}
    if set(operations) != EXPECTED_OPERATIONS:
        errors.append("operation_family_census_mismatch")
    else:
        create = operations["create"]
        if create["target_row_exists_before_command"]:
            errors.append("create_has_no_target_row")
        if create["required_serialization"] != "schedule_conflict_domain_fence":
            errors.append("create_requires_schedule_domain_fence")
        if set(create["required_rechecks"]) != {
            "current_authority",
            "schedule_overlap",
            "database_constraint",
        }:
            errors.append("create_recheck_set_mismatch")
        for name in ("update", "status", "delete"):
            if not operations[name]["target_row_exists_before_command"]:
                errors.append(f"{name}_target_row_must_exist")
            if "current_authority" not in operations[name]["required_rechecks"]:
                errors.append(f"{name}_must_recheck_current_authority")

    outcomes = {item["code"]: item for item in contract["outcomes"]}
    if set(outcomes) != EXPECTED_OUTCOMES:
        errors.append("outcome_census_mismatch")
    else:
        mutating = {code for code, item in outcomes.items() if item["mutation"]}
        if mutating != {"committed"}:
            errors.append("only_committed_may_mutate")
        replaying = {
            code for code, item in outcomes.items() if item["returns_original_receipt"]
        }
        if replaying != {"idempotent_replay"}:
            errors.append("only_idempotent_replay_returns_original_receipt")

    legacy = contract["legacy_compatibility_migration"]
    if legacy["current_behavior_changed_by_this_contract"]:
        errors.append("architecture_must_not_change_routes")
    if legacy["implicit_freshness_is_human_confirmation"]:
        errors.append("freshness_is_not_human_confirmation")
    if not legacy["retirement_requires_client_parity"]:
        errors.append("legacy_retirement_requires_client_parity")

    durability = contract["deferred_durable_event_and_cue_delivery"]
    if durability["command_authority"] or durability["current_truth_authority"]:
        errors.append("durable_cues_have_no_truth_or_command_authority")
    if not durability["cf_d1_evidence_retained"]:
        errors.append("cf_d1_must_be_retained")
    if durability["cf_d2_reopen_policy"] != "fresh_observability_first_plan_only":
        errors.append("cf_d2_requires_fresh_observability_first_plan")
    topology = durability["consumer_topology"]
    if topology != {
        "logical_consumers_per_partition": 1,
        "initial_physical_processes_per_database": 1,
        "high_availability_mode": "active_standby_with_external_fencing",
        "equal_checkpoint_writers_per_partition": False,
        "duplicate_delivery_policy": "idempotent_at_least_once",
    }:
        errors.append("watcher_topology_must_be_single_logical_owner_with_fenced_ha")

    descendant = contract["next_descendant"]
    if not descendant["authored_synthetic_only"] or any(
        descendant[key]
        for key in ("runtime", "database", "route_change", "provider_call", "command_or_write")
    ):
        errors.append("next_descendant_must_remain_provider_free_and_unmounted")
    return errors


def validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    Draft202012Validator.check_schema(schema)
    schema_errors = sorted(
        error.message for error in Draft202012Validator(schema).iter_errors(contract)
    )
    return schema_errors + semantic_errors(contract)


def hostile_mutations(contract: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    paths_and_values: list[tuple[str, tuple[Any, ...], Any]] = [
        ("source_depends_on_cue", ("authority_planes", "authoritative_source", "depends_on_cue_delivery_for_correctness"), True),
        ("fabric_mints_authority", ("authority_planes", "context_fabric", "may_mint_write_authority"), True),
        ("event_claims_truth", ("authority_planes", "event_watcher", "may_assert_current_truth"), True),
        ("event_claims_success", ("authority_planes", "event_watcher", "may_assert_command_success"), True),
        ("event_skips_fresh_read", ("authority_planes", "event_watcher", "fresh_authorized_read_required"), False),
        ("command_skips_authority", ("authority_planes", "command_service", "owns_current_authority_check"), False),
        ("client_mints_token", ("conditional_command_packet", "client_may_mint_or_amend"), True),
        ("token_closes_toctou", ("conditional_command_packet", "token_alone_closes_toctou"), True),
        ("authority_outside_transaction", ("conditional_command_packet", "current_authority_checked_in_transaction"), False),
        ("long_transaction", ("transaction_policy", "short_transaction_required"), False),
        ("no_final_constraint", ("transaction_policy", "final_database_invariant_check_required"), False),
        ("reordered_locks", ("transaction_policy", "canonical_lock_order"), ["appointment", "schedule_conflict_domain", "practice", "idempotency_record"]),
        ("create_claims_row", ("operation_families", 0, "target_row_exists_before_command"), True),
        ("create_uses_row_lock", ("operation_families", 0, "required_serialization"), "appointment_lock"),
        ("update_has_no_row", ("operation_families", 1, "target_row_exists_before_command"), False),
        ("loser_mutates", ("outcomes", 2, "mutation"), True),
        ("commit_no_mutation", ("outcomes", 0, "mutation"), False),
        ("replay_loses_receipt", ("outcomes", 1, "returns_original_receipt"), False),
        ("architecture_changes_routes", ("legacy_compatibility_migration", "current_behavior_changed_by_this_contract"), True),
        ("freshness_becomes_confirmation", ("legacy_compatibility_migration", "implicit_freshness_is_human_confirmation"), True),
        ("durable_cue_commands", ("deferred_durable_event_and_cue_delivery", "command_authority"), True),
        ("durable_cue_truth", ("deferred_durable_event_and_cue_delivery", "current_truth_authority"), True),
        ("discard_cf_d1", ("deferred_durable_event_and_cue_delivery", "cf_d1_evidence_retained"), False),
        ("retry_old_cf_d2", ("deferred_durable_event_and_cue_delivery", "cf_d2_reopen_policy"), "retry_old_authority"),
        ("two_logical_watchers", ("deferred_durable_event_and_cue_delivery", "consumer_topology", "logical_consumers_per_partition"), 2),
        ("equal_checkpoint_writers", ("deferred_durable_event_and_cue_delivery", "consumer_topology", "equal_checkpoint_writers_per_partition"), True),
        ("next_opens_runtime", ("next_descendant", "runtime"), True),
        ("next_opens_database", ("next_descendant", "database"), True),
    ]
    mutations: list[tuple[str, dict[str, Any]]] = []
    for name, path, value in paths_and_values:
        mutated = copy.deepcopy(contract)
        cursor: Any = mutated
        for component in path[:-1]:
            cursor = cursor[component]
        cursor[path[-1]] = value
        mutations.append((name, mutated))
    return mutations


def build_report() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    canonical_errors = validate_contract(contract, schema)
    admitted_mutations = [
        name
        for name, mutation in hostile_mutations(contract)
        if not validate_contract(mutation, schema)
    ]
    return {
        "status": "passed" if not canonical_errors and not admitted_mutations else "failed",
        "canonical_errors": canonical_errors,
        "hostile_mutation_count": len(hostile_mutations(contract)),
        "admitted_mutations": admitted_mutations,
        "runtime_started": False,
        "database_opened": False,
        "provider_calls": 0,
        "product_or_patient_data": False,
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

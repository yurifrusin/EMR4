"""Generate and validate the closed durability state-machine rehearsal packet."""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal import (
    EFFECT_CEILINGS,
    EVIDENCE_LABEL,
    FAULT_MEMBERS,
    FRAME_TYPES,
    RESULT,
    SCHEMA_VERSION,
    GenerationCensus,
    KeyInterval,
    KeyScheduleTransition,
    RetainedRow,
    RetentionAnchor,
    apply_key_rotation,
    authoritative_retention_anchor,
    build_initial_state,
    candidate_for,
    digest_value,
    key_for_position,
    recovery_anchor,
    restart,
    retention_eligibility,
    seal_census,
    seal_state,
    synthetic_digest,
    transition,
    verify_state,
)


OUT_DIR = ROOT / "orchestration" / "continuity" / (
    "raisa-provider-free-unmounted-authored-synthetic-"
    "durability-state-machine-rehearsal"
)
CONTRACT_PATH = OUT_DIR / "durability-state-machine-contract.json"
SCHEMA_PATH = OUT_DIR / "durability-state-machine-contract.schema.json"
EVIDENCE_PATH = OUT_DIR / "provider-free-unmounted-authored-synthetic-evidence.json"

CASE_SPECS = (
    ("relevant_selective_retirement", "ADVANCE_AFTER_ATOMIC_COMMIT", ("SELECTIVE_WATERMARK", "IRREVERSIBLE_RETIREMENT", "ONE_OBLIGATION")),
    ("exact_redelivery", "EXACT_REDELIVERY", ("CONSTANT_TIME_DIGEST", "IDENTICAL_STATE", "EXISTING_RECEIPT")),
    ("irrelevant_contiguous", "ADVANCE_AFTER_RECEIPT_AND_AUDIT", ("NO_INVALIDATION", "RECEIPT_RECORDED", "AUDIT_RECORDED")),
    ("coalesced_later_cause", "ADVANCE_AFTER_ATOMIC_COMMIT", ("ONE_OBLIGATION", "ROLLING_DIGEST", "TWO_TO_FOUR")),
    ("contiguous_full_invalidation", "ADVANCE_AFTER_ATOMIC_COMMIT", ("BOTH_WATERMARKS", "ALL_FRAMES_RETIRED", "CHECKPOINT_ADVANCED")),
    ("coverage_gap", "REBASE_REQUIRED", ("CHECKPOINT_HELD", "FULL_INVALIDATION", "NO_SKIPPED_POSITION")),
    ("same_position_mismatch", "REBASE_REQUIRED", ("CHECKPOINT_HELD", "IDENTITY_CORRUPTION", "FULL_INVALIDATION")),
    ("digest_reuse", "REBASE_REQUIRED", ("CHECKPOINT_HELD", "DIGEST_REUSE_CORRUPTION", "FULL_INVALIDATION")),
    ("rollback_receipt", "ROLLED_BACK", ("ORIGINAL_STATE", "ZERO_RESIDUE", "FAULT_RECEIPT")),
    ("rollback_watermark", "ROLLED_BACK", ("ORIGINAL_STATE", "ZERO_RESIDUE", "FAULT_WATERMARK")),
    ("rollback_obligation", "ROLLED_BACK", ("ORIGINAL_STATE", "ZERO_RESIDUE", "FAULT_OBLIGATION")),
    ("rollback_audit", "ROLLED_BACK", ("ORIGINAL_STATE", "ZERO_RESIDUE", "FAULT_AUDIT")),
    ("rollback_checkpoint", "ROLLED_BACK", ("ORIGINAL_STATE", "ZERO_RESIDUE", "FAULT_CHECKPOINT")),
    ("restart_resume", "RESUME", ("INTEGRITY_VALID", "ANCHOR_EXACT", "NEXT_ROW_EXACT")),
    ("restart_gap", "REBASE_REQUIRED", ("ANCHOR_EXACT", "CHECKPOINT_HELD", "FULL_INVALIDATION")),
    ("restart_corrupt_state", "NEW_GENERATION_REQUIRED", ("NO_SUCCESSOR_STATE", "NO_CANDIDATE_COORDINATE", "INTEGRITY_FAILED")),
    ("key_boundary_before", "key:alpha", ("SOLE_KEY", "LAST_PRE_ROTATION_POSITION")),
    ("key_boundary_successor", "key:beta", ("SOLE_KEY", "FIRST_SUCCESSOR_POSITION")),
    ("key_rotation_commit", "ROTATION_COMMITTED", ("ATOMIC_ROTATION", "FUTURE_FENCE", "PREDECESSOR_OVERLAP")),
    ("key_rotation_retroactive", "REBASE_REQUIRED", ("RETROACTIVE_REJECTED", "FULL_INVALIDATION")),
    ("key_rotation_underlap", "REBASE_REQUIRED", ("UNDERLAP_REJECTED", "FULL_INVALIDATION")),
    ("key_rotation_missing_predecessor", "REBASE_REQUIRED", ("MISSING_KEY_REJECTED", "NO_TRY_ALL_KEYS")),
    ("key_schedule_gap", "REBASE_REQUIRED", ("GAP_REJECTED", "FULL_INVALIDATION")),
    ("key_schedule_history_change", "REBASE_REQUIRED", ("HISTORY_CHANGE_REJECTED", "FULL_INVALIDATION")),
    ("retention_eligible", "ELIGIBLE", ("COMPLETE_CENSUS", "MINIMUM_CHECKPOINT", "INERT_DECISION")),
    ("retention_minimum_checkpoint", "DENIED", ("SLOWEST_GENERATION_CONTROLS", "INERT_DECISION")),
    ("retention_omitted_generation", "DENIED", ("CENSUS_DIGEST_MISMATCH", "OMISSION_REJECTED", "SELF_ECHO_ANCHOR_REJECTED")),
    ("retention_duplicate_generation", "DENIED", ("CENSUS_INTEGRITY_FAILED", "DUPLICATE_REJECTED")),
    ("retention_recovery_pin", "DENIED", ("RECOVERY_PIN", "INERT_DECISION")),
    ("retention_audit_pin", "DENIED", ("AUDIT_PIN", "INERT_DECISION")),
    ("retention_key_overlap", "DENIED", ("KEY_OVERLAP_OPEN", "INERT_DECISION")),
    ("retention_safety_grace", "DENIED", ("SAFETY_GRACE_PENDING", "INERT_DECISION")),
    ("effect_ceilings", "ALL_FALSE", ("NO_LIVE_EFFECT", "NO_AUTHORITY_EXPANSION")),
)


def build_contract() -> dict[str, Any]:
    return {
        "schema_version": "emr4.context-fabric.durability-state-machine-contract.v1",
        "status": "provider_free_unmounted_authored_synthetic_rehearsal_only",
        "evidence_label": EVIDENCE_LABEL,
        "result": RESULT,
        "parent_result": "raisa_provider_free_unmounted_source_specific_durability_architecture_pass",
        "source_profile": {
            "source_system": "emr4-diary",
            "event_type": "diary.appointment_rescheduled",
            "event_schema_version": "diary.appointment_rescheduled.v1",
            "aggregate_class": "APPOINTMENT",
            "stream_id": "emr4:diary:appointment-rescheduled:v1",
            "stream_epoch": 1,
        },
        "frame_types": list(FRAME_TYPES),
        "atomic_members": list(FAULT_MEMBERS),
        "count_buckets": ["ONE", "TWO_TO_FOUR", "FIVE_PLUS"],
        "restart_dispositions": ["RESUME", "REBASE_REQUIRED", "NEW_GENERATION_REQUIRED"],
        "key_rotation": {
            "atomic": True,
            "strictly_future_position_fenced": True,
            "historical_positions_preserved": True,
            "predecessor_available_through_dependency_and_safety_overlap": True,
            "try_all_keys": False,
            "key_material_present": False,
        },
        "retention": {
            "complete_state_census_required": True,
            "separately_typed_backend_anchor_required": True,
            "independent_census_and_registry_digest_required": True,
            "minimum_non_consumed_checkpoint_controls": True,
            "omission_or_duplication_denied": True,
            "candidate_self_echo_anchor_accepted": False,
            "wall_clock_or_event_ttl_used": False,
            "deletion_effect": False,
        },
        "scenario_ids": [item[0] for item in CASE_SPECS],
        "effect_ceilings": EFFECT_CEILINGS,
        "later_live_gates": [
            "postgresql_schema_and_migration",
            "transaction_isolation_and_locking",
            "rls_roles_and_credentials",
            "database_backed_crash_recovery",
            "operational_retention_and_monitoring",
            "live_source_mounting",
            "product_data_privacy_assessment",
            "runtime_deployment_and_production",
        ],
    }


def _case(
    case_id: str,
    disposition: str,
    passed: bool,
    state_digest: str,
    mutation_committed: bool,
) -> dict[str, Any]:
    spec = next(item for item in CASE_SPECS if item[0] == case_id)
    if disposition != spec[1]:
        passed = False
    return {
        "case_id": case_id,
        "disposition": disposition,
        "passed": passed,
        "state_digest": state_digest,
        "mutation_committed": mutation_committed,
        "proof_codes": list(spec[2]),
    }


def build_evidence(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or build_contract()
    cases: list[dict[str, Any]] = []
    initial = build_initial_state()

    relevant = transition(initial, candidate_for(initial, position=5))
    cases.append(_case("relevant_selective_retirement", relevant.disposition, relevant.state.frames[0].lifecycle == "RETIRED" and relevant.state.frames[1].lifecycle == "CURRENT", relevant.state.integrity_digest, relevant.mutation_committed))

    replay = transition(relevant.state, candidate_for(relevant.state, position=5))
    cases.append(_case("exact_redelivery", replay.disposition, replay.state is relevant.state and replay.receipt == relevant.receipt, replay.state.integrity_digest, replay.mutation_committed))

    irrelevant_candidate = candidate_for(initial, position=5, decision="CONTIGUOUS_NO_INTERSECTION", affected_frame_types=())
    irrelevant = transition(initial, irrelevant_candidate)
    cases.append(_case("irrelevant_contiguous", irrelevant.disposition, irrelevant.state.frames == initial.frames and len(irrelevant.state.audits) == 1, irrelevant.state.integrity_digest, irrelevant.mutation_committed))

    coalesced = transition(relevant.state, candidate_for(relevant.state, position=6))
    cases.append(_case("coalesced_later_cause", coalesced.disposition, len(coalesced.state.obligations) == 1 and coalesced.state.obligations[0].count_bucket == "TWO_TO_FOUR", coalesced.state.integrity_digest, coalesced.mutation_committed))

    full = transition(initial, candidate_for(initial, position=5, decision="CONTIGUOUS_FULL_INVALIDATION", affected_frame_types=FRAME_TYPES))
    cases.append(_case("contiguous_full_invalidation", full.disposition, all(frame.lifecycle == "RETIRED" for frame in full.state.frames), full.state.integrity_digest, full.mutation_committed))

    gap = transition(initial, replace(candidate_for(initial, position=7), predecessor_position=4))
    cases.append(_case("coverage_gap", gap.disposition, gap.state.last_classified_position == 4, gap.state.integrity_digest, gap.mutation_committed))
    mismatch = transition(initial, replace(candidate_for(initial, position=4), observation_digest=synthetic_digest("mismatch")))
    cases.append(_case("same_position_mismatch", mismatch.disposition, mismatch.state.last_classified_position == 4, mismatch.state.integrity_digest, mismatch.mutation_committed))
    reuse = transition(initial, replace(candidate_for(initial, position=5), observation_digest=initial.receipts[0].observation_digest))
    cases.append(_case("digest_reuse", reuse.disposition, reuse.state.last_classified_position == 4, reuse.state.integrity_digest, reuse.mutation_committed))

    rollback_ids = ("rollback_receipt", "rollback_watermark", "rollback_obligation", "rollback_audit", "rollback_checkpoint")
    for case_id, fault in zip(rollback_ids, FAULT_MEMBERS, strict=True):
        rolled = transition(initial, candidate_for(initial, position=5), fail_before=fault)
        cases.append(_case(case_id, rolled.disposition, rolled.state is initial and rolled.receipt is None, rolled.state.integrity_digest, rolled.mutation_committed))

    anchor = recovery_anchor(relevant.state)
    row = RetainedRow(True, 6, 5, synthetic_digest("observation:6"), "key:alpha")
    resumed = restart(relevant.state, anchor, row)
    cases.append(_case("restart_resume", resumed.disposition, resumed.state is relevant.state, relevant.state.integrity_digest, False))
    restarted_gap = restart(relevant.state, anchor, replace(row, position=7))
    cases.append(_case("restart_gap", restarted_gap.disposition, restarted_gap.state is not None and restarted_gap.state.last_classified_position == 5, restarted_gap.state.integrity_digest if restarted_gap.state else synthetic_digest("none"), True))
    corrupt = replace(relevant.state, last_classified_position=999, integrity_digest=synthetic_digest("forged"))
    corrupt_result = restart(corrupt, anchor, None)
    cases.append(_case("restart_corrupt_state", corrupt_result.disposition, corrupt_result.state is None, synthetic_digest("no-successor-state"), False))

    successor = (KeyInterval("key:alpha", 0, 7), KeyInterval("key:beta", 7, None))
    cases.append(_case("key_boundary_before", key_for_position(successor, 6) or "NONE", key_for_position(successor, 6) == "key:alpha", digest_value([asdict(item) for item in successor]), False))
    cases.append(_case("key_boundary_successor", key_for_position(successor, 7) or "NONE", key_for_position(successor, 7) == "key:beta", digest_value([asdict(item) for item in successor]), False))
    rotation = KeyScheduleTransition(digest_value([asdict(item) for item in initial.key_schedule]), successor, 7, "key:alpha", "key:beta", 6, 9, 2)
    rotated = apply_key_rotation(initial, rotation)
    cases.append(_case("key_rotation_commit", rotated.disposition, rotated.state.key_schedule == successor, rotated.state.integrity_digest, True))
    invalid_rotations = (
        ("key_rotation_retroactive", replace(rotation, activation_position=4)),
        ("key_rotation_underlap", replace(rotation, predecessor_key_available_through_position=7)),
        ("key_rotation_missing_predecessor", replace(rotation, predecessor_key_id="key:missing")),
        ("key_schedule_gap", replace(rotation, successor_schedule=(KeyInterval("key:alpha", 0, 6), KeyInterval("key:beta", 7, None)))),
        ("key_schedule_history_change", replace(rotation, successor_schedule=(KeyInterval("key:changed", 0, 7), KeyInterval("key:beta", 7, None)))),
    )
    for case_id, invalid_rotation in invalid_rotations:
        failed = apply_key_rotation(initial, invalid_rotation)
        cases.append(_case(case_id, failed.disposition, failed.state.checkpoint_state == "REBASE_REQUIRED", failed.state.integrity_digest, True))

    retention_args = {
        "source_row_position": 0,
        "anchor": authoritative_retention_anchor(),
        "recovery_pin": False,
        "audit_pin": False,
        "key_overlap_closed": True,
        "safety_grace_elapsed": True,
    }
    eligible = retention_eligibility(initial, **retention_args)
    cases.append(_case("retention_eligible", eligible.disposition, eligible.deletion_executed is False, initial.integrity_digest, False))
    behind = retention_eligibility(initial, **(retention_args | {"source_row_position": 1}))
    cases.append(_case("retention_minimum_checkpoint", behind.disposition, "MINIMUM_CHECKPOINT_BEHIND_ROW" in behind.reasons, initial.integrity_digest, False))

    omitted = seal_census(replace(initial.generation_census, members=initial.generation_census.members[1:], census_digest=""))
    omitted_state = seal_state(replace(initial, generation_census=omitted, integrity_digest=""))
    omitted_result = retention_eligibility(omitted_state, **retention_args)
    echoed_anchor = RetentionAnchor(
        "BACKEND_AUTHORED_RETENTION_CENSUS_ANCHOR",
        omitted.registry_digest,
        omitted.census_digest,
        (2,),
    )
    echoed_result = retention_eligibility(
        omitted_state,
        **(retention_args | {"anchor": echoed_anchor}),
    )
    cases.append(_case("retention_omitted_generation", omitted_result.disposition, "COMPLETE_CENSUS_DIGEST_MISMATCH" in omitted_result.reasons and "RETENTION_ANCHOR_INVALID" in echoed_result.reasons and echoed_result.disposition == "DENIED", omitted_state.integrity_digest, False))
    duplicate = seal_census(GenerationCensus(initial.registry_digest, (initial.generation_census.members[0],) * 2, ""))
    duplicate_state = seal_state(replace(initial, generation_census=duplicate, integrity_digest=""))
    duplicate_result = retention_eligibility(duplicate_state, **retention_args)
    cases.append(_case("retention_duplicate_generation", duplicate_result.disposition, "STATE_OR_CENSUS_INTEGRITY_INVALID" in duplicate_result.reasons, duplicate_state.integrity_digest, False))
    for case_id, change, proof_reason in (
        ("retention_recovery_pin", {"recovery_pin": True}, "RECOVERY_PIN_PRESENT"),
        ("retention_audit_pin", {"audit_pin": True}, "AUDIT_PIN_PRESENT"),
        ("retention_key_overlap", {"key_overlap_closed": False}, "KEY_OVERLAP_OPEN"),
        ("retention_safety_grace", {"safety_grace_elapsed": False}, "SAFETY_GRACE_PENDING"),
    ):
        denied = retention_eligibility(initial, **(retention_args | change))
        cases.append(_case(case_id, denied.disposition, proof_reason in denied.reasons, initial.integrity_digest, False))

    effects_pass = bool(EFFECT_CEILINGS) and all(value is False for value in EFFECT_CEILINGS.values())
    cases.append(_case("effect_ceilings", "ALL_FALSE", effects_pass, digest_value(EFFECT_CEILINGS), False))
    if [case["case_id"] for case in cases] != [spec[0] for spec in CASE_SPECS]:
        raise ValueError("scenario_order_mismatch")
    if not all(case["passed"] for case in cases):
        raise ValueError("scenario_failure")
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "result": RESULT,
        "data_class": "newly_authored_synthetic_opaque_control_metadata",
        "contract_digest": digest_value(contract),
        "case_count": len(cases),
        "passed_case_count": sum(bool(case["passed"]) for case in cases),
        "cases": cases,
        "effect_ceilings": EFFECT_CEILINGS,
        "claim_boundary": {
            "pure_in_memory_state_transitions_only": True,
            "database_or_migration_proved": False,
            "source_delivery_or_crash_recovery_proved": False,
            "patient_privacy_or_product_read_proved": False,
            "provider_command_runtime_or_production_proved": False,
        },
    }


def _const_schema(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            "type": "object",
            "additionalProperties": False,
            "required": list(value),
            "properties": {key: _const_schema(item) for key, item in value.items()},
        }
    if isinstance(value, list):
        return {
            "type": "array",
            "minItems": len(value),
            "maxItems": len(value),
            "prefixItems": [_const_schema(item) for item in value],
            "items": False,
        }
    return {"const": value}


def build_schema(contract: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://emr4.local/schemas/durability-state-machine-contract.schema.json",
        "title": "Closed durability state-machine rehearsal contract and evidence",
        "oneOf": [_const_schema(contract), _const_schema(evidence)],
    }


def generate() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = build_contract()
    evidence = build_evidence(contract)
    schema = build_schema(contract, evidence)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    if list(validator.iter_errors(contract)) or list(validator.iter_errors(evidence)):
        raise ValueError("closed_schema_validation_failed")
    if not verify_state(build_initial_state()):
        raise ValueError("initial_state_integrity_failed")
    return contract, schema, evidence


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    contract, schema, evidence = generate()
    write_json(args.output_dir / CONTRACT_PATH.name, contract)
    write_json(args.output_dir / SCHEMA_PATH.name, schema)
    write_json(args.output_dir / EVIDENCE_PATH.name, evidence)
    print(json.dumps({"status": "passed", "case_count": evidence["case_count"], "result": evidence["result"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

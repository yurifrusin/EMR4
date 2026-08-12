"""Pure authored-synthetic status transaction-kernel protocol rehearsal."""

from __future__ import annotations

import argparse
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
    / "raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal"
)
PACKET_PATH = PACKET_DIR / "protocol-packet.json"
SCHEMA_PATH = PACKET_DIR / "protocol-packet.schema.json"
EVIDENCE_PATH = PACKET_DIR / "protocol-evidence.json"

GLOBAL_LOCK_ORDER = ["practice", "schedule_domain", "appointment", "idempotency_record"]
LOCK_ORDER = ["practice", "appointment", "idempotency_record"]
OUTCOMES = [
    "committed",
    "idempotent_replay",
    "stale_precondition",
    "schedule_conflict",
    "authority_revoked",
    "confirmation_required",
    "validation_rejected",
    "idempotency_conflict",
]
SOURCE_BINDINGS = [
    {
        "path": "orchestration/continuity/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface/contract.json",
        "sha256": "abe1e35032ca5a979ac187b45adffc498897e341d185b65c8e0eb6b094cfb582",
    },
    {
        "path": "docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-design.md",
        "sha256": "ed84a15d101b3bc6cb616b6955d4054dc42d8e9827118f319ba9e4d72ebbea53",
    },
    {
        "path": "docs/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review.md",
        "sha256": "6863c1a7fef074d66d3c1870014f51b30e2dc8953e92e19642a2b86a4461218c",
    },
    {
        "path": "docs/raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair-closeout.md",
        "sha256": "d1b202abfe234d91a002e1b75f3880eb74eef14a47a1dbf19d267c1c09a7d907",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _decision(
    scenario_id: str,
    *,
    structure: str = "valid",
    binding: str = "exact",
    lock_plan: list[str] | None = None,
    authority: bool = True,
    confirmation: str = "valid",
    idempotency: str = "absent",
    source: str = "current",
    target: str = "exists",
    transition: str = "valid",
) -> dict[str, Any]:
    scenario = {
        "id": scenario_id,
        "structure": structure,
        "binding": binding,
        "lock_plan": lock_plan if lock_plan is not None else list(LOCK_ORDER),
        "current_authority": authority,
        "confirmation": confirmation,
        "idempotency": idempotency,
        "source": source,
        "target": target,
        "transition": transition,
    }
    scenario["expected"] = evaluate_decision(scenario)
    return scenario


def evaluate_decision(scenario: dict[str, Any]) -> dict[str, Any]:
    if scenario["structure"] != "valid":
        return _rejected("structure_invalid")
    if scenario["binding"] != "exact":
        return _rejected("binding_mismatch")
    if scenario["lock_plan"] != LOCK_ORDER:
        return _rejected("lock_plan_invalid")

    if not scenario["current_authority"]:
        return _loser("authority_revoked", "current_authority_revoked")
    if scenario["confirmation"] != "valid":
        reason = (
            "warning_acknowledgement_missing"
            if scenario["confirmation"] == "warning_unacknowledged"
            else "separate_confirmation_invalid"
        )
        return _loser("confirmation_required", reason)
    if scenario["idempotency"] == "same_digest_completed":
        return {
            "admission": "admitted",
            "outcome": "idempotent_replay",
            "reason": "same_digest_completed",
            "receipt_disclosed": True,
            "planned_effect": False,
        }
    if scenario["idempotency"] == "different_digest":
        return _loser("idempotency_conflict", "same_key_different_digest")
    if scenario["source"] != "current":
        return _loser("stale_precondition", "appointment_version_changed")
    if scenario["target"] != "exists":
        return _loser("validation_rejected", "target_not_found")
    if scenario["transition"] == "policy_deferred":
        return _loser("validation_rejected", "transition_policy_deferred")
    if scenario["transition"] != "valid":
        return _loser("validation_rejected", "transition_domain_invalid")
    return {
        "admission": "admitted",
        "outcome": "committed",
        "reason": "first_effect_planned",
        "receipt_disclosed": False,
        "planned_effect": True,
    }


def _rejected(reason: str) -> dict[str, Any]:
    return {
        "admission": "admission_rejected",
        "outcome": None,
        "reason": reason,
        "receipt_disclosed": False,
        "planned_effect": False,
    }


def _loser(outcome: str, reason: str) -> dict[str, Any]:
    return {
        "admission": "admitted",
        "outcome": outcome,
        "reason": reason,
        "receipt_disclosed": False,
        "planned_effect": False,
    }


def _base_state() -> dict[str, Any]:
    return {
        "appointment_status": "Booked",
        "appointment_version": 7,
        "mutation_count": 0,
        "audit_count": 0,
        "completed_receipt_count": 0,
        "receipt_id": None,
    }


def _committed_state() -> dict[str, Any]:
    return {
        "appointment_status": "Arrived",
        "appointment_version": 8,
        "mutation_count": 1,
        "audit_count": 1,
        "completed_receipt_count": 1,
        "receipt_id": "syn-receipt-status-001",
    }


def simulate_schedule(schedule: dict[str, Any]) -> dict[str, Any]:
    kind = schedule["kind"]
    injection = schedule["injection"]
    trace = list(schedule["trace"])
    response_delivered = True

    if kind == "single_first_effect":
        if injection in {
            "before_locks",
            "after_staged_mutation",
            "after_staged_audit",
            "after_staged_receipt",
        }:
            return {
                "durable_state": _base_state(),
                "participant_results": ["transaction_rolled_back"],
                "response_delivered": False,
                "trace": trace,
            }
        response_delivered = injection != "after_commit_before_response"
        return {
            "durable_state": _committed_state(),
            "participant_results": ["committed"],
            "response_delivered": response_delivered,
            "trace": trace,
        }

    if kind == "retry_after_lost_response":
        return {
            "durable_state": _committed_state(),
            "participant_results": ["committed", "idempotent_replay"],
            "response_delivered": True,
            "trace": trace,
        }
    if kind == "concurrent_same_digest":
        results = ["committed", "idempotent_replay"]
    elif kind == "concurrent_different_digest":
        results = ["committed", "idempotency_conflict"]
    elif kind == "concurrent_stale_source":
        results = ["committed", "stale_precondition"]
    elif kind == "concurrent_authority_loss":
        results = ["committed", "authority_revoked"]
    else:
        raise ValueError(f"unknown schedule kind: {kind}")
    return {
        "durable_state": _committed_state(),
        "participant_results": results,
        "response_delivered": True,
        "trace": trace,
    }


def _schedule(
    schedule_id: str,
    kind: str,
    injection: str,
    participant_count: int,
) -> dict[str, Any]:
    trace = [
        "lock:practice",
        "lock:appointment",
        "lock:idempotency_record",
        "recheck:current_authority",
        "inspect:idempotency",
        "recheck:appointment_version",
        "stage:appointment_mutation",
        "stage:mutation_audit",
        "stage:completed_receipt",
        "commit:atomic",
        "serialize:response",
    ]
    schedule = {
        "id": schedule_id,
        "kind": kind,
        "injection": injection,
        "participant_count": participant_count,
        "lock_plan": list(LOCK_ORDER),
        "trace": trace,
    }
    schedule["expected"] = simulate_schedule(schedule)
    return schedule


def build_packet() -> dict[str, Any]:
    decisions = [
        _decision("stk-001-commit"),
        _decision("stk-002-replay", idempotency="same_digest_completed"),
        _decision("stk-003-conflict", idempotency="different_digest"),
        _decision(
            "stk-004-authority-before-replay",
            authority=False,
            idempotency="same_digest_completed",
            source="stale",
        ),
        _decision(
            "stk-005-confirmation-before-replay",
            confirmation="missing",
            idempotency="same_digest_completed",
        ),
        _decision("stk-006-stale", source="stale"),
        _decision("stk-007-target-missing", target="missing"),
        _decision("stk-008-domain-invalid", transition="invalid"),
        _decision("stk-009-terminal-policy-deferred", transition="policy_deferred"),
        _decision("stk-010-structure-rejected", structure="invalid"),
        _decision("stk-011-binding-rejected", binding="mismatch"),
        _decision(
            "stk-012-reordered-locks",
            lock_plan=["practice", "idempotency_record", "appointment"],
        ),
        _decision(
            "stk-013-extra-schedule-lock",
            lock_plan=[
                "practice",
                "schedule_domain",
                "appointment",
                "idempotency_record",
            ],
        ),
        _decision(
            "stk-014-warning-unacknowledged",
            confirmation="warning_unacknowledged",
        ),
        _decision(
            "stk-015-authority-before-conflict",
            authority=False,
            idempotency="different_digest",
        ),
    ]
    schedules = [
        _schedule("sts-001-clean-commit", "single_first_effect", "none", 1),
        _schedule("sts-002-before-locks", "single_first_effect", "before_locks", 1),
        _schedule(
            "sts-003-after-mutation",
            "single_first_effect",
            "after_staged_mutation",
            1,
        ),
        _schedule("sts-004-after-audit", "single_first_effect", "after_staged_audit", 1),
        _schedule(
            "sts-005-after-receipt",
            "single_first_effect",
            "after_staged_receipt",
            1,
        ),
        _schedule(
            "sts-006-lost-response",
            "single_first_effect",
            "after_commit_before_response",
            1,
        ),
        _schedule("sts-007-retry", "retry_after_lost_response", "none", 2),
        _schedule("sts-008-same-digest", "concurrent_same_digest", "none", 2),
        _schedule("sts-009-different-digest", "concurrent_different_digest", "none", 2),
        _schedule("sts-010-stale-source", "concurrent_stale_source", "none", 2),
        _schedule("sts-011-authority-loss", "concurrent_authority_loss", "none", 2),
    ]
    return {
        "schema_version": "raisa.status_transaction_kernel_protocol.v1",
        "artifact_kind": "provider_free_unmounted_authored_synthetic_protocol",
        "source_bindings": copy.deepcopy(SOURCE_BINDINGS),
        "canonical_operation_id": "confirmAppointmentStatusProposal",
        "global_lock_order": list(GLOBAL_LOCK_ORDER),
        "status_lock_plan": list(LOCK_ORDER),
        "unused_lock_rule": "skip_schedule_domain_without_reordering",
        "outcome_vocabulary": list(OUTCOMES),
        "decision_scenarios": decisions,
        "transaction_schedules": schedules,
        "review_questions": [
            "terminal_status_retransition_warning_policy_deferred",
            "post_commit_response_serialization_contract_not_yet_runtime_proven",
            "ledger_first_runtime_helper_requires_future_lock_order_reconciliation",
        ],
        "effect_boundary": {
            "application_route_imported": False,
            "application_model_imported": False,
            "database_driver_imported": False,
            "database_or_source_opened": False,
            "watcher_or_event_consumed": False,
            "provider_or_network_used": False,
            "real_lock_acquired": False,
            "mutation_audit_or_receipt_written": False,
            "command_executed": False,
            "product_or_patient_data_used": False,
        },
    }


def build_schema() -> dict[str, Any]:
    string_array = {"type": "array", "items": {"type": "string"}}
    expected_decision = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "admission",
            "outcome",
            "reason",
            "receipt_disclosed",
            "planned_effect",
        ],
        "properties": {
            "admission": {"enum": ["admitted", "admission_rejected"]},
            "outcome": {"type": ["string", "null"]},
            "reason": {"type": "string"},
            "receipt_disclosed": {"type": "boolean"},
            "planned_effect": {"type": "boolean"},
        },
    }
    state_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "appointment_status",
            "appointment_version",
            "mutation_count",
            "audit_count",
            "completed_receipt_count",
            "receipt_id",
        ],
        "properties": {
            "appointment_status": {"type": "string"},
            "appointment_version": {"type": "integer"},
            "mutation_count": {"type": "integer"},
            "audit_count": {"type": "integer"},
            "completed_receipt_count": {"type": "integer"},
            "receipt_id": {"type": ["string", "null"]},
        },
    }
    expected_schedule = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "durable_state",
            "participant_results",
            "response_delivered",
            "trace",
        ],
        "properties": {
            "durable_state": state_schema,
            "participant_results": string_array,
            "response_delivered": {"type": "boolean"},
            "trace": string_array,
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "artifact_kind",
            "source_bindings",
            "canonical_operation_id",
            "global_lock_order",
            "status_lock_plan",
            "unused_lock_rule",
            "outcome_vocabulary",
            "decision_scenarios",
            "transaction_schedules",
            "review_questions",
            "effect_boundary",
        ],
        "properties": {
            "schema_version": {"const": "raisa.status_transaction_kernel_protocol.v1"},
            "artifact_kind": {
                "const": "provider_free_unmounted_authored_synthetic_protocol"
            },
            "source_bindings": {
                "type": "array",
                "minItems": 4,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["path", "sha256"],
                    "properties": {
                        "path": {"type": "string"},
                        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    },
                },
            },
            "canonical_operation_id": {"const": "confirmAppointmentStatusProposal"},
            "global_lock_order": string_array,
            "status_lock_plan": string_array,
            "unused_lock_rule": {"type": "string"},
            "outcome_vocabulary": string_array,
            "decision_scenarios": {
                "type": "array",
                "minItems": 15,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "structure",
                        "binding",
                        "lock_plan",
                        "current_authority",
                        "confirmation",
                        "idempotency",
                        "source",
                        "target",
                        "transition",
                        "expected",
                    ],
                    "properties": {
                        "id": {"type": "string", "pattern": "^stk-[0-9]{3}-"},
                        "structure": {"type": "string"},
                        "binding": {"type": "string"},
                        "lock_plan": string_array,
                        "current_authority": {"type": "boolean"},
                        "confirmation": {"type": "string"},
                        "idempotency": {"type": "string"},
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "transition": {"type": "string"},
                        "expected": expected_decision,
                    },
                },
            },
            "transaction_schedules": {
                "type": "array",
                "minItems": 11,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "kind",
                        "injection",
                        "participant_count",
                        "lock_plan",
                        "trace",
                        "expected",
                    ],
                    "properties": {
                        "id": {"type": "string", "pattern": "^sts-[0-9]{3}-"},
                        "kind": {"type": "string"},
                        "injection": {"type": "string"},
                        "participant_count": {"type": "integer", "minimum": 1},
                        "lock_plan": string_array,
                        "trace": string_array,
                        "expected": expected_schedule,
                    },
                },
            },
            "review_questions": {"type": "array", "minItems": 3, "maxItems": 3, "items": {"type": "string"}},
            "effect_boundary": {
                "type": "object",
                "additionalProperties": False,
                "minProperties": 10,
                "maxProperties": 10,
                "patternProperties": {"^[a-z_]+$": {"const": False}},
            },
        },
    }


def validate_packet(packet: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(packet)]
    if errors:
        return sorted(errors)
    if packet["source_bindings"] != SOURCE_BINDINGS:
        errors.append("source_binding_set_mismatch")
    for binding in packet["source_bindings"]:
        if _sha256(ROOT / binding["path"]) != binding["sha256"]:
            errors.append(f"source_hash_mismatch:{binding['path']}")
    if packet["global_lock_order"] != GLOBAL_LOCK_ORDER:
        errors.append("global_lock_order_mismatch")
    if packet["status_lock_plan"] != LOCK_ORDER:
        errors.append("status_lock_plan_mismatch")
    if packet["outcome_vocabulary"] != OUTCOMES:
        errors.append("outcome_vocabulary_mismatch")
    if any(packet["effect_boundary"].values()):
        errors.append("effect_boundary_open")

    decision_ids = [scenario["id"] for scenario in packet["decision_scenarios"]]
    if len(decision_ids) != len(set(decision_ids)):
        errors.append("decision_id_duplicate")
    for scenario in packet["decision_scenarios"]:
        if evaluate_decision(scenario) != scenario["expected"]:
            errors.append(f"decision_mismatch:{scenario['id']}")
        expected = scenario["expected"]
        if expected["admission"] == "admission_rejected" and expected["outcome"] is not None:
            errors.append(f"rejected_decision_has_outcome:{scenario['id']}")
        if expected["planned_effect"] != (expected["outcome"] == "committed"):
            errors.append(f"effect_not_commit_only:{scenario['id']}")
        if not scenario["current_authority"] and expected["receipt_disclosed"]:
            errors.append(f"revoked_authority_receipt_disclosed:{scenario['id']}")

    schedule_ids = [schedule["id"] for schedule in packet["transaction_schedules"]]
    if len(schedule_ids) != len(set(schedule_ids)):
        errors.append("schedule_id_duplicate")
    for schedule in packet["transaction_schedules"]:
        if schedule["lock_plan"] != LOCK_ORDER:
            errors.append(f"schedule_lock_plan_mismatch:{schedule['id']}")
        if simulate_schedule(schedule) != schedule["expected"]:
            errors.append(f"schedule_mismatch:{schedule['id']}")

    terminal = next(
        scenario
        for scenario in packet["decision_scenarios"]
        if scenario["id"] == "stk-009-terminal-policy-deferred"
    )
    if terminal["expected"]["reason"] != "transition_policy_deferred":
        errors.append("terminal_policy_not_deferred")
    return sorted(set(errors))


def hostile_mutations(packet: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutate(name: str, path: tuple[Any, ...], value: Any) -> None:
        candidate = copy.deepcopy(packet)
        cursor: Any = candidate
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = value
        mutations.append((name, candidate))

    mutate("operation", ("canonical_operation_id",), "rawStatusPatch")
    mutate("global_order", ("global_lock_order",), list(reversed(packet["global_lock_order"])))
    mutate("status_order", ("status_lock_plan",), ["practice", "idempotency_record", "appointment"])
    mutate("outcomes", ("outcome_vocabulary",), OUTCOMES[:-1])
    mutate("source_hash", ("source_bindings", 0, "sha256"), "0" * 64)
    mutate("source_path", ("source_bindings", 0, "path"), "app/routers/appointments.py")
    for key in packet["effect_boundary"]:
        mutate(f"effect_{key}", ("effect_boundary", key), True)
    mutate("commit_expected_replay", ("decision_scenarios", 0, "expected", "outcome"), "idempotent_replay")
    mutate("commit_no_effect", ("decision_scenarios", 0, "expected", "planned_effect"), False)
    mutate("replay_effect", ("decision_scenarios", 1, "expected", "planned_effect"), True)
    mutate("replay_hidden", ("decision_scenarios", 1, "expected", "receipt_disclosed"), False)
    mutate("authority_replay", ("decision_scenarios", 3, "expected", "outcome"), "idempotent_replay")
    mutate("authority_disclosure", ("decision_scenarios", 3, "expected", "receipt_disclosed"), True)
    mutate("confirmation_replay", ("decision_scenarios", 4, "expected", "outcome"), "idempotent_replay")
    mutate("stale_commit", ("decision_scenarios", 5, "expected", "outcome"), "committed")
    mutate("terminal_commit", ("decision_scenarios", 8, "expected", "outcome"), "committed")
    mutate("bad_lock_admitted", ("decision_scenarios", 11, "expected", "admission"), "admitted")
    mutate("extra_lock_admitted", ("decision_scenarios", 12, "expected", "admission"), "admitted")
    mutate("warning_commit", ("decision_scenarios", 13, "expected", "outcome"), "committed")
    mutate("rollback_mutation", ("transaction_schedules", 2, "expected", "durable_state", "mutation_count"), 1)
    mutate("rollback_audit", ("transaction_schedules", 3, "expected", "durable_state", "audit_count"), 1)
    mutate("rollback_receipt", ("transaction_schedules", 4, "expected", "durable_state", "completed_receipt_count"), 1)
    mutate("lost_response_rollback", ("transaction_schedules", 5, "expected", "durable_state", "mutation_count"), 0)
    mutate("retry_second_mutation", ("transaction_schedules", 6, "expected", "durable_state", "mutation_count"), 2)
    mutate("same_digest_second_audit", ("transaction_schedules", 7, "expected", "durable_state", "audit_count"), 2)
    mutate("different_digest_second_commit", ("transaction_schedules", 8, "expected", "participant_results", 1), "committed")
    mutate("stale_second_commit", ("transaction_schedules", 9, "expected", "participant_results", 1), "committed")
    mutate("revoked_second_replay", ("transaction_schedules", 10, "expected", "participant_results", 1), "idempotent_replay")
    return mutations


def build_report(packet: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    canonical_errors = validate_packet(packet, schema)
    admitted_mutations = [
        name
        for name, candidate in hostile_mutations(packet)
        if not validate_packet(candidate, schema)
    ]
    return {
        "schema_version": "raisa.status_transaction_kernel_protocol.evidence.v1",
        "status": "passed" if not canonical_errors and not admitted_mutations else "failed",
        "canonical_errors": canonical_errors,
        "decision_scenario_count": len(packet["decision_scenarios"]),
        "transaction_schedule_count": len(packet["transaction_schedules"]),
        "hostile_mutation_count": len(hostile_mutations(packet)),
        "admitted_hostile_mutations": admitted_mutations,
        "effect_boundary": packet["effect_boundary"],
        "runtime_or_command_authority_granted": False,
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    path.write_bytes((rendered + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    packet = build_packet()
    schema = build_schema()
    report = build_report(packet, schema)
    if args.write:
        _write(PACKET_PATH, packet)
        _write(SCHEMA_PATH, schema)
        _write(EVIDENCE_PATH, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

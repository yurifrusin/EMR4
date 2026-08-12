"""Validate the provider-free unmounted status-confirm convergence architecture."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "runtime-convergence-architecture"
)
CONTRACT_PATH = BASE / "convergence-architecture-contract.json"
SCHEMA_PATH = BASE / "convergence-architecture-contract.schema.json"
EVIDENCE_PATH = BASE / "provider-free-architecture-evidence.json"

EXPECTED_SOURCE_BINDINGS = {
    "docs/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review-closeout.md": "5f3ccdf0b95151ef2013530e23e317b3aafcfa3d177ebc119a8ffe9400875806",
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review/runtime-gap-review-contract.json": "e9aac014b2111a5c48563b1cf5386b734d9d95948d0157262d2db8d6cb71292a",
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review/runtime-gap-review-evidence.json": "54acf1b0b04e2387d64b778debedeb857204408dd4e7f4ea4922101b4ff260e1",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract/adapter-contract.json": "297e34fbd984baeb53892edf5bc67f3d4db15911fa83d0b59776b2d707bffc30",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract/adapter-contract.schema.json": "89140cc9f46dfb01cac2bcb9d0531be06b81d02b7d9ce0d779e8b456148f4144",
    "orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal/protocol-packet.json": "2967703f8baf395439a6e2c88885074fefe9f4bea308c0294ba7e67c57b26633",
    "orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal/protocol-packet.schema.json": "962a6fa2ee82226df2975a7f3c82d3f445498ef727b3d5addf4b891a380f840c",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
    "docs/api-spine/openapi/appointment-commands.yaml": "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6",
}

ARCHITECTURE_KEYS = [
    "route_discriminator",
    "server_authority_ingress",
    "transaction_boundary",
    "source_version",
    "signed_evidence",
    "warning_acknowledgement",
    "terminal_policy",
    "atomic_write_set",
    "stored_receipt_delivery",
]
EXPECTED_TRACE = [
    "discriminate:status_only",
    "ingress:server_authority",
    "lock:practice",
    "lock:appointment",
    "lock:idempotency_record",
    "recheck:current_authority",
    "inspect:idempotency",
    "recheck:appointment_state_version",
    "recompute:warning_codes",
    "verify:signed_confirmation",
    "check:terminal_policy",
    "stage:appointment_mutation",
    "stage:attributable_audit",
    "stage:completed_receipt",
    "commit:atomic",
    "render:stored_canonical_receipt",
]
EXPECTED_OUTCOMES = [
    "committed",
    "idempotent_replay",
    "stale_precondition",
    "authority_revoked",
    "confirmation_required",
    "validation_rejected",
    "idempotency_conflict",
    "transition_policy_deferred",
    "transaction_rolled_back",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_schema(contract: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)


def verify_source_bindings(contract: dict[str, Any]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise ValueError(f"missing source binding: {binding['path']}")
        digest = _sha256(path)
        if digest != binding["sha256"]:
            raise ValueError(f"source hash mismatch: {binding['path']}")
        observed[binding["path"]] = digest
    if len(observed) != 9:
        raise ValueError("exactly nine unique source bindings are required")
    return observed


def validate_contract_semantics(contract: dict[str, Any]) -> None:
    if contract["source_head"] != "fca97097eeca5070ad41e403aed9413eee45ccba":
        raise ValueError("source head changed")
    if contract["implementation_authorized"] is not False:
        raise ValueError("implementation authority must remain false")
    source_bindings = {
        item["path"]: item["sha256"] for item in contract["source_bindings"]
    }
    if source_bindings != EXPECTED_SOURCE_BINDINGS:
        raise ValueError("exact source binding set changed")
    if set(contract["forbidden"].values()) != {False}:
        raise ValueError("every forbidden effect must remain false")
    if contract["next_candidate"] != (
        "provider_free_unmounted_status_confirm_runtime_convergence_rehearsal"
    ):
        raise ValueError("next candidate must remain unmounted")

    architecture = contract["architecture"]
    route = architecture["route_discriminator"]
    if route != {
        "accepted_intent": "update_appointment_status",
        "rejected_intents": ["update_appointment_waiting_area"],
        "discriminate_before_kernel_ingress": True,
        "waiting_area_behavior_unchanged": True,
    }:
        raise ValueError("status-only route discriminator changed")

    ingress = architecture["server_authority_ingress"]
    if ingress != {
        "server_owned_fields": [
            "practice_id",
            "actor_id",
            "actor_role",
            "active_user",
            "session_binding_digest",
        ],
        "transport_authority_accepted": False,
        "opaque_session_binding": True,
        "recheck_after_locks": True,
    }:
        raise ValueError("server authority ingress changed")

    transaction = architecture["transaction_boundary"]
    if transaction != {
        "owner": "backend_status_confirm_kernel",
        "lock_order": ["practice", "appointment", "idempotency_record"],
        "unused_schedule_domain_rule": "skip_without_reordering",
        "idempotency_disclosure_after_authority_recheck": True,
        "single_transaction": True,
    }:
        raise ValueError("transaction boundary changed")

    source_version = architecture["source_version"]
    if source_version != {
        "name": "appointment_state_version",
        "type": "positive_monotonic_integer",
        "read_under_appointment_lock": True,
        "increment_on_committed_appointment_state_change": True,
        "physical_storage_deferred": True,
    }:
        raise ValueError("source version contract changed")

    evidence = architecture["signed_evidence"]
    if evidence != {
        "required_bindings": [
            "practice_id",
            "target_appointment_id",
            "actor_id",
            "session_binding_digest",
            "command",
            "appointment_state_version",
            "warning_codes",
            "freshness_id",
        ],
        "verified_after_locked_recomputation": True,
        "confirmation_distinct_from_freshness": True,
    }:
        raise ValueError("signed evidence contract changed")

    warnings = architecture["warning_acknowledgement"]
    if warnings != {
        "comparison": "exact_canonical_unique_set_equality",
        "reject_missing": True,
        "reject_extra": True,
        "reject_duplicate": True,
        "reject_unknown": True,
    }:
        raise ValueError("warning acknowledgement changed")

    terminal = architecture["terminal_policy"]
    if terminal != {
        "terminal_statuses": ["Completed", "Cancelled", "DidNotAttend"],
        "different_target_outcome": "transition_policy_deferred",
        "effect_allowed": False,
        "product_policy_invented": False,
    }:
        raise ValueError("terminal policy changed")

    write_set = architecture["atomic_write_set"]
    if write_set != {
        "members": [
            "appointment_mutation",
            "attributable_audit",
            "completed_receipt",
        ],
        "completed_receipt_private_bindings": [
            "operation_id",
            "practice_id",
            "target_appointment_id",
            "actor_id",
            "session_binding_digest",
            "idempotency_key",
            "request_digest",
            "audit_log_id",
            "pre_state_version",
            "post_state_version",
            "response_digest",
        ],
        "all_commit_or_rollback": True,
        "effect_outcome": "committed",
    }:
        raise ValueError("atomic write-set contract changed")

    delivery = architecture["stored_receipt_delivery"]
    if delivery != {
        "canonical_public_response_fields": [
            "appointment_id",
            "status",
            "status_reason_code",
            "waiting_area_id",
            "warning_codes",
        ],
        "initial_response_source": "stored_canonical_receipt",
        "replay_response_source": "stored_canonical_receipt",
        "post_commit_failure_state": "delivery_unknown",
        "server_effect_retry": False,
        "client_retry_requirement": "same_idempotency_key_and_request_digest",
    }:
        raise ValueError("stored receipt delivery changed")

    if architecture["decision_trace"] != EXPECTED_TRACE:
        raise ValueError("decision trace changed")
    if architecture["outcome_vocabulary"] != EXPECTED_OUTCOMES:
        raise ValueError("outcome vocabulary changed")

    scenario_ids = [scenario["id"] for scenario in contract["scenarios"]]
    if len(scenario_ids) != 20 or len(set(scenario_ids)) != 20:
        raise ValueError("exactly twenty unique scenarios are required")


def _result(
    *,
    outcome: str,
    reason: str,
    effect_planned: bool = False,
    receipt_disclosed: bool = False,
    invocation_write_set: str = "none",
    delivery_state: str = "not_applicable",
    response_source: str | None = None,
    trace: list[str],
) -> dict[str, Any]:
    return {
        "outcome": outcome,
        "reason": reason,
        "effect_planned": effect_planned,
        "receipt_disclosed": receipt_disclosed,
        "invocation_write_set": invocation_write_set,
        "delivery_state": delivery_state,
        "response_source": response_source,
        "trace": trace,
    }


def evaluate_scenario(
    architecture: dict[str, Any], scenario_input: dict[str, Any]
) -> dict[str, Any]:
    trace: list[str] = ["discriminate:status_only"]
    if scenario_input["intent"] != "update_appointment_status":
        return _result(
            outcome="validation_rejected",
            reason="unsupported_status_confirm_variant",
            trace=trace,
        )

    trace.append("ingress:server_authority")
    if not scenario_input["server_authority_complete"]:
        return _result(
            outcome="validation_rejected",
            reason="server_authority_incomplete",
            trace=trace,
        )
    if scenario_input["session_binding"] == "missing":
        return _result(
            outcome="validation_rejected",
            reason="server_session_binding_required",
            trace=trace,
        )

    trace.extend(["lock:practice", "lock:appointment"])
    if scenario_input["target"] == "absent":
        return _result(
            outcome="validation_rejected", reason="target_not_found", trace=trace
        )

    trace.extend(["lock:idempotency_record", "recheck:current_authority"])
    if scenario_input["authority"] != "current":
        return _result(
            outcome="authority_revoked",
            reason="current_authority_revoked",
            trace=trace,
        )

    trace.append("inspect:idempotency")
    if scenario_input["idempotency"] == "same_digest_completed":
        trace.append("render:stored_canonical_receipt")
        return _result(
            outcome="idempotent_replay",
            reason="stored_receipt_replay",
            receipt_disclosed=True,
            delivery_state="delivered",
            response_source="stored_canonical_receipt",
            trace=trace,
        )
    if scenario_input["idempotency"] == "different_digest_completed":
        return _result(
            outcome="idempotency_conflict",
            reason="idempotency_key_reused_with_different_digest",
            trace=trace,
        )

    trace.append("recheck:appointment_state_version")
    if scenario_input["proposal_version"] != scenario_input["current_version"]:
        return _result(
            outcome="stale_precondition",
            reason="locked_source_version_mismatch",
            trace=trace,
        )

    trace.append("recompute:warning_codes")
    current_warnings = scenario_input["current_warning_codes"]
    submitted_warnings = scenario_input["submitted_warning_codes"]
    exact_warnings = (
        len(submitted_warnings) == len(set(submitted_warnings))
        and set(submitted_warnings) == set(current_warnings)
        and len(current_warnings) == len(set(current_warnings))
    )
    if not exact_warnings:
        return _result(
            outcome="confirmation_required",
            reason="warning_acknowledgement_mismatch",
            trace=trace,
        )

    trace.append("verify:signed_confirmation")
    if scenario_input["evidence"] != "valid":
        return _result(
            outcome="confirmation_required",
            reason="signed_confirmation_evidence_invalid",
            trace=trace,
        )
    if scenario_input["session_binding"] != "exact":
        return _result(
            outcome="confirmation_required",
            reason="signed_confirmation_session_mismatch",
            trace=trace,
        )

    trace.append("check:terminal_policy")
    if (
        scenario_input["current_status"]
        in architecture["terminal_policy"]["terminal_statuses"]
        and scenario_input["current_status"] != scenario_input["requested_status"]
    ):
        return _result(
            outcome="transition_policy_deferred",
            reason="terminal_retransition_policy_deferred",
            trace=trace,
        )

    trace.extend(["stage:appointment_mutation", "stage:attributable_audit"])
    if scenario_input["failure_injection"] == "after_staged_audit":
        trace.append("rollback:atomic")
        return _result(
            outcome="transaction_rolled_back",
            reason="atomic_write_set_rolled_back",
            trace=trace,
        )

    trace.append("stage:completed_receipt")
    if scenario_input["failure_injection"] == "after_staged_receipt":
        trace.append("rollback:atomic")
        return _result(
            outcome="transaction_rolled_back",
            reason="atomic_write_set_rolled_back",
            trace=trace,
        )

    trace.append("commit:atomic")
    if scenario_input["failure_injection"] == "after_commit_before_response":
        return _result(
            outcome="committed",
            reason="status_change_committed_delivery_unknown",
            effect_planned=True,
            invocation_write_set="all",
            delivery_state="delivery_unknown",
            response_source="stored_canonical_receipt",
            trace=trace,
        )

    trace.append("render:stored_canonical_receipt")
    return _result(
        outcome="committed",
        reason="status_change_committed",
        effect_planned=True,
        receipt_disclosed=True,
        invocation_write_set="all",
        delivery_state="delivered",
        response_source="stored_canonical_receipt",
        trace=trace,
    )


def evaluate_contract(contract: dict[str, Any]) -> list[dict[str, Any]]:
    evaluated: list[dict[str, Any]] = []
    defaults = contract["scenario_defaults"]
    for scenario in contract["scenarios"]:
        scenario_input = defaults | scenario["overrides"]
        actual = evaluate_scenario(contract["architecture"], scenario_input)
        expected = scenario["expected"]
        if {key: actual[key] for key in expected} != expected:
            raise ValueError(f"scenario expectation mismatch: {scenario['id']}")
        evaluated.append(
            {
                "id": scenario["id"],
                "outcome": actual["outcome"],
                "reason": actual["reason"],
                "effect_planned": actual["effect_planned"],
                "receipt_disclosed": actual["receipt_disclosed"],
                "invocation_write_set": actual["invocation_write_set"],
                "delivery_state": actual["delivery_state"],
                "response_source": actual["response_source"],
                "trace": actual["trace"],
            }
        )
    return evaluated


Mutation = Callable[[dict[str, Any]], None]


def _set(path: tuple[Any, ...], value: Any) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value

    return mutate


def _remove(path: tuple[Any, ...]) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        target = path[-1]
        if isinstance(cursor, list):
            cursor.pop(target)
        else:
            cursor.pop(target)

    return mutate


def hostile_mutations() -> list[tuple[str, Mutation]]:
    mutations: list[tuple[str, Mutation]] = [
        ("implementation_authority", _set(("implementation_authorized",), True)),
        ("forbidden_app_import", _set(("forbidden", "application_imported"), True)),
        ("source_head", _set(("source_head",), "0" * 40)),
    ]
    for index in range(9):
        mutations.append(
            (
                f"source_hash_{index}",
                _set(("source_bindings", index, "sha256"), "0" * 64),
            )
        )
    mutations.extend(
        [
            ("route_intent", _set(("architecture", "route_discriminator", "accepted_intent"), "update_appointment_waiting_area")),
            ("route_precheck", _set(("architecture", "route_discriminator", "discriminate_before_kernel_ingress"), False)),
            ("waiting_behavior", _set(("architecture", "route_discriminator", "waiting_area_behavior_unchanged"), False)),
            ("server_field", _remove(("architecture", "server_authority_ingress", "server_owned_fields", 4))),
            ("transport_authority", _set(("architecture", "server_authority_ingress", "transport_authority_accepted"), True)),
            ("opaque_session", _set(("architecture", "server_authority_ingress", "opaque_session_binding"), False)),
            ("authority_recheck", _set(("architecture", "server_authority_ingress", "recheck_after_locks"), False)),
            ("lock_order", _set(("architecture", "transaction_boundary", "lock_order"), ["practice", "idempotency_record", "appointment"])),
            ("unused_lock", _set(("architecture", "transaction_boundary", "unused_schedule_domain_rule"), "reorder")),
            ("disclosure_order", _set(("architecture", "transaction_boundary", "idempotency_disclosure_after_authority_recheck"), False)),
            ("multi_transaction", _set(("architecture", "transaction_boundary", "single_transaction"), False)),
            ("version_name", _set(("architecture", "source_version", "name"), "updated_at")),
            ("version_type", _set(("architecture", "source_version", "type"), "timestamp")),
            ("version_lock", _set(("architecture", "source_version", "read_under_appointment_lock"), False)),
            ("version_increment", _set(("architecture", "source_version", "increment_on_committed_appointment_state_change"), False)),
            ("physical_storage", _set(("architecture", "source_version", "physical_storage_deferred"), False)),
            ("evidence_binding", _remove(("architecture", "signed_evidence", "required_bindings", 3))),
            ("evidence_order", _set(("architecture", "signed_evidence", "verified_after_locked_recomputation"), False)),
            ("confirmation_freshness", _set(("architecture", "signed_evidence", "confirmation_distinct_from_freshness"), False)),
            ("warning_comparison", _set(("architecture", "warning_acknowledgement", "comparison"), "subset")),
            ("warning_missing", _set(("architecture", "warning_acknowledgement", "reject_missing"), False)),
            ("warning_extra", _set(("architecture", "warning_acknowledgement", "reject_extra"), False)),
            ("warning_duplicate", _set(("architecture", "warning_acknowledgement", "reject_duplicate"), False)),
            ("warning_unknown", _set(("architecture", "warning_acknowledgement", "reject_unknown"), False)),
            ("terminal_list", _remove(("architecture", "terminal_policy", "terminal_statuses", 0))),
            ("terminal_outcome", _set(("architecture", "terminal_policy", "different_target_outcome"), "committed")),
            ("terminal_effect", _set(("architecture", "terminal_policy", "effect_allowed"), True)),
            ("invent_policy", _set(("architecture", "terminal_policy", "product_policy_invented"), True)),
            ("write_member", _remove(("architecture", "atomic_write_set", "members", 1))),
            ("audit_binding", _remove(("architecture", "atomic_write_set", "completed_receipt_private_bindings", 7))),
            ("atomicity", _set(("architecture", "atomic_write_set", "all_commit_or_rollback"), False)),
            ("effect_outcome", _set(("architecture", "atomic_write_set", "effect_outcome"), "idempotent_replay")),
            ("initial_response", _set(("architecture", "stored_receipt_delivery", "initial_response_source"), "held_object")),
            ("replay_response", _set(("architecture", "stored_receipt_delivery", "replay_response_source"), "recomputed")),
            ("delivery_failure", _set(("architecture", "stored_receipt_delivery", "post_commit_failure_state"), "rolled_back")),
            ("server_retry", _set(("architecture", "stored_receipt_delivery", "server_effect_retry"), True)),
            ("client_retry", _set(("architecture", "stored_receipt_delivery", "client_retry_requirement"), "new_key")),
            ("trace_order", _set(("architecture", "decision_trace", 2), "lock:idempotency_record")),
            ("outcome_removed", _remove(("architecture", "outcome_vocabulary", 7))),
            ("scenario_effect", _set(("scenarios", 1, "expected", "effect_planned"), True)),
            ("scenario_disclosure", _set(("scenarios", 5, "expected", "receipt_disclosed"), True)),
            ("scenario_write", _set(("scenarios", 18, "expected", "invocation_write_set"), "all")),
            ("scenario_outcome", _set(("scenarios", 13, "expected", "outcome"), "committed")),
            ("next_candidate", _set(("next_candidate",), "mounted_route_implementation")),
        ]
    )
    return mutations


def reject_hostile_mutations(
    contract: dict[str, Any], schema: dict[str, Any]
) -> dict[str, int]:
    mutations = hostile_mutations()
    rejected = 0
    for mutation_id, mutation in mutations:
        candidate = copy.deepcopy(contract)
        mutation(candidate)
        try:
            validate_schema(candidate, schema)
            validate_contract_semantics(candidate)
            evaluate_contract(candidate)
            verify_source_bindings(candidate)
        except (AssertionError, KeyError, TypeError, ValidationError, ValueError):
            rejected += 1
            continue
        raise ValueError(f"hostile mutation admitted: {mutation_id}")
    if rejected < 40:
        raise ValueError("fewer than forty hostile mutations were rejected")
    return {"attempted": len(mutations), "rejected": rejected}


def build_evidence() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    validate_schema(contract, schema)
    validate_contract_semantics(contract)
    hashes = verify_source_bindings(contract)
    scenarios = evaluate_contract(contract)
    hostile = reject_hostile_mutations(contract, schema)
    return {
        "schema_version": "raisa.status_confirm_runtime_convergence_architecture_evidence.v1",
        "result": contract["result"],
        "source_head": contract["source_head"],
        "evidence_label": contract["evidence_label"],
        "implementation_authorized": False,
        "architecture_decisions": ARCHITECTURE_KEYS,
        "source_hashes": hashes,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "hostile_mutations": hostile,
        "forbidden": contract["forbidden"],
        "next_candidate": contract["next_candidate"],
    }


def main() -> int:
    evidence = build_evidence()
    EVIDENCE_PATH.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

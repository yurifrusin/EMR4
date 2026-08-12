"""Run the pure in-memory status-confirm runtime convergence rehearsal."""

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
    "runtime-convergence-rehearsal"
)
PACKET_PATH = BASE / "rehearsal-packet.json"
SCHEMA_PATH = BASE / "rehearsal-packet.schema.json"
EVIDENCE_PATH = BASE / "provider-free-rehearsal-evidence.json"

EXPECTED_SOURCE_BINDINGS = {
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture-plan.md": (
        "b2a645e11c28e625d13458d25cd6d6d959059897feef5f58c919ca5628e398f1"
    ),
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture.md": (
        "aa2eab6fddc0f8394ea3950965d525222917506a04b0ef10ab22999e2e442363"
    ),
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture-closeout.md": (
        "b5be8112872ec870f5c889a92e2be85a09833ac72d240fd5fd7144641d5638ee"
    ),
    "orchestration/agent_inbox/codex/raisa-status-confirm-runtime-convergence-architecture-sol-acceptance.md": (
        "c726c94fd635727f9359ea5f707d6a4395317a7658ae795d24c99fc93c6340a5"
    ),
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.json": (
        "6f2c970a4ab9234e72d6ffb08b2aa9b8738b779b94cee1885dbf262bfb5306ce"
    ),
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.schema.json": (
        "634f143c4dd6e29e9c796cd9c03a7ae4e91b8565ffa6e68f05ca5a8193a98fbf"
    ),
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/provider-free-architecture-evidence.json": (
        "8e88d44b888eae461cfdbc4c0a8357e7cf60fffc9c93ee8d7436b0a4c023a750"
    ),
    "scripts/raisa_provider_free_unmounted_status_confirm_runtime_convergence_architecture.py": (
        "bddcd4120a24a5b733e1bbe6b7028d3a4f0424ba560ef47cd1a34d109034505d"
    ),
}

EXPECTED_SCHEDULES = [
    ("scr-001-clean-commit", "clean_commit"),
    ("scr-002-waiting-area", "unsupported_variant"),
    ("scr-003-server-authority", "server_authority_incomplete"),
    ("scr-004-session-missing", "session_missing"),
    ("scr-005-target-absent", "target_absent"),
    ("scr-006-authority-revoked", "authority_revoked"),
    ("scr-007-evidence-invalid", "signed_evidence_invalid"),
    ("scr-008-session-mismatch", "session_mismatch"),
    ("scr-009-version-stale", "stale_version"),
    ("scr-010-warning-missing", "warning_missing"),
    ("scr-011-warning-extra", "warning_extra"),
    ("scr-012-warning-duplicate", "warning_duplicate"),
    ("scr-013-warning-unknown", "warning_unknown"),
    ("scr-014-terminal", "terminal_retransition"),
    ("scr-015-rollback-after-mutation", "failure_after_mutation"),
    ("scr-016-rollback-after-audit", "failure_after_audit"),
    ("scr-017-rollback-after-receipt", "failure_after_receipt"),
    ("scr-018-response-loss-retry", "response_loss_then_retry"),
    ("scr-019-same-digest-race", "concurrent_same_digest"),
    ("scr-020-different-digest-race", "concurrent_different_digest"),
    ("scr-021-authority-loss-waiting", "authority_loss_while_waiting"),
    ("scr-022-source-loss-waiting", "source_change_while_waiting"),
    ("scr-023-replay-after-revocation", "replay_after_authority_revoked"),
    ("scr-024-replay-after-target-loss", "replay_after_target_removed"),
]

EXPECTED_ARCHITECTURE_BINDING = {
    "path": (
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
        "runtime-convergence-architecture/convergence-architecture-contract.json"
    ),
    "sha256": "6f2c970a4ab9234e72d6ffb08b2aa9b8738b779b94cee1885dbf262bfb5306ce",
    "lock_order": ["practice", "appointment", "idempotency_record"],
    "effect_write_set": [
        "appointment_mutation",
        "attributable_audit",
        "completed_receipt",
    ],
    "response_source": "stored_canonical_receipt",
}

EXPECTED_INITIAL_STATE = {
    "practice_id": "practice-synthetic-001",
    "appointment_id": "apt-synthetic-001",
    "target_exists": True,
    "appointment_status": "Booked",
    "appointment_state_version": 7,
    "actor_id": "actor-synthetic-001",
    "actor_role": "Receptionist",
    "session_binding_digest": "sha256:session-synthetic-001",
    "authority_current": True,
    "mutation_count": 0,
    "audit_count": 0,
    "receipt_count": 0,
}

LOCK_TRACE = ["lock:practice", "lock:appointment", "lock:idempotency_record"]
WRITE_SET = ["appointment_mutation", "attributable_audit", "completed_receipt"]
CANONICAL_WARNING = "status-arrival-confirmed"
TERMINAL_STATUSES = {"Cancelled", "Completed"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_schema(packet: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(packet)


def verify_source_bindings(packet: dict[str, Any]) -> dict[str, str]:
    declared = {item["path"]: item["sha256"] for item in packet["source_bindings"]}
    if declared != EXPECTED_SOURCE_BINDINGS:
        raise ValueError("exact source binding set changed")
    observed: dict[str, str] = {}
    for relative_path, expected_hash in EXPECTED_SOURCE_BINDINGS.items():
        path = ROOT / relative_path
        if not path.is_file():
            raise ValueError(f"missing source binding: {relative_path}")
        observed_hash = _sha256(path)
        if observed_hash != expected_hash:
            raise ValueError(f"source hash mismatch: {relative_path}")
        observed[relative_path] = observed_hash
    return observed


def validate_packet_semantics(packet: dict[str, Any]) -> None:
    if packet["source_head"] != "0fe6b9bfaea2394d7fb7ebb9866bfb1fa56611cc":
        raise ValueError("source head changed")
    if packet["implementation_authorized"] is not False:
        raise ValueError("implementation authority must remain false")
    if packet["evidence_label"] != (
        "authored_synthetic_provider_free_pure_in_memory"
    ):
        raise ValueError("evidence label changed")
    if packet["architecture_binding"] != EXPECTED_ARCHITECTURE_BINDING:
        raise ValueError("architecture binding changed")
    if packet["initial_state"] != EXPECTED_INITIAL_STATE:
        raise ValueError("initial state changed")
    observed_schedules = [(item["id"], item["kind"]) for item in packet["schedules"]]
    if observed_schedules != EXPECTED_SCHEDULES:
        raise ValueError("schedule identity or order changed")
    if set(packet["forbidden"].values()) != {False}:
        raise ValueError("every forbidden effect must remain false")
    if packet["next_candidate"] != (
        "provider_free_read_only_status_confirm_physical_representability_review"
    ):
        raise ValueError("next candidate changed")


def _fresh_state(packet: dict[str, Any]) -> dict[str, Any]:
    initial = packet["initial_state"]
    return {
        "practice_id": initial["practice_id"],
        "appointment": {
            "appointment_id": initial["appointment_id"],
            "target_exists": initial["target_exists"],
            "status": initial["appointment_status"],
            "state_version": initial["appointment_state_version"],
        },
        "authority": {
            "actor_id": initial["actor_id"],
            "actor_role": initial["actor_role"],
            "active_user": True,
            "session_binding_digest": initial["session_binding_digest"],
            "current": initial["authority_current"],
        },
        "mutation_count": initial["mutation_count"],
        "audits": [],
        "receipts": {},
    }


def _base_request(packet: dict[str, Any]) -> dict[str, Any]:
    initial = packet["initial_state"]
    warnings = [CANONICAL_WARNING]
    return {
        "intent": "update_appointment_status",
        "target_status": "Arrived",
        "idempotency_key": "idempotency-synthetic-001",
        "request_digest": "sha256:request-synthetic-001",
        "proposed_state_version": initial["appointment_state_version"],
        "submitted_warning_codes": warnings,
        "server_ingress_complete": True,
        "session_present": True,
        "signature_valid": True,
        "signed_evidence": {
            "practice_id": initial["practice_id"],
            "appointment_id": initial["appointment_id"],
            "actor_id": initial["actor_id"],
            "session_binding_digest": initial["session_binding_digest"],
            "command": "update_appointment_status",
            "appointment_state_version": initial["appointment_state_version"],
            "warning_codes": warnings,
            "freshness_id": "freshness-synthetic-001",
        },
        "failure_point": None,
        "lose_response_after_commit": False,
    }


def _result(
    outcome: str,
    trace: list[str],
    *,
    receipt_disclosed: bool = False,
    response_bytes: str | None = None,
    effect_written: bool = False,
) -> dict[str, Any]:
    return {
        "outcome": outcome,
        "trace": trace,
        "receipt_disclosed": receipt_disclosed,
        "response_digest": (
            _digest_text(response_bytes) if response_bytes is not None else None
        ),
        "response_bytes": response_bytes,
        "effect_written": effect_written,
    }


def _canonical_warnings(request: dict[str, Any]) -> list[str]:
    if request["target_status"] == "Arrived":
        return [CANONICAL_WARNING]
    return []


def invoke(state: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    """Execute one deterministic synthetic invocation against mutable state."""

    trace = ["discriminate:status_only"]
    if request["intent"] != "update_appointment_status":
        return _result("validation_rejected", trace)

    trace.append("ingress:server_authority")
    if not request["server_ingress_complete"] or not request["session_present"]:
        return _result("validation_rejected", trace)

    trace.append("lock:practice")
    trace.append("lock:appointment")
    appointment = state["appointment"]
    if not appointment["target_exists"]:
        return _result("validation_rejected", trace)

    trace.append("lock:idempotency_record")
    trace.append("recheck:current_authority")
    authority = state["authority"]
    if not authority["current"] or not authority["active_user"]:
        return _result("authority_revoked", trace)

    trace.append("inspect:idempotency")
    stored = state["receipts"].get(request["idempotency_key"])
    if stored is not None:
        if stored["request_digest"] != request["request_digest"]:
            return _result("idempotency_conflict", trace)
        trace.append("render:stored_canonical_receipt")
        return _result(
            "idempotent_replay",
            trace,
            receipt_disclosed=True,
            response_bytes=stored["canonical_response_bytes"],
        )

    trace.append("recheck:appointment_state_version")
    if request["proposed_state_version"] != appointment["state_version"]:
        return _result("stale_precondition", trace)

    trace.append("recompute:warning_codes")
    submitted_warnings = request["submitted_warning_codes"]
    canonical_warnings = _canonical_warnings(request)
    warning_set_exact = set(submitted_warnings) == set(canonical_warnings)
    warning_values_unique = len(submitted_warnings) == len(set(submitted_warnings))
    if not warning_set_exact or not warning_values_unique:
        return _result("confirmation_required", trace)

    trace.append("verify:signed_confirmation")
    expected_evidence = {
        "practice_id": state["practice_id"],
        "appointment_id": appointment["appointment_id"],
        "actor_id": authority["actor_id"],
        "session_binding_digest": authority["session_binding_digest"],
        "command": request["intent"],
        "appointment_state_version": appointment["state_version"],
        "warning_codes": canonical_warnings,
        "freshness_id": "freshness-synthetic-001",
    }
    if not request["signature_valid"] or request["signed_evidence"] != expected_evidence:
        return _result("confirmation_required", trace)

    trace.append("check:terminal_policy")
    if (
        appointment["status"] in TERMINAL_STATUSES
        and appointment["status"] != request["target_status"]
    ):
        return _result("transition_policy_deferred", trace)

    staged = copy.deepcopy(state)
    staged_appointment = staged["appointment"]
    pre_version = staged_appointment["state_version"]
    post_version = pre_version + 1

    trace.append("stage:appointment_mutation")
    staged_appointment["status"] = request["target_status"]
    staged_appointment["state_version"] = post_version
    staged["mutation_count"] += 1
    if request["failure_point"] == "after_mutation":
        trace.append("rollback:atomic")
        return _result("transaction_rolled_back", trace)

    trace.append("stage:attributable_audit")
    audit_id = f"audit-synthetic-{len(staged['audits']) + 1:03d}"
    staged["audits"].append(
        {
            "audit_id": audit_id,
            "practice_id": staged["practice_id"],
            "appointment_id": staged_appointment["appointment_id"],
            "actor_id": authority["actor_id"],
            "operation": request["intent"],
            "pre_state_version": pre_version,
            "post_state_version": post_version,
        }
    )
    if request["failure_point"] == "after_audit":
        trace.append("rollback:atomic")
        return _result("transaction_rolled_back", trace)

    trace.append("stage:completed_receipt")
    public_response = {
        "appointment_id": staged_appointment["appointment_id"],
        "appointment_state_version": post_version,
        "status": staged_appointment["status"],
    }
    canonical_response = _canonical_json(public_response)
    staged["receipts"][request["idempotency_key"]] = {
        "operation": request["intent"],
        "practice_id": staged["practice_id"],
        "appointment_id": staged_appointment["appointment_id"],
        "actor_id": authority["actor_id"],
        "session_binding_digest": authority["session_binding_digest"],
        "idempotency_key": request["idempotency_key"],
        "request_digest": request["request_digest"],
        "audit_id": audit_id,
        "pre_state_version": pre_version,
        "post_state_version": post_version,
        "canonical_response_digest": _digest_text(canonical_response),
        "canonical_response_bytes": canonical_response,
    }
    if request["failure_point"] == "after_receipt":
        trace.append("rollback:atomic")
        return _result("transaction_rolled_back", trace)

    trace.append("commit:atomic")
    state.clear()
    state.update(staged)
    if request["lose_response_after_commit"]:
        trace.append("delivery:unknown")
        return _result("committed_delivery_unknown", trace, effect_written=True)

    trace.append("render:stored_canonical_receipt")
    stored_after_commit = state["receipts"][request["idempotency_key"]]
    return _result(
        "committed",
        trace,
        receipt_disclosed=True,
        response_bytes=stored_after_commit["canonical_response_bytes"],
        effect_written=True,
    )


def _state_summary(state: dict[str, Any], participants: list[dict[str, Any]]) -> dict[str, Any]:
    appointment = state["appointment"]
    return {
        "participant_outcomes": [item["outcome"] for item in participants],
        "target_exists": appointment["target_exists"],
        "appointment_status": appointment["status"],
        "appointment_state_version": appointment["state_version"],
        "mutation_count": state["mutation_count"],
        "audit_count": len(state["audits"]),
        "receipt_count": len(state["receipts"]),
        "disclosure_count": sum(item["receipt_disclosed"] for item in participants),
    }


def _lock_order_valid(trace: list[str]) -> bool:
    present = [item for item in LOCK_TRACE if item in trace]
    if not present:
        return True
    positions = [trace.index(item) for item in present]
    return positions == sorted(positions) and present == LOCK_TRACE[: len(present)]


def _authority_first(trace: list[str]) -> bool:
    if "inspect:idempotency" not in trace:
        return True
    return trace.index("recheck:current_authority") < trace.index(
        "inspect:idempotency"
    )


def _minimize_participant(participant: dict[str, Any]) -> dict[str, Any]:
    return {
        "outcome": participant["outcome"],
        "trace": participant["trace"],
        "receipt_disclosed": participant["receipt_disclosed"],
        "response_digest": participant["response_digest"],
        "effect_written": participant["effect_written"],
    }


def simulate_schedule(
    schedule: dict[str, Any], packet: dict[str, Any]
) -> dict[str, Any]:
    state = _fresh_state(packet)
    request = _base_request(packet)
    kind = schedule["kind"]
    participants: list[dict[str, Any]] = []

    if kind == "unsupported_variant":
        request["intent"] = "update_appointment_waiting_area"
    elif kind == "server_authority_incomplete":
        request["server_ingress_complete"] = False
    elif kind == "session_missing":
        request["session_present"] = False
    elif kind == "target_absent":
        state["appointment"].update(
            {"target_exists": False, "status": None, "state_version": None}
        )
    elif kind == "authority_revoked":
        state["authority"]["current"] = False
    elif kind == "signed_evidence_invalid":
        request["signature_valid"] = False
    elif kind == "session_mismatch":
        request["signed_evidence"]["session_binding_digest"] = (
            "sha256:wrong-session"
        )
    elif kind == "stale_version":
        request["proposed_state_version"] = 6
    elif kind == "warning_missing":
        request["submitted_warning_codes"] = []
    elif kind == "warning_extra":
        request["submitted_warning_codes"] = [CANONICAL_WARNING, "extra-warning"]
    elif kind == "warning_duplicate":
        request["submitted_warning_codes"] = [
            CANONICAL_WARNING,
            CANONICAL_WARNING,
        ]
    elif kind == "warning_unknown":
        request["submitted_warning_codes"] = ["unknown-warning"]
    elif kind == "terminal_retransition":
        state["appointment"]["status"] = "Completed"
    elif kind == "failure_after_mutation":
        request["failure_point"] = "after_mutation"
    elif kind == "failure_after_audit":
        request["failure_point"] = "after_audit"
    elif kind == "failure_after_receipt":
        request["failure_point"] = "after_receipt"

    two_participant = kind in {
        "response_loss_then_retry",
        "concurrent_same_digest",
        "concurrent_different_digest",
        "authority_loss_while_waiting",
        "source_change_while_waiting",
        "replay_after_authority_revoked",
        "replay_after_target_removed",
    }
    if not two_participant:
        participants.append(invoke(state, request))
    else:
        first_request = copy.deepcopy(request)
        if kind == "response_loss_then_retry":
            first_request["lose_response_after_commit"] = True
        participants.append(invoke(state, first_request))

        second_request = copy.deepcopy(request)
        if kind == "concurrent_different_digest":
            second_request["request_digest"] = "sha256:request-synthetic-002"
        elif kind in {"authority_loss_while_waiting", "replay_after_authority_revoked"}:
            state["authority"]["current"] = False
        elif kind == "source_change_while_waiting":
            second_request["idempotency_key"] = "idempotency-synthetic-002"
            second_request["request_digest"] = "sha256:request-synthetic-002"
        elif kind == "replay_after_target_removed":
            state["appointment"].update(
                {"target_exists": False, "status": None, "state_version": None}
            )
        participants.append(invoke(state, second_request))

    summary = _state_summary(state, participants)
    if summary != schedule["expected"]:
        raise ValueError(f"schedule result changed: {schedule['id']}")

    lock_order_valid = all(_lock_order_valid(item["trace"]) for item in participants)
    authority_first = all(_authority_first(item["trace"]) for item in participants)
    atomic_counts = (
        summary["mutation_count"]
        == summary["audit_count"]
        == summary["receipt_count"]
    )
    stored_digests = {
        item["canonical_response_digest"] for item in state["receipts"].values()
    }
    delivered_digests = {
        item["response_digest"]
        for item in participants
        if item["response_digest"] is not None
    }
    exact_stored_delivery = delivered_digests.issubset(stored_digests)
    if not all(
        [lock_order_valid, authority_first, atomic_counts, exact_stored_delivery]
    ):
        raise ValueError(f"schedule invariant failed: {schedule['id']}")

    return {
        "id": schedule["id"],
        "kind": kind,
        "participants": [_minimize_participant(item) for item in participants],
        "final": summary,
        "invariants": {
            "lock_order_valid": lock_order_valid,
            "authority_before_idempotency": authority_first,
            "atomic_write_counts_correlated": atomic_counts,
            "delivered_response_matches_stored_receipt": exact_stored_delivery,
        },
    }


def evaluate_packet(packet: dict[str, Any]) -> list[dict[str, Any]]:
    results = [simulate_schedule(schedule, packet) for schedule in packet["schedules"]]
    if len(results) != 24:
        raise ValueError("exactly 24 schedule results are required")
    return results


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
        ("source_head", _set(("source_head",), "0" * 40)),
        ("evidence_label", _set(("evidence_label",), "runtime")),
        ("implementation_authority", _set(("implementation_authorized",), True)),
        ("architecture_path", _set(("architecture_binding", "path"), "other")),
        ("architecture_hash", _set(("architecture_binding", "sha256"), "0" * 64)),
        (
            "lock_order",
            _set(
                ("architecture_binding", "lock_order"),
                ["practice", "idempotency_record", "appointment"],
            ),
        ),
        (
            "write_set",
            _remove(("architecture_binding", "effect_write_set", 1)),
        ),
        (
            "response_source",
            _set(("architecture_binding", "response_source"), "recomputed"),
        ),
        ("schedule_removed", _remove(("schedules", 23))),
        (
            "next_candidate",
            _set(("next_candidate",), "mounted_route_implementation"),
        ),
    ]
    for index in range(8):
        mutations.append(
            (
                f"source_hash_{index}",
                _set(("source_bindings", index, "sha256"), "0" * 64),
            )
        )
    initial_mutations = {
        "practice_id": "other-practice",
        "appointment_id": "other-appointment",
        "target_exists": False,
        "appointment_status": "Arrived",
        "appointment_state_version": 8,
        "actor_id": "other-actor",
        "actor_role": "Administrator",
        "session_binding_digest": "sha256:other-session",
        "authority_current": False,
        "mutation_count": 1,
        "audit_count": 1,
        "receipt_count": 1,
    }
    for key, value in initial_mutations.items():
        mutations.append((f"initial_{key}", _set(("initial_state", key), value)))
    for index, (_, expected_kind) in enumerate(EXPECTED_SCHEDULES):
        replacement = "clean_commit" if expected_kind != "clean_commit" else "target_absent"
        mutations.append(
            (f"schedule_kind_{index}", _set(("schedules", index, "kind"), replacement))
        )
        mutations.append(
            (
                f"schedule_outcome_{index}",
                _set(
                    ("schedules", index, "expected", "participant_outcomes"),
                    ["hostile_outcome"],
                ),
            )
        )
    for key in [
        "application_imported",
        "application_edited",
        "route_executed",
        "database_driver_imported",
        "database_executed",
        "real_lock_acquired",
        "provider_called",
        "credential_or_browser_authorization_used",
        "product_or_patient_data_used",
        "command_executed",
    ]:
        mutations.append((f"forbidden_{key}", _set(("forbidden", key), True)))
    return mutations


def reject_hostile_mutations(
    packet: dict[str, Any], schema: dict[str, Any]
) -> dict[str, int]:
    mutations = hostile_mutations()
    rejected = 0
    for mutation_id, mutation in mutations:
        candidate = copy.deepcopy(packet)
        mutation(candidate)
        try:
            validate_schema(candidate, schema)
            validate_packet_semantics(candidate)
            evaluate_packet(candidate)
            verify_source_bindings(candidate)
        except (AssertionError, KeyError, TypeError, ValidationError, ValueError):
            rejected += 1
            continue
        raise ValueError(f"hostile mutation admitted: {mutation_id}")
    if rejected < 50:
        raise ValueError("fewer than 50 hostile mutations were rejected")
    return {"attempted": len(mutations), "rejected": rejected}


def build_evidence() -> dict[str, Any]:
    packet = _load(PACKET_PATH)
    schema = _load(SCHEMA_PATH)
    validate_schema(packet, schema)
    validate_packet_semantics(packet)
    source_hashes = verify_source_bindings(packet)
    schedules = evaluate_packet(packet)
    hostile = reject_hostile_mutations(packet, schema)
    return {
        "schema_version": "raisa.status_confirm_runtime_convergence_rehearsal_evidence.v1",
        "result": packet["result"],
        "source_head": packet["source_head"],
        "evidence_label": packet["evidence_label"],
        "implementation_authorized": False,
        "source_hashes": source_hashes,
        "architecture_binding": packet["architecture_binding"],
        "schedule_count": len(schedules),
        "schedules": schedules,
        "invariants": {
            "status_only_discrimination": True,
            "server_owned_authority_and_session": True,
            "ordered_locks": True,
            "authority_before_idempotency_disclosure": True,
            "exact_version_warning_and_evidence_checks": True,
            "terminal_retransition_deferred": True,
            "atomic_mutation_audit_receipt": True,
            "stored_canonical_initial_and_replay_delivery": True,
        },
        "hostile_mutations": hostile,
        "forbidden": packet["forbidden"],
        "next_candidate": packet["next_candidate"],
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

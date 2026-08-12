"""Pure provider-free status-confirm to transaction-kernel adapter contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract"
CONTRACT_PATH = OUT / "adapter-contract.json"
SCHEMA_PATH = OUT / "adapter-contract.schema.json"
EVIDENCE_PATH = OUT / "adapter-evidence.json"
LOCKS = ["practice", "appointment", "idempotency_record"]
TERMINAL = ["Completed", "Cancelled", "DNA", "NoShow"]
SOURCES = [
    {"path": "orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal/protocol-packet.json", "sha256": "2967703f8baf395439a6e2c88885074fefe9f4bea308c0294ba7e67c57b26633"},
    {"path": "orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal/protocol-evidence.json", "sha256": "c95288aa9903ebfa7d10abd199567038cfcc1c72d3e3b80f763dc6d7a588f23c"},
    {"path": "app/routers/appointments.py", "sha256": "59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb"},
    {"path": "app/schemas/appointments.py", "sha256": "d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d"},
    {"path": "docs/api-spine/openapi/appointment-commands.yaml", "sha256": "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6"},
    {"path": "tests/test_api_spine_status_confirm_idempotency_route_contract.py", "sha256": "0ecc5b2bff0853d3f9797163b979f575f9604c6ba0895cf5bd36c165664eb8af"},
    {"path": "tests/test_api_spine_confirmation_contract_matrix.py", "sha256": "4881bde300c6c62a061518aec8a1ddfc5e7b185e0c1cd4f86c490c5fef2c6ef6"},
    {"path": "review/test_raw_status_terminal_rollback_guard.py", "sha256": "fbfa53e8fc8cf22b522437c1d74aa77638ef930bfc1fec5ff678b45c221555b6"},
]


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def base_input() -> dict[str, Any]:
    command = {
        "kind": "status", "appointment_id": "apt-synthetic-001",
        "status": "Confirmed", "status_reason_code": None,
        "waiting_area_id": None, "waiting_area_id_supplied": False,
        "clears_waiting_area": False,
    }
    current = {
        "appointment_id": "apt-synthetic-001", "status": "Booked",
        "status_reason_code": None, "waiting_area_id": None, "source_version": 7,
    }
    return {
        "structure": "valid",
        "transport": {
            "operation_id": "confirmAppointmentStatusProposal",
            "route_family": "status-confirm", "idempotency_key": "status-key-001",
            "confirmed": True, "proposal_intent": "update_appointment_status",
            "proposal_safe": True, "requires_confirmation": True,
            "autonomy_tier": "execute_with_report", "command": command,
            "proposal_warning_codes": [], "confirmed_warning_codes": [],
            "freshness_id": "fresh-001", "signed_evidence_required": True,
        },
        "server": {
            "practice_id": "practice-synthetic-001", "actor_id": "actor-synthetic-001",
            "actor_role": "Receptionist", "session_id": "session-synthetic-001",
            "authority_current": True, "current_state": current,
            "expected_freshness_id": "fresh-001", "evidence_status": "verified",
            "evidence_purpose": "appointment.status.confirm.v1",
            "expected_evidence_purpose": "appointment.status.confirm.v1",
            "evidence_binding": "exact",
        },
    }


def stop(reason: str, outcome: str = "validation_rejected") -> dict[str, Any]:
    return {"kind": "stopped", "outcome": outcome, "reason": reason, "kernel_request": None, "effect_authority": False}


def adapt(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("structure") != "valid":
        return stop("structure_invalid")
    transport, server = value["transport"], value["server"]
    if transport["operation_id"] != "confirmAppointmentStatusProposal" or transport["route_family"] != "status-confirm":
        return stop("operation_binding_mismatch")
    if transport["proposal_intent"] != "update_appointment_status" or transport["command"]["kind"] != "status":
        return stop("unsupported_status_confirm_variant")
    if not transport["idempotency_key"].strip():
        return stop("idempotency_key_required", "idempotency_conflict")
    if not server["authority_current"]:
        return stop("current_authority_revoked", "authority_revoked")
    if not server["session_id"]:
        return stop("server_session_binding_required")
    if transport["confirmed"] is not True:
        return stop("explicit_confirmation_required", "confirmation_required")
    if not transport["proposal_safe"] or not transport["requires_confirmation"] or transport["autonomy_tier"] not in {"proposal", "execute_with_report"}:
        return stop("status_proposal_not_safe")
    if not transport["signed_evidence_required"] or server["evidence_status"] != "verified" or server["evidence_purpose"] != server["expected_evidence_purpose"] or server["evidence_binding"] != "exact":
        return stop("signed_confirmation_evidence_invalid", "confirmation_required")
    if transport["freshness_id"] != server["expected_freshness_id"]:
        return stop("stale_status_proposal_freshness_id", "stale_precondition")
    command, current = transport["command"], server["current_state"]
    if command["appointment_id"] != current["appointment_id"]:
        return stop("current_target_mismatch", "stale_precondition")
    proposed = transport["proposal_warning_codes"]
    confirmed = transport["confirmed_warning_codes"]
    if len(proposed) != len(set(proposed)) or len(confirmed) != len(set(confirmed)) or set(proposed) != set(confirmed):
        return stop("warning_acknowledgement_mismatch", "confirmation_required")
    if current["status"] in TERMINAL and command["status"] != current["status"]:
        return stop("transition_policy_deferred")
    request = {
        "schema_version": "raisa.status_kernel_request.v1",
        "operation_id": transport["operation_id"], "route_family": transport["route_family"],
        "practice_id": server["practice_id"], "actor_id": server["actor_id"],
        "actor_role": server["actor_role"], "session_id": server["session_id"],
        "idempotency_key": transport["idempotency_key"].strip(),
        "target_appointment_id": command["appointment_id"],
        "source_version": current["source_version"], "command": command,
        "warning_codes": sorted(proposed), "lock_plan": list(LOCKS),
        "signed_evidence_binding_digest": digest({"purpose": server["evidence_purpose"], "binding": server["evidence_binding"]}),
        "effect_authority": False,
    }
    request["request_digest"] = digest(request)
    return {"kind": "kernel_request_ready", "outcome": None, "reason": None, "kernel_request": request, "effect_authority": False}


def case(case_id: str, path: tuple[str, ...] | None = None, value: Any = None) -> dict[str, Any]:
    item = base_input()
    if path:
        cursor = item
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = value
    return {"id": case_id, "input": item, "expected": adapt(item)}


def result_mappings() -> list[dict[str, Any]]:
    return [
        {"outcome": "committed", "transport": "stored_receipt", "status": 200, "release": True},
        {"outcome": "idempotent_replay", "transport": "stored_receipt_exact", "status": 200, "release": True},
        {"outcome": "stale_precondition", "transport": "blocked", "status": 200, "release": True},
        {"outcome": "schedule_conflict", "transport": "internal_contract_error", "status": None, "release": False},
        {"outcome": "authority_revoked", "transport": "error", "status": 403, "release": True},
        {"outcome": "confirmation_required", "transport": "blocked", "status": 200, "release": True},
        {"outcome": "validation_rejected", "transport": "blocked", "status": 200, "release": True},
        {"outcome": "idempotency_conflict", "transport": "error", "status": 409, "release": True},
    ]


def build_contract() -> dict[str, Any]:
    cases = [
        case("ska-001-ready"), case("ska-002-structure", ("structure",), "invalid"),
        case("ska-003-operation", ("transport", "operation_id"), "rawStatusPatch"),
        case("ska-004-waiting-variant", ("transport", "proposal_intent"), "update_appointment_waiting_area"),
        case("ska-005-idempotency", ("transport", "idempotency_key"), " "),
        case("ska-006-authority", ("server", "authority_current"), False),
        case("ska-007-session", ("server", "session_id"), ""),
        case("ska-008-confirmation", ("transport", "confirmed"), False),
        case("ska-009-evidence", ("server", "evidence_status"), "invalid"),
        case("ska-010-freshness", ("transport", "freshness_id"), "stale"),
        case("ska-011-target", ("server", "current_state", "appointment_id"), "apt-other"),
        case("ska-012-warning", ("transport", "proposal_warning_codes"), ["already_terminal"]),
        case("ska-013-terminal", ("server", "current_state", "status"), "Completed"),
        case("ska-014-unsafe", ("transport", "proposal_safe"), False),
        case("ska-015-purpose", ("server", "evidence_purpose"), "wrong-purpose"),
    ]
    receipt = {"safe": True, "autonomy_tier": "confirmed_write", "appointment": {"id": "apt-synthetic-001", "status": "Confirmed"}}
    return {
        "schema_version": "raisa.status_confirm_kernel_adapter_contract.v1",
        "source_bindings": SOURCES, "lock_plan": LOCKS, "terminal_statuses": TERMINAL,
        "cases": cases, "result_mappings": result_mappings(),
        "delivery_recovery": {"stored_body": receipt, "stored_digest": digest(receipt), "delivery_failure_changes_receipt": False, "retry_uses_stored_receipt": True, "duplicate_kernel_request": False},
        "effect_boundary": {"application_import": False, "route_execution": False, "database": False, "provider": False, "network": False, "command": False, "product_data": False},
    }


def build_schema() -> dict[str, Any]:
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "additionalProperties": False,
            "required": ["schema_version", "source_bindings", "lock_plan", "terminal_statuses", "cases", "result_mappings", "delivery_recovery", "effect_boundary"],
            "properties": {"schema_version": {"const": "raisa.status_confirm_kernel_adapter_contract.v1"}, "source_bindings": {"type": "array", "minItems": 8}, "lock_plan": {"const": LOCKS}, "terminal_statuses": {"const": TERMINAL}, "cases": {"type": "array", "minItems": 15}, "result_mappings": {"type": "array", "minItems": 8, "maxItems": 8}, "delivery_recovery": {"type": "object"}, "effect_boundary": {"type": "object", "additionalProperties": {"const": False}}}}


def validate(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [e.message for e in Draft202012Validator(schema).iter_errors(contract)]
    if errors:
        return sorted(errors)
    if contract["source_bindings"] != SOURCES:
        errors.append("source_bindings_mismatch")
    for row in SOURCES:
        if hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            errors.append("source_hash_mismatch:" + row["path"])
    if contract["result_mappings"] != result_mappings():
        errors.append("result_mapping_mismatch")
    for item in contract["cases"]:
        if adapt(item["input"]) != item["expected"]:
            errors.append("case_mismatch:" + item["id"])
    delivery = contract["delivery_recovery"]
    if delivery["stored_digest"] != digest(delivery["stored_body"]) or delivery["delivery_failure_changes_receipt"] or not delivery["retry_uses_stored_receipt"] or delivery["duplicate_kernel_request"]:
        errors.append("delivery_recovery_mismatch")
    if any(contract["effect_boundary"].values()):
        errors.append("effect_boundary_open")
    return sorted(set(errors))


def mutations(contract: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    def add(name: str, path: tuple[Any, ...], value: Any) -> None:
        item = copy.deepcopy(contract); cursor: Any = item
        for part in path[:-1]: cursor = cursor[part]
        cursor[path[-1]] = value; out.append((name, item))
    add("schema", ("schema_version",), "v2"); add("locks", ("lock_plan",), list(reversed(LOCKS)))
    add("terminals", ("terminal_statuses",), TERMINAL[:-1]); add("mapping", ("result_mappings", 0, "status"), 201)
    add("receipt_digest", ("delivery_recovery", "stored_digest"), "0" * 64)
    add("retry", ("delivery_recovery", "retry_uses_stored_receipt"), False)
    add("duplicate", ("delivery_recovery", "duplicate_kernel_request"), True)
    for key in contract["effect_boundary"]: add("effect_" + key, ("effect_boundary", key), True)
    for index in range(15): add(f"case_{index}", ("cases", index, "expected", "effect_authority"), True)
    for index in range(8): add(f"source_{index}", ("source_bindings", index, "sha256"), "0" * 64)
    return out


def report(contract: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    canonical = validate(contract, schema)
    admitted = [name for name, item in mutations(contract) if not validate(item, schema)]
    return {"schema_version": "raisa.status_confirm_kernel_adapter_evidence.v1", "status": "passed" if not canonical and not admitted else "failed", "canonical_errors": canonical, "case_count": len(contract["cases"]), "result_mapping_count": len(contract["result_mappings"]), "hostile_mutation_count": len(mutations(contract)), "admitted_hostile_mutations": admitted, "runtime_or_command_authority_granted": False}


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); args = parser.parse_args()
    contract, schema = build_contract(), build_schema(); evidence = report(contract, schema)
    if args.write:
        write(CONTRACT_PATH, contract); write(SCHEMA_PATH, schema); write(EVIDENCE_PATH, evidence)
    else: print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__": raise SystemExit(main())

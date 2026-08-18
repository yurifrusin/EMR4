"""Run the provider-free unmounted check-in admission kernel rehearsal."""

from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterator

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.check_in_admission_control import (
    SCHEMA_VERSION,
    AdmissionLane,
    AdmissionRequest,
    AdmissionSnapshot,
    AdmissionState,
    CommandValidationReason,
    ControlCommandEnvelope,
    ControlOperation,
    DecisionReason,
    KillSwitchState,
    OrdinaryAdmissionRecord,
    REHEARSAL_PROFILE,
    engage_kill_switch,
    evaluate_admission,
    transition_record,
    unknown_commit_result,
    validate_command_envelope,
)


BASE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal"
)
CONTRACT = BASE / "contract.json"
SCHEMA = BASE / "contract.schema.json"
EVIDENCE = BASE / "provider-free-kernel-rehearsal-evidence.json"
REPORT = BASE / "kernel-rehearsal-report.md"
MODULE = ROOT / "orchestration_harness/check_in_admission_control.py"
ALLOWED_IMPORT_ROOTS = {"__future__", "dataclasses", "enum", "re"}


def _canonical_bytes(path: Path) -> bytes:
    text = path.read_bytes().decode("utf-8", errors="strict")
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        raise ValueError(f"bare carriage return: {path.relative_to(ROOT)}")
    return text.encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(_canonical_bytes(path)).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _source_bindings(contract: dict[str, Any]) -> int:
    bindings = contract["source_bindings"]
    for binding in bindings:
        path = ROOT / binding["path"]
        if _sha256(path) != binding["sha256"]:
            raise ValueError(f"source binding mismatch: {binding['path']}")
    return len(bindings)


def _module_imports() -> set[str]:
    tree = ast.parse(MODULE.read_text(encoding="utf-8"), filename=str(MODULE))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def validate_contract(
    candidate: dict[str, Any],
    schema: dict[str, Any],
    *,
    normative: dict[str, Any] | None = None,
) -> None:
    jsonschema.validate(candidate, schema)
    if normative is not None and candidate != normative:
        raise ValueError("candidate differs from the normative contract")
    profile = candidate["kernel_profile"]
    if profile != {
        "module": "orchestration_harness.check_in_admission_control",
        "unmounted": True,
        "standard_library_only": True,
        "imports_app": False,
        "ordinary_activation_authority_granted": False,
        "canonical_active_ordinary_record_count": 0,
        "ordinary_admission_release_possible": False,
        "executes_product_command": False,
        "persists_state": False,
        "reads_environment": False,
        "uses_network_or_provider": False,
    }:
        raise ValueError("kernel profile widened")
    if _module_imports() != ALLOWED_IMPORT_ROOTS:
        raise ValueError("kernel imports are not the exact standard-library allowlist")
    if REHEARSAL_PROFILE.ordinary_activation_authority_granted:
        raise ValueError("ordinary activation authority is open")
    if REHEARSAL_PROFILE.canonical_active_ordinary_record_count != 0:
        raise ValueError("canonical active ordinary record count is nonzero")
    types = candidate["types"]
    if types["admission_states"] != [item.value for item in AdmissionState]:
        raise ValueError("admission state vocabulary mismatch")
    if types["kill_switch_states"] != [item.value for item in KillSwitchState]:
        raise ValueError("kill-switch vocabulary mismatch")
    if types["lanes"] != [item.value for item in AdmissionLane]:
        raise ValueError("lane vocabulary mismatch")
    transitions = candidate["transitions"]
    if transitions["accepted_transition_may_produce_active"]:
        raise ValueError("current transition profile may produce active")
    if transitions["resume_operation_present"]:
        raise ValueError("resume operation is present")
    if transitions["kill_switch_clear_operation_present"]:
        raise ValueError("kill-switch clear operation is present")
    if candidate["command_envelope"]["operation_ids"] != [
        item.value for item in ControlOperation
    ]:
        raise ValueError("control operation vocabulary mismatch")
    if candidate["clockwork_boundary"]["live_gear_mesh_implemented"]:
        raise ValueError("live clockwork gear mesh is outside authority")
    if not all(value is False for value in candidate["closed_boundaries"].values()):
        raise ValueError("a protected boundary is open")


def _record(
    state: AdmissionState,
    *,
    evidence: bool = True,
    practice_id: str = "synthetic-practice-001",
    environment: str = "test",
) -> OrdinaryAdmissionRecord:
    return OrdinaryAdmissionRecord(
        state=state,
        practice_id=practice_id,
        environment=environment,
        operation_family="canonical_check_in",
        record_version=1,
        snapshot_generation=7,
        operational_evidence_valid=evidence,
    )


def _snapshot(
    *,
    record: OrdinaryAdmissionRecord | None = None,
    kill_switch: KillSwitchState = KillSwitchState.CLEAR,
) -> AdmissionSnapshot:
    return AdmissionSnapshot(
        schema_version=SCHEMA_VERSION,
        signature_valid=True,
        authority_git_object="752b521c59f5b44bf46de0cf776a33ac74b8134d",
        authority_git_object_resolved=True,
        fresh=True,
        environment="test",
        snapshot_generation=7,
        snapshot_digest="a" * 64,
        current_record_count=0 if record is None else 1,
        kill_switch=kill_switch,
        ordinary_record=record,
    )


def _request(
    *,
    feature: bool = True,
    synthetic: bool = False,
    practice_id: str = "synthetic-practice-001",
    environment: str = "test",
) -> AdmissionRequest:
    return AdmissionRequest(
        feature_enabled=feature,
        authored_synthetic_admitted=synthetic,
        practice_id=practice_id,
        environment=environment,
    )


def _evaluator_scenarios() -> list[tuple[str, AdmissionSnapshot | None, AdmissionRequest, DecisionReason, bool]]:
    active = _record(AdmissionState.ACTIVE)
    return [
        ("snapshot_missing", None, _request(), DecisionReason.SNAPSHOT_MISSING, False),
        ("schema_invalid", replace(_snapshot(), schema_version="v2"), _request(), DecisionReason.SNAPSHOT_INVALID, False),
        ("git_abbreviated", replace(_snapshot(), authority_git_object="752b521"), _request(), DecisionReason.SNAPSHOT_INVALID, False),
        ("git_unresolved", replace(_snapshot(), authority_git_object_resolved=False), _request(), DecisionReason.SNAPSHOT_INVALID, False),
        ("snapshot_stale", replace(_snapshot(), fresh=False), _request(), DecisionReason.SNAPSHOT_STALE, False),
        ("snapshot_ambiguous", replace(_snapshot(record=active), current_record_count=2), _request(), DecisionReason.SNAPSHOT_AMBIGUOUS, False),
        ("feature_disabled", _snapshot(), _request(feature=False), DecisionReason.FEATURE_DISABLED, False),
        ("kill_switch_synthetic", _snapshot(kill_switch=KillSwitchState.ENGAGED), _request(synthetic=True), DecisionReason.KILL_SWITCH_ENGAGED, False),
        ("kill_switch_ordinary", _snapshot(record=active, kill_switch=KillSwitchState.ENGAGED), _request(), DecisionReason.KILL_SWITCH_ENGAGED, False),
        ("lane_ambiguous", _snapshot(record=active), _request(synthetic=True), DecisionReason.LANE_AMBIGUOUS, False),
        ("synthetic_admitted", _snapshot(), _request(synthetic=True), DecisionReason.ADMITTED_SYNTHETIC, True),
        ("ordinary_absent", _snapshot(), _request(), DecisionReason.NO_MATCHING_LANE, False),
        ("ordinary_prepared", _snapshot(record=_record(AdmissionState.PREPARED)), _request(), DecisionReason.ORDINARY_STATE_NOT_ACTIVE, False),
        ("ordinary_active_evidence_missing", _snapshot(record=_record(AdmissionState.ACTIVE, evidence=False)), _request(), DecisionReason.ORDINARY_EVIDENCE_MISSING, False),
        ("ordinary_active_authority_closed", _snapshot(record=active), _request(), DecisionReason.ORDINARY_ACTIVATION_CLOSED, False),
        ("wrong_environment", _snapshot(), _request(environment="staging"), DecisionReason.SNAPSHOT_INVALID, False),
        ("ordinary_binding_mismatch", _snapshot(record=_record(AdmissionState.ACTIVE, practice_id="other-practice")), _request(), DecisionReason.ORDINARY_BINDING_MISMATCH, False),
    ]


def _run_evaluator_scenarios() -> dict[str, Any]:
    observed: list[dict[str, Any]] = []
    for scenario_id, snapshot, request, expected_reason, expected_admitted in _evaluator_scenarios():
        decision = evaluate_admission(snapshot, request)
        if decision.reason_code is not expected_reason:
            raise ValueError(f"evaluator reason mismatch: {scenario_id}")
        if decision.admitted is not expected_admitted:
            raise ValueError(f"evaluator decision mismatch: {scenario_id}")
        if decision.admitted and decision.lane is not AdmissionLane.AUTHORED_SYNTHETIC:
            raise ValueError(f"non-synthetic admission escaped: {scenario_id}")
        observed.append(
            {
                "scenario_id": scenario_id,
                "decision": decision.decision.value,
                "lane": decision.lane.value,
                "reason_code": decision.reason_code.value,
            }
        )
    return {"count": len(observed), "results": observed}


def _run_transition_scenarios() -> dict[str, Any]:
    accepted: list[str] = []
    count = 0
    for state in AdmissionState:
        for operation in ControlOperation:
            result = transition_record(state, operation)
            count += 1
            if result.accepted:
                edge = f"{result.from_state.value}->{result.to_state.value}"
                accepted.append(edge)
                if result.to_state is AdmissionState.ACTIVE:
                    raise ValueError("transition released active")
    expected = [
        "absent->prepared",
        "prepared->withdrawn",
        "active->suspended",
        "active->withdrawn",
        "suspended->withdrawn",
    ]
    if accepted != expected:
        raise ValueError("executable transition subset mismatch")
    kill_results = [engage_kill_switch(item) for item in KillSwitchState]
    if not kill_results[0].accepted or kill_results[0].to_state is not KillSwitchState.ENGAGED:
        raise ValueError("kill switch did not engage")
    if kill_results[1].accepted:
        raise ValueError("engaged kill switch changed in place")
    return {
        "record_matrix_count": count,
        "accepted_record_edges": accepted,
        "kill_switch_count": len(kill_results),
        "active_output_count": 0,
    }


def _valid_command() -> ControlCommandEnvelope:
    return ControlCommandEnvelope(
        operation_id=ControlOperation.PREPARE.value,
        authenticated_current_human=True,
        dedicated_operator_role=True,
        server_owned_practice_scope=True,
        server_owned_environment_scope=True,
        correlation_id="correlation-001",
        idempotency_key="idempotency-001",
        complete_request_digest="b" * 64,
        idempotency_bound_to_complete_request_digest=True,
        expected_record_version=0,
        expected_snapshot_generation=7,
        closed_reason_code="planned_rehearsal",
        authority_git_object="752b521c59f5b44bf46de0cf776a33ac74b8134d",
        authority_git_object_resolved=True,
        fresh=True,
        append_only_audit_available=True,
        bounded_patient_free_receipt=True,
    )


def _run_command_scenarios() -> dict[str, Any]:
    valid = _valid_command()
    scenarios: list[tuple[str, ControlCommandEnvelope, CommandValidationReason]] = [
        ("valid", valid, CommandValidationReason.ACCEPTED),
        ("unknown_operation", replace(valid, operation_id="unknown"), CommandValidationReason.UNKNOWN_OPERATION),
        ("human_missing", replace(valid, authenticated_current_human=False), CommandValidationReason.HUMAN_AUTHORITY_REQUIRED),
        ("role_missing", replace(valid, dedicated_operator_role=False), CommandValidationReason.OPERATOR_ROLE_REQUIRED),
        ("practice_scope_missing", replace(valid, server_owned_practice_scope=False), CommandValidationReason.PRACTICE_SCOPE_REQUIRED),
        ("environment_scope_missing", replace(valid, server_owned_environment_scope=False), CommandValidationReason.ENVIRONMENT_SCOPE_REQUIRED),
        ("correlation_missing", replace(valid, correlation_id=""), CommandValidationReason.CORRELATION_REQUIRED),
        ("idempotency_missing", replace(valid, idempotency_key=""), CommandValidationReason.IDEMPOTENCY_REQUIRED),
        ("request_digest_invalid", replace(valid, complete_request_digest="short"), CommandValidationReason.REQUEST_DIGEST_INVALID),
        ("digest_binding_missing", replace(valid, idempotency_bound_to_complete_request_digest=False), CommandValidationReason.IDEMPOTENCY_DIGEST_BINDING_REQUIRED),
        ("record_version_invalid", replace(valid, expected_record_version=-1), CommandValidationReason.EXPECTED_RECORD_VERSION_INVALID),
        ("generation_invalid", replace(valid, expected_snapshot_generation=0), CommandValidationReason.EXPECTED_GENERATION_INVALID),
        ("reason_missing", replace(valid, closed_reason_code=""), CommandValidationReason.CLOSED_REASON_REQUIRED),
        ("git_abbreviated", replace(valid, authority_git_object="752b521"), CommandValidationReason.AUTHORITY_GIT_OBJECT_INVALID),
        ("git_unresolved", replace(valid, authority_git_object_resolved=False), CommandValidationReason.AUTHORITY_GIT_OBJECT_UNRESOLVED),
        ("freshness_missing", replace(valid, fresh=False), CommandValidationReason.FRESHNESS_REQUIRED),
        ("audit_missing", replace(valid, append_only_audit_available=False), CommandValidationReason.AUDIT_REQUIRED),
        ("receipt_not_patient_free", replace(valid, bounded_patient_free_receipt=False), CommandValidationReason.PATIENT_FREE_RECEIPT_REQUIRED),
    ]
    for scenario_id, command, expected in scenarios:
        result = validate_command_envelope(command)
        if result.reason_code is not expected:
            raise ValueError(f"command reason mismatch: {scenario_id}")
        if result.accepted is not (expected is CommandValidationReason.ACCEPTED):
            raise ValueError(f"command decision mismatch: {scenario_id}")
    unknown = asdict(unknown_commit_result())
    if unknown != {
        "success_released": False,
        "readback_required": True,
        "retry_allowed": False,
        "readback_identity": "server_command_id_and_idempotency_identity",
    }:
        raise ValueError("unknown commit posture widened")
    return {
        "count": len(scenarios),
        "accepted_count": 1,
        "seven_character_git_object_rejected": True,
        "unknown_commit": unknown,
    }


PathPart = str | int


def _paths(value: Any, prefix: tuple[PathPart, ...] = ()) -> Iterator[tuple[PathPart, ...]]:
    if isinstance(value, dict):
        yield prefix
        for key, child in value.items():
            yield from _paths(child, prefix + (key,))
    elif isinstance(value, list):
        yield prefix
        for index, child in enumerate(value):
            yield from _paths(child, prefix + (index,))
    else:
        yield prefix


def _parent(value: Any, path: tuple[PathPart, ...]) -> tuple[Any, PathPart]:
    current = value
    for part in path[:-1]:
        current = current[part]
    return current, path[-1]


def hostile_mutations(contract: dict[str, Any]) -> Iterator[dict[str, Any]]:
    for path in list(_paths(contract)):
        if not path:
            continue
        parent, key = _parent(contract, path)
        value = parent[key]
        if isinstance(value, dict):
            mutated = deepcopy(contract)
            target, target_key = _parent(mutated, path)
            target[target_key]["__unexpected__"] = True
            yield mutated
            for child_key in value:
                mutated = deepcopy(contract)
                target, target_key = _parent(mutated, path)
                del target[target_key][child_key]
                yield mutated
        elif isinstance(value, list):
            mutated = deepcopy(contract)
            target, target_key = _parent(mutated, path)
            target[target_key].append("__unexpected__")
            yield mutated
            if value:
                mutated = deepcopy(contract)
                target, target_key = _parent(mutated, path)
                target[target_key].pop()
                yield mutated
        elif isinstance(value, bool):
            mutated = deepcopy(contract)
            target, target_key = _parent(mutated, path)
            target[target_key] = not value
            yield mutated
        elif isinstance(value, int):
            for replacement in (value + 1, value - 1):
                mutated = deepcopy(contract)
                target, target_key = _parent(mutated, path)
                target[target_key] = replacement
                yield mutated
        elif isinstance(value, str):
            for replacement in (value + "__mutated", "__mutated__"):
                mutated = deepcopy(contract)
                target, target_key = _parent(mutated, path)
                target[target_key] = replacement
                yield mutated


def _hostile_evidence(
    contract: dict[str, Any], schema: dict[str, Any]
) -> dict[str, int]:
    count = 0
    escapes = 0
    for mutated in hostile_mutations(contract):
        count += 1
        try:
            validate_contract(mutated, schema, normative=contract)
        except (jsonschema.ValidationError, ValueError):
            continue
        escapes += 1
    if count < contract["scenario_profile"]["minimum_hostile_contract_mutations"]:
        raise ValueError("insufficient hostile mutations")
    if escapes:
        raise ValueError("hostile contract mutation escaped")
    return {"count": count, "escapes": escapes}


def build_evidence() -> dict[str, Any]:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    source_count = _source_bindings(contract)
    validate_contract(contract, schema)
    evaluator = _run_evaluator_scenarios()
    transitions = _run_transition_scenarios()
    commands = _run_command_scenarios()
    hostile = _hostile_evidence(contract, schema)
    total_scenarios = (
        evaluator["count"]
        + transitions["record_matrix_count"]
        + transitions["kill_switch_count"]
        + commands["count"]
        + 1
    )
    if total_scenarios < contract["scenario_profile"]["minimum_total_scenarios"]:
        raise ValueError("insufficient named scenarios")
    return {
        "schema_version": "emr4.check-in-admission-kernel-rehearsal-evidence.v1",
        "status": "passed",
        "result": contract["result"],
        "source_head": contract["source_head"],
        "source_binding_count": source_count,
        "canonical_active_ordinary_record_count": 0,
        "ordinary_admission_release_count": 0,
        "evaluator": evaluator,
        "transitions": transitions,
        "commands": commands,
        "total_scenario_count": total_scenarios,
        "hostile_contract_mutations": hostile,
        "product_or_configuration_changed": False,
        "provider_or_network_used": False,
        "live_clockwork_adopted": False,
        "reasons": [],
    }


def _render_report(evidence: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Provider-free unmounted check-in admission-control kernel rehearsal report",
            "",
            f"Status: `{evidence['status']}`",
            "",
            f"Source HEAD: `{evidence['source_head']}`",
            "",
            f"Source bindings: {evidence['source_binding_count']}",
            "",
            f"Named scenarios: {evidence['total_scenario_count']}",
            "",
            f"Evaluator scenarios: {evidence['evaluator']['count']}",
            "",
            f"Record transition matrix: {evidence['transitions']['record_matrix_count']}",
            "",
            f"Command scenarios: {evidence['commands']['count']}",
            "",
            f"Hostile contract mutations: {evidence['hostile_contract_mutations']['count']}",
            "",
            "Hostile escapes: 0",
            "",
            "Canonical active ordinary records: 0",
            "",
            "Ordinary admission releases: 0",
            "",
            "Only the authored-synthetic lane may release admission. The kill switch",
            "dominates both lanes, executable transitions never produce active,",
            "withdrawal is disable-only, unknown commit releases no success, and the",
            "Ariadne/DeepSeek shared clock remains shadow-only.",
            "",
        ]
    )


def main() -> int:
    evidence = build_evidence()
    _write(EVIDENCE, evidence)
    REPORT.write_text(_render_report(evidence), encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

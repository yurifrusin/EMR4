from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_check_in_relay_free_recovery_attempt_007 as attempt,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal
    as base,
)


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-"
    "and-cleanup-projection-coordinate-diagnosis"
)
TOPIC = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = TOPIC / "contract.json"
SCHEMA_PATH = TOPIC / "diagnosis-evidence.schema.json"
EVIDENCE_PATH = TOPIC / "diagnosis-evidence.json"

PLAN_SOURCE = "3240c0a00dcce1ea9c07907a1d67b2493c8f33ed"
ACCEPTED_OCCUPIED_SOURCE = "b7c37a76c41d399c4b198d3ab6b526c5510b434b"
ACCEPTED_TERMINAL_SOURCE = "6657ee5061265d732096e9987f327d82feed800c"
PROTECTED_SOURCE = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PASS_RESULT = (
    "raisa_provider_free_read_only_check_in_attempt_007_redaction_cleanup_"
    "projection_coordinate_diagnosis_pass"
)
COORDINATE_VOCABULARY = (
    "prospective_success_projection_forbidden_field",
    "post_cleanup_result_redaction_escape",
    "wrapper_untyped_post_finalization_cleanup_collapse",
    "insufficient_closed_evidence",
)
EXPECTED_CONFLICT = (
    "closed_boundaries.live_secret_existing_hosted_or_product_database_used"
)

BASE_SOURCE = (
    ROOT
    / "scripts"
    / "raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_"
    "rollback_unknown_commit_recovery_rehearsal.py"
)
WRAPPER_SOURCE = (
    ROOT / "scripts" / "raisa_provider_free_check_in_relay_free_recovery_attempt_007.py"
)
BASE_CONTRACT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-"
    "rollback-unknown-commit-recovery-rehearsal"
    / "contract.json"
)
TERMINAL_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-check-in-relay-free-recovery-attempt-007"
)
FAILURE_PATH = TERMINAL_DIR / "rehearsal-failure-evidence.json"
ENVELOPE_PATH = TERMINAL_DIR / "attempt-007-execution-envelope.json"
ENVELOPE_SCHEMA_PATH = TERMINAL_DIR / "attempt-007-execution-envelope.schema.json"

SOURCE_BINDINGS = {
    "docs/raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis-plan.md": "fc66d153a42a5a8025d9c1ac46a8f43302ffc52a1bc4f4d3799aec7d2ef68e09",
    "docs/security/raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis-threat-model-delta.md": "eb6ffc1bf6f96872207bc0f7993ed06008a8113e80305d475f0cdfab44205e2f",
    "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py": "1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16",
    "scripts/raisa_provider_free_check_in_relay_free_recovery_attempt_007.py": "ed7d84993d3b89037db09d0af2e7a0de32b0fb00c5da01a00731d100dcc14295",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/contract.json": "bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2",
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/attempt-007-execution-envelope.schema.json": "4c62319a372a96897add7908159510b269ffca7f2a19d4f98facf03020d186c5",
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/rehearsal-failure-evidence.json": "86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422",
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/attempt-007-execution-envelope.json": "3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class DiagnosisError(RuntimeError):
    pass


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DiagnosisError(f"expected_object_{path.name}")
    return value


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    head = result.stdout.strip()
    if HEX40.fullmatch(head) is None:
        raise DiagnosisError("head_not_full_git_object")
    return head


def _assert_ancestor(source: str, head: str) -> None:
    if HEX40.fullmatch(source) is None:
        raise DiagnosisError("source_not_full_git_object")
    relation = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, head],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if relation.returncode != 0:
        raise DiagnosisError("source_not_ancestor")


def _binding_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if path == ROOT or ROOT not in path.parents or path.is_symlink() or not path.is_file():
        raise DiagnosisError("source_binding_path_invalid")
    return path


def _validate_contract(contract: Mapping[str, Any], head: str) -> None:
    expected_keys = {
        "schema_version",
        "operation_id",
        "result",
        "plan_source",
        "accepted_occupied_source",
        "accepted_terminal_source",
        "protected_source",
        "coordinate_vocabulary",
        "expected_conflict_paths",
        "expected_terminal",
        "source_bindings",
        "repair_gears",
        "closed_boundaries",
    }
    if set(contract) != expected_keys:
        raise DiagnosisError("contract_key_set_invalid")
    if contract["schema_version"] != "emr4.check-in-attempt-007-redaction-cleanup-diagnosis-contract.v1":
        raise DiagnosisError("contract_schema_invalid")
    expected_scalars = {
        "operation_id": OPERATION_ID,
        "result": PASS_RESULT,
        "plan_source": PLAN_SOURCE,
        "accepted_occupied_source": ACCEPTED_OCCUPIED_SOURCE,
        "accepted_terminal_source": ACCEPTED_TERMINAL_SOURCE,
        "protected_source": PROTECTED_SOURCE,
    }
    if any(contract.get(key) != value for key, value in expected_scalars.items()):
        raise DiagnosisError("contract_authority_binding_invalid")
    if tuple(contract["coordinate_vocabulary"]) != COORDINATE_VOCABULARY:
        raise DiagnosisError("coordinate_vocabulary_invalid")
    if contract["expected_conflict_paths"] != [EXPECTED_CONFLICT]:
        raise DiagnosisError("expected_conflict_invalid")
    if contract["expected_terminal"] != {
        "stage": "redaction",
        "code": "forbidden_field",
        "cleanup_status": "not_started",
        "occupied_execution_count": 1,
        "automatic_retry_count": 0,
    }:
        raise DiagnosisError("expected_terminal_invalid")
    if contract["repair_gears"] != [
        "prospective_success_projection_static_gate",
        "typed_post_finalization_terminal_bridge",
    ]:
        raise DiagnosisError("repair_gears_invalid")
    if not isinstance(contract["closed_boundaries"], dict) or any(
        contract["closed_boundaries"].values()
    ):
        raise DiagnosisError("closed_boundary_open")
    bindings = contract["source_bindings"]
    expected_bindings = [
        {"source_file": source_file, "sha256": digest}
        for source_file, digest in SOURCE_BINDINGS.items()
    ]
    if bindings != expected_bindings:
        raise DiagnosisError("source_bindings_invalid")
    for source_file, digest in SOURCE_BINDINGS.items():
        if HEX64.fullmatch(digest) is None or _sha256(_binding_path(source_file)) != digest:
            raise DiagnosisError("source_binding_drift")
    for source in (PLAN_SOURCE, ACCEPTED_OCCUPIED_SOURCE, ACCEPTED_TERMINAL_SOURCE, PROTECTED_SOURCE):
        _assert_ancestor(source, head)


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    found = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(found) != 1:
        raise DiagnosisError(f"function_shape_invalid_{name}")
    return found[0]


def _assigned_dict(function: ast.FunctionDef, name: str) -> ast.Dict:
    found: list[ast.Dict] = []
    for node in ast.walk(function):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            if isinstance(node.value, ast.Dict):
                found.append(node.value)
    if len(found) != 1:
        raise DiagnosisError(f"assigned_dict_shape_invalid_{name}")
    return found[0]


def _dict_paths(node: ast.Dict, prefix: str = "") -> set[str]:
    paths: set[str] = set()
    for key, value in zip(node.keys, node.values, strict=True):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            raise DiagnosisError("nonliteral_evidence_key")
        current = f"{prefix}.{key.value}" if prefix else key.value
        paths.add(current)
        if isinstance(value, ast.Dict):
            paths.update(_dict_paths(value, current))
    return paths


def _return_dict(function: ast.FunctionDef) -> ast.Dict:
    returns = [node.value for node in ast.walk(function) if isinstance(node, ast.Return)]
    if len(returns) != 1 or not isinstance(returns[0], ast.Dict):
        raise DiagnosisError("return_dict_shape_invalid")
    return returns[0]


def prospective_result_key_paths(source: str, contract: Mapping[str, Any]) -> tuple[str, ...]:
    tree = ast.parse(source)
    rehearsal = _function(tree, "run_rehearsal")
    paths = _dict_paths(_assigned_dict(rehearsal, "result"))

    try_nodes = [node for node in rehearsal.body if isinstance(node, ast.Try) and node.finalbody]
    if len(try_nodes) != 1:
        raise DiagnosisError("rehearsal_try_shape_invalid")
    finalizer_module = ast.Module(body=try_nodes[0].finalbody, type_ignores=[])
    finalizer_function = ast.FunctionDef(
        name="finalizer",
        args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=finalizer_module.body,
        decorator_list=[],
    )
    cleanup_paths = _dict_paths(_assigned_dict(finalizer_function, "cleanup"), "cleanup")
    paths.update(cleanup_paths)

    scenario = _function(tree, "_scenario")
    paths.update(_dict_paths(_return_dict(scenario), "scenarios[]"))

    closed = contract.get("closed_boundaries")
    if not isinstance(closed, dict) or len(closed) != 10:
        raise DiagnosisError("closed_boundaries_shape_invalid")
    paths.update(f"closed_boundaries.{key}" for key in closed)
    return tuple(sorted(paths))


def _key_conflicts(key: str) -> bool:
    lowered = key.lower()
    return lowered in base.FORBIDDEN_EVIDENCE_KEYS or any(
        f"{part}_" in lowered or lowered.endswith(f"_{part}")
        for part in base.FORBIDDEN_EVIDENCE_KEYS
    )


def conflict_paths(paths: Sequence[str]) -> tuple[str, ...]:
    return tuple(path for path in paths if _key_conflicts(path.rsplit(".", 1)[-1]))


def reproduce_redaction(contract: Mapping[str, Any]) -> dict[str, str]:
    try:
        base._assert_redacted(
            {"closed_boundaries": contract["closed_boundaries"]},
            forbidden_values=(),
        )
    except base.RehearsalFailure as error:
        return {"stage": error.stage, "code": error.code}
    raise DiagnosisError("redaction_conflict_not_reproduced")


def base_control_flow(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    rehearsal = _function(tree, "run_rehearsal")
    tries = [node for node in rehearsal.body if isinstance(node, ast.Try) and node.finalbody]
    if len(tries) != 1:
        raise DiagnosisError("base_try_shape_invalid")
    lifecycle_try = tries[0]
    result_dict = _assigned_dict(rehearsal, "result")
    result_inside = any(node is result_dict for statement in lifecycle_try.body for node in ast.walk(statement))
    cleanup_in_finally = any(
        isinstance(node, (ast.Assign, ast.AnnAssign))
        and any(
            isinstance(target, ast.Name) and target.id == "cleanup"
            for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
        )
        and isinstance(node.value, ast.Dict)
        for statement in lifecycle_try.finalbody
        for node in ast.walk(statement)
    )
    try_index = rehearsal.body.index(lifecycle_try)
    redaction_indexes = []
    for index, statement in enumerate(rehearsal.body):
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if (
            isinstance(call.func, ast.Name)
            and call.func.id == "_assert_redacted"
            and call.args
            and isinstance(call.args[0], ast.Name)
            and call.args[0].id == "result"
        ):
            redaction_indexes.append(index)
    if len(redaction_indexes) != 1:
        raise DiagnosisError("final_redaction_shape_invalid")
    redaction_index = redaction_indexes[0]
    facts = {
        "result_constructed_inside_lifecycle_try": result_inside,
        "cleanup_finalized_in_finally": cleanup_in_finally,
        "final_result_redaction_after_finally": redaction_index > try_index,
        "base_handler_covers_final_result_redaction": False,
        "lifecycle_try_statement_index": try_index,
        "final_result_redaction_statement_index": redaction_index,
    }
    if not all(
        facts[key]
        for key in (
            "result_constructed_inside_lifecycle_try",
            "cleanup_finalized_in_finally",
            "final_result_redaction_after_finally",
        )
    ):
        raise DiagnosisError("base_control_flow_not_admitted")
    return facts


def wrapper_projection(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    sanitizer = _function(tree, "_sanitized_failure")
    returned = [node.value for node in ast.walk(sanitizer) if isinstance(node, ast.Return)]
    if len(returned) != 1 or not isinstance(returned[0], ast.Call) or len(returned[0].args) != 3:
        raise DiagnosisError("sanitizer_shape_invalid")
    cleanup_arg = returned[0].args[2]
    if not isinstance(cleanup_arg, ast.Dict) or len(cleanup_arg.keys) != 1:
        raise DiagnosisError("sanitizer_cleanup_shape_invalid")
    key = cleanup_arg.keys[0]
    value = cleanup_arg.values[0]
    if not (
        isinstance(key, ast.Constant)
        and key.value == "status"
        and isinstance(value, ast.Constant)
        and value.value == "not_started"
    ):
        raise DiagnosisError("sanitizer_cleanup_value_invalid")

    writer = _function(tree, "_write_failure_if_absent")
    writer_calls_sanitizer = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_sanitized_failure"
        for node in ast.walk(writer)
    )
    run_attempt = _function(tree, "run_attempt")
    caught_forwarded = any(
        isinstance(node, ast.ExceptHandler)
        and isinstance(node.type, ast.Attribute)
        and node.type.attr == "RehearsalFailure"
        and any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == "_write_failure_if_absent"
            for child in ast.walk(node)
        )
        for node in ast.walk(run_attempt)
    )
    projected = attempt._sanitized_failure(
        base.RehearsalFailure("redaction", "forbidden_field")
    )
    cleanup = projected.get("cleanup")
    if not writer_calls_sanitizer or not caught_forwarded or cleanup != {"status": "not_started"}:
        raise DiagnosisError("wrapper_projection_not_admitted")
    return {
        "caught_base_failure_forwarded_to_writer": caught_forwarded,
        "writer_calls_sanitizer": writer_calls_sanitizer,
        "sanitizer_cleanup_status": cleanup["status"],
        "fake_stage": projected.get("stage"),
        "fake_code": projected.get("code"),
    }


def build_evidence(contract: Mapping[str, Any], head: str) -> dict[str, Any]:
    _validate_contract(contract, head)
    base_contract = _load_json(BASE_CONTRACT)
    terminal = _load_json(FAILURE_PATH)
    envelope = _load_json(ENVELOPE_PATH)
    schema_errors = list(
        Draft202012Validator(_load_json(ENVELOPE_SCHEMA_PATH)).iter_errors(envelope)
    )
    if schema_errors:
        raise DiagnosisError("immutable_envelope_schema_invalid")
    expected_terminal = contract["expected_terminal"]
    terminal_projection = {
        "stage": terminal.get("stage"),
        "code": terminal.get("code"),
        "cleanup_status": (terminal.get("cleanup") or {}).get("status"),
        "occupied_execution_count": envelope.get("occupied_execution_count"),
        "automatic_retry_count": envelope.get("automatic_retry_count"),
    }
    if terminal_projection != expected_terminal:
        raise DiagnosisError("immutable_terminal_projection_invalid")
    if envelope.get("source_head") != ACCEPTED_OCCUPIED_SOURCE:
        raise DiagnosisError("occupied_source_binding_invalid")

    paths = prospective_result_key_paths(BASE_SOURCE.read_text(encoding="utf-8"), base_contract)
    conflicts = conflict_paths(paths)
    if list(conflicts) != contract["expected_conflict_paths"]:
        raise DiagnosisError("prospective_conflict_set_invalid")
    predicate = reproduce_redaction(base_contract)
    if predicate != {"stage": "redaction", "code": "forbidden_field"}:
        raise DiagnosisError("redaction_terminal_mismatch")
    control = base_control_flow(BASE_SOURCE.read_text(encoding="utf-8"))
    wrapper = wrapper_projection(WRAPPER_SOURCE.read_text(encoding="utf-8"))

    evidence: dict[str, Any] = {
        "schema_version": "emr4.check-in-attempt-007-redaction-cleanup-diagnosis-evidence.v1",
        "operation_id": OPERATION_ID,
        "result": PASS_RESULT,
        "source_head": head,
        "plan_source": PLAN_SOURCE,
        "accepted_terminal_source": ACCEPTED_TERMINAL_SOURCE,
        "input_bindings_verified": True,
        "immutable_terminal": {
            **terminal_projection,
            "failure_sha256": SOURCE_BINDINGS[str(FAILURE_PATH.relative_to(ROOT)).replace('\\', '/')],
            "envelope_sha256": SOURCE_BINDINGS[str(ENVELOPE_PATH.relative_to(ROOT)).replace('\\', '/')],
            "transaction_attestation_present": False,
            "success_evidence_present": False,
        },
        "prospective_projection": {
            "key_path_count": len(paths),
            "key_path_set_sha256": hashlib.sha256(_canonical_bytes({"key_paths": list(paths)})).hexdigest(),
            "conflict_count": len(conflicts),
            "conflict_paths": list(conflicts),
            "predicate_stage": predicate["stage"],
            "predicate_code": predicate["code"],
            "coordinate": "prospective_success_projection_forbidden_field",
        },
        "base_control_flow": {
            **control,
            "coordinate": "post_cleanup_result_redaction_escape",
        },
        "wrapper_projection": {
            **wrapper,
            "coordinate": "wrapper_untyped_post_finalization_cleanup_collapse",
        },
        "repair_boundary": {
            "gears": contract["repair_gears"],
            "forbidden_field_predicate_weakened": False,
            "closed_boundary_default_denial_preserved": True,
            "attempt_008_authorized": False,
        },
        "activity": {
            "docker_object_commands": 0,
            "postgresql_processes_started": 0,
            "sql_executions": 0,
            "database_operations": 0,
            "provider_requests": 0,
            "product_effects": 0,
        },
        "claim_boundary": {
            "transaction_semantics": "unproved",
            "role_absence_before_teardown": "unproved",
            "internal_cleanup_history": "unproved",
            "external_owned_docker_resource_absence": "accepted_predecessor_evidence_only",
            "future_repair": "selected_not_implemented",
        },
    }
    validation_errors = list(
        Draft202012Validator(_load_json(SCHEMA_PATH)).iter_errors(evidence)
    )
    if validation_errors:
        raise DiagnosisError("diagnosis_evidence_schema_invalid")
    base._assert_redacted(evidence, forbidden_values=())
    return evidence


def _write_exclusive(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(_canonical_bytes(value))


def _evidence_binding_head(current_head: str) -> str:
    if not EVIDENCE_PATH.exists():
        return current_head
    existing = _load_json(EVIDENCE_PATH)
    bound_head = existing.get("source_head")
    if not isinstance(bound_head, str) or HEX40.fullmatch(bound_head) is None:
        raise DiagnosisError("existing_evidence_source_not_full_git_object")
    _assert_ancestor(bound_head, current_head)
    return bound_head


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        contract = _load_json(CONTRACT_PATH)
        current_head = _git_head()
        evidence = build_evidence(contract, _evidence_binding_head(current_head))
        if arguments.execute:
            _write_exclusive(EVIDENCE_PATH, evidence)
        elif EVIDENCE_PATH.exists() and EVIDENCE_PATH.read_bytes() != _canonical_bytes(evidence):
            raise DiagnosisError("existing_evidence_noncanonical_or_drifted")
    except (DiagnosisError, base.RehearsalFailure, FileExistsError) as error:
        print(json.dumps({"result": "failed_closed", "code": str(error)}))
        return 1
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

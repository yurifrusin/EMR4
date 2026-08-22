"""Verify the provider-free prospective-redaction and typed-terminal repair."""

from __future__ import annotations

import argparse
import ast
import copy
import dataclasses
import hashlib
import json
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, NoReturn

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import raisa_provider_free_check_in_relay_free_recovery_attempt_007 as attempt
from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal as base,
)

TOPIC = ROOT / (
    "orchestration/continuity/raisa-provider-free-check-in-prospective-success-"
    "redaction-and-typed-cleanup-projection-conformance-repair"
)
CONTRACT_PATH = TOPIC / "repair-contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "repair-contract.schema.json"
EVIDENCE_SCHEMA_PATH = TOPIC / "repair-evidence.schema.json"
EVIDENCE_PATH = TOPIC / "repair-evidence.json"
BASE_RELATIVE = (
    "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_"
    "relay_free_rollback_unknown_commit_recovery_rehearsal.py"
)
BASE_CONTRACT_RELATIVE = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/"
    "contract.json"
)
ATTEMPT_FAILURE = ROOT / (
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-"
    "attempt-007/rehearsal-failure-evidence.json"
)
ATTEMPT_ENVELOPE = ROOT / (
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-"
    "attempt-007/attempt-007-execution-envelope.json"
)
EXPECTED_FAILURE_SHA256 = (
    "86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422"
)
EXPECTED_ENVELOPE_SHA256 = (
    "3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5"
)


class RepairConformanceError(RuntimeError):
    pass


def _fail(code: str) -> NoReturn:
    raise RepairConformanceError(code)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        _fail("json_root_not_object")
    return value


def _git(*arguments: str, binary: bool = False) -> str | bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=not binary,
        timeout=30,
        shell=False,
    )
    if completed.returncode != 0:
        _fail("git_command_failed")
    return completed.stdout


def _assert_ancestor(source: str, head: str) -> None:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, head],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False,
    )
    if completed.returncode != 0:
        _fail("git_ancestry_invalid")


def _function_dump(source: str, name: str) -> str:
    tree = ast.parse(source)
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(matches) != 1:
        _fail("function_shape_invalid")
    return ast.dump(matches[0], include_attributes=False)


def _assignment_dump(source: str, name: str) -> str:
    tree = ast.parse(source)
    matches = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == name
            for target in node.targets
        )
    ]
    if len(matches) != 1:
        _fail("assignment_shape_invalid")
    return ast.dump(matches[0], include_attributes=False)


def _cleanup(status: str) -> dict[str, Any]:
    return {
        "role_absent_before_teardown": status == "cleanup_verified",
        "attachments_absent": True,
        "sidecars_absent": True,
        "server_absent": True,
        "network_absent": True,
        "matching_owned_resources": 0,
        "status": status,
    }


@contextmanager
def _bound_terminal_paths(root: Path) -> Iterator[None]:
    originals = (base.FAILURE_PATH, base.EVIDENCE_PATH, base.ATTESTATION_PATH)
    base.FAILURE_PATH = root / "failure.json"
    base.EVIDENCE_PATH = root / "evidence.json"
    base.ATTESTATION_PATH = root / "attestation.json"
    try:
        yield
    finally:
        base.FAILURE_PATH, base.EVIDENCE_PATH, base.ATTESTATION_PATH = originals


def _terminal_case(
    *,
    kind: str,
    root: Path,
    contract: dict[str, Any],
    source_head: str,
) -> tuple[base.PostFinalizationTerminal, Path]:
    root.mkdir(parents=True)
    candidate = base._prospective_success_evidence_projection(contract, source_head)
    error: base.RehearsalFailure | None = None
    lifecycle = ["cleanup_finalized"]
    forbidden_values: tuple[str, ...] = ()
    cleanup = _cleanup("cleanup_verified")
    if kind == "redaction":
        candidate["secret_material"] = False
    elif kind == "schema":
        candidate["source_binding_count"] = 14
    elif kind == "fallback":
        error = base.RehearsalFailure("execution", "bounded_failure")
        candidate = None
        lifecycle = ["contains-sensitive-token"]
        forbidden_values = ("sensitive-token",)
        cleanup = _cleanup("cleanup_incomplete")
    elif kind != "success":
        _fail("terminal_case_invalid")
    with _bound_terminal_paths(root):
        terminal = base._finalize_post_cleanup_terminal(
            error=error,
            result=candidate,
            attestation={"bounded": True} if candidate is not None else None,
            lifecycle=lifecycle,
            cleanup=cleanup,
            elapsed_seconds=1.0,
            forbidden_values=forbidden_values,
        )
        terminal_path = (
            base.EVIDENCE_PATH
            if terminal.attestation is not None
            else base.FAILURE_PATH
        )
        if not terminal_path.exists():
            _fail("terminal_artifact_missing")
    return terminal, terminal_path


def _terminal_reading(contract: dict[str, Any], source_head: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="emr4-checkin-terminal-repair-") as raw:
        root = Path(raw)
        redaction, redaction_path = _terminal_case(
            kind="redaction", root=root / "redaction", contract=contract, source_head=source_head
        )
        schema, _ = _terminal_case(
            kind="schema", root=root / "schema", contract=contract, source_head=source_head
        )
        fallback, fallback_path = _terminal_case(
            kind="fallback", root=root / "fallback", contract=contract, source_head=source_head
        )
        success, _ = _terminal_case(
            kind="success", root=root / "success", contract=contract, source_head=source_head
        )
        envelope = attempt._build_execution_envelope(
            source_head=source_head,
            evidence=redaction.evidence,
            terminal_path=redaction_path,
            terminal_kind="rehearsal_failure_evidence",
        )
        if "sensitive-token" in fallback_path.read_text(encoding="utf-8"):
            _fail("failure_evidence_value_leak")
        expected = {
            "redaction": ("redaction", "forbidden_field", "cleanup_verified"),
            "schema": ("evidence", "parent_schema_invalid", "cleanup_verified"),
            "fallback": ("redaction", "failure_evidence_rejected", "cleanup_incomplete"),
        }
        for name, terminal in (
            ("redaction", redaction),
            ("schema", schema),
            ("fallback", fallback),
        ):
            stage, code, cleanup_status = expected[name]
            if (
                terminal.attestation is not None
                or terminal.evidence.get("stage") != stage
                or terminal.evidence.get("code") != code
                or terminal.evidence.get("cleanup", {}).get("status")
                != cleanup_status
            ):
                _fail(f"{name}_terminal_invalid")
        if (
            success.attestation is None
            or success.evidence.get("result") != base.PASS_RESULT
            or success.evidence.get("cleanup", {}).get("status")
            != "cleanup_verified"
        ):
            _fail("success_terminal_invalid")
        if envelope.get("cleanup_status") != "cleanup_verified":
            _fail("wrapper_cleanup_projection_invalid")
    return {
        "frozen_dataclass": bool(
            dataclasses.is_dataclass(base.PostFinalizationTerminal)
            and base.PostFinalizationTerminal.__dataclass_params__.frozen
        ),
        "redaction_failure_cleanup": "cleanup_verified",
        "schema_failure_cleanup": "cleanup_verified",
        "failure_fallback_cleanup": "cleanup_incomplete",
        "success_cleanup": "cleanup_verified",
        "wrapper_cleanup_projection": "cleanup_verified",
        "late_failure_escape_count": 0,
        "success_release_after_late_failure_count": 0,
    }


def _validate_contract(contract: dict[str, Any], head: str) -> None:
    schema = _load_json(CONTRACT_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    if list(Draft202012Validator(schema).iter_errors(contract)):
        _fail("repair_contract_schema_invalid")
    if any(contract["closed_boundaries"].values()):
        _fail("repair_closed_boundary_open")
    for source in (
        contract["plan_source"],
        contract["accepted_diagnosis_source"],
        contract["accepted_diagnosis_closeout_source"],
        contract["protected_source"],
    ):
        _assert_ancestor(source, head)


def build_evidence() -> dict[str, Any]:
    head = str(_git("rev-parse", "HEAD")).strip()
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, head)
    base_source = Path(base.__file__).read_text(encoding="utf-8")
    historical_source = str(
        _git("show", f"{contract['accepted_diagnosis_source']}:{BASE_RELATIVE}")
    )
    if Path(base.__file__).read_bytes() != _git("show", f"HEAD:{BASE_RELATIVE}", binary=True):
        _fail("base_source_not_bound_to_head")
    if base.CONTRACT_PATH.read_bytes() != _git(
        "show", f"HEAD:{BASE_CONTRACT_RELATIVE}", binary=True
    ):
        _fail("base_contract_not_bound_to_head")
    redactor_unchanged = (
        _function_dump(base_source, "_assert_redacted")
        == _function_dump(historical_source, "_assert_redacted")
        and _assignment_dump(base_source, "FORBIDDEN_EVIDENCE_KEYS")
        == _assignment_dump(historical_source, "FORBIDDEN_EVIDENCE_KEYS")
    )
    if not redactor_unchanged:
        _fail("redactor_drift")
    base_contract = _load_json(base.CONTRACT_PATH)
    safe_key = contract["safe_boundary_key"]
    retired_key = contract["retired_conflicting_boundary_key"]
    if (
        safe_key not in base_contract["closed_boundaries"]
        or retired_key in base_contract["closed_boundaries"]
        or len(base_contract["closed_boundaries"]) != 10
        or any(base_contract["closed_boundaries"].values())
    ):
        _fail("boundary_repair_invalid")
    tree = ast.parse(base_source)
    run = base._ast_function(tree, "run_rehearsal")
    calls = [
        node.func.id
        for node in ast.walk(run)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    before_docker = calls.index("static_check") < calls.index("_docker_executable")
    static = base.static_check()
    projection = dict(static["prospective_projection"])
    projection["before_docker_capable_call"] = before_docker
    if projection["path_count"] != contract["expected_projection_path_count"]:
        _fail("projection_path_count_invalid")
    if projection["hostile_rejected"] != contract["expected_hostile_projection_mutations"]:
        _fail("projection_hostile_count_invalid")
    evidence = {
        "schema_version": "emr4.check-in-prospective-success-redaction-typed-cleanup-projection-repair-evidence.v1",
        "result": contract["result"],
        "source_head": head,
        "plan_source": contract["plan_source"],
        "accepted_diagnosis_source": contract["accepted_diagnosis_source"],
        "accepted_diagnosis_closeout_source": contract[
            "accepted_diagnosis_closeout_source"
        ],
        "protected_source": contract["protected_source"],
        "source_digests": {
            "base_harness_sha256": _sha256(Path(base.__file__)),
            "base_contract_sha256": _sha256(base.CONTRACT_PATH),
            "repair_contract_sha256": _sha256(CONTRACT_PATH),
        },
        "prospective_projection": projection,
        "boundary_repair": {
            "safe_key_present": True,
            "retired_key_absent": True,
            "boundary_count": 10,
            "all_default_denied": True,
            "redactor_ast_unchanged": redactor_unchanged,
        },
        "typed_terminal": _terminal_reading(base_contract, head),
        "immutable_attempt_007": {
            "failure_sha256": _sha256(ATTEMPT_FAILURE),
            "envelope_sha256": _sha256(ATTEMPT_ENVELOPE),
            "retry_count": 0,
            "reclassified": False,
        },
        "efficacy": {
            "diagnosed_forbidden_field_occupied_escape_before": 1,
            "diagnosed_forbidden_field_occupied_escape_after": 0,
            "diagnosed_cleanup_collapse_before": 1,
            "diagnosed_cleanup_collapse_after": 0,
            "occupied_runs_used_for_repair": 0,
        },
        "activity_counts": {
            "docker_objects": 0,
            "postgresql_starts": 0,
            "sql_executions": 0,
            "database_operations": 0,
            "provider_calls": 0,
            "product_calls": 0,
            "attempt_008_actions": 0,
        },
        "closed_boundaries": copy.deepcopy(contract["closed_boundaries"]),
    }
    if evidence["immutable_attempt_007"] != {
        "failure_sha256": EXPECTED_FAILURE_SHA256,
        "envelope_sha256": EXPECTED_ENVELOPE_SHA256,
        "retry_count": 0,
        "reclassified": False,
    }:
        _fail("attempt_007_artifact_drift")
    evidence_schema = _load_json(EVIDENCE_SCHEMA_PATH)
    Draft202012Validator.check_schema(evidence_schema)
    if list(Draft202012Validator(evidence_schema).iter_errors(evidence)):
        _fail("repair_evidence_schema_invalid")
    base._assert_redacted(evidence, forbidden_values=())
    return evidence


def _write_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(_json_bytes(value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        evidence = build_evidence()
        if arguments.execute:
            _write_exclusive(EVIDENCE_PATH, evidence)
        print(
            json.dumps(
                {
                    "result": evidence["result"],
                    "projection_paths": evidence["prospective_projection"][
                        "path_count"
                    ],
                    "late_failure_escapes": evidence["typed_terminal"][
                        "late_failure_escape_count"
                    ],
                    "occupied_runs": evidence["efficacy"][
                        "occupied_runs_used_for_repair"
                    ],
                },
                indent=2,
            )
        )
        return 0
    except (OSError, ValueError, RepairConformanceError) as error:
        print(json.dumps({"result": "failed_closed", "code": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Reconcile the consumed complete-runner result without another process."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration_harness.git_object_resolution import resolve_commit_source
from orchestration_harness.git_refs_snapshot import build_git_refs_snapshot
from scripts import (
    deepseek_native_harness_provider_free_complete_package_unloaded_runner_evaluation_rehearsal
    as parent,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-complete-runner-result-contract-"
    "reconciliation"
)
PARENT_OPERATION_ID = parent.OPERATION_ID
OPERATION_ROOT = parent.OPERATION_ROOT
ADDENDUM_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-complete-package-unloaded-runner-"
    "evaluation-rehearsal-result-contract-reconciliation.md"
)
EVIDENCE_PATH = OPERATION_ROOT / "result-contract-reconciliation-evidence.json"
REPORT_PATH = OPERATION_ROOT / "result-contract-reconciliation-report.md"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "result-contract-reconciliation-evidence.schema.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_complete_runner_result_contract_reconciliation.py"
)
PARENT_CONTROLLER_PATH = Path(parent.__file__).resolve()
PARENT_ENVELOPE_PATH = parent.PROCESS_ENVELOPE_PATH
PARENT_FAILURE_PATH = parent.FAILURE_TERMINAL_PATH
EXPECTED_STDOUT_BYTES = 129
EXPECTED_STDOUT_SHA256 = "f868b3fff25a29d8bdd822e0675ffff1bb92363f20ac19bcaf674d85701df49a"
EXPECTED_SIDECAR_BYTES = 1567
EXPECTED_SIDECAR_SHA256 = "841881411f203dc5f02f5b785bb5aa3a754f8663517e0145d95fc1376e5ea1a3"
EXPECTED_PROTECTED_COMMIT = parent.EXPECTED_PROTECTED_COMMIT
PROTECTED_REFS = parent.PROTECTED_REFS
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
SCHEMA_VERSION = "ariadne.native_harness_complete_runner_result_contract_reconciliation.v1"
ADMITTED_RESULT = "complete_package_unloaded_runner_evaluation_reconciled_pass"


class ReconciliationError(RuntimeError):
    """An immutable reconciliation binding failed."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ReconciliationError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise ReconciliationError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: object, code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        raise ReconciliationError(code) from error


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    if completed.returncode != 0:
        raise ReconciliationError("git_resolution_failed")
    return completed.stdout.strip()


def fixture_wire_bytes() -> bytes:
    value = parent.exact_fixture_result()
    if list(value) != ["schema_version", "result", "app_exit_code"]:
        raise ReconciliationError("fixture_declared_order_rejected")
    wire = (json.dumps(value, separators=(",", ":")) + "\n").encode()
    if len(wire) != EXPECTED_STDOUT_BYTES or sha256_bytes(wire) != EXPECTED_STDOUT_SHA256:
        raise ReconciliationError("fixture_wire_binding_rejected")
    if sha256_bytes(parent.canonical_bytes(value)) == EXPECTED_STDOUT_SHA256:
        raise ReconciliationError("controller_order_defect_not_demonstrated")
    return wire


def sidecar_wire_bytes(candidate_source: str) -> bytes:
    if FULL_OID.fullmatch(candidate_source) is None:
        raise ReconciliationError("candidate_source_rejected")
    value = parent.expected_sidecar(candidate_source)
    wire = (json.dumps(value, separators=(",", ":")) + "\n").encode()
    if len(wire) != EXPECTED_SIDECAR_BYTES or sha256_bytes(wire) != EXPECTED_SIDECAR_SHA256:
        raise ReconciliationError("sidecar_wire_binding_rejected")
    return wire


def validate_consumed_attempt(
    envelope: dict[str, Any], failure: dict[str, Any], candidate_source: str
) -> dict[str, Any]:
    try:
        parent._validate(
            parent.PROCESS_ENVELOPE_SCHEMA_PATH,
            envelope,
            "parent_envelope_schema_rejected",
        )
        parent._validate(
            parent.FAILURE_TERMINAL_SCHEMA_PATH,
            failure,
            "parent_failure_schema_rejected",
        )
    except parent.CompleteRunnerError as error:
        raise ReconciliationError(str(error)) from error
    fixture_wire = fixture_wire_bytes()
    sidecar_wire = sidecar_wire_bytes(candidate_source)
    exact_envelope = {
        "candidate_source": candidate_source,
        "numeric_exit_code": 0,
        "stdout_bytes": len(fixture_wire),
        "stdout_sha256": sha256_bytes(fixture_wire),
        "stderr_bytes": 0,
        "stderr_sha256": sha256_bytes(b""),
        "sidecar_present_before_cleanup": True,
        "sidecar_bytes": len(sidecar_wire),
        "sidecar_sha256": sha256_bytes(sidecar_wire),
        "stream_and_sidecar_content_retained_before_envelope": False,
        "raw_runtime_detail_retained": False,
        "fixture_root_absent": True,
        "installed_package_import_count": 0,
        "node_process_count": 1,
        "native_harness_process_count": 0,
        "worker_model_provider_process_count": 0,
        "further_process_authorized": False,
    }
    if any(envelope.get(key) != value for key, value in exact_envelope.items()):
        raise ReconciliationError("immutable_envelope_binding_rejected")
    if (
        failure.get("candidate_source") != candidate_source
        or failure.get("result") != "complete_runner_result_rejected"
        or failure.get("terminal")
        != {
            "stage": "complete_package_unloaded_runner",
            "code": "complete_runner_result_rejected",
            "detail": None,
        }
        or failure.get("process_envelope_sha256") != sha256_bytes(canonical_bytes(envelope))
        or failure.get("raw_runtime_detail_retained") is not False
        or failure.get("further_process_authorized") is not False
    ):
        raise ReconciliationError("immutable_failure_binding_rejected")
    return {
        "fixture_wire": {
            "bytes": len(fixture_wire),
            "sha256": sha256_bytes(fixture_wire),
            "declared_key_order": list(parent.exact_fixture_result()),
            "content_retained_from_process": False,
        },
        "sidecar_wire": {
            "bytes": len(sidecar_wire),
            "sha256": sha256_bytes(sidecar_wire),
            "declared_key_order": list(parent.expected_sidecar(candidate_source)),
            "content_retained_from_process": False,
        },
        "controller_defect": {
            "coordinate": "fixture_wire_key_order_comparison",
            "observed_wire_matches_declared_fixture_order": True,
            "generic_sorted_serializer_was_incorrect": True,
            "runner_process_failed": False,
        },
    }


def machine_git_bindings() -> dict[str, Any]:
    snapshot = build_git_refs_snapshot(
        repo_root=REPO_ROOT,
        expected_protected_commit=EXPECTED_PROTECTED_COMMIT,
        protected_refs=PROTECTED_REFS,
    )
    if snapshot["status"] != "passed" or snapshot["tracked_worktree_clean"] is not True or snapshot["branch_origin_aligned"] is not True or snapshot["protected_refs_aligned"] is not True:
        raise ReconciliationError("reconciliation_preflight_rejected")
    parent_observed = _git("log", "-1", "--format=%H", "--", PARENT_CONTROLLER_PATH.relative_to(REPO_ROOT).as_posix())
    reconciliation_observed = _git("log", "-1", "--format=%H", "--", Path(__file__).resolve().relative_to(REPO_ROOT).as_posix())
    parent_resolution = resolve_commit_source(repo_root=REPO_ROOT, source_head=parent_observed)
    reconciliation_resolution = resolve_commit_source(repo_root=REPO_ROOT, source_head=reconciliation_observed)
    if parent_resolution["status"] != "passed" or reconciliation_resolution["status"] != "passed":
        raise ReconciliationError("git_object_resolution_rejected")
    _git("merge-base", "--is-ancestor", parent_resolution["resolved_commit"], reconciliation_resolution["resolved_commit"])
    return {
        "policy": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
        "consumed_candidate_source": parent_resolution["resolved_commit"],
        "reconciliation_source": reconciliation_resolution["resolved_commit"],
        "consumed_candidate_is_ancestor_of_reconciliation": True,
        "branch": snapshot["branch"],
        "branch_origin_aligned": True,
        "protected_refs_aligned": True,
        "tracked_worktree_clean": True,
        "docs_branding_preserved": snapshot["preserved_untracked_paths"]["docs/branding"],
    }


def implementation_bindings() -> dict[str, str]:
    paths = {
        "reconciliation_addendum_sha256": ADDENDUM_PATH,
        "reconciliation_controller_sha256": Path(__file__).resolve(),
        "focused_test_sha256": FOCUSED_TEST_PATH,
        "evidence_schema_sha256": EVIDENCE_SCHEMA_PATH,
        "parent_controller_sha256": PARENT_CONTROLLER_PATH,
        "parent_contract_sha256": parent.CONTRACT_PATH,
        "parent_envelope_sha256": PARENT_ENVELOPE_PATH,
        "parent_failure_terminal_sha256": PARENT_FAILURE_PATH,
    }
    return {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}


def build_evidence(
    *, git_binding: dict[str, Any], reconciliation: dict[str, Any]
) -> dict[str, Any]:
    candidate = git_binding["consumed_candidate_source"]
    value = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "parent_operation_id": PARENT_OPERATION_ID,
        "result": ADMITTED_RESULT,
        "git_binding": git_binding,
        "implementation_bindings": implementation_bindings(),
        "immutable_parent_result": "complete_runner_result_rejected",
        "reconciliation": reconciliation,
        "fixture_result": parent.exact_fixture_result(),
        "runner_sidecar": parent.expected_sidecar(candidate),
        "process_boundary": {
            "consumed_node_process_count": 1,
            "reconciliation_process_count": 0,
            "retry_count": 0,
            "installed_package_import_count": 0,
            "native_harness_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "broker_process_count": 0,
            "broker_request_count": 0,
            "network_attempt_count": 0,
            "database_attempt_count": 0,
            "docker_attempt_count": 0,
            "target_creation_count": 0,
            "target_use_count": 0,
            "resume_count": 0,
        },
        "cleanup": {
            "fixture_root_absent": True,
            "raw_process_content_retained": False,
            "materialized_javascript_retained": False,
            "runner_sidecar_file_retained": False,
        },
        "claim_boundary": {
            "complete_package_unloaded_runner_reconciled": True,
            "runner_process_succeeded": True,
            "controller_postprocess_rejection_preserved": True,
            "hash_exact_preimages_derived_from_frozen_contract": True,
            "installed_package_loaded": False,
            "native_harness_proved": False,
            "worker_model_provider_executed": False,
            "retry_authorized": False,
            "product_authority": False,
        },
    }
    _validate(EVIDENCE_SCHEMA_PATH, value, "reconciliation_evidence_schema_rejected")
    return value


def render_report(evidence: dict[str, Any], timestamp: str) -> str:
    return f"""# Complete runner result-contract reconciliation report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **{evidence['result']}**

Consumed candidate source: `{evidence['git_binding']['consumed_candidate_source']}`

The one consumed Node process exited zero, emitted no stderr, produced the exact
declared 129-byte fixture wire hash and exact 1,567-byte runner sidecar hash,
and cleaned up completely. The immutable rejection is preserved. It resulted
solely from comparing the declared fixture key order with a sorted-key helper.

This process-free reconciliation launched nothing and performed no retry. The
complete package-unloaded runner composition is accepted; installed-package,
native-Harness, occupied-worker and model/provider behavior remain unproved.
"""


def reconcile() -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise ReconciliationError("reconciliation_output_not_fresh")
    git_binding = machine_git_bindings()
    envelope = _load_object(PARENT_ENVELOPE_PATH)
    failure = _load_object(PARENT_FAILURE_PATH)
    reconciliation = validate_consumed_attempt(
        envelope, failure, git_binding["consumed_candidate_source"]
    )
    evidence = build_evidence(git_binding=git_binding, reconciliation=reconciliation)
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    REPORT_PATH.write_text(
        render_report(evidence, datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()),
        encoding="utf-8",
    )
    return evidence


def check() -> dict[str, Any]:
    git_binding = machine_git_bindings()
    envelope = _load_object(PARENT_ENVELOPE_PATH)
    failure = _load_object(PARENT_FAILURE_PATH)
    reconciliation = validate_consumed_attempt(
        envelope, failure, git_binding["consumed_candidate_source"]
    )
    evidence = _load_object(EVIDENCE_PATH)
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "reconciliation_evidence_schema_rejected")
    if evidence != build_evidence(git_binding=git_binding, reconciliation=reconciliation):
        raise ReconciliationError("committed_reconciliation_evidence_rejected")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if f"Result: **{ADMITTED_RESULT}**" not in report or f"Consumed candidate source: `{git_binding['consumed_candidate_source']}`" not in report:
        raise ReconciliationError("committed_reconciliation_report_rejected")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--reconcile", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        evidence = reconcile() if args.reconcile else check()
    except ReconciliationError as error:
        print(json.dumps({"operation_id": OPERATION_ID, "result": str(error), "detail": None}, sort_keys=True))
        return 2
    print(json.dumps({"operation_id": OPERATION_ID, "result": evidence["result"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

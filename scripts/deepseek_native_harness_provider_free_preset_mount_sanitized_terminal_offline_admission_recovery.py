"""Recover one consumed native terminal offline and clean its exact root."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitized_terminal_native_rehearsal
    as consumed,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-sanitized-terminal-"
    "offline-admission-recovery"
)
OPERATION_ROOT = consumed.OPERATION_ROOT
PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-preset-mount-sanitized-terminal-"
    "offline-admission-recovery-plan.md"
)
THREAT_PATH = (
    REPO_ROOT
    / "docs"
    / "security"
    / "deepseek-native-harness-provider-free-preset-mount-sanitized-terminal-"
    "offline-admission-recovery-threat-model-delta.md"
)
CONTRACT_PATH = OPERATION_ROOT / "offline-recovery-contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "offline-recovery-contract.schema.json"
SIDECAR_SCHEMA_PATH = OPERATION_ROOT / "offline-retained-sidecar.schema.json"
ADMITTED_SCHEMA_PATH = OPERATION_ROOT / "offline-admitted-terminal.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "offline-recovery-evidence.schema.json"
ADMITTED_PATH = OPERATION_ROOT / "offline-admitted-terminal.json"
EVIDENCE_PATH = OPERATION_ROOT / "offline-recovery-evidence.json"
REPORT_PATH = OPERATION_ROOT / "offline-recovery-report.md"
ATTEMPT_PATH = consumed.ATTEMPT_CONSUMED_PATH
ENVELOPE_PATH = consumed.PROCESS_ENVELOPE_PATH
PLANNING_SOURCE = "6e60331ca6d5d003b852b837a6d668d411b1d482"
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


class OfflineRecoveryError(RuntimeError):
    """Fail-closed error containing only a controller-owned code."""


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256(path.read_bytes())


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise OfflineRecoveryError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise OfflineRecoveryError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: dict[str, Any], code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        raise OfflineRecoveryError(code) from error


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
        raise OfflineRecoveryError("git_resolution_failed")
    return completed.stdout.strip()


def _write_exclusive(path: Path, value: object, *, text: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if text else "xb"
    kwargs = {"encoding": "utf-8"} if text else {}
    with path.open(mode, **kwargs) as handle:
        handle.write(value if text else _canonical(value))


def load_contract() -> dict[str, Any]:
    contract = _load_object(CONTRACT_PATH)
    _validate(CONTRACT_SCHEMA_PATH, contract, "contract_schema_rejected")
    if contract["planning_source"] != PLANNING_SOURCE:
        raise OfflineRecoveryError("planning_source_constant_mismatch")
    if _git("log", "-1", "--format=%H", "--", str(PLAN_PATH)) != PLANNING_SOURCE:
        raise OfflineRecoveryError("planning_source_path_mismatch")
    if _git("merge-base", "--is-ancestor", PLANNING_SOURCE, "HEAD"):
        raise OfflineRecoveryError("planning_source_not_ancestor")
    return contract


def validate_immutable_inputs(contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    bindings = contract["input_bindings"]
    if _sha256_file(ATTEMPT_PATH) != bindings["attempt_consumed_sha256"]:
        raise OfflineRecoveryError("attempt_consumed_digest_mismatch")
    if _sha256_file(ENVELOPE_PATH) != bindings["process_envelope_sha256"]:
        raise OfflineRecoveryError("process_envelope_digest_mismatch")
    attempt = _load_object(ATTEMPT_PATH)
    envelope = _load_object(ENVELOPE_PATH)
    fixed_attempt = {
        "operation_id": contract["consumed_operation_id"],
        "execution_attempt_id": contract["execution_attempt_id"],
        "candidate_source": contract["consumed_candidate_source"],
        "state": "consumed",
        "retry_count": 0,
        "resume_permitted": False,
    }
    if any(attempt.get(key) != value for key, value in fixed_attempt.items()):
        raise OfflineRecoveryError("attempt_consumed_semantics_mismatch")
    fixed_envelope = {
        "operation_id": contract["consumed_operation_id"],
        "execution_attempt_id": contract["execution_attempt_id"],
        "candidate_source": contract["consumed_candidate_source"],
        "sidecar_file_seen": True,
        "sidecar_bytes": bindings["sidecar_bytes"],
        "sidecar_sha256": bindings["sidecar_sha256"],
        "numeric_exit_code_observed": False,
        "numeric_exit_code": None,
        "stdout_retained": False,
        "stderr_retained": False,
        "raw_stream_read": False,
        "stream_content_retained": False,
        "sidecar_semantics_interpreted": False,
        "raw_runtime_detail_retained": False,
        "native_process_count": 1,
        "retry_count": 0,
        "resume_count": 0,
        "further_process_authorized": False,
    }
    if any(envelope.get(key) != value for key, value in fixed_envelope.items()):
        raise OfflineRecoveryError("process_envelope_semantics_mismatch")
    return attempt, envelope


def disposable_parent() -> Path:
    return consumed.native_base.base.predecessor.predecessor.DISPOSABLE_PARENT.resolve()


def find_retained_root(contract: dict[str, Any]) -> Path:
    parent = disposable_parent()
    prefix = contract["retained_layout"]["root_prefix"]
    roots = sorted(path for path in parent.iterdir() if path.name.startswith(prefix))
    if len(roots) != 1:
        raise OfflineRecoveryError("retained_root_inventory_mismatch")
    root = roots[0]
    if root.is_symlink() or not root.is_dir() or root.resolve().parent != parent:
        raise OfflineRecoveryError("retained_root_boundary_rejected")
    return root.resolve()


def _owned_node_process_count(root: Path) -> int:
    powershell = shutil.which("powershell") or shutil.which("powershell.exe")
    if powershell is None:
        raise OfflineRecoveryError("powershell_process_probe_unavailable")
    escaped = str(root).replace("'", "''")
    probe = (
        "$r='" + escaped + "'; "
        "@((Get-CimInstance Win32_Process -Filter \"Name='node.exe'\") | "
        "Where-Object { $_.CommandLine -and $_.CommandLine.Contains($r) }).Count"
    )
    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", probe],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    if completed.returncode != 0:
        raise OfflineRecoveryError("owned_process_probe_failed")
    try:
        return int(completed.stdout.strip())
    except ValueError as error:
        raise OfflineRecoveryError("owned_process_probe_untyped") from error


def _bundle_root(root: Path, contract: dict[str, Any]) -> Path:
    parent = root / contract["retained_layout"]["bundle_parent"]
    children = sorted(path for path in parent.iterdir() if path.is_dir())
    if len(children) != 1 or children[0].is_symlink():
        raise OfflineRecoveryError("retained_bundle_inventory_mismatch")
    return children[0].resolve()


def validate_retained_sidecar(
    root: Path, contract: dict[str, Any]
) -> tuple[dict[str, Any], Path]:
    bundle = _bundle_root(root, contract)
    sidecar_path = bundle / contract["retained_layout"]["sidecar_relative"]
    if sidecar_path.is_symlink() or not sidecar_path.is_file():
        raise OfflineRecoveryError("retained_sidecar_missing")
    payload = sidecar_path.read_bytes()
    bindings = contract["input_bindings"]
    if len(payload) != bindings["sidecar_bytes"] or _sha256(payload) != bindings["sidecar_sha256"]:
        raise OfflineRecoveryError("retained_sidecar_envelope_mismatch")
    sidecar = _load_object(sidecar_path)
    _validate(SIDECAR_SCHEMA_PATH, sidecar, "retained_sidecar_schema_rejected")
    source_hashes = contract["source_hashes"]
    fixed = {
        "operation_id": contract["consumed_operation_id"],
        "execution_attempt_id": contract["execution_attempt_id"],
        "candidate_source": contract["consumed_candidate_source"],
        "schema_version": bindings["observed_sidecar_schema"],
        "runner_sha256": source_hashes["runner_sha256"],
        "effective_tool_guard_sha256": source_hashes["effective_tool_guard_sha256"],
        "preset_sha256": source_hashes["preset_sha256"],
        "fixed_identity_sha256": source_hashes["fixed_identity_sha256"],
        "target_path_sha256": source_hashes["target_path_sha256"],
        "agent_create_invocation_count": 1,
        "private_agent_preparation_count": 1,
        "private_session_preparation_count": 1,
        "preset_mounted": False,
        "model_selection_installed": False,
        "veto_exact": False,
        "veto_rejected": False,
        "target_created": False,
        "target_used": False,
        "raw_error_retained": False,
    }
    if any(sidecar.get(key) != value for key, value in fixed.items()):
        raise OfflineRecoveryError("retained_sidecar_fixed_binding_mismatch")
    if any(sidecar.get(key) != 0 for key in contract["required_zero_fields"]):
        raise OfflineRecoveryError("retained_sidecar_zero_counter_mismatch")
    if any(sidecar.get(key) != value for key, value in contract["expected_terminal"].items()):
        raise OfflineRecoveryError("retained_sidecar_terminal_mismatch")
    return sidecar, bundle


def validate_retained_context(root: Path, bundle: Path, contract: dict[str, Any]) -> dict[str, Any]:
    layout = contract["retained_layout"]
    readiness_path = root / layout["readiness_relative"]
    try:
        records = [json.loads(line) for line in readiness_path.read_text(encoding="utf-8").splitlines() if line]
        events = [row["event"] for row in records]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise OfflineRecoveryError("retained_readiness_rejected") from error
    if events != contract["expected_readiness"]:
        raise OfflineRecoveryError("retained_readiness_sequence_mismatch")
    network_path = root / layout["network_relative"]
    if network_path.exists() and (network_path.is_symlink() or network_path.stat().st_size != 0):
        raise OfflineRecoveryError("retained_network_ledger_nonzero")
    broker = _load_object(bundle / layout["broker_relative"])
    broker_fields = (
        "provider_call_started", "provider_call_completed", "provider_call_failed",
        "request_count", "request_rejected",
    )
    if any(broker.get(key) != 0 for key in broker_fields) or broker.get("raw_broker_stream_retained") is not False:
        raise OfflineRecoveryError("retained_broker_nonzero")
    proof_dir = root / layout["proof_relative"]
    expected_files = {
        "runner.mjs": contract["source_hashes"]["runner_sha256"],
        "effective-tool-guard.mjs": contract["source_hashes"]["effective_tool_guard_sha256"],
        "preset-mount-sanitizer-runner-bridge.mjs": contract["source_hashes"]["preset_mount_bridge_sha256"],
        "deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs": contract["source_hashes"]["preset_mount_sanitizer_sha256"],
        "sentinel.mjs": contract["source_hashes"]["readiness_sentinel_sha256"],
    }
    observed_files = {path.name: _sha256_file(path) for path in proof_dir.iterdir() if path.is_file()}
    if observed_files != expected_files:
        raise OfflineRecoveryError("retained_proof_hash_mismatch")
    target = bundle / layout["target_relative"]
    if target.exists() or target.is_symlink():
        raise OfflineRecoveryError("retained_target_present")
    return {
        "readiness_events": events,
        "network_attempt_count": 0,
        "broker_zero": True,
        "proof_hashes": observed_files,
        "target_absent": True,
    }


def admitted_projection(sidecar: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    projection = {
        "schema_version": "ariadne.native_harness_sanitized_terminal_offline_admitted_terminal.v1",
        "operation_id": contract["consumed_operation_id"],
        "execution_attempt_id": contract["execution_attempt_id"],
        "consumed_candidate_source": contract["consumed_candidate_source"],
        "process_envelope_sha256": contract["input_bindings"]["process_envelope_sha256"],
        "sidecar_sha256": contract["input_bindings"]["sidecar_sha256"],
        "sidecar_bytes": contract["input_bindings"]["sidecar_bytes"],
        "observed_schema_version": sidecar["schema_version"],
        "intended_schema_version": contract["input_bindings"]["intended_sidecar_schema"],
        "schema_token_mismatch_preserved": True,
        "terminal": contract["expected_terminal"],
        "source_hashes": contract["source_hashes"],
        "factory_counts": {
            key: sidecar[key]
            for key in (
                "agent_create_invocation_count", "private_agent_preparation_count",
                "private_session_preparation_count",
            )
        },
        "required_zero_counters": {key: sidecar[key] for key in contract["required_zero_fields"]},
        "raw_runtime_detail_retained": False,
        "retry_authorized": False,
    }
    _validate(ADMITTED_SCHEMA_PATH, projection, "admitted_projection_schema_rejected")
    return projection


def build_evidence(
    *, contract: dict[str, Any], recovery_candidate: str,
    projection: dict[str, Any], context: dict[str, Any], root_absent: bool,
) -> dict[str, Any]:
    evidence = {
        "schema_version": "ariadne.native_harness_sanitized_terminal_offline_recovery_evidence.v1",
        "operation_id": OPERATION_ID,
        "recovery_candidate_source": recovery_candidate,
        "consumed_candidate_source": contract["consumed_candidate_source"],
        "result": "recovered_finite_terminal",
        "failure_classification": "CONTROLLER_SCHEMA_VERSION_AND_ENVELOPE_COMPOSITION_DEFECT",
        "native_terminal": contract["expected_terminal"],
        "new_bridge_runtime_path_proved": False,
        "inputs": {
            "attempt_consumed_sha256": contract["input_bindings"]["attempt_consumed_sha256"],
            "process_envelope_sha256": contract["input_bindings"]["process_envelope_sha256"],
            "admitted_terminal_sha256": _sha256(_canonical(projection)),
        },
        "retained_artifacts": context,
        "provider_boundary": {
            **contract["recovery_process_budget"],
            "network_attempt_count": 0,
            "database_invocation_count": 0,
            "docker_invocation_count": 0,
            "target_creation_count": 0,
            "target_use_count": 0,
        },
        "cleanup": {
            "owned_node_process_count_before": 0,
            "retained_root_count_before": 1,
            "disposable_root_absent": root_absent,
            "retained_root_count_after": 0 if root_absent else 1,
        },
        "unavailable_launch_observations": {
            "numeric_exit_code_available": False,
            "duration_available": False,
            "exit_mode_available": False,
            "stdout_or_stderr_content_available": False,
        },
        "claim_boundary": {
            "offline_recovery_only": True,
            "native_attempt_passed": False,
            "finite_terminal_recovered": True,
            "controller_source_repair_prospective_only": True,
            "worker_launch_authorized": False,
            "model_provider_request_authorized": False,
            "retry_authorized": False,
            "product_authority": False,
        },
    }
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "recovery_evidence_schema_rejected")
    return evidence


def render_report(evidence: dict[str, Any], timestamp: str) -> str:
    terminal = evidence["native_terminal"]
    return f"""# Native Harness preset-mount sanitized-terminal offline recovery report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Consumed candidate: `{evidence['consumed_candidate_source']}`

Recovery candidate: `{evidence['recovery_candidate_source']}`

Result: **recovered finite terminal**

The sole native process remains consumed. Its content-free envelope was bound
to the exact retained typed sidecar before interpretation. The observed schema
token named the accepted predecessor while the object carried the successor
fields; that version mismatch caused the first admission rejection. A later
contradictory envelope rewrite interrupted canonical output and cleanup.

The recovered native terminal is `{terminal['result']}` at
`{terminal['safe_guard_coordinate']}`. This is bounded evidence of substantial
orchestrator control, zero turns/requests/provider activity and finite failure
attribution. It does **not** prove the new preset-mount bridge runtime path; only
`preset_mount_failure_attributed` could do that.

The exact inactive disposable root is absent. No retry, resume, Node process,
Harness process, worker/model/provider request or product/data action occurred
during recovery.
"""


def execute() -> dict[str, Any]:
    if any(path.exists() for path in (ADMITTED_PATH, EVIDENCE_PATH, REPORT_PATH)):
        raise OfflineRecoveryError("recovery_output_already_exists")
    if subprocess.run(
        ["git", "diff", "--quiet", "--"], cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode != 0:
        raise OfflineRecoveryError("tracked_worktree_must_be_clean")
    contract = load_contract()
    validate_immutable_inputs(contract)
    recovery_candidate = _git("rev-parse", "HEAD")
    if FULL_OID.fullmatch(recovery_candidate) is None:
        raise OfflineRecoveryError("recovery_candidate_invalid")
    root = find_retained_root(contract)
    if _owned_node_process_count(root) != 0:
        raise OfflineRecoveryError("retained_root_process_active")
    sidecar, bundle = validate_retained_sidecar(root, contract)
    context = validate_retained_context(root, bundle, contract)
    projection = admitted_projection(sidecar, contract)
    _write_exclusive(ADMITTED_PATH, projection)
    if _owned_node_process_count(root) != 0:
        raise OfflineRecoveryError("retained_root_process_appeared")
    parent = disposable_parent()
    if root.parent != parent or root.is_symlink():
        raise OfflineRecoveryError("cleanup_root_boundary_rejected")
    shutil.rmtree(root)
    root_absent = not root.exists()
    if not root_absent:
        raise OfflineRecoveryError("cleanup_root_remained")
    evidence = build_evidence(
        contract=contract, recovery_candidate=recovery_candidate,
        projection=projection, context=context, root_absent=root_absent,
    )
    _write_exclusive(EVIDENCE_PATH, evidence)
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    _write_exclusive(REPORT_PATH, render_report(evidence, timestamp), text=True)
    return evidence


def check() -> dict[str, Any]:
    contract = load_contract()
    validate_immutable_inputs(contract)
    projection = _load_object(ADMITTED_PATH)
    evidence = _load_object(EVIDENCE_PATH)
    _validate(ADMITTED_SCHEMA_PATH, projection, "admitted_projection_schema_rejected")
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "recovery_evidence_schema_rejected")
    if evidence["inputs"]["admitted_terminal_sha256"] != _sha256(_canonical(projection)):
        raise OfflineRecoveryError("admitted_projection_digest_mismatch")
    if evidence["inputs"]["process_envelope_sha256"] != contract["input_bindings"]["process_envelope_sha256"]:
        raise OfflineRecoveryError("evidence_envelope_binding_mismatch")
    if evidence["cleanup"]["disposable_root_absent"] is not True:
        raise OfflineRecoveryError("evidence_cleanup_not_complete")
    parent = disposable_parent()
    prefix = contract["retained_layout"]["root_prefix"]
    if any(path.name.startswith(prefix) for path in parent.iterdir()):
        raise OfflineRecoveryError("retained_root_still_present")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if evidence["consumed_candidate_source"] not in report:
        raise OfflineRecoveryError("report_candidate_binding_missing")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        evidence = execute() if args.execute else check()
    except (OfflineRecoveryError, OSError, ValueError) as error:
        print(json.dumps({"status": "failed", "error": type(error).__name__}))
        return 1
    print(json.dumps({
        "status": "passed",
        "operation_id": OPERATION_ID,
        "result": evidence["result"],
        "native_terminal": evidence["native_terminal"]["result"],
        "new_bridge_runtime_path_proved": evidence["new_bridge_runtime_path_proved"],
        "recovery_native_process_count": 0,
        "disposable_root_absent": evidence["cleanup"]["disposable_root_absent"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Run one pinned provider-free native Harness boot through structured diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

import jsonschema

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from orchestration_harness import native_startup_terminal as startup_terminal
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as materializer,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    DISPOSABLE_PARENT,
    ProofError,
    _network_attempts,
    _terminate_process,
    build_child_environment,
    network_guard_source,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-structured-diagnostic-"
    "native-boot-observability-rehearsal"
)
ATTEMPT_ID = "structured-diagnostic-native-boot-observability-attempt-001"
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "provider-free-structured-diagnostic-native-boot-evidence.json"
TERMINAL_PATH = CONTINUITY_ROOT / "pre-hmr-startup-terminal.json"
REPORT_PATH = CONTINUITY_ROOT / "provider-free-structured-diagnostic-native-boot-report.md"
EVIDENCE_SCHEMA = (
    "ariadne.native_harness_structured_diagnostic_native_boot_"
    "observability_evidence.v1"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")

COMPONENT_PATHS = {
    "structured_diagnostic_sha256": REPO_ROOT
    / "orchestration_harness"
    / "native_pre_hmr_diagnostic.py",
    "legacy_terminal_sha256": REPO_ROOT
    / "orchestration_harness"
    / "native_startup_terminal.py",
    "materializer_sha256": Path(materializer.__file__).resolve(),
    "materializer_contract_sha256": materializer.CONTRACT_PATH,
    "structured_seam_contract_sha256": REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-unclassified-pre-hmr-structured-diagnostic-seam-recovery"
    / "contract.json",
    "node_fixture_evidence_sha256": REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-structured-diagnostic-wrapper-node-fixture-rehearsal"
    / "provider-free-node-fixture-evidence.json",
    "complete_composition_evidence_sha256": REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-complete-composition-native-boot-recovery"
    / "provider-free-complete-composition-native-boot-evidence.json",
}


class NativeBootObservabilityError(RuntimeError):
    """The frozen single-boot boundary rejected."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise NativeBootObservabilityError("json_not_object")
    return value


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_json(path)
    jsonschema.validate(contract, _load_json(CONTRACT_SCHEMA_PATH))
    if contract.get("operation_id") != OPERATION_ID:
        raise NativeBootObservabilityError("contract_operation_mismatch")
    attempt = contract.get("attempt", {})
    if attempt != {
        "attempt_id": ATTEMPT_ID,
        "native_process_limit": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
        "reclassification": False,
    }:
        raise NativeBootObservabilityError("contract_attempt_latch_mismatch")
    launch = contract.get("launch", {})
    if (
        launch.get("node_flag") != "--expose-internals"
        or launch.get("profile_flag") != "--profile"
        or launch.get("profile") != "emr4-diagnostic-observability-missing"
        or launch.get("task_arguments") != []
        or launch.get("expected_exit_code") != 1
        or launch.get("expected_hmr_event_count") != 0
    ):
        raise NativeBootObservabilityError("contract_launch_mismatch")
    boundary = contract.get("process_boundary", {})
    if boundary.get("native_harness_processes") != 1 or any(
        boundary.get(field) != 0
        for field in (
            "package_materializer_processes",
            "broker_processes",
            "worker_sessions",
            "prompts",
            "tool_executions",
            "model_requests",
            "provider_requests",
            "network_attempts",
            "docker_invocations",
            "database_invocations",
        )
    ):
        raise NativeBootObservabilityError("contract_process_boundary_mismatch")
    return contract


def _git_commit_is_ancestor(object_id: str) -> bool:
    if FULL_OID.fullmatch(object_id) is None:
        return False
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{object_id}^{{commit}}"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    relation = subprocess.run(
        ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return exists.returncode == 0 and relation.returncode == 0


def _validate_immutable_artifacts(contract: dict[str, Any]) -> int:
    rows = contract["immutable_artifacts"]
    for row in rows:
        path = REPO_ROOT / row["path"]
        if not path.is_file() or _file_sha256(path) != row["sha256"]:
            raise NativeBootObservabilityError(
                "immutable_artifact_mismatch:" + row["path"]
            )
    return len(rows)


def _validate_installed_source(
    package_root: Path, contract: dict[str, Any]
) -> dict[str, Any]:
    package = contract["package"]
    manifest = _load_json(package_root / "package.json")
    if (
        manifest.get("name") != package["name"]
        or manifest.get("version") != package["version"]
        or manifest.get("bin", {}).get("dsh") != package["bin"]
    ):
        raise NativeBootObservabilityError("installed_package_identity_mismatch")
    scope_root = package_root.parent
    observed: dict[str, str] = {}
    for relative, expected in package["installed_source_sha256"].items():
        path = scope_root / Path(relative)
        if not path.is_file():
            raise NativeBootObservabilityError("installed_source_missing:" + relative)
        observed[relative] = _file_sha256(path)
        if observed[relative] != expected:
            raise NativeBootObservabilityError("installed_source_mismatch:" + relative)

    bin_text = (scope_root / "dsh/lib/bin.js").read_text(encoding="utf-8")
    boot_text = (scope_root / "dsh/lib/profile-boot-DG5t9aNs.js").read_text(
        encoding="utf-8"
    )
    app_boot_text = (scope_root / "dsh-app-boot/lib/index.js").read_text(
        encoding="utf-8"
    )
    compose_position = boot_text.index("const composed = composeProfile(")
    boot_position = boot_text.index("const ctx = await boot(")
    missing_profile_position = app_boot_text.index(
        "does not exist; create it with 'dsh plugin --profile"
    )
    app_boot_position = app_boot_text.index("async function boot(")
    checks = {
        "bin_awaits_run_profile": "await runProfile({" in bin_text,
        "profile_resolution_precedes_boot": compose_position < boot_position,
        "missing_profile_throw_precedes_boot_definition": missing_profile_position
        < app_boot_position,
        "missing_profile_is_plain_error": (
            "throw new Error(`${binName}: profile ${JSON.stringify(name)} does not exist;"
            in app_boot_text
        ),
    }
    if not all(checks.values()):
        raise NativeBootObservabilityError("installed_pre_hmr_source_shape_mismatch")
    return {"source_sha256": observed, "checks": checks}


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    sources = [contract["planning_source"], *contract["accepted_sources"].values()]
    if any(not _git_commit_is_ancestor(value) for value in sources):
        raise NativeBootObservabilityError("git_source_missing_or_not_ancestor")
    components = {
        field: _file_sha256(path) for field, path in COMPONENT_PATHS.items()
    }
    if components != contract["components"]:
        raise NativeBootObservabilityError("component_digest_mismatch")
    immutable_count = _validate_immutable_artifacts(contract)

    materializer_contract = materializer.load_contract()
    source_projection = materializer.validate_materialization_source(
        materializer_contract
    )
    specification = contract["materialization"]
    for field in (
        "source_root",
        "package_json_sha256",
        "package_lock_sha256",
        "node_modules_lock_sha256",
    ):
        source_field = "root" if field == "source_root" else field
        if source_projection[source_field] != specification[field]:
            raise NativeBootObservabilityError(
                "materialization_source_mismatch:" + field
            )
    package_root = (
        Path(specification["source_root"])
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    ).resolve(strict=True)
    installed = _validate_installed_source(package_root, contract)
    return {
        "components": components,
        "immutable_artifact_count": immutable_count,
        "materialization_source": source_projection,
        "installed_source": installed,
    }


def build_launch_command(
    *, node_executable: str, wrapper_path: Path, contract: dict[str, Any]
) -> list[str]:
    launch = contract["launch"]
    command = [
        node_executable,
        launch["node_flag"],
        str(wrapper_path),
        launch["profile_flag"],
        launch["profile"],
        *launch["task_arguments"],
    ]
    if len(command) != 5 or command[-1] != launch["profile"]:
        raise NativeBootObservabilityError("launch_command_surplus_argument")
    return command


def _expected_diagnostic(
    contract: dict[str, Any], candidate_source: str
) -> dict[str, Any]:
    return {
        "schema_version": contract["diagnostic"]["schema_version"],
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "candidate_source": candidate_source,
        "phase": contract["diagnostic"]["phase"],
        "cause_chain": contract["diagnostic"]["cause_chain"],
        "cause_chain_cycle_detected": False,
        "cause_chain_truncated": False,
        "raw_error_message_retained": False,
        "raw_stack_retained": False,
        "raw_paths_retained": False,
    }


def _terminal_payload(terminal: dict[str, Any]) -> bytes:
    if terminal.get("schema_version") == diagnostic.TERMINAL_SCHEMA_VERSION:
        return diagnostic.structured_terminal_bytes(terminal)
    return startup_terminal.terminal_bytes(terminal)


def _validate_terminal(terminal: dict[str, Any]) -> dict[str, Any]:
    if terminal.get("schema_version") == diagnostic.TERMINAL_SCHEMA_VERSION:
        return diagnostic.validate_structured_pre_hmr_terminal(terminal)
    return startup_terminal.validate_pre_hmr_terminal(terminal)


def _write_terminal_exclusive(
    *, path: Path, terminal: dict[str, Any], disposable_root: Path
) -> str:
    operation_root = CONTINUITY_ROOT.resolve(strict=True)
    resolved_disposable = disposable_root.resolve(strict=True)
    if path.parent.resolve() != operation_root or path.is_symlink() or path.exists():
        raise NativeBootObservabilityError("terminal_path_invalid")
    try:
        path.resolve().relative_to(resolved_disposable)
    except ValueError:
        pass
    else:
        raise NativeBootObservabilityError("terminal_inside_disposable_root")
    payload = _terminal_payload(terminal)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    readback = path.read_bytes()
    _validate_terminal(json.loads(readback))
    if readback != payload:
        raise NativeBootObservabilityError("terminal_readback_mismatch")
    return _sha256(payload)


def validate_controller_source() -> dict[str, bool]:
    source = inspect.getsource(execute_boot)
    checks = {
        "single_popen": source.count("subprocess.Popen(") == 1,
        "no_retry_loop": "while retry" not in source and "for attempt" not in source,
        "duration_in_finally": source.index("finally:")
        < source.index("duration_ms = round("),
        "duration_before_termination": source.index("duration_ms = round(")
        < source.index("_terminate_process(process)"),
        "terminal_before_cleanup": source.index("terminal_digest = _write_terminal_exclusive(")
        < source.index("shutil.rmtree(root)"),
        "termination_before_cleanup": source.index("_terminate_process(process)")
        < source.index("shutil.rmtree(root)"),
    }
    if not all(checks.values()):
        raise NativeBootObservabilityError("controller_source_shape_invalid")
    return checks


def deterministic_check(candidate_source: str | None = None) -> dict[str, Any]:
    contract = load_contract()
    if candidate_source is not None and not _git_commit_is_ancestor(candidate_source):
        raise NativeBootObservabilityError("candidate_source_invalid")
    predecessor = validate_predecessors(contract)
    root = Path("C:/deterministic/structured-diagnostic-native-boot")
    wrapper_path = root / "entrypoint-wrapper.mjs"
    diagnostic_path = root / "diagnostic.json"
    package_root = (
        Path(contract["materialization"]["source_root"])
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    ).resolve(strict=True)
    source = candidate_source or contract["planning_source"]
    wrapper = diagnostic.build_entrypoint_wrapper_source(
        package_root=package_root,
        wrapper_path=wrapper_path,
        diagnostic_path=diagnostic_path,
        disposable_root=root,
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=source,
        canonical_json=True,
    )
    command = build_launch_command(
        node_executable="node.exe", wrapper_path=wrapper_path, contract=contract
    )
    return {
        "contract": contract,
        "predecessor": predecessor,
        "wrapper": diagnostic.validate_entrypoint_wrapper_source(
            wrapper, require_canonical_json=True
        ),
        "command": command,
        "controller": validate_controller_source(),
        "native_process_count": 0,
    }


def _render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["terminal"]
    nested = evidence.get("structured_diagnostic") or {}
    kind = ((nested.get("cause_chain") or [{}])[0]).get("error_kind")
    return f"""# Provider-free structured diagnostic native-boot report

Date: 2026-08-21

Result: **{evidence['result']}**

- Attempt: `{evidence['attempt_id']}`
- Native process / retry count: `{evidence['launch']['native_process_count']} / {evidence['launch']['retry_count']}`
- Exit code / duration: `{evidence['launch']['exit_code']} / {evidence['launch']['duration_ms']} ms`
- Structured diagnostic accepted: `{str(evidence['launch']['structured_diagnostic_accepted']).lower()}`
- Safe top error kind: `{kind}`
- Terminal schema / cause: `{terminal.get('schema_version')}` / `{terminal.get('cause')}`
- HMR / session / prompt / tool / model / provider counts: `0 / 0 / 0 / 0 / 0 / 0`
- Network attempts: `{evidence['provider_boundary']['network_attempts']}`
- Process absent: `{str(evidence['cleanup']['process_absent']).lower()}`
- Disposable root absent: `{str(evidence['cleanup']['disposable_root_absent']).lower()}`

This proves only one pinned rc.7 provider-free pre-HMR structured diagnostic
composition. It is not a worker, model/provider or product-runtime result.
"""


def execute_boot(candidate_source: str) -> dict[str, Any]:
    if FULL_OID.fullmatch(candidate_source) is None:
        raise NativeBootObservabilityError("candidate_source_invalid")
    if any(path.exists() for path in (EVIDENCE_PATH, TERMINAL_PATH, REPORT_PATH)):
        raise NativeBootObservabilityError("canonical_attempt_output_already_exists")
    check = deterministic_check(candidate_source)
    contract = check["contract"]
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = Path(
        tempfile.mkdtemp(prefix="dsh-structured-diagnostic-boot-", dir=parent)
    ).resolve()
    if root.parent != parent:
        raise NativeBootObservabilityError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    started: float | None = None
    duration_ms: int | None = None
    exit_code: int | None = None
    timed_out = False
    terminal: dict[str, Any] | None = None
    terminal_digest: str | None = None
    safe_diagnostic: dict[str, Any] | None = None
    structured_accepted = False
    network_records: list[dict[str, Any]] = []
    removed_environment_names = 0
    copied_source: dict[str, Any] = {}
    wrapper_projection: dict[str, Any] = {}
    stdout_reading: dict[str, Any] | None = None
    stderr_reading: dict[str, Any] | None = None
    error: BaseException | None = None

    stdout_path = root / "stdout.log"
    stderr_path = root / "stderr.log"
    diagnostic_path = root / "diagnostic.json"
    wrapper_path = root / "entrypoint-wrapper.mjs"
    network_path = root / "network.jsonl"
    try:
        home = root / "home"
        workspace = root / "workspace"
        guard_path = root / "network-guard.mjs"
        home.mkdir()
        workspace.mkdir()
        guard_path.write_bytes(network_guard_source())
        environment, removed_environment_names = build_child_environment(
            home, guard_path, network_path
        )
        package_root, _source_projection = materializer.materialize_accepted_node_modules(
            root, materializer.load_contract()
        )
        copied_source = _validate_installed_source(package_root, contract)
        if (home / "profiles" / contract["launch"]["profile"]).exists():
            raise NativeBootObservabilityError("authored_missing_profile_preexists")
        wrapper = diagnostic.build_entrypoint_wrapper_source(
            package_root=package_root,
            wrapper_path=wrapper_path,
            diagnostic_path=diagnostic_path,
            disposable_root=root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=candidate_source,
            canonical_json=True,
        )
        wrapper_path.write_bytes(wrapper)
        wrapper_projection = diagnostic.validate_entrypoint_wrapper_source(
            wrapper, require_canonical_json=True
        )
        node = shutil.which("node")
        if node is None:
            raise NativeBootObservabilityError("node_not_found")
        command = build_launch_command(
            node_executable=node, wrapper_path=wrapper_path, contract=contract
        )
        started = time.monotonic()
        with stdout_path.open("wb") as stdout_stream, stderr_path.open(
            "wb"
        ) as stderr_stream:
            process = subprocess.Popen(
                command,
                cwd=workspace,
                env=environment,
                stdout=stdout_stream,
                stderr=stderr_stream,
            )
            process_started = True
            try:
                exit_code = process.wait(timeout=contract["launch"]["timeout_seconds"])
            except subprocess.TimeoutExpired:
                timed_out = True
    except (
        NativeBootObservabilityError,
        diagnostic.StructuredDiagnosticError,
        startup_terminal.StartupTerminalError,
        materializer.PresetMountProjectionError,
        ProofError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ) as caught:
        error = caught
    finally:
        if process_started and started is not None:
            duration_ms = round((time.monotonic() - started) * 1000)
        if process is not None:
            _terminate_process(process)
            if exit_code is None:
                exit_code = process.returncode
        if process_started:
            try:
                stdout_reading = startup_terminal.read_startup_stream(stdout_path)
                stderr_reading = startup_terminal.read_startup_stream(stderr_path)
                coordinate = (
                    "native_worker_timeout"
                    if timed_out
                    else "native_process_exited_nonzero"
                )
                fallback = startup_terminal.build_pre_hmr_terminal(
                    operation_id=OPERATION_ID,
                    attempt_id=ATTEMPT_ID,
                    candidate_source=candidate_source,
                    native_process_started=True,
                    exit_code=exit_code,
                    controller_coordinate=coordinate,
                    hmr_events=[],
                    stdout=stdout_reading,
                    stderr=stderr_reading,
                )
                terminal = fallback
                if not timed_out:
                    try:
                        safe_diagnostic = diagnostic.read_structured_diagnostic(
                            path=diagnostic_path,
                            disposable_root=root,
                            operation_id=OPERATION_ID,
                            attempt_id=ATTEMPT_ID,
                            candidate_source=candidate_source,
                        )
                        if safe_diagnostic != _expected_diagnostic(
                            contract, candidate_source
                        ):
                            raise NativeBootObservabilityError(
                                "structured_diagnostic_coordinate_mismatch"
                            )
                        terminal = diagnostic.build_structured_pre_hmr_terminal(
                            operation_id=OPERATION_ID,
                            attempt_id=ATTEMPT_ID,
                            candidate_source=candidate_source,
                            native_process_started=True,
                            exit_code=exit_code,
                            controller_coordinate="native_process_exited_nonzero",
                            hmr_events=[],
                            stdout=stdout_reading,
                            stderr=stderr_reading,
                            structured_diagnostic=safe_diagnostic,
                        )
                        structured_accepted = True
                    except (
                        NativeBootObservabilityError,
                        diagnostic.StructuredDiagnosticError,
                    ) as structured_error:
                        error = structured_error
                        safe_diagnostic = None
                terminal_digest = _write_terminal_exclusive(
                    path=TERMINAL_PATH,
                    terminal=terminal,
                    disposable_root=root,
                )
            except (
                NativeBootObservabilityError,
                diagnostic.StructuredDiagnosticError,
                startup_terminal.StartupTerminalError,
                OSError,
                ValueError,
                json.JSONDecodeError,
            ) as terminal_error:
                error = terminal_error
        try:
            network_records = _network_attempts(network_path)
        except (ProofError, OSError, ValueError, json.JSONDecodeError) as network_error:
            error = network_error
            network_records = [{"event": "invalid_network_ledger"}]
        if root.parent != parent:
            raise NativeBootObservabilityError("cleanup_root_escape")
        shutil.rmtree(root)

    process_absent = process is None or process.poll() is not None
    root_absent = not root.exists()
    immutable_count = _validate_immutable_artifacts(contract)
    result = "pass"
    if (
        error is not None
        or not process_started
        or timed_out
        or exit_code != contract["launch"]["expected_exit_code"]
        or duration_ms is None
        or duration_ms < 0
        or not structured_accepted
        or terminal is None
        or terminal.get("schema_version") != diagnostic.TERMINAL_SCHEMA_VERSION
        or terminal_digest is None
        or network_records
        or not process_absent
        or not root_absent
    ):
        result = "fail"
    if not process_started:
        raise NativeBootObservabilityError("prelaunch_validation_failed") from error
    if terminal is None or stdout_reading is None or stderr_reading is None:
        raise NativeBootObservabilityError("terminalization_failed") from error

    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "candidate_source": candidate_source,
        "attempt_id": ATTEMPT_ID,
        "result": result,
        "package": {
            "name": contract["package"]["name"],
            "version": contract["package"]["version"],
            "bin": contract["package"]["bin"],
            "materialization_method": contract["materialization"]["method"],
            "materialization_process_count": 0,
            "copied_source": copied_source,
        },
        "wrapper": wrapper_projection,
        "launch": {
            "native_process_count": 1,
            "retry_count": 0,
            "profile": contract["launch"]["profile"],
            "task_argument_count": 0,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "duration_source": "finally_before_termination_and_cleanup",
            "hmr_event_count": 0,
            "stdout": {
                "byte_count": stdout_reading["byte_count"],
                "sha256": stdout_reading["sha256"],
            },
            "stderr": {
                "byte_count": stderr_reading["byte_count"],
                "sha256": stderr_reading["sha256"],
            },
            "structured_diagnostic_accepted": structured_accepted,
            "terminal_sha256": terminal_digest,
            "raw_streams_retained": False,
        },
        "structured_diagnostic": safe_diagnostic,
        "terminal": terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempts": len(network_records),
            "broker_processes": 0,
            "worker_sessions": 0,
            "prompts": 0,
            "tool_executions": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "docker_invocations": 0,
            "database_invocations": 0,
        },
        "immutable_artifacts_match": immutable_count == len(
            contract["immutable_artifacts"]
        ),
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
            "raw_streams_retained": False,
            "copied_package_tree_retained": False,
        },
    }
    jsonschema.validate(evidence, _load_json(EVIDENCE_SCHEMA_PATH))
    EVIDENCE_PATH.write_bytes(_canonical_json(evidence))
    REPORT_PATH.write_text(_render_report(evidence), encoding="utf-8", newline="\n")
    if result != "pass":
        raise NativeBootObservabilityError("native_boot_observability_failed") from error
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--candidate-source")
    args = parser.parse_args()
    try:
        if args.check:
            projection = deterministic_check(args.candidate_source)
            print(
                json.dumps(
                    {
                        "status": "passed",
                        "attempt_id": ATTEMPT_ID,
                        "wrapper_sha256": projection["wrapper"]["sha256"],
                        "native_processes": 0,
                    },
                    sort_keys=True,
                )
            )
        else:
            if args.candidate_source is None:
                raise NativeBootObservabilityError("candidate_source_required")
            evidence = execute_boot(args.candidate_source)
            print(
                json.dumps(
                    {
                        "status": evidence["result"],
                        "attempt_id": evidence["attempt_id"],
                        "exit_code": evidence["launch"]["exit_code"],
                        "terminal_schema": evidence["terminal"]["schema_version"],
                        "cleanup": evidence["cleanup"],
                    },
                    sort_keys=True,
                )
            )
    except (
        NativeBootObservabilityError,
        diagnostic.StructuredDiagnosticError,
        startup_terminal.StartupTerminalError,
        materializer.PresetMountProjectionError,
        ProofError,
        jsonschema.ValidationError,
    ) as error:
        print(json.dumps({"status": "revision_required", "reason": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

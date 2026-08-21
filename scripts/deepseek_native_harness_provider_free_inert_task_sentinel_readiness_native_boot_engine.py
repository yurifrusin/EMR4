"""Run one provider-free rc.7 repaired-sentinel native Harness boot."""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness import native_startup_terminal as startup_terminal
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as repaired,
)
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as materializer,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    DISPOSABLE_PARENT,
    POLL_SECONDS,
    ProofError,
    _network_attempts,
    _terminate_process,
    build_child_environment,
    network_guard_source,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-repaired-sentinel-native-boot-proof"
)
ATTEMPT_ID = "repaired-sentinel-native-boot-attempt-001"
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
CONSUMED_PATH = CONTINUITY_ROOT / "native-attempt-consumed.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "provider-free-repaired-sentinel-native-boot-terminal.json"
REPORT_PATH = CONTINUITY_ROOT / "provider-free-repaired-sentinel-native-boot-report.md"
CONTRACT_SCHEMA = (
    "ariadne.deepseek_native_harness_repaired_sentinel_boot_contract.v1"
)
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_repaired_sentinel_boot_evidence.v1"
)
EVENT_SCHEMA = "ariadne.synthetic_native_worker_hmr_event.v1"
EXPECTED_EVENTS = ["sentinel_activated", "stock_headless_hmr_ready"]
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


class RepairedSentinelBootError(RuntimeError):
    """The frozen one-process repaired-sentinel boundary rejected."""


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
        raise RepairedSentinelBootError("json_not_object")
    return value


def _write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(_canonical_json(value))
        stream.flush()
        os.fsync(stream.fileno())


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


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_json(path)
    jsonschema.validate(contract, _load_json(CONTRACT_SCHEMA_PATH))
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RepairedSentinelBootError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise RepairedSentinelBootError("contract_operation_mismatch")
    if contract.get("attempt") != {
        "attempt_id": ATTEMPT_ID,
        "native_process_limit": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
        "fallback": False,
        "reclassification": False,
    }:
        raise RepairedSentinelBootError("contract_attempt_latch_mismatch")
    if contract.get("profile") != {
        "profile": "headless",
        "changed": False,
        "sentinel_id": "synthetic-worker-hmr-sentinel",
        "sentinel_name": "../../../installation/proof/sentinel.mjs",
        "expected_events": EXPECTED_EVENTS,
        "runner_row_count": 0,
        "runner_file_count": 0,
        "changed_profile_write_count": 0,
    }:
        raise RepairedSentinelBootError("contract_initial_profile_mismatch")
    launch = contract.get("launch", {})
    if launch != {
        "node_flag": "--expose-internals",
        "profile_flag": "--profile",
        "profile": "headless",
        "task_arguments": [],
        "argument_count": 5,
        "timeout_seconds": 45,
        "termination_owner": "controller_after_readiness",
    }:
        raise RepairedSentinelBootError("contract_launch_mismatch")
    return contract


def validate_lineage(contract: dict[str, Any]) -> dict[str, Any]:
    sources = [contract["planning_source"], *contract["accepted_sources"].values()]
    if any(not _git_commit_is_ancestor(source) for source in sources):
        raise RepairedSentinelBootError("git_source_missing_or_not_ancestor")
    observed: list[dict[str, Any]] = []
    roles: set[str] = set()
    for row in contract["components"]:
        role = row["role"]
        path = REPO_ROOT / row["path"]
        if role in roles or not path.is_file() or path.is_symlink():
            raise RepairedSentinelBootError("component_path_invalid:" + role)
        roles.add(role)
        digest = _file_sha256(path)
        if digest != row["sha256"]:
            raise RepairedSentinelBootError("component_digest_mismatch:" + role)
        observed.append({"role": role, "sha256": digest})

    repair_evidence = _load_json(
        REPO_ROOT
        / "orchestration"
        / "continuity"
        / "deepseek-native-harness-provider-free-proof-module-relative-specifier-repair"
        / "repair-evidence.json"
    )
    if (
        repair_evidence.get("status") != "passed"
        or repair_evidence.get("target_source_sha256")
        != _file_sha256(Path(repaired.__file__).resolve())
        or any(repair_evidence.get("zero_activity", {}).values())
    ):
        raise RepairedSentinelBootError("accepted_repair_evidence_mismatch")

    complete_evidence = _load_json(
        REPO_ROOT
        / "orchestration"
        / "continuity"
        / "deepseek-native-harness-provider-free-complete-composition-native-boot-recovery"
        / "provider-free-complete-composition-native-boot-evidence.json"
    )
    boundary = complete_evidence.get("provider_boundary", {})
    if complete_evidence.get("result") != "pass" or any(
        boundary.get(field) != 0
        for field in (
            "agent_session_count",
            "broker_request_count",
            "database_invocation_count",
            "docker_invocation_count",
            "model_request_count",
            "network_attempt_count",
            "occupied_worker_count",
            "provider_request_count",
            "turn_count",
        )
    ):
        raise RepairedSentinelBootError("accepted_native_predecessor_mismatch")
    return {"sources": sources, "components": observed}


def initial_profile_projection(root: Path) -> dict[str, Any]:
    payload = repaired.profile_patch(root, 43123, changed=False)
    repaired.validate_profile_patch(payload, changed=False)
    source = payload.decode("utf-8")
    parsed = yaml.safe_load(source)
    if not isinstance(parsed, list):
        raise RepairedSentinelBootError("profile_not_array")
    inserted: list[dict[str, Any]] = []
    for row in parsed:
        if isinstance(row, dict) and "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise RepairedSentinelBootError("profile_insert_shape_invalid")
            inserted.extend(row["insert"])
    sentinel = [row for row in inserted if row.get("id") == "synthetic-worker-hmr-sentinel"]
    runner = [row for row in inserted if row.get("id") == "synthetic-one-request-worker-runner"]
    if (
        len(sentinel) != 1
        or sentinel[0].get("name") != "../../../installation/proof/sentinel.mjs"
        or runner
        or source.count("../../../installation/proof/sentinel.mjs") != 1
        or "runner.mjs" in source
    ):
        raise RepairedSentinelBootError("repaired_initial_profile_mismatch")
    return {
        "bytes": len(payload),
        "sha256": _sha256(payload),
        "sentinel_row_count": len(sentinel),
        "runner_row_count": len(runner),
        "payload": payload,
    }


def build_launch_command(
    *, node_executable: str, package_root: Path, contract: dict[str, Any]
) -> list[str]:
    launch = contract["launch"]
    command = [
        node_executable,
        launch["node_flag"],
        str(package_root / contract["package"]["bin"]),
        launch["profile_flag"],
        launch["profile"],
        *launch["task_arguments"],
    ]
    expected_count = 5 + len(launch["task_arguments"])
    if (
        launch["argument_count"] != expected_count
        or len(command) != expected_count
        or command[3:5] != ["--profile", "headless"]
        or command[5:] != launch["task_arguments"]
    ):
        raise RepairedSentinelBootError("launch_command_surplus_argument")
    return command


def validate_controller_source() -> dict[str, bool]:
    source = inspect.getsource(execute_boot)
    module_source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(module_source)
    popen_calls = sum(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "Popen"
        for node in ast.walk(tree)
    )
    changed_true = "changed" + "=True"
    runner_materialization = "runner.mjs" + "\").write"
    checks = {
        "single_popen": source.count("subprocess.Popen(") == 1,
        "single_popen_module": popen_calls == 1,
        "no_retry_loop": "while retry" not in source and "for attempt" not in source,
        "no_changed_profile": changed_true not in module_source,
        "no_runner_materialization": runner_materialization not in module_source,
        "duration_before_termination": source.index("duration_ms = round(")
        < source.index("_terminate_process(process)"),
        "termination_before_cleanup": source.index("_terminate_process(process)")
        < source.index("shutil.rmtree(root)"),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise RepairedSentinelBootError(
            "controller_source_shape_invalid:" + ",".join(failed)
        )
    return checks


def deterministic_check(candidate_source: str | None = None) -> dict[str, Any]:
    contract = load_contract()
    if candidate_source is not None and not _git_commit_is_ancestor(candidate_source):
        raise RepairedSentinelBootError("candidate_source_invalid")
    lineage = validate_lineage(contract)
    source_projection = materializer.validate_materialization_source(
        materializer.load_contract()
    )
    profile = initial_profile_projection(
        Path("C:/deterministic/repaired-sentinel-native-boot")
    )
    command = build_launch_command(
        node_executable="node.exe",
        package_root=Path("C:/deterministic/installation/node_modules/@deepseek-ai/dsh"),
        contract=contract,
    )
    return {
        "contract": contract,
        "lineage": lineage,
        "materialization": source_projection,
        "profile": {key: value for key, value in profile.items() if key != "payload"},
        "sentinel_sha256": _sha256(repaired.sentinel_source()),
        "command": command,
        "controller": validate_controller_source(),
        "native_process_count": 0,
    }


def materialize_profile(
    root: Path, contract: dict[str, Any]
) -> tuple[Path, dict[str, Any]]:
    package_root, source_projection = materializer.materialize_accepted_node_modules(
        root, materializer.load_contract()
    )
    package = _load_json(package_root / "package.json")
    if (
        package.get("name") != contract["package"]["name"]
        or package.get("version") != contract["package"]["version"]
        or package.get("bin", {}).get("dsh") != contract["package"]["bin"]
    ):
        raise RepairedSentinelBootError("materialized_package_identity_mismatch")

    proof = root / "installation" / "proof"
    profile_dir = root / "home" / "profiles" / "headless"
    preset_dir = root / "home" / ".agent-presets" / "emr4-bounded-worker"
    proof.mkdir()
    profile_dir.mkdir(parents=True)
    preset_dir.mkdir(parents=True)
    profile_manifest = {
        "name": "dsh-profile-headless",
        "private": True,
        "dependencies": {},
        "dsh": {
            "profile": {
                "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]
            }
        },
    }
    (profile_dir / "package.json").write_bytes(_canonical_json(profile_manifest))
    (profile_dir / "pnpm-workspace.yaml").write_text(
        "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        encoding="utf-8",
        newline="\n",
    )
    preset = materializer.native_predecessor.build_preset_source(
        materializer.native_predecessor.load_contract()
    )
    (preset_dir / "agent.cordis.yml").write_bytes(preset)
    sentinel = repaired.sentinel_source()
    (proof / "sentinel.mjs").write_bytes(sentinel)
    if (proof / "runner.mjs").exists():
        raise RepairedSentinelBootError("runner_file_present")
    profile = initial_profile_projection(root)
    profile_path = profile_dir / "cordis.patch.yml"
    profile_path.write_bytes(profile["payload"])
    return package_root, {
        "package_json_sha256": _file_sha256(package_root / "package.json"),
        "source_root": source_projection["root"],
        "materialization_process_count": 0,
        "profile_sha256": profile["sha256"],
        "sentinel_sha256": _sha256(sentinel),
        "sentinel_relative_name": "../../../installation/proof/sentinel.mjs",
        "runner_row_count": 0,
        "runner_file_count": 0,
        "changed_profile_write_count": 0,
    }


def parse_events(path: Path, *, allow_incomplete: bool) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_bytes().splitlines(keepends=True)
    events: list[str] = []
    for index, line in enumerate(lines, start=1):
        if not line.endswith(b"\n"):
            if allow_incomplete and index == len(lines):
                break
            raise RepairedSentinelBootError("hmr_event_invalid")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise RepairedSentinelBootError("hmr_event_invalid") from error
        if (
            not isinstance(value, dict)
            or set(value) != {"schema_version", "sequence", "event"}
            or value["schema_version"] != EVENT_SCHEMA
            or value["sequence"] != index
            or value["event"] not in EXPECTED_EVENTS
        ):
            raise RepairedSentinelBootError("hmr_event_invalid")
        events.append(value["event"])
    if events != EXPECTED_EVENTS[: len(events)]:
        raise RepairedSentinelBootError("hmr_event_sequence_mismatch")
    return events


def _stream_projection(path: Path) -> dict[str, Any]:
    reading = startup_terminal.read_startup_stream(path)
    return {"byte_count": reading["byte_count"], "sha256": reading["sha256"]}


def _render_report(evidence: dict[str, Any]) -> str:
    return f"""# Provider-free repaired-sentinel native boot report

Date: 2026-08-21

Result: **{evidence['result']}**

- Attempt: `{evidence['attempt_id']}`
- Candidate: `{evidence['candidate_source']}`
- Native processes / retries: `{evidence['launch']['native_process_count']}` / `0`
- HMR events: `{', '.join(evidence['hmr_events'])}`
- Controller terminated after readiness: `{str(evidence['launch']['controller_terminated_after_readiness']).lower()}`
- Network / model / provider requests: `{evidence['provider_boundary']['network_attempts']}` / `0` / `0`
- Process absent: `{str(evidence['cleanup']['process_absent']).lower()}`
- Disposable root absent: `{str(evidence['cleanup']['disposable_root_absent']).lower()}`
- Raw streams retained: `false`

This proves only the repaired initial sentinel loads and stock-headless HMR
reaches readiness in one provider-free rc.7 process. It is not a worker,
model/provider, product-runtime or reliability result.
"""


def execute_boot(candidate_source: str) -> dict[str, Any]:
    if not _git_commit_is_ancestor(candidate_source):
        raise RepairedSentinelBootError("candidate_source_invalid")
    if any(path.exists() for path in (CONSUMED_PATH, EVIDENCE_PATH, REPORT_PATH)):
        raise RepairedSentinelBootError("canonical_attempt_output_already_exists")
    check = deterministic_check(candidate_source)
    contract = check["contract"]
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = Path(
        tempfile.mkdtemp(prefix="dsh-repaired-sentinel-boot-", dir=parent)
    ).resolve()
    if root.parent != parent or root.is_symlink():
        raise RepairedSentinelBootError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    launch_attempted = False
    readiness_observed = False
    terminated_after_readiness = False
    started: float | None = None
    duration_ms: int | None = None
    exit_code: int | None = None
    failure: str | None = None
    events: list[str] = []
    network_records: list[dict[str, Any]] = []
    removed_environment_names = 0
    profile_projection: dict[str, Any] = {}
    stdout_projection = {"byte_count": 0, "sha256": _sha256(b"")}
    stderr_projection = {"byte_count": 0, "sha256": _sha256(b"")}
    stdout_path = root / "stdout.raw"
    stderr_path = root / "stderr.raw"
    event_path = root / "hmr-events.jsonl"
    network_path = root / "network.jsonl"
    error: BaseException | None = None

    try:
        workspace = root / "workspace"
        home = root / "home"
        guard_path = root / "network-guard.mjs"
        workspace.mkdir()
        guard_path.write_bytes(network_guard_source())
        environment, removed_environment_names = build_child_environment(
            home, guard_path, network_path
        )
        if "DSH_EMR4_BROKER_TOKEN" in environment:
            raise RepairedSentinelBootError("broker_token_not_scrubbed")
        package_root, profile_projection = materialize_profile(root, contract)
        node = shutil.which("node")
        if node is None:
            raise RepairedSentinelBootError("node_not_found")
        command = build_launch_command(
            node_executable=node, package_root=package_root, contract=contract
        )
        consumed = {
            "schema_version": "ariadne.deepseek_native_harness_repaired_sentinel_boot_consumed.v1",
            "operation_id": OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "candidate_source": candidate_source,
            "state": "consumed",
            "native_process_limit": 1,
            "automatic_retry_count": 0,
            "resume_permitted": False,
        }
        _write_json_exclusive(CONSUMED_PATH, consumed)
        with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
            launch_attempted = True
            started = time.monotonic()
            try:
                process = subprocess.Popen(
                    command,
                    cwd=workspace,
                    env=environment,
                    stdout=stdout,
                    stderr=stderr,
                )
            except OSError as caught:
                failure = "native_process_creation_failed"
                error = caught
            if process is not None:
                process_started = True
                deadline = time.monotonic() + contract["launch"]["timeout_seconds"]
                while True:
                    try:
                        events = parse_events(event_path, allow_incomplete=True)
                    except RepairedSentinelBootError as caught:
                        failure = str(caught)
                        error = caught
                        break
                    if events == EXPECTED_EVENTS:
                        readiness_observed = True
                        break
                    if process.poll() is not None:
                        exit_code = process.returncode
                        failure = "native_process_exited_before_readiness"
                        break
                    if time.monotonic() >= deadline:
                        failure = "native_process_timeout_before_readiness"
                        break
                    time.sleep(POLL_SECONDS)
    except (
        RepairedSentinelBootError,
        materializer.PresetMountProjectionError,
        ProofError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ) as caught:
        error = caught
        if launch_attempted:
            failure = failure or "unexpected_controller_failure"
    finally:
        if process_started and started is not None:
            duration_ms = round((time.monotonic() - started) * 1000)
        if process is not None:
            _terminate_process(process)
            terminated_after_readiness = readiness_observed
            exit_code = process.returncode
        if launch_attempted:
            try:
                stdout_projection = _stream_projection(stdout_path)
                stderr_projection = _stream_projection(stderr_path)
                events = parse_events(event_path, allow_incomplete=False)
            except (RepairedSentinelBootError, startup_terminal.StartupTerminalError) as caught:
                error = caught
                failure = failure or "hmr_event_invalid"
        try:
            network_records = _network_attempts(network_path)
        except (ProofError, OSError, ValueError, json.JSONDecodeError) as caught:
            error = caught
            network_records = [{"event": "invalid_network_ledger"}]
        if network_records:
            failure = failure or "network_attempt_detected"
        if root.parent != parent:
            raise RepairedSentinelBootError("cleanup_root_escape")
        try:
            shutil.rmtree(root)
        except OSError as caught:
            error = caught
            failure = failure or "disposable_root_cleanup_failed"

    if not launch_attempted:
        raise RepairedSentinelBootError("prelaunch_validation_failed") from error
    process_absent = process is None or process.poll() is not None
    root_absent = not root.exists()
    if not process_absent:
        failure = failure or "process_cleanup_failed"
    if not root_absent:
        failure = failure or "disposable_root_cleanup_failed"
    success = (
        failure is None
        and process_started
        and readiness_observed
        and terminated_after_readiness
        and events == EXPECTED_EVENTS
        and not network_records
        and process_absent
        and root_absent
        and duration_ms is not None
    )
    if not success and failure is None:
        failure = "hmr_event_sequence_mismatch"
    if failure is not None and failure not in contract["failure_coordinates"]:
        failure = "unexpected_controller_failure"

    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "candidate_source": candidate_source,
        "result": "pass" if success else "failed_closed",
        "failure_coordinate": None if success else failure,
        "package": {
            "name": contract["package"]["name"],
            "version": contract["package"]["version"],
            "bin": contract["package"]["bin"],
            "materialization_method": "python_copy_only",
            "materialization_process_count": 0,
            "package_json_sha256": profile_projection.get("package_json_sha256"),
        },
        "profile": {
            "changed": False,
            "sha256": profile_projection.get("profile_sha256"),
            "sentinel_sha256": profile_projection.get("sentinel_sha256"),
            "sentinel_relative_name": profile_projection.get(
                "sentinel_relative_name"
            ),
            "sentinel_row_count": 1,
            "runner_row_count": 0,
            "runner_file_count": 0,
            "changed_profile_write_count": 0,
        },
        "launch": {
            "launch_attempt_count": 1,
            "native_process_count": 1 if process_started else 0,
            "retry_count": 0,
            "argument_count": contract["launch"]["argument_count"],
            "task_argument_count": len(contract["launch"]["task_arguments"]),
            "node_flag": "--expose-internals",
            "profile_args": ["--profile", "headless"],
            "duration_ms": duration_ms,
            "duration_source": "finally_before_termination_and_cleanup",
            "exit_code_after_controller_termination": exit_code,
            "readiness_observed": readiness_observed,
            "controller_terminated_after_readiness": terminated_after_readiness,
        },
        "hmr_events": events,
        "streams": {
            "stdout": stdout_projection,
            "stderr": stderr_projection,
            "raw_retained": False,
        },
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "changed_runner_processes": 0,
            "broker_processes": 0,
            "worker_sessions": 0,
            "prompts": 0,
            "tool_executions": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": len(network_records),
            "docker_invocations": 0,
            "database_invocations": 0,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
            "raw_streams_retained": False,
            "raw_environment_retained": False,
            "copied_package_tree_retained": False,
        },
        "claim_boundary": (
            "This proves only repaired initial sentinel loading and stock-headless "
            "HMR readiness in one provider-free rc.7 process; it is not a runner, "
            "worker, model/provider, product-runtime or reliability result."
        ),
    }
    jsonschema.validate(evidence, _load_json(EVIDENCE_SCHEMA_PATH))
    _write_json_exclusive(EVIDENCE_PATH, evidence)
    REPORT_PATH.write_text(_render_report(evidence), encoding="utf-8", newline="\n")
    if not success:
        raise RepairedSentinelBootError(
            "repaired_sentinel_native_boot_failed_closed:" + str(failure)
        ) from error
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
            output = {
                "status": "passed",
                "attempt_id": ATTEMPT_ID,
                "profile_sha256": projection["profile"]["sha256"],
                "native_processes": 0,
            }
        else:
            if args.candidate_source is None:
                raise RepairedSentinelBootError("candidate_source_required")
            evidence = execute_boot(args.candidate_source)
            output = {
                "status": evidence["result"],
                "attempt_id": ATTEMPT_ID,
                "hmr_events": evidence["hmr_events"],
                "cleanup": evidence["cleanup"],
            }
        print(json.dumps(output, sort_keys=True))
    except (
        RepairedSentinelBootError,
        materializer.PresetMountProjectionError,
        ProofError,
        jsonschema.ValidationError,
    ) as error:
        print(json.dumps({"status": "revision_required", "reason": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


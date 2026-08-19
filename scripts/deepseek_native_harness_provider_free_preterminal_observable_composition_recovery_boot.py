"""Run one provider-free preterminal-observable native composition boot."""

from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

import jsonschema
import yaml

from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    FAILURE_COORDINATES,
    GuardError,
    _default_cache_root,
    build_guard_source,
    validate_guard_source,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof import (
    build_preset_source,
    sentinel_source,
    validate_installed_packages,
    verify_cached_packages,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    DISPOSABLE_PARENT,
    POLL_SECONDS,
    ProofError,
    _network_attempts,
    _offline_install,
    _terminate_process,
    _verify_installed_source,
    atomic_write,
    build_child_environment,
    canonical_json_bytes,
    network_guard_source,
    sha256_bytes,
    sha256_file,
    verify_tarball,
)
from scripts.deepseek_native_harness_provider_free_preterminal_observability_recovery import (
    corrected_runner_source,
    validate_corrected_runner,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preterminal-observable-composition-"
    "recovery-boot"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = (
    OPERATION_ROOT / "provider-free-preterminal-observable-native-boot-evidence.json"
)
REPORT_PATH = (
    OPERATION_ROOT / "provider-free-preterminal-observable-native-boot-report.md"
)
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_preterminal_observable_composition_"
    "recovery_boot_evidence.v1"
)
SAFE_TOOL_NAME = re.compile(r"^[a-z_]+$")

PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / (
        "deepseek-native-harness-provider-free-preterminal-observable-composition-"
        "recovery-boot-plan.md"
    )
)
OBSERVABILITY_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / (
        "deepseek-native-harness-provider-free-preterminal-activation-observability-"
        "recovery"
    )
)
FAILED_BOOT_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / (
        "deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof"
    )
)
GUARD_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / (
        "deepseek-native-harness-provider-free-effective-tool-composition-and-terminal-"
        "coordinate-guard"
    )
)
HMR_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / (
        "deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-"
        "boot-proof"
    )
)
PROFILE_FAMILY = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / (
        "deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-"
        "admission"
    )
    / "profile-family.yaml"
)

PREDECESSOR_FILES = {
    "frozen_plan_sha256": PLAN_PATH,
    "preterminal_observability_script_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_preterminal_observability_recovery.py",
    "preterminal_observability_contract_sha256": OBSERVABILITY_ROOT / "contract.json",
    "preterminal_observability_evidence_sha256": OBSERVABILITY_ROOT
    / "provider-free-preterminal-observability-recovery-evidence.json",
    "immutable_failed_controller_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof.py",
    "immutable_failed_contract_sha256": FAILED_BOOT_ROOT / "contract.json",
    "immutable_failed_evidence_sha256": FAILED_BOOT_ROOT
    / "provider-free-effective-tool-native-boot-evidence.json",
    "effective_tool_guard_script_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_effective_tool_composition_guard.py",
    "effective_tool_guard_contract_sha256": GUARD_ROOT / "contract.json",
    "hmr_boot_script_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_hmr_boot_proof.py",
    "hmr_boot_contract_sha256": HMR_ROOT / "contract.json",
    "profile_family_sha256": PROFILE_FAMILY,
}
IMPLEMENTATION_FILES = {
    "controller_sha256": Path(__file__).resolve(),
    "focused_test_sha256": REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_preterminal_observable_composition_recovery_boot.py",
}


class RecoveryBootError(RuntimeError):
    """A closed recovery-boot controller rejection."""


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(contract, schema)
    expected_schema = (
        "ariadne.deepseek_native_harness_preterminal_observable_composition_"
        "recovery_boot_contract.v1"
    )
    if contract.get("schema_version") != expected_schema:
        raise RecoveryBootError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise RecoveryBootError("contract_operation_mismatch")
    attempt = contract.get("attempt", {})
    if attempt.get("attempt_id") == "native-composition-attempt-001":
        raise RecoveryBootError("immutable_attempt_id_reused")
    if (
        attempt.get("native_process_count") != 1
        or attempt.get("automatic_retry") is not False
        or attempt.get("manual_retry") is not False
        or attempt.get("resume") is not False
    ):
        raise RecoveryBootError("contract_one_process_latch_mismatch")
    if contract.get("preset", {}).get("selected_tools") != ["edit", "glob", "read"]:
        raise RecoveryBootError("contract_selected_tools_mismatch")
    return contract


def _git_object_is_ancestor(object_id: str) -> bool:
    if re.fullmatch(r"[0-9a-f]{40}", object_id) is None:
        return False
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{object_id}^{{commit}}"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if exists.returncode != 0:
        return False
    relation = subprocess.run(
        ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return relation.returncode == 0


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    sources = {
        "planning_source": contract["planning_source"],
        "frozen_plan_source": contract["frozen_plan_source"],
        **contract["accepted_sources"],
    }
    if any(not _git_object_is_ancestor(object_id) for object_id in sources.values()):
        raise RecoveryBootError("accepted_git_source_missing_or_not_ancestor")

    expected = contract["predecessor_bytes"]
    actual = {field: sha256_file(path) for field, path in PREDECESSOR_FILES.items()}
    generated = {
        "generated_corrected_runner_sha256": sha256_bytes(corrected_runner_source()),
        "generated_effective_tool_guard_sha256": sha256_bytes(build_guard_source()),
        "generated_readiness_sentinel_sha256": sha256_bytes(sentinel_source()),
    }
    for field, digest in {**actual, **generated}.items():
        if expected.get(field) != digest:
            raise RecoveryBootError(f"predecessor_digest_mismatch:{field}")
    implementation = {
        field: sha256_file(path) for field, path in IMPLEMENTATION_FILES.items()
    }
    if implementation != contract["implementation_bytes"]:
        raise RecoveryBootError("implementation_digest_mismatch")

    failed = json.loads(
        (
            FAILED_BOOT_ROOT / "provider-free-effective-tool-native-boot-evidence.json"
        ).read_text(encoding="utf-8")
    )
    immutable = contract["immutable_predecessor_attempt"]
    if (
        failed.get("attempt_id") != immutable["attempt_id"]
        or failed.get("result") != "fail"
        or failed.get("terminal") is not None
    ):
        raise RecoveryBootError("immutable_failed_attempt_shape_mismatch")
    observability = json.loads(
        (
            OBSERVABILITY_ROOT
            / "provider-free-preterminal-observability-recovery-evidence.json"
        ).read_text(encoding="utf-8")
    )
    if (
        observability.get("result") != "pass"
        or observability.get("diagnosis", {}).get("causal_classification")
        != immutable["causal_classification"]
        or observability.get("immutable_attempt", {}).get("unchanged") is not True
    ):
        raise RecoveryBootError("accepted_observability_evidence_mismatch")
    runner = validate_corrected_runner(corrected_runner_source())
    guard = validate_guard_source(build_guard_source())
    return {
        "accepted_sources": contract["accepted_sources"],
        "predecessor_sha256": actual,
        "generated_sha256": generated,
        "implementation_sha256": implementation,
        "corrected_runner": runner,
        "effective_tool_guard": guard,
        "immutable_predecessor_unchanged": True,
    }


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def build_patch_pair(
    profile_dir: Path,
    readiness_path: Path,
    activation_path: Path,
    terminal_path: Path,
    sentinel_path: Path,
    runner_path: Path,
) -> tuple[bytes, bytes]:
    profile_patch = profile_dir / "cordis.patch.yml"
    home_patch = profile_dir.parents[1] / "cordis.patch.yml"
    expected_modules = profile_dir.parents[2] / "installation" / "proof"
    if (
        sentinel_path != expected_modules / "sentinel.mjs"
        or runner_path != expected_modules / "runner.mjs"
    ):
        raise RecoveryBootError("proof_module_location_mismatch")
    common = f"""- id: headless-runner
  disabled: true
- id: code-runtime
  disabled: true
- id: session-telemetry-otel
  disabled: true
- insert:
    - id: provider-free-effective-tool-hmr-sentinel
      name: ../../../installation/proof/sentinel.mjs
      config:
        eventPath: {_yaml_path(readiness_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
"""
    changed = (
        common
        + f"""    - id: provider-free-preterminal-observable-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr]
      config:
        activationPath: {_yaml_path(activation_path)}
        terminalPath: {_yaml_path(terminal_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
"""
    )
    initial, changed_bytes = common.encode(), changed.encode()
    validate_patch_pair(initial, changed_bytes)
    return initial, changed_bytes


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = yaml.safe_load(payload)
    if not isinstance(rows, list):
        raise RecoveryBootError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise RecoveryBootError("patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise RecoveryBootError("patch_insert_invalid")
            inserted.extend(row["insert"])
        else:
            direct.append(row)
    return direct, inserted


def validate_patch_pair(initial: bytes, changed: bytes) -> None:
    initial_direct, initial_inserted = _patch_rows(initial)
    changed_direct, changed_inserted = _patch_rows(changed)
    expected_direct = [
        {"id": "headless-runner", "disabled": True},
        {"id": "code-runtime", "disabled": True},
        {"id": "session-telemetry-otel", "disabled": True},
    ]
    if initial_direct != expected_direct or changed_direct != expected_direct:
        raise RecoveryBootError("patch_disabled_rows_mismatch")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-effective-tool-hmr-sentinel"
    ]:
        raise RecoveryBootError("initial_patch_runner_present")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-effective-tool-hmr-sentinel",
        "provider-free-preterminal-observable-runner",
    ]:
        raise RecoveryBootError("changed_patch_rows_mismatch")
    if changed_inserted[:-1] != initial_inserted:
        raise RecoveryBootError("changed_patch_mutates_initial")
    runner = changed_inserted[-1]
    if runner.get("inject") != ["hmr"]:
        raise RecoveryBootError("runner_injection_mismatch")
    sentinel_config = initial_inserted[0].get("config", {})
    runner_config = runner.get("config", {})
    if "eventPath" not in sentinel_config or "activationPath" in sentinel_config:
        raise RecoveryBootError("readiness_writer_config_mismatch")
    if "activationPath" not in runner_config or "eventPath" in runner_config:
        raise RecoveryBootError("activation_writer_config_mismatch")


def _parse_ledger(
    path: Path,
    *,
    schema: str,
    value_key: str,
    allowed: set[str],
    allow_incomplete: bool = False,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_bytes().splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not line.endswith(b"\n"):
            if allow_incomplete and index == len(lines) - 1:
                break
            raise RecoveryBootError("ledger_partial_line")
        record = json.loads(line)
        if set(record) != {"schema_version", "sequence", value_key}:
            raise RecoveryBootError("ledger_record_shape_invalid")
        if record["schema_version"] != schema or record["sequence"] != len(records) + 1:
            raise RecoveryBootError("ledger_record_sequence_invalid")
        if record[value_key] not in allowed:
            raise RecoveryBootError("ledger_value_invalid")
        records.append(record)
    values = [record[value_key] for record in records]
    if len(values) != len(set(values)):
        raise RecoveryBootError("ledger_duplicate_value")
    return records


def parse_readiness(
    path: Path, contract: dict[str, Any], *, allow_incomplete: bool = False
) -> list[dict[str, Any]]:
    readiness = contract["readiness"]
    return _parse_ledger(
        path,
        schema=readiness["schema_version"],
        value_key="event",
        allowed=set(readiness["events"]),
        allow_incomplete=allow_incomplete,
    )


def parse_activation(path: Path, contract: dict[str, Any]) -> list[dict[str, Any]]:
    activation = contract["activation"]
    return _parse_ledger(
        path,
        schema=activation["schema_version"],
        value_key="coordinate",
        allowed=set(activation["coordinates"]),
    )


def validate_readiness_prefix(
    records: list[dict[str, Any]], contract: dict[str, Any]
) -> None:
    values = [record["event"] for record in records]
    expected = contract["readiness"]["events"]
    if values != expected[: len(values)]:
        raise RecoveryBootError("readiness_prefix_invalid")


def validate_readiness(records: list[dict[str, Any]], contract: dict[str, Any]) -> None:
    if [record["event"] for record in records] != contract["readiness"]["events"]:
        raise RecoveryBootError("readiness_sequence_mismatch")


def validate_activation(
    records: list[dict[str, Any]], contract: dict[str, Any]
) -> None:
    values = [record["coordinate"] for record in records]
    if values != contract["activation"]["success_sequence"]:
        raise RecoveryBootError("activation_sequence_mismatch")


def parse_terminal(path: Path, contract: dict[str, Any]) -> dict[str, Any]:
    payload = path.read_bytes()
    if not payload.endswith(b"\n") or payload.count(b"\n") != 1:
        raise RecoveryBootError("terminal_record_count_invalid")
    terminal = json.loads(payload)
    expected_keys = {
        "schema_version",
        "stage",
        "code",
        "detail",
        "effective_tool_names",
        "effective_tool_count",
    }
    expected = contract["terminal"]
    if (
        set(terminal) != expected_keys
        or terminal["schema_version"] != expected["schema_version"]
    ):
        raise RecoveryBootError("terminal_shape_invalid")
    if terminal["stage"] != expected["stage"]:
        raise RecoveryBootError("terminal_stage_invalid")
    allowed_codes = {
        expected["success_code"],
        *FAILURE_COORDINATES,
        *contract["activation"]["coordinates"],
    }
    if terminal["code"] not in allowed_codes:
        raise RecoveryBootError("terminal_code_invalid")
    names = terminal["effective_tool_names"]
    if (
        not isinstance(names, list)
        or names != sorted(names)
        or len(names) != len(set(names))
        or any(
            not isinstance(name, str) or SAFE_TOOL_NAME.fullmatch(name) is None
            for name in names
        )
        or terminal["effective_tool_count"] != len(names)
    ):
        raise RecoveryBootError("terminal_tool_projection_invalid")
    detail = terminal["detail"]
    if detail is not None and detail != ",".join(names):
        raise RecoveryBootError("terminal_detail_invalid")
    if terminal["code"] in contract["activation"]["coordinates"] and (
        detail is not None or names
    ):
        raise RecoveryBootError("activation_terminal_payload_invalid")
    return terminal


def _success_terminal(terminal: dict[str, Any], contract: dict[str, Any]) -> bool:
    expected = contract["terminal"]
    return terminal == {
        "schema_version": expected["schema_version"],
        "stage": expected["stage"],
        "code": expected["success_code"],
        "detail": expected["detail"],
        "effective_tool_names": expected["effective_tool_names"],
        "effective_tool_count": expected["effective_tool_count"],
    }


def validate_controller_source() -> dict[str, Any]:
    source = inspect.getsource(execute_boot)
    checks = {
        "single_popen": source.count("subprocess.Popen(") == 1,
        "no_retry_loop": "for attempt" not in source and "while retry" not in source,
        "duration_in_finally": source.index("finally:")
        < source.index("duration_ms = round("),
        "duration_before_termination": source.index("duration_ms = round(")
        < source.index("_terminate_process(process)"),
        "termination_before_cleanup": source.index("_terminate_process(process)")
        < source.index("shutil.rmtree(root)"),
        "single_atomic_mutation": source.count(
            "atomic_write(patch_path, changed_patch)"
        )
        == 1,
    }
    if not all(checks.values()):
        raise RecoveryBootError("controller_source_shape_invalid")
    return checks


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    predecessor = validate_predecessors(contract)
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    blob, packages = verify_cached_packages(contract, resolved_cache)
    preset = build_preset_source(contract)
    root = Path("C:/deterministic/preterminal-observable-recovery-boot")
    profile = root / "home" / "profiles" / "headless"
    modules = root / "installation" / "proof"
    initial, changed = build_patch_pair(
        profile,
        root / "readiness.jsonl",
        root / "activation.jsonl",
        root / "terminal.json",
        modules / "sentinel.mjs",
        modules / "runner.mjs",
    )
    runner = corrected_runner_source()
    guard = build_guard_source()
    return {
        "contract": contract,
        "predecessor": predecessor,
        "cache_blob_sha256": sha256_file(blob),
        "package_count": len(packages),
        "preset_sha256": sha256_bytes(preset),
        "initial_patch_sha256": sha256_bytes(initial),
        "changed_patch_sha256": sha256_bytes(changed),
        "runner": validate_corrected_runner(runner),
        "guard": validate_guard_source(guard),
        "sentinel_sha256": sha256_bytes(sentinel_source()),
        "network_guard_sha256": sha256_bytes(network_guard_source()),
        "controller": validate_controller_source(),
    }


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _safe_ledger_capture(
    path: Path,
    contract: dict[str, Any],
    kind: str,
) -> tuple[list[dict[str, Any]], bool]:
    try:
        if kind == "readiness":
            return parse_readiness(path, contract), True
        return parse_activation(path, contract), True
    except (RecoveryBootError, OSError, ValueError, json.JSONDecodeError):
        return [], False


def _safe_terminal_capture(
    path: Path, contract: dict[str, Any]
) -> tuple[dict[str, Any] | None, bool]:
    try:
        return parse_terminal(path, contract), True
    except (RecoveryBootError, OSError, ValueError, json.JSONDecodeError):
        return None, False


def _failure_coordinate(
    *,
    error: BaseException | None,
    readiness: list[dict[str, Any]],
    readiness_valid: bool,
    activation: list[dict[str, Any]],
    activation_valid: bool,
    terminal: dict[str, Any] | None,
    terminal_valid: bool,
    network_attempt_count: int,
    network_ledger_valid: bool,
) -> str:
    if network_attempt_count or not network_ledger_valid:
        return "NETWORK_BOUNDARY_REJECTED"
    if (
        isinstance(error, RecoveryBootError)
        and str(error) == "native_process_deadline_exceeded"
    ):
        if terminal_valid and terminal is not None:
            return str(terminal["code"])
        return "NATIVE_PROCESS_TIMEOUT"
    if not readiness_valid:
        return "READINESS_LEDGER_INVALID"
    if [row["event"] for row in readiness] != [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]:
        return "NATIVE_PROCESS_READINESS_INCOMPLETE"
    if not activation_valid:
        return "ACTIVATION_LEDGER_INVALID"
    if not activation:
        return "RUNNER_NOT_ACTIVATED"
    if not terminal_valid or terminal is None:
        return "TERMINAL_INVALID_OR_ABSENT"
    if terminal["code"] != "EFFECTIVE_TOOL_COMPOSITION_PASSED":
        return str(terminal["code"])
    return "CONTROLLER_ACCEPTANCE_MISMATCH"


def render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["terminal"] or {}
    return f"""# Provider-free preterminal-observable native composition recovery boot report

- Result: `{evidence["result"]}`
- Attempt: `{evidence["attempt_id"]}`
- Native process count: `{evidence["launch"]["native_process_count"]}`
- Exit code: `{evidence["launch"]["exit_code"]}`
- Reliable duration: `{evidence["launch"]["duration_ms"]} ms`
- Readiness: `{", ".join(evidence["readiness"]["events"])}`
- Activation: `{", ".join(evidence["activation"]["coordinates"])}`
- Terminal: `{terminal.get("code")}`
- Effective tools: `{", ".join(terminal.get("effective_tool_names", []))}`
- Network / agent-session / broker / model / provider counts: `0 / 0 / 0 / 0 / 0`
- Process absent: `{str(evidence["cleanup"]["process_absent"]).lower()}`
- Disposable root absent: `{str(evidence["cleanup"]["disposable_root_absent"]).lower()}`

This proves only the pinned local rc.7 provider-free pre-provider composition
path and its bounded preterminal observability. It is not an occupied worker or
a DeepSeek reasoning, coding-quality or provider-reliability result.
"""


def execute_boot(cache_root: Path | None = None) -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise RecoveryBootError("canonical_attempt_output_already_exists")
    check = deterministic_check(cache_root)
    contract = check["contract"]
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    blob, cached_packages = verify_cached_packages(contract, resolved_cache)
    parent = DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise RecoveryBootError("disposable_parent_missing")
    root = Path(
        tempfile.mkdtemp(prefix="dsh-preterminal-observable-boot-", dir=parent)
    ).resolve()
    if root.parent != parent:
        raise RecoveryBootError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    started: float | None = None
    error: BaseException | None = None
    result = "fail"
    package_identity: dict[str, Any] = {}
    install_projection: dict[str, Any] = {}
    source_projection: dict[str, Any] = {}
    installed_versions: dict[str, str] = {}
    readiness_records: list[dict[str, Any]] = []
    activation_records: list[dict[str, Any]] = []
    readiness_valid = False
    activation_valid = False
    terminal: dict[str, Any] | None = None
    terminal_valid = False
    network_records: list[dict[str, Any]] = []
    network_ledger_valid = True
    initial_patch = b""
    changed_patch = b""
    preset = build_preset_source(contract)
    sentinel = sentinel_source()
    runner = corrected_runner_source()
    guard = build_guard_source()
    network_guard = network_guard_source()
    launch_started_utc: str | None = None
    duration_ms: int | None = None
    exit_code: int | None = None
    mutated_after_readiness = False
    removed_environment_names = 0
    stdout_digest = sha256_bytes(b"")
    stderr_digest = sha256_bytes(b"")
    stdout_size = 0
    stderr_size = 0

    readiness_path = root / "readiness.jsonl"
    activation_path = root / "activation.jsonl"
    terminal_path = root / "terminal.json"
    network_path = root / "network.jsonl"
    stdout_path = root / "stdout.log"
    stderr_path = root / "stderr.log"

    try:
        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        workspace = root / "workspace"
        installation_proof = root / "installation" / "proof"
        network_guard_path = root / "network-guard.mjs"
        tarball = root / "dsh-0.1.0-rc.7.tgz"
        workspace.mkdir()
        profile_dir.mkdir(parents=True)
        _write_bytes(network_guard_path, network_guard)
        _write_bytes(tarball, blob.read_bytes())
        package_identity = verify_tarball(tarball, contract)
        if package_identity["sha256"] != contract["package"]["tarball_sha256"]:
            raise RecoveryBootError("materialized_tarball_sha256_mismatch")
        environment, removed_environment_names = build_child_environment(
            home, network_guard_path, network_path
        )
        package_root, install_projection = _offline_install(root, tarball, environment)
        source_projection = _verify_installed_source(package_root, contract)
        installed_versions = validate_installed_packages(package_root, contract)

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
        (profile_dir / "package.json").write_text(
            json.dumps(profile_manifest, indent=2) + "\n", encoding="utf-8"
        )
        (profile_dir / "pnpm-workspace.yaml").write_text(
            "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
            encoding="utf-8",
        )
        preset_path = (
            home / ".agent-presets" / contract["preset"]["id"] / "agent.cordis.yml"
        )
        _write_bytes(preset_path, preset)
        _write_bytes(installation_proof / "sentinel.mjs", sentinel)
        _write_bytes(installation_proof / "runner.mjs", runner)
        _write_bytes(installation_proof / "effective-tool-guard.mjs", guard)
        initial_patch, changed_patch = build_patch_pair(
            profile_dir,
            readiness_path,
            activation_path,
            terminal_path,
            installation_proof / "sentinel.mjs",
            installation_proof / "runner.mjs",
        )
        patch_path = profile_dir / "cordis.patch.yml"
        _write_bytes(patch_path, initial_patch)

        node = shutil.which("node")
        if node is None:
            raise RecoveryBootError("node_not_found")
        command = [
            node,
            contract["launch"]["node_flag"],
            str(package_root / contract["package"]["bin"]),
            *contract["launch"]["profile_args"],
            "provider-free preterminal-observable composition recovery boot",
        ]
        launch_started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        started = time.monotonic()
        with (
            stdout_path.open("wb") as stdout_stream,
            stderr_path.open("wb") as stderr_stream,
        ):
            process = subprocess.Popen(
                command,
                cwd=workspace,
                env=environment,
                stdout=stdout_stream,
                stderr=stderr_stream,
            )
            process_started = True
            deadline = started + float(contract["launch"]["timeout_seconds"])
            while True:
                readiness_records = parse_readiness(
                    readiness_path, contract, allow_incomplete=True
                )
                validate_readiness_prefix(readiness_records, contract)
                readiness_values = [record["event"] for record in readiness_records]
                if (
                    readiness_values == contract["readiness"]["events"]
                    and not mutated_after_readiness
                ):
                    atomic_write(patch_path, changed_patch)
                    mutated_after_readiness = True
                if process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    raise RecoveryBootError("native_process_deadline_exceeded")
                time.sleep(POLL_SECONDS)
            exit_code = process.wait(timeout=5)
        readiness_records = parse_readiness(readiness_path, contract)
        activation_records = parse_activation(activation_path, contract)
        terminal = parse_terminal(terminal_path, contract)
        network_records = _network_attempts(network_path)
        validate_readiness(readiness_records, contract)
        validate_activation(activation_records, contract)
        if not mutated_after_readiness:
            raise RecoveryBootError("patch_not_mutated_after_readiness")
        if network_records:
            raise RecoveryBootError("network_attempt_observed")
        if not _success_terminal(terminal, contract):
            raise RecoveryBootError("guard_terminal_not_success")
        if exit_code != contract["terminal"]["success_exit_code"]:
            raise RecoveryBootError("native_process_exit_code_mismatch")
        result = "pass"
    except (
        RecoveryBootError,
        ProofError,
        GuardError,
        subprocess.SubprocessError,
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
        if stdout_path.exists():
            stdout_payload = stdout_path.read_bytes()
            stdout_digest, stdout_size = (
                sha256_bytes(stdout_payload),
                len(stdout_payload),
            )
        if stderr_path.exists():
            stderr_payload = stderr_path.read_bytes()
            stderr_digest, stderr_size = (
                sha256_bytes(stderr_payload),
                len(stderr_payload),
            )
        readiness_records, readiness_valid = _safe_ledger_capture(
            readiness_path, contract, "readiness"
        )
        activation_records, activation_valid = _safe_ledger_capture(
            activation_path, contract, "activation"
        )
        terminal, terminal_valid = _safe_terminal_capture(terminal_path, contract)
        try:
            network_records = _network_attempts(network_path)
        except (ProofError, OSError, ValueError, json.JSONDecodeError):
            network_records = []
            network_ledger_valid = False
        if root.parent != parent:
            raise RecoveryBootError("cleanup_root_escape")
        shutil.rmtree(root)

    process_absent = process is None or process.poll() is not None
    root_absent = not root.exists()
    if not process_started:
        raise RecoveryBootError("prelaunch_validation_failed") from error
    if duration_ms is None or duration_ms < 0:
        result = "fail"
        error = RecoveryBootError("duration_not_retained")
    if not process_absent or not root_absent:
        result = "fail"
        error = RecoveryBootError("cleanup_incomplete")

    failure: str | None = None
    if result != "pass":
        failure = _failure_coordinate(
            error=error,
            readiness=readiness_records,
            readiness_valid=readiness_valid,
            activation=activation_records,
            activation_valid=activation_valid,
            terminal=terminal,
            terminal_valid=terminal_valid,
            network_attempt_count=len(network_records),
            network_ledger_valid=network_ledger_valid,
        )
        if not process_absent or not root_absent:
            failure = "CLEANUP_INCOMPLETE"

    readiness_values = [record["event"] for record in readiness_records]
    activation_values = [record["coordinate"] for record in activation_records]
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "attempt_id": contract["attempt"]["attempt_id"],
        "result": result,
        "failure_classification": failure,
        "package": {
            "name": contract["package"]["name"],
            "version": contract["package"]["version"],
            "bin": contract["package"]["bin"],
            **package_identity,
            "offline_install": install_projection,
            "verified_cached_package_count": len(cached_packages),
            "installed_versions": installed_versions,
        },
        "source_contract": {**check["predecessor"], "installed": source_projection},
        "launch": {
            "started_at_utc": launch_started_utc,
            "duration_ms": duration_ms,
            "duration_source": "finally_before_termination_and_cleanup",
            "node_flag": contract["launch"]["node_flag"],
            "profile_args": contract["launch"]["profile_args"],
            "native_process_count": 1,
            "retry_count": 0,
            "mutated_after_in_process_readiness": mutated_after_readiness,
            "exit_code": exit_code,
            "stdout_sha256": stdout_digest,
            "stderr_sha256": stderr_digest,
            "stdout_bytes": stdout_size,
            "stderr_bytes": stderr_size,
            "raw_logs_retained": False,
        },
        "composition": {
            "preset_sha256": sha256_bytes(preset),
            "initial_patch_sha256": sha256_bytes(initial_patch),
            "changed_patch_sha256": sha256_bytes(changed_patch),
            "sentinel_sha256": sha256_bytes(sentinel),
            "runner_sha256": sha256_bytes(runner),
            "effective_tool_guard_sha256": sha256_bytes(guard),
            "network_guard_sha256": sha256_bytes(network_guard),
            "stock_runner_enabled": False,
            "code_runtime_enabled": False,
            "telemetry_enabled": False,
            "custom_runner_in_initial_patch": False,
        },
        "readiness": {
            "events": readiness_values,
            "ledger_valid": readiness_valid,
            "exact_expected_order": readiness_values == contract["readiness"]["events"],
            "writer": contract["readiness"]["writer"],
        },
        "activation": {
            "coordinates": activation_values,
            "ledger_valid": activation_valid,
            "exact_success_order": activation_values
            == contract["activation"]["success_sequence"],
            "writer": contract["activation"]["writer"],
        },
        "terminal": terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempt_count": len(network_records),
            "network_ledger_valid": network_ledger_valid,
            "agent_session_count": 0,
            "turn_count": 0,
            "broker_request_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "occupied_worker_count": 0,
            "docker_invocation_count": 0,
            "database_invocation_count": 0,
        },
        "cleanup": {
            "process_wait_completed": process_absent,
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
            "raw_environment_retained": False,
            "raw_logs_retained": False,
            "npm_cache_retained_by_boot": False,
        },
    }
    evidence_schema = json.loads(EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(evidence, evidence_schema)
    OPERATION_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(canonical_json_bytes(evidence))
    REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
    if result != "pass":
        raise RecoveryBootError(f"native_recovery_boot_failed:{failure}") from error
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        if args.check:
            projection = deterministic_check(args.cache_root)
            print(
                json.dumps(
                    {
                        "result": "pass",
                        "package_count": projection["package_count"],
                        "runner_sha256": projection["runner"]["sha256"],
                        "guard_sha256": projection["guard"]["sha256"],
                    }
                )
            )
        else:
            evidence = execute_boot(args.cache_root)
            print(
                json.dumps(
                    {"result": evidence["result"], "attempt_id": evidence["attempt_id"]}
                )
            )
    except (
        RecoveryBootError,
        ProofError,
        GuardError,
        jsonschema.ValidationError,
    ) as error:
        print(json.dumps({"result": "fail", "error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

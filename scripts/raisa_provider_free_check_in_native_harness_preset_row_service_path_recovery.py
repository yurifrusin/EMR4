"""Prove and correct rc.7 native preset-row service inputs without a model call."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any

import jsonschema
import yaml

from scripts import (
    raisa_provider_free_check_in_native_harness_preset_validation_subcoordinate_recovery
    as predecessor,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    _network_attempts,
    _terminate_process,
    build_child_environment,
    network_guard_source,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery"
)
TOPIC = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = TOPIC / "contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "contract.schema.json"
STATIC_SCHEMA_PATH = TOPIC / "static-evidence.schema.json"
FIXTURE_SCHEMA_PATH = TOPIC / "fixture-evidence.schema.json"
STATIC_EVIDENCE_PATH = TOPIC / "source-and-effective-root-evidence.json"
FIXTURE_EVIDENCE_PATH = TOPIC / "service-input-fixture-evidence.json"
REPORT_PATH = TOPIC / "service-input-fixture-report.md"
NATIVE_CHECKPOINT_PATH = TOPIC / "native-preexecution-checkpoint.json"
NATIVE_CONSUMED_PATH = TOPIC / "native-service-consumed.json"
NATIVE_TERMINAL_PATH = TOPIC / "native-service-terminal.json"
NATIVE_REPORT_PATH = TOPIC / "native-service-report.md"
NATIVE_SCHEMA_PATH = TOPIC / "native-terminal.schema.json"

SCHEMA_CONTRACT = "ariadne.check_in_preset_row_service_path_contract.v1"
SCHEMA_STATIC = "ariadne.check_in_preset_row_service_path_static_evidence.v1"
SCHEMA_FIXTURE = "ariadne.check_in_preset_row_service_path_fixture_evidence.v1"
RUNNER_SCHEMA = "ariadne.check_in_preset_row_service_path_package_runner.v1"
NATIVE_CHECKPOINT_SCHEMA = "ariadne.check_in_preset_row_service_path_checkpoint.v1"
NATIVE_TERMINAL_SCHEMA = "ariadne.check_in_preset_row_service_path_native_terminal.v1"
PRESET_ID = "emr4-bounded-worker"
PRESET_BYTES = 158
PRESET_SHA256 = "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1"
SHIPPED_IDS = ["code", "cordis", "minimal", "standard"]
CORRECTED_IDS = ["code", "cordis", "emr4-bounded-worker", "minimal", "standard"]
NATIVE_ATTEMPT_ID = "check-in-preset-row-service-native-probe-001"
NATIVE_MARKERS = [
    "EFFECTIVE_ROOTS_ENTERED",
    "EFFECTIVE_ROOTS_PASSED",
    "PRESET_ROW_DISCOVERY_ENTERED",
    "PRESET_ROW_FOUND",
    "PRESET_ROW_HEALTHY",
    "PRESET_BYTES_READ",
    "PRESET_LENGTH_BOUND_PASSED",
    "PRESET_DIGEST_BOUND_PASSED",
]


PACKAGE_RUNNER = r"""
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const emit = (value) => process.stdout.write(JSON.stringify(value));
try {
  const inputPath = process.env.EMR4_PRESET_SERVICE_INPUT;
  const modulePath = process.env.EMR4_PRESET_SERVICE_MODULE;
  if (!inputPath || !modulePath) throw new Error("input");
  const input = JSON.parse(readFileSync(inputPath, "utf8"));
  const { discoverPresets } = await import(pathToFileURL(modulePath).href);
  if (typeof discoverPresets !== "function") throw new Error("export");
  const scenarios = [];
  for (const scenario of input.scenarios) {
    const rows = await discoverPresets(scenario.roots);
    const selected = rows.filter((row) => row?.id === "emr4-bounded-worker");
    let row;
    if (selected.length === 1) {
      const candidate = selected[0];
      const sourceRole = Object.entries(scenario.rolePaths).find(
        ([, path]) => resolve(path) === resolve(candidate.path),
      )?.[0] ?? "unbound";
      let bytes = null;
      let sha256 = null;
      if (candidate.broken === undefined) {
        const payload = readFileSync(candidate.path);
        bytes = payload.length;
        sha256 = createHash("sha256").update(payload).digest("hex");
      }
      row = {
        trust: candidate.trust,
        source_role: sourceRole,
        broken_absent: candidate.broken === undefined,
        bytes,
        sha256,
      };
    }
    scenarios.push({
      scenario: scenario.scenario,
      ids: rows.map((item) => item.id).sort(),
      emr4_count: selected.length,
      ...(row === undefined ? {} : { row }),
    });
  }
  emit({schema_version: "ariadne.check_in_preset_row_service_path_package_runner.v1", result: "pass", scenarios});
} catch {
  emit({schema_version: "ariadne.check_in_preset_row_service_path_package_runner.v1", result: "failed_closed", coordinate: "package_fixture_exception"});
  process.exitCode = 2;
}
"""


def native_runner_source() -> bytes:
    markers = json.dumps(NATIVE_MARKERS)
    return f'''import {{ createHash }} from "node:crypto";
import {{ appendFileSync, readFileSync, writeFileSync }} from "node:fs";
import {{ resolve }} from "node:path";

export const name = "emr4-provider-disabled-preset-row-service-probe";
export const inject = ["agentPresets"];
const EXPECTED = Object.freeze({markers});

function emit(config, seen, marker) {{
  seen.push(marker);
  appendFileSync(config.markerPath, JSON.stringify({{sequence: seen.length, marker}}) + "\\n", "utf8");
}}
function firstMissing(seen) {{
  return EXPECTED.find((marker) => !seen.includes(marker)) ?? "PRESET_DIGEST_BOUND_PASSED";
}}
function terminal(config, value) {{
  writeFileSync(config.terminalPath, JSON.stringify(value) + "\\n", {{encoding: "utf8", flag: "wx"}});
}}
async function run(ctx, config) {{
  const seen = [];
  try {{
    const presets = ctx.get("agentPresets");
    if (!presets || typeof presets.list !== "function" || !Array.isArray(presets.roots)) throw new Error("service");
    emit(config, seen, "EFFECTIVE_ROOTS_ENTERED");
    if (presets.roots.length !== 2) throw new Error("roots");
    if (resolve(presets.roots[0].path) !== resolve(config.shippedRoot) || presets.roots[0].trust !== "system") throw new Error("shipped");
    if (resolve(presets.roots[1].path) !== resolve(config.userRoot) || presets.roots[1].trust !== "user") throw new Error("user");
    emit(config, seen, "EFFECTIVE_ROOTS_PASSED");
    emit(config, seen, "PRESET_ROW_DISCOVERY_ENTERED");
    const rows = await presets.list();
    const selected = rows.filter((row) => row?.id === "emr4-bounded-worker");
    if (selected.length !== 1) throw new Error("row");
    const preset = selected[0];
    if (resolve(preset.path) !== resolve(config.presetPath) || preset.trust !== "user") throw new Error("identity");
    emit(config, seen, "PRESET_ROW_FOUND");
    if (preset.broken !== undefined) throw new Error("health");
    emit(config, seen, "PRESET_ROW_HEALTHY");
    const payload = readFileSync(preset.path);
    emit(config, seen, "PRESET_BYTES_READ");
    if (payload.length !== {PRESET_BYTES}) throw new Error("length");
    emit(config, seen, "PRESET_LENGTH_BOUND_PASSED");
    if (createHash("sha256").update(payload).digest("hex") !== "{PRESET_SHA256}") throw new Error("digest");
    emit(config, seen, "PRESET_DIGEST_BOUND_PASSED");
    terminal(config, {{schema_version: "emr4.check-in-preset-row-service-native-runner.v1", result: "pass", terminal_coordinate: "PRESET_DIGEST_BOUND_PASSED", markers: seen}});
    ctx.get("appExit")(0);
  }} catch {{
    terminal(config, {{schema_version: "emr4.check-in-preset-row-service-native-runner.v1", result: "failed_closed", terminal_coordinate: firstMissing(seen), markers: seen}});
    ctx.get("appExit")(1);
  }}
}}

export function apply(ctx, config) {{ void run(ctx, config); }}
'''.encode("utf-8")


def corrected_native_profile_patch(root: Path) -> bytes:
    text = predecessor.native_profile_patch(root).decode("utf-8")
    if text.count("includeUserRoot: false") != 1:
        raise ServicePathRecoveryError("predecessor_user_root_switch_not_unique")
    text = text.replace("includeUserRoot: false", "includeUserRoot: true")
    text = text.replace(
        "emr4-provider-disabled-preset-validation-probe",
        "emr4-provider-disabled-preset-row-service-probe",
    )
    preset_line = (
        "        presetPath: "
        + json.dumps(
            str(
                (
                    root
                    / "home"
                    / ".agent-presets"
                    / PRESET_ID
                    / "agent.cordis.yml"
                ).resolve()
            )
        )
    )
    if text.count(preset_line) != 1:
        raise ServicePathRecoveryError("corrected_profile_preset_binding_missing")
    installation = _installation_root(predecessor.load_contract())
    shipped_root = (
        installation
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
        / "config"
        / "agent-presets"
    ).resolve()
    extra = (
        "\n        shippedRoot: "
        + json.dumps(str(shipped_root))
        + "\n        userRoot: "
        + json.dumps(str((root / "home" / ".agent-presets").resolve()))
    )
    return text.replace(preset_line, preset_line + extra).encode("utf-8")


def validate_native_candidate(root: Path) -> dict[str, Any]:
    runner = native_runner_source()
    source = runner.decode("utf-8")
    runner_checks = {
        "single_service_list": source.count("await presets.list()") == 1,
        "exact_root_count": "presets.roots.length !== 2" in source,
        "shipped_root_system": 'presets.roots[0].trust !== "system"' in source,
        "derived_user_root_user": 'presets.roots[1].trust !== "user"' in source,
        "emr4_row_user_trust": 'preset.trust !== "user"' in source,
        "no_agent_create": "agents.create" not in source,
        "no_preset_mount": ".mount(" not in source,
        "no_session_or_turn": "SessionId" not in source and "createUserMessage" not in source,
        "no_raw_error": "error.message" not in source and "error.stack" not in source,
        "one_terminal_write": source.count("writeFileSync(config.terminalPath") == 1,
    }
    if not all(runner_checks.values()):
        raise ServicePathRecoveryError("native_candidate_runner_invalid")
    profile = corrected_native_profile_patch(root)
    rows = yaml.safe_load(profile)
    if not isinstance(rows, list):
        raise ServicePathRecoveryError("corrected_profile_not_array")
    preset_service = _inserted_row(profile, "agent-presets")
    config = preset_service.get("config")
    if not isinstance(config, dict) or config.get("includeUserRoot") is not True:
        raise ServicePathRecoveryError("corrected_profile_user_root_not_enabled")
    native_runner = _inserted_row(profile, "emr4-provider-disabled-preset-row-service-probe")
    if native_runner.get("inject") != ["agentPresets"]:
        raise ServicePathRecoveryError("corrected_profile_inject_invalid")
    if set(native_runner.get("config", {})) != {
        "markerPath",
        "terminalPath",
        "presetPath",
        "shippedRoot",
        "userRoot",
    }:
        raise ServicePathRecoveryError("corrected_profile_runner_config_invalid")
    if any(token in profile.decode("utf-8") for token in ("attempt-006", "http://", "https://")):
        raise ServicePathRecoveryError("corrected_profile_forbidden_surface")
    return {
        "runner": {"bytes": len(runner), "sha256": _sha256(runner), **runner_checks},
        "profile": {
            "bytes": len(profile),
            "sha256": _sha256(profile),
            "include_user_root": True,
            "runner_inject": ["agentPresets"],
        },
    }


def _write_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(_canonical_json(value))


def load_native_checkpoint(path: Path | None = None) -> dict[str, Any]:
    path = NATIVE_CHECKPOINT_PATH if path is None else path
    value = _load_json(path)
    expected = {
        "schema_version",
        "operation_id",
        "status",
        "semantic_candidate_source",
        "semantic_review_receipt",
        "semantic_review_receipt_sha256",
        "executor_candidate_source",
        "executor_review_receipt",
        "executor_review_receipt_sha256",
        "attempt_id",
        "native_process_limit",
        "automatic_retry_limit",
        "timeout_seconds",
        "markers",
        "runner_sha256",
        "checkpoint_admitted",
    }
    if set(value) != expected:
        raise ServicePathRecoveryError("native_checkpoint_shape_invalid")
    if (
        value["schema_version"] != NATIVE_CHECKPOINT_SCHEMA
        or value["operation_id"] != OPERATION_ID
        or value["status"] != "admitted"
        or value["attempt_id"] != NATIVE_ATTEMPT_ID
        or value["native_process_limit"] != 1
        or value["automatic_retry_limit"] != 0
        or value["timeout_seconds"] != 60
        or value["markers"] != NATIVE_MARKERS
        or value["runner_sha256"] != _sha256(native_runner_source())
        or value["checkpoint_admitted"] is not True
    ):
        raise ServicePathRecoveryError("native_checkpoint_binding_invalid")
    for prefix in ("semantic", "executor"):
        source = value[f"{prefix}_candidate_source"]
        if not isinstance(source, str) or len(source) != 40:
            raise ServicePathRecoveryError("native_checkpoint_source_invalid")
        receipt_path = REPO_ROOT / value[f"{prefix}_review_receipt"]
        if not receipt_path.is_file() or receipt_path.is_symlink():
            raise ServicePathRecoveryError("native_checkpoint_review_missing")
        if _file_sha256(receipt_path) != value[f"{prefix}_review_receipt_sha256"]:
            raise ServicePathRecoveryError("native_checkpoint_review_digest_mismatch")
        receipt = _load_json(receipt_path)
        if (
            receipt.get("status") != "completed"
            or receipt.get("decision") != "pass"
            or receipt.get("head_before") != source
            or receipt.get("head_after") != source
            or receipt.get("dirty_after") is not False
        ):
            raise ServicePathRecoveryError("native_checkpoint_review_invalid")
    ancestry = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            value["semantic_candidate_source"],
            value["executor_candidate_source"],
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if ancestry.returncode != 0:
        raise ServicePathRecoveryError("native_checkpoint_candidate_ancestry_invalid")
    if NATIVE_CONSUMED_PATH.exists() or NATIVE_TERMINAL_PATH.exists():
        raise ServicePathRecoveryError("native_checkpoint_already_consumed")
    return value


def _read_markers(path: Path) -> list[str]:
    if not path.is_file():
        return []
    markers: list[str] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ServicePathRecoveryError("native_marker_json_invalid") from error
        if row != {"sequence": index, "marker": row.get("marker")}:
            raise ServicePathRecoveryError("native_marker_shape_invalid")
        marker = row["marker"]
        if marker not in NATIVE_MARKERS or index > len(NATIVE_MARKERS):
            raise ServicePathRecoveryError("native_marker_value_invalid")
        markers.append(marker)
    if markers != NATIVE_MARKERS[: len(markers)]:
        raise ServicePathRecoveryError("native_marker_order_invalid")
    return markers


def _read_runner_terminal(path: Path, markers: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ServicePathRecoveryError("native_runner_terminal_json_invalid") from error
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "result",
        "terminal_coordinate",
        "markers",
    }:
        raise ServicePathRecoveryError("native_runner_terminal_shape_invalid")
    if value["schema_version"] != "emr4.check-in-preset-row-service-native-runner.v1":
        raise ServicePathRecoveryError("native_runner_terminal_schema_invalid")
    if value["result"] not in {"pass", "failed_closed"} or value["markers"] != markers:
        raise ServicePathRecoveryError("native_runner_terminal_result_invalid")
    expected_coordinate = (
        NATIVE_MARKERS[-1]
        if markers == NATIVE_MARKERS
        else NATIVE_MARKERS[len(markers)]
    )
    if value["terminal_coordinate"] != expected_coordinate:
        raise ServicePathRecoveryError("native_runner_terminal_coordinate_invalid")
    if (value["result"] == "pass") != (markers == NATIVE_MARKERS):
        raise ServicePathRecoveryError("native_runner_terminal_pass_invalid")
    return value


def execute_native_service_confirmation() -> dict[str, Any]:
    checkpoint = load_native_checkpoint()
    contract = load_contract()
    paths = _source_paths(contract)
    installation = _installation_root(contract)
    manifest = _load_json(paths["dsh_manifest"])
    bin_relative = manifest.get("bin", {}).get("dsh")
    if not isinstance(bin_relative, str):
        raise ServicePathRecoveryError("native_bin_binding_missing")
    bin_path = installation / "node_modules" / "@deepseek-ai" / "dsh" / bin_relative
    if not bin_path.is_file() or bin_path.is_symlink():
        raise ServicePathRecoveryError("native_bin_unavailable")

    consumed = {
        "schema_version": "ariadne.check_in_preset_row_service_path_consumed.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": NATIVE_ATTEMPT_ID,
        "state": "consumed",
        "native_process_limit": 1,
        "automatic_retry_count": 0,
        "resume_permitted": False,
        "provider_enabled": False,
        "executor_candidate_source": checkpoint["executor_candidate_source"],
    }
    _write_exclusive(NATIVE_CONSUMED_PATH, consumed)

    root_path: Path | None = None
    process: subprocess.Popen[bytes] | None = None
    process_started = False
    start: float | None = None
    exit_code: int | None = None
    failure_coordinate: str | None = None
    removed_environment_names = 0
    stdout_sha256 = _sha256(b"")
    stderr_sha256 = _sha256(b"")
    stdout_bytes = 0
    stderr_bytes = 0
    markers: list[str] = []
    runner_terminal: dict[str, Any] | None = None
    network_attempt_count = 0
    try:
        with tempfile.TemporaryDirectory(
            prefix="emr4-preset-row-native-",
            dir=predecessor.lifecycle.DISPOSABLE_PARENT,
        ) as temp:
            root_path = Path(temp)
            home = root_path / "home"
            profile = home / "profiles" / "headless"
            proof = profile / "proof"
            workspace = root_path / "workspace"
            marker_path = root_path / "markers.jsonl"
            runner_terminal_path = root_path / "runner-terminal.json"
            network_path = root_path / "network.jsonl"
            stdout_path = root_path / "stdout.log"
            stderr_path = root_path / "stderr.log"
            workspace.mkdir()
            proof.mkdir(parents=True)
            preset_path = home / ".agent-presets" / PRESET_ID / "agent.cordis.yml"
            preset_path.parent.mkdir(parents=True)
            preset_path.write_bytes(predecessor.CANONICAL_PRESET_PATH.read_bytes())
            (profile / "package.json").write_text(
                json.dumps(
                    {
                        "name": "dsh-profile-headless",
                        "private": True,
                        "dependencies": {},
                        "dsh": {
                            "profile": {
                                "bundles": [
                                    "@deepseek-ai/dsh-base",
                                    "@deepseek-ai/dsh-headless",
                                ]
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            (profile / "pnpm-workspace.yaml").write_text(
                "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
                encoding="utf-8",
                newline="\n",
            )
            (proof / "runner.mjs").write_bytes(native_runner_source())
            profile_payload = corrected_native_profile_patch(root_path)
            validate_native_candidate(root_path)
            (profile / "cordis.patch.yml").write_bytes(profile_payload)
            guard_path = root_path / "network-guard.mjs"
            guard_path.write_bytes(network_guard_source())
            environment, removed_environment_names = build_child_environment(
                home, guard_path, network_path
            )
            environment["DSH_CWD"] = str(workspace)
            environment["DSH_PERMISSION_MODE"] = "workspace-write"
            environment["DSH_TOOLS_MODE"] = "native"
            command = [
                shutil.which("node") or "node",
                "--expose-internals",
                str(bin_path),
                "--profile",
                "headless",
                "provider-disabled preset row service probe",
            ]
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                start = time.monotonic()
                process = subprocess.Popen(
                    command,
                    cwd=workspace,
                    env=environment,
                    stdout=stdout,
                    stderr=stderr,
                    shell=False,
                )
                process_started = True
                try:
                    exit_code = process.wait(timeout=checkpoint["timeout_seconds"])
                except subprocess.TimeoutExpired:
                    failure_coordinate = "NATIVE_PROCESS_TIMEOUT"
                    _terminate_process(process)
                    exit_code = process.returncode
            stdout_bytes = stdout_path.stat().st_size
            stderr_bytes = stderr_path.stat().st_size
            stdout_sha256 = _file_sha256(stdout_path)
            stderr_sha256 = _file_sha256(stderr_path)
            markers = _read_markers(marker_path)
            runner_terminal = _read_runner_terminal(runner_terminal_path, markers)
            network_attempt_count = len(_network_attempts(network_path))
            if network_attempt_count != 0:
                failure_coordinate = "NETWORK_ATTEMPT_OBSERVED"
    except Exception:
        if failure_coordinate is None:
            failure_coordinate = "NATIVE_SERVICE_EXECUTION_EXCEPTION"
    finally:
        if process is not None and process.poll() is None:
            _terminate_process(process)
        process_absent = process is None or process.poll() is not None
        disposable_absent = root_path is None or not root_path.exists()

    duration_ms = 0 if start is None else max(0, int((time.monotonic() - start) * 1000))
    passed = (
        process_started
        and exit_code == 0
        and failure_coordinate is None
        and runner_terminal is not None
        and runner_terminal["result"] == "pass"
        and markers == NATIVE_MARKERS
        and network_attempt_count == 0
        and process_absent
        and disposable_absent
    )
    terminal_coordinate = (
        NATIVE_MARKERS[-1]
        if passed
        else failure_coordinate
        or (NATIVE_MARKERS[len(markers)] if len(markers) < len(NATIVE_MARKERS) else NATIVE_MARKERS[-1])
    )
    terminal = {
        "schema_version": NATIVE_TERMINAL_SCHEMA,
        "operation_id": OPERATION_ID,
        "attempt_id": NATIVE_ATTEMPT_ID,
        "result": "pass" if passed else "failed_closed",
        "terminal_coordinate": terminal_coordinate,
        "markers": markers,
        "package": {
            "installation_id": installation.name,
            "name": "@deepseek-ai/dsh",
            "version": manifest.get("version"),
            "package_lock_sha256": _file_sha256(paths["lockfile"]),
        },
        "launch": {
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "stdout_bytes": stdout_bytes,
            "stdout_sha256": stdout_sha256,
            "stderr_bytes": stderr_bytes,
            "stderr_sha256": stderr_sha256,
            "raw_logs_retained": False,
            "credential_environment_names_removed_count": removed_environment_names,
        },
        "counts": {
            "native_processes": 1 if process_started else 0,
            "automatic_retries": 0,
            "agent_sessions": 0,
            "turns": 0,
            "broker_requests": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": network_attempt_count,
            "docker_invocations": 0,
            "database_invocations": 0,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": disposable_absent,
        },
        "runner_terminal_valid": runner_terminal is not None,
        "network_ledger_valid": network_attempt_count == 0,
        "claim_boundary": "provider_disabled_native_preset_row_service_confirmation_only_no_agent_mount_deepseek_database_or_product_claim",
    }
    jsonschema.Draft202012Validator(_load_json(NATIVE_SCHEMA_PATH)).validate(terminal)
    _write_exclusive(NATIVE_TERMINAL_PATH, terminal)
    NATIVE_REPORT_PATH.write_text(render_native_report(terminal), encoding="utf-8", newline="\n")
    return terminal


def render_native_report(terminal: dict[str, Any]) -> str:
    return f"""# Native Harness preset-row service confirmation report

- Result: `{terminal['result']}`
- Terminal coordinate: `{terminal['terminal_coordinate']}`
- Markers reached: `{', '.join(terminal['markers']) or 'none'}`
- Native processes / automatic retries: `{terminal['counts']['native_processes']} / 0`
- Agents / turns / provider / network: `0 / 0 / 0 / {terminal['counts']['network_attempts']}`
- Process and disposable root absent: `{str(terminal['cleanup']['process_absent']).lower()} / {str(terminal['cleanup']['disposable_root_absent']).lower()}`

This is one consumed provider-disabled native service-row reading. It proves no
preset mount, agent creation, DeepSeek request, model quality, attempt 006,
database or product behavior.
"""


class ServicePathRecoveryError(RuntimeError):
    """One closed service-path coordinate failed."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ServicePathRecoveryError("json_root_not_object")
    return value


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_json(value))


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_json(path)
    schema = _load_json(CONTRACT_SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(contract)
    if contract["schema_version"] != SCHEMA_CONTRACT:
        raise ServicePathRecoveryError("contract_schema_version_mismatch")
    if contract["operation_id"] != OPERATION_ID:
        raise ServicePathRecoveryError("contract_operation_mismatch")
    if contract["preset"] != {
        "id": PRESET_ID,
        "bytes": PRESET_BYTES,
        "sha256": PRESET_SHA256,
    }:
        raise ServicePathRecoveryError("contract_preset_mismatch")
    if contract["expected_shipped_ids"] != SHIPPED_IDS:
        raise ServicePathRecoveryError("contract_shipped_ids_mismatch")
    return contract


def _installation_root(contract: dict[str, Any]) -> Path:
    root = Path(contract["retained_installation_root"]).resolve()
    if root.name != "deepseek-check-in-attachment-observability-native-001":
        raise ServicePathRecoveryError("retained_installation_name_mismatch")
    if not root.is_dir() or root.is_symlink():
        raise ServicePathRecoveryError("retained_installation_unavailable")
    return root


def _source_paths(contract: dict[str, Any]) -> dict[str, Path]:
    root = _installation_root(contract)
    deepseek = root / "node_modules" / "@deepseek-ai"
    boot_candidates = [
        path
        for path in (deepseek / "dsh" / "lib").glob("profile-boot-*.js")
        if "function composeProfile" in path.read_text(encoding="utf-8")
    ]
    if len(boot_candidates) != 1:
        raise ServicePathRecoveryError("profile_boot_source_not_unique")
    return {
        "lockfile": root / "package-lock.json",
        "dsh_manifest": deepseek / "dsh" / "package.json",
        "profile_boot": boot_candidates[0],
        "presets_manifest": deepseek / "dsh-agent-presets" / "package.json",
        "presets_service": deepseek / "dsh-agent-presets" / "lib" / "index.js",
        "home_manifest": deepseek / "dsh-home-paths" / "package.json",
        "home_paths": deepseek / "dsh-home-paths" / "lib" / "index.js",
    }


def _bind_sources(contract: dict[str, Any]) -> tuple[dict[str, Path], list[dict[str, Any]]]:
    paths = _source_paths(contract)
    if any(not path.is_file() or path.is_symlink() for path in paths.values()):
        raise ServicePathRecoveryError("retained_source_unavailable")
    lock = _load_json(paths["lockfile"])
    packages = lock["packages"]
    bound: list[dict[str, Any]] = []
    for package in contract["packages"]:
        row = packages[package["lock_key"]]
        if row.get("version") != package["version"] or row.get("integrity") != package["integrity"]:
            raise ServicePathRecoveryError("retained_package_lock_mismatch")
        for source in package["sources"]:
            path = paths[source["role"]]
            actual = _file_sha256(path)
            if actual != source["sha256"]:
                raise ServicePathRecoveryError("retained_source_digest_mismatch")
            bound.append(
                {
                    "package": package["name"],
                    "role": source["role"],
                    "bytes": path.stat().st_size,
                    "sha256": actual,
                }
            )
    if _file_sha256(paths["lockfile"]) != contract["lockfile_sha256"]:
        raise ServicePathRecoveryError("retained_lockfile_digest_mismatch")
    return paths, bound


def _inserted_row(profile: bytes, row_id: str) -> dict[str, Any]:
    rows = yaml.safe_load(profile)
    if not isinstance(rows, list):
        raise ServicePathRecoveryError("profile_patch_not_array")
    inserted = [
        row
        for patch in rows
        if isinstance(patch, dict) and isinstance(patch.get("insert"), list)
        for row in patch["insert"]
        if isinstance(row, dict) and row.get("id") == row_id
    ]
    if len(inserted) != 1:
        raise ServicePathRecoveryError("profile_inserted_row_not_unique")
    return inserted[0]


def effective_root_roles(include_user_root: bool) -> list[dict[str, str]]:
    roots = [{"role": "shipped", "trust": "system"}]
    if include_user_root:
        roots.append({"role": "derived_user", "trust": "user"})
    return roots


def build_static_evidence(contract: dict[str, Any]) -> dict[str, Any]:
    paths, bound = _bind_sources(contract)
    profile_boot = paths["profile_boot"].read_text(encoding="utf-8")
    presets = paths["presets_service"].read_text(encoding="utf-8")
    home = paths["home_paths"].read_text(encoding="utf-8")
    checks = {
        "profile_rows_composed_before_forced_overlay": (
            "const rows = /* @__PURE__ */ new Map();" in profile_boot
            and "const composedOverlays = [...overlays];" in profile_boot
        ),
        "native_overlay_targets_agent_presets": (
            'if (rows.has("agent-presets")) composedOverlays.push({' in profile_boot
        ),
        "native_overlay_preserves_prior_config": (
            '...rows.get("agent-presets")?.config ?? {}' in profile_boot
        ),
        "native_overlay_replaces_roots_with_shipped_system": all(
            token in profile_boot
            for token in (
                "roots: [{",
                "path: SHIPPED_PRESET_ROOT",
                'trust: "system"',
            )
        ),
        "native_overlay_is_appended_after_user_overlays": (
            profile_boot.index("const composedOverlays = [...overlays];")
            < profile_boot.index('if (rows.has("agent-presets"))')
        ),
        "service_resolved_roots_include_configured_first": (
            "this.resolvedRoots = config.includeUserRoot ? [...config.roots, {"
            in presets
        ),
        "service_derived_user_root_exact": all(
            token in presets
            for token in (
                "path: dshHomePath(USER_PRESET_DIR)",
                'trust: "user"',
                'const USER_PRESET_DIR = ".agent-presets";',
            )
        ),
        "service_false_branch_excludes_user_root": (
            "}] : [...config.roots];" in presets
        ),
        "service_list_uses_resolved_roots": (
            "return await discoverPresets(this.resolvedRoots);" in presets
        ),
        "home_path_reads_dsh_home_at_call_time": all(
            token in home
            for token in (
                'const DSH_HOME_ENV = "DSH_HOME";',
                "const fromEnv = env[DSH_HOME_ENV];",
                "function dshHomePath(...segments)",
                "return join(resolveDshHome(), ...segments);",
            )
        ),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise ServicePathRecoveryError("source_semantics_mismatch:" + ",".join(failed))

    shipped_root = (paths["profile_boot"].parent / ".." / "config" / "agent-presets").resolve()
    if not shipped_root.is_dir() or shipped_root.is_symlink():
        raise ServicePathRecoveryError("shipped_root_unavailable")
    shipped_ids = sorted(path.name for path in shipped_root.iterdir() if path.is_dir())
    if shipped_ids != SHIPPED_IDS:
        raise ServicePathRecoveryError("shipped_roster_mismatch")

    fake_root = Path("C:/emr4-service-path-fixture").resolve()
    predecessor_profile = predecessor.native_profile_patch(fake_root)
    preset_row = _inserted_row(predecessor_profile, "agent-presets")
    configured = preset_row.get("config")
    if not isinstance(configured, dict):
        raise ServicePathRecoveryError("predecessor_preset_config_missing")
    if configured.get("includeUserRoot") is not False:
        raise ServicePathRecoveryError("predecessor_user_root_not_disabled")
    if len(configured.get("roots", [])) != 1:
        raise ServicePathRecoveryError("predecessor_configured_root_count_mismatch")

    forced_config = dict(configured)
    forced_config["roots"] = [{"path": str(shipped_root), "trust": "system"}]
    predecessor_roles = effective_root_roles(bool(forced_config["includeUserRoot"]))
    corrected_config = dict(forced_config)
    corrected_config["includeUserRoot"] = True
    corrected_roles = effective_root_roles(bool(corrected_config["includeUserRoot"]))
    if predecessor_roles != [{"role": "shipped", "trust": "system"}]:
        raise ServicePathRecoveryError("predecessor_effective_root_projection_mismatch")
    if corrected_roles != [
        {"role": "shipped", "trust": "system"},
        {"role": "derived_user", "trust": "user"},
    ]:
        raise ServicePathRecoveryError("corrected_effective_root_projection_mismatch")

    direct = _load_json(predecessor.PACKAGE_EVIDENCE_PATH)
    if direct.get("result") != "pass" or direct["subcoordinates"]["row_discovery"] != {
        "broken_absent": True,
        "exact_id_count": 1,
        "exact_path": True,
        "exact_trust": True,
    }:
        raise ServicePathRecoveryError("predecessor_direct_scan_not_bound")

    evidence = {
        "schema_version": SCHEMA_STATIC,
        "operation_id": OPERATION_ID,
        "result": "pass",
        "claim_boundary": "pinned_rc7_source_and_role_labelled_effective_root_proof_only_no_native_harness_agent_mount_or_provider_claim",
        "source_files": bound,
        "source_checks": checks,
        "shipped_roster": {"ids": shipped_ids, "emr4_present": PRESET_ID in shipped_ids},
        "root_transformation": {
            "configured_root_replaced_by_native_overlay": True,
            "predecessor_include_user_root": False,
            "predecessor_effective_roots": predecessor_roles,
            "corrected_include_user_root": True,
            "corrected_effective_roots": corrected_roles,
            "direct_scan_explicit_user_root": True,
        },
        "provider_boundary": {
            "package_only_node_processes": 0,
            "native_harness_processes": 0,
            "agent_sessions": 0,
            "turns": 0,
            "broker_requests": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": 0,
            "docker_invocations": 0,
            "database_invocations": 0,
        },
    }
    jsonschema.Draft202012Validator(_load_json(STATIC_SCHEMA_PATH)).validate(evidence)
    return evidence


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    text = payload.decode("utf-8")
    checks = {
        "single_discovery_call": text.count("await discoverPresets(scenario.roots)") == 1,
        "local_module_import": "pathToFileURL(modulePath).href" in text,
        "role_labelled_paths": "source_role: sourceRole" in text,
        "no_agent_create": "agents.create" not in text,
        "no_preset_mount": ".mount(" not in text,
        "no_session_or_turn": "SessionId" not in text and "createUserMessage" not in text,
        "no_provider": "deepseek" not in text.casefold(),
        "no_raw_error": "error.message" not in text and "error.stack" not in text,
    }
    if not all(checks.values()):
        raise ServicePathRecoveryError("package_runner_shape_invalid")
    return {"bytes": len(payload), "sha256": _sha256(payload), **checks}


def _validate_runner_output(value: dict[str, Any]) -> list[dict[str, Any]]:
    if value.get("schema_version") != RUNNER_SCHEMA or value.get("result") != "pass":
        raise ServicePathRecoveryError("package_runner_failed_closed")
    scenarios = value.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 5:
        raise ServicePathRecoveryError("package_runner_scenario_count_mismatch")
    if [item.get("scenario") for item in scenarios] != [
        "predecessor_shipped_only",
        "corrected_shipped_plus_user",
        "missing_user_root",
        "earlier_system_duplicate",
        "configured_root_displaced",
    ]:
        raise ServicePathRecoveryError("package_runner_scenario_order_mismatch")
    return scenarios


def _normalized_scenarios(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name = {item["scenario"]: item for item in scenarios}
    predecessor_row = by_name["predecessor_shipped_only"]
    corrected = by_name["corrected_shipped_plus_user"]
    missing = by_name["missing_user_root"]
    duplicate = by_name["earlier_system_duplicate"]
    displaced = by_name["configured_root_displaced"]
    if predecessor_row != {
        "scenario": "predecessor_shipped_only",
        "ids": SHIPPED_IDS,
        "emr4_count": 0,
    }:
        raise ServicePathRecoveryError("predecessor_fixture_mismatch")
    if corrected != {
        "scenario": "corrected_shipped_plus_user",
        "ids": CORRECTED_IDS,
        "emr4_count": 1,
        "row": {
            "trust": "user",
            "source_role": "derived_user",
            "broken_absent": True,
            "bytes": PRESET_BYTES,
            "sha256": PRESET_SHA256,
        },
    }:
        raise ServicePathRecoveryError("corrected_fixture_mismatch")
    if missing != {
        "scenario": "missing_user_root",
        "ids": SHIPPED_IDS,
        "emr4_count": 0,
    }:
        raise ServicePathRecoveryError("missing_user_fixture_mismatch")
    expected_duplicate = {
        "scenario": "earlier_system_duplicate",
        "ids": [PRESET_ID],
        "emr4_count": 1,
        "row": {
            "trust": "system",
            "source_role": "earlier_system",
            "broken_absent": True,
            "bytes": PRESET_BYTES,
            "sha256": PRESET_SHA256,
        },
    }
    if duplicate != expected_duplicate:
        raise ServicePathRecoveryError("duplicate_shadow_fixture_mismatch")
    if displaced != {
        "scenario": "configured_root_displaced",
        "ids": SHIPPED_IDS,
        "emr4_count": 0,
    }:
        raise ServicePathRecoveryError("configured_displacement_fixture_mismatch")
    return [
        {"scenario": predecessor_row["scenario"], "decision": "emr4_absent", **predecessor_row},
        {"scenario": corrected["scenario"], "decision": "accepted_exact_user_row", **corrected},
        {"scenario": missing["scenario"], "decision": "emr4_absent", **missing},
        {"scenario": duplicate["scenario"], "decision": "rejected_shadowed", **duplicate},
        {"scenario": displaced["scenario"], "decision": "configured_root_displaced", **displaced},
    ]


def run_fixture_characterization(contract: dict[str, Any]) -> dict[str, Any]:
    static = build_static_evidence(contract)
    paths = _source_paths(contract)
    package_module = paths["presets_service"]
    shipped_root = (paths["profile_boot"].parent / ".." / "config" / "agent-presets").resolve()
    runner = validate_runner_source(PACKAGE_RUNNER.encode("utf-8"))
    process_started = False
    disposable_path: Path | None = None
    network_attempt_count = 0
    removed_environment_names = 0
    try:
        with tempfile.TemporaryDirectory(
            prefix="emr4-preset-service-fixture-",
            dir=predecessor.lifecycle.DISPOSABLE_PARENT,
        ) as temp:
            disposable_path = Path(temp)
            home = disposable_path / "home"
            user_root = home / ".agent-presets"
            user_preset = user_root / PRESET_ID / "agent.cordis.yml"
            user_preset.parent.mkdir(parents=True)
            user_preset.write_bytes(predecessor.CANONICAL_PRESET_PATH.read_bytes())
            duplicate_root = disposable_path / "earlier-system"
            duplicate_preset = duplicate_root / PRESET_ID / "agent.cordis.yml"
            duplicate_preset.parent.mkdir(parents=True)
            duplicate_preset.write_bytes(predecessor.CANONICAL_PRESET_PATH.read_bytes())
            configured_root = disposable_path / "configured-but-displaced"
            configured_preset = configured_root / PRESET_ID / "agent.cordis.yml"
            configured_preset.parent.mkdir(parents=True)
            configured_preset.write_bytes(predecessor.CANONICAL_PRESET_PATH.read_bytes())
            missing_root = disposable_path / "missing-user"
            runner_path = disposable_path / "runner.mjs"
            input_path = disposable_path / "input.json"
            network_path = disposable_path / "network.jsonl"
            guard_path = disposable_path / "network-guard.mjs"
            runner_path.write_bytes(PACKAGE_RUNNER.encode("utf-8"))
            guard_path.write_bytes(network_guard_source())
            inputs = {
                "scenarios": [
                    {
                        "scenario": "predecessor_shipped_only",
                        "roots": [{"path": str(shipped_root), "trust": "system"}],
                        "rolePaths": {},
                    },
                    {
                        "scenario": "corrected_shipped_plus_user",
                        "roots": [
                            {"path": str(shipped_root), "trust": "system"},
                            {"path": str(user_root), "trust": "user"},
                        ],
                        "rolePaths": {"derived_user": str(user_preset)},
                    },
                    {
                        "scenario": "missing_user_root",
                        "roots": [
                            {"path": str(shipped_root), "trust": "system"},
                            {"path": str(missing_root), "trust": "user"},
                        ],
                        "rolePaths": {},
                    },
                    {
                        "scenario": "earlier_system_duplicate",
                        "roots": [
                            {"path": str(duplicate_root), "trust": "system"},
                            {"path": str(user_root), "trust": "user"},
                        ],
                        "rolePaths": {
                            "earlier_system": str(duplicate_preset),
                            "derived_user": str(user_preset),
                        },
                    },
                    {
                        "scenario": "configured_root_displaced",
                        "roots": [{"path": str(shipped_root), "trust": "system"}],
                        "rolePaths": {"configured": str(configured_preset)},
                    },
                ]
            }
            input_path.write_bytes(_canonical_json(inputs))
            environment, removed_environment_names = build_child_environment(
                home, guard_path, network_path
            )
            environment["EMR4_PRESET_SERVICE_INPUT"] = str(input_path)
            environment["EMR4_PRESET_SERVICE_MODULE"] = str(package_module)
            result = subprocess.run(
                [shutil.which("node") or "node", str(runner_path)],
                cwd=disposable_path,
                env=environment,
                capture_output=True,
                check=False,
                timeout=30,
            )
            process_started = True
            network_attempt_count = len(_network_attempts(network_path))
            if result.returncode != 0 or result.stderr != b"" or network_attempt_count != 0:
                raise ServicePathRecoveryError("package_fixture_process_failed")
            try:
                projected = json.loads(result.stdout.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ServicePathRecoveryError("package_fixture_output_invalid") from error
            if not isinstance(projected, dict):
                raise ServicePathRecoveryError("package_fixture_output_not_object")
            scenarios = _normalized_scenarios(_validate_runner_output(projected))
    finally:
        disposable_absent = disposable_path is None or not disposable_path.exists()
    if not process_started or not disposable_absent:
        raise ServicePathRecoveryError("package_fixture_cleanup_failed")

    evidence = {
        "schema_version": SCHEMA_FIXTURE,
        "operation_id": OPERATION_ID,
        "result": "pass",
        "claim_boundary": "pinned_rc7_provider_free_service_input_fixture_only_no_native_harness_agent_mount_or_provider_claim",
        "static_source_gate": static["result"],
        "runner": runner,
        "scenarios": scenarios,
        "correction_candidate": {
            "include_user_root": True,
            "effective_root_roles": effective_root_roles(True),
            "emr4_row_trust": "user",
            "installed_package_mutated": False,
            "shipped_preset_mutated": False,
        },
        "native_candidate": validate_native_candidate(
            Path("C:/emr4-service-path-native-candidate").resolve()
        ),
        "process_boundary": {
            "package_only_node_processes": 1,
            "native_harness_processes": 0,
            "agent_sessions": 0,
            "turns": 0,
            "broker_requests": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": network_attempt_count,
            "docker_invocations": 0,
            "database_invocations": 0,
        },
        "cleanup": {
            "package_process_absent": True,
            "disposable_root_absent": disposable_absent,
        },
        "credential_environment_names_removed_count": removed_environment_names,
        "raw_stdout_retained": False,
        "raw_stderr_retained": False,
        "native_process_checkpoint_admitted": False,
    }
    jsonschema.Draft202012Validator(_load_json(FIXTURE_SCHEMA_PATH)).validate(evidence)
    return evidence


def render_report(evidence: dict[str, Any]) -> str:
    corrected = next(
        item for item in evidence["scenarios"] if item["scenario"] == "corrected_shipped_plus_user"
    )
    return f"""# Native Harness preset-row service-path fixture report

- Result: `{evidence['result']}`
- Predecessor effective roots: shipped `system` only
- Corrected effective roots: shipped `system`, then derived user `user`
- Corrected EMR4 row: `{corrected['decision']}`
- Exact row trust / bytes / digest: `{corrected['row']['trust']} / {corrected['row']['bytes']} / {corrected['row']['sha256']}`
- Package-only Node / native Harness processes: `1 / 0`
- Agent / turn / provider / network counts: `0 / 0 / 0 / 0`
- Disposable process and root absent: `true / true`

The rc.7 native profile composer replaces configured preset roots with its
shipped system root. The predecessor additionally disabled the derived user
root, excluding the canonical EMR4 preset under `$DSH_HOME/.agent-presets`.
The closed fixture proves that re-enabling the derived user root produces the
expected shipped-plus-user roster and exactly one healthy, user-trust EMR4 row.

This is provider-free package/service-input evidence. It does not prove a
native Harness process, preset mount, agent, DeepSeek request, model quality,
attempt 006, database or product behavior.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("static", "fixture", "native", "all"), default="all")
    args = parser.parse_args()
    contract = load_contract()
    if args.stage in {"static", "all"}:
        static = build_static_evidence(contract)
        _write_json(STATIC_EVIDENCE_PATH, static)
    if args.stage in {"fixture", "all"}:
        evidence = run_fixture_characterization(contract)
        _write_json(FIXTURE_EVIDENCE_PATH, evidence)
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
    if args.stage == "native":
        terminal = execute_native_service_confirmation()
        return 0 if terminal["result"] == "pass" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

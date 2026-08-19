"""Deterministic recovery for native-Harness preterminal observability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any

from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    _cache_blob_path,
    _default_cache_root,
    build_guard_source,
    load_contract as load_guard_contract,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    DISPOSABLE_PARENT,
    _network_attempts,
    _offline_install,
    _verify_installed_source,
    build_child_environment,
    canonical_json_bytes,
    network_guard_source,
    sha256_bytes,
    sha256_file,
    verify_tarball,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = "deepseek-native-harness-provider-free-preterminal-activation-observability-recovery"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
EVIDENCE_PATH = OPERATION_ROOT / "provider-free-preterminal-observability-recovery-evidence.json"
REPORT_PATH = OPERATION_ROOT / "provider-free-preterminal-observability-recovery-report.md"
TIMING_EVIDENCE_PATH = OPERATION_ROOT / "future-controller-timing-design-evidence.json"
FAILED_OPERATION_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof"
)
FAILED_EVIDENCE_PATH = FAILED_OPERATION_ROOT / "provider-free-effective-tool-native-boot-evidence.json"
FAILED_CONTRACT_PATH = FAILED_OPERATION_ROOT / "contract.json"
FAILED_CONTROLLER_PATH = (
    REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof.py"
)
EVIDENCE_SCHEMA = "ariadne.deepseek_native_harness_preterminal_observability_recovery_evidence.v1"
ACTIVATION_SCHEMA = "ariadne.deepseek_native_harness_preterminal_activation.v1"
TERMINAL_SCHEMA = "ariadne.deepseek_native_harness_effective_tool_native_boot_terminal.v1"


class RecoveryError(RuntimeError):
    """A closed deterministic recovery rejection."""


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != (
        "ariadne.deepseek_native_harness_preterminal_observability_recovery_contract.v1"
    ):
        raise RecoveryError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise RecoveryError("contract_operation_mismatch")
    if contract.get("probe") != {
        "offline_materialisation_count": 1,
        "non_harness_node_import_count": 1,
        "native_harness_process_count": 0,
        "online_fallback": False,
        "lifecycle_scripts": False,
    }:
        raise RecoveryError("contract_probe_boundary_mismatch")
    return contract


def diagnose_failed_attempt(contract: dict[str, Any]) -> dict[str, Any]:
    attempt = contract["immutable_attempt"]
    if sha256_file(FAILED_EVIDENCE_PATH) != attempt["evidence_sha256"]:
        raise RecoveryError("immutable_attempt_evidence_drift")
    if sha256_file(FAILED_CONTROLLER_PATH) != attempt["controller_sha256"]:
        raise RecoveryError("immutable_attempt_controller_drift")
    if sha256_file(FAILED_CONTRACT_PATH) != attempt["contract_sha256"]:
        raise RecoveryError("immutable_attempt_contract_drift")
    evidence = json.loads(FAILED_EVIDENCE_PATH.read_text(encoding="utf-8"))
    expected = {
        "attempt_id": "native-composition-attempt-001",
        "result": "fail",
        "failure_classification": "NATIVE_COMPOSITION_EXECUTION_FAILED",
        "events": ["sentinel_activated", "stock_headless_hmr_ready"],
        "terminal": None,
        "duration_ms": 0,
    }
    observed = {
        "attempt_id": evidence.get("attempt_id"),
        "result": evidence.get("result"),
        "failure_classification": evidence.get("failure_classification"),
        "events": evidence.get("lifecycle", {}).get("events"),
        "terminal": evidence.get("terminal"),
        "duration_ms": evidence.get("launch", {}).get("duration_ms"),
    }
    if observed != expected:
        raise RecoveryError("immutable_attempt_projection_mismatch")
    source = FAILED_CONTROLLER_PATH.read_text(encoding="utf-8")
    generic = 'failure = "NATIVE_COMPOSITION_EXECUTION_FAILED"'
    duration = "launch_duration_ms = round((time.monotonic() - started) * 1000)"
    if source.count(generic) != 1 or source.count(duration) != 1:
        raise RecoveryError("failed_controller_source_shape_mismatch")
    if source.index(duration) < source.index("while True:"):
        raise RecoveryError("failed_controller_duration_order_unexpected")
    return {
        "causal_classification": "indeterminate_preterminal_failure",
        "retained_events": expected["events"],
        "guard_terminal_retained": False,
        "effective_tool_view_observed": False,
        "generic_failure_collapse_present": True,
        "duration_assigned_after_throwable_polling_path": True,
        "retained_duration_reliable": False,
        "permitted_root_cause_claims": [],
    }


def corrected_runner_source() -> bytes:
    coordinates = load_contract()["activation_coordinates"]
    coordinate_literal = json.dumps(coordinates)
    source = f'''import {{ appendFileSync, closeSync, existsSync, openSync, readFileSync, writeFileSync }} from "node:fs";
import {{ resolve }} from "node:path";

const COORDINATES = new Set({coordinate_literal});
export const name = "provider-free-preterminal-observable-runner";
export const inject = ["hmr"];

function activation(config, coordinate) {{
  if (!COORDINATES.has(coordinate)) throw new Error("closed activation coordinate required");
  const lines = existsSync(config.activationPath) ? readFileSync(config.activationPath, "utf8").split(/\\r?\\n/).filter(Boolean) : [];
  const record = {{ schema_version: "{ACTIVATION_SCHEMA}", sequence: lines.length + 1, coordinate }};
  appendFileSync(config.activationPath, JSON.stringify(record) + "\\n", "utf8");
}}

function terminal(config, code, detail = null, names = []) {{
  const descriptor = openSync(config.terminalPath, "wx");
  try {{
    writeFileSync(descriptor, JSON.stringify({{
      schema_version: "{TERMINAL_SCHEMA}", stage: "preterminal_activation", code, detail,
      effective_tool_names: names, effective_tool_count: names.length,
    }}) + "\\n", "utf8");
  }} finally {{ closeSync(descriptor); }}
}}

function stop(config, coordinate, exit) {{
  try {{ terminal(config, coordinate); activation(config, coordinate); }}
  catch {{ activation(config, "TERMINAL_WRITE_FAILED"); }}
  if (typeof exit === "function") {{ activation(config, "EXIT_REQUESTED"); exit(2); }}
}}

export async function apply(ctx, config) {{
  activation(config, "BOOTSTRAP_APPLY_ENTERED");
  const hmr = ctx.get("hmr");
  const exit = ctx.get("appExit");
  if (hmr === undefined || !(hmr.configs instanceof Map)) {{ stop(config, "HMR_UNAVAILABLE", exit); return; }}
  if (typeof exit !== "function") {{ stop(config, "APP_EXIT_UNAVAILABLE", exit); return; }}
  const observed = new Set([...hmr.configs.keys()].map((value) => resolve(value).toLowerCase()));
  const expected = config.watchedPaths.map((value) => resolve(value).toLowerCase());
  if (!expected.every((value) => observed.has(value))) {{ stop(config, "HMR_UNAVAILABLE", exit); return; }}
  if (ctx.get("agentPresets") === undefined || ctx.get("tools") === undefined) {{ stop(config, "SERVICES_UNAVAILABLE", exit); return; }}
  let createScope, assertEffectiveToolComposition, sanitizeEffectiveToolTerminal;
  try {{
    ({{ createScope }} = await import("@deepseek-ai/dsh-scope"));
    ({{ assertEffectiveToolComposition, sanitizeEffectiveToolTerminal }} = await import("./effective-tool-guard.mjs"));
    activation(config, "RUNTIME_MODULES_IMPORTED");
  }} catch {{ stop(config, "RUNTIME_MODULE_IMPORT_FAILED", exit); return; }}
  let scope;
  try {{ scope = createScope(ctx, Object.freeze({{}})); activation(config, "SCOPE_CREATED"); }}
  catch {{ stop(config, "SCOPE_CREATION_FAILED", exit); return; }}
  let result, exitCode = 2;
  try {{
    activation(config, "GUARD_ENTRY_REACHED");
    result = await assertEffectiveToolComposition(scope.ctx, "emr4-bounded-worker", ["edit", "glob", "read"]);
    terminal(config, result.coordinate, null, result.effectiveToolNames);
    activation(config, "GUARD_TERMINAL_REACHED");
    exitCode = 0;
  }} catch (error) {{
    const safe = sanitizeEffectiveToolTerminal(error);
    const names = safe.detail === null ? [] : safe.detail.split(",").filter((value) => /^[a-z_]+$/.test(value));
    try {{ terminal(config, safe.code, safe.detail, names); activation(config, "GUARD_TERMINAL_REACHED"); }}
    catch {{ activation(config, "TERMINAL_WRITE_FAILED"); }}
  }}
  try {{ await scope.dispose(); activation(config, "SCOPE_DISPOSED"); }}
  catch {{ activation(config, "SCOPE_DISPOSAL_FAILED"); exitCode = 2; }}
  activation(config, "EXIT_REQUESTED");
  exit(exitCode);
}}
'''
    return source.encode()


def validate_corrected_runner(payload: bytes) -> dict[str, Any]:
    source = payload.decode()
    if source.split("export const name", maxsplit=1)[0].count("@deepseek-ai/") != 0:
        raise RecoveryError("top_level_runtime_import_present")
    checks = {
        "bootstrap_before_dynamic_import": source.index("BOOTSTRAP_APPLY_ENTERED")
        < source.index('await import("@deepseek-ai/dsh-scope")'),
        "scope_import_is_dynamic": source.count('await import("@deepseek-ai/dsh-scope")') == 1,
        "guard_import_is_dynamic": source.count('await import("./effective-tool-guard.mjs")') == 1,
        "single_activation_writer": source.count("appendFileSync(config.activationPath") == 1,
        "single_terminal_exclusive_writer": source.count('openSync(config.terminalPath, "wx")') == 1,
        "single_scope_creation": source.count("createScope(ctx,") == 1,
        "single_guard_call": source.count("assertEffectiveToolComposition(scope.ctx,") == 1,
        "single_scope_disposal": source.count("await scope.dispose()") == 1,
    }
    if not all(checks.values()):
        raise RecoveryError("corrected_runner_shape_invalid")
    for coordinate in load_contract()["activation_coordinates"]:
        if coordinate not in source:
            raise RecoveryError("corrected_runner_coordinate_missing")
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), "checks": checks}


def scenario_matrix() -> list[dict[str, Any]]:
    scenarios = [
        ("missing_hmr", ["BOOTSTRAP_APPLY_ENTERED", "HMR_UNAVAILABLE", "EXIT_REQUESTED"]),
        ("missing_app_exit", ["BOOTSTRAP_APPLY_ENTERED", "APP_EXIT_UNAVAILABLE"]),
        ("missing_services", ["BOOTSTRAP_APPLY_ENTERED", "SERVICES_UNAVAILABLE", "EXIT_REQUESTED"]),
        ("module_import_rejected", ["BOOTSTRAP_APPLY_ENTERED", "RUNTIME_MODULE_IMPORT_FAILED", "EXIT_REQUESTED"]),
        ("scope_creation_rejected", ["BOOTSTRAP_APPLY_ENTERED", "RUNTIME_MODULES_IMPORTED", "SCOPE_CREATION_FAILED", "EXIT_REQUESTED"]),
        ("guard_failure", ["BOOTSTRAP_APPLY_ENTERED", "RUNTIME_MODULES_IMPORTED", "SCOPE_CREATED", "GUARD_ENTRY_REACHED", "GUARD_TERMINAL_REACHED", "SCOPE_DISPOSED", "EXIT_REQUESTED"]),
        ("terminal_write_rejected", ["BOOTSTRAP_APPLY_ENTERED", "RUNTIME_MODULES_IMPORTED", "SCOPE_CREATED", "GUARD_ENTRY_REACHED", "TERMINAL_WRITE_FAILED", "SCOPE_DISPOSED", "EXIT_REQUESTED"]),
        ("scope_disposal_rejected", ["BOOTSTRAP_APPLY_ENTERED", "RUNTIME_MODULES_IMPORTED", "SCOPE_CREATED", "GUARD_ENTRY_REACHED", "GUARD_TERMINAL_REACHED", "SCOPE_DISPOSAL_FAILED", "EXIT_REQUESTED"]),
        ("success", ["BOOTSTRAP_APPLY_ENTERED", "RUNTIME_MODULES_IMPORTED", "SCOPE_CREATED", "GUARD_ENTRY_REACHED", "GUARD_TERMINAL_REACHED", "SCOPE_DISPOSED", "EXIT_REQUESTED"]),
        ("unknown_exception", ["BOOTSTRAP_APPLY_ENTERED", "RUNTIME_MODULE_IMPORT_FAILED", "EXIT_REQUESTED"]),
    ]
    admitted = set(load_contract()["activation_coordinates"])
    rows = []
    for scenario, coordinates in scenarios:
        if any(coordinate not in admitted for coordinate in coordinates):
            raise RecoveryError("scenario_coordinate_not_admitted")
        rows.append({"scenario": scenario, "coordinates": coordinates, "safe": True})
    return rows


def future_controller_envelope_source() -> bytes:
    """Return the frozen future lifecycle skeleton; it is never executed here."""
    return b'''started_at = None
process = None
launch_duration_ms = None
try:
    started_at = monotonic()
    process = launch_exact_native_process()
    observe_bounded_terminal(process)
finally:
    if started_at is not None:
        launch_duration_ms = round((monotonic() - started_at) * 1000)
    terminate_and_wait_exact_process(process)
    remove_exact_disposable_root()
'''


def validate_future_controller_envelope(payload: bytes) -> dict[str, Any]:
    source = payload.decode()
    checks = {
        "single_process_launch": source.count("launch_exact_native_process()") == 1,
        "duration_initialized_unknown": "launch_duration_ms = None" in source,
        "duration_assignment_in_finally": source.index("finally:")
        < source.index("launch_duration_ms = round("),
        "termination_after_duration": source.index("launch_duration_ms = round(")
        < source.index("terminate_and_wait_exact_process(process)"),
        "cleanup_after_termination": source.index("terminate_and_wait_exact_process(process)")
        < source.index("remove_exact_disposable_root()"),
    }
    if not all(checks.values()):
        raise RecoveryError("future_controller_envelope_invalid")
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), "checks": checks}


def deterministic_projection() -> dict[str, Any]:
    contract = load_contract()
    return {
        "contract": contract,
        "diagnosis": diagnose_failed_attempt(contract),
        "runner": validate_corrected_runner(corrected_runner_source()),
        "controller_envelope": validate_future_controller_envelope(
            future_controller_envelope_source()
        ),
        "scenario_matrix": scenario_matrix(),
    }


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def execute_offline_probe(cache_root: Path | None = None) -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise RecoveryError("canonical_output_already_exists")
    projection = deterministic_projection()
    contract = projection["contract"]
    guard_contract = load_guard_contract()
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    dsh = guard_contract["packages"][0]
    blob = _cache_blob_path(resolved_cache, dsh["registry_integrity"])
    if sha256_file(blob) != contract["package"]["tarball_sha256"]:
        raise RecoveryError("package_cache_digest_mismatch")
    parent = DISPOSABLE_PARENT.resolve()
    root = Path(tempfile.mkdtemp(prefix="dsh-preterminal-recovery-", dir=parent)).resolve()
    if root.parent != parent:
        raise RecoveryError("disposable_root_escape")
    network_records: list[dict[str, Any]] = []
    install_projection: dict[str, Any] = {}
    installed_source: dict[str, Any] = {}
    probe_duration_ms = 0
    probe_exit_code: int | None = None
    stdout_digest = sha256_bytes(b"")
    stderr_digest = sha256_bytes(b"")
    error: BaseException | None = None
    try:
        home = root / "home"
        guard_path = root / "network-guard.mjs"
        network_path = root / "network.jsonl"
        tarball = root / "dsh-0.1.0-rc.7.tgz"
        _write(guard_path, network_guard_source())
        _write(tarball, blob.read_bytes())
        identity = verify_tarball(tarball, contract)
        if identity["sha256"] != contract["package"]["tarball_sha256"]:
            raise RecoveryError("materialized_package_digest_mismatch")
        environment, removed = build_child_environment(home, guard_path, network_path)
        package_root, install_projection = _offline_install(root, tarball, environment)
        installed_source = _verify_installed_source(package_root, contract)
        proof = root / "installation" / "proof"
        _write(proof / "effective-tool-guard.mjs", build_guard_source())
        _write(proof / "corrected-runner.mjs", corrected_runner_source())
        probe = b'''const scope = await import("@deepseek-ai/dsh-scope");
const guard = await import("./effective-tool-guard.mjs");
const runner = await import("./corrected-runner.mjs");
if (typeof scope.createScope !== "function" || typeof guard.assertEffectiveToolComposition !== "function" || typeof runner.apply !== "function") process.exit(2);
'''
        _write(proof / "probe.mjs", probe)
        node = shutil.which("node")
        if node is None:
            raise RecoveryError("node_not_found")
        started = time.monotonic()
        completed = subprocess.run(
            [node, str(proof / "probe.mjs")],
            cwd=proof,
            env=environment,
            capture_output=True,
            check=False,
            timeout=30,
        )
        probe_duration_ms = round((time.monotonic() - started) * 1000)
        probe_exit_code = completed.returncode
        stdout_digest = sha256_bytes(completed.stdout)
        stderr_digest = sha256_bytes(completed.stderr)
        network_records = _network_attempts(network_path)
        if probe_exit_code != 0 or network_records:
            raise RecoveryError("non_harness_module_import_probe_failed")
    except (RecoveryError, OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError) as caught:
        error = caught
    finally:
        if root.parent != parent:
            raise RecoveryError("cleanup_root_escape")
        shutil.rmtree(root)
    root_absent = not root.exists()
    if error is not None or not root_absent:
        raise RecoveryError("offline_probe_failed") from error
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "result": "pass",
        "immutable_attempt": {**contract["immutable_attempt"], "unchanged": True},
        "diagnosis": projection["diagnosis"],
        "corrected_design": projection["runner"],
        "scenario_matrix": projection["scenario_matrix"],
        "offline_probe": {
            "offline_materialisation_count": 1,
            "offline_materialisation": install_projection,
            "installed_source": installed_source,
            "non_harness_node_import_count": 1,
            "native_harness_process_count": 0,
            "node_probe_exit_code": probe_exit_code,
            "node_probe_duration_ms": probe_duration_ms,
            "stdout_sha256": stdout_digest,
            "stderr_sha256": stderr_digest,
            "raw_logs_retained": False,
        },
        "provider_boundary": {
            "network_attempt_count": len(network_records),
            "agent_session_count": 0,
            "turn_count": 0,
            "broker_request_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "occupied_worker_count": 0,
            "docker_invocation_count": 0,
            "database_invocation_count": 0,
            "credential_environment_names_removed_count": removed,
        },
        "cleanup": {
            "disposable_root_absent": root_absent,
            "raw_environment_retained": False,
            "raw_logs_retained": False,
            "npm_cache_retained_by_recovery": False,
        },
    }
    OPERATION_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(canonical_json_bytes(evidence))
    REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
    return evidence


def render_report(evidence: dict[str, Any]) -> str:
    probe = evidence["offline_probe"]
    return f"""# Provider-free preterminal observability recovery report

- Result: `{evidence['result']}`
- Failed-attempt diagnosis: `{evidence['diagnosis']['causal_classification']}`
- Scenario count: `{len(evidence['scenario_matrix'])}`
- Real-package non-Harness Node import probes: `{probe['non_harness_node_import_count']}`
- Native Harness processes: `{probe['native_harness_process_count']}`
- Network attempts: `{evidence['provider_boundary']['network_attempt_count']}`
- Disposable root absent: `{str(evidence['cleanup']['disposable_root_absent']).lower()}`

The recovery improves future preterminal traceability only. It does not change,
retry or reclassify native-composition-attempt-001 and is not a native Harness,
agent, model or provider result.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--publish", action="store_true")
    action.add_argument("--publish-timing", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        if args.check:
            projection = deterministic_projection()
            print(json.dumps({"result": "pass", "scenario_count": len(projection["scenario_matrix"]), "runner_sha256": projection["runner"]["sha256"], "controller_envelope_sha256": projection["controller_envelope"]["sha256"]}))
        elif args.publish:
            evidence = execute_offline_probe(args.cache_root)
            print(json.dumps({"result": evidence["result"], "native_harness_process_count": 0}))
        else:
            if TIMING_EVIDENCE_PATH.exists():
                raise RecoveryError("timing_evidence_already_exists")
            projection = deterministic_projection()["controller_envelope"]
            payload = {
                "schema_version": "ariadne.deepseek_native_harness_future_controller_timing_design.v1",
                "operation_id": OPERATION_ID,
                "result": "pass",
                "native_harness_process_count": 0,
                "controller_envelope": projection,
            }
            TIMING_EVIDENCE_PATH.write_bytes(canonical_json_bytes(payload))
            print(json.dumps({"result": "pass", "native_harness_process_count": 0, "controller_envelope_sha256": projection["sha256"]}))
    except RecoveryError as error:
        print(json.dumps({"result": "fail", "error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

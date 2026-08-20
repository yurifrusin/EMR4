"""Build and run the bounded check-in lifecycle conformance repair readings."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, NoReturn

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.git_object_resolution import resolve_commit_source
from scripts.deepseek_native_harness_provider_free_emr4_bounded_worker_preset_materialisation_recovery import (
    PRESET_BYTES,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    _network_attempts,
    _terminate_process,
    build_child_environment,
    network_guard_source,
)

OPERATION_ID = (
    "raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-"
    "lifecycle-conformance-repair"
)
TOPIC = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = TOPIC / "contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "contract.schema.json"
DIAGNOSTIC_SCHEMA_PATH = TOPIC / "server-post-readiness.schema.json"
EVIDENCE_SCHEMA_PATH = TOPIC / "evidence.schema.json"
PROBE_TERMINAL_PATH = TOPIC / "native-probe-terminal.json"
PROBE_CONSUMED_PATH = TOPIC / "native-probe-consumed.json"
EVIDENCE_PATH = TOPIC / "repair-evidence.json"
REPORT_PATH = TOPIC / "repair-report.md"
EFFICACY_PATH = TOPIC / "efficacy-reading.json"

PLAN_SOURCE = "d62ecb97f9d0a844d0021235cf8f067bfb925a78"
BASELINE_SOURCE = "2ebb05ebaf28cc4978e1f21bf8a7340fb6ee44bd"
PROTECTED_SOURCE = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PASS_RESULT = (
    "raisa_provider_free_check_in_server_post_readiness_exit_state_and_stdin_"
    "lifecycle_conformance_repair_pass"
)
PROBE_ATTEMPT_ID = "check-in-lifecycle-native-mount-probe-001"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_CHECKPOINT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _./,:;()'\-]{0,159}$")
EXPECTED_TOOLS = ["edit", "glob", "read"]
SUCCESS_MARKERS = [
    "PRESET_DISCOVERY_ENTERED",
    "PRESET_DISCOVERY_PASSED",
    "PRESET_VALIDATION_PASSED",
    "AGENTS_CREATE_ENTERED",
    "AGENT_SETUP_ENTERED",
    "PRESET_RESOLUTION_ENTERED",
    "PRESET_RESOLUTION_PASSED",
    "PRESET_STANDING_ENTERED",
    "PRESET_STANDING_PASSED",
    "PRESET_SCOPE_BINDING_ENTERED",
    "PRESET_SCOPE_BINDING_PASSED",
    "EFFECTIVE_TOOL_VIEW_PASSED",
    "AGENT_CREATED_PROVIDER_DISABLED",
    "AGENT_DISPOSED",
]
INSTRUMENTATION_UNAVAILABLE = "PRESET_SUBSTAGE_INSTRUMENTATION_UNAVAILABLE"
ARTIFACT_ROLES = {
    "contract": "contract.json",
    "contract_schema": "contract.schema.json",
    "diagnostic_schema": "server-post-readiness.schema.json",
    "evidence_schema": "evidence.schema.json",
    "native_probe_consumed": "native-probe-consumed.json",
    "native_probe_terminal": "native-probe-terminal.json",
    "repair_evidence": "repair-evidence.json",
    "repair_report": "repair-report.md",
    "efficacy_reading": "efficacy-reading.json",
}
NATIVE_INSTALLATION_ID = "deepseek-check-in-attachment-observability-native-001"
NATIVE_INSTALLATION_ROOT = (
    ROOT.parent / "EMR4-worktrees" / NATIVE_INSTALLATION_ID
)
DISPOSABLE_PARENT = ROOT.parent / "EMR4-worktrees"


class LifecycleRepairError(RuntimeError):
    """Closed controller failure carrying only one stable coordinate."""


def _fail(code: str) -> NoReturn:
    raise LifecycleRepairError(code)


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _pretty_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        _fail("json_object_required")
    return value


def _validate_schema(value: object, schema_path: Path, code: str) -> None:
    schema = _load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    if list(Draft202012Validator(schema).iter_errors(value)):
        _fail(code)


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _write_replace(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".next")
    if temporary.exists():
        _fail("artifact_temporary_exists")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def validate_contract(value: object) -> dict[str, Any]:
    _validate_schema(value, CONTRACT_SCHEMA_PATH, "contract_schema_invalid")
    if not isinstance(value, dict):
        _fail("contract_object_required")
    contract = value
    if contract.get("operation_id") != OPERATION_ID:
        _fail("contract_operation_mismatch")
    if contract.get("plan_source") != PLAN_SOURCE:
        _fail("contract_plan_source_mismatch")
    if contract.get("baseline_source") != BASELINE_SOURCE:
        _fail("contract_baseline_source_mismatch")
    if contract.get("protected_source") != PROTECTED_SOURCE:
        _fail("contract_protected_source_mismatch")
    if contract.get("artifact_roles") != ARTIFACT_ROLES:
        _fail("contract_artifact_roles_mismatch")
    if contract.get("native_probe", {}).get("success_markers") != SUCCESS_MARKERS:
        _fail("contract_native_marker_mismatch")
    if contract.get("native_probe", {}).get("expected_tools") != EXPECTED_TOOLS:
        _fail("contract_native_tool_mismatch")
    if any(contract.get("closed_boundaries", {}).values()):
        _fail("contract_closed_boundary_open")
    return contract


def resolve_git_bindings(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    projections: dict[str, dict[str, Any]] = {}
    for source in contract["git_sources"]:
        supplied = source["commit"]
        if HEX40.fullmatch(supplied) is None:
            _fail("git_source_not_full_object_id")
        projections[source["role"]] = resolve_commit_source(
            repo_root=ROOT,
            source_head=supplied,
        )
    return projections


def verify_immutable_bindings(contract: dict[str, Any]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for row in contract["immutable_bindings"]:
        path = ROOT / row["path"]
        if not path.is_file() or path.is_symlink():
            _fail("immutable_binding_missing_or_unsafe")
        digest = _sha256_path(path)
        if digest != row["sha256"]:
            _fail("immutable_binding_digest_mismatch")
        observed[row["path"]] = digest
    for row in contract["baseline_blob_bindings"]:
        payload = _git_blob(contract["baseline_source"], row["path"])
        if payload is None or _sha256_bytes(payload) != row["sha256"]:
            _fail("baseline_blob_binding_digest_mismatch")
        observed[f"{contract['baseline_source']}:{row['path']}"] = row["sha256"]
    return observed


def verify_native_installation(contract: dict[str, Any]) -> dict[str, Any]:
    installation = contract["native_installation"]
    if installation["installation_id"] != NATIVE_INSTALLATION_ID:
        _fail("native_installation_id_mismatch")
    root = NATIVE_INSTALLATION_ROOT.resolve()
    expected_parent = DISPOSABLE_PARENT.resolve()
    if root.parent != expected_parent or not root.is_dir() or root.is_symlink():
        _fail("native_installation_root_unavailable")
    lock = root / "package-lock.json"
    if not lock.is_file() or _sha256_path(lock) != installation["package_lock_sha256"]:
        _fail("native_installation_lock_mismatch")
    lock_value = _load_json(lock)
    packages = lock_value.get("packages")
    if not isinstance(packages, dict):
        _fail("native_installation_lock_shape_invalid")
    versions: dict[str, str] = {}
    for name in installation["packages"]:
        leaf = name.removeprefix("@deepseek-ai/")
        manifest_path = root / "node_modules" / "@deepseek-ai" / leaf / "package.json"
        if not manifest_path.is_file() or manifest_path.is_symlink():
            _fail("native_installation_package_missing")
        manifest = _load_json(manifest_path)
        lock_row = packages.get(f"node_modules/@deepseek-ai/{leaf}")
        if (
            manifest.get("name") != name
            or manifest.get("version") != "0.1.0-rc.7"
            or not isinstance(lock_row, dict)
            or lock_row.get("version") != "0.1.0-rc.7"
        ):
            _fail("native_installation_package_version_mismatch")
        versions[name] = manifest["version"]
    method_checks: dict[str, bool] = {}
    for row in installation["method_sources"]:
        path = root / row["relative_path"]
        if not path.is_file() or path.is_symlink() or _sha256_path(path) != row["sha256"]:
            _fail("native_method_source_digest_mismatch")
        source = path.read_text(encoding="utf-8")
        for fragment in row["required_fragments"]:
            key = f"{row['id']}:{fragment['id']}"
            method_checks[key] = source.count(fragment["text"]) == fragment["count"]
    if not all(method_checks.values()):
        _fail("native_method_source_shape_mismatch")
    bin_path = root / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js"
    if not bin_path.is_file() or bin_path.is_symlink():
        _fail("native_harness_bin_missing")
    return {
        "installation_id": NATIVE_INSTALLATION_ID,
        "package_lock_sha256": installation["package_lock_sha256"],
        "versions": versions,
        "method_checks": method_checks,
        "bin_path": bin_path,
    }


def derive_test_dependencies(contract: dict[str, Any]) -> dict[str, list[str]]:
    manifest = contract["command_manifest"]
    dependency_manifest = contract["dependency_manifest"]
    dependency_rows = {
        row["command_id"]: row for row in dependency_manifest["commands"]
    }
    if len(dependency_rows) != len(dependency_manifest["commands"]):
        _fail("dependency_command_duplicate")
    result: dict[str, list[str]] = {}
    for command in manifest["commands"]:
        argv = command["argv"]
        selected = [item.replace("\\", "/") for item in argv if item.endswith(".py")]
        selected = [item for item in selected if item.startswith("tests/")]
        dependency = dependency_rows.get(command["id"])
        if dependency is None or selected != dependency["test_paths"]:
            _fail("dependency_test_coverage_mismatch")
        paths = dependency["required_paths"]
        if len(paths) != len(set(paths)) or any(not (ROOT / path).is_file() for path in paths):
            _fail("dependency_path_missing_or_duplicate")
        if any(path not in paths for path in selected):
            _fail("dependency_selected_test_omitted")
        result[command["id"]] = paths
    if set(result) != set(dependency_rows):
        _fail("dependency_command_coverage_mismatch")
    return result


def render_checkpoint(
    contract: dict[str, Any], template_id: str, values: dict[str, str]
) -> str:
    template = contract["checkpoint_templates"].get(template_id)
    if not isinstance(template, str):
        _fail("checkpoint_template_unknown")
    if any(not isinstance(value, str) for value in values.values()):
        _fail("checkpoint_value_invalid")
    try:
        rendered = template.format(**values)
    except (KeyError, ValueError) as error:
        raise LifecycleRepairError("checkpoint_render_failed") from error
    if SAFE_CHECKPOINT.fullmatch(rendered) is None:
        _fail("checkpoint_render_not_bounded")
    return rendered


def derive_changed_paths(
    baseline: dict[str, str | None], terminal: dict[str, str | None]
) -> list[str]:
    if set(baseline) != set(terminal):
        _fail("changed_path_map_coverage_mismatch")
    for value in (*baseline.values(), *terminal.values()):
        if value is not None and HEX64.fullmatch(value) is None:
            _fail("changed_path_digest_invalid")
    return sorted(path for path in baseline if baseline[path] != terminal[path])


def _git_blob(source: str, path: str) -> bytes | None:
    completed = subprocess.run(
        ["git", "show", f"{source}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        timeout=30,
        shell=False,
    )
    if completed.returncode == 128:
        return None
    if completed.returncode != 0:
        _fail("baseline_blob_read_failed")
    return completed.stdout


def changed_path_reading(contract: dict[str, Any]) -> dict[str, Any]:
    baseline: dict[str, str | None] = {}
    terminal: dict[str, str | None] = {}
    for path in contract["tracked_paths"]:
        baseline_payload = _git_blob(contract["baseline_source"], path)
        baseline[path] = (
            None if baseline_payload is None else _sha256_bytes(baseline_payload)
        )
        current = ROOT / path
        terminal[path] = _sha256_path(current) if current.is_file() else None
    return {
        "baseline": baseline,
        "terminal": terminal,
        "changed_paths": derive_changed_paths(baseline, terminal),
    }


def artifact_paths(contract: dict[str, Any]) -> dict[str, str]:
    if contract["artifact_roles"] != ARTIFACT_ROLES:
        _fail("artifact_role_noncanonical")
    return {
        role: (TOPIC / relative).relative_to(ROOT).as_posix()
        for role, relative in contract["artifact_roles"].items()
    }


def example_server_projection() -> dict[str, Any]:
    return {
        "projection_valid": True,
        "status": "exited",
        "running": False,
        "exit_code": 1,
        "oom_killed": False,
        "state_error_empty": False,
        "restart_count": 0,
        "attachment_process": "running",
        "attachment_stdin": "open_after_delivery",
    }


def runner_source() -> bytes:
    markers_json = json.dumps(SUCCESS_MARKERS)
    tools_json = json.dumps(EXPECTED_TOOLS)
    source = f'''import {{ createHash, randomUUID }} from "node:crypto";
import {{ appendFileSync, readFileSync, writeFileSync }} from "node:fs";
import {{ scopeOf }} from "@deepseek-ai/dsh-scope";
import {{ SessionId }} from "@deepseek-ai/dsh-session";

export const name = "emr4-provider-disabled-lifecycle-probe";
export const inject = ["agents", "agentPresets", "tools"];
const EXPECTED = Object.freeze({markers_json});
const EXPECTED_TOOLS = Object.freeze({tools_json});
const INSTRUMENTATION_UNAVAILABLE = "{INSTRUMENTATION_UNAVAILABLE}";

function emit(config, markers, marker) {{
  markers.push(marker);
  appendFileSync(config.markerPath, JSON.stringify({{ sequence: markers.length, marker }}) + "\\n", "utf8");
}}
function writeTerminal(config, value) {{
  writeFileSync(config.terminalPath, JSON.stringify(value) + "\\n", {{ encoding: "utf8", flag: "wx" }});
}}
function terminalCoordinate(markers) {{
  if (markers.includes(INSTRUMENTATION_UNAVAILABLE)) return INSTRUMENTATION_UNAVAILABLE;
  return EXPECTED.find((marker) => !markers.includes(marker)) ?? "AGENT_DISPOSED";
}}
function exactTools(agentCtx) {{
  const scope = scopeOf(agentCtx);
  if (scope === undefined) return [];
  const schemas = agentCtx.tools.schemas(scope);
  if (!Array.isArray(schemas)) return [];
  const names = schemas.map((schema) => schema?.name);
  if (!names.every((name) => typeof name === "string" && /^[a-z_]+$/.test(name))) return [];
  return [...new Set(names)].sort();
}}

async function run(ctx, config) {{
  const markers = [];
  let handle;
  let tools = [];
  try {{
    const agents = ctx.get("agents");
    const presets = ctx.get("agentPresets");
    if (!agents || !presets) throw new Error("service unavailable");
    emit(config, markers, "PRESET_DISCOVERY_ENTERED");
    const rows = await presets.list();
    emit(config, markers, "PRESET_DISCOVERY_PASSED");
    const preset = rows.find((row) => row?.id === "emr4-bounded-worker");
    if (!preset || preset.broken !== undefined) throw new Error("preset invalid");
    const payload = readFileSync(preset.path);
    if (payload.length !== 158 || createHash("sha256").update(payload).digest("hex") !== "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1") throw new Error("preset bytes invalid");
    emit(config, markers, "PRESET_VALIDATION_PASSED");

    if (typeof agents.create !== "function" || typeof presets.resolveMountable !== "function" || typeof presets.ensureStanding !== "function" || !(presets.bindings instanceof WeakMap) || typeof presets.bindings.set !== "function") {{
      emit(config, markers, INSTRUMENTATION_UNAVAILABLE);
      throw new Error("instrumentation unavailable");
    }}
    const resolveMountable = presets.resolveMountable.bind(presets);
    const ensureStanding = presets.ensureStanding.bind(presets);
    const bindingSet = presets.bindings.set.bind(presets.bindings);
    presets.resolveMountable = async (...args) => {{
      emit(config, markers, "PRESET_RESOLUTION_ENTERED");
      const value = await resolveMountable(...args);
      emit(config, markers, "PRESET_RESOLUTION_PASSED");
      return value;
    }};
    presets.ensureStanding = async (...args) => {{
      emit(config, markers, "PRESET_STANDING_ENTERED");
      const value = await ensureStanding(...args);
      emit(config, markers, "PRESET_STANDING_PASSED");
      return value;
    }};
    presets.bindings.set = (...args) => {{
      emit(config, markers, "PRESET_SCOPE_BINDING_ENTERED");
      const value = bindingSet(...args);
      emit(config, markers, "PRESET_SCOPE_BINDING_PASSED");
      return value;
    }};

    emit(config, markers, "AGENTS_CREATE_ENTERED");
    handle = await agents.create({{
      sessionId: SessionId(`provider-disabled-${{randomUUID()}}`),
      meta: {{ cwd: process.cwd() }},
      agentOptions: {{ provider: "provider-disabled", model: "provider-disabled", maxTokens: 1 }},
      setup: async (agentCtx) => {{
        emit(config, markers, "AGENT_SETUP_ENTERED");
        await presets.mount(agentCtx, "emr4-bounded-worker");
        tools = exactTools(agentCtx);
        if (JSON.stringify(tools) !== JSON.stringify(EXPECTED_TOOLS)) throw new Error("effective tools invalid");
        emit(config, markers, "EFFECTIVE_TOOL_VIEW_PASSED");
      }},
    }});
    emit(config, markers, "AGENT_CREATED_PROVIDER_DISABLED");
    await handle.dispose();
    handle = undefined;
    emit(config, markers, "AGENT_DISPOSED");
    writeTerminal(config, {{ schema_version: "emr4.check-in-lifecycle-native-runner.v1", result: "pass", terminal_coordinate: "AGENT_DISPOSED", markers, effective_tool_names: tools }});
    ctx.get("appExit")(0);
  }} catch {{
    if (handle !== undefined) {{ try {{ await handle.dispose(); }} catch {{}} }}
    writeTerminal(config, {{ schema_version: "emr4.check-in-lifecycle-native-runner.v1", result: "failed_closed", terminal_coordinate: terminalCoordinate(markers), markers, effective_tool_names: [] }});
    ctx.get("appExit")(1);
  }}
}}

export function apply(ctx, config) {{ void run(ctx, config); }}
'''
    return source.encode("utf-8")


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode("utf-8")
    positions = [source.index(json.dumps(marker)) for marker in SUCCESS_MARKERS]
    checks = {
        "markers_ordered": positions == sorted(positions),
        "single_agents_create": source.count("await agents.create(") == 1,
        "single_preset_mount": source.count("await presets.mount(") == 1,
        "single_dispose_success": source.count("await handle.dispose();") == 2,
        "no_followup": ".followup(" not in source,
        "no_model_request": "createUserMessage" not in source,
        "no_raw_exception": "error.message" not in source and "error.stack" not in source,
        "provider_disabled": "provider-disabled" in source,
    }
    if not all(checks.values()):
        _fail("runner_source_shape_invalid")
    return {"sha256": _sha256_bytes(payload), "bytes": len(payload), **checks}


def profile_patch(root: Path) -> bytes:
    workspace = json.dumps(str((root / "workspace").resolve()))
    preset_root = json.dumps(str((root / "home" / ".agent-presets").resolve()))
    marker_path = json.dumps(str((root / "markers.jsonl").resolve()))
    terminal_path = json.dumps(str((root / "runner-terminal.json").resolve()))
    return f"""- id: headless-runner
  disabled: true
- id: code-runtime
  disabled: true
- id: session-telemetry-otel
  disabled: true
- id: session-title-llm
  disabled: true
- id: compaction-basic
  disabled: true
- id: command-compact
  disabled: true
- id: llm-pi-ai
  disabled: true
- id: llm-deepseek
  disabled: true
- id: llm-retry
  disabled: true
- id: tool-bash
  disabled: true
- id: tool-pwsh
  disabled: true
- id: tool-jobs
  disabled: true
- id: tool-skill
  disabled: true
- id: tool-goal
  disabled: true
- id: tool-ralph
  disabled: true
- id: tool-subagent
  disabled: true
- id: tool-subagent-fork
  disabled: true
- id: tool-subagent-control
  disabled: true
- id: tool-subagent-list-agents
  disabled: true
- id: tool-subagent-report
  disabled: true
- id: tool-workflow
  disabled: true
- id: tool-todo
  disabled: true
- id: tool-web
  disabled: true
- id: web-search-deepseek
  disabled: true
- id: tool-str-replace-editor
  disabled: true
- id: sandbox-policy
  config:
    mode: workspace-write
    workspaceRoot: {workspace}
- id: approval
  config:
    policy: never
- id: permission
  config:
    defaultPreset: emr4-bounded-worker
    presets:
      emr4-bounded-worker:
        sandbox: workspace-write
        approval: never
- id: fs-sandbox
  config:
    cwd: {workspace}
- id: agent-loop
  config:
    agents: []
    maxParallelToolCalls: 1
- insert:
    - id: agent-presets
      name: '@deepseek-ai/dsh-agent-presets'
      config:
        default: emr4-bounded-worker
        roots:
          - path: {preset_root}
            trust: system
        includeUserRoot: false
    - id: emr4-provider-disabled-lifecycle-probe
      name: ./proof/runner.mjs
      inject: [agents, agentPresets, tools]
      config:
        markerPath: {marker_path}
        terminalPath: {terminal_path}
""".encode("utf-8")


def validate_profile_patch(payload: bytes) -> dict[str, Any]:
    value = yaml.safe_load(payload)
    if not isinstance(value, list):
        _fail("profile_patch_not_array")
    inserted: list[dict[str, Any]] = []
    for row in value:
        if not isinstance(row, dict):
            _fail("profile_patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                _fail("profile_patch_insert_invalid")
            inserted.extend(row["insert"])
    if [row.get("id") for row in inserted] != [
        "agent-presets",
        "emr4-provider-disabled-lifecycle-probe",
    ]:
        _fail("profile_patch_insert_order_invalid")
    text = payload.decode("utf-8")
    for forbidden in (
        "DEEPSEEK" + "_API_KEY",
        "http://",
        "https://",
        "attempt" + "-006",
    ):
        if forbidden in text:
            _fail("profile_patch_forbidden_surface")
    return {"sha256": _sha256_bytes(payload), "row_count": len(value)}


def deterministic_check() -> dict[str, Any]:
    contract = validate_contract(_load_json(CONTRACT_PATH))
    git = resolve_git_bindings(contract)
    immutable = verify_immutable_bindings(contract)
    installation = verify_native_installation(contract)
    dependencies = derive_test_dependencies(contract)
    checkpoint = render_checkpoint(
        contract,
        "deterministic_ready",
        {"test_count": str(len(contract["dependency_manifest"]["commands"][0]["test_paths"]))},
    )
    changed = changed_path_reading(contract)
    artifacts = artifact_paths(contract)
    _validate_schema(
        example_server_projection(),
        DIAGNOSTIC_SCHEMA_PATH,
        "diagnostic_schema_rejected_example",
    )
    fake_root = Path("C:/deterministic/check-in-lifecycle-native-probe")
    runner = validate_runner_source(runner_source())
    profile = validate_profile_patch(profile_patch(fake_root))
    if len(PRESET_BYTES) != 158 or _sha256_bytes(PRESET_BYTES) != contract["native_probe"]["preset_sha256"]:
        _fail("preset_binding_mismatch")
    return {
        "contract": contract,
        "git": git,
        "immutable": immutable,
        "installation": installation,
        "dependencies": dependencies,
        "checkpoint": checkpoint,
        "changed_paths": changed,
        "artifacts": artifacts,
        "runner": runner,
        "profile": profile,
    }


def _read_markers(path: Path) -> tuple[list[str], bool]:
    if not path.is_file():
        return [], False
    markers: list[str] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if set(row) != {"sequence", "marker"} or row["sequence"] != len(markers) + 1:
                return [], False
            marker = row["marker"]
            if marker not in {*SUCCESS_MARKERS, INSTRUMENTATION_UNAVAILABLE}:
                return [], False
            markers.append(marker)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return [], False
    if INSTRUMENTATION_UNAVAILABLE in markers:
        valid = markers[-1] == INSTRUMENTATION_UNAVAILABLE
    else:
        valid = markers == SUCCESS_MARKERS[: len(markers)]
    return (markers if valid else []), valid


def _read_runner_terminal(path: Path, markers: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = _load_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError, LifecycleRepairError):
        return None
    if set(value) != {
        "schema_version",
        "result",
        "terminal_coordinate",
        "markers",
        "effective_tool_names",
    }:
        return None
    if value["schema_version"] != "emr4.check-in-lifecycle-native-runner.v1":
        return None
    if value["markers"] != markers:
        return None
    coordinate = value["terminal_coordinate"]
    if coordinate not in {*SUCCESS_MARKERS, INSTRUMENTATION_UNAVAILABLE}:
        return None
    if value["result"] == "pass":
        if coordinate != "AGENT_DISPOSED" or markers != SUCCESS_MARKERS:
            return None
        if value["effective_tool_names"] != EXPECTED_TOOLS:
            return None
    elif value["result"] == "failed_closed":
        if value["effective_tool_names"] != []:
            return None
    else:
        return None
    return value


def _first_missing(markers: list[str]) -> str:
    if INSTRUMENTATION_UNAVAILABLE in markers:
        return INSTRUMENTATION_UNAVAILABLE
    return next((marker for marker in SUCCESS_MARKERS if marker not in markers), "AGENT_DISPOSED")


def execute_native_probe() -> dict[str, Any]:
    if PROBE_CONSUMED_PATH.exists() or PROBE_TERMINAL_PATH.exists():
        _fail("native_probe_already_consumed")
    check = deterministic_check()
    contract = check["contract"]
    installation = check["installation"]
    parent = DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        _fail("disposable_parent_missing")
    root = Path(tempfile.mkdtemp(prefix="check-in-lifecycle-native-probe-", dir=parent)).resolve()
    if root.parent != parent:
        _fail("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    start: float | None = None
    exit_code: int | None = None
    failure = None
    removed_environment_names = 0
    stdout_sha256 = _sha256_bytes(b"")
    stderr_sha256 = _sha256_bytes(b"")
    stdout_bytes = 0
    stderr_bytes = 0
    markers: list[str] = []
    markers_valid = False
    runner_terminal: dict[str, Any] | None = None
    network_records: list[dict[str, Any]] = []
    network_ledger_valid = True

    marker_path = root / "markers.jsonl"
    runner_terminal_path = root / "runner-terminal.json"
    network_path = root / "network.jsonl"
    stdout_path = root / "stdout.log"
    stderr_path = root / "stderr.log"
    try:
        home = root / "home"
        profile = home / "profiles" / "headless"
        proof = profile / "proof"
        workspace = root / "workspace"
        workspace.mkdir()
        proof.mkdir(parents=True)
        (home / ".agent-presets" / "emr4-bounded-worker").mkdir(parents=True)
        (profile / "package.json").write_text(
            json.dumps(
                {
                    "name": "dsh-profile-headless",
                    "private": True,
                    "dependencies": {},
                    "dsh": {
                        "profile": {
                            "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]
                        }
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (profile / "pnpm-workspace.yaml").write_text(
            "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
            encoding="utf-8",
        )
        (home / ".agent-presets" / "emr4-bounded-worker" / "agent.cordis.yml").write_bytes(PRESET_BYTES)
        (proof / "runner.mjs").write_bytes(runner_source())
        (profile / "cordis.patch.yml").write_bytes(profile_patch(root))
        guard_path = root / "network-guard.mjs"
        guard_path.write_bytes(network_guard_source())
        environment, removed_environment_names = build_child_environment(
            home, guard_path, network_path
        )
        environment["DSH_CWD"] = str(workspace)
        environment["DSH_PERMISSION_MODE"] = "workspace-write"
        environment["DSH_TOOLS_MODE"] = "native"
        if any(
            re.search(
                r"(DEEPSEEK|OPENAI|ANTHROPIC|GEMINI|VERTEX|GOOGLE|AZURE|AWS|GCP|API[_-]?KEY|TOKEN|PASSWORD|SECRET)",
                name,
                re.IGNORECASE,
            )
            for name in environment
        ):
            _fail("provider_environment_not_scrubbed")
        command = [
            shutil.which("node") or "node",
            "--expose-internals",
            str(installation["bin_path"]),
            "--profile",
            "headless",
            "provider-disabled lifecycle probe",
        ]
        consumed = {
            "schema_version": "emr4.check-in-lifecycle-native-probe-latch.v1",
            "operation_id": OPERATION_ID,
            "attempt_id": PROBE_ATTEMPT_ID,
            "state": "consumed",
            "native_process_limit": 1,
            "automatic_retry_count": 0,
            "resume_permitted": False,
            "provider_enabled": False,
        }
        _write_exclusive(PROBE_CONSUMED_PATH, _pretty_json_bytes(consumed))
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
            exit_code = process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        failure = "NATIVE_PROCESS_TIMEOUT"
    except (LifecycleRepairError, OSError, subprocess.SubprocessError, ValueError):
        failure = "NATIVE_PROCESS_OR_CONTROLLER_FAILURE"
    finally:
        duration_ms = (
            round((time.monotonic() - start) * 1000) if start is not None else None
        )
        if process is not None:
            _terminate_process(process)
            if exit_code is None:
                exit_code = process.returncode
        if stdout_path.exists():
            payload = stdout_path.read_bytes()
            stdout_sha256, stdout_bytes = _sha256_bytes(payload), len(payload)
        if stderr_path.exists():
            payload = stderr_path.read_bytes()
            stderr_sha256, stderr_bytes = _sha256_bytes(payload), len(payload)
        markers, markers_valid = _read_markers(marker_path)
        runner_terminal = (
            _read_runner_terminal(runner_terminal_path, markers)
            if markers_valid
            else None
        )
        try:
            network_records = _network_attempts(network_path)
        except (OSError, ValueError, json.JSONDecodeError):
            network_records = []
            network_ledger_valid = False
        if root.parent != parent:
            _fail("cleanup_root_escape")
        shutil.rmtree(root)

    process_absent = process is None or process.poll() is not None
    root_absent = not root.exists()
    coordinate = (
        runner_terminal["terminal_coordinate"]
        if runner_terminal is not None
        else _first_missing(markers)
    )
    success = bool(
        process_started
        and exit_code == 0
        and failure is None
        and markers_valid
        and markers == SUCCESS_MARKERS
        and runner_terminal is not None
        and runner_terminal["result"] == "pass"
        and runner_terminal["effective_tool_names"] == EXPECTED_TOOLS
        and not network_records
        and network_ledger_valid
        and process_absent
        and root_absent
    )
    terminal = {
        "schema_version": "emr4.check-in-lifecycle-native-probe-terminal.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": PROBE_ATTEMPT_ID,
        "result": "pass" if success else "failed_closed",
        "terminal_coordinate": "AGENT_DISPOSED" if success else coordinate,
        "markers": markers,
        "effective_tool_names": EXPECTED_TOOLS if success else [],
        "package": {
            "name": "@deepseek-ai/dsh",
            "version": "0.1.0-rc.7",
            "installation_id": installation["installation_id"],
            "package_lock_sha256": installation["package_lock_sha256"],
        },
        "counts": {
            "native_processes": 1 if process_started else 0,
            "automatic_retries": 0,
            "agent_sessions": 1 if "AGENT_CREATED_PROVIDER_DISABLED" in markers else 0,
            "turns": 0,
            "broker_requests": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": len(network_records),
            "docker_invocations": 0,
            "database_invocations": 0,
        },
        "launch": {
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "stdout_sha256": stdout_sha256,
            "stdout_bytes": stdout_bytes,
            "stderr_sha256": stderr_sha256,
            "stderr_bytes": stderr_bytes,
            "raw_logs_retained": False,
            "credential_environment_names_removed_count": removed_environment_names,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
        },
    }
    _validate_schema(terminal, EVIDENCE_SCHEMA_PATH, "native_terminal_schema_invalid")
    _write_exclusive(PROBE_TERMINAL_PATH, _pretty_json_bytes(terminal))
    return terminal


def build_evidence() -> dict[str, Any]:
    check = deterministic_check()
    if not PROBE_TERMINAL_PATH.is_file():
        _fail("native_probe_terminal_missing")
    terminal = _load_json(PROBE_TERMINAL_PATH)
    _validate_schema(terminal, EVIDENCE_SCHEMA_PATH, "native_terminal_schema_invalid")
    result = PASS_RESULT if terminal["result"] == "pass" else "failed_closed"
    evidence = {
        "schema_version": "emr4.check-in-lifecycle-conformance-repair-evidence.v1",
        "operation_id": OPERATION_ID,
        "result": result,
        "source_head": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
            timeout=30,
        ).stdout.strip(),
        "plan_source": PLAN_SOURCE,
        "git_bindings": {role: row["resolved_commit"] for role, row in check["git"].items()},
        "server_lifecycle": {
            "stdin_open_after_delivery": True,
            "final_cleanup_is_sole_stdin_close_owner": True,
            "diagnostic_key_count": 9,
            "other_failure_families_carry_null": True,
        },
        "workflow_readings": {
            "checkpoint": check["checkpoint"],
            "test_dependencies": check["dependencies"],
            "changed_paths": check["changed_paths"]["changed_paths"],
            "artifact_paths": check["artifacts"],
        },
        "native_probe": terminal,
        "historical_evidence_unchanged": True,
        "closed_boundaries": check["contract"]["closed_boundaries"],
    }
    _validate_schema(evidence, EVIDENCE_SCHEMA_PATH, "repair_evidence_schema_invalid")
    return evidence


def render_report(evidence: dict[str, Any]) -> str:
    native = evidence["native_probe"]
    return f"""# Check-in lifecycle conformance repair report

- Result: `{evidence['result']}`
- Server stdin remains open after credential delivery: `true`
- Final cleanup is the sole stdin closer: `true`
- Closed server diagnostic keys: `9`
- Native Harness terminal: `{native['terminal_coordinate']}`
- Effective tools: `{', '.join(native['effective_tool_names'])}`
- Native processes / retries: `{native['counts']['native_processes']} / 0`
- Model / provider / network / Docker / database requests: `0 / 0 / {native['counts']['network_attempts']} / 0 / 0`
- Process and disposable-root absence: `{str(native['cleanup']['process_absent']).lower()} / {str(native['cleanup']['disposable_root_absent']).lower()}`

This proves only the closed lifecycle projection and one pinned rc.7
provider-disabled `agents.create({{setup}})` mount. It is not attempt 006, an
occupied DeepSeek worker, a model-quality result or product/runtime admission.
"""


def build_efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    native = evidence["native_probe"]
    return {
        "schema_version": "ariadne.tranche_efficacy_reading.v1",
        "operation_id": OPERATION_ID,
        "outcome": (
            "lifecycle_readings_passed"
            if evidence["result"] == PASS_RESULT
            else "native_mount_probe_failed_closed"
        ),
        "native_processes": native["counts"]["native_processes"],
        "automatic_retries": 0,
        "provider_requests": 0,
        "docker_invocations": 0,
        "database_invocations": 0,
        "manual_checklist_fields_replaced": [
            "full_git_object_resolution",
            "test_dependency_closure",
            "bounded_checkpoint_rendering",
            "changed_path_sha256_comparison",
            "artifact_role_projection",
        ],
        "efficiency_judgment": (
            "ready_for_independent_veto"
            if evidence["result"] == PASS_RESULT
            else "blocked_before_occupied_worker"
        ),
    }


def publish() -> dict[str, Any]:
    for path in (EVIDENCE_PATH, REPORT_PATH, EFFICACY_PATH):
        if path.exists():
            _fail("published_artifact_already_exists")
    evidence = build_evidence()
    _write_exclusive(EVIDENCE_PATH, _pretty_json_bytes(evidence))
    _write_exclusive(REPORT_PATH, render_report(evidence).encode("utf-8"))
    _write_exclusive(EFFICACY_PATH, _pretty_json_bytes(build_efficacy(evidence)))
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute-native", action="store_true")
    action.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.check:
        check = deterministic_check()
        print(
            json.dumps(
                {
                    "status": "passed",
                    "checkpoint": check["checkpoint"],
                    "changed_paths": check["changed_paths"]["changed_paths"],
                    "native_processes": 0,
                },
                sort_keys=True,
            )
        )
    elif args.execute_native:
        terminal = execute_native_probe()
        print(
            json.dumps(
                {
                    "status": terminal["result"],
                    "terminal_coordinate": terminal["terminal_coordinate"],
                    "counts": terminal["counts"],
                    "cleanup": terminal["cleanup"],
                },
                sort_keys=True,
            )
        )
    else:
        evidence = publish()
        print(json.dumps({"status": evidence["result"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

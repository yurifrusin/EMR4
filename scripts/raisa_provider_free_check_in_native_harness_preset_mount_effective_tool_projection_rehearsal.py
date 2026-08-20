"""Provider-free rc.7 preset-mount and exact effective-tool projection proof."""

from __future__ import annotations

import argparse
import hashlib
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

from scripts import (
    deepseek_native_harness_provider_free_effective_tool_composition_guard as guard,
)
from scripts import (
    deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof
    as native_predecessor,
)
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_row_service_path_recovery
    as service_predecessor,
)
from scripts import (
    deepseek_native_harness_provider_free_required_service_injection_recovery
    as service_injection_recovery,
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
    network_guard_source,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-check-in-native-harness-preset-mount-"
    "effective-tool-projection-rehearsal"
)
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
DETERMINISTIC_SCHEMA_PATH = CONTINUITY_ROOT / "deterministic-evidence.schema.json"
NATIVE_SCHEMA_PATH = CONTINUITY_ROOT / "native-terminal.schema.json"
DETERMINISTIC_EVIDENCE_PATH = CONTINUITY_ROOT / "deterministic-evidence.json"
DETERMINISTIC_REPORT_PATH = CONTINUITY_ROOT / "deterministic-report.md"
NATIVE_CHECKPOINT_PATH = CONTINUITY_ROOT / "native-preexecution-checkpoint.json"
NATIVE_CONSUMED_PATH = CONTINUITY_ROOT / "native-consumed.json"
NATIVE_TERMINAL_PATH = CONTINUITY_ROOT / "native-terminal.json"
NATIVE_REPORT_PATH = CONTINUITY_ROOT / "native-report.md"

CONTRACT_SCHEMA = "ariadne.check_in_preset_mount_effective_tool_contract.v1"
DETERMINISTIC_SCHEMA = (
    "ariadne.check_in_preset_mount_effective_tool_deterministic_evidence.v1"
)
EVENT_SCHEMA = "ariadne.check_in_preset_mount_effective_tool_event.v1"
RUNNER_TERMINAL_SCHEMA = "emr4.check-in-preset-mount-effective-tool-runner.v1"
NATIVE_TERMINAL_SCHEMA = (
    "ariadne.check_in_preset_mount_effective_tool_native_terminal.v1"
)
NATIVE_ATTEMPT_ID = "check-in-preset-mount-effective-tool-native-001"
EXPECTED_TOOLS = ["edit", "glob", "read"]
SUCCESS_CODE = "EFFECTIVE_TOOL_COMPOSITION_PASSED"
ROOT_FAILURE_CODE = "EFFECTIVE_ROOT_ROSTER_MISMATCH"
DISPOSAL_FAILURE_CODE = "EFFECTIVE_TOOL_SCOPE_DISPOSAL_FAILED"
EXPECTED_EVENTS = [
    "sentinel_activated",
    "stock_headless_hmr_ready",
    "effective_roots_entered",
    "effective_roots_passed",
    "effective_tool_guard_started",
    "effective_tool_projection_passed",
    "scope_disposed",
    "effective_tool_guard_terminal",
    "app_exit_requested",
]
SAFE_CODE = re.compile(r"^[A-Z0-9_]+$")
SAFE_TOOL = re.compile(r"^[a-z_]+$")


class PresetMountProjectionError(RuntimeError):
    """A closed preset-mount/projection boundary rejected."""


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
        raise PresetMountProjectionError("json_not_object")
    return value


def _write_json(path: Path, value: dict[str, Any], *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "xb" if exclusive else "wb"
    with path.open(mode) as stream:
        stream.write(_canonical_json(value))


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = _load_json(path)
    if value.get("schema_version") != CONTRACT_SCHEMA:
        raise PresetMountProjectionError("contract_schema_mismatch")
    if value.get("operation_id") != OPERATION_ID:
        raise PresetMountProjectionError("contract_operation_mismatch")
    if value.get("authored_at") != "2026-08-20T19:06:25.3877564+10:00":
        raise PresetMountProjectionError("contract_timestamp_mismatch")
    if value.get("guard") != {
        "generated_sha256": "6678ed31bdcd30a5018689b72ad509c182854bf5d63862f59b397acc8de40894",
        "success_code": SUCCESS_CODE,
        "expected_tools": EXPECTED_TOOLS,
    }:
        raise PresetMountProjectionError("contract_guard_mismatch")
    if value.get("preset") != {
        "id": "emr4-bounded-worker",
        "relative_path": ".agent-presets/emr4-bounded-worker/agent.cordis.yml",
        "bytes": 158,
        "sha256": "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1",
        "trust": "user",
    }:
        raise PresetMountProjectionError("contract_preset_mismatch")
    if value.get("profile") != {
        "include_user_root": True,
        "effective_roots": [
            {"role": "shipped", "trust": "system"},
            {"role": "derived_user", "trust": "user"},
        ],
        "runner_inject": ["hmr", "agentPresets", "tools"],
    }:
        raise PresetMountProjectionError("contract_profile_mismatch")
    native = value.get("native", {})
    if native != {
        "attempt_id": NATIVE_ATTEMPT_ID,
        "process_limit": 1,
        "automatic_retry_limit": 0,
        "timeout_seconds": 75,
        "expected_events": EXPECTED_EVENTS,
    }:
        raise PresetMountProjectionError("contract_native_mismatch")
    if value.get("zero_counts") != [
        "agent_sessions",
        "turns",
        "broker_requests",
        "model_requests",
        "provider_requests",
        "network_attempts",
        "occupied_workers",
        "docker_invocations",
        "database_invocations",
    ]:
        raise PresetMountProjectionError("contract_zero_count_mismatch")
    predecessor_files = value.get("predecessor_files")
    if not isinstance(predecessor_files, list) or len(predecessor_files) != 6:
        raise PresetMountProjectionError("contract_predecessor_count_mismatch")
    return value


def bind_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    bound: list[dict[str, Any]] = []
    roles: set[str] = set()
    for row in contract["predecessor_files"]:
        if set(row) != {"role", "path", "sha256"}:
            raise PresetMountProjectionError("predecessor_binding_keys_mismatch")
        role = row["role"]
        path = REPO_ROOT / row["path"]
        if not isinstance(role, str) or role in roles or not path.is_file():
            raise PresetMountProjectionError("predecessor_binding_invalid")
        roles.add(role)
        actual = _file_sha256(path)
        if actual != row["sha256"]:
            raise PresetMountProjectionError("predecessor_digest_mismatch:" + role)
        bound.append({"role": role, "bytes": path.stat().st_size, "sha256": actual})

    cache_root = service_injection_recovery.default_cache_root().resolve()
    old_projection = native_predecessor.deterministic_check(cache_root)
    service_contract = service_predecessor.load_contract()
    service_projection = service_predecessor.build_static_evidence(service_contract)
    generated_guard = guard.build_guard_source()
    guard_projection = guard.validate_guard_source(generated_guard)
    if guard_projection["sha256"] != contract["guard"]["generated_sha256"]:
        raise PresetMountProjectionError("accepted_guard_digest_mismatch")
    preset = service_predecessor.predecessor.CANONICAL_PRESET_PATH
    if preset.stat().st_size != 158 or _file_sha256(preset) != contract["preset"]["sha256"]:
        raise PresetMountProjectionError("canonical_preset_mismatch")
    return {
        "files": bound,
        "old_native_package_count": old_projection["package_count"],
        "old_native_runner_sha256": old_projection["runner"]["sha256"],
        "service_root_transformation": service_projection["root_transformation"],
        "guard": guard_projection,
        "preset_bytes": preset.stat().st_size,
        "preset_sha256": _file_sha256(preset),
    }


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def _event_writer_source() -> str:
    return f'''function emit(event) {{
  const existing = existsSync(config.eventPath)
    ? readFileSync(config.eventPath, "utf8").split(/\\r?\\n/).filter(Boolean)
    : [];
  const record = {{ schema_version: "{EVENT_SCHEMA}", sequence: existing.length + 1, event }};
  appendFileSync(config.eventPath, JSON.stringify(record) + "\\n", "utf8");
}}
'''


def sentinel_source() -> bytes:
    return f'''import {{ appendFileSync, existsSync, readFileSync }} from "node:fs";
import {{ resolve }} from "node:path";

export const name = "provider-free-preset-mount-hmr-sentinel";
export function apply(ctx, config) {{
{_event_writer_source()}
  emit("sentinel_activated");
  let ready = false;
  const timer = setInterval(() => {{
    if (ready) return;
    const hmr = ctx.get("hmr");
    if (hmr === undefined || !(hmr.configs instanceof Map)) return;
    const observed = new Set([...hmr.configs.keys()].map((value) => resolve(value).toLowerCase()));
    const expected = config.watchedPaths.map((value) => resolve(value).toLowerCase());
    if (!expected.every((value) => observed.has(value))) return;
    ready = true;
    clearInterval(timer);
    emit("stock_headless_hmr_ready");
  }}, 20);
  ctx.effect(() => () => clearInterval(timer), "provider-free preset-mount HMR sentinel");
}}
'''.encode("utf-8")


def runner_source() -> bytes:
    return f'''import {{ appendFileSync, closeSync, existsSync, openSync, readFileSync, writeFileSync }} from "node:fs";
import {{ resolve }} from "node:path";
import {{ createScope }} from "@deepseek-ai/dsh-scope";
import {{ assertEffectiveToolComposition, sanitizeEffectiveToolTerminal }} from "./effective-tool-guard.mjs";

export const name = "provider-free-preset-mount-effective-tool-runner";
export const inject = ["hmr", "agentPresets", "tools"];

function writeTerminal(path, record) {{
  const descriptor = openSync(path, "wx");
  try {{ writeFileSync(descriptor, JSON.stringify(record) + "\\n", "utf8"); }}
  finally {{ closeSync(descriptor); }}
}}

export async function apply(ctx, config) {{
{_event_writer_source()}
  const exit = ctx.get("appExit");
  let scope;
  let exitCode = 2;
  let terminal = {{
    schema_version: "{RUNNER_TERMINAL_SCHEMA}",
    stage: "pre_provider_tool_composition",
    code: "{ROOT_FAILURE_CODE}",
    detail: null,
    effective_tool_names: [],
    effective_tool_count: 0,
  }};
  try {{
    const presets = ctx.get("agentPresets");
    emit("effective_roots_entered");
    if (!presets || !Array.isArray(presets.roots) || presets.roots.length !== 2) throw new Error("roots");
    if (resolve(presets.roots[0].path) !== resolve(config.shippedRoot) || presets.roots[0].trust !== "system") throw new Error("shipped");
    if (resolve(presets.roots[1].path) !== resolve(config.userRoot) || presets.roots[1].trust !== "user") throw new Error("user");
    emit("effective_roots_passed");
    scope = createScope(ctx, Object.freeze({{}}));
    emit("effective_tool_guard_started");
    const result = await assertEffectiveToolComposition(scope.ctx, "emr4-bounded-worker", ["edit", "glob", "read"]);
    terminal = {{
      schema_version: "{RUNNER_TERMINAL_SCHEMA}",
      stage: "pre_provider_tool_composition",
      code: result.coordinate,
      detail: null,
      effective_tool_names: result.effectiveToolNames,
      effective_tool_count: result.effectiveToolCount,
    }};
    exitCode = 0;
    emit("effective_tool_projection_passed");
  }} catch (error) {{
    if (terminal.code !== "{ROOT_FAILURE_CODE}") {{
      const safe = sanitizeEffectiveToolTerminal(error);
      const names = safe.detail === null ? [] : safe.detail.split(",").filter((value) => /^[a-z_]+$/.test(value));
      terminal = {{
        schema_version: "{RUNNER_TERMINAL_SCHEMA}",
        stage: safe.stage,
        code: safe.code,
        detail: safe.detail,
        effective_tool_names: names,
        effective_tool_count: names.length,
      }};
    }}
  }} finally {{
    if (scope !== undefined) {{
      try {{ await scope.dispose(); emit("scope_disposed"); }}
      catch {{ terminal = {{ ...terminal, code: "{DISPOSAL_FAILURE_CODE}", detail: null, effective_tool_names: [], effective_tool_count: 0 }}; exitCode = 2; }}
    }}
    try {{ writeTerminal(config.terminalPath, terminal); if (exitCode === 0) emit("effective_tool_guard_terminal"); }}
    finally {{ if (exitCode === 0) emit("app_exit_requested"); exit(exitCode); }}
  }}
}}
'''.encode("utf-8")


def _inserted_rows(payload: bytes) -> list[dict[str, Any]]:
    value = yaml.safe_load(payload)
    if not isinstance(value, list):
        raise PresetMountProjectionError("profile_patch_not_array")
    rows: list[dict[str, Any]] = []
    for patch in value:
        if not isinstance(patch, dict):
            raise PresetMountProjectionError("profile_patch_row_invalid")
        if "insert" in patch:
            if set(patch) != {"insert"} or not isinstance(patch["insert"], list):
                raise PresetMountProjectionError("profile_patch_insert_invalid")
            rows.extend(patch["insert"])
    return rows


def build_patch_pair(
    root: Path,
    event_path: Path,
    terminal_path: Path,
    sentinel_path: Path,
    runner_path: Path,
) -> tuple[bytes, bytes]:
    profile_dir = root / "home" / "profiles" / "headless"
    initial, changed = native_predecessor.build_patch_pair(
        profile_dir, event_path, terminal_path, sentinel_path, runner_path
    )
    shipped_root = (
        root
        / "installation"
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
        / "config"
        / "agent-presets"
    ).resolve()
    user_root = (root / "home" / ".agent-presets").resolve()
    preset_row = {
        "id": "agent-presets",
        "name": "@deepseek-ai/dsh-agent-presets",
        "config": {
            "default": "emr4-bounded-worker",
            "roots": [{"path": str(user_root), "trust": "system"}],
            "includeUserRoot": True,
        },
    }

    def amend(payload: bytes, *, runner_present: bool) -> bytes:
        value = yaml.safe_load(payload)
        insertion = next(row["insert"] for row in value if "insert" in row)
        insertion.insert(0, preset_row)
        if runner_present:
            runner = next(
                row
                for row in insertion
                if row.get("id") == "provider-free-effective-tool-proof-runner"
            )
            runner["config"]["shippedRoot"] = str(shipped_root)
            runner["config"]["userRoot"] = str(user_root)
        return yaml.safe_dump(value, sort_keys=False, allow_unicode=False).encode("utf-8")

    amended_initial = amend(initial, runner_present=False)
    amended_changed = amend(changed, runner_present=True)
    validate_patch_pair(amended_initial, amended_changed, root)
    return amended_initial, amended_changed


def validate_patch_pair(initial: bytes, changed: bytes, root: Path) -> dict[str, Any]:
    initial_rows = _inserted_rows(initial)
    changed_rows = _inserted_rows(changed)
    if [row.get("id") for row in initial_rows] != [
        "agent-presets",
        "provider-free-effective-tool-hmr-sentinel",
    ]:
        raise PresetMountProjectionError("initial_insert_order_mismatch")
    if [row.get("id") for row in changed_rows] != [
        "agent-presets",
        "provider-free-effective-tool-hmr-sentinel",
        "provider-free-effective-tool-proof-runner",
    ]:
        raise PresetMountProjectionError("changed_insert_order_mismatch")
    preset = changed_rows[0]
    config = preset.get("config")
    if not isinstance(config, dict) or config.get("includeUserRoot") is not True:
        raise PresetMountProjectionError("user_root_not_enabled")
    if config.get("default") != "emr4-bounded-worker":
        raise PresetMountProjectionError("default_preset_mismatch")
    runner = changed_rows[-1]
    if runner.get("inject") != ["hmr", "agentPresets", "tools"]:
        raise PresetMountProjectionError("runner_injection_mismatch")
    runner_config = runner.get("config")
    if not isinstance(runner_config, dict) or set(runner_config) != {
        "eventPath",
        "terminalPath",
        "watchedPaths",
        "shippedRoot",
        "userRoot",
    }:
        raise PresetMountProjectionError("runner_config_mismatch")
    expected_user = str((root / "home" / ".agent-presets").resolve())
    if runner_config["userRoot"] != expected_user:
        raise PresetMountProjectionError("runner_user_root_mismatch")
    return {
        "initial_sha256": _sha256(initial),
        "changed_sha256": _sha256(changed),
        "include_user_root": True,
        "runner_inject": runner["inject"],
        "inserted_ids": [row["id"] for row in changed_rows],
    }


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode("utf-8")
    checks = {
        "one_scope": source.count("createScope(ctx,") == 1,
        "one_guard_call": source.count("assertEffectiveToolComposition(scope.ctx,") == 1,
        "one_terminal": source.count('openSync(path, "wx")') == 1,
        "one_dispose": source.count("await scope.dispose()") == 1,
        "root_count_exact": "presets.roots.length !== 2" in source,
        "system_then_user": (
            'presets.roots[0].trust !== "system"' in source
            and 'presets.roots[1].trust !== "user"' in source
        ),
        "exact_tools": '["edit", "glob", "read"]' in source,
        "no_agents_create": "agents.create" not in source,
        "no_session_or_turn": "SessionId" not in source and ".followup(" not in source,
        "no_broker_or_provider": all(
            token not in source
            for token in (
                'ctx.get("broker")',
                'ctx.get("models")',
                'ctx.get("providers")',
                "createUserMessage",
            )
        ),
        "no_raw_exception": "error.message" not in source and "error.stack" not in source,
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise PresetMountProjectionError("runner_shape_mismatch:" + ",".join(failed))
    return {"bytes": len(payload), "sha256": _sha256(payload), **checks}


def parse_events(path: Path, *, allow_incomplete: bool = False) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if set(row) != {"schema_version", "sequence", "event"}:
                raise PresetMountProjectionError("event_keys_mismatch")
            if row["schema_version"] != EVENT_SCHEMA or row["sequence"] != len(records) + 1:
                raise PresetMountProjectionError("event_identity_mismatch")
            if row["event"] not in EXPECTED_EVENTS:
                raise PresetMountProjectionError("event_vocabulary_mismatch")
            records.append(row)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PresetMountProjectionError("event_parse_failed") from error
    names = [row["event"] for row in records]
    if len(names) != len(set(names)):
        raise PresetMountProjectionError("event_duplicate")
    if allow_incomplete:
        if names != EXPECTED_EVENTS[: len(names)]:
            raise PresetMountProjectionError("event_prefix_mismatch")
    elif names != EXPECTED_EVENTS:
        raise PresetMountProjectionError("event_sequence_mismatch")
    return records


def parse_runner_terminal(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    expected_keys = {
        "schema_version",
        "stage",
        "code",
        "detail",
        "effective_tool_names",
        "effective_tool_count",
    }
    if set(value) != expected_keys or value["schema_version"] != RUNNER_TERMINAL_SCHEMA:
        raise PresetMountProjectionError("runner_terminal_shape_mismatch")
    if value["stage"] != "pre_provider_tool_composition":
        raise PresetMountProjectionError("runner_terminal_stage_mismatch")
    if not isinstance(value["code"], str) or SAFE_CODE.fullmatch(value["code"]) is None:
        raise PresetMountProjectionError("runner_terminal_code_invalid")
    names = value["effective_tool_names"]
    if (
        not isinstance(names, list)
        or any(not isinstance(name, str) or SAFE_TOOL.fullmatch(name) is None for name in names)
        or names != sorted(set(names))
        or value["effective_tool_count"] != len(names)
    ):
        raise PresetMountProjectionError("runner_terminal_names_invalid")
    detail = value["detail"]
    if detail is not None and (not isinstance(detail, str) or detail != ",".join(names)):
        raise PresetMountProjectionError("runner_terminal_detail_invalid")
    return value


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    predecessors = bind_predecessors(contract)
    service_fixture = service_predecessor.run_fixture_characterization(
        service_predecessor.load_contract()
    )
    root_scenarios = service_fixture["scenarios"]
    corrected = next(
        row for row in root_scenarios if row["scenario"] == "corrected_shipped_plus_user"
    )
    if corrected["decision"] != "accepted_exact_user_row" or corrected["row"]["trust"] != "user":
        raise PresetMountProjectionError("corrected_root_fixture_not_accepted")
    guard_scenarios = guard.scenario_matrix()
    if len(guard_scenarios) != 13:
        raise PresetMountProjectionError("guard_fixture_count_mismatch")
    fake_root = Path("C:/emr4-preset-mount-candidate").resolve()
    proof = fake_root / "installation" / "proof"
    initial, changed = build_patch_pair(
        fake_root,
        fake_root / "events.jsonl",
        fake_root / "runner-terminal.json",
        proof / "sentinel.mjs",
        proof / "runner.mjs",
    )
    candidate = {
        "patch": validate_patch_pair(initial, changed, fake_root),
        "runner": validate_runner_source(runner_source()),
        "sentinel_sha256": _sha256(sentinel_source()),
        "guard_sha256": _sha256(guard.build_guard_source()),
        "native_process_checkpoint_admitted": False,
    }
    evidence = {
        "schema_version": DETERMINISTIC_SCHEMA,
        "operation_id": OPERATION_ID,
        "result": "pass",
        "predecessors": predecessors,
        "root_fixture": {
            "scenario_count": len(root_scenarios),
            "scenarios": root_scenarios,
            "package_only_node_processes": 1,
            "network_attempts": 0,
            "cleanup_passed": service_fixture["cleanup"]["disposable_root_absent"],
        },
        "guard_fixture": {
            "scenario_count": len(guard_scenarios),
            "scenarios": guard_scenarios,
            "success_code": SUCCESS_CODE,
            "expected_tools": EXPECTED_TOOLS,
        },
        "candidate": candidate,
        "process_boundary": {
            "package_only_node_processes": 1,
            "native_harness_processes": 0,
            "agent_sessions": 0,
            "turns": 0,
            "broker_requests": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": 0,
            "occupied_workers": 0,
            "docker_invocations": 0,
            "database_invocations": 0,
        },
    }
    jsonschema.Draft202012Validator(_load_json(DETERMINISTIC_SCHEMA_PATH)).validate(
        evidence
    )
    return evidence


def render_deterministic_report(evidence: dict[str, Any]) -> str:
    return f"""# Provider-free preset-mount/effective-tool deterministic report

- Result: `{evidence['result']}`
- Root fixtures: `{evidence['root_fixture']['scenario_count']}`
- Guard fixtures: `{evidence['guard_fixture']['scenario_count']}`
- Effective tools: `edit`, `glob`, `read`
- Package-only Node / native Harness processes: `1 / 0`
- Agent/session/turn/broker/model/provider/network/Docker/database counts: all `0`
- Native checkpoint admitted: `false`

This binds the accepted rc.7 guard to the corrected shipped-plus-derived-user
root candidate. It proves no native mount, agent session or model request.
"""


def build_deterministic_artifacts() -> dict[str, Any]:
    evidence = deterministic_evidence()
    _write_json(DETERMINISTIC_EVIDENCE_PATH, evidence)
    DETERMINISTIC_REPORT_PATH.write_text(
        render_deterministic_report(evidence), encoding="utf-8", newline="\n"
    )
    return evidence


def load_checkpoint(path: Path | None = None) -> dict[str, Any]:
    resolved = NATIVE_CHECKPOINT_PATH if path is None else path
    value = _load_json(resolved)
    expected_keys = {
        "schema_version",
        "operation_id",
        "status",
        "candidate_source",
        "review_receipt",
        "review_receipt_sha256",
        "attempt_id",
        "native_process_limit",
        "automatic_retry_limit",
        "timeout_seconds",
        "expected_events",
        "runner_sha256",
        "guard_sha256",
        "checkpoint_admitted",
    }
    if set(value) != expected_keys:
        raise PresetMountProjectionError("checkpoint_keys_mismatch")
    if value["schema_version"] != "ariadne.check_in_preset_mount_native_checkpoint.v1":
        raise PresetMountProjectionError("checkpoint_schema_mismatch")
    if value["operation_id"] != OPERATION_ID or value["status"] != "admitted":
        raise PresetMountProjectionError("checkpoint_status_mismatch")
    if value["attempt_id"] != NATIVE_ATTEMPT_ID:
        raise PresetMountProjectionError("checkpoint_attempt_mismatch")
    if value["native_process_limit"] != 1 or value["automatic_retry_limit"] != 0:
        raise PresetMountProjectionError("checkpoint_process_limit_mismatch")
    if value["timeout_seconds"] != 75 or value["expected_events"] != EXPECTED_EVENTS:
        raise PresetMountProjectionError("checkpoint_envelope_mismatch")
    if value["runner_sha256"] != _sha256(runner_source()):
        raise PresetMountProjectionError("checkpoint_runner_mismatch")
    if value["guard_sha256"] != _sha256(guard.build_guard_source()):
        raise PresetMountProjectionError("checkpoint_guard_mismatch")
    if value["checkpoint_admitted"] is not True:
        raise PresetMountProjectionError("checkpoint_not_admitted")
    source = value["candidate_source"]
    if not isinstance(source, str) or re.fullmatch(r"[0-9a-f]{40}", source) is None:
        raise PresetMountProjectionError("checkpoint_source_invalid")
    receipt_path = REPO_ROOT / value["review_receipt"]
    if not receipt_path.is_file() or _file_sha256(receipt_path) != value["review_receipt_sha256"]:
        raise PresetMountProjectionError("checkpoint_review_binding_mismatch")
    receipt = _load_json(receipt_path)
    if (
        receipt.get("decision") != "pass"
        or receipt.get("head_before") != source
        or receipt.get("head_after") != source
        or receipt.get("dirty_after") is not False
    ):
        raise PresetMountProjectionError("checkpoint_review_not_passed")
    return value


def _success_runner_terminal(value: dict[str, Any]) -> bool:
    return value == {
        "schema_version": RUNNER_TERMINAL_SCHEMA,
        "stage": "pre_provider_tool_composition",
        "code": SUCCESS_CODE,
        "detail": None,
        "effective_tool_names": EXPECTED_TOOLS,
        "effective_tool_count": 3,
    }


def render_native_report(value: dict[str, Any]) -> str:
    return f"""# Provider-free native preset-mount/effective-tool report

- Result: `{value['result']}`
- Attempt: `{value['attempt_id']}`
- Terminal: `{value['terminal_code']}`
- Events: `{len(value['events'])}/{len(EXPECTED_EVENTS)}`
- Effective tools: `{', '.join(value['effective_tool_names'])}`
- Native processes / automatic retries: `1 / 0`
- Agent/session/turn/broker/model/provider/network/Docker/database counts: all `0`
- Process and disposable-root absence: `{str(value['cleanup']['process_absent']).lower()} / {str(value['cleanup']['disposable_root_absent']).lower()}`

This proves only the provider-disabled disposable rc.7 preset mount and exact
effective-tool projection. It is not an occupied worker or DeepSeek result.
"""


def execute_native() -> dict[str, Any]:
    if NATIVE_CONSUMED_PATH.exists() or NATIVE_TERMINAL_PATH.exists():
        raise PresetMountProjectionError("native_attempt_output_already_exists")
    checkpoint = load_checkpoint()
    deterministic_evidence()
    old_contract = native_predecessor.load_contract()
    cache_root = service_injection_recovery.default_cache_root().resolve()
    blob, cached_packages = native_predecessor.verify_cached_packages(
        old_contract, cache_root
    )
    parent = DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise PresetMountProjectionError("disposable_parent_missing")

    root = Path(tempfile.mkdtemp(prefix="dsh-preset-mount-proof-", dir=parent)).resolve()
    if root.parent != parent:
        raise PresetMountProjectionError("disposable_root_escape")
    process: subprocess.Popen[bytes] | None = None
    process_started = False
    exit_code: int | None = None
    started: float | None = None
    failure = "NATIVE_PRELAUNCH_FAILED"
    events: list[dict[str, Any]] = []
    runner_terminal: dict[str, Any] | None = None
    network_count = 0
    removed_environment_names = 0
    stdout_bytes = 0
    stderr_bytes = 0
    stdout_sha256 = _sha256(b"")
    stderr_sha256 = _sha256(b"")
    mutated = False

    try:
        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        workspace = root / "workspace"
        proof = root / "installation" / "proof"
        event_path = root / "events.jsonl"
        runner_terminal_path = root / "runner-terminal.json"
        network_path = root / "network.jsonl"
        stdout_path = root / "stdout.log"
        stderr_path = root / "stderr.log"
        guard_path = root / "network-guard.mjs"
        tarball = root / "dsh-0.1.0-rc.7.tgz"
        workspace.mkdir()
        profile_dir.mkdir(parents=True)
        proof.mkdir(parents=True)
        guard_path.write_bytes(network_guard_source())
        tarball.write_bytes(blob.read_bytes())
        environment, removed_environment_names = build_child_environment(
            home, guard_path, network_path
        )
        package_root, _ = _offline_install(root, tarball, environment)
        _verify_installed_source(package_root, old_contract)
        native_predecessor.validate_installed_packages(package_root, old_contract)

        (profile_dir / "package.json").write_text(
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
        )
        (profile_dir / "pnpm-workspace.yaml").write_text(
            "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
            encoding="utf-8",
        )
        preset = native_predecessor.build_preset_source(old_contract)
        preset_path = home / ".agent-presets" / "emr4-bounded-worker" / "agent.cordis.yml"
        preset_path.parent.mkdir(parents=True)
        preset_path.write_bytes(preset)
        (proof / "sentinel.mjs").write_bytes(sentinel_source())
        (proof / "runner.mjs").write_bytes(runner_source())
        (proof / "effective-tool-guard.mjs").write_bytes(guard.build_guard_source())
        initial, changed = build_patch_pair(
            root,
            event_path,
            runner_terminal_path,
            proof / "sentinel.mjs",
            proof / "runner.mjs",
        )
        patch_path = profile_dir / "cordis.patch.yml"
        patch_path.write_bytes(initial)
        node = shutil.which("node")
        if node is None:
            raise PresetMountProjectionError("node_not_found")
        command = [
            node,
            old_contract["launch"]["node_flag"],
            str(package_root / old_contract["package"]["bin"]),
            *old_contract["launch"]["profile_args"],
            "provider-free preset mount effective-tool proof",
        ]
        consumed = {
            "schema_version": "ariadne.check_in_preset_mount_effective_tool_consumed.v1",
            "operation_id": OPERATION_ID,
            "attempt_id": NATIVE_ATTEMPT_ID,
            "state": "consumed",
            "candidate_source": checkpoint["candidate_source"],
            "native_process_limit": 1,
            "automatic_retry_count": 0,
            "resume_permitted": False,
            "provider_enabled": False,
        }
        _write_json(NATIVE_CONSUMED_PATH, consumed, exclusive=True)
        failure = "NATIVE_EXECUTION_FAILED"
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            started = time.monotonic()
            process = subprocess.Popen(
                command,
                cwd=workspace,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                shell=False,
            )
            process_started = True
            deadline = started + checkpoint["timeout_seconds"]
            while True:
                events = parse_events(event_path, allow_incomplete=True)
                names = [row["event"] for row in events]
                if "stock_headless_hmr_ready" in names and not mutated:
                    atomic_write(patch_path, changed)
                    mutated = True
                if process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    failure = "NATIVE_PROCESS_TIMEOUT"
                    _terminate_process(process)
                    break
                time.sleep(POLL_SECONDS)
            exit_code = process.wait(timeout=5)
        stdout_payload = stdout_path.read_bytes()
        stderr_payload = stderr_path.read_bytes()
        stdout_bytes, stderr_bytes = len(stdout_payload), len(stderr_payload)
        stdout_sha256, stderr_sha256 = _sha256(stdout_payload), _sha256(stderr_payload)
        events = parse_events(event_path, allow_incomplete=True)
        if runner_terminal_path.is_file():
            runner_terminal = parse_runner_terminal(runner_terminal_path)
        network_count = len(_network_attempts(network_path))
        if network_count:
            failure = "NETWORK_ATTEMPT_OBSERVED"
        elif runner_terminal is not None:
            failure = runner_terminal["code"]
    except (
        PresetMountProjectionError,
        ProofError,
        guard.GuardError,
        subprocess.SubprocessError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ):
        if process_started and failure == "NATIVE_PRELAUNCH_FAILED":
            failure = "NATIVE_EXECUTION_EXCEPTION"
    finally:
        if process is not None and process.poll() is None:
            _terminate_process(process)
        if root.parent != parent:
            raise PresetMountProjectionError("cleanup_root_escape")
        shutil.rmtree(root)

    if not process_started:
        raise PresetMountProjectionError("prelaunch_failed_before_process")
    process_absent = process is not None and process.poll() is not None
    root_absent = not root.exists()
    success = (
        exit_code == 0
        and mutated
        and [row["event"] for row in events] == EXPECTED_EVENTS
        and runner_terminal is not None
        and _success_runner_terminal(runner_terminal)
        and network_count == 0
        and process_absent
        and root_absent
    )
    terminal = {
        "schema_version": NATIVE_TERMINAL_SCHEMA,
        "operation_id": OPERATION_ID,
        "attempt_id": NATIVE_ATTEMPT_ID,
        "result": "pass" if success else "failed_closed",
        "terminal_code": SUCCESS_CODE if success else failure,
        "events": [row["event"] for row in events],
        "effective_tool_names": (
            runner_terminal["effective_tool_names"] if runner_terminal is not None else []
        ),
        "effective_tool_count": (
            runner_terminal["effective_tool_count"] if runner_terminal is not None else 0
        ),
        "native_process_count": 1,
        "automatic_retry_count": 0,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "agent_session_count": 0,
            "turn_count": 0,
            "broker_request_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_attempt_count": network_count,
            "occupied_worker_count": 0,
            "docker_invocation_count": 0,
            "database_invocation_count": 0,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
            "raw_logs_retained": False,
            "raw_environment_retained": False,
            "stdout_bytes": stdout_bytes,
            "stderr_bytes": stderr_bytes,
            "stdout_sha256": stdout_sha256,
            "stderr_sha256": stderr_sha256,
        },
    }
    jsonschema.Draft202012Validator(_load_json(NATIVE_SCHEMA_PATH)).validate(terminal)
    _write_json(NATIVE_TERMINAL_PATH, terminal, exclusive=True)
    NATIVE_REPORT_PATH.write_text(
        render_native_report(terminal), encoding="utf-8", newline="\n"
    )
    if not success:
        raise PresetMountProjectionError("native_failed_closed:" + failure)
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--build", action="store_true")
    action.add_argument("--native", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            value = deterministic_evidence()
        elif args.build:
            value = build_deterministic_artifacts()
        else:
            value = execute_native()
        print(
            json.dumps(
                {
                    "result": value["result"],
                    "operation_id": OPERATION_ID,
                    "native_processes": value.get("native_process_count", 0),
                }
            )
        )
        return 0
    except (
        PresetMountProjectionError,
        ProofError,
        guard.GuardError,
        jsonschema.ValidationError,
    ) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

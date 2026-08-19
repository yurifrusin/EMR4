"""One-run provider-free rc.7 native effective-tool composition proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

import yaml

from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    FAILURE_COORDINATES,
    GuardError,
    _cache_blob_path,
    _default_cache_root,
    build_guard_source,
    load_contract as load_guard_contract,
    validate_guard_source,
    verify_package_blob,
    verify_profile,
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


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
EVIDENCE_PATH = OPERATION_ROOT / "provider-free-effective-tool-native-boot-evidence.json"
REPORT_PATH = OPERATION_ROOT / "provider-free-effective-tool-native-boot-report.md"
EVENT_SCHEMA = "ariadne.deepseek_native_harness_effective_tool_native_boot_event.v1"
TERMINAL_SCHEMA = "ariadne.deepseek_native_harness_effective_tool_native_boot_terminal.v1"
EVIDENCE_SCHEMA = "ariadne.deepseek_native_harness_effective_tool_native_boot_evidence.v1"
EXPECTED_EVENTS = [
    "sentinel_activated",
    "stock_headless_hmr_ready",
    "effective_tool_guard_started",
    "effective_tool_guard_terminal",
    "scope_disposed",
    "app_exit_requested",
]
SAFE_TOOL_NAME = re.compile(r"^[a-z_]+$")
NATIVE_BOOT_TIMEOUT_SECONDS = 45.0

GUARD_SCRIPT = REPO_ROOT / "scripts" / "deepseek_native_harness_provider_free_effective_tool_composition_guard.py"
GUARD_CONTRACT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-effective-tool-composition-and-terminal-coordinate-guard"
    / "contract.json"
)
HMR_SCRIPT = REPO_ROOT / "scripts" / "deepseek_native_harness_provider_free_hmr_boot_proof.py"
HMR_CONTRACT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-boot-proof"
    / "contract.json"
)
PROFILE_FAMILY = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission"
    / "profile-family.yaml"
)


class NativeCompositionProofError(RuntimeError):
    """A closed controller rejection."""


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != (
        "ariadne.deepseek_native_harness_effective_tool_native_boot_contract.v1"
    ):
        raise NativeCompositionProofError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise NativeCompositionProofError("contract_operation_mismatch")
    if contract.get("expected_events") != EXPECTED_EVENTS:
        raise NativeCompositionProofError("contract_event_sequence_mismatch")
    launch = contract.get("launch", {})
    if launch.get("native_boot_process_count") != 1 or launch.get("automatic_retry") is not False:
        raise NativeCompositionProofError("contract_one_run_boundary_mismatch")
    if launch.get("attempt_id") != "native-composition-attempt-001":
        raise NativeCompositionProofError("contract_attempt_mismatch")
    if contract.get("preset", {}).get("selected_tools") != ["edit", "glob", "read"]:
        raise NativeCompositionProofError("contract_selected_tools_mismatch")
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
    sources = contract["accepted_sources"]
    for object_id in (contract["planning_source"], *sources.values()):
        if not _git_object_is_ancestor(object_id):
            raise NativeCompositionProofError("accepted_git_source_missing_or_not_ancestor")
    expected = contract["predecessor_bytes"]
    actual = {
        "effective_tool_guard_script_sha256": sha256_file(GUARD_SCRIPT),
        "effective_tool_guard_contract_sha256": sha256_file(GUARD_CONTRACT),
        "hmr_boot_script_sha256": sha256_file(HMR_SCRIPT),
        "hmr_boot_contract_sha256": sha256_file(HMR_CONTRACT),
        "profile_family_sha256": sha256_file(PROFILE_FAMILY),
    }
    for field, digest in actual.items():
        if expected.get(field) != digest:
            raise NativeCompositionProofError(f"predecessor_digest_mismatch:{field}")
    guard = build_guard_source()
    projection = validate_guard_source(guard)
    if projection["sha256"] != expected.get("generated_guard_sha256"):
        raise NativeCompositionProofError("generated_guard_digest_mismatch")
    return {"accepted_sources": sources, "predecessor_sha256": actual, "guard": projection}


def verify_cached_packages(
    contract: dict[str, Any], cache_root: Path
) -> tuple[Path, list[dict[str, Any]]]:
    guard_contract = load_guard_contract()
    packages: list[dict[str, Any]] = []
    for package in guard_contract["packages"]:
        projection, _ = verify_package_blob(package, cache_root)
        packages.append(projection)
    dsh = guard_contract["packages"][0]
    if dsh["name"] != contract["package"]["name"]:
        raise NativeCompositionProofError("dsh_package_contract_mismatch")
    blob = _cache_blob_path(cache_root, dsh["registry_integrity"])
    if sha256_file(blob) != contract["package"]["tarball_sha256"]:
        raise NativeCompositionProofError("dsh_package_sha256_mismatch")
    verify_profile(guard_contract)
    return blob, packages


def build_preset_source(contract: dict[str, Any]) -> bytes:
    payload = """- id: tool-fs
  name: '@deepseek-ai/dsh-tool-fs'
- id: tool-fs-search
  name: '@deepseek-ai/dsh-tool-fs-search'
  config:
    sampleOverCapGlobResults: false
""".encode()
    if yaml.safe_load(payload) != contract["preset"]["rows"]:
        raise NativeCompositionProofError("preset_shape_mismatch")
    return payload


def _yaml_string(value: Path) -> str:
    return json.dumps(str(value.resolve()))


def build_patch_pair(
    profile_dir: Path,
    event_path: Path,
    terminal_path: Path,
    sentinel_path: Path,
    runner_path: Path,
) -> tuple[bytes, bytes]:
    profile_patch = profile_dir / "cordis.patch.yml"
    home_patch = profile_dir.parents[1] / "cordis.patch.yml"
    expected_modules = profile_dir.parents[2] / "installation" / "proof"
    if sentinel_path != expected_modules / "sentinel.mjs" or runner_path != expected_modules / "runner.mjs":
        raise NativeCompositionProofError("proof_module_location_mismatch")
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
        eventPath: {_yaml_string(event_path)}
        watchedPaths:
          - {_yaml_string(profile_patch)}
          - {_yaml_string(home_patch)}
"""
    changed = common + f"""    - id: provider-free-effective-tool-proof-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr, agentPresets, tools]
      config:
        eventPath: {_yaml_string(event_path)}
        terminalPath: {_yaml_string(terminal_path)}
        watchedPaths:
          - {_yaml_string(profile_patch)}
          - {_yaml_string(home_patch)}
"""
    initial, changed_bytes = common.encode(), changed.encode()
    validate_patch_pair(initial, changed_bytes)
    return initial, changed_bytes


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = yaml.safe_load(payload)
    if not isinstance(rows, list):
        raise NativeCompositionProofError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise NativeCompositionProofError("patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise NativeCompositionProofError("patch_insert_invalid")
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
        raise NativeCompositionProofError("patch_disabled_rows_mismatch")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-effective-tool-hmr-sentinel"
    ]:
        raise NativeCompositionProofError("initial_patch_runner_present")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-effective-tool-hmr-sentinel",
        "provider-free-effective-tool-proof-runner",
    ]:
        raise NativeCompositionProofError("changed_patch_rows_mismatch")
    if changed_inserted[:-1] != initial_inserted:
        raise NativeCompositionProofError("changed_patch_mutates_initial")
    runner = changed_inserted[-1]
    if runner.get("inject") != ["hmr", "agentPresets", "tools"]:
        raise NativeCompositionProofError("runner_injection_mismatch")


def _event_writer_source() -> str:
    return f"""function emit(event) {{
  const existing = existsSync(config.eventPath)
    ? readFileSync(config.eventPath, \"utf8\").split(/\\r?\\n/).filter(Boolean)
    : [];
  const record = {{ schema_version: \"{EVENT_SCHEMA}\", sequence: existing.length + 1, event }};
  appendFileSync(config.eventPath, JSON.stringify(record) + \"\\n\", \"utf8\");
}}
"""


def sentinel_source() -> bytes:
    return f"""import {{ appendFileSync, existsSync, readFileSync }} from \"node:fs\";
import {{ resolve }} from \"node:path\";

export const name = \"provider-free-effective-tool-hmr-sentinel\";
export function apply(ctx, config) {{
{_event_writer_source()}
  emit(\"sentinel_activated\");
  let ready = false;
  const timer = setInterval(() => {{
    if (ready) return;
    const hmr = ctx.get(\"hmr\");
    if (hmr === undefined || !(hmr.configs instanceof Map)) return;
    const observed = new Set([...hmr.configs.keys()].map((value) => resolve(value).toLowerCase()));
    const expected = config.watchedPaths.map((value) => resolve(value).toLowerCase());
    if (!expected.every((value) => observed.has(value))) return;
    ready = true;
    clearInterval(timer);
    emit(\"stock_headless_hmr_ready\");
  }}, 20);
  ctx.effect(() => () => clearInterval(timer), \"provider-free effective-tool HMR sentinel\");
}}
""".encode()


def runner_source() -> bytes:
    source = f"""import {{ appendFileSync, closeSync, existsSync, openSync, readFileSync, writeFileSync }} from \"node:fs\";
import {{ resolve }} from \"node:path\";
import {{ createScope }} from \"@deepseek-ai/dsh-scope\";
import {{ assertEffectiveToolComposition, sanitizeEffectiveToolTerminal }} from \"./effective-tool-guard.mjs\";

export const name = \"provider-free-effective-tool-proof-runner\";
export const inject = [\"hmr\", \"agentPresets\", \"tools\"];

function writeTerminal(path, record) {{
  const descriptor = openSync(path, \"wx\");
  try {{ writeFileSync(descriptor, JSON.stringify(record) + \"\\n\", \"utf8\"); }}
  finally {{ closeSync(descriptor); }}
}}

export async function apply(ctx, config) {{
{_event_writer_source()}
  const hmr = ctx.get(\"hmr\");
  const exit = ctx.get(\"appExit\");
  if (hmr === undefined || !(hmr.configs instanceof Map)) throw new Error(\"hmr unavailable\");
  if (typeof exit !== \"function\") throw new Error(\"app exit unavailable\");
  const observed = new Set([...hmr.configs.keys()].map((value) => resolve(value).toLowerCase()));
  const expected = config.watchedPaths.map((value) => resolve(value).toLowerCase());
  if (!expected.every((value) => observed.has(value))) throw new Error(\"stock watches unavailable\");
  emit(\"effective_tool_guard_started\");
  const scope = createScope(ctx, Object.freeze({{}}));
  let terminal;
  let exitCode = 2;
  try {{
    const result = await assertEffectiveToolComposition(scope.ctx, \"emr4-bounded-worker\", [\"edit\", \"glob\", \"read\"]);
    terminal = {{
      schema_version: \"{TERMINAL_SCHEMA}\",
      stage: \"pre_provider_tool_composition\",
      code: result.coordinate,
      detail: null,
      effective_tool_names: result.effectiveToolNames,
      effective_tool_count: result.effectiveToolCount,
    }};
    exitCode = 0;
  }} catch (error) {{
    const safe = sanitizeEffectiveToolTerminal(error);
    const names = safe.detail === null ? [] : safe.detail.split(\",\").filter((value) => /^[a-z_]+$/.test(value));
    terminal = {{
      schema_version: \"{TERMINAL_SCHEMA}\",
      stage: safe.stage,
      code: safe.code,
      detail: safe.detail,
      effective_tool_names: names,
      effective_tool_count: names.length,
    }};
  }}
  try {{
    writeTerminal(config.terminalPath, terminal);
    emit(\"effective_tool_guard_terminal\");
  }} finally {{
    await scope.dispose();
    emit(\"scope_disposed\");
    emit(\"app_exit_requested\");
    exit(exitCode);
  }}
}}
"""
    return source.encode()


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode()
    counts = {
        "create_scope_count": source.count("createScope(ctx,"),
        "guard_call_count": source.count("assertEffectiveToolComposition(scope.ctx,"),
        "exclusive_terminal_count": source.count('openSync(path, "wx")'),
        "scope_dispose_count": source.count("await scope.dispose()"),
        "exit_request_count": source.count("exit(exitCode)"),
    }
    if any(value != 1 for value in counts.values()):
        raise NativeCompositionProofError("runner_call_count_mismatch")
    ordered = [
        'emit("effective_tool_guard_started")',
        "createScope(ctx,",
        "assertEffectiveToolComposition(scope.ctx,",
        "writeTerminal(config.terminalPath, terminal)",
        'emit("effective_tool_guard_terminal")',
        "await scope.dispose()",
        'emit("scope_disposed")',
        'emit("app_exit_requested")',
        "exit(exitCode)",
    ]
    positions = [source.index(fragment) for fragment in ordered]
    if positions != sorted(positions):
        raise NativeCompositionProofError("runner_causal_order_mismatch")
    if "CUSTOM_RUNNER_FAILURE" in source:
        raise NativeCompositionProofError("runner_forbidden_generic_terminal")
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), **counts}


def parse_events(path: Path, *, allow_incomplete: bool = False) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_bytes().splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not line.endswith(b"\n"):
            if allow_incomplete and index == len(lines) - 1:
                break
            raise NativeCompositionProofError("event_ledger_partial_line")
        record = json.loads(line)
        if set(record) != {"schema_version", "sequence", "event"}:
            raise NativeCompositionProofError("event_record_shape_invalid")
        if record["schema_version"] != EVENT_SCHEMA or record["sequence"] != len(records) + 1:
            raise NativeCompositionProofError("event_record_sequence_invalid")
        if record["event"] not in EXPECTED_EVENTS:
            raise NativeCompositionProofError("event_name_invalid")
        records.append(record)
    return records


def validate_events(records: list[dict[str, Any]]) -> None:
    if [record["event"] for record in records] != EXPECTED_EVENTS:
        raise NativeCompositionProofError("native_composition_event_sequence_mismatch")


def parse_terminal(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    if not payload.endswith(b"\n") or payload.count(b"\n") != 1:
        raise NativeCompositionProofError("terminal_record_count_invalid")
    terminal = json.loads(payload)
    expected_keys = {
        "schema_version",
        "stage",
        "code",
        "detail",
        "effective_tool_names",
        "effective_tool_count",
    }
    if set(terminal) != expected_keys or terminal["schema_version"] != TERMINAL_SCHEMA:
        raise NativeCompositionProofError("terminal_shape_invalid")
    if terminal["stage"] != "pre_provider_tool_composition":
        raise NativeCompositionProofError("terminal_stage_invalid")
    code = terminal["code"]
    if code not in {"EFFECTIVE_TOOL_COMPOSITION_PASSED", *FAILURE_COORDINATES}:
        raise NativeCompositionProofError("terminal_code_invalid")
    names = terminal["effective_tool_names"]
    if (
        not isinstance(names, list)
        or names != sorted(names)
        or len(names) != len(set(names))
        or any(not isinstance(name, str) or SAFE_TOOL_NAME.fullmatch(name) is None for name in names)
        or terminal["effective_tool_count"] != len(names)
    ):
        raise NativeCompositionProofError("terminal_tool_projection_invalid")
    detail = terminal["detail"]
    if detail is not None and detail != ",".join(names):
        raise NativeCompositionProofError("terminal_detail_invalid")
    return terminal


def validate_installed_packages(
    package_root: Path, contract: dict[str, Any]
) -> dict[str, str]:
    node_modules = package_root.parents[1]
    versions: dict[str, str] = {}
    for name in contract["required_installed_packages"]:
        scope, leaf = name.split("/", maxsplit=1)
        manifest = node_modules / scope / leaf / "package.json"
        if not manifest.is_file():
            raise NativeCompositionProofError("required_installed_package_missing")
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        if payload.get("name") != name or payload.get("version") != "0.1.0-rc.7":
            raise NativeCompositionProofError("required_installed_package_identity_mismatch")
        versions[name] = payload["version"]
    return versions


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    predecessor = validate_predecessors(contract)
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    blob, packages = verify_cached_packages(contract, resolved_cache)
    preset = build_preset_source(contract)
    root = Path("C:/deterministic/native-composition")
    profile = root / "home" / "profiles" / "headless"
    modules = root / "installation" / "proof"
    initial, changed = build_patch_pair(
        profile,
        root / "events.jsonl",
        root / "terminal.json",
        modules / "sentinel.mjs",
        modules / "runner.mjs",
    )
    runner = runner_source()
    return {
        "contract": contract,
        "predecessor": predecessor,
        "cache_blob_sha256": sha256_file(blob),
        "package_count": len(packages),
        "preset_sha256": sha256_bytes(preset),
        "initial_patch_sha256": sha256_bytes(initial),
        "changed_patch_sha256": sha256_bytes(changed),
        "runner": validate_runner_source(runner),
        "sentinel_sha256": sha256_bytes(sentinel_source()),
        "network_guard_sha256": sha256_bytes(network_guard_source()),
    }


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _success_terminal(terminal: dict[str, Any], contract: dict[str, Any]) -> bool:
    expected = contract["terminal"]
    return terminal == {
        "schema_version": TERMINAL_SCHEMA,
        "stage": expected["stage"],
        "code": expected["success_code"],
        "detail": expected["detail"],
        "effective_tool_names": expected["effective_tool_names"],
        "effective_tool_count": expected["effective_tool_count"],
    }


def render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["terminal"] or {}
    return f"""# Provider-free effective-tool native-boot proof report

- Result: `{evidence['result']}`
- Attempt: `{evidence['attempt_id']}`
- Native process count: `{evidence['launch']['native_boot_process_count']}`
- Exit code: `{evidence['launch']['exit_code']}`
- Duration: `{evidence['launch']['duration_ms']} ms`
- Terminal: `{terminal.get('code')}`
- Effective tools: `{', '.join(terminal.get('effective_tool_names', []))}`
- Network / agent-session / broker / model / provider counts: `0 / 0 / 0 / 0 / 0`
- Process absent: `{str(evidence['cleanup']['process_absent']).lower()}`
- Disposable root absent: `{str(evidence['cleanup']['disposable_root_absent']).lower()}`

This proves only the pinned local rc.7 native composition path and sanitized
pre-provider terminal. It is not an occupied worker or a DeepSeek model-quality
or provider-reliability result.
"""


def execute_proof(cache_root: Path | None = None) -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise NativeCompositionProofError("canonical_attempt_output_already_exists")
    check = deterministic_check(cache_root)
    contract = check["contract"]
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    blob, cached_packages = verify_cached_packages(contract, resolved_cache)
    parent = DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise NativeCompositionProofError("disposable_parent_missing")
    root = Path(tempfile.mkdtemp(prefix="dsh-native-composition-proof-", dir=parent)).resolve()
    if root.parent != parent:
        raise NativeCompositionProofError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    error: BaseException | None = None
    result = "fail"
    failure: str | None = None
    package_identity: dict[str, Any] = {}
    install_projection: dict[str, Any] = {}
    source_projection: dict[str, Any] = {}
    installed_versions: dict[str, str] = {}
    lifecycle: list[dict[str, Any]] = []
    terminal: dict[str, Any] | None = None
    network_records: list[dict[str, Any]] = []
    initial_patch = b""
    changed_patch = b""
    preset = build_preset_source(contract)
    sentinel = sentinel_source()
    runner = runner_source()
    guard = build_guard_source()
    network_guard = network_guard_source()
    launch_started_utc: str | None = None
    launch_duration_ms = 0
    exit_code: int | None = None
    mutated_after_readiness = False
    removed_environment_names = 0
    stdout_digest = sha256_bytes(b"")
    stderr_digest = sha256_bytes(b"")
    stdout_size = 0
    stderr_size = 0

    try:
        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        workspace = root / "workspace"
        installation_proof = root / "installation" / "proof"
        event_path = root / "events.jsonl"
        terminal_path = root / "terminal.json"
        network_path = root / "network.jsonl"
        stdout_path = root / "stdout.log"
        stderr_path = root / "stderr.log"
        network_guard_path = root / "network-guard.mjs"
        tarball = root / "dsh-0.1.0-rc.7.tgz"
        workspace.mkdir()
        profile_dir.mkdir(parents=True)
        _write_bytes(network_guard_path, network_guard)
        _write_bytes(tarball, blob.read_bytes())
        package_identity = verify_tarball(tarball, contract)
        if package_identity["sha256"] != contract["package"]["tarball_sha256"]:
            raise NativeCompositionProofError("materialized_tarball_sha256_mismatch")
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
            "dsh": {"profile": {"bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]}},
        }
        (profile_dir / "package.json").write_text(
            json.dumps(profile_manifest, indent=2) + "\n", encoding="utf-8"
        )
        (profile_dir / "pnpm-workspace.yaml").write_text(
            "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n", encoding="utf-8"
        )
        preset_path = home / ".agent-presets" / contract["preset"]["id"] / "agent.cordis.yml"
        _write_bytes(preset_path, preset)
        _write_bytes(installation_proof / "sentinel.mjs", sentinel)
        _write_bytes(installation_proof / "runner.mjs", runner)
        _write_bytes(installation_proof / "effective-tool-guard.mjs", guard)
        initial_patch, changed_patch = build_patch_pair(
            profile_dir,
            event_path,
            terminal_path,
            installation_proof / "sentinel.mjs",
            installation_proof / "runner.mjs",
        )
        patch_path = profile_dir / "cordis.patch.yml"
        _write_bytes(patch_path, initial_patch)

        node = shutil.which("node")
        if node is None:
            raise NativeCompositionProofError("node_not_found")
        command = [
            node,
            contract["launch"]["node_flag"],
            str(package_root / contract["package"]["bin"]),
            *contract["launch"]["profile_args"],
            "provider-free effective-tool composition proof",
        ]
        launch_started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        started = time.monotonic()
        with stdout_path.open("wb") as stdout_stream, stderr_path.open("wb") as stderr_stream:
            process = subprocess.Popen(
                command,
                cwd=workspace,
                env=environment,
                stdout=stdout_stream,
                stderr=stderr_stream,
            )
            process_started = True
            deadline = started + NATIVE_BOOT_TIMEOUT_SECONDS
            while True:
                lifecycle = parse_events(event_path, allow_incomplete=True)
                names = [record["event"] for record in lifecycle]
                if names and names != EXPECTED_EVENTS[: len(names)]:
                    raise NativeCompositionProofError("native_composition_event_prefix_invalid")
                if "stock_headless_hmr_ready" in names and not mutated_after_readiness:
                    atomic_write(patch_path, changed_patch)
                    mutated_after_readiness = True
                if process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    raise NativeCompositionProofError("native_composition_deadline_exceeded")
                time.sleep(POLL_SECONDS)
            exit_code = process.wait(timeout=5)
        launch_duration_ms = round((time.monotonic() - started) * 1000)
        stdout_payload = stdout_path.read_bytes()
        stderr_payload = stderr_path.read_bytes()
        stdout_digest, stderr_digest = sha256_bytes(stdout_payload), sha256_bytes(stderr_payload)
        stdout_size, stderr_size = len(stdout_payload), len(stderr_payload)
        lifecycle = parse_events(event_path)
        validate_events(lifecycle)
        terminal = parse_terminal(terminal_path)
        network_records = _network_attempts(network_path)
        if not mutated_after_readiness:
            raise NativeCompositionProofError("patch_not_mutated_after_readiness")
        if network_records:
            raise NativeCompositionProofError("network_attempt_observed")
        if not _success_terminal(terminal, contract):
            failure = terminal["code"]
            raise NativeCompositionProofError("guard_terminal_not_success")
        if exit_code != contract["terminal"]["success_exit_code"]:
            raise NativeCompositionProofError("native_composition_exit_code_mismatch")
        result = "pass"
    except (NativeCompositionProofError, ProofError, GuardError, subprocess.SubprocessError, OSError, ValueError, json.JSONDecodeError) as caught:
        error = caught
        if process_started and failure is None:
            failure = "NATIVE_COMPOSITION_EXECUTION_FAILED"
    finally:
        if process is not None:
            _terminate_process(process)
            if exit_code is None:
                exit_code = process.returncode
        if root.parent != parent:
            raise NativeCompositionProofError("cleanup_root_escape")
        shutil.rmtree(root)

    process_absent = process is None or process.poll() is not None
    root_absent = not root.exists()
    if not process_started:
        raise NativeCompositionProofError("prelaunch_validation_failed") from error
    if not process_absent or not root_absent:
        result = "fail"
        failure = "NATIVE_COMPOSITION_CLEANUP_INCOMPLETE"

    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "attempt_id": contract["launch"]["attempt_id"],
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
            "duration_ms": launch_duration_ms,
            "node_flag": contract["launch"]["node_flag"],
            "profile_args": contract["launch"]["profile_args"],
            "native_boot_process_count": 1,
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
        "lifecycle": {
            "events": [record["event"] for record in lifecycle],
            "exact_expected_order": [record["event"] for record in lifecycle] == EXPECTED_EVENTS,
            "readiness_source": "in_process_sentinel_only",
        },
        "terminal": terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempt_count": len(network_records),
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
            "npm_cache_retained_by_proof": False,
        },
    }
    OPERATION_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(canonical_json_bytes(evidence))
    REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
    if result != "pass":
        raise NativeCompositionProofError(f"native_composition_proof_failed:{failure}") from error
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
                    }
                )
            )
        else:
            evidence = execute_proof(args.cache_root)
            print(json.dumps({"result": evidence["result"], "attempt_id": evidence["attempt_id"]}))
    except (NativeCompositionProofError, ProofError, GuardError) as error:
        print(json.dumps({"result": "fail", "error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""One fail-closed provider-free rc.7 stock-headless-to-custom-runner HMR proof."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-boot-proof"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
EVIDENCE_PATH = OPERATION_ROOT / "provider-free-native-harness-hmr-boot-evidence.json"
EXPECTED_EVENTS = [
    "sentinel_activated",
    "stock_headless_hmr_ready",
    "custom_runner_reached",
    "app_exit_requested",
]
EVENT_SCHEMA = "ariadne.deepseek_native_harness_hmr_boot_event.v1"
EVIDENCE_SCHEMA = "ariadne.deepseek_native_harness_hmr_boot_evidence.v1"
DISPOSABLE_PARENT = Path(r"C:\Users\sarashera\EMR4-worktrees")
NATIVE_BOOT_TIMEOUT_SECONDS = 45.0
POLL_SECONDS = 0.025


class ProofError(RuntimeError):
    """A fail-closed proof construction or terminal error."""


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != (
        "ariadne.deepseek_native_harness_hmr_boot_proof_contract.v1"
    ):
        raise ProofError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise ProofError("contract_operation_mismatch")
    planning_source = contract.get("planning_source")
    if not isinstance(planning_source, str) or re.fullmatch(r"[0-9a-f]{40}", planning_source) is None:
        raise ProofError("contract_planning_source_not_full_git_oid")
    if contract.get("expected_events") != EXPECTED_EVENTS:
        raise ProofError("contract_event_sequence_mismatch")
    if contract.get("launch", {}).get("native_boot_process_count") != 1:
        raise ProofError("contract_native_boot_count_not_one")
    if contract.get("terminal", {}).get("automatic_retry") is not False:
        raise ProofError("contract_retry_not_closed")
    return contract


def verify_tarball(path: Path, contract: dict[str, Any]) -> dict[str, str]:
    if not path.is_file() or path.is_symlink():
        raise ProofError("package_tarball_not_regular_file")
    payload = path.read_bytes()
    package = contract["package"]
    sha1 = hashlib.sha1(payload).hexdigest()  # noqa: S324 - npm registry identity is SHA-1.
    integrity = "sha512-" + base64.b64encode(hashlib.sha512(payload).digest()).decode("ascii")
    if sha1 != package["tarball_sha1"]:
        raise ProofError("package_tarball_sha1_mismatch")
    if integrity != package["tarball_integrity"]:
        raise ProofError("package_tarball_integrity_mismatch")
    return {"sha1": sha1, "integrity": integrity, "sha256": sha256_bytes(payload)}


def _yaml_string(value: Path) -> str:
    return json.dumps(str(value.resolve()))


def build_patch_pair(profile_dir: Path, event_path: Path) -> tuple[bytes, bytes]:
    profile_patch = profile_dir / "cordis.patch.yml"
    home_patch = profile_dir.parents[1] / "cordis.patch.yml"
    common = f"""- id: headless-runner
  disabled: true
- id: code-runtime
  disabled: true
- id: session-telemetry-otel
  disabled: true
- insert:
    - id: provider-free-hmr-sentinel
      name: ./proof/sentinel.mjs
      config:
        eventPath: {_yaml_string(event_path)}
        watchedPaths:
          - {_yaml_string(profile_patch)}
          - {_yaml_string(home_patch)}
"""
    changed = common + f"""    - id: provider-free-hmr-custom-runner
      name: ./proof/custom-runner.mjs
      inject: [hmr]
      config:
        eventPath: {_yaml_string(event_path)}
        watchedPaths:
          - {_yaml_string(profile_patch)}
          - {_yaml_string(home_patch)}
"""
    initial = common.encode("utf-8")
    changed_bytes = changed.encode("utf-8")
    validate_patch_pair(initial, changed_bytes)
    return initial, changed_bytes


def _patch_rows(payload: bytes) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    parsed = yaml.safe_load(payload.decode("utf-8"))
    if not isinstance(parsed, list):
        raise ProofError("patch_not_top_level_array")
    direct: dict[str, Any] = {}
    inserted: list[dict[str, Any]] = []
    for row in parsed:
        if not isinstance(row, dict):
            raise ProofError("patch_row_not_mapping")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise ProofError("patch_insert_shape_invalid")
            inserted.extend(row["insert"])
        elif isinstance(row.get("id"), str):
            if row["id"] in direct:
                raise ProofError("patch_duplicate_direct_id")
            direct[row["id"]] = row
        else:
            raise ProofError("patch_unowned_row")
    return direct, inserted


def validate_patch_pair(initial: bytes, changed: bytes) -> None:
    initial_direct, initial_inserted = _patch_rows(initial)
    changed_direct, changed_inserted = _patch_rows(changed)
    expected_disabled = ["headless-runner", "code-runtime", "session-telemetry-otel"]
    for rows in (initial_direct, changed_direct):
        if list(rows) != expected_disabled:
            raise ProofError("patch_disabled_row_set_mismatch")
        if any(rows[row_id] != {"id": row_id, "disabled": True} for row_id in expected_disabled):
            raise ProofError("patch_disabled_row_not_fail_closed")
    initial_ids = [row.get("id") for row in initial_inserted]
    changed_ids = [row.get("id") for row in changed_inserted]
    if initial_ids != ["provider-free-hmr-sentinel"]:
        raise ProofError("initial_patch_custom_runner_present_or_sentinel_invalid")
    if changed_ids != ["provider-free-hmr-sentinel", "provider-free-hmr-custom-runner"]:
        raise ProofError("changed_patch_runner_set_invalid")
    if changed_inserted[:-1] != initial_inserted:
        raise ProofError("changed_patch_mutates_initial_rows")
    custom = changed_inserted[-1]
    if custom.get("inject") != ["hmr"] or custom.get("name") != "./proof/custom-runner.mjs":
        raise ProofError("custom_runner_not_hmr_bound")


def _event_writer_source() -> str:
    return f"""function emit(event) {{
  const existing = existsSync(config.eventPath)
    ? readFileSync(config.eventPath, "utf8").split(/\\r?\\n/).filter(Boolean)
    : [];
  const record = {{ schema_version: "{EVENT_SCHEMA}", sequence: existing.length + 1, event }};
  appendFileSync(config.eventPath, JSON.stringify(record) + "\\n", "utf8");
}}
"""


def sentinel_source() -> bytes:
    source = f"""import {{ appendFileSync, existsSync, readFileSync }} from "node:fs";
import {{ resolve }} from "node:path";

export const name = "provider-free-hmr-sentinel";
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
  ctx.effect(() => () => clearInterval(timer), "provider-free HMR sentinel");
}}
"""
    return source.encode("utf-8")


def custom_runner_source() -> bytes:
    source = f"""import {{ appendFileSync, existsSync, readFileSync }} from "node:fs";
import {{ resolve }} from "node:path";

export const name = "provider-free-hmr-custom-runner";
export const inject = ["hmr"];
export function apply(ctx, config) {{
{_event_writer_source()}
  const hmr = ctx.get("hmr");
  const exit = ctx.get("appExit");
  if (hmr === undefined || !(hmr.configs instanceof Map)) throw new Error("proof runner requires active HMR");
  if (typeof exit !== "function") throw new Error("proof runner requires appExit");
  const observed = new Set([...hmr.configs.keys()].map((value) => resolve(value).toLowerCase()));
  const expected = config.watchedPaths.map((value) => resolve(value).toLowerCase());
  if (!expected.every((value) => observed.has(value))) throw new Error("proof runner requires both stock patch watches");
  emit("custom_runner_reached");
  emit("app_exit_requested");
  exit(0);
}}
"""
    return source.encode("utf-8")


def network_guard_source() -> bytes:
    source = """import { appendFileSync } from "node:fs";
import { syncBuiltinESMExports } from "node:module";
import net from "node:net";
import tls from "node:tls";
import http from "node:http";
import https from "node:https";
import dns from "node:dns";
import dgram from "node:dgram";

const ledger = process.env.EMR4_HMR_NETWORK_LEDGER;
function deny(primitive) {
  if (ledger) appendFileSync(ledger, JSON.stringify({ event: "network_attempt_blocked", primitive }) + "\\n", "utf8");
  throw new Error(`provider-free proof denied network primitive: ${primitive}`);
}
net.Socket.prototype.connect = function () { return deny("net.Socket.connect"); };
net.connect = (..._args) => deny("net.connect");
net.createConnection = (..._args) => deny("net.createConnection");
tls.connect = (..._args) => deny("tls.connect");
http.request = (..._args) => deny("http.request");
http.get = (..._args) => deny("http.get");
https.request = (..._args) => deny("https.request");
https.get = (..._args) => deny("https.get");
dgram.createSocket = (..._args) => deny("dgram.createSocket");
for (const key of ["lookup", "resolve", "resolve4", "resolve6", "resolveAny", "reverse"]) {
  dns[key] = (..._args) => deny(`dns.${key}`);
  if (dns.promises && typeof dns.promises[key] === "function") dns.promises[key] = (..._args) => deny(`dns.promises.${key}`);
}
Object.defineProperty(globalThis, "fetch", { configurable: true, writable: true, value: (..._args) => deny("fetch") });
if ("WebSocket" in globalThis) Object.defineProperty(globalThis, "WebSocket", { configurable: true, writable: true, value: class { constructor() { deny("WebSocket"); } } });
syncBuiltinESMExports();
"""
    return source.encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".next")
    if temporary.exists():
        raise ProofError("atomic_patch_temporary_already_exists")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def parse_events(path: Path, *, allow_incomplete: bool = False) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = path.read_bytes()
    lines = payload.splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not line.endswith(b"\n"):
            if allow_incomplete and index == len(lines) - 1:
                break
            raise ProofError("event_ledger_partial_line")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ProofError("event_ledger_invalid_json") from error
        if set(record) != {"schema_version", "sequence", "event"}:
            raise ProofError("event_record_shape_invalid")
        if record["schema_version"] != EVENT_SCHEMA or record["sequence"] != len(records) + 1:
            raise ProofError("event_record_schema_or_sequence_invalid")
        if not isinstance(record["event"], str):
            raise ProofError("event_name_invalid")
        records.append(record)
    return records


def validate_terminal_events(records: list[dict[str, Any]]) -> None:
    observed = [record["event"] for record in records]
    if observed != EXPECTED_EVENTS:
        raise ProofError("native_harness_event_sequence_mismatch")


SENSITIVE_ENVIRONMENT_NAME = re.compile(
    r"(AUTH|BEARER|CREDENTIAL|SECRET|TOKEN|PASSWORD|API[_-]?KEY|DEEPSEEK|OPENAI|ANTHROPIC|GEMINI|VERTEX|GOOGLE|AZURE|AWS|GCP|PUSHOVER)",
    re.IGNORECASE,
)


def build_child_environment(home: Path, guard: Path, network_ledger: Path) -> tuple[dict[str, str], int]:
    child: dict[str, str] = {}
    removed = 0
    for name, value in os.environ.items():
        if SENSITIVE_ENVIRONMENT_NAME.search(name) or name.upper().endswith("_PROXY"):
            removed += 1
            continue
        child[name] = value
    child.update(
        {
            "DSH_HOME": str(home),
            "DSH_TELEMETRY_DISABLED": "1",
            "EMR4_HMR_NETWORK_LEDGER": str(network_ledger),
            "NODE_OPTIONS": f"--import={guard.resolve().as_uri()}",
            "NPM_CONFIG_OFFLINE": "true",
            "NPM_CONFIG_AUDIT": "false",
            "NPM_CONFIG_FUND": "false",
            "NPM_CONFIG_IGNORE_SCRIPTS": "true",
        }
    )
    remaining = [name for name in child if SENSITIVE_ENVIRONMENT_NAME.search(name)]
    if remaining:
        raise ProofError("credential_environment_scrub_incomplete")
    return child, removed


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _verify_installed_source(package_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    manifest_path = package_root / "package.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    package = contract["package"]
    if manifest.get("name") != package["name"] or manifest.get("version") != package["version"]:
        raise ProofError("installed_package_identity_mismatch")
    if manifest.get("bin", {}).get("dsh") != package["bin"]:
        raise ProofError("installed_package_bin_mismatch")
    bin_path = package_root / package["bin"]
    headless_patch = package_root.parent / "dsh-headless" / "cordis.patch.yml"
    hmr_source = package_root.parent / "cordis-plugin-hmr" / "lib" / "index.js"
    boot_sources = sorted((package_root / "lib").glob("profile-boot-*.js"), key=lambda item: item.stat().st_size)
    boot_source = boot_sources[-1] if boot_sources else Path()
    required = [bin_path, headless_patch, hmr_source, boot_source]
    if any(not path.is_file() for path in required):
        raise ProofError("installed_source_surface_missing")
    bin_text = bin_path.read_text(encoding="utf-8")
    headless_text = headless_patch.read_text(encoding="utf-8")
    hmr_text = hmr_source.read_text(encoding="utf-8")
    boot_text = boot_source.read_text(encoding="utf-8")
    checks = {
        "documented_headless_profile_flag": '--profile <name>' in bin_text and '"headless"' in bin_text,
        "headless_hmr_row_disabled": "- id: hmr" in headless_text and "disabled: true" in headless_text,
        "headless_runner_declared": "- id: headless-runner" in headless_text,
        "hmr_expose_internals_required": "--expose-internals is required for HMR service" in hmr_text,
        "hmr_register_config_present": "async registerConfig(" in hmr_text,
        "profile_boot_creates_watch_only_hmr": 'config: { root: [] }' in boot_text,
        "profile_boot_watches_user_patches_twice": boot_text.count("await watchUserPatches(ctx") == 2,
    }
    if not all(checks.values()):
        raise ProofError("installed_source_contract_mismatch")
    return {
        "checks": checks,
        "source_sha256": {
            "bin": sha256_file(bin_path),
            "headless_patch": sha256_file(headless_patch),
            "hmr": sha256_file(hmr_source),
            "profile_boot": sha256_file(boot_source),
        },
    }


def _offline_install(root: Path, tarball: Path, environment: dict[str, str]) -> tuple[Path, dict[str, Any]]:
    install_root = root / "installation"
    install_root.mkdir()
    (install_root / "package.json").write_text(
        json.dumps({"name": "emr4-provider-free-hmr-proof", "private": True}, indent=2) + "\n",
        encoding="utf-8",
    )
    npm = shutil.which("npm")
    if npm is None:
        raise ProofError("npm_not_found")
    started = time.monotonic()
    result = subprocess.run(
        [
            npm,
            "install",
            "--offline",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
            str(tarball.resolve()),
        ],
        cwd=install_root,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=300,
    )
    duration_ms = round((time.monotonic() - started) * 1000)
    if result.returncode != 0:
        raise ProofError("offline_package_materialisation_failed")
    package_root = install_root / "node_modules" / "@deepseek-ai" / "dsh"
    return package_root, {"exit_code": result.returncode, "duration_ms": duration_ms}


def _network_attempts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("event") != "network_attempt_blocked" or not isinstance(record.get("primitive"), str):
            raise ProofError("network_ledger_shape_invalid")
        records.append(record)
    return records


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def execute_proof(tarball: Path, output: Path = EVIDENCE_PATH) -> dict[str, Any]:
    if output.resolve() != EVIDENCE_PATH.resolve():
        raise ProofError("evidence_output_not_canonical")
    if output.exists():
        raise ProofError("evidence_output_already_exists")
    contract = load_contract()
    tarball_identity = verify_tarball(tarball, contract)
    parent = DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise ProofError("disposable_parent_missing")
    root = Path(tempfile.mkdtemp(prefix="dsh-hmr-proof-", dir=parent)).resolve()
    if root.parent != parent:
        raise ProofError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    result = "fail"
    failure: str | None = None
    install_projection: dict[str, Any] = {}
    source_projection: dict[str, Any] = {}
    lifecycle_records: list[dict[str, Any]] = []
    network_records: list[dict[str, Any]] = []
    launch_started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    launch_duration_ms = 0
    exit_code: int | None = None
    mutated_after_readiness = False
    removed_environment_names = 0
    stdout_digest = sha256_bytes(b"")
    stderr_digest = sha256_bytes(b"")
    stdout_size = 0
    stderr_size = 0
    initial_patch = b""
    changed_patch = b""
    sentinel = sentinel_source()
    custom = custom_runner_source()
    guard = network_guard_source()

    try:
        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        proof_dir = profile_dir / "proof"
        workspace = root / "workspace"
        event_path = root / "events.jsonl"
        network_path = root / "network.jsonl"
        stdout_path = root / "stdout.log"
        stderr_path = root / "stderr.log"
        guard_path = root / "network-guard.mjs"
        workspace.mkdir()
        proof_dir.mkdir(parents=True)
        _write_bytes(guard_path, guard)
        environment, removed_environment_names = build_child_environment(home, guard_path, network_path)
        package_root, install_projection = _offline_install(root, tarball, environment)
        source_projection = _verify_installed_source(package_root, contract)

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
        _write_bytes(proof_dir / "sentinel.mjs", sentinel)
        _write_bytes(proof_dir / "custom-runner.mjs", custom)
        initial_patch, changed_patch = build_patch_pair(profile_dir, event_path)
        patch_path = profile_dir / "cordis.patch.yml"
        _write_bytes(patch_path, initial_patch)

        node = shutil.which("node")
        if node is None:
            raise ProofError("node_not_found")
        bin_path = package_root / contract["package"]["bin"]
        command = [
            node,
            contract["launch"]["node_flag"],
            str(bin_path),
            *contract["launch"]["profile_args"],
            "provider-free HMR boot proof",
        ]
        started = time.monotonic()
        with stdout_path.open("wb") as stdout_stream, stderr_path.open("wb") as stderr_stream:
            process = subprocess.Popen(
                command,
                cwd=workspace,
                env=environment,
                stdout=stdout_stream,
                stderr=stderr_stream,
            )
            deadline = started + NATIVE_BOOT_TIMEOUT_SECONDS
            while True:
                lifecycle_records = parse_events(event_path, allow_incomplete=True)
                names = [record["event"] for record in lifecycle_records]
                if names and names != EXPECTED_EVENTS[: len(names)]:
                    raise ProofError("native_harness_event_prefix_invalid")
                if "stock_headless_hmr_ready" in names and not mutated_after_readiness:
                    atomic_write(patch_path, changed_patch)
                    mutated_after_readiness = True
                if process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    raise ProofError("native_harness_boot_deadline_exceeded")
                time.sleep(POLL_SECONDS)
            exit_code = process.wait(timeout=5)
        launch_duration_ms = round((time.monotonic() - started) * 1000)
        stdout_payload = stdout_path.read_bytes()
        stderr_payload = stderr_path.read_bytes()
        stdout_digest, stderr_digest = sha256_bytes(stdout_payload), sha256_bytes(stderr_payload)
        stdout_size, stderr_size = len(stdout_payload), len(stderr_payload)
        lifecycle_records = parse_events(event_path)
        network_records = _network_attempts(network_path)
        validate_terminal_events(lifecycle_records)
        if not mutated_after_readiness:
            raise ProofError("profile_patch_not_mutated_after_readiness")
        if network_records:
            raise ProofError("network_attempt_observed")
        if exit_code != contract["terminal"]["exit_code"]:
            raise ProofError("native_harness_exit_code_mismatch")
        result = "pass"
    except (ProofError, subprocess.SubprocessError, OSError, ValueError, json.JSONDecodeError) as error:
        failure = str(error)
    finally:
        if process is not None:
            _terminate_process(process)
            if exit_code is None:
                exit_code = process.returncode
        if root.parent != parent:
            raise ProofError("cleanup_root_escape")
        shutil.rmtree(root)

    root_absent = not root.exists()
    process_absent = process is None or process.poll() is not None
    if not root_absent or not process_absent:
        result = "fail"
        failure = failure or "cleanup_incomplete"
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "attempt_id": "attempt-001",
        "result": result,
        "failure_classification": failure,
        "package": {
            "name": contract["package"]["name"],
            "version": contract["package"]["version"],
            "bin": contract["package"]["bin"],
            **tarball_identity,
            "offline_install": install_projection,
        },
        "source_contract": source_projection,
        "launch": {
            "started_at_utc": launch_started_utc,
            "duration_ms": launch_duration_ms,
            "node_flag": contract["launch"]["node_flag"],
            "profile_args": contract["launch"]["profile_args"],
            "native_boot_process_count": 1 if process is not None else 0,
            "mutated_after_in_process_readiness": mutated_after_readiness,
            "exit_code": exit_code,
            "stdout_sha256": stdout_digest,
            "stderr_sha256": stderr_digest,
            "stdout_bytes": stdout_size,
            "stderr_bytes": stderr_size,
            "raw_logs_retained": False,
        },
        "composition": {
            "initial_patch_sha256": sha256_bytes(initial_patch),
            "changed_patch_sha256": sha256_bytes(changed_patch),
            "sentinel_sha256": sha256_bytes(sentinel),
            "custom_runner_sha256": sha256_bytes(custom),
            "network_guard_sha256": sha256_bytes(guard),
            "stock_runner_enabled": False,
            "code_runtime_enabled": False,
            "telemetry_enabled": False,
            "custom_runner_in_initial_patch": False,
        },
        "lifecycle": {
            "events": [record["event"] for record in lifecycle_records],
            "exact_expected_order": [record["event"] for record in lifecycle_records] == EXPECTED_EVENTS,
            "readiness_source": "in_process_sentinel_only",
        },
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempt_count": len(network_records),
            "model_request_count": 0,
            "broker_request_count": 0,
            "provider_request_count": 0,
            "agent_session_count": 0,
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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_json_bytes(evidence))
    if result != "pass":
        raise ProofError(f"native_harness_hmr_boot_proof_failed:{failure}")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--package-tarball", type=Path)
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    if not args.execute:
        load_contract()
        print("provider-free native Harness HMR boot-proof contract: pass")
        return
    if args.package_tarball is None:
        raise SystemExit("--package-tarball is required with --execute")
    evidence = execute_proof(args.package_tarball, args.output)
    print(json.dumps({"result": evidence["result"], "attempt_id": evidence["attempt_id"]}))


if __name__ == "__main__":
    main()

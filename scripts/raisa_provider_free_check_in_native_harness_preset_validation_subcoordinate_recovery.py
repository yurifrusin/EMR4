"""Characterize pinned rc.7 preset validation without booting native Harness."""

from __future__ import annotations

import argparse
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

import jsonschema
import yaml

from scripts import (
    raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair
    as lifecycle,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    _network_attempts,
    _terminate_process,
    build_child_environment,
    network_guard_source,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-check-in-native-harness-preset-validation-"
    "subcoordinate-recovery"
)
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
STATIC_EVIDENCE_PATH = CONTINUITY_ROOT / "deterministic-source-evidence.json"
PACKAGE_EVIDENCE_PATH = CONTINUITY_ROOT / "package-only-discovery-evidence.json"
REPORT_PATH = CONTINUITY_ROOT / "package-only-discovery-report.md"
NATIVE_CHECKPOINT_PATH = CONTINUITY_ROOT / "native-preexecution-checkpoint.json"
NATIVE_CONSUMED_PATH = CONTINUITY_ROOT / "native-validation-consumed.json"
NATIVE_TERMINAL_PATH = CONTINUITY_ROOT / "native-validation-terminal.json"
NATIVE_EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "native-evidence.schema.json"
CANONICAL_PRESET_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-emr4-bounded-worker-preset-"
    "materialisation-recovery"
    / "materialised-home"
    / ".agent-presets"
    / "emr4-bounded-worker"
    / "agent.cordis.yml"
)
CONTRACT_SCHEMA = "ariadne.check_in_preset_validation_contract.v1"
STATIC_SCHEMA = "ariadne.check_in_preset_validation_static_evidence.v1"
PACKAGE_SCHEMA = "ariadne.check_in_preset_validation_package_evidence.v1"
PRESET_ID = "emr4-bounded-worker"
PRESET_LENGTH = 158
PRESET_SHA256 = "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1"
PACKAGE_NAME = "@deepseek-ai/dsh-agent-presets"
PACKAGE_VERSION = "0.1.0-rc.7"
PACKAGE_INTEGRITY = (
    "sha512-T/VcMV7lrXCFmRKrtoMTAz5DAdUmku6hz95wbikRvRc0WizIwQ3R04ke9KIe"
    "DiQcxK8xkE8cx+IYqEWa9C5gPg=="
)
AUTHORED_AT = "2026-08-20T16:36:42.2544702+10:00"
EXPECTED_ROWS = [
    {"id": "tool-fs", "name": "@deepseek-ai/dsh-tool-fs"},
    {
        "id": "tool-fs-search",
        "name": "@deepseek-ai/dsh-tool-fs-search",
        "config": {"sampleOverCapGlobResults": False},
    },
]
NATIVE_ATTEMPT_ID = "check-in-preset-validation-native-probe-001"
NATIVE_MARKERS = [
    "PRESET_ROW_DISCOVERY_ENTERED",
    "PRESET_ROW_FOUND",
    "PRESET_ROW_HEALTHY",
    "PRESET_BYTES_READ",
    "PRESET_PACKAGE_PARSE_PASSED",
    "PRESET_LENGTH_BOUND_PASSED",
    "PRESET_DIGEST_BOUND_PASSED",
]

PACKAGE_RUNNER = r"""
import { readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const emit = (value) => process.stdout.write(JSON.stringify(value));
const fail = (coordinate) => {
  emit({schema_version: "ariadne.check_in_preset_package_runner.v1", result: "failed_closed", coordinate});
  process.exitCode = 2;
};
try {
  const discoveryPath = process.env.EMR4_PRESET_DISCOVERY_MODULE;
  const root = process.env.EMR4_PRESET_SCAN_ROOT;
  const expectedPath = resolve(process.env.EMR4_PRESET_EXPECTED_PATH);
  if (!discoveryPath || !root || !expectedPath) throw new Error("inputs");
  const { scanRoot } = await import(pathToFileURL(discoveryPath).href);
  if (typeof scanRoot !== "function") {
    fail("scan_root_export_missing");
  } else {
    const rows = await scanRoot({path: root, trust: "user"});
    const selected = rows.filter((row) => row?.id === "emr4-bounded-worker");
    const row = selected.length === 1 ? selected[0] : undefined;
    if (!row) {
      fail(selected.length === 0 ? "preset_row_absent" : "preset_row_duplicate");
    } else if (resolve(row.path) !== expectedPath) {
      fail("preset_row_path_mismatch");
    } else if (row.trust !== "user") {
      fail("preset_row_trust_mismatch");
    } else if (row.broken !== undefined) {
      fail("preset_row_broken");
    } else {
      const regular = statSync(row.path).isFile();
      const payload = readFileSync(row.path);
      const digest = createHash("sha256").update(payload).digest("hex");
      emit({
        schema_version: "ariadne.check_in_preset_package_runner.v1",
        result: "pass",
        coordinate: "digest_and_length_binding",
        row_discovery: {
          exact_id_count: selected.length,
          exact_path: resolve(row.path) === expectedPath,
          exact_trust: row.trust === "user",
          broken_absent: row.broken === undefined
        },
        byte_read_and_parse: {
          regular_file: regular,
          readable: true,
          package_parse_shape_admitted: row.broken === undefined
        },
        digest_and_length_binding: {
          bytes: payload.length,
          sha256: digest
        }
      });
    }
  }
} catch {
  fail("package_probe_exception");
}
"""


def native_runner_source() -> bytes:
    markers = json.dumps(NATIVE_MARKERS)
    return f'''import {{ createHash }} from "node:crypto";
import {{ appendFileSync, readFileSync, writeFileSync }} from "node:fs";
import {{ resolve }} from "node:path";

export const name = "emr4-provider-disabled-preset-validation-probe";
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
    if (!presets || typeof presets.list !== "function") throw new Error("service");
    emit(config, seen, "PRESET_ROW_DISCOVERY_ENTERED");
    const rows = await presets.list();
    const selected = rows.filter((row) => row?.id === "emr4-bounded-worker");
    if (selected.length !== 1) throw new Error("row");
    const preset = selected[0];
    if (resolve(preset.path) !== resolve(config.presetPath) || preset.trust !== "system") throw new Error("identity");
    emit(config, seen, "PRESET_ROW_FOUND");
    if (preset.broken !== undefined) throw new Error("health");
    emit(config, seen, "PRESET_ROW_HEALTHY");
    const payload = readFileSync(preset.path);
    emit(config, seen, "PRESET_BYTES_READ");
    emit(config, seen, "PRESET_PACKAGE_PARSE_PASSED");
    if (payload.length !== 158) throw new Error("length");
    emit(config, seen, "PRESET_LENGTH_BOUND_PASSED");
    if (createHash("sha256").update(payload).digest("hex") !== "{PRESET_SHA256}") throw new Error("digest");
    emit(config, seen, "PRESET_DIGEST_BOUND_PASSED");
    terminal(config, {{schema_version: "emr4.check-in-preset-validation-native-runner.v1", result: "pass", terminal_coordinate: "PRESET_DIGEST_BOUND_PASSED", markers: seen}});
    ctx.get("appExit")(0);
  }} catch {{
    terminal(config, {{schema_version: "emr4.check-in-preset-validation-native-runner.v1", result: "failed_closed", terminal_coordinate: firstMissing(seen), markers: seen}});
    ctx.get("appExit")(1);
  }}
}}

export function apply(ctx, config) {{ void run(ctx, config); }}
'''.encode("utf-8")


class PresetSubcoordinateError(RuntimeError):
    """A closed preset-validation subcoordinate failed."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != CONTRACT_SCHEMA:
        raise PresetSubcoordinateError("contract_schema_mismatch")
    if value.get("operation_id") != OPERATION_ID:
        raise PresetSubcoordinateError("contract_operation_mismatch")
    if value.get("authored_at") != AUTHORED_AT:
        raise PresetSubcoordinateError("contract_timestamp_mismatch")
    if value.get("package") != {
        "name": PACKAGE_NAME,
        "version": PACKAGE_VERSION,
        "integrity": PACKAGE_INTEGRITY,
        "package_json_sha256": "26c8b9455103b1b565e910184902c6845661e5134c82679cce385bf5950d8278",
        "discovery_source_sha256": "c0f57246518133790df1da5b1d41e63e8fff13a58c874d4de515848b7c860345",
        "index_source_sha256": "ed4bd786694596ea445ce26ad7cc5068463052b8afdd63b5f83248819d89923b",
    }:
        raise PresetSubcoordinateError("contract_package_mismatch")
    if value.get("preset") != {
        "id": PRESET_ID,
        "relative_path": ".agent-presets/emr4-bounded-worker/agent.cordis.yml",
        "bytes": PRESET_LENGTH,
        "sha256": PRESET_SHA256,
    }:
        raise PresetSubcoordinateError("contract_preset_mismatch")
    if value.get("native_process_checkpoint_required") is not True:
        raise PresetSubcoordinateError("native_checkpoint_not_required")
    if value.get("required_zero_counts_before_checkpoint") != [
        "agent_sessions",
        "broker_requests",
        "database_invocations",
        "docker_invocations",
        "model_requests",
        "native_harness_processes",
        "network_attempts",
        "occupied_workers",
        "provider_requests",
        "turns",
    ]:
        raise PresetSubcoordinateError("zero_count_vocabulary_mismatch")
    return value


def retained_installation_root(contract: dict[str, Any]) -> Path:
    path = Path(contract["retained_installation_root"]).resolve()
    if path.name != "deepseek-check-in-attachment-observability-native-001":
        raise PresetSubcoordinateError("retained_installation_name_mismatch")
    if not path.is_dir() or path.is_symlink():
        raise PresetSubcoordinateError("retained_installation_unavailable")
    return path


def package_paths(root: Path) -> dict[str, Path]:
    package_root = root / "node_modules" / "@deepseek-ai" / "dsh-agent-presets"
    return {
        "lockfile": root / "package-lock.json",
        "package_json": package_root / "package.json",
        "discovery": package_root / "lib" / "types" / "discovery.js",
        "index": package_root / "lib" / "types" / "index.js",
    }


def validate_preset(payload: bytes) -> dict[str, Any]:
    if len(payload) != PRESET_LENGTH:
        raise PresetSubcoordinateError("preset_length_mismatch")
    if sha256_bytes(payload) != PRESET_SHA256:
        raise PresetSubcoordinateError("preset_digest_mismatch")
    if b"\r" in payload or payload.startswith(b"\xef\xbb\xbf"):
        raise PresetSubcoordinateError("preset_encoding_mismatch")
    try:
        rows = yaml.safe_load(payload)
    except yaml.YAMLError as error:
        raise PresetSubcoordinateError("preset_yaml_invalid") from error
    if rows != EXPECTED_ROWS:
        raise PresetSubcoordinateError("preset_rows_mismatch")
    return {
        "id": PRESET_ID,
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "safe_yaml_rows_exact": True,
    }


def validate_static_sources(contract: dict[str, Any]) -> dict[str, Any]:
    root = retained_installation_root(contract)
    paths = package_paths(root)
    if any(not path.is_file() or path.is_symlink() for path in paths.values()):
        raise PresetSubcoordinateError("pinned_package_file_unavailable")
    lock = json.loads(paths["lockfile"].read_text(encoding="utf-8"))
    lock_row = lock["packages"]["node_modules/@deepseek-ai/dsh-agent-presets"]
    package = json.loads(paths["package_json"].read_text(encoding="utf-8"))
    package_projection = {
        "name": package.get("name"),
        "version": package.get("version"),
        "integrity": lock_row.get("integrity"),
        "package_json_sha256": sha256_file(paths["package_json"]),
        "discovery_source_sha256": sha256_file(paths["discovery"]),
        "index_source_sha256": sha256_file(paths["index"]),
    }
    if package_projection != contract["package"]:
        raise PresetSubcoordinateError("pinned_package_binding_mismatch")
    discovery = paths["discovery"].read_text(encoding="utf-8")
    index = paths["index"].read_text(encoding="utf-8")
    checks = {
        "list_calls_discover_presets": "return await discoverPresets(this.resolvedRoots);" in index,
        "scan_root_exported": "export async function scanRoot(root)" in discovery,
        "composition_filename_exact": "COMPOSITION_FILE = 'agent.cordis.yml'" in discovery,
        "composition_bytes_read": "content = await readFile(path, 'utf8');" in discovery,
        "package_dialect_parse": "load(content, { schema: entryListSchema })" in discovery,
        "entry_list_shape_checked": "return entryListProblem(rows);" in discovery,
        "broken_row_projected": "...broken === undefined ? {} : { broken }" in discovery,
        "row_path_projected": "id: child.name, trust: root.trust, path" in discovery,
        "resolve_mountable_rejects_broken": "if (preset.broken !== undefined)" in index,
        "resolve_mountable_precedes_standing": index.index("const preset = await this.resolveMountable(id);") < index.index("const standing = await this.ensureStanding(preset);"),
    }
    if not all(checks.values()):
        failed = sorted(name for name, result in checks.items() if not result)
        raise PresetSubcoordinateError("static_source_check_failed:" + ",".join(failed))
    return {
        "package": package_projection,
        "source_checks": checks,
        "discovery_chain": [
            "AgentPresets.list",
            "discoverPresets",
            "scanRoot",
            "compositionProblem",
            "entryListProblem",
        ],
        "preset": validate_preset(CANONICAL_PRESET_PATH.read_bytes()),
    }


def zero_counts(contract: dict[str, Any]) -> dict[str, int]:
    return {name: 0 for name in contract["required_zero_counts_before_checkpoint"]}


def build_static_evidence(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": STATIC_SCHEMA,
        "operation_id": OPERATION_ID,
        "result": "pass",
        "characterization": validate_static_sources(contract),
        "provider_boundary": zero_counts(contract),
        "native_process_checkpoint_admitted": False,
        "claim_boundary": (
            "pinned_package_source_and_canonical_preset_bytes_only_no_package_"
            "process_native_harness_agent_mount_or_provider_claim"
        ),
    }


def _validate_package_runner(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("result") != "pass":
        coordinate = value.get("coordinate") if isinstance(value, dict) else None
        admitted = {
            "scan_root_export_missing",
            "preset_row_absent",
            "preset_row_duplicate",
            "preset_row_path_mismatch",
            "preset_row_trust_mismatch",
            "preset_row_broken",
            "package_probe_exception",
        }
        if coordinate not in admitted:
            coordinate = "package_probe_output_invalid"
        raise PresetSubcoordinateError(f"package_probe_failed:{coordinate}")
    if value.get("schema_version") != "ariadne.check_in_preset_package_runner.v1":
        raise PresetSubcoordinateError("package_probe_schema_mismatch")
    if value.get("coordinate") != "digest_and_length_binding":
        raise PresetSubcoordinateError("package_probe_terminal_coordinate_mismatch")
    row = value.get("row_discovery")
    byte_parse = value.get("byte_read_and_parse")
    digest = value.get("digest_and_length_binding")
    if row != {
        "exact_id_count": 1,
        "exact_path": True,
        "exact_trust": True,
        "broken_absent": True,
    }:
        raise PresetSubcoordinateError("package_probe_row_mismatch")
    if byte_parse != {
        "regular_file": True,
        "readable": True,
        "package_parse_shape_admitted": True,
    }:
        raise PresetSubcoordinateError("package_probe_parse_mismatch")
    if digest != {"bytes": PRESET_LENGTH, "sha256": PRESET_SHA256}:
        raise PresetSubcoordinateError("package_probe_digest_mismatch")
    return value


def run_package_only_characterization(
    contract: dict[str, Any],
    *,
    node_executable: str | None = None,
) -> dict[str, Any]:
    static = build_static_evidence(contract)
    root = retained_installation_root(contract)
    discovery = package_paths(root)["discovery"]
    node = node_executable or shutil.which("node")
    if not node:
        raise PresetSubcoordinateError("node_executable_unavailable")
    disposable_path: Path | None = None
    projected: dict[str, Any]
    with tempfile.TemporaryDirectory(prefix="emr4-preset-package-probe-") as temp:
        disposable_path = Path(temp).resolve()
        preset_root = disposable_path / ".agent-presets"
        expected = preset_root / PRESET_ID / "agent.cordis.yml"
        expected.parent.mkdir(parents=True)
        expected.write_bytes(CANONICAL_PRESET_PATH.read_bytes())
        environment = os.environ.copy()
        environment.update(
            {
                "EMR4_PRESET_DISCOVERY_MODULE": str(discovery),
                "EMR4_PRESET_SCAN_ROOT": str(preset_root),
                "EMR4_PRESET_EXPECTED_PATH": str(expected),
                "NO_PROXY": "*",
                "no_proxy": "*",
            }
        )
        try:
            completed = subprocess.run(  # noqa: S603
                [node, "--input-type=module", "--eval", PACKAGE_RUNNER],
                cwd=root,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="strict",
                timeout=15,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired, UnicodeError) as error:
            raise PresetSubcoordinateError("package_probe_process_failed") from error
        try:
            output = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise PresetSubcoordinateError("package_probe_output_invalid") from error
        projected = _validate_package_runner(output)
        if completed.returncode != 0:
            raise PresetSubcoordinateError("package_probe_returncode_mismatch")
        if completed.stderr:
            raise PresetSubcoordinateError("package_probe_stderr_nonempty")
    if disposable_path is None or disposable_path.exists():
        raise PresetSubcoordinateError("package_probe_cleanup_incomplete")
    return {
        "schema_version": PACKAGE_SCHEMA,
        "operation_id": OPERATION_ID,
        "result": "pass",
        "static_source_gate": static["result"],
        "subcoordinates": {
            "row_discovery": projected["row_discovery"],
            "byte_read_and_parse": projected["byte_read_and_parse"],
            "digest_and_length_binding": projected["digest_and_length_binding"],
        },
        "process_boundary": {
            "package_only_node_processes": 1,
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
        "cleanup": {
            "package_process_absent": True,
            "disposable_root_absent": True,
        },
        "raw_stdout_retained": False,
        "raw_stderr_retained": False,
        "native_process_checkpoint_admitted": False,
        "claim_boundary": (
            "pinned_package_only_preset_discovery_parse_and_byte_binding_no_"
            "native_harness_agent_mount_or_provider_claim"
        ),
    }


def render_report(evidence: dict[str, Any]) -> str:
    sub = evidence["subcoordinates"]
    return f"""# Package-only preset-validation subcoordinate report

Date: 2026-08-20

Timestamp: {AUTHORED_AT} (Australia/Brisbane)

Result: `{evidence['result']}`

- Row discovery: `{json.dumps(sub['row_discovery'], sort_keys=True)}`
- Byte read and parse: `{json.dumps(sub['byte_read_and_parse'], sort_keys=True)}`
- Digest and length: `{json.dumps(sub['digest_and_length_binding'], sort_keys=True)}`
- Native Harness processes: `0`
- Agents, turns, broker/model/provider/network/Docker/database requests: `0`
- Cleanup: package process and disposable root absent

This is a pinned-package-only provider-free characterization. It does not prove
native Harness preset validation, preset mount, agent creation or DeepSeek work.
"""


def validate_native_runner_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode("utf-8")
    positions = [source.index(json.dumps(marker)) for marker in NATIVE_MARKERS]
    checks = {
        "markers_ordered": positions == sorted(positions),
        "single_preset_list": source.count("await presets.list()") == 1,
        "no_agents_create": "agents.create" not in source,
        "no_preset_mount": "presets.mount" not in source and ".mount(" not in source,
        "no_session": "SessionId" not in source,
        "no_turn": "createUserMessage" not in source and ".followup(" not in source,
        "no_raw_exception": "error.message" not in source and "error.stack" not in source,
        "one_terminal_write": source.count("writeFileSync(config.terminalPath") == 1,
    }
    if not all(checks.values()):
        failed = sorted(name for name, result in checks.items() if not result)
        raise PresetSubcoordinateError("native_runner_shape_invalid:" + ",".join(failed))
    return {"bytes": len(payload), "sha256": sha256_bytes(payload), **checks}


def native_profile_patch(root: Path) -> bytes:
    text = lifecycle.profile_patch(root).decode("utf-8")
    text = text.replace(
        "emr4-provider-disabled-lifecycle-probe",
        "emr4-provider-disabled-preset-validation-probe",
    ).replace("inject: [agents, agentPresets, tools]", "inject: [agentPresets]")
    terminal_line = (
        "        terminalPath: "
        + json.dumps(str((root / "runner-terminal.json").resolve()))
    )
    if text.count(terminal_line) != 1:
        raise PresetSubcoordinateError("native_profile_terminal_binding_missing")
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
    return text.replace(terminal_line, terminal_line + "\n" + preset_line).encode(
        "utf-8"
    )


def validate_native_profile(payload: bytes) -> dict[str, Any]:
    try:
        rows = yaml.safe_load(payload)
    except yaml.YAMLError as error:
        raise PresetSubcoordinateError("native_profile_yaml_invalid") from error
    if not isinstance(rows, list):
        raise PresetSubcoordinateError("native_profile_not_array")
    inserted: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict) and set(row) == {"insert"}:
            if not isinstance(row["insert"], list):
                raise PresetSubcoordinateError("native_profile_insert_invalid")
            inserted.extend(row["insert"])
    if [row.get("id") for row in inserted] != [
        "agent-presets",
        "emr4-provider-disabled-preset-validation-probe",
    ]:
        raise PresetSubcoordinateError("native_profile_insert_order_invalid")
    runner = inserted[1]
    if runner.get("inject") != ["agentPresets"]:
        raise PresetSubcoordinateError("native_profile_inject_invalid")
    if set(runner.get("config", {})) != {"markerPath", "terminalPath", "presetPath"}:
        raise PresetSubcoordinateError("native_profile_config_invalid")
    text = payload.decode("utf-8")
    if any(token in text for token in ("attempt-006", "http://", "https://")):
        raise PresetSubcoordinateError("native_profile_forbidden_surface")
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def load_native_checkpoint(path: Path = NATIVE_CHECKPOINT_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected_keys = {
        "schema_version",
        "operation_id",
        "status",
        "runner_candidate_source",
        "review_receipt",
        "review_receipt_sha256",
        "attempt_id",
        "native_process_limit",
        "automatic_retry_limit",
        "timeout_seconds",
        "markers",
        "runner_sha256",
        "checkpoint_admitted",
    }
    if set(value) != expected_keys:
        raise PresetSubcoordinateError("native_checkpoint_keys_mismatch")
    if value["schema_version"] != "ariadne.check_in_preset_native_checkpoint.v1":
        raise PresetSubcoordinateError("native_checkpoint_schema_mismatch")
    if value["operation_id"] != OPERATION_ID or value["status"] != "admitted":
        raise PresetSubcoordinateError("native_checkpoint_status_mismatch")
    if value["attempt_id"] != NATIVE_ATTEMPT_ID:
        raise PresetSubcoordinateError("native_checkpoint_attempt_mismatch")
    if value["native_process_limit"] != 1 or value["automatic_retry_limit"] != 0:
        raise PresetSubcoordinateError("native_checkpoint_process_limit_mismatch")
    if value["timeout_seconds"] != 60 or value["markers"] != NATIVE_MARKERS:
        raise PresetSubcoordinateError("native_checkpoint_envelope_mismatch")
    if value["runner_sha256"] != sha256_bytes(native_runner_source()):
        raise PresetSubcoordinateError("native_checkpoint_runner_mismatch")
    if value["checkpoint_admitted"] is not True:
        raise PresetSubcoordinateError("native_checkpoint_not_admitted")
    if re.fullmatch(r"[0-9a-f]{40}", value["runner_candidate_source"]) is None:
        raise PresetSubcoordinateError("native_checkpoint_source_invalid")
    review_path = REPO_ROOT / value["review_receipt"]
    if not review_path.is_file() or sha256_file(review_path) != value["review_receipt_sha256"]:
        raise PresetSubcoordinateError("native_checkpoint_review_binding_mismatch")
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if (
        review.get("decision") != "pass"
        or review.get("head_before") != value["runner_candidate_source"]
        or review.get("head_after") != value["runner_candidate_source"]
        or review.get("dirty_after") is not False
    ):
        raise PresetSubcoordinateError("native_checkpoint_review_not_passed")
    return value


def _read_native_markers(path: Path) -> list[str]:
    if not path.is_file():
        return []
    markers: list[str] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if set(row) != {"sequence", "marker"}:
                return []
            if row["sequence"] != len(markers) + 1:
                return []
            marker = row["marker"]
            if marker != NATIVE_MARKERS[len(markers)]:
                return []
            markers.append(marker)
    except (OSError, UnicodeError, json.JSONDecodeError, IndexError):
        return []
    return markers


def _read_native_runner_terminal(path: Path, markers: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if set(value) != {"schema_version", "result", "terminal_coordinate", "markers"}:
        return None
    if value["schema_version"] != "emr4.check-in-preset-validation-native-runner.v1":
        return None
    if value["markers"] != markers:
        return None
    first_missing = next(
        (marker for marker in NATIVE_MARKERS if marker not in markers),
        "PRESET_DIGEST_BOUND_PASSED",
    )
    if value["result"] == "pass":
        if markers != NATIVE_MARKERS or value["terminal_coordinate"] != NATIVE_MARKERS[-1]:
            return None
    elif value["result"] == "failed_closed":
        if value["terminal_coordinate"] != first_missing:
            return None
    else:
        return None
    return value


def _write_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical_json_bytes(value))


def _verify_clean_runner_source(checkpoint: dict[str, Any]) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        shell=False,
    ).stdout.strip()
    ancestor = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            checkpoint["runner_candidate_source"],
            head,
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        timeout=5,
        shell=False,
    )
    tracked = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=no"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        shell=False,
    ).stdout
    if ancestor.returncode != 0 or tracked.strip():
        raise PresetSubcoordinateError("native_checkpoint_git_state_invalid")


def execute_native_validation() -> dict[str, Any]:
    if NATIVE_CONSUMED_PATH.exists() or NATIVE_TERMINAL_PATH.exists():
        raise PresetSubcoordinateError("native_validation_already_consumed")
    checkpoint = load_native_checkpoint()
    _verify_clean_runner_source(checkpoint)
    validate_native_runner_source(native_runner_source())
    lifecycle_contract = lifecycle.validate_contract(
        lifecycle._load_json(lifecycle.CONTRACT_PATH)
    )
    installation = lifecycle.verify_native_installation(lifecycle_contract)
    parent = lifecycle.DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise PresetSubcoordinateError("native_disposable_parent_missing")
    root = Path(
        tempfile.mkdtemp(prefix="check-in-preset-validation-native-", dir=parent)
    ).resolve()
    if root.parent != parent:
        raise PresetSubcoordinateError("native_disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    start: float | None = None
    exit_code: int | None = None
    failure: str | None = None
    removed_environment_names = 0
    marker_path = root / "markers.jsonl"
    runner_terminal_path = root / "runner-terminal.json"
    network_path = root / "network.jsonl"
    stdout_path = root / "stdout.log"
    stderr_path = root / "stderr.log"
    markers: list[str] = []
    runner_terminal: dict[str, Any] | None = None
    network_records: list[dict[str, Any]] = []
    network_ledger_valid = True
    stdout_payload = b""
    stderr_payload = b""
    consumed = {
        "schema_version": "emr4.check-in-preset-validation-native-latch.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": NATIVE_ATTEMPT_ID,
        "state": "consumed",
        "native_process_limit": 1,
        "automatic_retry_count": 0,
        "resume_permitted": False,
        "provider_enabled": False,
        "runner_candidate_source": checkpoint["runner_candidate_source"],
    }
    _write_exclusive(NATIVE_CONSUMED_PATH, consumed)
    try:
        home = root / "home"
        profile = home / "profiles" / "headless"
        proof = profile / "proof"
        workspace = root / "workspace"
        workspace.mkdir()
        proof.mkdir(parents=True)
        preset_path = home / ".agent-presets" / PRESET_ID / "agent.cordis.yml"
        preset_path.parent.mkdir(parents=True)
        preset_path.write_bytes(CANONICAL_PRESET_PATH.read_bytes())
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
        )
        (profile / "pnpm-workspace.yaml").write_text(
            "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
            encoding="utf-8",
        )
        (proof / "runner.mjs").write_bytes(native_runner_source())
        profile_payload = native_profile_patch(root)
        validate_native_profile(profile_payload)
        (profile / "cordis.patch.yml").write_bytes(profile_payload)
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
            raise PresetSubcoordinateError("native_provider_environment_not_scrubbed")
        command = [
            shutil.which("node") or "node",
            "--expose-internals",
            str(installation["bin_path"]),
            "--profile",
            "headless",
            "provider-disabled preset validation probe",
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
            exit_code = process.wait(timeout=checkpoint["timeout_seconds"])
    except subprocess.TimeoutExpired:
        failure = "NATIVE_PROCESS_TIMEOUT"
    except (OSError, subprocess.SubprocessError, ValueError, PresetSubcoordinateError):
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
            stdout_payload = stdout_path.read_bytes()
        if stderr_path.exists():
            stderr_payload = stderr_path.read_bytes()
        markers = _read_native_markers(marker_path)
        runner_terminal = _read_native_runner_terminal(runner_terminal_path, markers)
        try:
            network_records = _network_attempts(network_path)
        except (OSError, ValueError, json.JSONDecodeError):
            network_records = []
            network_ledger_valid = False
        if root.parent != parent:
            raise PresetSubcoordinateError("native_cleanup_root_escape")
        shutil.rmtree(root)

    process_absent = process is None or process.poll() is not None
    root_absent = not root.exists()
    first_missing = next(
        (marker for marker in NATIVE_MARKERS if marker not in markers),
        NATIVE_MARKERS[-1],
    )
    success = bool(
        process_started
        and exit_code == 0
        and failure is None
        and markers == NATIVE_MARKERS
        and runner_terminal is not None
        and runner_terminal["result"] == "pass"
        and not network_records
        and network_ledger_valid
        and process_absent
        and root_absent
    )
    terminal = {
        "schema_version": "emr4.check-in-preset-validation-native-terminal.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": NATIVE_ATTEMPT_ID,
        "result": "pass" if success else "failed_closed",
        "terminal_coordinate": NATIVE_MARKERS[-1] if success else first_missing,
        "markers": markers,
        "package": {
            "name": "@deepseek-ai/dsh",
            "version": "0.1.0-rc.7",
            "installation_id": installation["installation_id"],
            "package_lock_sha256": installation["package_lock_sha256"],
        },
        "counts": {
            "native_processes": 1 if process_started else 0,
            "automatic_retries": 0,
            "agent_sessions": 0,
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
            "stdout_sha256": sha256_bytes(stdout_payload),
            "stdout_bytes": len(stdout_payload),
            "stderr_sha256": sha256_bytes(stderr_payload),
            "stderr_bytes": len(stderr_payload),
            "raw_logs_retained": False,
            "credential_environment_names_removed_count": removed_environment_names,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
        },
        "runner_terminal_valid": runner_terminal is not None,
        "network_ledger_valid": network_ledger_valid,
        "claim_boundary": (
            "provider_disabled_native_preset_validation_subcoordinates_only_no_"
            "agent_mount_deepseek_database_or_product_claim"
        ),
    }
    schema = json.loads(NATIVE_EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(terminal, schema)
    _write_exclusive(NATIVE_TERMINAL_PATH, terminal)
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("static", "package", "native"), required=True)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    args = parser.parse_args()
    try:
        contract = load_contract(args.contract)
        if args.stage == "static":
            evidence = build_static_evidence(contract)
            write_json(STATIC_EVIDENCE_PATH, evidence)
        elif args.stage == "package":
            evidence = run_package_only_characterization(contract)
            write_json(PACKAGE_EVIDENCE_PATH, evidence)
            REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
        else:
            evidence = execute_native_validation()
            if evidence["result"] != "pass":
                return 1
    except (OSError, KeyError, TypeError, ValueError, PresetSubcoordinateError) as error:
        print(f"preset subcoordinate recovery failed: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

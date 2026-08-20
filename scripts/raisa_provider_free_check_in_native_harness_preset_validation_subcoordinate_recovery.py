"""Characterize pinned rc.7 preset validation without booting native Harness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

import yaml


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("static", "package"), required=True)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    args = parser.parse_args()
    try:
        contract = load_contract(args.contract)
        if args.stage == "static":
            evidence = build_static_evidence(contract)
            write_json(STATIC_EVIDENCE_PATH, evidence)
        else:
            evidence = run_package_only_characterization(contract)
            write_json(PACKAGE_EVIDENCE_PATH, evidence)
            REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
    except (OSError, KeyError, TypeError, ValueError, PresetSubcoordinateError) as error:
        print(f"preset subcoordinate recovery failed: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

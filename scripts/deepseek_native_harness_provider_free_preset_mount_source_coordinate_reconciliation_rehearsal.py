"""Reconcile the pinned rc.7 preset-mount source without a native process."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-source-coordinate-"
    "reconciliation-rehearsal"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "source-coordinate-reconciliation-evidence.json"
REPORT_PATH = OPERATION_ROOT / "source-coordinate-reconciliation-report.md"
ACCEPTED_EVIDENCE_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-preset-composition-safe-terminal-bridge-rehearsal"
    / "safe-terminal-bridge-evidence.json"
)
ACCEPTED_INTERPRETATION_PATH = ACCEPTED_EVIDENCE_PATH.with_name(
    "preset-mount-source-coordinate-interpretation.json"
)
SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_source_reconciliation_evidence.v1"
)
CONTRACT_SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_source_reconciliation_contract.v1"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_VERSION = "0.1.0-rc.7"
FINITE_COORDINATES = [
    "PRESET_MOUNT_AGENT_SCOPE_ABSENT",
    "PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE",
    "PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED",
    "PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT",
    "PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT",
    "PRESET_MOUNT_ROOT_SERVICE_LEAK",
]
ELIMINATED_COORDINATES = [
    "preset_root_count_mismatch",
    "shipped_root_mismatch",
    "user_root_mismatch",
    "preset_roster_mismatch",
    "unknown_or_discovery_broken_preset",
    "package_import_rejected_before_factory",
    "public_agent_or_session_creation",
]
ZERO_COUNTERS = [
    "native_harness_process_count",
    "turn_count",
    "request_count",
    "broker_process_count",
    "broker_request_count",
    "occupied_worker_count",
    "model_request_count",
    "provider_request_count",
    "network_attempt_count",
    "database_invocation_count",
    "docker_invocation_count",
    "target_creation_count",
    "target_use_count",
]


class SourceReconciliationError(RuntimeError):
    """Fail-closed deterministic source reconciliation error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SourceReconciliationError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise SourceReconciliationError(f"json_object_required:{path.name}")
    return value


def load_contract() -> dict[str, Any]:
    contract = _load_object(CONTRACT_PATH)
    schema = _load_object(CONTRACT_SCHEMA_PATH)
    try:
        jsonschema.Draft202012Validator(schema).validate(contract)
    except jsonschema.ValidationError as error:
        raise SourceReconciliationError("contract_schema_rejected") from error
    if contract["schema_version"] != CONTRACT_SCHEMA_VERSION:
        raise SourceReconciliationError("contract_schema_version_mismatch")
    if contract["operation_id"] != OPERATION_ID:
        raise SourceReconciliationError("contract_operation_mismatch")
    if contract["finite_remaining_coordinates"] != FINITE_COORDINATES:
        raise SourceReconciliationError("contract_coordinate_order_mismatch")
    if contract["eliminated_coordinates"] != ELIMINATED_COORDINATES:
        raise SourceReconciliationError("contract_elimination_order_mismatch")
    if contract["required_zero_counters"] != ZERO_COUNTERS:
        raise SourceReconciliationError("contract_zero_counter_order_mismatch")
    return contract


def default_cache_root() -> Path:
    profile = os.environ.get("USERPROFILE")
    if not profile:
        raise SourceReconciliationError("userprofile_missing")
    return Path(profile) / ".cache" / "emr4-native-harness"


def _safe_source_path(source_root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise SourceReconciliationError("source_path_unsafe")
    path = source_root.joinpath(*pure.parts).resolve()
    try:
        path.relative_to(source_root.resolve())
    except ValueError as error:
        raise SourceReconciliationError("source_path_escape") from error
    if not path.is_file() or path.is_symlink():
        raise SourceReconciliationError(f"source_file_missing:{relative}")
    return path


def verify_source_bindings(
    contract: dict[str, Any], cache_root: Path
) -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    configured = PurePosixPath(contract["seed_relative_path"])
    expected_prefix = PurePosixPath("emr4-native-harness")
    if configured.parts[0] != expected_prefix.name:
        raise SourceReconciliationError("seed_relative_path_mismatch")
    source_root = cache_root.parent.joinpath(*configured.parts).resolve()
    if source_root.is_symlink() or not source_root.is_dir():
        raise SourceReconciliationError("source_root_missing_or_unsafe")

    payloads: dict[str, bytes] = {}
    bindings: list[dict[str, Any]] = []
    package_versions: dict[str, str] = {}
    for row in contract["source_files"]:
        relative = row["path"]
        path = _safe_source_path(source_root, relative)
        payload = path.read_bytes()
        if len(payload) != row["bytes"]:
            raise SourceReconciliationError(f"source_bytes_mismatch:{relative}")
        digest = sha256_bytes(payload)
        if digest != row["sha256"]:
            raise SourceReconciliationError(f"source_sha256_mismatch:{relative}")
        if relative.endswith("/package.json"):
            manifest = json.loads(payload.decode("utf-8"))
            version = manifest.get("version")
            package_versions[relative.split("/", 1)[0]] = version
        payloads[relative] = payload

    if set(package_versions) != {
        "dsh-agent-presets",
        "dsh-tool-fs",
        "dsh-tool-fs-search",
        "dsh-base",
    } or any(value != contract["package_version"] for value in package_versions.values()):
        raise SourceReconciliationError("package_version_mismatch")

    for row in contract["source_files"]:
        package = row["path"].split("/", 1)[0]
        bindings.append(
            {
                "path": row["path"],
                "bytes": row["bytes"],
                "sha256": row["sha256"],
                "version": package_versions[package],
                "passed": True,
            }
        )
    return payloads, bindings


def _requires(source: str, anchors: list[str], coordinate: str) -> bool:
    if not all(anchor in source for anchor in anchors):
        raise SourceReconciliationError(f"source_semantic_missing:{coordinate}")
    return True


def verify_source_semantics(payloads: dict[str, bytes]) -> dict[str, bool]:
    presets = payloads["dsh-agent-presets/lib/index.js"].decode("utf-8")
    checks = {
        "mount_checks_agent_scope": _requires(
            presets,
            [
                "async mount(agentCtx, id)",
                'if (agentKey === void 0) throw new Error("agent-presets: refusing to compose an unscoped context;',
            ],
            "mount_checks_agent_scope",
        ),
        "mount_resolves_mountable_roster": _requires(
            presets,
            ["const preset = await this.resolveMountable(id);"],
            "mount_resolves_mountable_roster",
        ),
        "mount_awaits_standing_scope": _requires(
            presets,
            ["const standing = await this.ensureStanding(preset);"],
            "mount_awaits_standing_scope",
        ),
        "standing_checks_composition_stamp": _requires(
            presets,
            [
                "const stamp = await compositionStamp(preset.path);",
                "if (stamp === void 0) throw new PresetMountError",
            ],
            "standing_checks_composition_stamp",
        ),
        "standing_calls_mount_preset": _requires(
            presets,
            ["await mountPreset(scope.ctx, preset);"],
            "standing_calls_mount_preset",
        ),
        "mount_awaits_entry_tree": _requires(
            presets,
            [
                "const handle = agentCtx.plugin(PresetTree, config);",
                "await handle.await();",
            ],
            "mount_awaits_entry_tree",
        ),
        "mount_checks_subtree_publication": _requires(
            presets,
            [
                "const subtree = mounted.get(config);",
                'if (subtree === void 0) throw new Error("mounted subtree did not publish its entry tree");',
            ],
            "mount_checks_subtree_publication",
        ),
        "mount_checks_inactive_rows": _requires(
            presets,
            [
                "const unusable = inactiveRows(tree);",
                "if (unusable.length > 0) throw new Error",
            ],
            "mount_checks_inactive_rows",
        ),
        "mount_checks_root_service_leaks": _requires(
            presets,
            [
                "const leaked = leakedServices(agentCtx, fiber);",
                "if (leaked.length > 0) throw new Error",
            ],
            "mount_checks_root_service_leaks",
        ),
        "scope_binding_occurs_after_standing_mount": _requires(
            presets,
            [
                "const standing = await this.ensureStanding(preset);\n\t\tthis.bindings.set(agentKey, bindScopeParent(agentKey, standing.key));",
            ],
            "scope_binding_occurs_after_standing_mount",
        ),
        "preset_tree_owns_bare_package_resolution": _requires(
            presets,
            [
                "var PresetTree = class extends Include",
                "return internal.import(specifier, base, {});",
            ],
            "preset_tree_owns_bare_package_resolution",
        ),
    }
    return checks


def _inject_block(source: str, package: str) -> list[str]:
    match = re.search(r"const inject = \[\n(?P<body>(?:\t\"[A-Za-z]+\",?\n)+)\];", source)
    if match is None:
        raise SourceReconciliationError(f"inject_block_missing:{package}")
    names = re.findall(r'\"([A-Za-z]+)\"', match.group("body"))
    if not names:
        raise SourceReconciliationError(f"inject_block_empty:{package}")
    return names


def verify_plugin_prerequisites(payloads: dict[str, bytes]) -> dict[str, Any]:
    tool_fs = payloads["dsh-tool-fs/lib/index.js"].decode("utf-8")
    tool_search = payloads["dsh-tool-fs-search/lib/index.js"].decode("utf-8")
    base = payloads["dsh-base/cordis.patch.yml"].decode("utf-8")
    fs_inject = _inject_block(tool_fs, "dsh-tool-fs")
    search_inject = _inject_block(tool_search, "dsh-tool-fs-search")
    if fs_inject != ["tools", "fs", "systemPrompt"]:
        raise SourceReconciliationError("tool_fs_inject_mismatch")
    if search_inject != ["tools", "systemPrompt", "subprocess"]:
        raise SourceReconciliationError("tool_fs_search_inject_mismatch")
    service_anchors = {
        "fs": "name: '@deepseek-ai/dsh-fs-sandbox'",
        "subprocess": "name: '@deepseek-ai/dsh-subprocess-local'",
        "systemPrompt": "name: '@deepseek-ai/dsh-system-prompt'",
        "tools": "name: '@deepseek-ai/dsh-tools'",
    }
    if not all(anchor in base for anchor in service_anchors.values()):
        raise SourceReconciliationError("host_service_declaration_missing")
    return {
        "preset_rows": [
            "@deepseek-ai/dsh-tool-fs",
            "@deepseek-ai/dsh-tool-fs-search",
        ],
        "tool_fs_inject": fs_inject,
        "tool_fs_search_inject": search_inject,
        "host_declared_services": sorted(service_anchors),
        "all_injected_services_declared_by_host": set(fs_inject + search_inject)
        <= set(service_anchors),
    }


def verify_accepted_terminal(contract: dict[str, Any]) -> dict[str, Any]:
    evidence_path = REPO_ROOT / contract["accepted_terminal_evidence"]
    interpretation_path = REPO_ROOT / contract["accepted_source_interpretation"]
    if evidence_path.resolve() != ACCEPTED_EVIDENCE_PATH.resolve():
        raise SourceReconciliationError("accepted_evidence_path_mismatch")
    if interpretation_path.resolve() != ACCEPTED_INTERPRETATION_PATH.resolve():
        raise SourceReconciliationError("accepted_interpretation_path_mismatch")
    evidence = _load_object(evidence_path)
    interpretation = _load_object(interpretation_path)
    terminal = evidence.get("controller_terminal")
    expected = {
        "candidate_source": contract["accepted_terminal_source"],
        "result": "preset_composition_failure_attributed",
        "last_admitted_stage": "private_identity_admitted",
        "safe_guard_coordinate": "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
        "safe_guard_detail": None,
        "raw_runtime_detail_retained": False,
    }
    observed = {
        "candidate_source": evidence.get("candidate_source"),
        "result": terminal.get("result") if isinstance(terminal, dict) else None,
        "last_admitted_stage": terminal.get("last_admitted_stage") if isinstance(terminal, dict) else None,
        "safe_guard_coordinate": terminal.get("safe_guard_coordinate") if isinstance(terminal, dict) else None,
        "safe_guard_detail": terminal.get("safe_guard_detail") if isinstance(terminal, dict) else None,
        "raw_runtime_detail_retained": terminal.get("raw_runtime_detail_retained") if isinstance(terminal, dict) else None,
    }
    if observed != expected:
        raise SourceReconciliationError("accepted_terminal_mismatch")
    if interpretation.get("finite_remaining_coordinates") != FINITE_COORDINATES:
        raise SourceReconciliationError("accepted_interpretation_coordinate_mismatch")
    return observed


def resolve_candidate_source() -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    candidate = completed.stdout.strip()
    if completed.returncode != 0 or FULL_OID.fullmatch(candidate) is None:
        raise SourceReconciliationError("candidate_source_resolution_failed")
    return candidate


def build_evidence(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    resolved_cache = (cache_root or default_cache_root()).resolve()
    payloads, source_bindings = verify_source_bindings(contract, resolved_cache)
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "candidate_source": resolve_candidate_source(),
        "result": "pass",
        "accepted_terminal": verify_accepted_terminal(contract),
        "source_bindings": source_bindings,
        "source_semantics": verify_source_semantics(payloads),
        "plugin_prerequisites": verify_plugin_prerequisites(payloads),
        "eliminated_coordinates": list(ELIMINATED_COORDINATES),
        "finite_remaining_coordinates": list(FINITE_COORDINATES),
        "zero_counters": {name: 0 for name in ZERO_COUNTERS},
        "claim_boundary": {
            "source_reachable_candidate_set_only": True,
            "exact_internal_coordinate_observed": False,
            "raw_runtime_error_recovered": False,
            "repair_selected": False,
            "second_native_process_authorized": False,
            "worker_launch_authorized": False,
            "occupied_model_launch_authorized": False,
        },
    }
    schema = _load_object(EVIDENCE_SCHEMA_PATH)
    try:
        jsonschema.Draft202012Validator(schema).validate(evidence)
    except jsonschema.ValidationError as error:
        raise SourceReconciliationError("evidence_schema_rejected") from error
    return evidence


def render_report(evidence: dict[str, Any], created_at: datetime | None = None) -> str:
    stamp = (created_at or datetime.now(tz=ZoneInfo("Australia/Brisbane"))).isoformat()
    coordinates = "\n".join(
        f"- `{coordinate}`" for coordinate in evidence["finite_remaining_coordinates"]
    )
    return f"""# Native Harness preset-mount source-coordinate reconciliation report

Date: {stamp[:10]}

Timestamp: {stamp} (Australia/Brisbane)

Candidate source: `{evidence['candidate_source']}`

Result: **pass**

The accepted terminal remains
`EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED`. Eight exact rc.7 source and
manifest bindings pass. The two preset rows require `tools`, `fs`,
`systemPrompt` and `subprocess`; the pinned host composition declares all four.

The source-reachable internal candidate set is:

{coordinates}

This is a finite static candidate set, not an observed internal runtime
coordinate. No raw error was recovered, no repair was selected, and no native
Harness process, turn, request, provider, target or product action occurred.
"""


def write_outputs(evidence: dict[str, Any]) -> None:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise SourceReconciliationError("output_already_exists")
    report = render_report(evidence)
    try:
        EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
        REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")
    except OSError as error:
        EVIDENCE_PATH.unlink(missing_ok=True)
        REPORT_PATH.unlink(missing_ok=True)
        raise SourceReconciliationError("output_write_failed") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    evidence = build_evidence(args.cache_root)
    if args.write:
        write_outputs(evidence)
    print(
        json.dumps(
            {
                "status": "passed",
                "operation_id": OPERATION_ID,
                "candidate_source": evidence["candidate_source"],
                "native_harness_process_count": 0,
                "finite_coordinate_count": len(FINITE_COORDINATES),
                "outputs_written": bool(args.write),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

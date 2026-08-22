"""Run one package-unloaded Node graph for the accepted guard and bridge."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration_harness.git_object_resolution import resolve_commit_source
from orchestration_harness.git_refs_snapshot import build_git_refs_snapshot
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_isolated_node_fixture_rehearsal as isolated_predecessor,
)
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_process_free_correction_rehearsal as correction_predecessor,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-root-service-forwarding-"
    "package-unloaded-guard-bridge-module-graph-rehearsal"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
PROCESS_ENVELOPE_SCHEMA_PATH = OPERATION_ROOT / "process-envelope.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
FAILURE_TERMINAL_SCHEMA_PATH = OPERATION_ROOT / "failure-terminal.schema.json"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "attempt-001-process-envelope.json"
EVIDENCE_PATH = OPERATION_ROOT / "module-graph-evidence.json"
REPORT_PATH = OPERATION_ROOT / "module-graph-report.md"
FAILURE_TERMINAL_PATH = OPERATION_ROOT / "attempt-001-failure-terminal.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_package_unloaded_guard_bridge_module_graph_rehearsal.py"
)
CORRECTION_EVIDENCE_PATH = correction_predecessor.EVIDENCE_PATH
CORRECTION_CONTROLLER_PATH = Path(correction_predecessor.__file__).resolve()
ISOLATED_EVIDENCE_PATH = isolated_predecessor.EVIDENCE_PATH
ISOLATED_CONTROLLER_PATH = Path(isolated_predecessor.__file__).resolve()
GUARD_FILENAME = "effective-tool-guard.mjs"
BRIDGE_FILENAME = correction_predecessor.predecessor.BRIDGE_PATH.name
SANITIZER_FILENAME = correction_predecessor.predecessor.SANITIZER_PATH.name
FIXTURE_FILENAME = "package_unloaded_guard_bridge_fixture.mjs"
SCOPE_STUB_MANIFEST = "node_modules/@deepseek-ai/dsh-scope/package.json"
SCOPE_STUB_SOURCE = "node_modules/@deepseek-ai/dsh-scope/index.mjs"
PRESETS_STUB_MANIFEST = "node_modules/@deepseek-ai/dsh-agent-presets/package.json"
PRESETS_STUB_SOURCE = "node_modules/@deepseek-ai/dsh-agent-presets/index.mjs"
MATERIALIZED_RELATIVE_PATHS = (
    GUARD_FILENAME,
    BRIDGE_FILENAME,
    SANITIZER_FILENAME,
    FIXTURE_FILENAME,
    SCOPE_STUB_MANIFEST,
    SCOPE_STUB_SOURCE,
    PRESETS_STUB_MANIFEST,
    PRESETS_STUB_SOURCE,
)
EXPECTED_PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PROTECTED_REFS = (
    "refs/heads/master",
    "refs/remotes/origin/master",
    "refs/heads/handoff/current",
    "refs/remotes/origin/handoff/current",
)
WINDOWS_ENVIRONMENT_KEYS = ("SystemRoot", "WINDIR", "ComSpec", "TEMP", "TMP")
FORBIDDEN_ENVIRONMENT_KEYS = frozenset({"PATH", "NODE_OPTIONS"})
FULL_OID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
CONTRACT_VERSION = (
    "ariadne.native_harness_package_unloaded_guard_bridge_module_graph_contract.v1"
)
PROCESS_ENVELOPE_VERSION = (
    "ariadne.native_harness_package_unloaded_guard_bridge_process_envelope.v1"
)
FIXTURE_RESULT_VERSION = (
    "ariadne.native_harness_package_unloaded_guard_bridge_fixture_result.v1"
)
EVIDENCE_VERSION = (
    "ariadne.native_harness_package_unloaded_guard_bridge_module_graph_evidence.v1"
)
FAILURE_TERMINAL_VERSION = (
    "ariadne.native_harness_package_unloaded_guard_bridge_failure_terminal.v1"
)
CLOSED_RESULTS = [
    "package_unloaded_guard_bridge_module_graph_pass",
    "module_graph_preflight_rejected",
    "module_graph_process_terminal",
    "module_graph_result_rejected",
]
ADMITTED_RESULT = "package_unloaded_guard_bridge_module_graph_pass"
ZERO_COUNTERS = (
    "derived_runner_materialization_count",
    "derived_runner_execution_count",
    "installed_package_import_count",
    "native_harness_process_count",
    "worker_process_count",
    "model_request_count",
    "provider_request_count",
    "network_attempt_count",
    "database_attempt_count",
    "docker_attempt_count",
    "target_creation_count",
    "target_use_count",
    "retry_count",
    "resume_count",
)
OUTPUT_PATHS = (
    PROCESS_ENVELOPE_PATH,
    EVIDENCE_PATH,
    REPORT_PATH,
    FAILURE_TERMINAL_PATH,
)


class ModuleGraphError(RuntimeError):
    """A closed module-graph coordinate failed without raw runtime detail."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def source_entry(payload: bytes) -> dict[str, Any]:
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ModuleGraphError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise ModuleGraphError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: object, code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        raise ModuleGraphError(code) from error


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    if completed.returncode != 0:
        raise ModuleGraphError("git_resolution_failed")
    return completed.stdout.strip()


def documentation_bindings() -> dict[str, str]:
    return {
        "plan_sha256": sha256_bytes(PLAN_PATH.read_bytes()),
        "threat_model_sha256": sha256_bytes(THREAT_PATH.read_bytes()),
    }


def predecessor_bindings() -> dict[str, str]:
    return {
        "accepted_correction_evidence_sha256": sha256_bytes(
            CORRECTION_EVIDENCE_PATH.read_bytes()
        ),
        "accepted_correction_controller_sha256": sha256_bytes(
            CORRECTION_CONTROLLER_PATH.read_bytes()
        ),
        "accepted_isolated_evidence_sha256": sha256_bytes(
            ISOLATED_EVIDENCE_PATH.read_bytes()
        ),
        "accepted_isolated_controller_sha256": sha256_bytes(
            ISOLATED_CONTROLLER_PATH.read_bytes()
        ),
    }


def implementation_bindings() -> dict[str, str]:
    paths = {
        "controller_sha256": Path(__file__).resolve(),
        "focused_test_sha256": FOCUSED_TEST_PATH,
        "contract_schema_sha256": CONTRACT_SCHEMA_PATH,
        "process_envelope_schema_sha256": PROCESS_ENVELOPE_SCHEMA_PATH,
        "evidence_schema_sha256": EVIDENCE_SCHEMA_PATH,
        "failure_terminal_schema_sha256": FAILURE_TERMINAL_SCHEMA_PATH,
    }
    return {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}


def accepted_graph_sources() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    correction_evidence = _load_object(CORRECTION_EVIDENCE_PATH)
    isolated_evidence = _load_object(ISOLATED_EVIDENCE_PATH)
    if (
        correction_evidence.get("result")
        != "root_service_forwarding_correction_admitted"
        or correction_evidence.get("failed_source_coordinates") != []
        or isolated_evidence.get("result") != "isolated_node_fixture_pass"
        or isolated_evidence.get("claim_boundary", {}).get(
            "isolated_bridge_behavior_proved"
        )
        is not True
    ):
        raise ModuleGraphError("accepted_predecessor_evidence_rejected")
    accepted, _ = correction_predecessor.accepted_source_inventory()
    sources = {
        "derived_guard": correction_predecessor.derive_guard_source(
            accepted["accepted_generated_guard"]
        ),
        "derived_bridge": correction_predecessor.derive_bridge_source(
            accepted["accepted_preset_mount_bridge"]
        ),
        "accepted_sanitizer": accepted["accepted_preset_mount_sanitizer"],
    }
    inventory = {name: source_entry(payload) for name, payload in sources.items()}
    expected_derived = correction_evidence.get("derived_source_inventory", {})
    expected_accepted = correction_evidence.get("accepted_source_inventory", {})
    if (
        inventory["derived_guard"] != expected_derived.get("derived_guard")
        or inventory["derived_bridge"] != expected_derived.get("derived_bridge")
        or inventory["accepted_sanitizer"]
        != expected_accepted.get("accepted_preset_mount_sanitizer")
        or inventory["derived_bridge"]
        != isolated_evidence.get("accepted_source_inventory", {}).get("derived_bridge")
        or inventory["accepted_sanitizer"]
        != isolated_evidence.get("accepted_source_inventory", {}).get(
            "accepted_sanitizer"
        )
    ):
        raise ModuleGraphError("accepted_source_binding_rejected")
    return sources, inventory


def package_stub_sources() -> dict[str, bytes]:
    manifest = lambda name: canonical_bytes(
        {
            "exports": "./index.mjs",
            "name": name,
            "private": True,
            "type": "module",
            "version": "0.0.0-emr4-fixture",
        }
    )
    scope = b"""export function scopeOf(value) {\n  if (value === null || (typeof value !== "object" && typeof value !== "function")) return undefined;\n  const scope = value.__emr4FixtureScope;\n  return scope;\n}\n"""
    presets = b"""export class PresetMountError extends Error {\n  constructor(reason) {\n    super("PRESET_MOUNT_FAILURE");\n    this.name = "PresetMountError";\n    this.reason = reason;\n  }\n}\n"""
    result = {
        SCOPE_STUB_MANIFEST: manifest("@deepseek-ai/dsh-scope"),
        SCOPE_STUB_SOURCE: scope,
        PRESETS_STUB_MANIFEST: manifest("@deepseek-ai/dsh-agent-presets"),
        PRESETS_STUB_SOURCE: presets,
    }
    forbidden = (
        "process.env",
        "node:fs",
        "node:child_process",
        "node:http",
        "node:https",
        "fetch(",
        "import(",
        "require(",
    )
    if any(
        token in payload.decode("utf-8")
        for payload in result.values()
        for token in forbidden
    ):
        raise ModuleGraphError("stub_source_forbidden_coordinate")
    return result


def exact_mount_terminal() -> dict[str, Any]:
    return {
        "stage": "preset_mount",
        "code": "PRESET_MOUNT_UNCLASSIFIED",
        "detail": None,
    }


def exact_fixture_outcome() -> dict[str, Any]:
    terminal = exact_mount_terminal()
    zero_later_calls = {
        "scope_lookup_count": 0,
        "view_call_count": 0,
        "restrict_call_count": 0,
        "schema_call_count": 0,
    }
    return {
        "schema_version": FIXTURE_RESULT_VERSION,
        "result": "pass",
        "cases": [
            {
                "case_id": "success",
                "passed": True,
                "terminal": None,
                "guard_result": {
                    "coordinate": "EFFECTIVE_TOOL_COMPOSITION_PASSED",
                    "presetId": "emr4-bounded-worker",
                    "effectiveToolNames": ["edit", "glob", "read"],
                    "effectiveToolCount": 3,
                },
                "mount_call_count": 1,
                "receiver_bound": True,
                "context_forwarded": True,
                "preset_id_forwarded": True,
                "scope_lookup_count": 1,
                "scope_forwarded": True,
                "view_call_count": 1,
                "view_scope_forwarded": True,
                "restrict_call_count": 1,
                "restrict_allow_exact": True,
                "schema_call_count": 1,
                "schema_scope_forwarded": True,
            },
            {
                "case_id": "missing_service",
                "passed": False,
                "typed_terminal_caught": True,
                "terminal": dict(terminal),
                **zero_later_calls,
            },
            {
                "case_id": "missing_mount",
                "passed": False,
                "typed_terminal_caught": True,
                "terminal": dict(terminal),
                **zero_later_calls,
            },
        ],
    }


def fixture_source() -> bytes:
    source = f'''import {{\n  PresetMountSanitizedTerminalError,\n  assertEffectiveToolComposition,\n+}} from "./{GUARD_FILENAME}";\n\n+const PRESET_ID = "emr4-bounded-worker";\n+const EXPECTED_TOOLS = Object.freeze(["edit", "glob", "read"]);\n+\n+function makeContext() {{\n+  const scope = Object.freeze({{ id: "authored-synthetic-scope" }});\n+  const calls = {{ scope: 0, view: 0, restrict: 0, schemas: 0 }};\n+  const readings = {{ scopeForwarded: false, viewScopeForwarded: false, restrictAllowExact: false, schemaScopeForwarded: false }};\n+  const tools = {{\n+    view(observedScope) {{\n+      calls.view += 1;\n+      readings.viewScopeForwarded = observedScope === scope && this === tools;\n+      return {{ knownNames: [], restrictableNames: [...EXPECTED_TOOLS] }};\n+    }},\n+    restrict(value) {{\n+      calls.restrict += 1;\n+      readings.restrictAllowExact = this === tools && JSON.stringify(value) === JSON.stringify({{ allow: [...EXPECTED_TOOLS] }});\n+    }},\n+    schemas(observedScope) {{\n+      calls.schemas += 1;\n+      readings.schemaScopeForwarded = observedScope === scope && this === tools;\n+      return EXPECTED_TOOLS.map((name) => ({{ name }}));\n+    }},\n+  }};\n+  const context = {{\n+    fixture: "authored-synthetic",\n+    tools,\n+    get __emr4FixtureScope() {{\n+      calls.scope += 1;\n+      readings.scopeForwarded = this === context;\n+      return scope;\n+    }},\n+  }};\n+  return {{ context, calls, readings }};\n+}}\n+\n+async function successCase() {{\n+  const {{ context, calls, readings }} = makeContext();\n+  const mount = {{ count: 0, receiverBound: false, contextForwarded: false, presetIdForwarded: false }};\n+  const presetService = {{\n+    async mount(observedContext, observedPresetId) {{\n+      mount.count += 1;\n+      mount.receiverBound = this === presetService;\n+      mount.contextForwarded = observedContext === context;\n+      mount.presetIdForwarded = observedPresetId === PRESET_ID;\n+    }},\n+  }};\n+  const result = await assertEffectiveToolComposition(context, presetService, PRESET_ID, [...EXPECTED_TOOLS]);\n+  return {{\n+    case_id: "success",\n+    passed: true,\n+    terminal: null,\n+    guard_result: result,\n+    mount_call_count: mount.count,\n+    receiver_bound: mount.receiverBound,\n+    context_forwarded: mount.contextForwarded,\n+    preset_id_forwarded: mount.presetIdForwarded,\n+    scope_lookup_count: calls.scope,\n+    scope_forwarded: readings.scopeForwarded,\n+    view_call_count: calls.view,\n+    view_scope_forwarded: readings.viewScopeForwarded,\n+    restrict_call_count: calls.restrict,\n+    restrict_allow_exact: readings.restrictAllowExact,\n+    schema_call_count: calls.schemas,\n+    schema_scope_forwarded: readings.schemaScopeForwarded,\n+  }};\n+}}\n+\n+async function failureCase(caseId, presetService) {{\n+  const {{ context, calls }} = makeContext();\n+  let typedTerminalCaught = false;\n+  let terminal = null;\n+  try {{\n+    await assertEffectiveToolComposition(context, presetService, PRESET_ID, [...EXPECTED_TOOLS]);\n+  }} catch (error) {{\n+    if (error instanceof PresetMountSanitizedTerminalError) {{\n+      typedTerminalCaught = true;\n+      terminal = error.terminal;\n+    }}\n+  }}\n+  return {{\n+    case_id: caseId,\n+    passed: false,\n+    typed_terminal_caught: typedTerminalCaught,\n+    terminal,\n+    scope_lookup_count: calls.scope,\n+    view_call_count: calls.view,\n+    restrict_call_count: calls.restrict,\n+    schema_call_count: calls.schemas,\n+  }};\n+}}\n+\n+const output = {{\n+  schema_version: "{FIXTURE_RESULT_VERSION}",\n+  result: "pass",\n+  cases: [\n+    await successCase(),\n+    await failureCase("missing_service", null),\n+    await failureCase("missing_mount", Object.freeze({{}})),\n+  ],\n+}};\n+process.stdout.write(JSON.stringify(output) + "\\n");\n+'''
    forbidden = (
        "process.env",
        "node:fs",
        "node:child_process",
        "node:http",
        "node:https",
        "fetch(",
        ".message",
        ".stack",
        ".cause",
    )
    if any(token in source for token in forbidden):
        raise ModuleGraphError("fixture_source_forbidden_coordinate")
    return source.encode("utf-8")


def materialized_sources() -> dict[str, bytes]:
    sources, _ = accepted_graph_sources()
    result = {
        GUARD_FILENAME: sources["derived_guard"],
        BRIDGE_FILENAME: sources["derived_bridge"],
        SANITIZER_FILENAME: sources["accepted_sanitizer"],
        FIXTURE_FILENAME: fixture_source(),
        **package_stub_sources(),
    }
    if tuple(result) != MATERIALIZED_RELATIVE_PATHS:
        raise ModuleGraphError("materialized_inventory_rejected")
    if any("runner" in path.lower() for path in result if path != BRIDGE_FILENAME):
        raise ModuleGraphError("derived_runner_materialization_rejected")
    return result


def contract_value() -> dict[str, Any]:
    _, source_inventory = accepted_graph_sources()
    stubs = package_stub_sources()
    return {
        "schema_version": CONTRACT_VERSION,
        "operation_id": OPERATION_ID,
        "git_binding_policy": {
            "mode": "machine_resolved_only",
            "plan_path": PLAN_PATH.relative_to(REPO_ROOT).as_posix(),
            "controller_path": Path(__file__)
            .resolve()
            .relative_to(REPO_ROOT)
            .as_posix(),
            "caller_authored_object_id_count": 0,
        },
        "closed_results": CLOSED_RESULTS,
        "windows_environment_keys": list(WINDOWS_ENVIRONMENT_KEYS),
        "case_ids": ["success", "missing_service", "missing_mount"],
        "materialized_relative_paths": list(MATERIALIZED_RELATIVE_PATHS),
        "required_zero_counters": list(ZERO_COUNTERS),
        "documentation_bindings": documentation_bindings(),
        "predecessor_bindings": predecessor_bindings(),
        "implementation_bindings": implementation_bindings(),
        "accepted_source_inventory": source_inventory,
        "stub_source_inventory": {
            path: source_entry(payload) for path, payload in stubs.items()
        },
        "fixture_source_inventory": source_entry(fixture_source()),
        "expected_result": exact_fixture_outcome(),
        "claim_boundary": {
            "package_unloaded_guard_bridge_graph_only": True,
            "derived_runner_proved": False,
            "installed_package_loaded": False,
            "native_harness_proved": False,
            "worker_model_provider_executed": False,
            "retry_authorized": False,
            "product_authority": False,
        },
    }


def write_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = contract_value()
    _validate(CONTRACT_SCHEMA_PATH, value, "contract_schema_rejected")
    serialized = json.dumps(value, sort_keys=True)
    if FULL_OID.search(serialized) is not None:
        raise ModuleGraphError("caller_authored_git_object_id_rejected")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    return value


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_object(path)
    _validate(CONTRACT_SCHEMA_PATH, contract, "contract_schema_rejected")
    if FULL_OID.search(json.dumps(contract, sort_keys=True)) is not None:
        raise ModuleGraphError("caller_authored_git_object_id_rejected")
    if contract != contract_value():
        raise ModuleGraphError("contract_rejected")
    return contract


def machine_git_bindings() -> dict[str, Any]:
    snapshot = build_git_refs_snapshot(
        repo_root=REPO_ROOT,
        expected_protected_commit=EXPECTED_PROTECTED_COMMIT,
        protected_refs=PROTECTED_REFS,
    )
    if (
        snapshot["status"] != "passed"
        or snapshot["tracked_worktree_clean"] is not True
        or snapshot["branch_origin_aligned"] is not True
        or snapshot["protected_refs_aligned"] is not True
    ):
        raise ModuleGraphError("module_graph_preflight_rejected")
    plan_observed = _git(
        "log", "-1", "--format=%H", "--", PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    )
    controller_observed = _git(
        "log",
        "-1",
        "--format=%H",
        "--",
        Path(__file__).resolve().relative_to(REPO_ROOT).as_posix(),
    )
    plan = resolve_commit_source(repo_root=REPO_ROOT, source_head=plan_observed)
    candidate = resolve_commit_source(
        repo_root=REPO_ROOT, source_head=controller_observed
    )
    if (
        plan["status"] != "passed"
        or candidate["status"] != "passed"
        or FULL_OID.fullmatch(plan["resolved_commit"]) is None
        or FULL_OID.fullmatch(candidate["resolved_commit"]) is None
    ):
        raise ModuleGraphError("module_graph_preflight_rejected")
    _git(
        "merge-base",
        "--is-ancestor",
        plan["resolved_commit"],
        candidate["resolved_commit"],
    )
    return {
        "policy": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
        "planning_source_commit": plan["resolved_commit"],
        "candidate_source_commit": candidate["resolved_commit"],
        "planning_source_is_ancestor_of_candidate": True,
        "branch": snapshot["branch"],
        "branch_origin_aligned": True,
        "protected_refs_aligned": True,
        "tracked_worktree_clean": True,
        "docs_branding_preserved": snapshot["preserved_untracked_paths"][
            "docs/branding"
        ],
    }


def minimum_windows_environment(
    source: dict[str, str] | os._Environ[str] | None = None,
) -> dict[str, str]:
    environment = os.environ if source is None else source
    if any(not environment.get(key) for key in WINDOWS_ENVIRONMENT_KEYS):
        raise ModuleGraphError("module_graph_preflight_rejected")
    result = {key: environment[key] for key in WINDOWS_ENVIRONMENT_KEYS}
    if (
        tuple(result) != WINDOWS_ENVIRONMENT_KEYS
        or set(result) & FORBIDDEN_ENVIRONMENT_KEYS
        or len(result) != len(WINDOWS_ENVIRONMENT_KEYS)
    ):
        raise ModuleGraphError("module_graph_preflight_rejected")
    return result


def environment_projection() -> dict[str, Any]:
    return {
        "keys": list(WINDOWS_ENVIRONMENT_KEYS),
        "key_count": len(WINDOWS_ENVIRONMENT_KEYS),
        "values_retained": False,
        "path_present": False,
        "node_options_present": False,
    }


def resolved_node_executable() -> Path:
    raw = shutil.which("node")
    if not raw:
        raise ModuleGraphError("module_graph_preflight_rejected")
    node = Path(raw).resolve()
    if not node.is_absolute() or not node.is_file():
        raise ModuleGraphError("module_graph_preflight_rejected")
    return node


def build_process_envelope(
    *,
    candidate_source: str,
    returncode: int,
    stdout: bytes,
    stderr: bytes,
    fixture_root_absent: bool,
) -> dict[str, Any]:
    envelope = {
        "schema_version": PROCESS_ENVELOPE_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "numeric_exit_code": returncode,
        "stdout_bytes": len(stdout),
        "stdout_sha256": sha256_bytes(stdout),
        "stderr_bytes": len(stderr),
        "stderr_sha256": sha256_bytes(stderr),
        "stream_content_retained": False,
        "raw_runtime_detail_retained": False,
        "executable_path_retained": False,
        "fixture_root_path_retained": False,
        "fixture_root_absent": fixture_root_absent,
        "environment": environment_projection(),
        "materialized_file_count": len(MATERIALIZED_RELATIVE_PATHS),
        "local_stub_package_count": 2,
        "installed_package_import_count": 0,
        "node_process_count": 1,
        "native_harness_process_count": 0,
        "worker_model_provider_process_count": 0,
        "further_process_authorized": False,
    }
    _validate(
        PROCESS_ENVELOPE_SCHEMA_PATH, envelope, "process_envelope_schema_rejected"
    )
    return envelope


def run_graph_once(
    *,
    node: Path,
    environment: dict[str, str],
    sources: dict[str, bytes],
    candidate_source: str,
    envelope_path: Path = PROCESS_ENVELOPE_PATH,
) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    root_path: Path | None = None
    completed: subprocess.CompletedProcess[bytes]
    try:
        with tempfile.TemporaryDirectory(
            prefix="emr4-package-unloaded-guard-graph-"
        ) as raw_root:
            root_path = Path(raw_root)
            for relative, payload in sources.items():
                destination = root_path / Path(relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payload)
            observed = sorted(
                path.relative_to(root_path).as_posix()
                for path in root_path.rglob("*")
                if path.is_file()
            )
            if observed != sorted(MATERIALIZED_RELATIVE_PATHS):
                raise ModuleGraphError("module_graph_preflight_rejected")
            fixture_path = (root_path / FIXTURE_FILENAME).resolve()
            try:
                completed = subprocess.run(
                    [str(node), str(fixture_path)],
                    cwd=root_path,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=False,
                    timeout=30,
                )
            except subprocess.TimeoutExpired as error:
                completed = subprocess.CompletedProcess(
                    args=[str(node), str(fixture_path)],
                    returncode=-1,
                    stdout=error.stdout or b"",
                    stderr=error.stderr or b"",
                )
    except ModuleGraphError:
        raise
    except OSError as error:
        raise ModuleGraphError("module_graph_process_terminal") from error
    root_absent = root_path is not None and not root_path.exists()
    envelope = build_process_envelope(
        candidate_source=candidate_source,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        fixture_root_absent=root_absent,
    )
    envelope_path.parent.mkdir(parents=True, exist_ok=True)
    envelope_path.write_bytes(canonical_bytes(envelope))
    return completed, envelope


def _require_keys(value: dict[str, Any], keys: list[str], code: str) -> None:
    if list(value) != keys:
        raise ModuleGraphError(code)


def validate_fixture_result(
    *, completed: subprocess.CompletedProcess[bytes], contract: dict[str, Any]
) -> dict[str, Any]:
    if completed.returncode != 0 or completed.stderr != b"":
        raise ModuleGraphError("module_graph_process_terminal")
    try:
        stdout = completed.stdout.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ModuleGraphError("module_graph_result_rejected") from error
    if not stdout.endswith("\n") or stdout.count("\n") != 1 or "\r" in stdout:
        raise ModuleGraphError("module_graph_process_terminal")
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise ModuleGraphError("module_graph_result_rejected") from error
    if not isinstance(value, dict):
        raise ModuleGraphError("module_graph_result_rejected")
    _require_keys(
        value, ["schema_version", "result", "cases"], "module_graph_result_rejected"
    )
    cases = value.get("cases")
    if not isinstance(cases, list) or len(cases) != 3:
        raise ModuleGraphError("module_graph_result_rejected")
    _require_keys(
        cases[0],
        [
            "case_id",
            "passed",
            "terminal",
            "guard_result",
            "mount_call_count",
            "receiver_bound",
            "context_forwarded",
            "preset_id_forwarded",
            "scope_lookup_count",
            "scope_forwarded",
            "view_call_count",
            "view_scope_forwarded",
            "restrict_call_count",
            "restrict_allow_exact",
            "schema_call_count",
            "schema_scope_forwarded",
        ],
        "module_graph_result_rejected",
    )
    if not isinstance(cases[0].get("guard_result"), dict):
        raise ModuleGraphError("module_graph_result_rejected")
    _require_keys(
        cases[0]["guard_result"],
        ["coordinate", "presetId", "effectiveToolNames", "effectiveToolCount"],
        "module_graph_result_rejected",
    )
    for row in cases[1:]:
        if not isinstance(row, dict):
            raise ModuleGraphError("module_graph_result_rejected")
        _require_keys(
            row,
            [
                "case_id",
                "passed",
                "typed_terminal_caught",
                "terminal",
                "scope_lookup_count",
                "view_call_count",
                "restrict_call_count",
                "schema_call_count",
            ],
            "module_graph_result_rejected",
        )
        terminal = row.get("terminal")
        if not isinstance(terminal, dict):
            raise ModuleGraphError("module_graph_result_rejected")
        _require_keys(
            terminal, ["stage", "code", "detail"], "module_graph_result_rejected"
        )
    if value != contract["expected_result"]:
        raise ModuleGraphError("module_graph_result_rejected")
    return value


def build_failure_terminal(
    *, candidate_source: str, result: str, code: str, envelope_sha256: str
) -> dict[str, Any]:
    terminal = {
        "schema_version": FAILURE_TERMINAL_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "result": result,
        "terminal": {
            "stage": "package_unloaded_module_graph",
            "code": code,
            "detail": None,
        },
        "process_envelope_sha256": envelope_sha256,
        "raw_runtime_detail_retained": False,
        "further_process_authorized": False,
    }
    _validate(
        FAILURE_TERMINAL_SCHEMA_PATH, terminal, "failure_terminal_schema_rejected"
    )
    return terminal


def build_evidence(
    *,
    contract: dict[str, Any],
    git_binding: dict[str, Any],
    source_inventory: dict[str, dict[str, Any]],
    stub_inventory: dict[str, dict[str, Any]],
    fixture_inventory: dict[str, Any],
    outcome: dict[str, Any],
    process_envelope: dict[str, Any],
) -> dict[str, Any]:
    evidence = {
        "schema_version": EVIDENCE_VERSION,
        "operation_id": OPERATION_ID,
        "result": ADMITTED_RESULT,
        "git_binding": git_binding,
        "accepted_source_inventory": source_inventory,
        "stub_source_inventory": stub_inventory,
        "fixture_source_inventory": fixture_inventory,
        "materialized_relative_paths": list(MATERIALIZED_RELATIVE_PATHS),
        "process_envelope_sha256": sha256_bytes(canonical_bytes(process_envelope)),
        "process_envelope_recorded_before_interpretation": True,
        "fixture_outcome": outcome,
        "environment": environment_projection(),
        "cleanup": {
            "fixture_root_absent": process_envelope["fixture_root_absent"],
            "fixture_root_path_retained": False,
            "materialized_javascript_retained": False,
            "materialized_package_manifests_retained": False,
        },
        "process_boundary": {
            "node_process_count": 1,
            "guard_module_execution_count": 1,
            "bridge_module_execution_count": 1,
            "sanitizer_module_execution_count": 1,
            "local_stub_package_count": 2,
            "materialized_file_count": len(MATERIALIZED_RELATIVE_PATHS),
            **{name: 0 for name in contract["required_zero_counters"]},
        },
        "claim_boundary": {
            "package_unloaded_guard_bridge_graph_proved": True,
            "derived_runner_proved": False,
            "installed_package_loaded": False,
            "native_harness_proved": False,
            "worker_model_provider_executed": False,
            "retry_authorized": False,
            "product_authority": False,
        },
    }
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "evidence_schema_rejected")
    return evidence


def render_report(evidence: dict[str, Any], timestamp: str) -> str:
    candidate = evidence["git_binding"]["candidate_source_commit"]
    return f"""# Native Harness package-unloaded guard–bridge module-graph report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **{evidence["result"]}**

Candidate source: `{candidate}`

Exactly one isolated authored-synthetic Node process evaluated the exact
derived guard, bridge and sanitizer with two local package stubs. The success
case mounted once, resolved the exact synthetic scope, applied one exact tool
restriction and projected `edit`, `glob`, `read`. Missing service and missing
mount each reduced to `PRESET_MOUNT_UNCLASSIFIED` with null detail before any
scope or tool-surface call.

The content-free process envelope was persisted before stream decoding or JSON
interpretation. The five-key child environment retained no values, the
installed package was unloaded, and the disposable root plus all eight files
were absent before admission.

No derived runner, installed-package import, native Harness, DeepSeek worker,
model, provider, network, database, Docker, target, retry or resume activity
occurred. This proves the package-unloaded guard–bridge graph only.
"""


def _ensure_fresh_outputs() -> None:
    if any(path.exists() for path in OUTPUT_PATHS):
        raise ModuleGraphError("module_graph_preflight_rejected")


def execute() -> dict[str, Any]:
    contract = load_contract()
    _ensure_fresh_outputs()
    _, source_inventory = accepted_graph_sources()
    stubs = package_stub_sources()
    stub_inventory = {path: source_entry(payload) for path, payload in stubs.items()}
    fixture_inventory = source_entry(fixture_source())
    sources = materialized_sources()
    git_binding = machine_git_bindings()
    node = resolved_node_executable()
    environment = minimum_windows_environment()
    completed, envelope = run_graph_once(
        node=node,
        environment=environment,
        sources=sources,
        candidate_source=git_binding["candidate_source_commit"],
    )
    envelope_sha256 = sha256_bytes(canonical_bytes(envelope))
    try:
        outcome = validate_fixture_result(completed=completed, contract=contract)
        if envelope["fixture_root_absent"] is not True:
            raise ModuleGraphError("module_graph_process_terminal")
    except ModuleGraphError as error:
        result = (
            "module_graph_process_terminal"
            if str(error) == "module_graph_process_terminal"
            else "module_graph_result_rejected"
        )
        terminal = build_failure_terminal(
            candidate_source=git_binding["candidate_source_commit"],
            result=result,
            code=str(error),
            envelope_sha256=envelope_sha256,
        )
        FAILURE_TERMINAL_PATH.write_bytes(canonical_bytes(terminal))
        raise
    evidence = build_evidence(
        contract=contract,
        git_binding=git_binding,
        source_inventory=source_inventory,
        stub_inventory=stub_inventory,
        fixture_inventory=fixture_inventory,
        outcome=outcome,
        process_envelope=envelope,
    )
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    REPORT_PATH.write_text(render_report(evidence, timestamp), encoding="utf-8")
    return evidence


def check() -> dict[str, Any]:
    contract = load_contract()
    _, source_inventory = accepted_graph_sources()
    stubs = package_stub_sources()
    stub_inventory = {path: source_entry(payload) for path, payload in stubs.items()}
    fixture_inventory = source_entry(fixture_source())
    if (
        source_inventory != contract["accepted_source_inventory"]
        or stub_inventory != contract["stub_source_inventory"]
        or fixture_inventory != contract["fixture_source_inventory"]
    ):
        raise ModuleGraphError("committed_source_inventory_rejected")
    git_binding = machine_git_bindings()
    envelope = _load_object(PROCESS_ENVELOPE_PATH)
    _validate(
        PROCESS_ENVELOPE_SCHEMA_PATH, envelope, "process_envelope_schema_rejected"
    )
    evidence = _load_object(EVIDENCE_PATH)
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "evidence_schema_rejected")
    if FAILURE_TERMINAL_PATH.exists():
        raise ModuleGraphError("failure_terminal_present")
    if (
        envelope["candidate_source"] != git_binding["candidate_source_commit"]
        or envelope["numeric_exit_code"] != 0
        or envelope["stderr_bytes"] != 0
        or envelope["node_process_count"] != 1
        or envelope["fixture_root_absent"] is not True
        or evidence["git_binding"] != git_binding
        or evidence["accepted_source_inventory"] != source_inventory
        or evidence["stub_source_inventory"] != stub_inventory
        or evidence["fixture_source_inventory"] != fixture_inventory
        or evidence["fixture_outcome"] != contract["expected_result"]
        or evidence["process_envelope_sha256"]
        != sha256_bytes(canonical_bytes(envelope))
    ):
        raise ModuleGraphError("committed_evidence_rejected")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if (
        f"Candidate source: `{git_binding['candidate_source_commit']}`" not in report
        or f"Result: **{ADMITTED_RESULT}**" not in report
    ):
        raise ModuleGraphError("committed_report_rejected")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-contract", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write_contract:
            contract = write_contract()
            print(
                json.dumps(
                    {
                        "operation_id": OPERATION_ID,
                        "result": "contract_written",
                        "materialized_file_count": len(
                            contract["materialized_relative_paths"]
                        ),
                    },
                    sort_keys=True,
                )
            )
            return 0
        evidence = execute() if args.execute else check()
    except ModuleGraphError as error:
        raise SystemExit(str(error)) from None
    print(
        json.dumps(
            {
                "operation_id": OPERATION_ID,
                "result": evidence["result"],
                "candidate_source": evidence["git_binding"]["candidate_source_commit"],
                "node_process_count": evidence["process_boundary"][
                    "node_process_count"
                ],
                "native_harness_process_count": evidence["process_boundary"][
                    "native_harness_process_count"
                ],
                "fixture_root_absent": evidence["cleanup"]["fixture_root_absent"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

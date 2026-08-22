"""Evaluate the complete derived runner once without loading the DSH package."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
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
    deepseek_native_harness_provider_free_guard_bridge_import_closure_recovery_rehearsal
    as accepted_graph,
)
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_process_free_correction_rehearsal
    as accepted_runner,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-complete-package-unloaded-runner-"
    "evaluation-rehearsal"
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
EVIDENCE_PATH = OPERATION_ROOT / "complete-runner-evaluation-evidence.json"
REPORT_PATH = OPERATION_ROOT / "complete-runner-evaluation-report.md"
FAILURE_TERMINAL_PATH = OPERATION_ROOT / "attempt-001-failure-terminal.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_complete_package_unloaded_runner_evaluation_rehearsal.py"
)
PREDECESSOR_EVIDENCE_PATH = accepted_graph.EVIDENCE_PATH
PREDECESSOR_CONTROLLER_PATH = Path(accepted_graph.__file__).resolve()

RUNNER_FILENAME = "derived-runner.mjs"
GUARD_FILENAME = accepted_graph.GUARD_FILENAME
BRIDGE_FILENAME = accepted_graph.BRIDGE_TARGET_FILENAME
SANITIZER_FILENAME = accepted_graph.SANITIZER_FILENAME
FIXTURE_FILENAME = "complete_package_unloaded_runner_fixture.mjs"
SIDECAR_FILENAME = "complete-runner-sidecar.json"
AGENT_MANIFEST = "node_modules/@deepseek-ai/dsh-agent/package.json"
AGENT_SOURCE = "node_modules/@deepseek-ai/dsh-agent/index.mjs"
SESSION_MANIFEST = "node_modules/@deepseek-ai/dsh-session/package.json"
SESSION_SOURCE = "node_modules/@deepseek-ai/dsh-session/index.mjs"
SCOPE_MANIFEST = accepted_graph.SCOPE_STUB_MANIFEST
SCOPE_SOURCE = accepted_graph.SCOPE_STUB_SOURCE
PRESETS_MANIFEST = accepted_graph.PRESETS_STUB_MANIFEST
PRESETS_SOURCE = accepted_graph.PRESETS_STUB_SOURCE
MATERIALIZED_RELATIVE_PATHS = (
    RUNNER_FILENAME,
    GUARD_FILENAME,
    BRIDGE_FILENAME,
    SANITIZER_FILENAME,
    FIXTURE_FILENAME,
    AGENT_MANIFEST,
    AGENT_SOURCE,
    SESSION_MANIFEST,
    SESSION_SOURCE,
    SCOPE_MANIFEST,
    SCOPE_SOURCE,
    PRESETS_MANIFEST,
    PRESETS_SOURCE,
)

EXPECTED_SOURCE_INVENTORY = {
    "derived_runner": {
        "bytes": 12950,
        "sha256": "5ef3b25babad23f4851faf7981cbdd6e77bf04701e91bf9ed80387df53f93ab9",
    },
    "derived_guard": {
        "bytes": 4501,
        "sha256": "76029da0f9c030651fd10c0df16f4e75e86b2269d7560af7f94c74680f8598b9",
    },
    "derived_bridge": {
        "bytes": 1661,
        "sha256": "3a49b28174eeefd77d7efe0a00498901ac6636b637ed9dfe60aba46980df1d0b",
    },
    "accepted_sanitizer": {
        "bytes": 2439,
        "sha256": "12552925a600dc951afc30b9a738746499c7e2f4cefc9962bc05fb06780f158f",
    },
}
EXPECTED_NODE_BUILTINS = ("node:crypto", "node:fs", "node:path")
EXPECTED_RELATIVE_EDGES = (
    (RUNNER_FILENAME, f"./{GUARD_FILENAME}", GUARD_FILENAME, "dynamic"),
    (GUARD_FILENAME, f"./{BRIDGE_FILENAME}", BRIDGE_FILENAME, "static"),
    (BRIDGE_FILENAME, f"./{SANITIZER_FILENAME}", SANITIZER_FILENAME, "static"),
    (FIXTURE_FILENAME, f"./{RUNNER_FILENAME}", RUNNER_FILENAME, "static"),
)
EXPECTED_BARE_EDGES = (
    (RUNNER_FILENAME, "@deepseek-ai/dsh-agent", AGENT_MANIFEST, AGENT_SOURCE, "dynamic"),
    (RUNNER_FILENAME, "@deepseek-ai/dsh-session", SESSION_MANIFEST, SESSION_SOURCE, "dynamic"),
    (GUARD_FILENAME, "@deepseek-ai/dsh-scope", SCOPE_MANIFEST, SCOPE_SOURCE, "static"),
    (GUARD_FILENAME, "@deepseek-ai/dsh-agent-presets", PRESETS_MANIFEST, PRESETS_SOURCE, "static"),
)
EXPECTED_BUILTIN_EDGES = tuple(
    (RUNNER_FILENAME, specifier, "static") for specifier in EXPECTED_NODE_BUILTINS
)
WINDOWS_ENVIRONMENT_KEYS = accepted_graph.WINDOWS_ENVIRONMENT_KEYS
FORBIDDEN_ENVIRONMENT_KEYS = accepted_graph.FORBIDDEN_ENVIRONMENT_KEYS
EXPECTED_PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PROTECTED_REFS = accepted_graph.PROTECTED_REFS
FULL_OID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
STATIC_FROM_SPECIFIER = re.compile(
    r"(?ms)^[ \t]*(?:import|export)\b(?:(?!;).)*?\bfrom\s*"
    r"(?P<quote>['\"])(?P<specifier>[^'\"]+)(?P=quote)\s*;"
)
STATIC_SIDE_EFFECT_SPECIFIER = re.compile(
    r"(?m)^[ \t]*import\s*(?P<quote>['\"])(?P<specifier>[^'\"]+)"
    r"(?P=quote)\s*;"
)
DYNAMIC_SPECIFIER = re.compile(
    r"\bimport\s*\(\s*(?P<quote>['\"])(?P<specifier>[^'\"]+)(?P=quote)\s*\)"
)
IMPORT_TOKEN = re.compile(r"\bimport\s*(?:\(|[{'\"])")

CONTRACT_VERSION = "ariadne.native_harness_complete_package_unloaded_runner_contract.v1"
PROCESS_ENVELOPE_VERSION = (
    "ariadne.native_harness_complete_package_unloaded_runner_process_envelope.v1"
)
FIXTURE_RESULT_VERSION = (
    "ariadne.native_harness_complete_package_unloaded_runner_fixture_result.v1"
)
EVIDENCE_VERSION = "ariadne.native_harness_complete_package_unloaded_runner_evidence.v1"
FAILURE_TERMINAL_VERSION = (
    "ariadne.native_harness_complete_package_unloaded_runner_failure_terminal.v1"
)
CLOSED_RESULTS = [
    "complete_package_unloaded_runner_evaluation_pass",
    "complete_runner_preflight_rejected",
    "complete_runner_process_terminal",
    "complete_runner_result_rejected",
]
ADMITTED_RESULT = CLOSED_RESULTS[0]
ZERO_COUNTERS = (
    "installed_package_import_count",
    "native_harness_process_count",
    "worker_process_count",
    "model_request_count",
    "provider_request_count",
    "broker_process_count",
    "broker_request_count",
    "network_attempt_count",
    "database_attempt_count",
    "docker_attempt_count",
    "target_creation_count",
    "target_use_count",
    "retry_count",
    "resume_count",
)
OUTPUT_PATHS = (PROCESS_ENVELOPE_PATH, EVIDENCE_PATH, REPORT_PATH, FAILURE_TERMINAL_PATH)


class CompleteRunnerError(RuntimeError):
    """A closed complete-runner coordinate failed."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_entry(value: bytes) -> dict[str, Any]:
    return {"bytes": len(value), "sha256": sha256_bytes(value)}


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CompleteRunnerError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise CompleteRunnerError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: object, code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        raise CompleteRunnerError(code) from error


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
        raise CompleteRunnerError("git_resolution_failed")
    return completed.stdout.strip()


def documentation_bindings() -> dict[str, str]:
    return {
        "plan_sha256": sha256_bytes(PLAN_PATH.read_bytes()),
        "threat_model_sha256": sha256_bytes(THREAT_PATH.read_bytes()),
    }


def predecessor_bindings() -> dict[str, str]:
    return {
        "accepted_graph_controller_sha256": sha256_bytes(
            PREDECESSOR_CONTROLLER_PATH.read_bytes()
        ),
        "accepted_graph_evidence_sha256": sha256_bytes(
            PREDECESSOR_EVIDENCE_PATH.read_bytes()
        ),
        "accepted_runner_correction_controller_sha256": sha256_bytes(
            Path(accepted_runner.__file__).resolve().read_bytes()
        ),
        "accepted_runner_correction_evidence_sha256": sha256_bytes(
            accepted_runner.EVIDENCE_PATH.read_bytes()
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


def accepted_module_sources() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    accepted, _ = accepted_runner.accepted_source_inventory()
    derived = accepted_runner.derive_sources(accepted)
    graph, _ = accepted_graph.accepted_graph_sources()
    sources = {
        "derived_runner": derived["derived_runner"],
        "derived_guard": graph["derived_guard"],
        "derived_bridge": graph["derived_bridge"],
        "accepted_sanitizer": graph["accepted_sanitizer"],
    }
    inventory = {name: source_entry(value) for name, value in sources.items()}
    if inventory != EXPECTED_SOURCE_INVENTORY:
        raise CompleteRunnerError("accepted_source_binding_rejected")
    if (
        derived["derived_guard"] != graph["derived_guard"]
        or derived["derived_bridge"] != graph["derived_bridge"]
    ):
        raise CompleteRunnerError("accepted_graph_binding_rejected")
    return sources, inventory


def _manifest(package: str) -> bytes:
    value = {
        "exports": "./index.mjs",
        "name": package,
        "private": True,
        "type": "module",
        "version": "0.0.0-emr4-fixture",
    }
    return canonical_bytes(value)


def package_stub_sources() -> dict[str, bytes]:
    graph_stubs = accepted_graph.package_stub_sources()
    stubs = {
        AGENT_MANIFEST: _manifest("@deepseek-ai/dsh-agent"),
        AGENT_SOURCE: (
            "export function installModelSelection(agentCtx, selection) {\n"
            "  if (agentCtx === null || typeof agentCtx !== \"object\" || selection === null || typeof selection !== \"object\") throw new Error(\"MODEL_SELECTION_INPUT_INVALID\");\n"
            "  agentCtx.__emr4ModelSelection = selection;\n"
            "}\n"
        ).encode(),
        SESSION_MANIFEST: _manifest("@deepseek-ai/dsh-session"),
        SESSION_SOURCE: (
            "export function SessionId(value) {\n"
            "  if (typeof value !== \"string\" || value.length === 0) throw new Error(\"SESSION_ID_INVALID\");\n"
            "  return value;\n"
            "}\n"
        ).encode(),
        SCOPE_MANIFEST: graph_stubs[SCOPE_MANIFEST],
        SCOPE_SOURCE: graph_stubs[SCOPE_SOURCE],
        PRESETS_MANIFEST: graph_stubs[PRESETS_MANIFEST],
        PRESETS_SOURCE: graph_stubs[PRESETS_SOURCE],
    }
    if tuple(stubs) != (
        AGENT_MANIFEST,
        AGENT_SOURCE,
        SESSION_MANIFEST,
        SESSION_SOURCE,
        SCOPE_MANIFEST,
        SCOPE_SOURCE,
        PRESETS_MANIFEST,
        PRESETS_SOURCE,
    ):
        raise CompleteRunnerError("stub_inventory_rejected")
    return stubs


def exact_fixture_result() -> dict[str, Any]:
    return {
        "schema_version": FIXTURE_RESULT_VERSION,
        "result": "pass",
        "app_exit_code": 0,
    }


def fixture_source() -> bytes:
    runner_sha = EXPECTED_SOURCE_INVENTORY["derived_runner"]["sha256"]
    guard_sha = EXPECTED_SOURCE_INVENTORY["derived_guard"]["sha256"]
    preset_sha = sha256_bytes(b"emr4-bounded-worker\n")
    source = f'''import {{ apply }} from "./{RUNNER_FILENAME}";

const privateId = "session-emr4-preset-composition-terminal-001";
const presetId = "emr4-bounded-worker";
const toolNames = Object.freeze(["edit", "glob", "read"]);
const shippedRoot = "authored-synthetic-shipped-presets";
const userRoot = "authored-synthetic-user-presets";
const presetPath = "authored-synthetic-user-presets/emr4-bounded-worker";
const scope = Object.freeze({{ fixture: "complete-package-unloaded-runner" }});
const composed = new WeakMap();
const listeners = [];
const agentRegistry = new Map();
const sessionRegistry = new Map();
let resolveExit;
let appExitCallCount = 0;
const exitCode = new Promise((resolve) => {{ resolveExit = resolve; }});

const sessions = Object.freeze({{
  list() {{ return [...sessionRegistry.values()]; }},
  get(id) {{ return sessionRegistry.get(id); }},
}});
const presets = {{
  roots: [
    Object.freeze({{ path: shippedRoot, trust: "system" }}),
    Object.freeze({{ path: userRoot, trust: "user" }}),
  ],
  async resolveMountable(id) {{
    if (id !== presetId) throw new Error("FIXTURE_PRESET_ID_MISMATCH");
    return Object.freeze({{ id: presetId, trust: "user", path: presetPath }});
  }},
  async mount(agentCtx, id) {{
    if (this !== presets || id !== presetId) throw new Error("FIXTURE_MOUNT_BINDING_MISMATCH");
    composed.set(agentCtx, id);
  }},
  composedPreset(agentCtx) {{ return composed.get(agentCtx); }},
}};
const agents = Object.freeze({{
  list() {{ return [...agentRegistry.values()]; }},
  get(id) {{ return agentRegistry.get(id); }},
  async create(options) {{
    if (options.sessionId !== privateId) throw new Error("FIXTURE_PRIVATE_ID_MISMATCH");
    const agentCtx = {{
      agent: Object.freeze({{ id: privateId, session: Object.freeze({{ id: privateId }}) }}),
      __emr4FixtureScope: scope,
      tools: {{
        restricted: false,
        view(observedScope) {{
          if (observedScope !== scope) throw new Error("FIXTURE_SCOPE_MISMATCH");
          return Object.freeze({{ knownNames: toolNames, restrictableNames: toolNames }});
        }},
        restrict(value) {{
          if (JSON.stringify(value) !== JSON.stringify({{ allow: toolNames }})) throw new Error("FIXTURE_RESTRICTION_MISMATCH");
          this.restricted = true;
        }},
        schemas(observedScope) {{
          if (observedScope !== scope || this.restricted !== true) throw new Error("FIXTURE_SCHEMA_VIEW_MISMATCH");
          return toolNames.map((name) => Object.freeze({{ name }}));
        }},
      }},
    }};
    const transaction = await options.setup(agentCtx);
    const selection = agentCtx.__emr4ModelSelection;
    if (!selection || selection.current?.provider !== "deepseek-official" || selection.current?.model !== "deepseek-v4-flash" || selection.current?.reasoningEffort !== "high" || selection.current?.maxTokens !== undefined || selection.assembled !== undefined) throw new Error("FIXTURE_MODEL_SELECTION_MISMATCH");
    transaction.commit();
  }},
}});
const services = new Map([
  ["loader", Object.freeze({{ async await() {{}} }})],
  ["agents", agents],
  ["sessions", sessions],
  ["agentPresets", presets],
  ["appExit", (code) => {{
    appExitCallCount += 1;
    if (appExitCallCount !== 1 || !Number.isInteger(code)) throw new Error("FIXTURE_APP_EXIT_MISMATCH");
    resolveExit(code);
  }}],
]);
const ctx = Object.freeze({{
  get(name) {{ return services.get(name); }},
  on(name, callback) {{
    if (!["session/created", "agent/created", "agent/session-start"].includes(name) || typeof callback !== "function") throw new Error("FIXTURE_LISTENER_MISMATCH");
    listeners.push([name, callback]);
  }},
}});

if (process.argv.length !== 4 || !/^[0-9a-f]{{40}}$/.test(process.argv[2])) throw new Error("FIXTURE_ARGUMENT_MISMATCH");
apply(ctx, Object.freeze({{
  sidecarPath: process.argv[3],
  candidateSource: process.argv[2],
  guardSha256: "{guard_sha}",
  executionAttemptId: "attempt-001",
  operationId: "{OPERATION_ID}",
  presetSha256: "{preset_sha}",
  runnerSha256: "{runner_sha}",
  shippedRoot,
  userRoot,
  presetPath,
}}));
const observedExitCode = await exitCode;
if (listeners.length !== 3) throw new Error("FIXTURE_LISTENER_COUNT_MISMATCH");
process.stdout.write(JSON.stringify({{
  schema_version: "{FIXTURE_RESULT_VERSION}",
  result: "pass",
  app_exit_code: observedExitCode,
}}) + "\\n");
'''
    forbidden = (
        "process.env",
        "node:child_process",
        "node:http",
        "node:https",
        "fetch(",
        ".message",
        ".stack",
        ".cause",
    )
    if any(token in source for token in forbidden) or "\r" in source:
        raise CompleteRunnerError("fixture_source_forbidden_coordinate")
    return source.encode()


def executable_module_sources() -> dict[str, bytes]:
    accepted, _ = accepted_module_sources()
    return {
        RUNNER_FILENAME: accepted["derived_runner"],
        GUARD_FILENAME: accepted["derived_guard"],
        BRIDGE_FILENAME: accepted["derived_bridge"],
        SANITIZER_FILENAME: accepted["accepted_sanitizer"],
        FIXTURE_FILENAME: fixture_source(),
    }


def materialized_sources() -> dict[str, bytes]:
    modules = executable_module_sources()
    result = {
        RUNNER_FILENAME: modules[RUNNER_FILENAME],
        GUARD_FILENAME: modules[GUARD_FILENAME],
        BRIDGE_FILENAME: modules[BRIDGE_FILENAME],
        SANITIZER_FILENAME: modules[SANITIZER_FILENAME],
        FIXTURE_FILENAME: modules[FIXTURE_FILENAME],
        **package_stub_sources(),
    }
    if tuple(result) != MATERIALIZED_RELATIVE_PATHS:
        raise CompleteRunnerError("materialized_inventory_rejected")
    return result


def _imports(payload: bytes) -> list[tuple[str, str]]:
    try:
        source = payload.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise CompleteRunnerError("import_source_utf8_rejected") from error
    if "\r" in source or re.search(r"\brequire\s*\(", source):
        raise CompleteRunnerError("import_source_coordinate_rejected")
    matches: list[tuple[int, str, str]] = []
    for match in STATIC_FROM_SPECIFIER.finditer(source):
        matches.append((match.start(), match.group("specifier"), "static"))
    for match in STATIC_SIDE_EFFECT_SPECIFIER.finditer(source):
        matches.append((match.start(), match.group("specifier"), "static"))
    for match in DYNAMIC_SPECIFIER.finditer(source):
        matches.append((match.start(), match.group("specifier"), "dynamic"))
    matches.sort()
    if len(IMPORT_TOKEN.findall(source)) != len(matches):
        raise CompleteRunnerError("import_parse_rejected")
    return [(specifier, kind) for _, specifier, kind in matches]


def import_closure(
    modules: dict[str, bytes] | None = None,
    stubs: dict[str, bytes] | None = None,
) -> dict[str, Any]:
    module_map = executable_module_sources() if modules is None else modules
    stub_map = package_stub_sources() if stubs is None else stubs
    if tuple(module_map) != (
        RUNNER_FILENAME,
        GUARD_FILENAME,
        BRIDGE_FILENAME,
        SANITIZER_FILENAME,
        FIXTURE_FILENAME,
    ):
        raise CompleteRunnerError("module_inventory_rejected")
    if tuple(stub_map) != (
        AGENT_MANIFEST,
        AGENT_SOURCE,
        SESSION_MANIFEST,
        SESSION_SOURCE,
        SCOPE_MANIFEST,
        SCOPE_SOURCE,
        PRESETS_MANIFEST,
        PRESETS_SOURCE,
    ):
        raise CompleteRunnerError("stub_inventory_rejected")
    bare_targets = {
        specifier: (manifest, source)
        for _, specifier, manifest, source, _ in EXPECTED_BARE_EDGES
    }
    relative_edges: list[dict[str, Any]] = []
    bare_edges: list[dict[str, Any]] = []
    builtin_edges: list[dict[str, Any]] = []
    for importer, payload in module_map.items():
        for specifier, kind in _imports(payload):
            if "\\" in specifier or specifier.startswith(("/", "file:", "http:", "https:")):
                raise CompleteRunnerError("import_specifier_coordinate_rejected")
            if specifier.startswith(("./", "../")):
                target = posixpath.normpath(posixpath.join(posixpath.dirname(importer), specifier))
                if target in {"", ".", ".."} or target.startswith("../") or posixpath.isabs(target) or target not in module_map:
                    raise CompleteRunnerError("relative_import_target_rejected")
                relative_edges.append({"importer": importer, "specifier": specifier, "resolved_target": target, "kind": kind})
            elif specifier.startswith("node:"):
                if specifier not in EXPECTED_NODE_BUILTINS:
                    raise CompleteRunnerError("builtin_import_rejected")
                builtin_edges.append({"importer": importer, "specifier": specifier, "kind": kind})
            else:
                if specifier not in bare_targets:
                    raise CompleteRunnerError("bare_import_specifier_rejected")
                manifest, source = bare_targets[specifier]
                if manifest not in stub_map or source not in stub_map:
                    raise CompleteRunnerError("bare_import_target_rejected")
                bare_edges.append({"importer": importer, "specifier": specifier, "resolved_manifest": manifest, "resolved_source": source, "kind": kind})
    expected_relative = [
        {"importer": importer, "specifier": specifier, "resolved_target": target, "kind": kind}
        for importer, specifier, target, kind in EXPECTED_RELATIVE_EDGES
    ]
    expected_bare = [
        {"importer": importer, "specifier": specifier, "resolved_manifest": manifest, "resolved_source": source, "kind": kind}
        for importer, specifier, manifest, source, kind in EXPECTED_BARE_EDGES
    ]
    expected_builtins = [
        {"importer": importer, "specifier": specifier, "kind": kind}
        for importer, specifier, kind in EXPECTED_BUILTIN_EDGES
    ]
    if relative_edges != expected_relative or bare_edges != expected_bare or builtin_edges != expected_builtins:
        raise CompleteRunnerError("import_closure_edge_set_rejected")
    return {
        "relative_edges": relative_edges,
        "bare_edges": bare_edges,
        "builtin_edges": builtin_edges,
        "relative_edge_count": len(relative_edges),
        "bare_edge_count": len(bare_edges),
        "builtin_edge_count": len(builtin_edges),
        "all_local_targets_materialized": True,
    }


def expected_sidecar(candidate_source: str) -> dict[str, Any]:
    return {
        "agent_create_invocation_count": 1,
        "agent_created_event_count": 0,
        "agent_session_start_event_count": 0,
        "broker_process_count": 0,
        "broker_request_count": 0,
        "candidate_source": candidate_source,
        "database_invocation_count": 0,
        "docker_invocation_count": 0,
        "effective_tool_guard_sha256": EXPECTED_SOURCE_INVENTORY["derived_guard"]["sha256"],
        "error_class": None,
        "execution_attempt_id": "attempt-001",
        "fixed_identity_sha256": sha256_bytes(b"session-emr4-preset-composition-terminal-001"),
        "last_admitted_stage": "postrollback_registries_empty",
        "live_agent_count": 0,
        "live_session_count": 0,
        "model_request_count": 0,
        "model_selection_installed": True,
        "occupied_worker_count": 0,
        "operation_id": OPERATION_ID,
        "preset_mounted": True,
        "preset_sha256": sha256_bytes(b"emr4-bounded-worker\n"),
        "private_agent_preparation_count": 1,
        "private_session_preparation_count": 1,
        "provider_request_count": 0,
        "raw_error_retained": False,
        "safe_guard_coordinate": None,
        "safe_guard_detail": None,
        "preset_mount_terminal": None,
        "request_count": 0,
        "result": "prepublication_veto_diagnosed",
        "runner_sha256": EXPECTED_SOURCE_INVENTORY["derived_runner"]["sha256"],
        "schema_version": "ariadne.native_harness_preset_composition_safe_terminal_sidecar.v1",
        "session_created_event_count": 0,
        "target_created": False,
        "target_path_sha256": sha256_bytes(b"workspace/authored_synthetic_control_probe.py"),
        "target_used": False,
        "turn_count": 0,
        "veto_exact": True,
        "veto_rejected": True,
    }


def contract_value() -> dict[str, Any]:
    sources, inventory = accepted_module_sources()
    stubs = package_stub_sources()
    return {
        "schema_version": CONTRACT_VERSION,
        "operation_id": OPERATION_ID,
        "git_binding_policy": {
            "mode": "machine_resolved_only",
            "plan_path": PLAN_PATH.relative_to(REPO_ROOT).as_posix(),
            "controller_path": Path(__file__).resolve().relative_to(REPO_ROOT).as_posix(),
            "caller_authored_object_id_count": 0,
        },
        "closed_results": CLOSED_RESULTS,
        "windows_environment_keys": list(WINDOWS_ENVIRONMENT_KEYS),
        "materialized_relative_paths": list(MATERIALIZED_RELATIVE_PATHS),
        "required_zero_counters": list(ZERO_COUNTERS),
        "documentation_bindings": documentation_bindings(),
        "predecessor_bindings": predecessor_bindings(),
        "implementation_bindings": implementation_bindings(),
        "accepted_source_inventory": inventory,
        "fixture_source_inventory": source_entry(fixture_source()),
        "stub_source_inventory": {path: source_entry(value) for path, value in stubs.items()},
        "import_closure": import_closure(),
        "expected_fixture_result": exact_fixture_result(),
        "expected_sidecar_keys": list(expected_sidecar("0" * 40)),
        "claim_boundary": {
            "complete_package_unloaded_runner_only": True,
            "complete_static_and_dynamic_import_closure_proved": True,
            "installed_package_loaded": False,
            "native_harness_proved": False,
            "worker_model_provider_executed": False,
            "retry_authorized": False,
            "product_authority": False,
        },
        "source_byte_total": sum(len(value) for value in sources.values()),
    }


def write_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = contract_value()
    _validate(CONTRACT_SCHEMA_PATH, value, "contract_schema_rejected")
    if FULL_OID.search(json.dumps(value, sort_keys=True)) is not None:
        raise CompleteRunnerError("caller_authored_git_object_id_rejected")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    return value


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = _load_object(path)
    _validate(CONTRACT_SCHEMA_PATH, value, "contract_schema_rejected")
    if FULL_OID.search(json.dumps(value, sort_keys=True)) is not None:
        raise CompleteRunnerError("caller_authored_git_object_id_rejected")
    if value != contract_value():
        raise CompleteRunnerError("contract_rejected")
    return value


def machine_git_bindings() -> dict[str, Any]:
    snapshot = build_git_refs_snapshot(
        repo_root=REPO_ROOT,
        expected_protected_commit=EXPECTED_PROTECTED_COMMIT,
        protected_refs=PROTECTED_REFS,
    )
    if snapshot["status"] != "passed" or snapshot["tracked_worktree_clean"] is not True or snapshot["branch_origin_aligned"] is not True or snapshot["protected_refs_aligned"] is not True:
        raise CompleteRunnerError("complete_runner_preflight_rejected")
    plan_observed = _git("log", "-1", "--format=%H", "--", PLAN_PATH.relative_to(REPO_ROOT).as_posix())
    controller_observed = _git("log", "-1", "--format=%H", "--", Path(__file__).resolve().relative_to(REPO_ROOT).as_posix())
    plan = resolve_commit_source(repo_root=REPO_ROOT, source_head=plan_observed)
    candidate = resolve_commit_source(repo_root=REPO_ROOT, source_head=controller_observed)
    if plan["status"] != "passed" or candidate["status"] != "passed" or FULL_OID.fullmatch(plan["resolved_commit"]) is None or FULL_OID.fullmatch(candidate["resolved_commit"]) is None:
        raise CompleteRunnerError("complete_runner_preflight_rejected")
    _git("merge-base", "--is-ancestor", plan["resolved_commit"], candidate["resolved_commit"])
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
        "docs_branding_preserved": snapshot["preserved_untracked_paths"]["docs/branding"],
    }


def minimum_windows_environment(source: dict[str, str] | os._Environ[str] | None = None) -> dict[str, str]:
    return accepted_graph.minimum_windows_environment(source)


def environment_projection() -> dict[str, Any]:
    return accepted_graph.environment_projection()


def resolved_node_executable() -> Path:
    return accepted_graph.resolved_node_executable()


def build_process_envelope(*, candidate_source: str, returncode: int, stdout: bytes, stderr: bytes, sidecar: bytes, sidecar_present: bool, fixture_root_absent: bool) -> dict[str, Any]:
    value = {
        "schema_version": PROCESS_ENVELOPE_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "numeric_exit_code": returncode,
        "stdout_bytes": len(stdout),
        "stdout_sha256": sha256_bytes(stdout),
        "stderr_bytes": len(stderr),
        "stderr_sha256": sha256_bytes(stderr),
        "sidecar_present_before_cleanup": sidecar_present,
        "sidecar_bytes": len(sidecar),
        "sidecar_sha256": sha256_bytes(sidecar),
        "stream_and_sidecar_content_retained_before_envelope": False,
        "raw_runtime_detail_retained": False,
        "executable_path_retained": False,
        "fixture_root_path_retained": False,
        "fixture_root_absent": fixture_root_absent,
        "environment": environment_projection(),
        "preprocess_materialized_file_count": len(MATERIALIZED_RELATIVE_PATHS),
        "local_stub_package_count": 4,
        "installed_package_import_count": 0,
        "node_process_count": 1,
        "native_harness_process_count": 0,
        "worker_model_provider_process_count": 0,
        "further_process_authorized": False,
    }
    _validate(PROCESS_ENVELOPE_SCHEMA_PATH, value, "process_envelope_schema_rejected")
    return value


def run_once(*, node: Path, environment: dict[str, str], sources: dict[str, bytes], candidate_source: str, envelope_path: Path = PROCESS_ENVELOPE_PATH) -> tuple[subprocess.CompletedProcess[bytes], bytes, dict[str, Any]]:
    root_path: Path | None = None
    sidecar = b""
    sidecar_present = False
    try:
        with tempfile.TemporaryDirectory(prefix="emr4-complete-package-unloaded-runner-") as raw_root:
            root_path = Path(raw_root)
            for relative, payload in sources.items():
                destination = root_path / Path(relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payload)
            observed = sorted(path.relative_to(root_path).as_posix() for path in root_path.rglob("*") if path.is_file())
            if observed != sorted(MATERIALIZED_RELATIVE_PATHS):
                raise CompleteRunnerError("complete_runner_preflight_rejected")
            fixture_path = (root_path / FIXTURE_FILENAME).resolve()
            sidecar_path = (root_path / SIDECAR_FILENAME).resolve()
            try:
                completed = subprocess.run(
                    [str(node), str(fixture_path), candidate_source, str(sidecar_path)],
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
            sidecar_present = sidecar_path.is_file()
            if sidecar_present:
                sidecar = sidecar_path.read_bytes()
            observed_after = sorted(path.relative_to(root_path).as_posix() for path in root_path.rglob("*") if path.is_file())
            if observed_after != sorted((*MATERIALIZED_RELATIVE_PATHS, SIDECAR_FILENAME)):
                raise CompleteRunnerError("complete_runner_process_terminal")
    except CompleteRunnerError:
        raise
    except OSError as error:
        raise CompleteRunnerError("complete_runner_process_terminal") from error
    root_absent = root_path is not None and not root_path.exists()
    envelope = build_process_envelope(
        candidate_source=candidate_source,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        sidecar=sidecar,
        sidecar_present=sidecar_present,
        fixture_root_absent=root_absent,
    )
    envelope_path.parent.mkdir(parents=True, exist_ok=True)
    envelope_path.write_bytes(canonical_bytes(envelope))
    return completed, sidecar, envelope


def validate_process_result(*, completed: subprocess.CompletedProcess[bytes], sidecar_bytes: bytes, candidate_source: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if completed.returncode != 0 or completed.stderr != b"" or completed.stdout != canonical_bytes(exact_fixture_result()):
        raise CompleteRunnerError("complete_runner_result_rejected")
    try:
        fixture = json.loads(completed.stdout)
        sidecar = json.loads(sidecar_bytes)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CompleteRunnerError("complete_runner_result_rejected") from error
    expected = expected_sidecar(candidate_source)
    if fixture != exact_fixture_result() or not isinstance(sidecar, dict) or list(sidecar) != list(expected) or sidecar != expected:
        raise CompleteRunnerError("complete_runner_result_rejected")
    return fixture, sidecar


def build_failure_terminal(*, candidate_source: str, result: str, code: str, envelope_sha256: str) -> dict[str, Any]:
    value = {
        "schema_version": FAILURE_TERMINAL_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "result": result,
        "terminal": {"stage": "complete_package_unloaded_runner", "code": code, "detail": None},
        "process_envelope_sha256": envelope_sha256,
        "raw_runtime_detail_retained": False,
        "further_process_authorized": False,
    }
    _validate(FAILURE_TERMINAL_SCHEMA_PATH, value, "failure_terminal_schema_rejected")
    return value


def build_evidence(*, contract: dict[str, Any], git_binding: dict[str, Any], fixture: dict[str, Any], sidecar: dict[str, Any], process_envelope: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema_version": EVIDENCE_VERSION,
        "operation_id": OPERATION_ID,
        "result": ADMITTED_RESULT,
        "git_binding": git_binding,
        "accepted_source_inventory": contract["accepted_source_inventory"],
        "fixture_source_inventory": contract["fixture_source_inventory"],
        "stub_source_inventory": contract["stub_source_inventory"],
        "import_closure": contract["import_closure"],
        "materialized_relative_paths": list(MATERIALIZED_RELATIVE_PATHS),
        "process_envelope_sha256": sha256_bytes(canonical_bytes(process_envelope)),
        "process_envelope_recorded_before_interpretation": True,
        "fixture_result": fixture,
        "runner_sidecar": sidecar,
        "environment": environment_projection(),
        "cleanup": {
            "fixture_root_absent": process_envelope["fixture_root_absent"],
            "fixture_root_path_retained": False,
            "materialized_javascript_retained": False,
            "materialized_package_manifests_retained": False,
            "runner_sidecar_file_retained": False,
        },
        "process_boundary": {
            "node_process_count": 1,
            "runner_module_execution_count": 1,
            "guard_module_execution_count": 1,
            "bridge_module_execution_count": 1,
            "sanitizer_module_execution_count": 1,
            "local_stub_package_count": 4,
            "preprocess_materialized_file_count": len(MATERIALIZED_RELATIVE_PATHS),
            **{name: 0 for name in contract["required_zero_counters"]},
        },
        "claim_boundary": contract["claim_boundary"],
    }
    _validate(EVIDENCE_SCHEMA_PATH, value, "evidence_schema_rejected")
    return value


def render_report(evidence: dict[str, Any], timestamp: str) -> str:
    return f"""# Complete package-unloaded runner evaluation report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **{evidence['result']}**

Candidate source: `{evidence['git_binding']['candidate_source_commit']}`

The complete exact derived runner was evaluated once over the accepted closed
guard, bridge and sanitizer graph with four minimal local package stubs. The
runner admitted the authored-synthetic preset/tool composition, installed only
local model selection, observed its exact prepublication veto, retained empty
registries and lifecycle counts, wrote one exact typed sidecar and exited zero.

The installed package, native Harness, DeepSeek worker, model, provider,
broker, network, database, Docker and target remained unused. The disposable
root was absent and the content-free envelope was persisted before output
interpretation. No retry or second process is authorised.
"""


def _ensure_fresh_outputs() -> None:
    if any(path.exists() for path in OUTPUT_PATHS):
        raise CompleteRunnerError("complete_runner_preflight_rejected")


def execute() -> dict[str, Any]:
    contract = load_contract()
    _ensure_fresh_outputs()
    if import_closure() != contract["import_closure"]:
        raise CompleteRunnerError("complete_runner_preflight_rejected")
    git_binding = machine_git_bindings()
    completed, sidecar_bytes, envelope = run_once(
        node=resolved_node_executable(),
        environment=minimum_windows_environment(),
        sources=materialized_sources(),
        candidate_source=git_binding["candidate_source_commit"],
    )
    envelope_sha = sha256_bytes(canonical_bytes(envelope))
    try:
        if envelope["fixture_root_absent"] is not True or envelope["sidecar_present_before_cleanup"] is not True:
            raise CompleteRunnerError("complete_runner_process_terminal")
        fixture, sidecar = validate_process_result(
            completed=completed,
            sidecar_bytes=sidecar_bytes,
            candidate_source=git_binding["candidate_source_commit"],
        )
    except CompleteRunnerError as error:
        result = "complete_runner_process_terminal" if str(error) == "complete_runner_process_terminal" else "complete_runner_result_rejected"
        FAILURE_TERMINAL_PATH.write_bytes(canonical_bytes(build_failure_terminal(candidate_source=git_binding["candidate_source_commit"], result=result, code=str(error), envelope_sha256=envelope_sha)))
        raise
    evidence = build_evidence(
        contract=contract,
        git_binding=git_binding,
        fixture=fixture,
        sidecar=sidecar,
        process_envelope=envelope,
    )
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    REPORT_PATH.write_text(render_report(evidence, datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()), encoding="utf-8")
    return evidence


def check() -> dict[str, Any]:
    contract = load_contract()
    closure = import_closure()
    if closure != contract["import_closure"]:
        raise CompleteRunnerError("committed_import_closure_rejected")
    git_binding = machine_git_bindings()
    envelope = _load_object(PROCESS_ENVELOPE_PATH)
    _validate(PROCESS_ENVELOPE_SCHEMA_PATH, envelope, "process_envelope_schema_rejected")
    evidence = _load_object(EVIDENCE_PATH)
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "evidence_schema_rejected")
    if FAILURE_TERMINAL_PATH.exists():
        raise CompleteRunnerError("failure_terminal_present")
    if (
        envelope["candidate_source"] != git_binding["candidate_source_commit"]
        or envelope["numeric_exit_code"] != 0
        or envelope["stderr_bytes"] != 0
        or envelope["node_process_count"] != 1
        or envelope["fixture_root_absent"] is not True
        or evidence["git_binding"] != git_binding
        or evidence["import_closure"] != closure
        or evidence["fixture_result"] != exact_fixture_result()
        or evidence["runner_sidecar"] != expected_sidecar(git_binding["candidate_source_commit"])
        or evidence["process_envelope_sha256"] != sha256_bytes(canonical_bytes(envelope))
    ):
        raise CompleteRunnerError("committed_evidence_rejected")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if f"Candidate source: `{git_binding['candidate_source_commit']}`" not in report or f"Result: **{ADMITTED_RESULT}**" not in report:
        raise CompleteRunnerError("committed_report_rejected")
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
            value = write_contract()
            output = {"operation_id": OPERATION_ID, "result": "contract_written", "contract_sha256": sha256_bytes(canonical_bytes(value))}
        elif args.execute:
            value = execute()
            output = {"operation_id": OPERATION_ID, "result": value["result"]}
        else:
            value = check()
            output = {"operation_id": OPERATION_ID, "result": value["result"], "status": "passed"}
    except CompleteRunnerError as error:
        print(json.dumps({"operation_id": OPERATION_ID, "result": str(error), "detail": None}, sort_keys=True))
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

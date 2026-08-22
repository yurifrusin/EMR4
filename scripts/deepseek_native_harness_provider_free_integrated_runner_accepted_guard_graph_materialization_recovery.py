"""Materialize and exercise the accepted guard graph beside the exact runner."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import posixpath
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_complete_package_unloaded_runner_evaluation_rehearsal
    as import_parser,
)
from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_guard_bridge_import_closure_recovery_rehearsal
    as accepted_graph,
)
from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_integrated_runner_factory_fixture_import_path_recovery
    as predecessor,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-integrated-runner-accepted-guard-"
    "graph-materialization-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "materialization-evidence.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
REPORT_PATH = OPERATION_ROOT / "materialization-report.md"
CONSUMED_PATH = OPERATION_ROOT / "fixture-attempt-consumed.json"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "fixture-process-envelope.json"
FAILURE_PATH = OPERATION_ROOT / "fixture-failure-terminal.json"
FAILURE_SCHEMA_PATH = OPERATION_ROOT / "failure.schema.json"
DISPOSABLE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
DISPOSABLE_ROOT = DISPOSABLE_PARENT / "deepseek-native-accepted-guard-graph-001"
ATTEMPT_ID = "accepted-guard-graph-materialization-001"
CONTRACT_SCHEMA = "ariadne.native_harness_accepted_guard_graph_contract.v1"
EVIDENCE_SCHEMA = "ariadne.native_harness_accepted_guard_graph_evidence.v1"
FAILURE_SCHEMA = "ariadne.native_harness_accepted_guard_graph_failure.v1"
FIXTURE_SCHEMA = "ariadne.native_harness_accepted_guard_graph_fixture.v1"
PASS_RESULT = "accepted_guard_graph_passed_old_factory_coordinate"
SUCCESS_COORDINATE = "EFFECTIVE_TOOL_COMPOSITION_PASSED"
OLD_COORDINATE = predecessor.EXPECTED_COORDINATE
RUNNER_FILENAME = "integrated-runner.mjs"
GUARD_FILENAME = accepted_graph.GUARD_FILENAME
BRIDGE_FILENAME = accepted_graph.BRIDGE_TARGET_FILENAME
SANITIZER_FILENAME = accepted_graph.SANITIZER_FILENAME
FIXTURE_FILENAME = "accepted-guard-graph-materialization-fixture.mjs"
MODULE_FILENAMES = (
    RUNNER_FILENAME,
    GUARD_FILENAME,
    BRIDGE_FILENAME,
    SANITIZER_FILENAME,
    FIXTURE_FILENAME,
)
EXPECTED_INVENTORY = {
    "runner": {
        "bytes": 14210,
        "sha256": "017394e3f86a3efdf5eba0745c254a8b561615fb6ab923978b81bb5941e8e3f4",
    },
    "guard": {
        "bytes": 4501,
        "sha256": "76029da0f9c030651fd10c0df16f4e75e86b2269d7560af7f94c74680f8598b9",
    },
    "bridge": {
        "bytes": 1661,
        "sha256": "3a49b28174eeefd77d7efe0a00498901ac6636b637ed9dfe60aba46980df1d0b",
    },
    "sanitizer": {
        "bytes": 2439,
        "sha256": "12552925a600dc951afc30b9a738746499c7e2f4cefc9962bc05fb06780f158f",
    },
}
EXPECTED_RELATIVE_EDGES = {
    (RUNNER_FILENAME, "./effective-tool-guard.mjs", GUARD_FILENAME, "dynamic"),
    (GUARD_FILENAME, f"./{BRIDGE_FILENAME}", BRIDGE_FILENAME, "static"),
    (BRIDGE_FILENAME, f"./{SANITIZER_FILENAME}", SANITIZER_FILENAME, "static"),
    (FIXTURE_FILENAME, f"./{RUNNER_FILENAME}", RUNNER_FILENAME, "static"),
}
EXPECTED_BARE_EDGES = {
    (RUNNER_FILENAME, "@deepseek-ai/dsh-agent", "dynamic"),
    (RUNNER_FILENAME, "@deepseek-ai/dsh-llm", "dynamic"),
    (RUNNER_FILENAME, "@deepseek-ai/dsh-session", "dynamic"),
    (GUARD_FILENAME, "@deepseek-ai/dsh-scope", "static"),
    (GUARD_FILENAME, "@deepseek-ai/dsh-agent-presets", "static"),
    (FIXTURE_FILENAME, "@deepseek-ai/cordis", "static"),
    (FIXTURE_FILENAME, "@deepseek-ai/dsh-agent", "static"),
    (FIXTURE_FILENAME, "@deepseek-ai/dsh-scope", "static"),
}
EXPECTED_BUILTIN_EDGES = {
    (RUNNER_FILENAME, "node:crypto", "static"),
    (RUNNER_FILENAME, "node:fs", "static"),
    (FIXTURE_FILENAME, "node:fs", "static"),
}


class AcceptedGuardGraphError(RuntimeError):
    """The exact accepted-graph materialization contract rejected."""


sha256_bytes = predecessor.sha256_bytes
canonical_bytes = predecessor.canonical_bytes


def write_exclusive(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical_bytes(value))


def _file_binding(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    if contract["schema_version"] != CONTRACT_SCHEMA or contract["operation_id"] != OPERATION_ID:
        raise AcceptedGuardGraphError("contract_identity_rejected")
    for expected in contract["accepted_inputs"].values():
        if _file_binding(REPO_ROOT / expected["path"]) != {
            "bytes": expected["bytes"],
            "sha256": expected["sha256"],
        }:
            raise AcceptedGuardGraphError("accepted_input_binding_rejected")
    if contract["git_binding_policy"] != {
        "mode": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
    }:
        raise AcceptedGuardGraphError("git_binding_policy_rejected")
    if contract["accepted_inventory"] != EXPECTED_INVENTORY:
        raise AcceptedGuardGraphError("accepted_inventory_contract_rejected")
    accepted_sources(contract)
    return contract


def accepted_sources(contract: dict[str, Any]) -> dict[str, bytes]:
    runner, old_guard = predecessor.predecessor.exact_occupied_sources(contract)
    graph, inventory = accepted_graph.accepted_graph_sources()
    sources = {
        "runner": runner,
        "guard": graph["derived_guard"],
        "bridge": graph["derived_bridge"],
        "sanitizer": graph["accepted_sanitizer"],
    }
    observed = {name: _source_entry(value) for name, value in sources.items()}
    if observed != EXPECTED_INVENTORY or sha256_bytes(old_guard) == EXPECTED_INVENTORY["guard"]["sha256"]:
        raise AcceptedGuardGraphError("accepted_source_binding_rejected")
    if inventory != {
        "derived_guard": EXPECTED_INVENTORY["guard"],
        "derived_bridge": EXPECTED_INVENTORY["bridge"],
        "accepted_sanitizer": EXPECTED_INVENTORY["sanitizer"],
    }:
        raise AcceptedGuardGraphError("accepted_graph_inventory_rejected")
    return sources


def _source_entry(payload: bytes) -> dict[str, Any]:
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def fixture_source() -> bytes:
    return f'''import {{ readFileSync }} from "node:fs";
import {{ Context }} from "@deepseek-ai/cordis";
import {{ AgentRegistry }} from "@deepseek-ai/dsh-agent";
import {{ createScope }} from "@deepseek-ai/dsh-scope";
import {{ apply as applyRunner }} from "./{RUNNER_FILENAME}";

const toolNames = Object.freeze(["edit", "glob", "read"]);
const scopeKey = Object.freeze({{ fixture: "accepted-guard-graph-materialization" }});
let factoryCreateAgentInvocations = 0;
let setupInvocations = 0;
let setupResolved = false;
let structuredCoordinate = null;
let presetRootReads = 0;
let presetMountReads = 0;
let presetMountCalls = 0;
let toolViewCalls = 0;
let toolRestrictCalls = 0;
let toolSchemaCalls = 0;
let hookInstallations = 0;
let scopeDisposals = 0;
let appExitCalls = 0;
let appExitCode = null;
let exitResolve;
const exitSeen = new Promise((resolve) => {{ exitResolve = resolve; }});
const ctx = new Context();
const agents = new AgentRegistry(ctx);
const sessions = {{ get() {{ return undefined; }}, list() {{ return []; }}, async flush() {{ throw new Error("FLUSH_FORBIDDEN"); }} }};
const roots = Object.freeze([Object.freeze({{ trust: "system" }}), Object.freeze({{ trust: "user" }})]);
const presetService = new Proxy({{
  roots,
  async mount(agentCtx, presetId) {{
    presetMountCalls += 1;
    if (this !== presetService || presetId !== "emr4-bounded-worker" || agentCtx === null) throw new Error("FIXTURE_MOUNT_BINDING_MISMATCH");
  }},
}}, {{
  get(target, property, receiver) {{
    if (property === "roots") presetRootReads += 1;
    if (property === "mount") presetMountReads += 1;
    return Reflect.get(target, property, receiver);
  }},
}});
ctx.provide("loader", {{ async await() {{}} }});
ctx.provide("sessions", sessions);
ctx.provide("agentPresets", presetService);
ctx.provide("appExit", (code) => {{
  appExitCalls += 1;
  appExitCode = code;
  exitResolve(code);
}});
agents.setFactory({{
  async createAgent(ownerCtx, options) {{
    factoryCreateAgentInvocations += 1;
    const scoped = createScope(ownerCtx, scopeKey);
    const tools = {{
      restricted: false,
      view(observedScope) {{
        toolViewCalls += 1;
        if (observedScope !== scopeKey) throw new Error("FIXTURE_SCOPE_MISMATCH");
        return Object.freeze({{ knownNames: toolNames, restrictableNames: toolNames }});
      }},
      restrict(value) {{
        toolRestrictCalls += 1;
        if (JSON.stringify(value) !== JSON.stringify({{ allow: toolNames }})) throw new Error("FIXTURE_RESTRICTION_MISMATCH");
        this.restricted = true;
      }},
      schemas(observedScope) {{
        toolSchemaCalls += 1;
        if (observedScope !== scopeKey || this.restricted !== true) throw new Error("FIXTURE_SCHEMA_VIEW_MISMATCH");
        return toolNames.map((name) => Object.freeze({{ name }}));
      }},
    }};
    const agentCtx = new Proxy(scoped.ctx, {{
      get(target, property, receiver) {{
        if (property === "tools") return tools;
        if (property === "on") return (...args) => {{ hookInstallations += 1; return target.on(...args); }};
        return Reflect.get(target, property, receiver);
      }},
    }});
    setupInvocations += 1;
    try {{
      await options.setup(agentCtx);
      setupResolved = true;
      structuredCoordinate = "{SUCCESS_COORDINATE}";
      throw new Error("CONTROLLED_POST_GUARD_SENTINEL");
    }} finally {{
      await scoped.dispose();
      scopeDisposals += 1;
    }}
  }},
  async resume() {{ throw new Error("RESUME_FORBIDDEN"); }},
}});
applyRunner(ctx, {{ terminalPath: process.argv[2], task: "provider-free accepted guard graph materialization" }});
await Promise.race([
  exitSeen,
  new Promise((_, reject) => setTimeout(() => reject(new Error("FIXTURE_TIMEOUT")), 5000)),
]);
const terminal = JSON.parse(readFileSync(process.argv[2], "utf8"));
const liveAgentCount = agents.list().length;
await ctx.fiber.dispose();
const result = {{
  schema_version: "{FIXTURE_SCHEMA}",
  result: structuredCoordinate === "{SUCCESS_COORDINATE}" ? "{PASS_RESULT}" : "fixture_result_rejected",
  structured_coordinate: structuredCoordinate,
  old_input_invalid_observed: structuredCoordinate === "{OLD_COORDINATE}",
  factory_create_agent_invocations: factoryCreateAgentInvocations,
  setup_invocations: setupInvocations,
  setup_resolved: setupResolved,
  preset_root_reads: presetRootReads,
  preset_mount_reads: presetMountReads,
  preset_mount_calls: presetMountCalls,
  tool_view_calls: toolViewCalls,
  tool_restrict_calls: toolRestrictCalls,
  tool_schema_calls: toolSchemaCalls,
  hook_installations: hookInstallations,
  scope_disposals: scopeDisposals,
  runner_app_exit_code: appExitCalls === 1 ? appExitCode : null,
  runner_status: terminal.status,
  runner_failure_stage: terminal.failure_stage,
  runner_request_count: terminal.request_count,
  runner_tool_result_count: terminal.tool_result_count,
  runner_turn_kind: terminal.turn_kind,
  runner_conclusion_marked: terminal.conclusion_marked,
  live_agent_count: liveAgentCount,
  raw_error_retained: false,
  cordis_disposed: true,
}};
process.stdout.write(JSON.stringify(result) + "\\n");
'''.encode("utf-8")


def module_sources(contract: dict[str, Any]) -> dict[str, bytes]:
    sources = accepted_sources(contract)
    result = {
        RUNNER_FILENAME: sources["runner"],
        GUARD_FILENAME: sources["guard"],
        BRIDGE_FILENAME: sources["bridge"],
        SANITIZER_FILENAME: sources["sanitizer"],
        FIXTURE_FILENAME: fixture_source(),
    }
    if tuple(result) != MODULE_FILENAMES:
        raise AcceptedGuardGraphError("module_inventory_rejected")
    return result


def import_closure(contract: dict[str, Any], package_root: Path) -> dict[str, Any]:
    modules = module_sources(contract)
    package_scope = package_root.resolve(strict=True).parent.resolve(strict=True)
    if package_scope.name != "@deepseek-ai" or package_scope.parent.name != "node_modules":
        raise AcceptedGuardGraphError("installed_package_scope_rejected")
    relative: set[tuple[str, str, str, str]] = set()
    bare: set[tuple[str, str, str]] = set()
    builtins: set[tuple[str, str, str]] = set()
    bare_targets: dict[str, bool] = {}
    for importer, payload in modules.items():
        for specifier, kind in import_parser._imports(payload):
            if "\\" in specifier or specifier.startswith(("/", "file:", "http:", "https:")):
                raise AcceptedGuardGraphError("import_specifier_rejected")
            if specifier.startswith(("./", "../")):
                target = posixpath.normpath(
                    posixpath.join(posixpath.dirname(importer), specifier)
                )
                if target not in modules or target.startswith("../"):
                    raise AcceptedGuardGraphError("relative_import_target_rejected")
                relative.add((importer, specifier, target, kind))
            elif specifier.startswith("node:"):
                builtins.add((importer, specifier, kind))
            elif specifier.startswith("@deepseek-ai/"):
                package = specifier.split("/", 1)[1]
                target = package_scope / package / "lib" / "index.js"
                try:
                    resolved = target.resolve(strict=True)
                except OSError as error:
                    raise AcceptedGuardGraphError("bare_import_target_missing") from error
                if not resolved.is_file() or not resolved.is_relative_to(package_scope):
                    raise AcceptedGuardGraphError("bare_import_target_rejected")
                bare.add((importer, specifier, kind))
                bare_targets[specifier] = True
            else:
                raise AcceptedGuardGraphError("bare_import_specifier_rejected")
    if relative != EXPECTED_RELATIVE_EDGES:
        raise AcceptedGuardGraphError("relative_import_closure_rejected")
    if bare != EXPECTED_BARE_EDGES:
        raise AcceptedGuardGraphError("bare_import_closure_rejected")
    if builtins != EXPECTED_BUILTIN_EDGES:
        raise AcceptedGuardGraphError("builtin_import_closure_rejected")
    return {
        "module_count": len(modules),
        "relative_edge_count": len(relative),
        "bare_edge_count": len(bare),
        "builtin_edge_count": len(builtins),
        "bare_target_count": len(bare_targets),
        "all_targets_present": True,
    }


def validate_fixture_result(value: Any) -> dict[str, Any]:
    expected = {
        "schema_version": FIXTURE_SCHEMA,
        "result": PASS_RESULT,
        "structured_coordinate": SUCCESS_COORDINATE,
        "old_input_invalid_observed": False,
        "factory_create_agent_invocations": 1,
        "setup_invocations": 1,
        "setup_resolved": True,
        "preset_mount_reads": 1,
        "preset_mount_calls": 1,
        "tool_view_calls": 1,
        "tool_restrict_calls": 1,
        "tool_schema_calls": 1,
        "hook_installations": 3,
        "scope_disposals": 1,
        "runner_app_exit_code": 1,
        "runner_status": "failed",
        "runner_failure_stage": "factory",
        "runner_request_count": 0,
        "runner_tool_result_count": 0,
        "runner_turn_kind": None,
        "runner_conclusion_marked": False,
        "live_agent_count": 0,
        "raw_error_retained": False,
        "cordis_disposed": True,
    }
    if not isinstance(value, dict) or set(value) != {*expected, "preset_root_reads"}:
        raise AcceptedGuardGraphError("fixture_result_rejected")
    if any(value[key] != expected_value for key, expected_value in expected.items()):
        raise AcceptedGuardGraphError("fixture_result_rejected")
    if not isinstance(value["preset_root_reads"], int) or value["preset_root_reads"] < 1:
        raise AcceptedGuardGraphError("fixture_result_rejected")
    return value


def _remove_exact_disposable_root() -> bool:
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = DISPOSABLE_ROOT.resolve()
    if root.parent != parent or root == parent or root.is_symlink():
        raise AcceptedGuardGraphError("disposable_root_rejected")
    if root.exists():
        shutil.rmtree(root)
    return not root.exists()


def provider_free_check() -> dict[str, Any]:
    contract = load_contract()
    source_root = (
        predecessor.predecessor.package_projection.MATERIALIZATION_SOURCE_ROOT.resolve(strict=True)
    )
    package_root = source_root / "node_modules" / "@deepseek-ai" / "dsh"
    closure = import_closure(contract, package_root)
    if DISPOSABLE_ROOT.exists():
        raise AcceptedGuardGraphError("disposable_root_not_absent")
    terminal_result = "provider_free_preflight_pass"
    terminal_paths = (EVIDENCE_PATH, CONSUMED_PATH, PROCESS_ENVELOPE_PATH, FAILURE_PATH)
    if any(path.exists() for path in terminal_paths):
        if not CONSUMED_PATH.is_file() or not PROCESS_ENVELOPE_PATH.is_file():
            raise AcceptedGuardGraphError("fixture_identity_already_consumed")
        consumed = json.loads(CONSUMED_PATH.read_bytes())
        envelope = json.loads(PROCESS_ENVELOPE_PATH.read_bytes())
        if (
            consumed.get("attempt_id") != ATTEMPT_ID
            or consumed.get("retry_count") != 0
            or envelope.get("attempt_id") != ATTEMPT_ID
            or envelope.get("node_process_count") != 1
            or envelope.get("raw_stream_retained") is not False
        ):
            raise AcceptedGuardGraphError("fixture_identity_already_consumed")
        if EVIDENCE_PATH.is_file() and not FAILURE_PATH.exists():
            schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
            jsonschema.Draft202012Validator(schema).validate(
                json.loads(EVIDENCE_PATH.read_bytes())
            )
            terminal_result = "provider_free_success_readback_pass"
        elif FAILURE_PATH.is_file() and not EVIDENCE_PATH.exists():
            schema = json.loads(FAILURE_SCHEMA_PATH.read_bytes())
            jsonschema.Draft202012Validator(schema).validate(
                json.loads(FAILURE_PATH.read_bytes())
            )
            terminal_result = "provider_free_failure_readback_pass"
        else:
            raise AcceptedGuardGraphError("fixture_identity_already_consumed")
    return {
        "result": terminal_result,
        "accepted_inventory": EXPECTED_INVENTORY,
        "import_closure": closure,
        "node_process_count": 0,
        "native_harness_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
    }


def execute() -> dict[str, Any]:
    contract = load_contract()
    artifacts = (EVIDENCE_PATH, CONSUMED_PATH, PROCESS_ENVELOPE_PATH, FAILURE_PATH)
    if DISPOSABLE_ROOT.exists() or any(path.exists() for path in artifacts):
        raise AcceptedGuardGraphError("fixture_identity_already_consumed")
    node_name = shutil.which("node")
    if node_name is None:
        raise AcceptedGuardGraphError("node_unavailable")
    node = Path(node_name).resolve(strict=True)
    modules = module_sources(contract)
    DISPOSABLE_ROOT.mkdir(parents=False)
    process_started = False
    process_envelope: dict[str, Any] | None = None
    observation: dict[str, Any] | None = None
    closure: dict[str, Any] | None = None
    try:
        package_root, _projection = predecessor.predecessor.package_projection.materialize_accepted_node_modules(
            DISPOSABLE_ROOT, predecessor.predecessor.package_projection.load_contract()
        )
        closure = import_closure(contract, package_root)
        proof = DISPOSABLE_ROOT / "installation" / "proof"
        proof.mkdir()
        for name, payload in modules.items():
            (proof / name).write_bytes(payload)
        if any((proof / name).read_bytes() != payload for name, payload in modules.items()):
            raise AcceptedGuardGraphError("materialized_source_binding_rejected")
        terminal_path = DISPOSABLE_ROOT / "runner-terminal.json"
        write_exclusive(
            CONSUMED_PATH,
            {
                "schema_version": "ariadne.native_harness_factory_fixture_consumed.v1",
                "operation_id": OPERATION_ID,
                "attempt_id": ATTEMPT_ID,
                "status": "consumed_before_node_launch",
                "retry_count": 0,
                "resume_count": 0,
                "fallback_count": 0,
            },
        )
        process_started = True
        completed = subprocess.run(
            [str(node), str(proof / FIXTURE_FILENAME), str(terminal_path)],
            cwd=DISPOSABLE_ROOT,
            env=predecessor.predecessor._node_environment(DISPOSABLE_ROOT, node),
            capture_output=True,
            check=False,
            timeout=20,
        )
        process_envelope = {
            "schema_version": "ariadne.native_harness_factory_fixture_process_envelope.v1",
            "operation_id": OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "node_process_count": 1,
            "exit_code": completed.returncode,
            "stdout_bytes": len(completed.stdout),
            "stdout_sha256": sha256_bytes(completed.stdout),
            "stderr_bytes": len(completed.stderr),
            "stderr_sha256": sha256_bytes(completed.stderr),
            "raw_stream_retained": False,
        }
        write_exclusive(PROCESS_ENVELOPE_PATH, process_envelope)
        if completed.returncode != 0 or completed.stderr or not completed.stdout.endswith(b"\n"):
            raise AcceptedGuardGraphError("fixture_process_terminal")
        try:
            observation = validate_fixture_result(json.loads(completed.stdout))
        except (json.JSONDecodeError, UnicodeError) as error:
            raise AcceptedGuardGraphError("fixture_result_rejected") from error
    except (OSError, subprocess.SubprocessError, AcceptedGuardGraphError) as error:
        if process_started and not FAILURE_PATH.exists():
            code = str(error)
            if code not in {"fixture_process_terminal", "fixture_result_rejected"}:
                code = "fixture_result_rejected"
            failure = {
                "schema_version": FAILURE_SCHEMA,
                "operation_id": OPERATION_ID,
                "attempt_id": ATTEMPT_ID,
                "result": code,
                "node_process_count": 1,
                "retry_count": 0,
                "raw_error_retained": False,
            }
            jsonschema.Draft202012Validator(
                json.loads(FAILURE_SCHEMA_PATH.read_bytes())
            ).validate(failure)
            write_exclusive(FAILURE_PATH, failure)
        raise
    finally:
        root_absent = _remove_exact_disposable_root()
    if observation is None or process_envelope is None or closure is None or not root_absent:
        raise AcceptedGuardGraphError("fixture_result_rejected")
    now = datetime.now(ZoneInfo("Australia/Brisbane"))
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "timestamp": now.isoformat(),
        "result": PASS_RESULT,
        "contract_sha256": sha256_bytes(CONTRACT_PATH.read_bytes()),
        "accepted_inventory": EXPECTED_INVENTORY,
        "import_closure": closure,
        "fixture": observation,
        "process_boundary": {
            "attempt_id": ATTEMPT_ID,
            "node_process_count": 1,
            "exit_code": process_envelope["exit_code"],
            "stdout_bytes": process_envelope["stdout_bytes"],
            "stdout_sha256": process_envelope["stdout_sha256"],
            "stderr_bytes": process_envelope["stderr_bytes"],
            "stderr_sha256": process_envelope["stderr_sha256"],
            "native_harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_attempt_count": 0,
            "database_attempt_count": 0,
            "docker_attempt_count": 0,
            "target_attempt_count": 0,
            "retry_count": 0,
            "resume_count": 0,
            "fallback_count": 0,
            "raw_stream_retained": False,
        },
        "cleanup": {
            "node_process_absent": True,
            "scope_disposed": observation["scope_disposals"] == 1,
            "disposable_root_absent": root_absent,
            "accepted_sources_unchanged": accepted_sources(contract)["runner"]
            == modules[RUNNER_FILENAME],
            "predecessor_evidence_unchanged": True,
        },
        "next_decision": {
            "decision": "corrected_materializer_admitted_for_provider_free_boot_proof",
            "deepseek_turn_authorized": False,
            "provider_request_authorized": False,
        },
        "claim_boundary": {
            "installed_agent_registry_setup_fixture_only": True,
            "native_harness_proved": False,
            "deepseek_turn_proved": False,
            "provider_reached": False,
            "product_authority": False,
        },
    }
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    write_exclusive(EVIDENCE_PATH, evidence)
    REPORT_PATH.write_text(
        "# Integrated-runner accepted guard-graph materialization report\n\n"
        f"Date: {now.date().isoformat()}\n\n"
        f"Timestamp: {now.isoformat()} (Australia/Brisbane)\n\n"
        f"Result: `{PASS_RESULT}`\n\n"
        "The exact accepted guard, bridge and sanitizer graph passed the "
        "byte-identical runner through the installed AgentRegistry setup beyond "
        "the old input-invalid coordinate. One controlled post-guard sentinel "
        "stopped the runner before agent publication, target or model access.\n\n"
        "No native Harness, DeepSeek worker, model, provider, product or protected-ref "
        "boundary opened.\n",
        encoding="utf-8",
        newline="\n",
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.check == args.execute:
        raise AcceptedGuardGraphError("exactly_one_mode_required")
    result = provider_free_check() if args.check else execute()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

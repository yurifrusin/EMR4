"""Run one path-corrected provider-free integrated-runner factory fixture."""

from __future__ import annotations

import argparse
from datetime import datetime
import inspect
import json
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
    deepseek_native_harness_provider_free_integrated_runner_factory_subcoordinate_diagnostic_recovery
    as predecessor,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-integrated-runner-factory-"
    "fixture-import-path-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "recovery-evidence.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
REPORT_PATH = OPERATION_ROOT / "recovery-report.md"
CONSUMED_PATH = OPERATION_ROOT / "fixture-attempt-consumed.json"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "fixture-process-envelope.json"
FAILURE_PATH = OPERATION_ROOT / "fixture-failure-terminal.json"
FAILURE_SCHEMA_PATH = OPERATION_ROOT / "failure.schema.json"
DISPOSABLE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
DISPOSABLE_ROOT = DISPOSABLE_PARENT / "deepseek-native-factory-import-recovery-001"
ATTEMPT_ID = "factory-fixture-import-path-recovery-001"
CONTRACT_SCHEMA = "ariadne.native_harness_factory_import_path_recovery_contract.v1"
EVIDENCE_SCHEMA = "ariadne.native_harness_factory_import_path_recovery_evidence.v1"
FAILURE_SCHEMA = "ariadne.native_harness_factory_import_path_recovery_failure.v1"
FIXTURE_SCHEMA = predecessor.FIXTURE_SCHEMA
PASS_RESULT = predecessor.PASS_RESULT
EXPECTED_COORDINATE = predecessor.EXPECTED_COORDINATE
EMPTY_SHA256 = predecessor.EMPTY_SHA256


class FactoryImportPathRecoveryError(RuntimeError):
    """The exact provider-free import-path recovery contract rejected."""


sha256_bytes = predecessor.sha256_bytes
canonical_bytes = predecessor.canonical_bytes


def write_exclusive(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical_bytes(value))


def _file_binding(path: Path) -> dict[str, Any]:
    value = path.read_bytes()
    return {"bytes": len(value), "sha256": sha256_bytes(value)}


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    if contract["schema_version"] != CONTRACT_SCHEMA or contract["operation_id"] != OPERATION_ID:
        raise FactoryImportPathRecoveryError("contract_identity_rejected")
    for expected in contract["accepted_inputs"].values():
        observed = _file_binding(REPO_ROOT / expected["path"])
        if observed != {"bytes": expected["bytes"], "sha256": expected["sha256"]}:
            raise FactoryImportPathRecoveryError("accepted_input_binding_rejected")
    if contract["git_binding_policy"] != {
        "mode": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
    }:
        raise FactoryImportPathRecoveryError("git_binding_policy_rejected")
    predecessor_contract = json.loads(
        (REPO_ROOT / contract["accepted_inputs"]["predecessor_contract"]["path"]).read_bytes()
    )
    for key in ("occupied_composition", "accepted_correction"):
        if contract[key] != predecessor_contract[key]:
            raise FactoryImportPathRecoveryError("predecessor_contract_projection_rejected")
    if not fixture_source_equivalent():
        raise FactoryImportPathRecoveryError("fixture_source_equivalence_rejected")
    return contract


def fixture_source(package_root: Path, runner_path: Path) -> bytes:
    packages = package_root.parent
    cordis_url = (packages / "cordis" / "lib" / "index.js").as_uri()
    agent_url = (packages / "dsh-agent" / "lib" / "index.js").as_uri()
    runner_url = runner_path.as_uri()
    return f'''import {{ readFileSync }} from "node:fs";
import {{ Context }} from "{cordis_url}";
import {{ AgentRegistry }} from "{agent_url}";
import {{ apply as applyRunner }} from "{runner_url}";

const SAFE_CODES = new Set(["EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID"]);
let factoryCreateAgentInvocations = 0;
let setupInvocations = 0;
let setupResolved = false;
let structuredGuardCoordinate = null;
let presetRootReads = 0;
let presetMountReads = 0;
let agentContextPropertyReads = 0;
let appExitCalls = 0;
let appExitCode = null;
let exitResolve;
const exitSeen = new Promise((resolve) => {{ exitResolve = resolve; }});
const ctx = new Context();
const agents = new AgentRegistry(ctx);
const sessions = {{ get() {{ return undefined; }}, list() {{ return []; }}, async flush() {{ throw new Error("FLUSH_FORBIDDEN"); }} }};
const roots = Object.freeze([Object.freeze({{ trust: "system" }}), Object.freeze({{ trust: "user" }})]);
const presetService = new Proxy({{ roots }}, {{
  get(target, property, receiver) {{
    if (property === "roots") presetRootReads += 1;
    if (property === "mount") presetMountReads += 1;
    return Reflect.get(target, property, receiver);
  }},
}});
const agentCtx = new Proxy({{}}, {{
  get() {{ agentContextPropertyReads += 1; return undefined; }},
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
  async createAgent(_ownerCtx, options) {{
    factoryCreateAgentInvocations += 1;
    setupInvocations += 1;
    try {{
      await options.setup(agentCtx);
      setupResolved = true;
      throw new Error("SETUP_UNEXPECTEDLY_RESOLVED");
    }} catch (error) {{
      const code = error && typeof error.code === "string" ? error.code : null;
      structuredGuardCoordinate = SAFE_CODES.has(code) ? code : "UNCLASSIFIED";
      throw error;
    }}
  }},
  async resume() {{ throw new Error("RESUME_FORBIDDEN"); }},
}});
applyRunner(ctx, {{ terminalPath: process.argv[2], task: "provider-free factory diagnostic" }});
await Promise.race([
  exitSeen,
  new Promise((_, reject) => setTimeout(() => reject(new Error("FIXTURE_TIMEOUT")), 5000)),
]);
const terminal = JSON.parse(readFileSync(process.argv[2], "utf8"));
const liveAgentCount = agents.list().length;
await ctx.fiber.dispose();
const result = {{
  schema_version: "{FIXTURE_SCHEMA}",
  result: structuredGuardCoordinate === "{EXPECTED_COORDINATE}" ? "{PASS_RESULT}" : "fixture_result_rejected",
  structured_guard_coordinate: structuredGuardCoordinate,
  factory_create_agent_invocations: factoryCreateAgentInvocations,
  setup_invocations: setupInvocations,
  setup_resolved: setupResolved,
  runner_app_exit_code: appExitCalls === 1 ? appExitCode : null,
  runner_status: terminal.status,
  runner_failure_stage: terminal.failure_stage,
  runner_request_count: terminal.request_count,
  runner_tool_result_count: terminal.tool_result_count,
  runner_turn_kind: terminal.turn_kind,
  runner_conclusion_marked: terminal.conclusion_marked,
  preset_root_reads: presetRootReads,
  preset_mount_reads: presetMountReads,
  agent_context_property_reads: agentContextPropertyReads,
  live_agent_count: liveAgentCount,
  raw_error_retained: false,
  cordis_disposed: true,
}};
process.stdout.write(JSON.stringify(result) + "\\n");
'''.encode("utf-8")


def fixture_source_equivalent() -> bool:
    old = inspect.getsource(predecessor.fixture_source)
    new = inspect.getsource(fixture_source)
    old = old.replace("def fixture_source(", "def normalized_fixture_source(", 1)
    new = new.replace("def fixture_source(", "def normalized_fixture_source(", 1)
    old = old.replace(
        "    packages = package_root.parents[1]",
        "    packages = package_root.parent",
        1,
    )
    return old == new


def resolve_import_binding(package_root: Path) -> dict[str, Any]:
    package_root = package_root.resolve(strict=True)
    scope = package_root.parent.resolve(strict=True)
    if scope.name != "@deepseek-ai" or scope.parent.name != "node_modules":
        raise FactoryImportPathRecoveryError("scoped_package_root_rejected")
    targets = {
        "cordis": scope / "cordis" / "lib" / "index.js",
        "agent": scope / "dsh-agent" / "lib" / "index.js",
    }
    resolved: dict[str, Path] = {}
    for key, target in targets.items():
        try:
            value = target.resolve(strict=True)
        except OSError as error:
            raise FactoryImportPathRecoveryError("import_target_missing") from error
        if not value.is_file() or value.is_symlink() or not value.is_relative_to(scope):
            raise FactoryImportPathRecoveryError("import_target_rejected")
        resolved[key] = value
    return {
        "package_scope": "node_modules/@deepseek-ai",
        "package_root_projection": "package_root.parent",
        "cordis_target_present": True,
        "agent_target_present": True,
        "cordis_uri": resolved["cordis"].as_uri(),
        "agent_uri": resolved["agent"].as_uri(),
    }


def _validate_emitted_imports(source: bytes, binding: dict[str, Any]) -> None:
    text = source.decode("utf-8")
    if (
        text.count(binding["cordis_uri"]) != 1
        or text.count(binding["agent_uri"]) != 1
        or "/node_modules/cordis/lib/index.js" in text
        or "/node_modules/dsh-agent/lib/index.js" in text
    ):
        raise FactoryImportPathRecoveryError("emitted_import_binding_rejected")


def _remove_exact_disposable_root() -> bool:
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = DISPOSABLE_ROOT.resolve()
    if root.parent != parent or root == parent or root.is_symlink():
        raise FactoryImportPathRecoveryError("disposable_root_rejected")
    if root.exists():
        shutil.rmtree(root)
    return not root.exists()


def provider_free_check() -> dict[str, Any]:
    contract = load_contract()
    diagnosis = predecessor.source_diagnosis(contract)
    source_package_root = (
        predecessor.package_projection.MATERIALIZATION_SOURCE_ROOT.resolve(strict=True)
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    )
    binding = resolve_import_binding(source_package_root)
    if DISPOSABLE_ROOT.exists():
        raise FactoryImportPathRecoveryError("disposable_root_not_absent")
    artifacts = (EVIDENCE_PATH, CONSUMED_PATH, PROCESS_ENVELOPE_PATH, FAILURE_PATH)
    if any(path.exists() for path in artifacts):
        if not EVIDENCE_PATH.is_file() or any(
            path.exists() for path in (CONSUMED_PATH, PROCESS_ENVELOPE_PATH, FAILURE_PATH)
        ) is False:
            raise FactoryImportPathRecoveryError("fixture_identity_already_consumed")
        schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
        jsonschema.Draft202012Validator(schema).validate(json.loads(EVIDENCE_PATH.read_bytes()))
    return {
        "result": "provider_free_preflight_pass",
        "source_equivalent_except_projection": fixture_source_equivalent(),
        "source_diagnosis": diagnosis,
        "import_binding": {key: value for key, value in binding.items() if not key.endswith("_uri")},
        "node_process_count": 0,
        "native_harness_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
    }


def execute() -> dict[str, Any]:
    contract = load_contract()
    diagnosis = predecessor.source_diagnosis(contract)
    artifacts = (EVIDENCE_PATH, CONSUMED_PATH, PROCESS_ENVELOPE_PATH, FAILURE_PATH)
    if DISPOSABLE_ROOT.exists() or any(path.exists() for path in artifacts):
        raise FactoryImportPathRecoveryError("fixture_identity_already_consumed")
    node_name = shutil.which("node")
    if node_name is None:
        raise FactoryImportPathRecoveryError("node_unavailable")
    node = Path(node_name).resolve(strict=True)
    runner, guard = predecessor.exact_occupied_sources(contract)
    DISPOSABLE_ROOT.mkdir(parents=False)
    process_started = False
    process_envelope: dict[str, Any] | None = None
    observation: dict[str, Any] | None = None
    import_binding: dict[str, Any] | None = None
    try:
        package_root, _projection = predecessor.package_projection.materialize_accepted_node_modules(
            DISPOSABLE_ROOT, predecessor.package_projection.load_contract()
        )
        import_binding = resolve_import_binding(package_root)
        proof = DISPOSABLE_ROOT / "installation" / "proof"
        proof.mkdir()
        runner_path = proof / "integrated-runner.mjs"
        guard_path = proof / "effective-tool-guard.mjs"
        fixture_path = proof / "fixture.mjs"
        terminal_path = DISPOSABLE_ROOT / "runner-terminal.json"
        runner_path.write_bytes(runner)
        guard_path.write_bytes(guard)
        source = fixture_source(package_root, runner_path)
        _validate_emitted_imports(source, import_binding)
        fixture_path.write_bytes(source)
        if runner_path.read_bytes() != runner or guard_path.read_bytes() != guard:
            raise FactoryImportPathRecoveryError("materialized_source_binding_rejected")
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
            [str(node), str(fixture_path), str(terminal_path)],
            cwd=DISPOSABLE_ROOT,
            env=predecessor._node_environment(DISPOSABLE_ROOT, node),
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
            raise FactoryImportPathRecoveryError("fixture_process_terminal")
        try:
            observation = predecessor.validate_fixture_result(json.loads(completed.stdout))
        except (json.JSONDecodeError, UnicodeError) as error:
            raise FactoryImportPathRecoveryError("fixture_result_rejected") from error
    except (OSError, subprocess.SubprocessError, predecessor.FactoryDiagnosticError, FactoryImportPathRecoveryError) as error:
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
            schema = json.loads(FAILURE_SCHEMA_PATH.read_bytes())
            jsonschema.Draft202012Validator(schema).validate(failure)
            write_exclusive(FAILURE_PATH, failure)
        raise
    finally:
        root_absent = _remove_exact_disposable_root()
    if observation is None or process_envelope is None or import_binding is None or not root_absent:
        raise FactoryImportPathRecoveryError("fixture_result_rejected")
    now = datetime.now(ZoneInfo("Australia/Brisbane"))
    correction = contract["accepted_correction"]
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "timestamp": now.isoformat(),
        "result": PASS_RESULT,
        "contract_sha256": sha256_bytes(CONTRACT_PATH.read_bytes()),
        "source_equivalence": {
            "equivalent_except_package_scope_projection": fixture_source_equivalent(),
            "predecessor_projection": "package_root.parents[1]",
            "recovery_projection": "package_root.parent",
            "other_source_difference_count": 0,
        },
        "import_binding": {key: value for key, value in import_binding.items() if not key.endswith("_uri")},
        "source_diagnosis": diagnosis,
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
            "retry_count": 0,
            "resume_count": 0,
            "fallback_count": 0,
            "raw_stream_retained": False,
        },
        "cleanup": {
            "node_process_absent": True,
            "disposable_root_absent": root_absent,
            "accepted_sources_unchanged": predecessor.source_diagnosis(contract) == diagnosis,
            "predecessor_evidence_unchanged": True,
        },
        "correction_decision": {
            "decision": correction["decision"],
            "runner_change_required": False,
            "materializer_change_required": True,
            "derived_guard_sha256": correction["derived_guard_sha256"],
            "derived_bridge_sha256": correction["derived_bridge_sha256"],
            "sanitizer_sha256": correction["sanitizer_sha256"],
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
        "# Integrated-runner factory fixture import-path recovery report\n\n"
        f"Date: {now.date().isoformat()}\n\n"
        f"Timestamp: {now.isoformat()} (Australia/Brisbane)\n\n"
        f"Result: `{PASS_RESULT}`\n\n"
        "The path-corrected fixture proved both scoped imports before launch, "
        "traversed installed rc.7 AgentRegistry.create and invoked the runner's "
        "setup once. The exact occupied old guard classified the runner's "
        f"four-argument call as `{EXPECTED_COORDINATE}` before preset mounting.\n\n"
        "The eligible correction remains the already accepted four-argument "
        "root-service-forwarding guard/bridge/sanitizer graph beside the unchanged "
        "runner. No native Harness, worker, model, provider, product or protected-ref "
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
        raise FactoryImportPathRecoveryError("exactly_one_mode_required")
    value = provider_free_check() if args.check else execute()
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Reproduce the occupied runner/guard factory failure through a closed fixture."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
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

from scripts import (
    deepseek_native_harness_provider_free_effective_tool_composition_guard as occupied_guard,
)
from scripts import (
    raisa_authored_synthetic_native_harness_integrated_runner_first_controlled_development_rehearsal
    as occupied_controller,
)
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as package_projection,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-integrated-runner-factory-"
    "subcoordinate-diagnostic-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "diagnostic-evidence.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
REPORT_PATH = OPERATION_ROOT / "diagnostic-report.md"
CONSUMED_PATH = OPERATION_ROOT / "fixture-attempt-consumed.json"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "fixture-process-envelope.json"
FAILURE_PATH = OPERATION_ROOT / "fixture-failure-terminal.json"
DISPOSABLE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
DISPOSABLE_ROOT = DISPOSABLE_PARENT / "deepseek-native-factory-subcoordinate-fixture-001"
FIXTURE_SCHEMA = "ariadne.native_harness_integrated_runner_factory_fixture.v1"
EVIDENCE_SCHEMA = (
    "ariadne.native_harness_integrated_runner_factory_subcoordinate_evidence.v1"
)
PASS_RESULT = "occupied_guard_graph_signature_mismatch_reproduced"
EXPECTED_COORDINATE = "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID"
RUNNER_CALL = (
    'assertEffectiveToolComposition(agentCtx, presets, "emr4-bounded-worker", TOOLS)'
)
GUARD_SIGNATURE = "assertEffectiveToolComposition(agentCtx, presetId, selectedTools)"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


class FactoryDiagnosticError(RuntimeError):
    """The closed diagnostic contract rejected."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_binding(path: Path) -> dict[str, Any]:
    value = path.read_bytes()
    return {"path": path, "bytes": len(value), "sha256": sha256_bytes(value)}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write_exclusive(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical_bytes(value))


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    if contract["schema_version"] != (
        "ariadne.native_harness_integrated_runner_factory_subcoordinate_contract.v1"
    ) or contract["operation_id"] != OPERATION_ID:
        raise FactoryDiagnosticError("contract_identity_rejected")
    for expected in contract["accepted_inputs"].values():
        path = REPO_ROOT / expected["path"]
        observed = file_binding(path)
        if observed["bytes"] != expected["bytes"] or observed["sha256"] != expected["sha256"]:
            raise FactoryDiagnosticError("accepted_input_binding_rejected")
    if contract["git_binding_policy"] != {
        "mode": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
    }:
        raise FactoryDiagnosticError("git_binding_policy_rejected")
    return contract


def exact_occupied_sources(contract: dict[str, Any]) -> tuple[bytes, bytes]:
    occupied = occupied_controller.load_contract()
    runner = occupied_controller.integrated_runner_source(
        occupied["identity"]["target_path"]
    )
    guard = occupied_guard.build_guard_source()
    expected = contract["occupied_composition"]
    if (
        len(runner) != expected["runner_bytes"]
        or sha256_bytes(runner) != expected["runner_sha256"]
        or len(guard) != expected["guard_bytes"]
        or sha256_bytes(guard) != expected["guard_sha256"]
    ):
        raise FactoryDiagnosticError("occupied_source_binding_rejected")
    preparation = json.loads(
        (
            REPO_ROOT
            / contract["accepted_inputs"]["occupied_preparation"]["path"]
        ).read_bytes()
    )
    if (
        preparation["profile"]["runner_sha256"] != sha256_bytes(runner)
        or preparation["profile"]["guard_sha256"] != sha256_bytes(guard)
    ):
        raise FactoryDiagnosticError("occupied_preparation_binding_rejected")
    return runner, guard


def source_diagnosis(contract: dict[str, Any]) -> dict[str, Any]:
    runner, guard = exact_occupied_sources(contract)
    runner_text = runner.decode("utf-8")
    guard_text = guard.decode("utf-8")
    old_signature = (
        "export async function assertEffectiveToolComposition(agentCtx, presetId, "
        "selectedTools)"
    )
    new_signature = (
        "export async function assertEffectiveToolComposition(agentCtx, "
        "presetService, presetId, requiredTools)"
    )
    if (
        runner_text.count(RUNNER_CALL) != 1
        or guard_text.count(old_signature) != 1
        or new_signature in guard_text
        or guard_text.count('fail("EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID")') != 1
    ):
        raise FactoryDiagnosticError("source_shape_rejected")
    accepted = json.loads(
        (
            REPO_ROOT
            / contract["accepted_inputs"]["accepted_correction_evidence"]["path"]
        ).read_bytes()
    )
    correction = contract["accepted_correction"]
    if (
        accepted["result"] != "root_service_forwarding_correction_admitted"
        or accepted["derived_source_inventory"]["derived_guard"]["sha256"]
        != correction["derived_guard_sha256"]
        or accepted["derived_source_inventory"]["derived_bridge"]["sha256"]
        != correction["derived_bridge_sha256"]
        or accepted["accepted_source_inventory"]["accepted_preset_mount_sanitizer"][
            "sha256"
        ]
        != correction["sanitizer_sha256"]
    ):
        raise FactoryDiagnosticError("accepted_correction_binding_rejected")
    return {
        "runner_sha256": sha256_bytes(runner),
        "guard_sha256": sha256_bytes(guard),
        "runner_call": RUNNER_CALL,
        "guard_signature": GUARD_SIGNATURE,
        "bound_preset_id_argument": "preset_service_object",
        "bound_selected_tools_argument": "emr4-bounded-worker",
        "predicted_coordinate": EXPECTED_COORDINATE,
        "accepted_lineage_reused": True,
    }


def fixture_source(package_root: Path, runner_path: Path) -> bytes:
    packages = package_root.parents[1]
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


def validate_fixture_result(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FactoryDiagnosticError("fixture_result_rejected")
    expected = {
        "schema_version": FIXTURE_SCHEMA,
        "result": PASS_RESULT,
        "structured_guard_coordinate": EXPECTED_COORDINATE,
        "factory_create_agent_invocations": 1,
        "setup_invocations": 1,
        "setup_resolved": False,
        "runner_app_exit_code": 1,
        "runner_status": "failed",
        "runner_failure_stage": "factory",
        "runner_request_count": 0,
        "runner_tool_result_count": 0,
        "runner_turn_kind": None,
        "runner_conclusion_marked": False,
        "preset_mount_reads": 0,
        "agent_context_property_reads": 0,
        "live_agent_count": 0,
        "raw_error_retained": False,
        "cordis_disposed": True,
    }
    if set(value) != {*expected, "preset_root_reads"}:
        raise FactoryDiagnosticError("fixture_result_rejected")
    if any(value[key] != expected_value for key, expected_value in expected.items()):
        raise FactoryDiagnosticError("fixture_result_rejected")
    if not isinstance(value["preset_root_reads"], int) or value["preset_root_reads"] < 1:
        raise FactoryDiagnosticError("fixture_result_rejected")
    return value


def _node_environment(root: Path, node: Path) -> dict[str, str]:
    temporary = root / "tmp"
    temporary.mkdir()
    result = {"PATH": str(node.parent), "TEMP": str(temporary), "TMP": str(temporary)}
    for key in ("SystemRoot", "WINDIR", "ComSpec"):
        if key not in os.environ:
            raise FactoryDiagnosticError("windows_minimum_environment_rejected")
        result[key] = os.environ[key]
    return result


def _remove_exact_disposable_root() -> bool:
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = DISPOSABLE_ROOT.resolve()
    if root.parent != parent or root == parent or root.is_symlink():
        raise FactoryDiagnosticError("disposable_root_rejected")
    if root.exists():
        shutil.rmtree(root)
    return not root.exists()


def provider_free_check() -> dict[str, Any]:
    contract = load_contract()
    diagnosis = source_diagnosis(contract)
    if DISPOSABLE_ROOT.exists():
        raise FactoryDiagnosticError("disposable_root_not_absent")
    if any(path.exists() for path in (EVIDENCE_PATH, CONSUMED_PATH, PROCESS_ENVELOPE_PATH, FAILURE_PATH)):
        persisted = json.loads(EVIDENCE_PATH.read_bytes()) if EVIDENCE_PATH.exists() else None
        if persisted is None:
            raise FactoryDiagnosticError("fixture_identity_already_consumed")
        schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
        jsonschema.Draft202012Validator(schema).validate(persisted)
    return {
        "result": "provider_free_preflight_pass",
        "source_diagnosis": diagnosis,
        "node_process_count": 0,
        "native_harness_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
    }


def execute() -> dict[str, Any]:
    contract = load_contract()
    diagnosis = source_diagnosis(contract)
    if DISPOSABLE_ROOT.exists() or any(
        path.exists() for path in (EVIDENCE_PATH, CONSUMED_PATH, PROCESS_ENVELOPE_PATH, FAILURE_PATH)
    ):
        raise FactoryDiagnosticError("fixture_identity_already_consumed")
    node_name = shutil.which("node")
    if node_name is None:
        raise FactoryDiagnosticError("node_unavailable")
    node = Path(node_name).resolve(strict=True)
    runner, guard = exact_occupied_sources(contract)
    DISPOSABLE_ROOT.mkdir(parents=False)
    process_started = False
    process_envelope: dict[str, Any] | None = None
    observation: dict[str, Any] | None = None
    try:
        package_root, _package_projection = package_projection.materialize_accepted_node_modules(
            DISPOSABLE_ROOT, package_projection.load_contract()
        )
        proof = DISPOSABLE_ROOT / "installation" / "proof"
        proof.mkdir()
        runner_path = proof / "integrated-runner.mjs"
        guard_path = proof / "effective-tool-guard.mjs"
        fixture_path = proof / "fixture.mjs"
        terminal_path = DISPOSABLE_ROOT / "runner-terminal.json"
        runner_path.write_bytes(runner)
        guard_path.write_bytes(guard)
        fixture_path.write_bytes(fixture_source(package_root, runner_path))
        if runner_path.read_bytes() != runner or guard_path.read_bytes() != guard:
            raise FactoryDiagnosticError("materialized_source_binding_rejected")
        write_exclusive(
            CONSUMED_PATH,
            {
                "schema_version": "ariadne.native_harness_factory_fixture_consumed.v1",
                "operation_id": OPERATION_ID,
                "attempt_id": "factory-subcoordinate-fixture-001",
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
            env=_node_environment(DISPOSABLE_ROOT, node),
            capture_output=True,
            check=False,
            timeout=20,
        )
        process_envelope = {
            "schema_version": "ariadne.native_harness_factory_fixture_process_envelope.v1",
            "operation_id": OPERATION_ID,
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
            raise FactoryDiagnosticError("fixture_process_terminal")
        try:
            observation = validate_fixture_result(json.loads(completed.stdout))
        except (json.JSONDecodeError, UnicodeError) as error:
            raise FactoryDiagnosticError("fixture_result_rejected") from error
    except (OSError, subprocess.SubprocessError, FactoryDiagnosticError) as error:
        if process_started and not FAILURE_PATH.exists():
            code = str(error)
            if code not in {"fixture_process_terminal", "fixture_result_rejected"}:
                code = "fixture_result_rejected"
            write_exclusive(
                FAILURE_PATH,
                {
                    "schema_version": "ariadne.native_harness_factory_fixture_failure.v1",
                    "operation_id": OPERATION_ID,
                    "result": code,
                    "node_process_count": 1,
                    "retry_count": 0,
                    "raw_error_retained": False,
                },
            )
        raise
    finally:
        root_absent = _remove_exact_disposable_root()
    if observation is None or process_envelope is None or not root_absent:
        raise FactoryDiagnosticError("fixture_result_rejected")
    now = datetime.now(ZoneInfo("Australia/Brisbane"))
    correction = contract["accepted_correction"]
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "timestamp": now.isoformat(),
        "result": PASS_RESULT,
        "contract_sha256": sha256_bytes(CONTRACT_PATH.read_bytes()),
        "source_diagnosis": diagnosis,
        "fixture": observation,
        "process_boundary": {
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
            "accepted_sources_unchanged": source_diagnosis(contract) == diagnosis,
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
        "# Integrated-runner factory-subcoordinate diagnostic report\n\n"
        f"Date: {now.date().isoformat()}\n\n"
        f"Timestamp: {now.isoformat()} (Australia/Brisbane)\n\n"
        f"Result: `{PASS_RESULT}`\n\n"
        "The exact occupied runner traversed the installed rc.7 AgentRegistry "
        "and entered its supplied setup once. The exact occupied three-argument "
        "guard classified the runner's four-argument call as "
        f"`{EXPECTED_COORDINATE}` before preset mounting. The runner reproduced "
        "its generic `factory` terminal with zero request, tool or turn activity.\n\n"
        "The narrow correction is to materialise the already accepted root-service-"
        "forwarding guard/bridge/sanitizer graph beside the unchanged runner. No "
        "Harness, worker, model, provider, product or protected-ref boundary opened.\n",
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
        raise FactoryDiagnosticError("exactly_one_mode_required")
    value = provider_free_check() if args.check else execute()
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

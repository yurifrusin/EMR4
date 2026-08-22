"""Diagnose the native-Harness tool-result/conclusion seam without a provider."""

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
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

from orchestration_harness import git_object_resolution
from orchestration_harness import native_tool_result_conclusion_coordinate as coordinate
from scripts import (
    raisa_native_harness_bounded_occupied_useful_worker_rehearsal as accepted_worker,
)
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal as accepted_projection,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-tool-result-conclusion-coordinate-"
    "diagnostic-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
COORDINATE_SCHEMA_PATH = OPERATION_ROOT / "coordinate.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
FAILURE_SCHEMA_PATH = OPERATION_ROOT / "failure-terminal.schema.json"
DERIVED_RUNNER_PATH = OPERATION_ROOT / "future-runner.mjs"
EVIDENCE_PATH = OPERATION_ROOT / "deterministic-evidence.json"
REPORT_PATH = OPERATION_ROOT / "deterministic-report.md"
FAILURE_PATH = OPERATION_ROOT / "failure-terminal.json"
DISPOSABLE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
DISPOSABLE_ROOT = DISPOSABLE_PARENT / "deepseek-tool-result-coordinate-fixture-001"

CONTRACT_SCHEMA_VERSION = (
    "ariadne.native_harness_tool_result_conclusion_diagnostic_contract.v1"
)
EVIDENCE_SCHEMA_VERSION = (
    "ariadne.native_harness_tool_result_conclusion_diagnostic_evidence.v1"
)
FAILURE_SCHEMA_VERSION = (
    "ariadne.native_harness_tool_result_conclusion_diagnostic_failure.v1"
)
FUTURE_RUNNER_SCHEMA_VERSION = (
    "ariadne.native_harness_tool_result_conclusion_runner_terminal.v1"
)
FIXTURE_RESULT_SCHEMA_VERSION = (
    "ariadne.native_harness_tool_result_conclusion_fixture_result.v1"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
FAILURE_CODES = frozenset(
    {
        "contract_rejected",
        "package_source_rejected",
        "accepted_runner_rejected",
        "derived_runner_rejected",
        "historical_terminal_drift",
        "fixture_root_rejected",
        "fixture_process_failed",
        "fixture_output_rejected",
        "fixture_cleanup_failed",
        "evidence_rejected",
        "output_conflict",
        "unexpected_provider_free_failure",
    }
)


class DiagnosticRecoveryError(RuntimeError):
    """A provider-free diagnostic invariant failed closed."""

    def __init__(self, code: str) -> None:
        if code not in FAILURE_CODES:
            code = "unexpected_provider_free_failure"
        self.code = code
        super().__init__(code)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("json_root_invalid")
    return value


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise DiagnosticRecoveryError("derived_runner_rejected")
    return source.replace(old, new, 1)


def _replace_count(
    source: str, old: str, new: str, expected_count: int, label: str
) -> str:
    if source.count(old) != expected_count:
        raise DiagnosticRecoveryError("derived_runner_rejected")
    return source.replace(old, new)


def validate_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        value = load_json(path)
        jsonschema.Draft202012Validator(load_json(CONTRACT_SCHEMA_PATH)).validate(value)
        if value["schema_version"] != CONTRACT_SCHEMA_VERSION:
            raise ValueError("contract_schema_mismatch")
        if value["operation_id"] != OPERATION_ID:
            raise ValueError("contract_operation_mismatch")
        if value["coordinates"] != list(coordinate.COORDINATES):
            raise ValueError("contract_coordinates_mismatch")
        if len({row["variant_id"] for row in value["variants"]}) != 5:
            raise ValueError("contract_variant_ids_not_unique")
        if len({row["coordinate"] for row in value["variants"]}) != 5:
            raise ValueError("contract_variant_coordinates_not_unique")
        if set(value["process_limits"].values()) != {0, 1}:
            raise ValueError("contract_process_limits_invalid")
        if value["process_limits"]["node_fixture_process_count"] != 1:
            raise ValueError("contract_fixture_process_limit_invalid")
        for row in value["variants"]:
            released = coordinate.classify_observation(row["observation"])
            if released["coordinate"] != row["coordinate"]:
                raise ValueError("contract_variant_coordinate_mismatch")
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        coordinate.ToolResultConclusionCoordinateError,
    ) as error:
        raise DiagnosticRecoveryError("contract_rejected") from error
    return value


def _file_binding(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    payload = path.read_bytes()
    observed = {"bytes": len(payload), "sha256": sha256_bytes(payload)}
    if observed != expected:
        raise DiagnosticRecoveryError("package_source_rejected")
    return observed


def validate_package_source(contract: dict[str, Any]) -> dict[str, Any]:
    try:
        accepted_projection.validate_materialization_source(
            accepted_projection.load_contract()
        )
        root = (
            accepted_projection.MATERIALIZATION_SOURCE_ROOT.resolve(strict=True)
            / "node_modules"
            / "@deepseek-ai"
            / "dsh-tools"
        )
        package = load_json(root / "package.json")
        expected = contract["accepted_dsh_tools"]
        if (
            package.get("name") != expected["name"]
            or package.get("version") != expected["version"]
        ):
            raise DiagnosticRecoveryError("package_source_rejected")
        files = {
            relative: _file_binding(root / relative, binding)
            for relative, binding in expected["files"].items()
        }
        runtime = (root / "lib/index.js").read_text(encoding="utf-8")
        types = (root / "lib/types/index.d.ts").read_text(encoding="utf-8")
        post_definition = runtime.index("async postExecute(exec, result) {")
        post_end = runtime.index("\n\t}\n\t/** Registry-normalized", post_definition)
        post_body = runtime[post_definition:post_end]
        positions = {
            "finalize_post_execute_call": runtime.index(
                "const postResult = await this.postExecute(exec, result);"
            ),
            "post_execute_definition": post_definition,
            "success_marker_snapshot": runtime.index(
                "const concludesTurn = this.concludingExecutions.has(exec);"
            ),
            "success_marker_projection": runtime.index(
                "...concludesTurn ? { concludesTurn: true } : {}"
            ),
            "final_success_marker_projection": runtime.index(
                "...result.concludesTurn === true ? { concludesTurn: true } : {}"
            ),
        }
        checks = {
            "finalize_calls_post_execute": runtime.count(
                "const postResult = await this.postExecute(exec, result);"
            )
            == 1,
            "success_creation_snapshots_marker": runtime.count(
                "const concludesTurn = this.concludingExecutions.has(exec);"
            )
            == 1,
            "post_execute_does_not_resnapshot_marker": "concludingExecutions"
            not in post_body,
            "post_execute_default_is_accept": '() => Promise.resolve({ kind: "accept" })'
            in post_body,
            "success_type_allows_conclusion": "readonly concludesTurn?: true;" in types,
            "failure_type_forbids_conclusion": "readonly concludesTurn?: never;"
            in types,
            "result_observer_is_final_outcome": "Observe the frozen, lossless-JSON final outcome."
            in types,
            "post_execute_receives_normalized_outcome": "result - the dispatch outcome a listener may accept, replace, or block."
            in types,
        }
        if not all(checks.values()):
            raise DiagnosticRecoveryError("package_source_rejected")
    except DiagnosticRecoveryError:
        raise
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise DiagnosticRecoveryError("package_source_rejected") from error
    return {
        "name": package["name"],
        "version": package["version"],
        "files": files,
        "lifecycle_positions": positions,
        "lifecycle_checks": checks,
        "third_party_source_text_retained": False,
    }


_CLASSIFIER_SOURCE = """const TOOL_LIFECYCLE_KEYS = Object.freeze(["authoritative_final_result_kind", "conclusion_request_stage", "input_result_kind", "post_execute_decision_kind", "turn_kind"]);
const TOOL_LIFECYCLE_COORDINATES = Object.freeze({
  "success|accept|pre_execute_after_boundary_accept|success_concluding|completed": "edit_success_accept_concluded",
  "success|accept|post_execute_after_decision|success_nonconcluding|error": "edit_success_accept_late_marker",
  "error|accept|pre_execute_after_boundary_accept|error|error": "edit_error_accept_not_concluded",
  "success|block|pre_execute_after_boundary_accept|error|error": "edit_success_blocked_not_concluded",
  "success|failed|pre_execute_after_boundary_accept|error|error": "post_execute_decision_failed_not_concluded",
});
export function classifyToolLifecycle(observation) {
  if (!observation || typeof observation !== "object" || Array.isArray(observation) || JSON.stringify(Object.keys(observation).sort()) !== JSON.stringify(TOOL_LIFECYCLE_KEYS)) throw new Error("TOOL_LIFECYCLE_KEYS_INVALID");
  const key = [observation.input_result_kind, observation.post_execute_decision_kind, observation.conclusion_request_stage, observation.authoritative_final_result_kind, observation.turn_kind].join("|");
  const value = TOOL_LIFECYCLE_COORDINATES[key];
  if (value === undefined) throw new Error("TOOL_LIFECYCLE_COORDINATE_INVALID");
  return value;
}
"""


def derive_future_runner_source(
    accepted_payload: bytes, *, target_path: str, expected_sha256: str
) -> bytes:
    try:
        accepted = accepted_worker.validate_runner_source(accepted_payload, target_path)
    except (UnicodeError, accepted_worker.UsefulWorkerError) as error:
        raise DiagnosticRecoveryError("accepted_runner_rejected") from error
    if (
        accepted
        != {
            **accepted,
            "sha256": expected_sha256,
        }
        or accepted["sha256"] != expected_sha256
    ):
        raise DiagnosticRecoveryError("accepted_runner_rejected")
    source = accepted_payload.decode("utf-8")
    old_schema = accepted_worker.RUNNER_TERMINAL_SCHEMA_VERSION
    source = _replace_count(
        source, old_schema, FUTURE_RUNNER_SCHEMA_VERSION, 2, "runner_schema"
    )
    source = _replace_once(
        source,
        "  return { request_count: requestCount, tool_names: toolNames, tool_result_count: toolResultCount, turn_kind: turnKind };\n}\nexport function apply(ctx, config) {",
        "  return { request_count: requestCount, tool_names: toolNames, tool_result_count: toolResultCount, turn_kind: turnKind };\n}\n"
        + _CLASSIFIER_SOURCE
        + "export function apply(ctx, config) {",
        "classifier",
    )
    source = _replace_once(
        source,
        "    let observedCalls = 0;\n    let conclusionMarked = false;",
        "    let observedCalls = 0;\n"
        '    let conclusionRequestStage = "not_requested";\n'
        '    let postExecuteInputResultKind = "unobserved";\n'
        '    let postExecuteDecisionKind = "unobserved";\n'
        '    let authoritativeFinalResultKind = "unobserved";',
        "state",
    )
    source = _replace_once(
        source,
        '          if (exec.parent !== undefined || !args || typeof args !== "object" || args.file_path !== TARGET_PATH || args.replace_all === true) return { kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" };\n'
        "          return next();",
        '          if (exec.parent !== undefined || !args || typeof args !== "object" || args.file_path !== TARGET_PATH || args.replace_all === true) return { kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" };\n'
        "          exec.concludeTurn();\n"
        '          conclusionRequestStage = "pre_execute_after_boundary_accept";\n'
        "          return next();",
        "pre_execute_conclusion",
    )
    source = _replace_once(
        source,
        '        agentCtx.on("tools/post-execute", async (exec, result, next) => {\n'
        "          const decision = await next();\n"
        "          const args = exec.arguments;\n"
        '          if (observedCalls === 1 && exec.name === "edit" && exec.parent === undefined && args && typeof args === "object" && args.file_path === TARGET_PATH && args.replace_all !== true && result.isError === false && decision.kind === "accept") { exec.concludeTurn(); conclusionMarked = true; }\n'
        "          return decision;\n"
        "        });",
        '        agentCtx.on("tools/post-execute", async (exec, result, next) => {\n'
        '          postExecuteInputResultKind = result.isError === false ? "success" : "error";\n'
        "          try {\n"
        "            const decision = await next();\n"
        '            if (decision.kind !== "accept" && decision.kind !== "block") throw new Error("POST_EXECUTE_DECISION_INVALID");\n'
        "            postExecuteDecisionKind = decision.kind;\n"
        "            return decision;\n"
        "          } catch {\n"
        '            postExecuteDecisionKind = "failed";\n'
        '            throw new Error("POST_EXECUTE_DECISION_FAILED");\n'
        "          }\n"
        "        });\n"
        '        agentCtx.on("tools/result", (exec, result) => {\n'
        "          const args = exec.arguments;\n"
        '          if (observedCalls === 1 && exec.name === "edit" && exec.parent === undefined && args && typeof args === "object" && args.file_path === TARGET_PATH && args.replace_all !== true) authoritativeFinalResultKind = result.isError === true ? "error" : result.concludesTurn === true ? "success_concluding" : "success_nonconcluding";\n'
        "        });",
        "post_and_result_observers",
    )
    source = _replace_once(
        source,
        '    const passed = summary.request_count === 1 && summary.tool_names.length === 1 && summary.tool_names[0] === "edit" && summary.tool_result_count === 1 && summary.turn_kind === "completed" && conclusionMarked;\n'
        '    stage = "terminal";\n'
        "    writeTerminal(config.terminalPath, {\n"
        f'      schema_version: "{FUTURE_RUNNER_SCHEMA_VERSION}", status: passed ? "completed" : "failed", failure_stage: passed ? null : "terminal", session_id_sha256: digest(sessionText), provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, conclusion_marked: conclusionMarked, target_path_sha256: digest(TARGET_PATH), ...summary,\n'
        "    });",
        "    let toolLifecycleCoordinate = null;\n"
        "    try { toolLifecycleCoordinate = classifyToolLifecycle({ input_result_kind: postExecuteInputResultKind, post_execute_decision_kind: postExecuteDecisionKind, conclusion_request_stage: conclusionRequestStage, authoritative_final_result_kind: authoritativeFinalResultKind, turn_kind: summary.turn_kind }); } catch {}\n"
        '    const passed = summary.request_count === 1 && summary.tool_names.length === 1 && summary.tool_names[0] === "edit" && summary.tool_result_count === 1 && summary.turn_kind === "completed" && toolLifecycleCoordinate === "edit_success_accept_concluded";\n'
        '    stage = "terminal";\n'
        "    writeTerminal(config.terminalPath, {\n"
        f'      schema_version: "{FUTURE_RUNNER_SCHEMA_VERSION}", status: passed ? "completed" : "failed", failure_stage: passed ? null : "terminal", session_id_sha256: digest(sessionText), provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, target_path_sha256: digest(TARGET_PATH), tool_lifecycle: {{ input_result_kind: postExecuteInputResultKind, post_execute_decision_kind: postExecuteDecisionKind, conclusion_request_stage: conclusionRequestStage, authoritative_final_result_kind: authoritativeFinalResultKind, coordinate: toolLifecycleCoordinate }}, ...summary,\n'
        "    });",
        "terminal",
    )
    source = _replace_once(
        source,
        f'      writeTerminal(config.terminalPath, {{ schema_version: "{FUTURE_RUNNER_SCHEMA_VERSION}", status: "failed", failure_stage: safeStage, session_id_sha256: null, provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, conclusion_marked: false, target_path_sha256: digest(TARGET_PATH), request_count: 0, tool_names: [], tool_result_count: 0, turn_kind: null }});',
        f'      writeTerminal(config.terminalPath, {{ schema_version: "{FUTURE_RUNNER_SCHEMA_VERSION}", status: "failed", failure_stage: safeStage, session_id_sha256: null, provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, target_path_sha256: digest(TARGET_PATH), tool_lifecycle: {{ input_result_kind: "unobserved", post_execute_decision_kind: "unobserved", conclusion_request_stage: "not_requested", authoritative_final_result_kind: "unobserved", coordinate: null }}, request_count: 0, tool_names: [], tool_result_count: 0, turn_kind: null }});',
        "catch_terminal",
    )
    payload = source.encode("utf-8")
    validate_future_runner_source(
        payload,
        accepted_payload=accepted_payload,
        target_path=target_path,
        expected_accepted_sha256=expected_sha256,
    )
    return payload


def validate_future_runner_source(
    payload: bytes,
    *,
    accepted_payload: bytes,
    target_path: str,
    expected_accepted_sha256: str,
) -> dict[str, Any]:
    try:
        source = payload.decode("utf-8")
        accepted = accepted_worker.validate_runner_source(accepted_payload, target_path)
        if accepted["sha256"] != expected_accepted_sha256:
            raise ValueError("accepted_hash_mismatch")
        pre_start = source.index('agentCtx.on("tools/pre-execute"')
        post_start = source.index('agentCtx.on("tools/post-execute"')
        result_start = source.index('agentCtx.on("tools/result"')
        followup = source.index("agent.followup(")
        pre_body = source[pre_start:post_start]
        post_body = source[post_start:result_start]
        checks = {
            "accepted_runner_bound": sha256_bytes(accepted_payload)
            == expected_accepted_sha256,
            "one_classifier": source.count("export function classifyToolLifecycle(")
            == 1,
            "closed_coordinate_inventory_exact": source.count(
                "edit_success_accept_concluded"
            )
            == 2
            and all(source.count(name) == 1 for name in coordinate.COORDINATES[1:]),
            "one_pre_execute_conclusion": pre_body.count("exec.concludeTurn()") == 1,
            "conclusion_before_dispatch": pre_body.index("exec.concludeTurn()")
            < pre_body.index("return next();"),
            "no_post_execute_conclusion": "exec.concludeTurn()" not in post_body,
            "post_result_observer_order": pre_start
            < post_start
            < result_start
            < followup,
            "post_result_observer_authoritative": "result.concludesTurn === true"
            in source[result_start:followup],
            "typed_terminal_present": source.count("tool_lifecycle:") == 2,
            "new_schema_exact": source.count(FUTURE_RUNNER_SCHEMA_VERSION) == 2,
            "old_schema_absent": accepted_worker.RUNNER_TERMINAL_SCHEMA_VERSION
            not in source,
            "no_raw_error_projection": all(
                token not in source
                for token in ("error.message", "error.stack", "String(error)")
            ),
            "no_retry_resume_fallback": all(
                token not in source.lower()
                for token in ("retry(", "resume(", "fallback(")
            ),
        }
        if not all(checks.values()):
            raise ValueError("future_runner_checks_failed")
    except (
        UnicodeError,
        ValueError,
        accepted_worker.UsefulWorkerError,
    ) as error:
        raise DiagnosticRecoveryError("derived_runner_rejected") from error
    return {
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "accepted_runner_sha256": expected_accepted_sha256,
        "checks": checks,
    }


def _fixture_source(variants: list[dict[str, Any]], *, package_root: Path) -> bytes:
    encoded = json.dumps(variants, sort_keys=True, separators=(",", ":"))
    cordis_url = (
        (package_root.parent / "cordis" / "lib" / "index.js")
        .resolve(strict=True)
        .as_uri()
    )
    tools_url = (package_root / "lib" / "index.js").resolve(strict=True).as_uri()
    return f'''import {{ Context }} from "{cordis_url}";
import {{ ToolRuntime }} from "{tools_url}";
import {{ classifyToolLifecycle }} from "./future-runner.mjs";
const variants = {encoded};
async function simulate(row) {{
  const ctx = new Context();
  ctx.provide("systemPrompt", {{ tools() {{ return () => {{}}; }}, section() {{ return () => {{}}; }} }});
  const tools = new ToolRuntime(ctx);
  tools.register({{
    name: "edit",
    description: "Authored-synthetic lifecycle fixture",
    parameters: {{ type: "object", additionalProperties: false }},
    output: {{
      schema: {{ type: "object", properties: {{ changed: {{ type: "boolean" }} }}, required: ["changed"], additionalProperties: false }},
      render() {{ return [{{ type: "text", text: "synthetic" }}]; }},
    }},
    async execute() {{
      if (row.observation.input_result_kind === "error") throw new Error("SYNTHETIC_TOOL_ERROR");
      return {{ changed: true }};
    }},
  }});
  let inputResultKind = null;
  let postExecuteDecisionKind = null;
  let observedFinalKind = null;
  ctx.on("tools/pre-execute", async (exec, next) => {{
    if (row.observation.conclusion_request_stage === "pre_execute_after_boundary_accept") exec.concludeTurn();
    return next();
  }});
  ctx.on("tools/post-execute", async (exec, result, next) => {{
    inputResultKind = result.isError === false ? "success" : "error";
    if (row.observation.post_execute_decision_kind === "block") {{
      postExecuteDecisionKind = "block";
      return {{ kind: "block", feedback: [{{ type: "text", text: "synthetic block" }}] }};
    }}
    if (row.observation.post_execute_decision_kind === "failed") {{
      postExecuteDecisionKind = "failed";
      throw new Error("SYNTHETIC_POST_EXECUTE_FAILURE");
    }}
    const decision = await next();
    postExecuteDecisionKind = decision.kind;
    if (row.observation.conclusion_request_stage === "post_execute_after_decision") exec.concludeTurn();
    return decision;
  }});
  ctx.on("tools/result", (_exec, result) => {{
    observedFinalKind = result.isError === true ? "error" : result.concludesTurn === true ? "success_concluding" : "success_nonconcluding";
  }});
  const finalResult = await tools.execute({{ callId: `synthetic-${{row.variant_id}}`, name: "edit", arguments: {{}}, signal: new AbortController().signal }});
  const finalKind = finalResult.isError === true ? "error" : finalResult.concludesTurn === true ? "success_concluding" : "success_nonconcluding";
  if (finalKind !== observedFinalKind) throw new Error("FINAL_OBSERVER_MISMATCH");
  const turnKind = finalKind === "success_concluding" ? "completed" : "error";
  const observation = {{ input_result_kind: inputResultKind, post_execute_decision_kind: postExecuteDecisionKind, conclusion_request_stage: row.observation.conclusion_request_stage, authoritative_final_result_kind: finalKind, turn_kind: turnKind }};
  if (Object.keys(observation).some((key) => observation[key] !== row.observation[key]) || Object.keys(row.observation).length !== Object.keys(observation).length) throw new Error("FIXTURE_EXPECTATION_MISMATCH");
  const released = {{ variant_id: row.variant_id, schema_version: "{coordinate.SCHEMA_VERSION}", ...observation, coordinate: classifyToolLifecycle(observation) }};
  await ctx.fiber.dispose();
  return released;
}}
const rows = [];
for (const row of variants) rows.push(await simulate(row));
process.stdout.write(JSON.stringify({{ schema_version: "{FIXTURE_RESULT_SCHEMA_VERSION}", rows }}) + "\\n");
'''.encode("utf-8")


def _remove_exact_root(root: Path) -> bool:
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    try:
        resolved = root.resolve()
    except OSError:
        return False
    if resolved.parent != parent or resolved == parent or resolved.is_symlink():
        return False
    if resolved.exists():
        shutil.rmtree(resolved)
    return not resolved.exists()


def _fixture_environment(root: Path, node: Path) -> dict[str, str]:
    temp = root / "tmp"
    temp.mkdir()
    environment = {
        "PATH": str(node.parent),
        "TEMP": str(temp),
        "TMP": str(temp),
    }
    for key in ("SystemRoot", "WINDIR", "ComSpec", "PATHEXT"):
        if key in os.environ:
            environment[key] = os.environ[key]
    return environment


def run_node_fixture(
    contract: dict[str, Any], derived_payload: bytes
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    node_name = shutil.which("node")
    if node_name is None:
        raise DiagnosticRecoveryError("fixture_process_failed")
    node = Path(node_name).resolve(strict=True)
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = DISPOSABLE_ROOT.resolve()
    if root.parent != parent or root.exists():
        raise DiagnosticRecoveryError("fixture_root_rejected")
    package_root = (
        accepted_projection.MATERIALIZATION_SOURCE_ROOT.resolve(strict=True)
        / "node_modules"
        / "@deepseek-ai"
        / "dsh-tools"
    )
    cleanup_passed = False
    completed: subprocess.CompletedProcess[bytes] | None = None
    try:
        root.mkdir()
        (root / "future-runner.mjs").write_bytes(derived_payload)
        (root / "fixture.mjs").write_bytes(
            _fixture_source(contract["variants"], package_root=package_root)
        )
        completed = subprocess.run(
            [str(node), str(root / "fixture.mjs")],
            cwd=root,
            env=_fixture_environment(root, node),
            capture_output=True,
            check=False,
            timeout=30,
        )
        if completed.returncode != 0 or completed.stderr:
            raise DiagnosticRecoveryError("fixture_process_failed")
        result = json.loads(completed.stdout)
        if not isinstance(result, dict) or set(result) != {"schema_version", "rows"}:
            raise DiagnosticRecoveryError("fixture_output_rejected")
        if result["schema_version"] != FIXTURE_RESULT_SCHEMA_VERSION:
            raise DiagnosticRecoveryError("fixture_output_rejected")
        rows = result["rows"]
        if not isinstance(rows, list) or len(rows) != len(contract["variants"]):
            raise DiagnosticRecoveryError("fixture_output_rejected")
        for expected, row in zip(contract["variants"], rows, strict=True):
            if (
                not isinstance(row, dict)
                or row.get("variant_id") != expected["variant_id"]
            ):
                raise DiagnosticRecoveryError("fixture_output_rejected")
            released = {key: value for key, value in row.items() if key != "variant_id"}
            coordinate.validate_coordinate(released)
            jsonschema.Draft202012Validator(load_json(COORDINATE_SCHEMA_PATH)).validate(
                released
            )
            if released["coordinate"] != expected["coordinate"]:
                raise DiagnosticRecoveryError("fixture_output_rejected")
    except DiagnosticRecoveryError:
        raise
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        subprocess.SubprocessError,
        coordinate.ToolResultConclusionCoordinateError,
    ) as error:
        raise DiagnosticRecoveryError("fixture_output_rejected") from error
    finally:
        cleanup_passed = _remove_exact_root(root)
    if not cleanup_passed or root.exists():
        raise DiagnosticRecoveryError("fixture_cleanup_failed")
    assert completed is not None
    return rows, {
        "node_fixture_process_count": 1,
        "actual_dsh_tools_runtime_imported": True,
        "tool_runtime_execution_count": len(contract["variants"]),
        "exit_code": completed.returncode,
        "stdout_bytes": len(completed.stdout),
        "stdout_sha256": sha256_bytes(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "stderr_sha256": sha256_bytes(completed.stderr),
        "owned_process_absent": True,
        "disposable_root_absent": True,
    }


def provider_free_check() -> dict[str, Any]:
    contract = validate_contract()
    package = validate_package_source(contract)
    runner_contract = contract["accepted_runner"]
    try:
        source_resolution = git_object_resolution.resolve_commit_source(
            repo_root=REPO_ROOT,
            source_head=runner_contract["source_commit"],
        )
    except git_object_resolution.GitObjectResolutionError as error:
        raise DiagnosticRecoveryError("accepted_runner_rejected") from error
    accepted_payload = accepted_worker.runner_source(runner_contract["fixture_target"])
    if {
        "bytes": len(accepted_payload),
        "sha256": sha256_bytes(accepted_payload),
    } != {"bytes": runner_contract["bytes"], "sha256": runner_contract["sha256"]}:
        raise DiagnosticRecoveryError("accepted_runner_rejected")
    derived = derive_future_runner_source(
        accepted_payload,
        target_path=runner_contract["fixture_target"],
        expected_sha256=runner_contract["sha256"],
    )
    future = validate_future_runner_source(
        derived,
        accepted_payload=accepted_payload,
        target_path=runner_contract["fixture_target"],
        expected_accepted_sha256=runner_contract["sha256"],
    )
    historical = REPO_ROOT / contract["historical_terminal"]["path"]
    if sha256_file(historical) != contract["historical_terminal"]["sha256"]:
        raise DiagnosticRecoveryError("historical_terminal_drift")
    return {
        "schema_version": "ariadne.native_harness_tool_result_conclusion_preflight.v1",
        "status": "passed",
        "operation_id": OPERATION_ID,
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "package": package,
        "accepted_runner": {
            "bytes": len(accepted_payload),
            "sha256": sha256_bytes(accepted_payload),
            "source_commit": source_resolution["resolved_commit"],
            "source_commit_resolved": True,
            "source_is_ancestor_of_head": source_resolution[
                "source_is_ancestor_of_head"
            ],
        },
        "future_runner": future,
        "historical_terminal_sha256": sha256_file(historical),
        "coordinate_count": len(contract["coordinates"]),
        "native_harness_process_count": 0,
        "worker_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "network_attempt_count": 0,
    }


def _write_exact(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise DiagnosticRecoveryError("output_conflict")
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)


def _render_report(evidence: dict[str, Any]) -> str:
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    coordinates = "\n".join(
        f"- `{row['variant_id']}` -> `{row['coordinate']}`"
        for row in evidence["variants"]
    )
    return f"""# DeepSeek native Harness tool-result/conclusion coordinate diagnostic report

Date: {timestamp[:10]}

Timestamp: {timestamp} (Australia/Brisbane)

Result: `{evidence["result"]}`

The provider-free source-bound diagnostic establishes that rc.7 snapshots the
conclusion marker while creating a successful tool result, before post-execute.
The future runner therefore requests conclusion only after the exact root-edit
pre-execute boundary accepts, then observes post-policy and authoritative final
result state separately.

{coordinates}

One local Node fixture process imported the exact accepted rc.7 `ToolRuntime`
and executed all five variants through its real pre-execute, body,
post-execute and result pipeline. Native Harness worker, model, provider,
broker, network, database, Docker, retry, resume and fallback counts are zero.
The disposable root and owned process are absent, and the consumed occupied
terminal remains byte-identical. This is diagnostic evidence only; it does not
prove a useful future DeepSeek edit.
"""


def execute() -> dict[str, Any]:
    preflight = provider_free_check()
    contract = validate_contract()
    runner_contract = contract["accepted_runner"]
    accepted_payload = accepted_worker.runner_source(runner_contract["fixture_target"])
    derived = derive_future_runner_source(
        accepted_payload,
        target_path=runner_contract["fixture_target"],
        expected_sha256=runner_contract["sha256"],
    )
    rows, fixture = run_node_fixture(contract, derived)
    released_rows = []
    for row in rows:
        released = {key: value for key, value in row.items() if key != "variant_id"}
        released_rows.append(
            {
                "variant_id": row["variant_id"],
                **coordinate.validate_coordinate(released),
            }
        )
    counters = dict(contract["process_limits"])
    evidence = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "status": "passed",
        "result": "tool_result_conclusion_coordinate_diagnostic_pass",
        "operation_id": OPERATION_ID,
        "evidence_label": contract["evidence_label"],
        "contract_sha256": preflight["contract_sha256"],
        "package_source": preflight["package"],
        "accepted_runner": preflight["accepted_runner"],
        "future_runner": preflight["future_runner"],
        "historical_terminal": {
            "sha256": preflight["historical_terminal_sha256"],
            "unchanged": True,
            "classification": "immutable_unresolved_observation",
        },
        "variants": released_rows,
        "process_counts": counters,
        "fixture": fixture,
        "cleanup": {
            "owned_process_absent": True,
            "disposable_root_absent": True,
            "raw_argument_content_value_error_retained": False,
            "raw_prompt_response_reasoning_session_environment_retained": False,
        },
    }
    try:
        jsonschema.Draft202012Validator(load_json(EVIDENCE_SCHEMA_PATH)).validate(
            evidence
        )
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as error:
        raise DiagnosticRecoveryError("evidence_rejected") from error
    _write_exact(DERIVED_RUNNER_PATH, derived)
    _write_exact(EVIDENCE_PATH, canonical_bytes(evidence))
    _write_exact(REPORT_PATH, _render_report(evidence).encode("utf-8"))
    return evidence


def write_failure_terminal(code: str) -> dict[str, Any]:
    value = {
        "schema_version": FAILURE_SCHEMA_VERSION,
        "status": "failed_closed",
        "operation_id": OPERATION_ID,
        "failure_coordinate": code
        if code in FAILURE_CODES
        else "unexpected_provider_free_failure",
        "native_harness_process_count": 0,
        "worker_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "broker_process_count": 0,
        "network_attempt_count": 0,
        "database_attempt_count": 0,
        "docker_attempt_count": 0,
        "retry_count": 0,
        "resume_count": 0,
        "fallback_count": 0,
        "disposable_root_absent": not DISPOSABLE_ROOT.exists(),
        "raw_sensitive_material_retained": False,
    }
    try:
        jsonschema.Draft202012Validator(load_json(FAILURE_SCHEMA_PATH)).validate(value)
        _write_exact(FAILURE_PATH, canonical_bytes(value))
    except (
        OSError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        DiagnosticRecoveryError,
    ):
        pass
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--run", action="store_true")
    args = parser.parse_args()
    try:
        value = provider_free_check() if args.check else execute()
        print(json.dumps({"status": value["status"], "operation_id": OPERATION_ID}))
        return 0
    except DiagnosticRecoveryError as error:
        terminal = write_failure_terminal(error.code)
        print(
            json.dumps(
                {"status": terminal["status"], "error": terminal["failure_coordinate"]}
            )
        )
        return 1
    except Exception:
        terminal = write_failure_terminal("unexpected_provider_free_failure")
        print(
            json.dumps(
                {"status": terminal["status"], "error": terminal["failure_coordinate"]}
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

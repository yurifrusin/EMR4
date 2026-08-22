"""Build provider-free evidence for native-Harness edit-coordinate runner integration."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Any

import jsonschema

from orchestration_harness import native_edit_argument_result_coordinate as coordinate
from scripts import (
    deepseek_native_harness_provider_free_edit_argument_result_coordinate_diagnostic_recovery
    as predecessor,
)


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-edit-coordinate-future-runner-"
    "integration-rehearsal"
)
TOPIC = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = TOPIC / "contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = TOPIC / "evidence.schema.json"
FAILURE_SCHEMA_PATH = TOPIC / "failure-terminal.schema.json"
DERIVED_RUNNER_PATH = TOPIC / "integrated-future-runner.mjs"
EVIDENCE_PATH = TOPIC / "deterministic-evidence.json"
REPORT_PATH = TOPIC / "deterministic-report.md"
FAILURE_PATH = TOPIC / "failure-terminal.json"
DISPOSABLE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
DISPOSABLE_ROOT = DISPOSABLE_PARENT / "deepseek-edit-coordinate-runner-integration-001"

CONTRACT_SCHEMA_VERSION = (
    "ariadne.native_harness_edit_coordinate_future_runner_integration_contract.v1"
)
EVIDENCE_SCHEMA_VERSION = (
    "ariadne.native_harness_edit_coordinate_future_runner_integration_evidence.v1"
)
FAILURE_SCHEMA_VERSION = (
    "ariadne.native_harness_edit_coordinate_future_runner_integration_failure.v1"
)
FIXTURE_SCHEMA_VERSION = (
    "ariadne.native_harness_edit_coordinate_future_runner_integration_fixture.v1"
)
TRANSFORMATION_VERSION = "edit_coordinate_future_runner_integration_v1"

VARIANT_IDS = (
    "unique_match_success",
    "replace_all_success",
    "schema_missing_required",
    "blank_file_path",
    "empty_old_string",
    "equal_old_new",
    "missing_target",
    "literal_not_found",
    "literal_ambiguous",
)
PRE_DISPATCH_DECISIONS = (
    "defer_to_tool_schema",
    "deny_blank_file_path",
    "deny_empty_old_string",
    "deny_equal_old_new",
    "admit_semantic_constraints",
)
EXPECTED_VARIANT_ROWS = (
    ("unique_match_success", "admit_semantic_constraints", True, "edit_success_unique_match", None, "unique_match"),
    ("replace_all_success", "admit_semantic_constraints", True, "edit_success_replace_all", None, "replace_all"),
    ("schema_missing_required", "defer_to_tool_schema", True, "edit_error_invalid_args", "INVALID_ARGS", None),
    ("blank_file_path", "deny_blank_file_path", False, "edit_error_untyped_argument_constraint", None, None),
    ("empty_old_string", "deny_empty_old_string", False, "edit_error_untyped_argument_constraint", None, None),
    ("equal_old_new", "deny_equal_old_new", False, "edit_error_untyped_argument_constraint", None, None),
    ("missing_target", "admit_semantic_constraints", True, "edit_error_fs_stale_version", "FS_STALE_VERSION", None),
    ("literal_not_found", "admit_semantic_constraints", True, "edit_error_fs_edit_not_found", "FS_EDIT_NOT_FOUND", None),
    ("literal_ambiguous", "admit_semantic_constraints", True, "edit_error_fs_ambiguous_edit", "FS_AMBIGUOUS_EDIT", None),
)
FAILURE_CODES = frozenset(
    {
        "contract_rejected",
        "input_binding_rejected",
        "runner_derivation_rejected",
        "runner_syntax_rejected",
        "fixture_root_rejected",
        "fixture_source_rejected",
        "fixture_process_failed",
        "fixture_output_rejected",
        "fixture_cleanup_failed",
        "evidence_rejected",
        "output_conflict",
        "unexpected_provider_free_failure",
    }
)


class EditCoordinateIntegrationError(ValueError):
    """One closed integration invariant failed."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code if code in FAILURE_CODES else "unexpected_provider_free_failure"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("object_required")
    return value


def _resolve_owned(path_text: str) -> Path:
    path = (ROOT / path_text).resolve(strict=True)
    try:
        path.relative_to(ROOT.resolve(strict=True))
    except ValueError as error:
        raise EditCoordinateIntegrationError("input_binding_rejected") from error
    return path


def _binding(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    value = path.read_bytes()
    if len(value) != expected["bytes"] or sha256_bytes(value) != expected["sha256"]:
        raise EditCoordinateIntegrationError("input_binding_rejected")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(value),
        "sha256": sha256_bytes(value),
    }


def _git_binding(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    observed = _binding(path, expected)
    source = expected["source_commit"]
    checks = (
        subprocess.run(
            ["git", "cat-file", "-e", f"{source}^{{commit}}"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        ),
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", source, "HEAD"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        ),
    )
    if checks[0].returncode != 0 or checks[1].returncode != 0:
        raise EditCoordinateIntegrationError("input_binding_rejected")
    return {**observed, "source_commit": source, "source_is_ancestor_of_head": True}


def validate_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        value = load_json(path)
        schema = load_json(CONTRACT_SCHEMA_PATH)
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
        if path.read_bytes() != canonical_bytes(value):
            raise ValueError("contract_not_canonical")
        if value["schema_version"] != CONTRACT_SCHEMA_VERSION:
            raise ValueError("schema_version_invalid")
        if tuple(value["coordinates"]) != coordinate.COORDINATES:
            raise ValueError("coordinate_order_invalid")
        if tuple(value["derivation"]["pre_dispatch_decisions"]) != (
            PRE_DISPATCH_DECISIONS
        ):
            raise ValueError("decision_order_invalid")
        if tuple(row["variant_id"] for row in value["variants"]) != VARIANT_IDS:
            raise ValueError("variant_order_invalid")
        observed_rows = tuple(
            (
                row["variant_id"],
                row["pre_dispatch_decision"],
                row["tool_execution_expected"],
                row["expected_coordinate"],
                row["structured_error_code"],
                row["success_class"],
            )
            for row in value["variants"]
        )
        if observed_rows != EXPECTED_VARIANT_ROWS:
            raise ValueError("variant_contract_invalid")
        if sum(row["tool_execution_expected"] for row in value["variants"]) != 6:
            raise ValueError("tool_execution_count_invalid")
        if value["process_limits"] != {
            "node_fixture_process_count": 1,
            "real_edit_tool_execution_count": 6,
            "pre_dispatch_denial_count": 3,
            "native_harness_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "broker_process_count": 0,
            "broker_request_count": 0,
            "network_attempt_count": 0,
            "database_attempt_count": 0,
            "docker_attempt_count": 0,
            "retry_count": 0,
            "resume_count": 0,
            "fallback_count": 0,
        }:
            raise ValueError("process_limits_invalid")
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.ValidationError) as error:
        raise EditCoordinateIntegrationError("contract_rejected") from error
    return value


def validate_inputs(contract: dict[str, Any]) -> dict[str, Any]:
    inputs = contract["accepted_inputs"]
    bindings = {
        "future_runner": _git_binding(
            _resolve_owned(inputs["future_runner"]["path"]), inputs["future_runner"]
        ),
        "python_coordinate_classifier": _git_binding(
            _resolve_owned(inputs["python_coordinate_classifier"]["path"]),
            inputs["python_coordinate_classifier"],
        ),
        "predecessor_contract": _binding(
            _resolve_owned(inputs["predecessor_contract"]["path"]),
            inputs["predecessor_contract"],
        ),
        "predecessor_evidence": _binding(
            _resolve_owned(inputs["predecessor_evidence"]["path"]),
            inputs["predecessor_evidence"],
        ),
    }
    predecessor_contract = predecessor.validate_contract()
    predecessor_preflight = predecessor.provider_free_check()
    predecessor_evidence = load_json(predecessor.EVIDENCE_PATH)
    if (
        predecessor_evidence.get("status") != "passed"
        or predecessor_evidence.get("variants") is None
        or len(predecessor_evidence["variants"]) != len(VARIANT_IDS)
    ):
        raise EditCoordinateIntegrationError("input_binding_rejected")
    if tuple(predecessor_contract["coordinates"]) != coordinate.COORDINATES:
        raise EditCoordinateIntegrationError("input_binding_rejected")
    return {
        **bindings,
        "packages": predecessor_preflight["package_source"],
        "consumed_attempt_bindings": predecessor_preflight[
            "consumed_attempt_bindings"
        ],
        "packages_root": predecessor_preflight["packages_root"],
    }


def _replace_once(value: str, old: str, new: str) -> str:
    if value.count(old) != 1:
        raise EditCoordinateIntegrationError("runner_derivation_rejected")
    return value.replace(old, new, 1)


EDIT_COORDINATE_BLOCK = r'''
const EDIT_ARGUMENT_RESULT_KEYS = Object.freeze(["result_kind", "structured_error_code", "success_class", "target_changed"]);
const EDIT_RESULT_COORDINATES = Object.freeze({
  "success||unique_match|true": "edit_success_unique_match",
  "success||replace_all|true": "edit_success_replace_all",
  "error|INVALID_ARGS||false": "edit_error_invalid_args",
  "error|||false": "edit_error_untyped_argument_constraint",
  "error|FS_STALE_VERSION||false": "edit_error_fs_stale_version",
  "error|FS_EDIT_NOT_FOUND||false": "edit_error_fs_edit_not_found",
  "error|FS_AMBIGUOUS_EDIT||false": "edit_error_fs_ambiguous_edit",
});
export function preflightEditArguments(args) {
  let decision = "defer_to_tool_schema";
  let coordinate = null;
  if (args && typeof args === "object" && !Array.isArray(args) && typeof args.file_path === "string" && typeof args.old_string === "string" && typeof args.new_string === "string") {
    if (args.file_path.trim() === "") { decision = "deny_blank_file_path"; coordinate = "edit_error_untyped_argument_constraint"; }
    else if (args.old_string.length === 0) { decision = "deny_empty_old_string"; coordinate = "edit_error_untyped_argument_constraint"; }
    else if (args.old_string === args.new_string) { decision = "deny_equal_old_new"; coordinate = "edit_error_untyped_argument_constraint"; }
    else decision = "admit_semantic_constraints";
  }
  return { schema_version: "ariadne.native_harness_edit_argument_preflight.v1", decision, dispatch_permitted: coordinate === null, coordinate };
}
export function classifyEditArgumentResult(observation) {
  if (!observation || typeof observation !== "object" || Array.isArray(observation) || JSON.stringify(Object.keys(observation).sort()) !== JSON.stringify(EDIT_ARGUMENT_RESULT_KEYS)) throw new Error("EDIT_ARGUMENT_RESULT_KEYS_INVALID");
  if (!new Set(["success", "error"]).has(observation.result_kind)) throw new Error("EDIT_RESULT_KIND_INVALID");
  if (!new Set([null, "INVALID_ARGS", "FS_STALE_VERSION", "FS_EDIT_NOT_FOUND", "FS_AMBIGUOUS_EDIT"]).has(observation.structured_error_code)) throw new Error("EDIT_ERROR_CODE_INVALID");
  if (!new Set([null, "unique_match", "replace_all"]).has(observation.success_class) || typeof observation.target_changed !== "boolean") throw new Error("EDIT_RESULT_FIELD_INVALID");
  const key = [observation.result_kind, observation.structured_error_code ?? "", observation.success_class ?? "", String(observation.target_changed)].join("|");
  const value = EDIT_RESULT_COORDINATES[key];
  if (value === undefined) throw new Error("EDIT_ARGUMENT_RESULT_COORDINATE_INVALID");
  return value;
}
function targetState(path) {
  if (!existsSync(path)) return { present: false, bytes: null, sha256: null };
  const value = readFileSync(path);
  return { present: true, bytes: value.length, sha256: digest(value) };
}
function targetChanged(before, after) {
  return before.present !== after.present || before.bytes !== after.bytes || before.sha256 !== after.sha256;
}
'''


def derive_runner(base: bytes) -> bytes:
    try:
        newline = "\r\n" if b"\r\n" in base else "\n"
        value = base.decode("utf-8").replace("\r\n", "\n")
        value = _replace_once(
            value,
            'import { closeSync, openSync, writeFileSync } from "node:fs";',
            'import { closeSync, existsSync, openSync, readFileSync, writeFileSync } from "node:fs";',
        )
        value = _replace_once(
            value,
            "\nexport function apply(ctx, config) {",
            f"\n{EDIT_COORDINATE_BLOCK}\nexport function apply(ctx, config) {{",
        )
        value = _replace_once(
            value,
            '    let authoritativeFinalResultKind = "unobserved";',
            '    let authoritativeFinalResultKind = "unobserved";\n'
            '    let editArgumentDecision = "not_observed";\n'
            "    let editResultCoordinate = null;\n"
            "    let targetBeforeState = null;",
        )
        value = _replace_once(
            value,
            "          const args = exec.arguments;\n"
            '          if (exec.parent !== undefined || !args || typeof args !== "object" || args.file_path !== TARGET_PATH || args.replace_all === true) return { kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" };',
            "          const args = exec.arguments;\n"
            "          const argumentPreflight = preflightEditArguments(args);\n"
            "          editArgumentDecision = argumentPreflight.decision;\n"
            "          if (argumentPreflight.coordinate !== null) { editResultCoordinate = argumentPreflight.coordinate; return { kind: \"deny\", reason: \"EDIT_ARGUMENT_CONSTRAINT\" }; }\n"
            '          if (argumentPreflight.decision === "defer_to_tool_schema") return { kind: "deny", reason: "EDIT_SCHEMA_REQUIRED" };\n'
            '          if (exec.parent !== undefined || !args || typeof args !== "object" || args.file_path !== TARGET_PATH || args.replace_all === true) return { kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" };',
        )
        value = _replace_once(
            value,
            "        agentCtx.on(\"tools/result\", (exec, result) => {\n"
            "          const args = exec.arguments;\n"
            '          if (observedCalls === 1 && exec.name === "edit" && exec.parent === undefined && args && typeof args === "object" && args.file_path === TARGET_PATH && args.replace_all !== true) authoritativeFinalResultKind = result.isError === true ? "error" : result.concludesTurn === true ? "success_concluding" : "success_nonconcluding";\n'
            "        });",
            "        agentCtx.on(\"tools/result\", (exec, result) => {\n"
            "          const args = exec.arguments;\n"
            '          if (observedCalls === 1 && exec.name === "edit" && exec.parent === undefined && args && typeof args === "object" && args.file_path === TARGET_PATH && args.replace_all !== true) {\n'
            '            authoritativeFinalResultKind = result.isError === true ? "error" : result.concludesTurn === true ? "success_concluding" : "success_nonconcluding";\n'
            "            if (editResultCoordinate === null && targetBeforeState !== null) {\n"
            "              const afterState = targetState(TARGET_PATH);\n"
            '              const resultKind = result.isError === true ? "error" : "success";\n'
            '              const errorCode = result.isError === true && typeof result.error?.info?.code === "string" ? result.error.info.code : null;\n'
            '              const successClass = resultKind === "success" ? (args.replace_all === true ? "replace_all" : "unique_match") : null;\n'
            "              editResultCoordinate = classifyEditArgumentResult({ result_kind: resultKind, structured_error_code: errorCode, success_class: successClass, target_changed: targetChanged(targetBeforeState, afterState) });\n"
            "            }\n"
            "          }\n"
            "        });",
        )
        value = _replace_once(
            value,
            "    const firstSeq = agent.session.seq;",
            "    const firstSeq = agent.session.seq;\n"
            "    targetBeforeState = targetState(TARGET_PATH);",
        )
        value = _replace_once(
            value,
            "tool_lifecycle: { input_result_kind: postExecuteInputResultKind, post_execute_decision_kind: postExecuteDecisionKind, conclusion_request_stage: conclusionRequestStage, authoritative_final_result_kind: authoritativeFinalResultKind, coordinate: toolLifecycleCoordinate }, ...summary,",
            "tool_lifecycle: { input_result_kind: postExecuteInputResultKind, post_execute_decision_kind: postExecuteDecisionKind, conclusion_request_stage: conclusionRequestStage, authoritative_final_result_kind: authoritativeFinalResultKind, coordinate: toolLifecycleCoordinate }, edit_argument_result: { pre_dispatch_decision: editArgumentDecision, coordinate: editResultCoordinate }, ...summary,",
        )
        value = _replace_once(
            value,
            'tool_lifecycle: { input_result_kind: "unobserved", post_execute_decision_kind: "unobserved", conclusion_request_stage: "not_requested", authoritative_final_result_kind: "unobserved", coordinate: null }, request_count: 0,',
            'tool_lifecycle: { input_result_kind: "unobserved", post_execute_decision_kind: "unobserved", conclusion_request_stage: "not_requested", authoritative_final_result_kind: "unobserved", coordinate: null }, edit_argument_result: { pre_dispatch_decision: "not_observed", coordinate: null }, request_count: 0,',
        )
    except UnicodeDecodeError as error:
        raise EditCoordinateIntegrationError("runner_derivation_rejected") from error
    return value.replace("\n", newline).encode("utf-8")


def validate_derived_source(value: bytes) -> dict[str, bool]:
    text = value.decode("utf-8")
    checks = {
        "argument_preflight_export_once": text.count(
            "export function preflightEditArguments(args)"
        )
        == 1,
        "result_classifier_export_once": text.count(
            "export function classifyEditArgumentResult(observation)"
        )
        == 1,
        "pre_execute_preflight_use_once": text.count(
            "const argumentPreflight = preflightEditArguments(args);"
        )
        == 1,
        "authoritative_result_classifier_use_once": text.count(
            "editResultCoordinate = classifyEditArgumentResult({"
        )
        == 1,
        "target_before_snapshot_once": text.count(
            "targetBeforeState = targetState(TARGET_PATH);"
        )
        == 1,
        "typed_terminal_field_twice": text.count("edit_argument_result:") == 2,
        "argument_constraint_denial_once": text.count(
            'reason: "EDIT_ARGUMENT_CONSTRAINT"'
        )
        == 1,
        "raw_error_message_parse_absent": "error.message" not in text,
        "existing_one_edit_boundary_preserved": text.count(
            'args.replace_all === true) return { kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH"'
        )
        == 1,
    }
    if not all(checks.values()):
        raise EditCoordinateIntegrationError("runner_derivation_rejected")
    return checks


def _write_exact(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise EditCoordinateIntegrationError("output_conflict")
        return
    path.write_bytes(payload)


def _fixture_source(
    variants: list[dict[str, Any]], packages_root: Path, runner_path: Path
) -> bytes:
    rows = [
        {
            "variant_id": row["variant_id"],
            "success_class": row["success_class"],
        }
        for row in variants
    ]
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    cordis_url = (packages_root / "cordis" / "lib" / "index.js").as_uri()
    tools_url = (packages_root / "dsh-tools" / "lib" / "index.js").as_uri()
    tool_fs_url = (packages_root / "dsh-tool-fs" / "lib" / "index.js").as_uri()
    fs_local_url = (packages_root / "dsh-fs-local" / "lib" / "index.js").as_uri()
    runner_url = runner_path.as_uri()
    return f'''import {{ createHash }} from "node:crypto";
import {{ existsSync, mkdirSync, readFileSync, rmSync, writeFileSync }} from "node:fs";
import {{ join }} from "node:path";
import {{ Context }} from "{cordis_url}";
import {{ ToolRuntime }} from "{tools_url}";
import {{ apply as applyToolFs }} from "{tool_fs_url}";
import {{ LocalFileSystem }} from "{fs_local_url}";
import {{ classifyEditArgumentResult, preflightEditArguments }} from "{runner_url}";
const variants = {encoded};
const fixtureRoot = process.cwd();
const workspace = join(fixtureRoot, "workspace");
function digest(value) {{ return createHash("sha256").update(value).digest("hex"); }}
function state(path) {{
  if (!existsSync(path)) return {{ present: false, bytes: null, sha256: null }};
  const value = readFileSync(path);
  return {{ present: true, bytes: value.length, sha256: digest(value) }};
}}
function spec(row, target) {{
  const ordinary = "header\\nneedle\\nfooter\\n";
  const multiple = "needle\\nmiddle\\nneedle\\n";
  switch (row.variant_id) {{
    case "unique_match_success": return {{ initial: ordinary, args: {{ file_path: target, old_string: "needle", new_string: "replacement" }} }};
    case "replace_all_success": return {{ initial: multiple, args: {{ file_path: target, old_string: "needle", new_string: "replacement", replace_all: true }} }};
    case "schema_missing_required": return {{ initial: ordinary, args: {{ file_path: target, old_string: "needle" }} }};
    case "blank_file_path": return {{ initial: ordinary, args: {{ file_path: "   ", old_string: "needle", new_string: "replacement" }} }};
    case "empty_old_string": return {{ initial: ordinary, args: {{ file_path: target, old_string: "", new_string: "replacement" }} }};
    case "equal_old_new": return {{ initial: ordinary, args: {{ file_path: target, old_string: "needle", new_string: "needle" }} }};
    case "missing_target": return {{ initial: null, args: {{ file_path: target, old_string: "needle", new_string: "replacement" }} }};
    case "literal_not_found": return {{ initial: ordinary, args: {{ file_path: target, old_string: "absent", new_string: "replacement" }} }};
    case "literal_ambiguous": return {{ initial: multiple, args: {{ file_path: target, old_string: "needle", new_string: "replacement" }} }};
    default: throw new Error("VARIANT_INVALID");
  }}
}}
const ctx = new Context();
ctx.provide("systemPrompt", {{ tools() {{ return () => {{}}; }}, section() {{ return () => {{}}; }} }});
const tools = new ToolRuntime(ctx);
new LocalFileSystem(ctx, {{ cwd: fixtureRoot, diffBasisMaxBytes: 10485760 }});
applyToolFs(ctx, {{ readLimit: 2000, readMaxLineLength: 2000, readMaxBytes: 51200, readStreamMinSize: 10485760 }});
const edit = tools.get("edit");
if (!edit || edit.description !== "Edit an existing UTF-8 text file by replacing literal text.") throw new Error("REAL_EDIT_NOT_MOUNTED");
const released = [];
let toolExecutionCount = 0;
let denialCount = 0;
for (const row of variants) {{
  rmSync(workspace, {{ recursive: true, force: true }});
  mkdirSync(workspace, {{ recursive: true }});
  const target = join(workspace, `${{row.variant_id}}.txt`);
  const value = spec(row, target);
  if (value.initial !== null) writeFileSync(target, value.initial, "utf8");
  const before = state(target);
  const preflight = preflightEditArguments(value.args);
  let resultKind = "error";
  let code = null;
  let successClass = null;
  let toolExecuted = false;
  if (preflight.dispatch_permitted) {{
    const result = await tools.execute({{ callId: `fixture-${{row.variant_id}}`, name: "edit", arguments: value.args, signal: new AbortController().signal }});
    toolExecuted = true;
    toolExecutionCount += 1;
    resultKind = result.isError === true ? "error" : "success";
    code = result.isError === true && typeof result.error?.info?.code === "string" ? result.error.info.code : null;
    successClass = resultKind === "success" ? row.success_class : null;
  }} else {{
    denialCount += 1;
  }}
  const after = state(target);
  const changed = before.present !== after.present || before.bytes !== after.bytes || before.sha256 !== after.sha256;
  const observation = {{ result_kind: resultKind, structured_error_code: code, success_class: successClass, target_changed: changed }};
  const classified = preflight.coordinate ?? classifyEditArgumentResult(observation);
  released.push({{ variant_id: row.variant_id, pre_dispatch_decision: preflight.decision, tool_executed: toolExecuted, ...observation, coordinate: classified, before, after }});
}}
const hostile = [
  {{ result_kind: "success", structured_error_code: null, success_class: "unique_match", target_changed: true, extra: false }},
  {{ result_kind: "error", structured_error_code: "UNKNOWN", success_class: null, target_changed: false }},
  {{ result_kind: "success", structured_error_code: null, success_class: "unique_match", target_changed: false }},
  {{ result_kind: "error", structured_error_code: "FS_EDIT_NOT_FOUND", success_class: null, target_changed: true }},
  {{ result_kind: "maybe", structured_error_code: null, success_class: null, target_changed: false }}
];
let hostileRejectionCount = 0;
for (const mutation of hostile) {{ try {{ classifyEditArgumentResult(mutation); }} catch {{ hostileRejectionCount += 1; }} }}
await ctx.fiber.dispose();
process.stdout.write(JSON.stringify({{ schema_version: "{FIXTURE_SCHEMA_VERSION}", actual_dsh_tools_runtime_imported: true, actual_dsh_tool_fs_edit_imported: true, actual_dsh_fs_local_imported: true, integrated_runner_imported: true, synthetic_edit_registration_count: 0, tool_execution_count: toolExecutionCount, pre_dispatch_denial_count: denialCount, hostile_rejection_count: hostileRejectionCount, cordis_disposed: true, rows: released }}) + "\\n");
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
    environment = {"PATH": str(node.parent), "TEMP": str(temp), "TMP": str(temp)}
    for key in ("SystemRoot", "WINDIR", "ComSpec", "PATHEXT"):
        if key in os.environ:
            environment[key] = os.environ[key]
    return environment


def validate_runner_with_node(runner_path: Path) -> tuple[bool, bool]:
    node_name = shutil.which("node")
    if node_name is None:
        raise EditCoordinateIntegrationError("runner_syntax_rejected")
    node = Path(node_name).resolve(strict=True)
    environment = {"PATH": str(node.parent)}
    for key in ("SystemRoot", "WINDIR", "ComSpec", "PATHEXT"):
        if key in os.environ:
            environment[key] = os.environ[key]
    syntax = subprocess.run(
        [str(node), "--check", str(runner_path)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        timeout=15,
    )
    imported = subprocess.run(
        [
            str(node),
            "--input-type=module",
            "--eval",
            "const m=await import(process.argv[1]); if(typeof m.preflightEditArguments!=='function'||typeof m.classifyEditArgumentResult!=='function') process.exit(2);",
            runner_path.as_uri(),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        timeout=15,
    )
    if syntax.returncode != 0 or syntax.stderr or imported.returncode != 0 or imported.stderr:
        raise EditCoordinateIntegrationError("runner_syntax_rejected")
    return True, True


def run_node_fixture(
    contract: dict[str, Any], packages_root: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    node_name = shutil.which("node")
    if node_name is None:
        raise EditCoordinateIntegrationError("fixture_process_failed")
    node = Path(node_name).resolve(strict=True)
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = DISPOSABLE_ROOT.resolve()
    if root.parent != parent or root.exists():
        raise EditCoordinateIntegrationError("fixture_root_rejected")
    source = _fixture_source(contract["variants"], packages_root, DERIVED_RUNNER_PATH)
    decoded = source.decode("utf-8")
    if (
        "tools.register(" in decoded
        or decoded.count("new ToolRuntime(ctx)") != 1
        or decoded.count("applyToolFs(ctx,") != 1
        or decoded.count("new LocalFileSystem(ctx,") != 1
    ):
        raise EditCoordinateIntegrationError("fixture_source_rejected")
    cleanup_passed = False
    completed: subprocess.CompletedProcess[bytes] | None = None
    try:
        root.mkdir()
        fixture_path = root / "fixture.mjs"
        fixture_path.write_bytes(source)
        completed = subprocess.run(
            [str(node), str(fixture_path)],
            cwd=root,
            env=_fixture_environment(root, node),
            capture_output=True,
            check=False,
            timeout=30,
        )
        if completed.returncode != 0 or completed.stderr:
            raise EditCoordinateIntegrationError("fixture_process_failed")
        output = json.loads(completed.stdout)
        expected_keys = {
            "schema_version",
            "actual_dsh_tools_runtime_imported",
            "actual_dsh_tool_fs_edit_imported",
            "actual_dsh_fs_local_imported",
            "integrated_runner_imported",
            "synthetic_edit_registration_count",
            "tool_execution_count",
            "pre_dispatch_denial_count",
            "hostile_rejection_count",
            "cordis_disposed",
            "rows",
        }
        if not isinstance(output, dict) or set(output) != expected_keys:
            raise EditCoordinateIntegrationError("fixture_output_rejected")
        if (
            output["schema_version"] != FIXTURE_SCHEMA_VERSION
            or output["actual_dsh_tools_runtime_imported"] is not True
            or output["actual_dsh_tool_fs_edit_imported"] is not True
            or output["actual_dsh_fs_local_imported"] is not True
            or output["integrated_runner_imported"] is not True
            or output["synthetic_edit_registration_count"] != 0
            or output["tool_execution_count"] != 6
            or output["pre_dispatch_denial_count"] != 3
            or output["hostile_rejection_count"] != 5
            or output["cordis_disposed"] is not True
        ):
            raise EditCoordinateIntegrationError("fixture_output_rejected")
        rows = output["rows"]
        if not isinstance(rows, list) or len(rows) != len(VARIANT_IDS):
            raise EditCoordinateIntegrationError("fixture_output_rejected")
        released_rows = []
        row_keys = {
            "variant_id",
            "pre_dispatch_decision",
            "tool_executed",
            "result_kind",
            "structured_error_code",
            "success_class",
            "target_changed",
            "coordinate",
            "before",
            "after",
        }
        for expected, row in zip(contract["variants"], rows, strict=True):
            if not isinstance(row, dict) or set(row) != row_keys:
                raise EditCoordinateIntegrationError("fixture_output_rejected")
            if (
                row["variant_id"] != expected["variant_id"]
                or row["pre_dispatch_decision"]
                != expected["pre_dispatch_decision"]
                or row["tool_executed"] != expected["tool_execution_expected"]
                or row["coordinate"] != expected["expected_coordinate"]
                or row["structured_error_code"]
                != expected["structured_error_code"]
                or row["success_class"] != expected["success_class"]
            ):
                raise EditCoordinateIntegrationError("fixture_output_rejected")
            expected_before, expected_after = predecessor._expected_state(
                row["variant_id"]
            )
            if row["before"] != expected_before or row["after"] != expected_after:
                raise EditCoordinateIntegrationError("fixture_output_rejected")
            observation = {
                "result_kind": row["result_kind"],
                "structured_error_code": row["structured_error_code"],
                "success_class": row["success_class"],
                "target_changed": row["target_changed"],
            }
            python_release = coordinate.classify_observation(observation)
            if python_release["coordinate"] != row["coordinate"]:
                raise EditCoordinateIntegrationError("fixture_output_rejected")
            released_rows.append(
                {
                    **row,
                    "python_coordinate_agreement": True,
                }
            )
    except EditCoordinateIntegrationError:
        raise
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
        coordinate.NativeEditCoordinateError,
    ) as error:
        raise EditCoordinateIntegrationError("fixture_output_rejected") from error
    finally:
        cleanup_passed = _remove_exact_root(root)
    if not cleanup_passed or root.exists():
        raise EditCoordinateIntegrationError("fixture_cleanup_failed")
    assert completed is not None
    return released_rows, {
        "node_fixture_process_count": 1,
        "actual_dsh_tools_runtime_imported": True,
        "actual_dsh_tool_fs_edit_imported": True,
        "actual_dsh_fs_local_imported": True,
        "integrated_runner_imported": True,
        "synthetic_edit_registration_count": 0,
        "real_edit_tool_execution_count": 6,
        "pre_dispatch_denial_count": 3,
        "hostile_rejection_count": 5,
        "cordis_disposed": True,
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
    inputs = validate_inputs(contract)
    packages_root = inputs.pop("packages_root")
    base = _resolve_owned(contract["accepted_inputs"]["future_runner"]["path"])
    derived = derive_runner(base.read_bytes())
    source_checks = validate_derived_source(derived)
    return {
        "schema_version": "ariadne.native_harness_edit_coordinate_future_runner_integration_preflight.v1",
        "status": "passed",
        "operation_id": OPERATION_ID,
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "input_bindings": inputs,
        "derived_bytes": derived,
        "source_checks": source_checks,
        "packages_root": packages_root,
    }


def _render_report(evidence: dict[str, Any]) -> str:
    lines = "\n".join(
        f"- `{row['variant_id']}`: `{row['pre_dispatch_decision']}` -> "
        f"`{row['coordinate']}` (tool executed: `{str(row['tool_executed']).lower()}`)"
        for row in evidence["variants"]
    )
    return f"""# Provider-free edit-coordinate future-runner integration report

Status: passed

Result: `provider_free_edit_coordinate_future_runner_integration_pass`

The exact accepted future runner was deterministically derived with a closed
semantic-argument preflight and the accepted seven-coordinate result
classifier. One local Node fixture imported that runner and the real accepted
rc.7 edit stack without starting a Harness worker, model, provider or broker.

## Closed readings

{lines}

The three semantic argument violations were denied before dispatch. The other
six variants executed the real edit tool exactly once. JavaScript and Python
coordinates agreed for all nine variants, both successful hash transitions
were exact, every failure preserved its target state and cleanup completed.
No raw arguments, content, errors, prompts, responses, reasoning, sessions,
environment or credentials were retained.
"""


def execute() -> dict[str, Any]:
    preflight = provider_free_check()
    contract = validate_contract()
    derived = preflight.pop("derived_bytes")
    packages_root = preflight.pop("packages_root")
    _write_exact(DERIVED_RUNNER_PATH, derived)
    syntax_passed, import_passed = validate_runner_with_node(DERIVED_RUNNER_PATH)
    rows, fixture = run_node_fixture(contract, packages_root)
    evidence = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "status": "passed",
        "result": "provider_free_edit_coordinate_future_runner_integration_pass",
        "evidence_label": contract["evidence_label"],
        "contract_sha256": preflight["contract_sha256"],
        "input_bindings": preflight["input_bindings"],
        "derived_runner": {
            "path": DERIVED_RUNNER_PATH.relative_to(ROOT).as_posix(),
            "bytes": len(derived),
            "sha256": sha256_bytes(derived),
            "syntax_check_passed": syntax_passed,
            "import_check_passed": import_passed,
            "transformation_version": TRANSFORMATION_VERSION,
            "source_checks": preflight["source_checks"],
        },
        "variants": rows,
        "process_counts": dict(contract["process_limits"]),
        "fixture": fixture,
        "cleanup": {
            "cordis_disposed": True,
            "owned_process_absent": True,
            "disposable_root_absent": True,
            "credentials_present_in_fixture_environment": False,
            "raw_arguments_content_error_stack_retained": False,
            "raw_prompt_response_reasoning_session_environment_retained": False,
        },
    }
    try:
        jsonschema.Draft202012Validator(load_json(EVIDENCE_SCHEMA_PATH)).validate(
            evidence
        )
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as error:
        raise EditCoordinateIntegrationError("evidence_rejected") from error
    _write_exact(EVIDENCE_PATH, canonical_bytes(evidence))
    _write_exact(REPORT_PATH, _render_report(evidence).encode("utf-8"))
    return evidence


def write_failure_terminal(code: str) -> dict[str, Any]:
    value = {
        "schema_version": FAILURE_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "status": "failed_closed",
        "failure_coordinate": code
        if code in FAILURE_CODES
        else "unexpected_provider_free_failure",
        "worker_model_provider_request_count": 0,
        "retry_count": 0,
        "resume_count": 0,
        "fallback_count": 0,
        "disposable_root_absent": not DISPOSABLE_ROOT.exists(),
    }
    try:
        jsonschema.Draft202012Validator(load_json(FAILURE_SCHEMA_PATH)).validate(value)
        _write_exact(FAILURE_PATH, canonical_bytes(value))
    except (
        OSError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        EditCoordinateIntegrationError,
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
    except EditCoordinateIntegrationError as error:
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

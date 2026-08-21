"""Statically diagnose the repaired-sentinel preactivation failure coordinate."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import subprocess
from typing import Any

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-repaired-sentinel-preactivation-"
    "source-coordinate-diagnosis"
)
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "diagnosis-evidence.json"
REPORT_PATH = CONTINUITY_ROOT / "diagnosis-report.md"
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_repaired_sentinel_preactivation_"
    "source_diagnosis_evidence.v1"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
FULL_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class DiagnosisError(RuntimeError):
    """The bounded static diagnosis failed closed."""


@dataclass(frozen=True)
class StaticInputs:
    components: dict[str, bytes]
    package_json: bytes
    loader_entry: bytes
    loader_tree: bytes


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _load_json_bytes(payload: bytes, coordinate: str) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DiagnosisError(f"static_json_invalid:{coordinate}") from error
    if not isinstance(value, dict):
        raise DiagnosisError(f"static_json_not_object:{coordinate}")
    return value


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_json_bytes(path.read_bytes(), "contract")
    schema = _load_json_bytes(CONTRACT_SCHEMA_PATH.read_bytes(), "contract_schema")
    jsonschema.validate(contract, schema)
    if contract.get("operation_id") != OPERATION_ID:
        raise DiagnosisError("contract_operation_mismatch")
    method = contract.get("method", {})
    if (
        method.get("execute_failed_author") is not False
        or method.get("import_failed_author") is not False
        or method.get("node_process_limit") != 0
        or method.get("harness_process_limit") != 0
        or method.get("provider_request_limit") != 0
        or method.get("raw_stream_reconstruction") is not False
        or method.get("required_unique_coordinate_count") != 1
    ):
        raise DiagnosisError("contract_static_boundary_mismatch")
    return contract


def _git_source_is_ancestor(object_id: str) -> bool:
    if FULL_OID.fullmatch(object_id) is None:
        return False
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{object_id}^{{commit}}"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    relation = subprocess.run(
        ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return exists.returncode == 0 and relation.returncode == 0


def repository_inputs(contract: dict[str, Any]) -> StaticInputs:
    components: dict[str, bytes] = {}
    for row in contract["components"]:
        path = REPO_ROOT / row["path"]
        if not path.is_file() or path.is_symlink() or row["role"] in components:
            raise DiagnosisError(f"component_path_invalid:{row['role']}")
        components[row["role"]] = path.read_bytes()

    package_root = Path(contract["package"]["materialization_root"])
    return StaticInputs(
        components=components,
        package_json=(package_root / "dsh" / "package.json").read_bytes(),
        loader_entry=(
            package_root / "cordis-plugin-loader" / "src" / "config" / "entry.ts"
        ).read_bytes(),
        loader_tree=(
            package_root / "cordis-plugin-loader" / "src" / "config" / "tree.ts"
        ).read_bytes(),
    )


def _module_constants(tree: ast.Module) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value_node = node.value
        if value_node is None or not isinstance(value_node, ast.Constant):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                values[target.id] = value_node.value
    return values


def _static_functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    functions: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name in functions:
                raise DiagnosisError(f"duplicate_static_function:{node.name}")
            functions[node.name] = node
    return functions


def _evaluate_static_expr(
    node: ast.expr,
    *,
    functions: dict[str, ast.FunctionDef],
    constants: dict[str, Any],
    stack: tuple[str, ...],
) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in constants:
        return constants[node.id]
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                rendered = _evaluate_static_expr(
                    value.value,
                    functions=functions,
                    constants=constants,
                    stack=stack,
                )
                if not isinstance(rendered, (str, int)):
                    raise DiagnosisError("static_fstring_value_invalid")
                parts.append(str(rendered))
            else:
                raise DiagnosisError("static_fstring_shape_invalid")
        return "".join(parts)
    if isinstance(node, ast.Call):
        if (
            isinstance(node.func, ast.Name)
            and not node.args
            and not node.keywords
            and node.func.id in functions
        ):
            return _evaluate_static_function(
                node.func.id,
                functions=functions,
                constants=constants,
                stack=stack,
            )[0]
        if isinstance(node.func, ast.Attribute) and node.func.attr == "encode":
            value = _evaluate_static_expr(
                node.func.value,
                functions=functions,
                constants=constants,
                stack=stack,
            )
            if not isinstance(value, str) or node.keywords or len(node.args) > 1:
                raise DiagnosisError("static_encode_shape_invalid")
            encoding = "utf-8"
            if node.args:
                encoding = _evaluate_static_expr(
                    node.args[0],
                    functions=functions,
                    constants=constants,
                    stack=stack,
                )
            if encoding != "utf-8":
                raise DiagnosisError("static_encode_not_utf8")
            return value.encode("utf-8")
    raise DiagnosisError(f"unsupported_static_expression:{type(node).__name__}")


def _evaluate_static_function(
    name: str,
    *,
    functions: dict[str, ast.FunctionDef],
    constants: dict[str, Any],
    stack: tuple[str, ...] = (),
) -> tuple[Any, ast.Return]:
    if name in stack:
        raise DiagnosisError(f"static_function_cycle:{name}")
    function = functions.get(name)
    if function is None or function.args.args or function.args.kwonlyargs:
        raise DiagnosisError(f"static_function_shape_invalid:{name}")
    returns = [node for node in function.body if isinstance(node, ast.Return)]
    non_doc = [
        node
        for node in function.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]
    if len(returns) != 1 or non_doc != returns or returns[0].value is None:
        raise DiagnosisError(f"static_function_not_single_return:{name}")
    value = _evaluate_static_expr(
        returns[0].value,
        functions=functions,
        constants=constants,
        stack=(*stack, name),
    )
    return value, returns[0]


def extract_static_module(source: bytes, function_name: str) -> dict[str, Any]:
    try:
        text = source.decode("utf-8")
        tree = ast.parse(text)
    except (UnicodeDecodeError, SyntaxError) as error:
        raise DiagnosisError("python_source_parse_failed") from error
    functions = _static_functions(tree)
    value, return_node = _evaluate_static_function(
        function_name,
        functions=functions,
        constants=_module_constants(tree),
    )
    if not isinstance(value, bytes):
        raise DiagnosisError("static_function_did_not_return_bytes")
    function = functions[function_name]
    segment = ast.get_source_segment(text, function)
    if segment is None:
        raise DiagnosisError("static_function_segment_unavailable")
    return {
        "bytes": value,
        "sha256": _sha256(value),
        "function_line": function.lineno,
        "return_line": return_node.lineno,
        "source_segment": segment,
        "source_text": text,
    }


def _line_column(payload: bytes, offset: int) -> tuple[int, int]:
    prefix = payload[:offset]
    return prefix.count(b"\n") + 1, offset - (prefix.rfind(b"\n") + 1) + 1


def lexical_line_terminator_violations(payload: bytes) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []

    marker = b".split(/"
    cursor = 0
    while True:
        start = payload.find(marker, cursor)
        if start < 0:
            break
        position = start + len(marker)
        escaped = False
        while position < len(payload):
            value = payload[position]
            if value in (10, 13):
                line, column = _line_column(payload, position)
                violations.append(
                    {
                        "offset": position,
                        "line": line,
                        "column": column,
                        "context": "regular_expression_literal",
                        "control": "LF" if value == 10 else "CR",
                    }
                )
            if value == 47 and not escaped:
                break
            if value == 92 and not escaped:
                escaped = True
            else:
                escaped = False
            position += 1
        cursor = start + len(marker)

    quote: int | None = None
    escaped = False
    for offset, value in enumerate(payload):
        if quote is None:
            if value in (34, 39):
                quote = value
                escaped = False
            continue
        if value in (10, 13):
            line, column = _line_column(payload, offset)
            violations.append(
                {
                    "offset": offset,
                    "line": line,
                    "column": column,
                    "context": "quoted_string_literal",
                    "control": "LF" if value == 10 else "CR",
                }
            )
        if value == quote and not escaped:
            quote = None
            continue
        if value == 92 and not escaped:
            escaped = True
        else:
            escaped = False

    return sorted(violations, key=lambda row: (row["offset"], row["context"]))


def _bindings(contract: dict[str, Any], inputs: StaticInputs) -> tuple[list[dict[str, Any]], bool]:
    rows: list[dict[str, Any]] = []
    expected_components = {row["role"]: row for row in contract["components"]}
    for role in sorted(expected_components):
        expected = expected_components[role]["sha256"]
        observed = _sha256(inputs.components.get(role, b""))
        rows.append(
            {
                "role": role,
                "expected_sha256": expected,
                "observed_sha256": observed,
                "matched": expected == observed,
            }
        )
    package_bindings = (
        ("rc7_package_manifest", contract["package"]["package_json_sha256"], inputs.package_json),
        ("rc7_loader_entry", contract["package"]["loader_entry_sha256"], inputs.loader_entry),
        ("rc7_loader_tree", contract["package"]["loader_tree_sha256"], inputs.loader_tree),
    )
    for role, expected, payload in package_bindings:
        observed = _sha256(payload)
        rows.append(
            {
                "role": role,
                "expected_sha256": expected,
                "observed_sha256": observed,
                "matched": expected == observed,
            }
        )
    sources_ok = all(
        _git_source_is_ancestor(value)
        for value in [contract["planning_source"], *contract["accepted_sources"].values()]
    )
    rows.append(
        {
            "role": "git_sources_full_and_ancestral",
            "expected_sha256": "0" * 64,
            "observed_sha256": "0" * 64 if sources_ok else "f" * 64,
            "matched": sources_ok,
        }
    )
    return rows, all(row["matched"] for row in rows)


def analyze_static_inputs(contract: dict[str, Any], inputs: StaticInputs) -> dict[str, Any]:
    bindings, bindings_ok = _bindings(contract, inputs)
    package = _load_json_bytes(inputs.package_json, "package_manifest")
    terminal = _load_json_bytes(
        inputs.components["failed_boot_terminal"], "failed_boot_terminal"
    )
    control_terminal = _load_json_bytes(
        inputs.components["passing_control_terminal"], "passing_control_terminal"
    )

    failed_module = extract_static_module(
        inputs.components["failed_sentinel_author"], "sentinel_source"
    )
    control_module = extract_static_module(
        inputs.components["passing_control_author"], "sentinel_source"
    )
    failed_violations = lexical_line_terminator_violations(failed_module["bytes"])
    control_violations = lexical_line_terminator_violations(control_module["bytes"])

    failed_segment = failed_module["source_segment"]
    control_source = control_module["source_text"]
    spelling = {
        "failed_single_escaped_regex": failed_segment.count(r"split(/\r?\n/)") == 1,
        "failed_single_escaped_newline_string": failed_segment.count(r'+ "\n",') == 1,
        "control_double_escaped_regex": control_source.count(r"split(/\\r?\\n/)") >= 1,
        "control_double_escaped_newline_string": control_source.count(r'+ "\\n",') >= 1,
    }
    first_violation = failed_violations[0] if failed_violations else None
    source_coordinate_count = int(
        bool(
            failed_violations
            and first_violation is not None
            and first_violation["context"] == "regular_expression_literal"
            and first_violation["control"] == "CR"
            and all(spelling.values())
        )
    )

    failed_zero_fields = (
        "broker_processes",
        "changed_runner_processes",
        "database_invocations",
        "docker_invocations",
        "model_requests",
        "network_attempts",
        "prompts",
        "provider_requests",
        "tool_executions",
        "worker_sessions",
    )
    control_zero_fields = (
        "agent_session_count",
        "broker_request_count",
        "database_invocation_count",
        "docker_invocation_count",
        "model_request_count",
        "network_attempt_count",
        "occupied_worker_count",
        "provider_request_count",
        "turn_count",
    )
    terminal_ok = bool(
        terminal.get("result") == "failed_closed"
        and terminal.get("failure_coordinate")
        == "native_process_exited_before_readiness"
        and terminal.get("hmr_events") == []
        and terminal.get("launch", {}).get("exit_code_after_controller_termination") == 1
        and terminal.get("launch", {}).get("readiness_observed") is False
        and terminal.get("launch", {}).get("retry_count") == 0
        and terminal.get("streams", {}).get("raw_retained") is False
        and terminal.get("streams", {}).get("stderr", {}).get("byte_count") == 79
        and all(
            terminal.get("provider_boundary", {}).get(field) == 0
            for field in failed_zero_fields
        )
    )
    control_events = control_terminal.get("events", [])
    control_ok = bool(
        control_terminal.get("result") == "pass"
        and control_events[:2] == ["sentinel_activated", "stock_headless_hmr_ready"]
        and control_terminal.get("native_process_count") == 1
        and control_terminal.get("automatic_retry_count") == 0
        and not control_violations
        and all(
            control_terminal.get("provider_boundary", {}).get(field) == 0
            for field in control_zero_fields
        )
    )
    package_ok = bool(
        package.get("name") == contract["package"]["name"]
        and package.get("version") == contract["package"]["version"]
        and "else if (name.startsWith('.'))" in inputs.loader_tree.decode("utf-8")
        and "new URL(name, this.ctx.baseUrl).href" in inputs.loader_tree.decode("utf-8")
        and "throw updateError('import', this.options, error)" in inputs.loader_entry.decode("utf-8")
    )
    module_digest_ok = failed_module["sha256"] == terminal.get("profile", {}).get(
        "sentinel_sha256"
    )

    unique = bool(
        bindings_ok
        and terminal_ok
        and control_ok
        and package_ok
        and module_digest_ok
        and source_coordinate_count
        == contract["method"]["required_unique_coordinate_count"]
    )
    if unique:
        result = "pass"
        verdict = "unique_supported_coordinate"
        coordinate = (
            "failed_sentinel_author.sentinel_source.return_bytes_literal:"
            "python_escape_translation_emits_raw_line_terminators_inside_"
            "javascript_regex_and_string_literals"
        )
    else:
        result = "failed_closed"
        verdict = "insufficient_source_coordinate"
        coordinate = None

    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "result": result,
        "verdict": verdict,
        "bindings": bindings,
        "terminal": {
            "binding_passed": terminal_ok,
            "result": terminal.get("result"),
            "failure_coordinate": terminal.get("failure_coordinate"),
            "exit_code": terminal.get("launch", {}).get(
                "exit_code_after_controller_termination"
            ),
            "hmr_event_count": len(terminal.get("hmr_events", [])),
            "readiness_observed": terminal.get("launch", {}).get(
                "readiness_observed"
            ),
            "retry_count": terminal.get("launch", {}).get("retry_count"),
            "stderr_byte_count": terminal.get("streams", {})
            .get("stderr", {})
            .get("byte_count"),
            "raw_streams_retained": terminal.get("streams", {}).get("raw_retained"),
        },
        "lexical_analysis": {
            "failed_module_sha256": failed_module["sha256"],
            "failed_module_digest_matches_terminal": module_digest_ok,
            "source_function_line": failed_module["function_line"],
            "source_return_line": failed_module["return_line"],
            "source_spelling": spelling,
            "violation_count": len(failed_violations),
            "first_fatal_coordinate": first_violation,
            "source_coordinate_count": source_coordinate_count,
            "classification": "javascript_lexical_line_terminator_in_literal",
        },
        "passing_control": {
            "binding_passed": control_ok,
            "module_sha256": control_module["sha256"],
            "lexical_violation_count": len(control_violations),
            "first_two_events": control_events[:2],
            "result": control_terminal.get("result"),
        },
        "narrowest_supported_coordinate": coordinate,
        "zero_activity": {
            "node_process_count": 0,
            "harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_request_count": 0,
            "raw_stream_reconstruction_count": 0,
        },
        "claim_boundary": contract["claim_boundary"],
    }
    jsonschema.validate(evidence, _load_json_bytes(EVIDENCE_SCHEMA_PATH.read_bytes(), "evidence_schema"))
    return evidence


def report_markdown(evidence: dict[str, Any]) -> str:
    timestamp = datetime.now().astimezone().isoformat()
    lexical = evidence["lexical_analysis"]
    coordinate = evidence["narrowest_supported_coordinate"] or "none"
    first = lexical["first_fatal_coordinate"] or {}
    return f"""# DeepSeek native Harness repaired-sentinel preactivation source-coordinate diagnosis

Date: {timestamp[:10]}
Timestamp: {timestamp} (Australia/Brisbane)

## Result

- Verdict: `{evidence['verdict']}`
- Narrowest supported coordinate: `{coordinate}`
- Generated-module lexical violations: `{lexical['violation_count']}`
- First fatal generated coordinate: line `{first.get('line', 'none')}`, column `{first.get('column', 'none')}` (`{first.get('context', 'none')}` / `{first.get('control', 'none')}`)
- Accepted passing-control violations: `{evidence['passing_control']['lexical_violation_count']}`
- Node / Harness / broker / worker / model / provider / network activity: `0 / 0 / 0 / 0 / 0 / 0 / 0`

## Reading

The failed author returns one ordinary Python bytes literal. Python translates its single-escaped carriage-return and newline spellings before writing the JavaScript module, placing raw line terminators inside a JavaScript regular-expression literal and a quoted string. The first such byte is sufficient to reject module parsing before `apply()` can emit `sentinel_activated`. The accepted control double-escapes those spellings, has no lexical violation and previously emitted both readiness events on the same pinned rc.7 materialisation.

No destroyed stderr message, raw path, stack, environment or stream content was reconstructed or guessed from the retained digest.

## Claim boundary

{evidence['claim_boundary']}
"""


def run(output_root: Path = CONTINUITY_ROOT) -> dict[str, Any]:
    contract = load_contract()
    evidence = analyze_static_inputs(contract, repository_inputs(contract))
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / EVIDENCE_PATH.name).write_bytes(_canonical_json(evidence))
    (output_root / REPORT_PATH.name).write_text(
        report_markdown(evidence), encoding="utf-8", newline="\n"
    )
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=CONTINUITY_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evidence = run(args.output_root)
    except (DiagnosisError, OSError, jsonschema.ValidationError) as error:
        raise SystemExit(str(error)) from error
    print(evidence["verdict"])
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

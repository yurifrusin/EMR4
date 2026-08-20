"""Closed structured diagnostics for native-Harness failures before first HMR."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Sequence

from orchestration_harness import native_startup_terminal as legacy_terminal


SCHEMA_VERSION = "ariadne.native_harness_pre_hmr_structured_diagnostic.v1"
TERMINAL_SCHEMA_VERSION = "ariadne.native_harness_pre_hmr_startup_terminal.v2"
TERMINAL_CAUSE = "structured_entrypoint_import_rejected"
PHASE = "entrypoint_import_rejected"
MAX_CAUSE_NODES = 6
MAX_SIDECAR_BYTES = 16_384
ERROR_KINDS = frozenset(
    {
        "aggregate_error",
        "config_file_error",
        "cordis_error",
        "error",
        "type_error",
        "unknown",
        "validation_error",
    }
)
CODE_COORDINATES = frozenset(
    {
        "ERR_INVALID_MODULE_SPECIFIER",
        "ERR_INVALID_PACKAGE_CONFIG",
        "ERR_MODULE_NOT_FOUND",
        "ERR_PACKAGE_PATH_NOT_EXPORTED",
        "ERR_REQUIRE_ESM",
        "ERR_UNKNOWN_BUILTIN_MODULE",
        "ERR_UNSUPPORTED_DIR_IMPORT",
        "INACTIVE_EFFECT",
        "MODULE_NOT_FOUND",
        "none",
        "unrecognized",
    }
)
CONFIG_STAGES = frozenset({"none", "parse", "read", "validate"})
MESSAGE_COORDINATES = frozenset(
    {
        "entries_did_not_activate",
        "host_preparation_failed",
        "none",
        "plugin_tree_failed_to_load",
        "plugins_failed_to_load",
    }
)
AGGREGATE_SHAPES = frozenset({"multiple", "none", "one", "unreadable", "zero"})
_FULL_OID = re.compile(r"^[0-9a-f]{40}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")
_MISSING = object()


class StructuredDiagnosticError(ValueError):
    """The safe diagnostic contract was not satisfied."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise StructuredDiagnosticError(f"{label}_invalid")
    return value


def _read(value: object, key: str, default: object = _MISSING) -> object:
    try:
        if isinstance(value, dict):
            return value.get(key, default)
        return getattr(value, key)
    except Exception:
        return default


def _error_kind(value: object) -> str:
    constructor = _read(value, "constructor_name", None)
    name = _read(value, "name", None)
    labels = {item for item in (constructor, name) if isinstance(item, str)}
    if "ConfigFileError" in labels:
        return "config_file_error"
    if "ValidationError" in labels:
        return "validation_error"
    if "CordisError" in labels:
        return "cordis_error"
    if "AggregateError" in labels:
        return "aggregate_error"
    if "TypeError" in labels:
        return "type_error"
    if "Error" in labels:
        return "error"
    return "unknown"


def _code_coordinate(value: object) -> str:
    code = _read(value, "code", _MISSING)
    if code is _MISSING or code is None:
        return "none"
    if isinstance(code, str) and code in CODE_COORDINATES - {"none", "unrecognized"}:
        return code
    return "unrecognized"


def _config_stage(value: object, kind: str) -> str:
    if kind != "config_file_error":
        return "none"
    stage = _read(value, "stage", _MISSING)
    return stage if isinstance(stage, str) and stage in CONFIG_STAGES - {"none"} else "none"


def _message_coordinate(value: object) -> str:
    message = _read(value, "message", _MISSING)
    if not isinstance(message, str):
        return "none"
    if "host preparation failed" in message:
        return "host_preparation_failed"
    if "plugin tree failed to load" in message:
        return "plugin_tree_failed_to_load"
    if "plugin(s) failed to load" in message:
        return "plugins_failed_to_load"
    if " entry did not activate" in message or " entries did not activate" in message:
        return "entries_did_not_activate"
    return "none"


def _aggregate_shape(value: object, kind: str) -> str:
    if kind != "aggregate_error":
        return "none"
    errors = _read(value, "errors", _MISSING)
    if not isinstance(errors, list):
        return "unreadable"
    if not errors:
        return "zero"
    if len(errors) == 1:
        return "one"
    return "multiple"


def sanitize_error_fixture(value: object) -> dict[str, Any]:
    """Model the wrapper projection without executing Node or reading raw evidence."""

    nodes: list[dict[str, Any]] = []
    seen: set[int] = set()
    cursor = value
    cycle = False
    truncated = False
    for position in range(MAX_CAUSE_NODES):
        identity = id(cursor)
        if identity in seen:
            cycle = True
            break
        seen.add(identity)
        kind = _error_kind(cursor)
        nodes.append(
            {
                "position": position,
                "error_kind": kind,
                "code_coordinate": _code_coordinate(cursor),
                "config_stage": _config_stage(cursor, kind),
                "message_coordinate": _message_coordinate(cursor),
                "aggregate_shape": _aggregate_shape(cursor, kind),
            }
        )
        cause = _read(cursor, "cause", _MISSING)
        if cause is _MISSING:
            break
        if id(cause) in seen:
            cycle = True
            break
        if position == MAX_CAUSE_NODES - 1:
            truncated = True
            break
        cursor = cause
    return {
        "cause_chain": nodes,
        "cause_chain_cycle_detected": cycle,
        "cause_chain_truncated": truncated,
    }


def build_diagnostic_from_fixture(
    value: object,
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
) -> dict[str, Any]:
    operation_id = _identifier(operation_id, "operation_id")
    attempt_id = _identifier(attempt_id, "attempt_id")
    if not isinstance(candidate_source, str) or _FULL_OID.fullmatch(candidate_source) is None:
        raise StructuredDiagnosticError("candidate_source_invalid")
    diagnostic = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": operation_id,
        "attempt_id": attempt_id,
        "candidate_source": candidate_source,
        "phase": PHASE,
        **sanitize_error_fixture(value),
        "raw_error_message_retained": False,
        "raw_stack_retained": False,
        "raw_paths_retained": False,
    }
    return validate_structured_diagnostic(diagnostic)


def validate_structured_diagnostic(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "operation_id",
        "attempt_id",
        "candidate_source",
        "phase",
        "cause_chain",
        "cause_chain_cycle_detected",
        "cause_chain_truncated",
        "raw_error_message_retained",
        "raw_stack_retained",
        "raw_paths_retained",
    }:
        raise StructuredDiagnosticError("diagnostic_keys_invalid")
    if value["schema_version"] != SCHEMA_VERSION or value["phase"] != PHASE:
        raise StructuredDiagnosticError("diagnostic_identity_invalid")
    _identifier(value["operation_id"], "operation_id")
    _identifier(value["attempt_id"], "attempt_id")
    if not isinstance(value["candidate_source"], str) or _FULL_OID.fullmatch(
        value["candidate_source"]
    ) is None:
        raise StructuredDiagnosticError("candidate_source_invalid")
    if any(
        value[field] is not False
        for field in (
            "raw_error_message_retained",
            "raw_stack_retained",
            "raw_paths_retained",
        )
    ):
        raise StructuredDiagnosticError("raw_retention_invalid")
    if not isinstance(value["cause_chain_cycle_detected"], bool) or not isinstance(
        value["cause_chain_truncated"], bool
    ):
        raise StructuredDiagnosticError("chain_flags_invalid")
    chain = value["cause_chain"]
    if not isinstance(chain, list) or not 1 <= len(chain) <= MAX_CAUSE_NODES:
        raise StructuredDiagnosticError("cause_chain_length_invalid")
    for position, node in enumerate(chain):
        if not isinstance(node, dict) or set(node) != {
            "position",
            "error_kind",
            "code_coordinate",
            "config_stage",
            "message_coordinate",
            "aggregate_shape",
        }:
            raise StructuredDiagnosticError("cause_node_keys_invalid")
        if (
            node["position"] != position
            or node["error_kind"] not in ERROR_KINDS
            or node["code_coordinate"] not in CODE_COORDINATES
            or node["config_stage"] not in CONFIG_STAGES
            or node["message_coordinate"] not in MESSAGE_COORDINATES
            or node["aggregate_shape"] not in AGGREGATE_SHAPES
        ):
            raise StructuredDiagnosticError("cause_node_coordinate_invalid")
        if node["error_kind"] != "config_file_error" and node["config_stage"] != "none":
            raise StructuredDiagnosticError("config_stage_relationship_invalid")
        if node["error_kind"] != "aggregate_error" and node["aggregate_shape"] != "none":
            raise StructuredDiagnosticError("aggregate_shape_relationship_invalid")
    if value["cause_chain_cycle_detected"] and value["cause_chain_truncated"]:
        raise StructuredDiagnosticError("chain_terminal_flags_ambiguous")
    return value


def diagnostic_bytes(value: object) -> bytes:
    diagnostic = validate_structured_diagnostic(value)
    payload = (json.dumps(diagnostic, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(payload) > MAX_SIDECAR_BYTES:
        raise StructuredDiagnosticError("diagnostic_size_exceeded")
    return payload


def read_structured_diagnostic(
    path: Path,
    *,
    disposable_root: Path,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
) -> dict[str, Any]:
    if not path.is_absolute() or not disposable_root.is_absolute():
        raise StructuredDiagnosticError("diagnostic_paths_must_be_absolute")
    if disposable_root.is_symlink() or not disposable_root.is_dir() or path.is_symlink():
        raise StructuredDiagnosticError("diagnostic_path_invalid")
    resolved_root = disposable_root.resolve()
    resolved_path = path.resolve(strict=True)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise StructuredDiagnosticError("diagnostic_path_outside_disposable_root") from error
    if not resolved_path.is_file() or resolved_path.stat().st_size > MAX_SIDECAR_BYTES:
        raise StructuredDiagnosticError("diagnostic_file_invalid")
    try:
        value = json.loads(resolved_path.read_bytes())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise StructuredDiagnosticError("diagnostic_json_invalid") from error
    diagnostic = validate_structured_diagnostic(value)
    if (
        diagnostic["operation_id"] != operation_id
        or diagnostic["attempt_id"] != attempt_id
        or diagnostic["candidate_source"] != candidate_source
    ):
        raise StructuredDiagnosticError("diagnostic_runtime_identity_mismatch")
    if resolved_path.read_bytes() != diagnostic_bytes(diagnostic):
        raise StructuredDiagnosticError("diagnostic_canonical_bytes_required")
    return diagnostic


def build_entrypoint_wrapper_source(
    *,
    package_root: Path,
    wrapper_path: Path,
    diagnostic_path: Path,
    disposable_root: Path,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
) -> bytes:
    operation_id = _identifier(operation_id, "operation_id")
    attempt_id = _identifier(attempt_id, "attempt_id")
    if not isinstance(candidate_source, str) or _FULL_OID.fullmatch(candidate_source) is None:
        raise StructuredDiagnosticError("candidate_source_invalid")
    paths = (package_root, wrapper_path, diagnostic_path, disposable_root)
    if any(not path.is_absolute() for path in paths):
        raise StructuredDiagnosticError("wrapper_paths_must_be_absolute")
    resolved_root = disposable_root.resolve()
    resolved_package = package_root.resolve(strict=True)
    entrypoint = (resolved_package / "lib" / "bin.js").resolve(strict=True)
    if entrypoint.parent != resolved_package / "lib":
        raise StructuredDiagnosticError("entrypoint_path_invalid")
    for label, path in (("wrapper", wrapper_path), ("diagnostic", diagnostic_path)):
        resolved = path.parent.resolve() / path.name
        try:
            resolved.relative_to(resolved_root)
        except ValueError as error:
            raise StructuredDiagnosticError(f"{label}_path_outside_disposable_root") from error
    known_codes = sorted(CODE_COORDINATES - {"none", "unrecognized"})
    source = f'''import {{ closeSync, fsyncSync, openSync, writeFileSync }} from "node:fs";

const SCHEMA_VERSION = {json.dumps(SCHEMA_VERSION)};
const OPERATION_ID = {json.dumps(operation_id)};
const ATTEMPT_ID = {json.dumps(attempt_id)};
const CANDIDATE_SOURCE = {json.dumps(candidate_source)};
const ENTRYPOINT_URL = {json.dumps(entrypoint.as_uri())};
const DIAGNOSTIC_PATH = {json.dumps(str(diagnostic_path))};
const MAX_CAUSE_NODES = {MAX_CAUSE_NODES};
const KNOWN_CODES = new Set({json.dumps(known_codes)});

function safeRead(reader, fallback) {{
  try {{ return reader(); }} catch {{ return fallback; }}
}}

function errorKind(value) {{
  const constructorName = safeRead(() => value?.constructor?.name, null);
  const name = safeRead(() => value?.name, null);
  const labels = new Set([constructorName, name]);
  if (labels.has("ConfigFileError")) return "config_file_error";
  if (labels.has("ValidationError")) return "validation_error";
  if (labels.has("CordisError")) return "cordis_error";
  if (labels.has("AggregateError")) return "aggregate_error";
  if (labels.has("TypeError")) return "type_error";
  if (labels.has("Error")) return "error";
  return "unknown";
}}

function codeCoordinate(value) {{
  const code = safeRead(() => value?.code, undefined);
  if (code === undefined || code === null) return "none";
  return typeof code === "string" && KNOWN_CODES.has(code) ? code : "unrecognized";
}}

function configStage(value, kind) {{
  if (kind !== "config_file_error") return "none";
  const stage = safeRead(() => value?.stage, undefined);
  return stage === "read" || stage === "parse" || stage === "validate" ? stage : "none";
}}

function messageCoordinate(value) {{
  const message = safeRead(() => value?.message, undefined);
  if (typeof message !== "string") return "none";
  if (message.includes("host preparation failed")) return "host_preparation_failed";
  if (message.includes("plugin tree failed to load")) return "plugin_tree_failed_to_load";
  if (message.includes("plugin(s) failed to load")) return "plugins_failed_to_load";
  if (message.includes(" entry did not activate") || message.includes(" entries did not activate")) return "entries_did_not_activate";
  return "none";
}}

function aggregateShape(value, kind) {{
  if (kind !== "aggregate_error") return "none";
  const errors = safeRead(() => value?.errors, undefined);
  if (!Array.isArray(errors)) return "unreadable";
  if (errors.length === 0) return "zero";
  if (errors.length === 1) return "one";
  return "multiple";
}}

function buildDiagnostic(error) {{
  const causeChain = [];
  const seen = new Set();
  let cursor = error;
  let causeChainCycleDetected = false;
  let causeChainTruncated = false;
  for (let position = 0; position < MAX_CAUSE_NODES; position += 1) {{
    if (seen.has(cursor)) {{ causeChainCycleDetected = true; break; }}
    seen.add(cursor);
    const kind = errorKind(cursor);
    causeChain.push({{
      position,
      error_kind: kind,
      code_coordinate: codeCoordinate(cursor),
      config_stage: configStage(cursor, kind),
      message_coordinate: messageCoordinate(cursor),
      aggregate_shape: aggregateShape(cursor, kind),
    }});
    const cause = safeRead(() => cursor?.cause, undefined);
    if (cause === undefined) break;
    if (seen.has(cause)) {{ causeChainCycleDetected = true; break; }}
    if (position === MAX_CAUSE_NODES - 1) {{ causeChainTruncated = true; break; }}
    cursor = cause;
  }}
  return {{
    schema_version: SCHEMA_VERSION,
    operation_id: OPERATION_ID,
    attempt_id: ATTEMPT_ID,
    candidate_source: CANDIDATE_SOURCE,
    phase: "entrypoint_import_rejected",
    cause_chain: causeChain,
    cause_chain_cycle_detected: causeChainCycleDetected,
    cause_chain_truncated: causeChainTruncated,
    raw_error_message_retained: false,
    raw_stack_retained: false,
    raw_paths_retained: false,
  }};
}}

try {{
  await import(ENTRYPOINT_URL);
}} catch (error) {{
  let descriptor;
  try {{
    const payload = JSON.stringify(buildDiagnostic(error)) + "\\n";
    descriptor = openSync(DIAGNOSTIC_PATH, "wx", 0o600);
    writeFileSync(descriptor, payload, "utf8");
    fsyncSync(descriptor);
  }} catch {{
    // Diagnostic failure must never replace the native Harness rejection.
  }} finally {{
    if (descriptor !== undefined) {{ try {{ closeSync(descriptor); }} catch {{}} }}
  }}
  throw error;
}}
'''
    payload = source.encode()
    validate_entrypoint_wrapper_source(payload)
    return payload


def validate_entrypoint_wrapper_source(payload: bytes) -> dict[str, Any]:
    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise StructuredDiagnosticError("wrapper_utf8_invalid") from error
    checks = {
        "single_entrypoint_import": source.count("await import(ENTRYPOINT_URL)") == 1,
        "single_exclusive_writer": source.count('openSync(DIAGNOSTIC_PATH, "wx"') == 1,
        "single_identical_rethrow": source.count("throw error;") == 1,
        "bounded_cause_chain": f"const MAX_CAUSE_NODES = {MAX_CAUSE_NODES};" in source,
        "no_process_exit": "process.exit" not in source,
        "no_stack_property_read": ".stack" not in source,
        "no_network_module": "node:http" not in source and "node:https" not in source,
        "raw_retention_false": all(
            f"{field}: false" in source
            for field in (
                "raw_error_message_retained",
                "raw_stack_retained",
                "raw_paths_retained",
            )
        ),
    }
    if not all(checks.values()):
        raise StructuredDiagnosticError("wrapper_source_shape_invalid")
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "checks": checks,
    }


def build_launch_command(
    *, node_executable: str, wrapper_path: Path, profile: str, task: str
) -> list[str]:
    if not node_executable or not wrapper_path.is_absolute() or profile != "headless":
        raise StructuredDiagnosticError("launch_command_input_invalid")
    if not isinstance(task, str) or not task:
        raise StructuredDiagnosticError("launch_task_invalid")
    return [
        node_executable,
        "--expose-internals",
        str(wrapper_path),
        "--profile",
        profile,
        task,
    ]


def build_structured_pre_hmr_terminal(
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    native_process_started: bool,
    exit_code: int | None,
    controller_coordinate: str,
    hmr_events: Sequence[str],
    stdout: dict[str, Any],
    stderr: dict[str, Any],
    structured_diagnostic: dict[str, Any],
) -> dict[str, Any]:
    """Build v2 without changing the accepted v1 component or its evidence."""

    legacy = legacy_terminal.build_pre_hmr_terminal(
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
        native_process_started=native_process_started,
        exit_code=exit_code,
        controller_coordinate=controller_coordinate,
        hmr_events=hmr_events,
        stdout=stdout,
        stderr=stderr,
    )
    safe_diagnostic = validate_structured_diagnostic(structured_diagnostic)
    if (
        safe_diagnostic["operation_id"] != operation_id
        or safe_diagnostic["attempt_id"] != attempt_id
        or safe_diagnostic["candidate_source"] != candidate_source
    ):
        raise StructuredDiagnosticError("structured_terminal_identity_mismatch")
    if (
        legacy["stage"] != "native_process_started_before_first_hmr_event"
        or controller_coordinate != "native_process_exited_nonzero"
        or exit_code is None
        or exit_code == 0
    ):
        raise StructuredDiagnosticError("structured_terminal_runtime_relationship_invalid")
    terminal = {
        **legacy,
        "schema_version": TERMINAL_SCHEMA_VERSION,
        "cause": TERMINAL_CAUSE,
        "matched_signature_groups": [],
        "structured_diagnostic": safe_diagnostic,
    }
    return validate_structured_pre_hmr_terminal(terminal)


def validate_structured_pre_hmr_terminal(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StructuredDiagnosticError("structured_terminal_invalid")
    expected_keys = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "candidate_source",
        "stage",
        "cause",
        "exit_code",
        "controller_coordinate",
        "hmr_event_count",
        "matched_signature_groups",
        "classification_byte_limit_per_stream",
        "stdout",
        "stderr",
        "raw_streams_retained",
        "structured_diagnostic",
    }
    if set(value) != expected_keys or value["schema_version"] != TERMINAL_SCHEMA_VERSION:
        raise StructuredDiagnosticError("structured_terminal_keys_or_schema_invalid")
    if value["cause"] != TERMINAL_CAUSE or value["matched_signature_groups"] != []:
        raise StructuredDiagnosticError("structured_terminal_cause_invalid")
    diagnostic = validate_structured_diagnostic(value["structured_diagnostic"])
    if (
        diagnostic["operation_id"] != value["operation_id"]
        or diagnostic["attempt_id"] != value["attempt_id"]
        or diagnostic["candidate_source"] != value["candidate_source"]
    ):
        raise StructuredDiagnosticError("structured_terminal_identity_mismatch")
    if (
        value["stage"] != "native_process_started_before_first_hmr_event"
        or value["controller_coordinate"] != "native_process_exited_nonzero"
        or value["exit_code"] is None
        or value["exit_code"] == 0
    ):
        raise StructuredDiagnosticError("structured_terminal_runtime_relationship_invalid")
    stream_limit = any(
        value[label]["byte_count"] > legacy_terminal.MAX_CLASSIFICATION_BYTES
        for label in ("stdout", "stderr")
    )
    legacy_projection = {
        key: nested
        for key, nested in value.items()
        if key != "structured_diagnostic"
    }
    legacy_projection["schema_version"] = legacy_terminal.SCHEMA_VERSION
    legacy_projection["cause"] = (
        "startup_stream_limit_exceeded" if stream_limit else "unclassified_nonzero_exit"
    )
    try:
        legacy_terminal.validate_pre_hmr_terminal(legacy_projection)
    except legacy_terminal.StartupTerminalError as error:
        raise StructuredDiagnosticError("structured_terminal_legacy_shape_invalid") from error
    return value


def structured_terminal_bytes(value: object) -> bytes:
    terminal = validate_structured_pre_hmr_terminal(value)
    return (json.dumps(terminal, sort_keys=True, indent=2) + "\n").encode()


def future_controller_binding_envelope_source() -> bytes:
    """Freeze the future-only ordering without mutating a consumed controller."""

    return b'''wrapper = build_entrypoint_wrapper_source(...)
write_wrapper_inside_exact_disposable_root(wrapper)
command = build_launch_command(wrapper_path=exact_wrapper_path, ...)
process = launch_exactly_one_native_process(command)
wait_for_exit_or_first_hmr_event(process)
diagnostic = read_structured_diagnostic_before_cleanup(exact_sidecar_path)
terminal = build_structured_pre_hmr_terminal(structured_diagnostic=diagnostic, ...)
write_pre_hmr_terminal_exclusive_outside_disposable_root(terminal)
remove_exact_disposable_root()
'''


def validate_future_controller_binding_envelope(payload: bytes) -> dict[str, Any]:
    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise StructuredDiagnosticError("controller_envelope_utf8_invalid") from error
    coordinates = [
        "build_entrypoint_wrapper_source(",
        "build_launch_command(",
        "launch_exactly_one_native_process(",
        "read_structured_diagnostic_before_cleanup(",
        "build_structured_pre_hmr_terminal(",
        "write_pre_hmr_terminal_exclusive_outside_disposable_root(",
        "remove_exact_disposable_root()",
    ]
    positions = [source.index(coordinate) for coordinate in coordinates]
    checks = {
        "exact_order": positions == sorted(positions),
        "single_process_launch": source.count("launch_exactly_one_native_process(") == 1,
        "single_wrapper_build": source.count("build_entrypoint_wrapper_source(") == 1,
        "single_safe_terminal_write": source.count(
            "write_pre_hmr_terminal_exclusive_outside_disposable_root("
        )
        == 1,
        "cleanup_last": source.rstrip().endswith("remove_exact_disposable_root()"),
        "no_retry": "retry" not in source.lower(),
    }
    if not all(checks.values()):
        raise StructuredDiagnosticError("controller_envelope_invalid")
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "checks": checks,
    }

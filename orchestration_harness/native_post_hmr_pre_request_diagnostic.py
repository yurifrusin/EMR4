"""Closed post-HMR coordinates for native-Harness runner failures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


SCHEMA_VERSION = "ariadne.native_harness_post_hmr_pre_request_diagnostic.v1"
MAX_SIDECAR_BYTES = 4_096
PRE_REQUEST_STAGES = (
    "loader_readiness_wait",
    "required_service_lookup",
    "preset_root_roster_admission",
    "agent_create_setup_publish",
    "initial_idle_wait",
    "first_followup_dispatch",
    "first_turn_idle_wait",
)
CAUSE_COORDINATES = (
    "operation_rejected",
    "required_service_missing",
    "preset_root_roster_mismatch",
)
ERROR_KINDS = (
    "aggregate_error",
    "error",
    "invalid_preset_id_error",
    "preset_mount_error",
    "type_error",
    "unknown",
    "unknown_preset_error",
)
_FULL_OID = re.compile(r"^[0-9a-f]{40}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")


class PostHmrDiagnosticError(ValueError):
    """The closed diagnostic contract was not satisfied."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise PostHmrDiagnosticError(f"{label}_invalid")
    return value


def _safe_label(value: object, key: str) -> str | None:
    try:
        if isinstance(value, Mapping):
            label = value.get(key)
        else:
            label = getattr(value, key)
    except Exception:
        return None
    return label if isinstance(label, str) else None


def error_kind_from_fixture(value: object) -> str:
    """Project only a closed constructor/name identity from a test fixture."""

    labels = {
        label
        for label in (
            _safe_label(value, "constructor_name"),
            _safe_label(value, "name"),
        )
        if label is not None
    }
    mapping = {
        "InvalidPresetIdError": "invalid_preset_id_error",
        "PresetMountError": "preset_mount_error",
        "UnknownPresetError": "unknown_preset_error",
        "AggregateError": "aggregate_error",
        "TypeError": "type_error",
        "Error": "error",
    }
    for label, coordinate in mapping.items():
        if label in labels:
            return coordinate
    return "unknown"


def build_diagnostic_from_fixture(
    value: object,
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    stage: str,
    cause_coordinate: str = "operation_rejected",
) -> dict[str, Any]:
    _identifier(operation_id, "operation_id")
    _identifier(attempt_id, "attempt_id")
    if not isinstance(candidate_source, str) or _FULL_OID.fullmatch(candidate_source) is None:
        raise PostHmrDiagnosticError("candidate_source_invalid")
    diagnostic = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": operation_id,
        "attempt_id": attempt_id,
        "candidate_source": candidate_source,
        "stage": stage,
        "cause_coordinate": cause_coordinate,
        "error_kind": error_kind_from_fixture(value),
        "raw_error_message_retained": False,
        "raw_stack_retained": False,
        "raw_paths_retained": False,
        "raw_cause_retained": False,
    }
    return validate_diagnostic(diagnostic)


def validate_diagnostic(value: object) -> dict[str, Any]:
    expected_keys = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "candidate_source",
        "stage",
        "cause_coordinate",
        "error_kind",
        "raw_error_message_retained",
        "raw_stack_retained",
        "raw_paths_retained",
        "raw_cause_retained",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise PostHmrDiagnosticError("diagnostic_keys_invalid")
    if value["schema_version"] != SCHEMA_VERSION:
        raise PostHmrDiagnosticError("diagnostic_schema_invalid")
    _identifier(value["operation_id"], "operation_id")
    _identifier(value["attempt_id"], "attempt_id")
    if not isinstance(value["candidate_source"], str) or _FULL_OID.fullmatch(
        value["candidate_source"]
    ) is None:
        raise PostHmrDiagnosticError("candidate_source_invalid")
    if value["stage"] not in PRE_REQUEST_STAGES:
        raise PostHmrDiagnosticError("stage_invalid")
    if value["cause_coordinate"] not in CAUSE_COORDINATES:
        raise PostHmrDiagnosticError("cause_coordinate_invalid")
    if value["error_kind"] not in ERROR_KINDS:
        raise PostHmrDiagnosticError("error_kind_invalid")
    if (
        value["cause_coordinate"] == "required_service_missing"
        and value["stage"] != "required_service_lookup"
    ):
        raise PostHmrDiagnosticError("service_cause_stage_mismatch")
    if (
        value["cause_coordinate"] == "preset_root_roster_mismatch"
        and value["stage"] != "preset_root_roster_admission"
    ):
        raise PostHmrDiagnosticError("roster_cause_stage_mismatch")
    raw_flags = (
        "raw_error_message_retained",
        "raw_stack_retained",
        "raw_paths_retained",
        "raw_cause_retained",
    )
    if any(value[field] is not False for field in raw_flags):
        raise PostHmrDiagnosticError("raw_retention_invalid")
    return value


def diagnostic_bytes(value: object) -> bytes:
    diagnostic = validate_diagnostic(value)
    payload = (json.dumps(diagnostic, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(payload) > MAX_SIDECAR_BYTES:
        raise PostHmrDiagnosticError("diagnostic_size_exceeded")
    return payload


def read_diagnostic(
    path: Path,
    *,
    disposable_root: Path,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
) -> dict[str, Any]:
    if not path.is_absolute() or not disposable_root.is_absolute():
        raise PostHmrDiagnosticError("diagnostic_paths_must_be_absolute")
    if disposable_root.is_symlink() or not disposable_root.is_dir() or path.is_symlink():
        raise PostHmrDiagnosticError("diagnostic_path_invalid")
    resolved_root = disposable_root.resolve()
    resolved_path = path.resolve(strict=True)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise PostHmrDiagnosticError("diagnostic_path_outside_disposable_root") from error
    if not resolved_path.is_file() or resolved_path.stat().st_size > MAX_SIDECAR_BYTES:
        raise PostHmrDiagnosticError("diagnostic_file_invalid")
    try:
        payload = resolved_path.read_bytes()
        value = json.loads(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PostHmrDiagnosticError("diagnostic_json_invalid") from error
    diagnostic = validate_diagnostic(value)
    if (
        diagnostic["operation_id"] != operation_id
        or diagnostic["attempt_id"] != attempt_id
        or diagnostic["candidate_source"] != candidate_source
    ):
        raise PostHmrDiagnosticError("diagnostic_runtime_identity_mismatch")
    if payload != diagnostic_bytes(diagnostic):
        raise PostHmrDiagnosticError("diagnostic_canonical_bytes_required")
    return diagnostic


def build_helper_source(
    *, operation_id: str, attempt_id: str, candidate_source: str
) -> bytes:
    _identifier(operation_id, "operation_id")
    _identifier(attempt_id, "attempt_id")
    if not isinstance(candidate_source, str) or _FULL_OID.fullmatch(candidate_source) is None:
        raise PostHmrDiagnosticError("candidate_source_invalid")
    source = f'''import {{ closeSync, fsyncSync, openSync, writeFileSync }} from "node:fs";

const SCHEMA_VERSION = {json.dumps(SCHEMA_VERSION)};
const OPERATION_ID = {json.dumps(operation_id)};
const ATTEMPT_ID = {json.dumps(attempt_id)};
const CANDIDATE_SOURCE = {json.dumps(candidate_source)};
export const PRE_REQUEST_STAGES = Object.freeze({json.dumps(list(PRE_REQUEST_STAGES))});
export const CAUSE_COORDINATES = Object.freeze({json.dumps(list(CAUSE_COORDINATES))});
export const ERROR_KINDS = Object.freeze({json.dumps(list(ERROR_KINDS))});
const STAGE_SET = new Set(PRE_REQUEST_STAGES);
const CAUSE_SET = new Set(CAUSE_COORDINATES);

function safeRead(reader) {{ try {{ return reader(); }} catch {{ return null; }} }}
function errorKind(error) {{
  const labels = new Set([safeRead(() => error?.constructor?.name), safeRead(() => error?.name)]);
  if (labels.has("InvalidPresetIdError")) return "invalid_preset_id_error";
  if (labels.has("PresetMountError")) return "preset_mount_error";
  if (labels.has("UnknownPresetError")) return "unknown_preset_error";
  if (labels.has("AggregateError")) return "aggregate_error";
  if (labels.has("TypeError")) return "type_error";
  if (labels.has("Error")) return "error";
  return "unknown";
}}
function canonicalize(value) {{
  if (Array.isArray(value)) return value.map((item) => canonicalize(item));
  if (value !== null && typeof value === "object") {{
    const result = {{}};
    for (const key of Object.keys(value).sort()) result[key] = canonicalize(value[key]);
    return result;
  }}
  return value;
}}
export function writePostHmrDiagnostic(path, stage, causeCoordinate, error) {{
  let descriptor;
  try {{
    if (!STAGE_SET.has(stage) || !CAUSE_SET.has(causeCoordinate)) return false;
    if (causeCoordinate === "required_service_missing" && stage !== "required_service_lookup") return false;
    if (causeCoordinate === "preset_root_roster_mismatch" && stage !== "preset_root_roster_admission") return false;
    const diagnostic = {{
      schema_version: SCHEMA_VERSION,
      operation_id: OPERATION_ID,
      attempt_id: ATTEMPT_ID,
      candidate_source: CANDIDATE_SOURCE,
      stage,
      cause_coordinate: causeCoordinate,
      error_kind: errorKind(error),
      raw_error_message_retained: false,
      raw_stack_retained: false,
      raw_paths_retained: false,
      raw_cause_retained: false,
    }};
    const payload = JSON.stringify(canonicalize(diagnostic)) + "\\n";
    descriptor = openSync(path, "wx", 0o600);
    writeFileSync(descriptor, payload, "utf8");
    fsyncSync(descriptor);
    return true;
  }} catch {{
    return false;
  }} finally {{
    if (descriptor !== undefined) {{ try {{ closeSync(descriptor); }} catch {{}} }}
  }}
}}
'''
    payload = source.encode()
    validate_helper_source(payload)
    return payload


def validate_helper_source(payload: bytes) -> dict[str, Any]:
    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise PostHmrDiagnosticError("helper_utf8_invalid") from error
    forbidden = (
        ".message",
        ".stack",
        ".cause",
        "error?.code",
        "process.env",
        "node:http",
        "node:https",
        "fetch(",
        "process.exit",
    )
    checks = {
        "one_exclusive_writer": source.count('openSync(path, "wx"') == 1,
        "one_canonical_serializer": source.count("Object.keys(value).sort()") == 1,
        "one_safe_export": source.count("export function writePostHmrDiagnostic(") == 1,
        "exact_stage_vocabulary": json.dumps(list(PRE_REQUEST_STAGES)) in source,
        "exact_cause_vocabulary": json.dumps(list(CAUSE_COORDINATES)) in source,
        "exact_error_vocabulary": json.dumps(list(ERROR_KINDS)) in source,
        "raw_retention_false": all(
            f"{field}: false" in source
            for field in (
                "raw_error_message_retained",
                "raw_stack_retained",
                "raw_paths_retained",
                "raw_cause_retained",
            )
        ),
        "no_raw_or_execution_surface": all(token not in source for token in forbidden),
    }
    if not all(checks.values()):
        raise PostHmrDiagnosticError("helper_source_shape_invalid")
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "checks": checks,
    }


def future_runner_instrumentation_envelope_source() -> bytes:
    """Freeze stage ownership without mutating the accepted attempt-005 runner."""

    return b'''let agent;
let sessions;
let failureStage = "loader_readiness_wait";
let causeCoordinate = "operation_rejected";
try {
  await ctx.get("loader")?.await();
  failureStage = "required_service_lookup";
  const agents = ctx.get("agents");
  sessions = ctx.get("sessions");
  const presets = ctx.get("agentPresets");
  if (!agents || !sessions || !presets) { causeCoordinate = "required_service_missing"; throw new Error("REQUIRED_SERVICE_MISSING"); }
  failureStage = "preset_root_roster_admission";
  causeCoordinate = "operation_rejected";
  if (!exactPresetRootRoster(presets, config)) { causeCoordinate = "preset_root_roster_mismatch"; throw new Error("PRESET_ROOT_ROSTER_MISMATCH"); }
  failureStage = "agent_create_setup_publish";
  causeCoordinate = "operation_rejected";
  ({ agent } = await agents.create({ setup: acceptedSetup }));
  failureStage = "initial_idle_wait";
  await agent.whenIdle();
  failureStage = "first_followup_dispatch";
  agent.followup(acceptedMessage);
  failureStage = "first_turn_idle_wait";
  await agent.whenIdle();
} catch (error) {
  writePostHmrDiagnostic(config.diagnosticPath, failureStage, causeCoordinate, error);
  throw error;
}
await sessions.flush(agent.session);
'''


def validate_future_runner_instrumentation_envelope(payload: bytes) -> dict[str, Any]:
    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise PostHmrDiagnosticError("runner_envelope_utf8_invalid") from error
    stage_tokens = [f'failureStage = "{stage}"' for stage in PRE_REQUEST_STAGES]
    stage_positions = [source.index(token) for token in stage_tokens]
    operation_tokens = (
        'await ctx.get("loader")?.await()',
        'const agents = ctx.get("agents")',
        "exactPresetRootRoster(presets, config)",
        "await agents.create(",
        "await agent.whenIdle()",
        "agent.followup(",
        "await agent.whenIdle()",
    )
    cursor = 0
    operation_positions: list[int] = []
    for token in operation_tokens:
        position = source.index(token, cursor)
        operation_positions.append(position)
        cursor = position + len(token)
    checks = {
        "outer_lifecycle_bindings": source.startswith(
            'let agent;\nlet sessions;\nlet failureStage = "loader_readiness_wait";'
        ),
        "stage_order_exact": stage_positions == sorted(stage_positions),
        "stage_before_each_operation": all(
            stage < operation for stage, operation in zip(stage_positions, operation_positions)
        ),
        "single_sidecar_write": source.count("writePostHmrDiagnostic(") == 1,
        "single_identical_rethrow": source.count("throw error;") == 1,
        "flush_outside_interval": source.index("await sessions.flush(")
        > source.index("throw error;"),
        "no_retry_or_fallback": all(
            token not in source.lower() for token in ("retry", "resume", "fallback")
        ),
        "no_raw_error_projection": all(
            token not in source for token in ("error.message", "error.stack", "error.code")
        ),
    }
    if not all(checks.values()):
        raise PostHmrDiagnosticError("runner_envelope_invalid")
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "checks": checks,
        "stage_positions": dict(zip(PRE_REQUEST_STAGES, stage_positions)),
    }


def validate_source_binding(
    payload: bytes, *, expected_sha256: str, required_fragments: tuple[bytes, ...]
) -> dict[str, Any]:
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        raise PostHmrDiagnosticError("source_sha256_mismatch")
    fragment_counts = {
        fragment.decode("utf-8"): payload.count(fragment) for fragment in required_fragments
    }
    if any(count < 1 for count in fragment_counts.values()):
        raise PostHmrDiagnosticError("source_fragment_missing")
    return {
        "sha256": digest,
        "bytes": len(payload),
        "fragment_counts": fragment_counts,
    }


def validate_accepted_runner_source(payload: bytes, *, expected_sha256: str) -> dict[str, Any]:
    fragments = (
        b'await ctx.get("loader")?.await()',
        b'const agents = ctx.get("agents")',
        b'const sessions = ctx.get("sessions")',
        b'const presets = ctx.get("agentPresets")',
        b"presets.roots.length !== 2",
        b"await agents.create(",
        b"await agent.whenIdle()",
        b"agent.followup(",
        b"await sessions.flush(agent.session)",
        b'failure_code: "CUSTOM_RUNNER_FAILURE"',
    )
    binding = validate_source_binding(
        payload, expected_sha256=expected_sha256, required_fragments=fragments
    )
    source = payload.decode("utf-8")
    ordered = (
        'await ctx.get("loader")?.await()',
        'const agents = ctx.get("agents")',
        "presets.roots.length !== 2",
        "await agents.create(",
        "await agent.whenIdle()",
        "agent.followup(",
        "await agent.whenIdle()",
        "await sessions.flush(agent.session)",
    )
    cursor = 0
    positions: list[int] = []
    for token in ordered:
        position = source.index(token, cursor)
        positions.append(position)
        cursor = position + len(token)
    return {**binding, "operation_order": positions, "operation_order_exact": True}

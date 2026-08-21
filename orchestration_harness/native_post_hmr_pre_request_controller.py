"""Provider-free integration of post-HMR diagnostics with broker-zero evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic


BROKER_SCHEMA_VERSION = "ariadne.native_harness_broker_request_reading.v1"
SELECTION_SCHEMA_VERSION = "ariadne.native_harness_post_hmr_selection.v1"
MAX_BROKER_READING_BYTES = 4_096
BROKER_COUNTERS = (
    "request_count",
    "provider_call_started",
    "provider_call_completed",
    "provider_call_failed",
    "request_rejected",
)
COORDINATES = (
    "native_harness_terminal_failure",
    "post_hmr_pre_request_failure",
    "post_hmr_request_boundary_unresolved",
)
HELPER_SPECIFIER = "./post-hmr-pre-request-diagnostic.mjs"
_FULL_OID = re.compile(r"^[0-9a-f]{40}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")


class PostHmrControllerError(ValueError):
    """The future-runner or controller join contract was not satisfied."""


def _identity(value: object, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise PostHmrControllerError(f"{label}_invalid")
    return value


def _candidate_source(value: object) -> str:
    if not isinstance(value, str) or _FULL_OID.fullmatch(value) is None:
        raise PostHmrControllerError("candidate_source_invalid")
    return value


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise PostHmrControllerError(f"runner_marker_{label}_invalid")
    return source.replace(old, new, 1)


def derive_future_runner_source(
    accepted_payload: bytes, *, expected_accepted_sha256: str
) -> bytes:
    """Apply only the closed diagnostic transformations to the accepted runner."""

    diagnostic.validate_accepted_runner_source(
        accepted_payload, expected_sha256=expected_accepted_sha256
    )
    try:
        source = accepted_payload.decode("utf-8")
    except UnicodeError as error:
        raise PostHmrControllerError("accepted_runner_utf8_invalid") from error
    source = _replace_once(
        source,
        'import { assertEffectiveToolComposition } from "./effective-tool-guard.mjs";\n',
        'import { assertEffectiveToolComposition } from "./effective-tool-guard.mjs";\n'
        f'import {{ writePostHmrDiagnostic }} from "{HELPER_SPECIFIER}";\n',
        "helper_import",
    )
    source = _replace_once(
        source,
        'async function run(ctx, config) {\n  await ctx.get("loader")?.await();\n'
        '  const agents = ctx.get("agents");',
        'async function run(ctx, config) {\n'
        '  let failureStage = "loader_readiness_wait";\n'
        '  let causeCoordinate = "operation_rejected";\n'
        '  let diagnosticActive = true;\n'
        '  try {\n'
        '    await ctx.get("loader")?.await();\n'
        '    failureStage = "required_service_lookup";\n'
        '    const agents = ctx.get("agents");',
        "run_preamble",
    )
    source = _replace_once(
        source,
        '  const sessions = ctx.get("sessions");\n'
        '  const presets = ctx.get("agentPresets");\n'
        '  if (!agents || !sessions || !presets) throw new Error("REQUIRED_SERVICE_MISSING");\n'
        '  if (!Array.isArray(presets.roots)',
        '    const sessions = ctx.get("sessions");\n'
        '    const presets = ctx.get("agentPresets");\n'
        '    if (!agents || !sessions || !presets) {\n'
        '      causeCoordinate = "required_service_missing";\n'
        '      throw new Error("REQUIRED_SERVICE_MISSING");\n'
        '    }\n'
        '    failureStage = "preset_root_roster_admission";\n'
        '    causeCoordinate = "operation_rejected";\n'
        '    if (!Array.isArray(presets.roots)',
        "required_services",
    )
    roster_tail = (
        'presets.roots[1].trust !== "user") throw new Error("PRESET_ROOT_ROSTER_MISMATCH");'
    )
    source = _replace_once(
        source,
        roster_tail,
        'presets.roots[1].trust !== "user") {\n'
        '      causeCoordinate = "preset_root_roster_mismatch";\n'
        '      throw new Error("PRESET_ROOT_ROSTER_MISMATCH");\n'
        '    }\n'
        '    failureStage = "agent_create_setup_publish";\n'
        '    causeCoordinate = "operation_rejected";',
        "preset_roster",
    )
    source = _replace_once(
        source,
        '  const { agent } = await agents.create({',
        '    const { agent } = await agents.create({',
        "agent_create_indent",
    )
    source = _replace_once(
        source,
        '  await agent.whenIdle();\n  const firstSeq = agent.session.seq;',
        '    failureStage = "initial_idle_wait";\n'
        '    await agent.whenIdle();\n'
        '    const firstSeq = agent.session.seq;',
        "initial_idle",
    )
    source = _replace_once(
        source,
        '  agent.followup(createUserMessage(',
        '    failureStage = "first_followup_dispatch";\n'
        '    agent.followup(createUserMessage(',
        "followup",
    )
    source = _replace_once(
        source,
        '  await agent.whenIdle();\n  await sessions.flush(agent.session);',
        '    failureStage = "first_turn_idle_wait";\n'
        '    await agent.whenIdle();\n'
        '    diagnosticActive = false;\n'
        '    await sessions.flush(agent.session);',
        "first_turn_idle",
    )
    source = _replace_once(
        source,
        '  ctx.get("appExit")(passed ? 0 : 1);\n}\n\nexport function apply',
        '    ctx.get("appExit")(passed ? 0 : 1);\n'
        '  } catch (error) {\n'
        '    if (diagnosticActive) {\n'
        '      writePostHmrDiagnostic(config.diagnosticPath, failureStage, causeCoordinate, error);\n'
        '    }\n'
        '    throw error;\n'
        '  }\n'
        '}\n\nexport function apply',
        "diagnostic_catch",
    )
    payload = source.encode("utf-8")
    validate_future_runner_source(
        payload,
        accepted_payload=accepted_payload,
        expected_accepted_sha256=expected_accepted_sha256,
    )
    return payload


def validate_future_runner_source(
    payload: bytes,
    *,
    accepted_payload: bytes,
    expected_accepted_sha256: str,
) -> dict[str, Any]:
    """Validate the complete future runner and its reversible derivation."""

    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise PostHmrControllerError("future_runner_utf8_invalid") from error
    accepted_binding = diagnostic.validate_accepted_runner_source(
        accepted_payload, expected_sha256=expected_accepted_sha256
    )
    stage_tokens = [f'failureStage = "{stage}"' for stage in diagnostic.PRE_REQUEST_STAGES]
    try:
        stage_positions = [source.index(token) for token in stage_tokens]
        first_idle = source.index('failureStage = "initial_idle_wait"')
        followup = source.index('failureStage = "first_followup_dispatch"')
        first_turn = source.index('failureStage = "first_turn_idle_wait"')
        interval_closed = source.index("diagnosticActive = false;")
        flush = source.index("await sessions.flush(agent.session);")
    except ValueError as error:
        raise PostHmrControllerError("future_runner_coordinate_missing") from error
    checks = {
        "accepted_runner_bound": accepted_binding["sha256"]
        == expected_accepted_sha256,
        "one_helper_import": source.count(
            f'import {{ writePostHmrDiagnostic }} from "{HELPER_SPECIFIER}";'
        )
        == 1,
        "stage_order_exact": stage_positions == sorted(stage_positions),
        "stage_assignment_exact": all(source.count(token) == 1 for token in stage_tokens),
        "special_causes_exact": source.count(
            'causeCoordinate = "required_service_missing"'
        )
        == 1
        and source.count('causeCoordinate = "preset_root_roster_mismatch"') == 1,
        "one_sidecar_write": source.count("writePostHmrDiagnostic(") == 1,
        "one_identical_rethrow": source.count("throw error;") == 1,
        "interval_closes_after_first_turn": first_idle
        < followup
        < first_turn
        < interval_closed
        < flush,
        "generic_terminal_preserved": source.count(
            'failure_code: "CUSTOM_RUNNER_FAILURE"'
        )
        == 1,
        "accepted_tool_controls_preserved": all(
            token in source
            for token in (
                'Object.freeze(["edit", "glob", "read"])',
                'agentCtx.on("tools/pre-execute"',
                'agentCtx.on("tools/post-execute"',
                "exec.concludeTurn()",
            )
        ),
        "no_retry_resume_fallback": all(
            token not in source.lower() for token in ("retry", "resume", "fallback")
        ),
        "no_raw_error_projection": all(
            token not in source
            for token in ("error.message", "error.stack", "error.code", "error.cause")
        ),
    }
    if not all(checks.values()):
        failed = sorted(key for key, value in checks.items() if not value)
        raise PostHmrControllerError(
            "future_runner_shape_invalid:" + ",".join(failed)
        )
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "accepted_runner_sha256": accepted_binding["sha256"],
        "stage_positions": dict(zip(diagnostic.PRE_REQUEST_STAGES, stage_positions)),
        "checks": checks,
    }


def validate_broker_reading(value: object) -> dict[str, Any]:
    expected_keys = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "candidate_source",
        *BROKER_COUNTERS,
        "raw_broker_stream_retained",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise PostHmrControllerError("broker_reading_keys_invalid")
    if value["schema_version"] != BROKER_SCHEMA_VERSION:
        raise PostHmrControllerError("broker_reading_schema_invalid")
    _identity(value["operation_id"], "operation_id")
    _identity(value["attempt_id"], "attempt_id")
    _candidate_source(value["candidate_source"])
    if any(type(value[key]) is not int or value[key] < 0 for key in BROKER_COUNTERS):
        raise PostHmrControllerError("broker_counter_invalid")
    if value["raw_broker_stream_retained"] is not False:
        raise PostHmrControllerError("broker_raw_retention_invalid")
    return value


def broker_reading_bytes(value: object) -> bytes:
    reading = validate_broker_reading(value)
    payload = (json.dumps(reading, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(payload) > MAX_BROKER_READING_BYTES:
        raise PostHmrControllerError("broker_reading_size_exceeded")
    return payload


def build_broker_reading(
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    counters: dict[str, int] | None = None,
) -> dict[str, Any]:
    supplied = counters or {}
    if set(supplied).difference(BROKER_COUNTERS):
        raise PostHmrControllerError("broker_counter_keys_invalid")
    return validate_broker_reading(
        {
            "schema_version": BROKER_SCHEMA_VERSION,
            "operation_id": operation_id,
            "attempt_id": attempt_id,
            "candidate_source": candidate_source,
            **{key: supplied.get(key, 0) for key in BROKER_COUNTERS},
            "raw_broker_stream_retained": False,
        }
    )


def _read_contained(path: Path, *, disposable_root: Path) -> bytes:
    if not path.is_absolute() or not disposable_root.is_absolute():
        raise PostHmrControllerError("broker_paths_must_be_absolute")
    if disposable_root.is_symlink() or not disposable_root.is_dir() or path.is_symlink():
        raise PostHmrControllerError("broker_path_invalid")
    root = disposable_root.resolve()
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise PostHmrControllerError("broker_path_outside_disposable_root") from error
    if not resolved.is_file() or resolved.stat().st_size > MAX_BROKER_READING_BYTES:
        raise PostHmrControllerError("broker_file_invalid")
    return resolved.read_bytes()


def read_broker_reading(
    path: Path,
    *,
    disposable_root: Path,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
) -> dict[str, Any]:
    payload = _read_contained(path, disposable_root=disposable_root)
    try:
        value = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PostHmrControllerError("broker_json_invalid") from error
    reading = validate_broker_reading(value)
    if (
        reading["operation_id"] != operation_id
        or reading["attempt_id"] != attempt_id
        or reading["candidate_source"] != candidate_source
    ):
        raise PostHmrControllerError("broker_runtime_identity_mismatch")
    if payload != broker_reading_bytes(reading):
        raise PostHmrControllerError("broker_canonical_bytes_required")
    return reading


def select_post_hmr_failure(
    *,
    diagnostic_path: Path,
    broker_reading_path: Path,
    disposable_root: Path,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
) -> dict[str, Any]:
    """Join canonical sidecar and broker evidence without reading raw streams."""

    broker = read_broker_reading(
        broker_reading_path,
        disposable_root=disposable_root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
    )
    broker_zero = all(broker[key] == 0 for key in BROKER_COUNTERS)
    try:
        sidecar = diagnostic.read_diagnostic(
            diagnostic_path,
            disposable_root=disposable_root,
            operation_id=operation_id,
            attempt_id=attempt_id,
            candidate_source=candidate_source,
        )
    except (diagnostic.PostHmrDiagnosticError, OSError):
        sidecar = None
    accepted = sidecar is not None
    if not accepted:
        coordinate = "native_harness_terminal_failure"
    elif broker_zero:
        coordinate = "post_hmr_pre_request_failure"
    else:
        coordinate = "post_hmr_request_boundary_unresolved"
    result = {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "coordinate": coordinate,
        "diagnostic_accepted": accepted,
        "broker_zero": broker_zero,
        "pre_request_supported": accepted and broker_zero,
        "stage": sidecar["stage"] if sidecar else None,
        "cause_coordinate": sidecar["cause_coordinate"] if sidecar else None,
        "error_kind": sidecar["error_kind"] if sidecar else None,
        "raw_stream_read": False,
    }
    if result["coordinate"] not in COORDINATES:
        raise PostHmrControllerError("selection_coordinate_invalid")
    return result

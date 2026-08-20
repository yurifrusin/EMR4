"""Fail-closed sanitized terminals for native-Harness pre-HMR startup failures."""

from __future__ import annotations

from collections.abc import Sequence
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, BinaryIO


SCHEMA_VERSION = "ariadne.native_harness_pre_hmr_startup_terminal.v1"
MAX_CLASSIFICATION_BYTES = 65_536
STREAM_CHUNK_BYTES = 16_384
STAGES = frozenset(
    {
        "native_process_creation",
        "native_process_started_before_first_hmr_event",
    }
)
CAUSES = frozenset(
    {
        "node_runtime_contract_rejected",
        "package_entrypoint_load_failed",
        "profile_load_or_validation_failed",
        "module_resolution_failed",
        "required_service_unavailable",
        "hmr_bootstrap_failed",
        "operating_system_process_failure",
        "controller_startup_exception",
        "startup_stream_limit_exceeded",
        "ambiguous_startup_signatures",
        "unclassified_nonzero_exit",
    }
)
CONTROLLER_COORDINATES = frozenset(
    {
        "native_process_creation_failed",
        "native_process_exited_nonzero",
        "native_worker_timeout",
        "unexpected_controller_failure",
    }
)
SIGNATURE_GROUPS: dict[str, tuple[bytes, ...]] = {
    "node_runtime_contract_rejected": (
        b"err_unknown_builtin_module",
        b"unknown builtin module",
        b"--expose-internals",
    ),
    "package_entrypoint_load_failed": (
        b"err_package_path_not_exported",
        b"cannot find package '@deepseek-ai/dsh'",
        b"package entrypoint load failed",
    ),
    "profile_load_or_validation_failed": (
        b"profile validation failed",
        b"profile not found",
        b"yamlparseerror",
        b"cordis.patch.yml",
    ),
    "module_resolution_failed": (
        b"err_module_not_found",
        b"cannot find module",
        b"module not found",
    ),
    "required_service_unavailable": (
        b"services_unavailable",
        b"required service unavailable",
        b"no provider for",
        b"dependency injection failed",
    ),
    "hmr_bootstrap_failed": (
        b"hmr unavailable",
        b"hmr bootstrap failed",
        b"hot module replacement failed",
    ),
}
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")
_FULL_OID = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class StartupTerminalError(ValueError):
    """A pre-HMR startup terminal invariant failed closed."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise StartupTerminalError(f"{label}_invalid")
    return value


def _stream_projection(reading: dict[str, Any]) -> dict[str, Any]:
    if set(reading) != {
        "byte_count",
        "sha256",
        "classification_bytes",
        "limit_exceeded",
    }:
        raise StartupTerminalError("stream_reading_keys_invalid")
    byte_count = reading["byte_count"]
    digest = reading["sha256"]
    sample = reading["classification_bytes"]
    limit_exceeded = reading["limit_exceeded"]
    if (
        isinstance(byte_count, bool)
        or not isinstance(byte_count, int)
        or byte_count < 0
        or not isinstance(digest, str)
        or _DIGEST.fullmatch(digest) is None
        or not isinstance(sample, bytes)
        or len(sample) > MAX_CLASSIFICATION_BYTES
        or not isinstance(limit_exceeded, bool)
        or limit_exceeded != (byte_count > MAX_CLASSIFICATION_BYTES)
        or (not limit_exceeded and len(sample) != byte_count)
        or (limit_exceeded and len(sample) != MAX_CLASSIFICATION_BYTES)
    ):
        raise StartupTerminalError("stream_reading_invalid")
    return {"byte_count": byte_count, "sha256": digest}


def read_startup_stream(path: Path) -> dict[str, Any]:
    """Hash/count a local stream and retain only a bounded matching prefix."""

    if path.is_symlink() or not path.is_file():
        raise StartupTerminalError("startup_stream_path_invalid")
    digest = hashlib.sha256()
    byte_count = 0
    sample = bytearray()
    try:
        stream: BinaryIO
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(STREAM_CHUNK_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
                byte_count += len(chunk)
                remaining = MAX_CLASSIFICATION_BYTES - len(sample)
                if remaining > 0:
                    sample.extend(chunk[:remaining])
    except OSError as error:
        raise StartupTerminalError("startup_stream_read_failed") from error
    return {
        "byte_count": byte_count,
        "sha256": digest.hexdigest(),
        "classification_bytes": bytes(sample),
        "limit_exceeded": byte_count > MAX_CLASSIFICATION_BYTES,
    }


def _matched_groups(stdout: bytes, stderr: bytes) -> list[str]:
    combined = stdout.lower() + b"\n" + stderr.lower()
    return sorted(
        cause
        for cause, signatures in SIGNATURE_GROUPS.items()
        if any(signature in combined for signature in signatures)
    )


def build_pre_hmr_terminal(
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
) -> dict[str, Any]:
    """Derive one safe terminal from closed facts and bounded raw prefixes."""

    operation_id = _identifier(operation_id, "operation_id")
    attempt_id = _identifier(attempt_id, "attempt_id")
    if not isinstance(candidate_source, str) or _FULL_OID.fullmatch(candidate_source) is None:
        raise StartupTerminalError("candidate_source_invalid")
    if not isinstance(native_process_started, bool):
        raise StartupTerminalError("native_process_started_invalid")
    if controller_coordinate not in CONTROLLER_COORDINATES:
        raise StartupTerminalError("controller_coordinate_invalid")
    if isinstance(hmr_events, (str, bytes)) or not isinstance(hmr_events, Sequence):
        raise StartupTerminalError("hmr_events_invalid")
    if list(hmr_events):
        raise StartupTerminalError("pre_hmr_scope_exceeded")
    stdout_projection = _stream_projection(stdout)
    stderr_projection = _stream_projection(stderr)
    stdout_over_limit = stdout["limit_exceeded"]
    stderr_over_limit = stderr["limit_exceeded"]
    if native_process_started:
        stage = "native_process_started_before_first_hmr_event"
        if controller_coordinate == "native_process_creation_failed":
            raise StartupTerminalError("started_process_coordinate_invalid")
        if exit_code is not None and (isinstance(exit_code, bool) or not isinstance(exit_code, int)):
            raise StartupTerminalError("exit_code_invalid")
        if controller_coordinate == "native_process_exited_nonzero" and (
            exit_code is None or exit_code == 0
        ):
            raise StartupTerminalError("nonzero_exit_required")
        if controller_coordinate in {
            "native_worker_timeout",
            "unexpected_controller_failure",
        } and exit_code == 0:
            raise StartupTerminalError("failed_controller_coordinate_exit_invalid")
    else:
        stage = "native_process_creation"
        if controller_coordinate != "native_process_creation_failed" or exit_code is not None:
            raise StartupTerminalError("process_creation_coordinate_invalid")
        if stdout_projection["byte_count"] != 0 or stderr_projection["byte_count"] != 0:
            raise StartupTerminalError("process_creation_streams_not_empty")

    if not native_process_started:
        cause = "operating_system_process_failure"
        matched: list[str] = []
    elif stdout_over_limit or stderr_over_limit:
        cause = "startup_stream_limit_exceeded"
        matched = []
    elif controller_coordinate == "unexpected_controller_failure":
        cause = "controller_startup_exception"
        matched = []
    elif controller_coordinate == "native_worker_timeout":
        cause = "hmr_bootstrap_failed"
        matched = []
    else:
        matched = _matched_groups(
            stdout["classification_bytes"], stderr["classification_bytes"]
        )
        if not matched:
            cause = "unclassified_nonzero_exit"
        elif len(matched) > 1:
            cause = "ambiguous_startup_signatures"
        else:
            cause = matched[0]

    terminal = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": operation_id,
        "attempt_id": attempt_id,
        "candidate_source": candidate_source,
        "stage": stage,
        "cause": cause,
        "exit_code": exit_code,
        "controller_coordinate": controller_coordinate,
        "hmr_event_count": 0,
        "matched_signature_groups": matched,
        "classification_byte_limit_per_stream": MAX_CLASSIFICATION_BYTES,
        "stdout": stdout_projection,
        "stderr": stderr_projection,
        "raw_streams_retained": False,
    }
    validate_pre_hmr_terminal(terminal)
    return terminal


def validate_pre_hmr_terminal(value: object) -> dict[str, Any]:
    """Validate the exact safe terminal shape without trusting its producer."""

    if not isinstance(value, dict) or set(value) != {
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
    }:
        raise StartupTerminalError("terminal_keys_invalid")
    if value["schema_version"] != SCHEMA_VERSION:
        raise StartupTerminalError("terminal_schema_version_invalid")
    _identifier(value["operation_id"], "operation_id")
    _identifier(value["attempt_id"], "attempt_id")
    if not isinstance(value["candidate_source"], str) or _FULL_OID.fullmatch(
        value["candidate_source"]
    ) is None:
        raise StartupTerminalError("candidate_source_invalid")
    if value["stage"] not in STAGES or value["cause"] not in CAUSES:
        raise StartupTerminalError("terminal_coordinate_invalid")
    if value["controller_coordinate"] not in CONTROLLER_COORDINATES:
        raise StartupTerminalError("controller_coordinate_invalid")
    exit_code = value["exit_code"]
    if exit_code is not None and (isinstance(exit_code, bool) or not isinstance(exit_code, int)):
        raise StartupTerminalError("exit_code_invalid")
    if value["hmr_event_count"] != 0:
        raise StartupTerminalError("hmr_event_count_invalid")
    if value["classification_byte_limit_per_stream"] != MAX_CLASSIFICATION_BYTES:
        raise StartupTerminalError("classification_limit_invalid")
    if value["raw_streams_retained"] is not False:
        raise StartupTerminalError("raw_stream_retention_invalid")
    for label in ("stdout", "stderr"):
        projection = value[label]
        if (
            not isinstance(projection, dict)
            or set(projection) != {"byte_count", "sha256"}
            or isinstance(projection["byte_count"], bool)
            or not isinstance(projection["byte_count"], int)
            or projection["byte_count"] < 0
            or not isinstance(projection["sha256"], str)
            or _DIGEST.fullmatch(projection["sha256"]) is None
        ):
            raise StartupTerminalError(f"{label}_projection_invalid")
        if projection["byte_count"] == 0 and projection["sha256"] != hashlib.sha256(
            b""
        ).hexdigest():
            raise StartupTerminalError(f"{label}_empty_digest_invalid")
    matched = value["matched_signature_groups"]
    if (
        not isinstance(matched, list)
        or matched != sorted(set(matched))
        or any(item not in SIGNATURE_GROUPS for item in matched)
    ):
        raise StartupTerminalError("matched_signature_groups_invalid")
    cause = value["cause"]
    if (
        value["controller_coordinate"] == "native_process_exited_nonzero"
        and cause in SIGNATURE_GROUPS
        and matched != [cause]
    ):
        raise StartupTerminalError("single_signature_cause_invalid")
    if cause == "ambiguous_startup_signatures" and len(matched) < 2:
        raise StartupTerminalError("ambiguous_signature_cause_invalid")
    if cause not in {*SIGNATURE_GROUPS, "ambiguous_startup_signatures"} and matched:
        raise StartupTerminalError("non_signature_cause_has_matches")
    if value["stage"] == "native_process_creation":
        if (
            value["cause"] != "operating_system_process_failure"
            or value["controller_coordinate"] != "native_process_creation_failed"
            or exit_code is not None
            or value["stdout"]["byte_count"] != 0
            or value["stderr"]["byte_count"] != 0
        ):
            raise StartupTerminalError("process_creation_terminal_invalid")
    else:
        coordinate = value["controller_coordinate"]
        if coordinate == "native_process_creation_failed":
            raise StartupTerminalError("started_process_coordinate_invalid")
        if coordinate == "native_process_exited_nonzero" and (
            exit_code is None or exit_code == 0
        ):
            raise StartupTerminalError("nonzero_exit_required")
        if coordinate in {
            "native_worker_timeout",
            "unexpected_controller_failure",
        } and exit_code == 0:
            raise StartupTerminalError("failed_controller_coordinate_exit_invalid")
        stream_limit_exceeded = any(
            value[label]["byte_count"] > MAX_CLASSIFICATION_BYTES
            for label in ("stdout", "stderr")
        )
        if stream_limit_exceeded:
            if cause != "startup_stream_limit_exceeded" or matched:
                raise StartupTerminalError("stream_limit_terminal_invalid")
        elif coordinate == "unexpected_controller_failure":
            if cause != "controller_startup_exception" or matched:
                raise StartupTerminalError("controller_exception_terminal_invalid")
        elif coordinate == "native_worker_timeout":
            if cause != "hmr_bootstrap_failed" or matched:
                raise StartupTerminalError("timeout_terminal_invalid")
        elif cause not in {
            *SIGNATURE_GROUPS,
            "ambiguous_startup_signatures",
            "unclassified_nonzero_exit",
        }:
            raise StartupTerminalError("nonzero_exit_cause_invalid")
    return value


def terminal_bytes(value: object) -> bytes:
    terminal = validate_pre_hmr_terminal(value)
    return (json.dumps(terminal, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_pre_hmr_terminal_exclusive(
    *,
    path: Path,
    terminal: object,
    evidence_root: Path,
    disposable_root: Path,
) -> str:
    """Write and read back one terminal outside the disposable root."""

    if not path.is_absolute() or not evidence_root.is_absolute() or not disposable_root.is_absolute():
        raise StartupTerminalError("terminal_paths_must_be_absolute")
    if (
        evidence_root.is_symlink()
        or not evidence_root.is_dir()
        or disposable_root.is_symlink()
        or not disposable_root.is_dir()
    ):
        raise StartupTerminalError("terminal_root_invalid")
    resolved_root = evidence_root.resolve()
    resolved_disposable = disposable_root.resolve()
    resolved_parent = path.parent.resolve()
    resolved_path = resolved_parent / path.name
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise StartupTerminalError("terminal_path_outside_evidence_root") from error
    try:
        resolved_path.relative_to(resolved_disposable)
    except ValueError:
        pass
    else:
        raise StartupTerminalError("terminal_path_inside_disposable_root")
    lexical_root = evidence_root.absolute()
    lexical_parent = path.parent.absolute()
    try:
        lexical_parent.relative_to(lexical_root)
    except ValueError as error:
        raise StartupTerminalError("terminal_path_alias_or_escape") from error
    current = lexical_parent
    while True:
        if current.is_symlink():
            raise StartupTerminalError("terminal_parent_symlink_forbidden")
        if current == lexical_root:
            break
        if current == current.parent:
            raise StartupTerminalError("terminal_parent_invalid")
        current = current.parent
    if not resolved_parent.is_dir() or path.is_symlink() or path.exists():
        raise StartupTerminalError("terminal_path_invalid")
    payload = terminal_bytes(terminal)
    try:
        descriptor = os.open(resolved_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        raise StartupTerminalError("terminal_exclusive_write_failed") from error
    try:
        readback = resolved_path.read_bytes()
        validate_pre_hmr_terminal(json.loads(readback))
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        StartupTerminalError,
        TypeError,
    ) as error:
        raise StartupTerminalError("terminal_readback_failed") from error
    if readback != payload:
        raise StartupTerminalError("terminal_readback_mismatch")
    return hashlib.sha256(payload).hexdigest()

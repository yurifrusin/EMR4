"""Provider-free structured-diagnostic gear for a future bounded worker."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from orchestration_harness import native_startup_terminal as legacy_terminal
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as bounded_worker,
)


WRAPPER_LEAF = "entrypoint-wrapper.mjs"
DIAGNOSTIC_LEAF = "pre-hmr-structured-diagnostic.json"
PROFILE = "headless"
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


class ControllerConvergenceError(ValueError):
    """The provider-free controller convergence contract was not satisfied."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_inside_root_exclusive(
    *, path: Path, payload: bytes, disposable_root: Path
) -> str:
    root = disposable_root.resolve(strict=True)
    if root.is_symlink() or path.is_symlink() or path.exists():
        raise ControllerConvergenceError("disposable_output_path_invalid")
    resolved = path.parent.resolve(strict=True) / path.name
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ControllerConvergenceError("disposable_output_path_escape") from error
    descriptor = os.open(resolved, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    if resolved.read_bytes() != payload:
        raise ControllerConvergenceError("disposable_output_readback_mismatch")
    return _sha256(payload)


def build_launch_binding(
    *,
    disposable_root: Path,
    package_root: Path,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    target_path: str,
    node_executable: str,
) -> dict[str, Any]:
    """Write the canonical wrapper and return exact future-worker argv."""

    root = disposable_root.resolve(strict=True)
    if (
        root.is_symlink()
        or FULL_OID.fullmatch(candidate_source) is None
        or not target_path
    ):
        raise ControllerConvergenceError("launch_identity_invalid")
    wrapper_path = root / WRAPPER_LEAF
    diagnostic_path = root / DIAGNOSTIC_LEAF
    wrapper = diagnostic.build_entrypoint_wrapper_source(
        package_root=package_root.resolve(strict=True),
        wrapper_path=wrapper_path,
        diagnostic_path=diagnostic_path,
        disposable_root=root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
        canonical_json=True,
    )
    wrapper_sha256 = _write_inside_root_exclusive(
        path=wrapper_path,
        payload=wrapper,
        disposable_root=root,
    )
    wrapper_projection = diagnostic.validate_entrypoint_wrapper_source(
        wrapper, require_canonical_json=True
    )
    task = bounded_worker.task_text(target_path)
    command = diagnostic.build_launch_command(
        node_executable=node_executable,
        wrapper_path=wrapper_path,
        profile=PROFILE,
        task=task,
    )
    return {
        "wrapper_path": wrapper_path,
        "diagnostic_path": diagnostic_path,
        "wrapper_sha256": wrapper_sha256,
        "wrapper_projection": wrapper_projection,
        "command": command,
        "task_sha256": _sha256(task.encode()),
    }


def select_pre_hmr_terminal(
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    native_process_started: bool,
    exit_code: int | None,
    controller_coordinate: str,
    hmr_events: list[str],
    stdout: dict[str, Any],
    stderr: dict[str, Any],
    diagnostic_path: Path,
    disposable_root: Path,
) -> dict[str, Any]:
    """Build v1 first and select v2 only from exact canonical evidence."""

    fallback = legacy_terminal.build_pre_hmr_terminal(
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
    applicable = (
        native_process_started
        and controller_coordinate == "native_process_exited_nonzero"
        and exit_code is not None
        and exit_code != 0
        and not hmr_events
    )
    if not applicable:
        return {
            "terminal": fallback,
            "structured_accepted": False,
            "failure_coordinate": None,
        }
    if diagnostic_path.is_symlink():
        return {
            "terminal": fallback,
            "structured_accepted": False,
            "failure_coordinate": "structured_diagnostic_invalid",
        }
    if not diagnostic_path.exists():
        return {
            "terminal": fallback,
            "structured_accepted": False,
            "failure_coordinate": "structured_diagnostic_absent",
        }
    try:
        safe = diagnostic.read_structured_diagnostic(
            diagnostic_path,
            disposable_root=disposable_root,
            operation_id=operation_id,
            attempt_id=attempt_id,
            candidate_source=candidate_source,
        )
        terminal = diagnostic.build_structured_pre_hmr_terminal(
            operation_id=operation_id,
            attempt_id=attempt_id,
            candidate_source=candidate_source,
            native_process_started=native_process_started,
            exit_code=exit_code,
            controller_coordinate=controller_coordinate,
            hmr_events=hmr_events,
            stdout=stdout,
            stderr=stderr,
            structured_diagnostic=safe,
        )
    except (diagnostic.StructuredDiagnosticError, OSError, ValueError):
        return {
            "terminal": fallback,
            "structured_accepted": False,
            "failure_coordinate": "structured_diagnostic_invalid",
        }
    return {
        "terminal": terminal,
        "structured_accepted": True,
        "failure_coordinate": None,
    }


def write_selected_terminal_exclusive(
    *, path: Path, terminal: dict[str, Any], evidence_root: Path, disposable_root: Path
) -> str:
    """Persist one validated v1 or v2 terminal outside the disposable root."""

    if terminal.get("schema_version") == legacy_terminal.SCHEMA_VERSION:
        return legacy_terminal.write_pre_hmr_terminal_exclusive(
            path=path,
            terminal=terminal,
            evidence_root=evidence_root,
            disposable_root=disposable_root,
        )
    diagnostic.validate_structured_pre_hmr_terminal(terminal)
    resolved_evidence = evidence_root.resolve(strict=True)
    resolved_disposable = disposable_root.resolve(strict=True)
    if path.parent.resolve() != resolved_evidence or path.is_symlink() or path.exists():
        raise ControllerConvergenceError("terminal_path_invalid")
    try:
        path.resolve().relative_to(resolved_disposable)
    except ValueError:
        pass
    else:
        raise ControllerConvergenceError("terminal_inside_disposable_root")
    payload = diagnostic.structured_terminal_bytes(terminal)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    readback = path.read_bytes()
    try:
        diagnostic.validate_structured_pre_hmr_terminal(json.loads(readback))
    except (
        json.JSONDecodeError,
        diagnostic.StructuredDiagnosticError,
    ) as error:
        raise ControllerConvergenceError("terminal_readback_invalid") from error
    if readback != payload:
        raise ControllerConvergenceError("terminal_readback_mismatch")
    return _sha256(payload)


def lifecycle_envelope_source() -> bytes:
    """Return the exact serial ordering required of a fresh occupied runner."""

    return b'''binding = build_launch_binding(...)
process = launch_exactly_one_native_process(binding["command"])
wait_for_exit_or_first_hmr(process)
selection = select_pre_hmr_terminal(diagnostic_path=binding["diagnostic_path"], ...)
require_structured_acceptance_or_fail_closed(selection)
write_selected_terminal_exclusive(terminal=selection["terminal"], ...)
terminate_exact_owned_process(process)
remove_exact_disposable_root()
'''


def validate_lifecycle_envelope(payload: bytes) -> dict[str, Any]:
    try:
        source = payload.decode()
    except UnicodeError as error:
        raise ControllerConvergenceError("lifecycle_envelope_utf8_invalid") from error
    coordinates = [
        "build_launch_binding(",
        "launch_exactly_one_native_process(",
        "wait_for_exit_or_first_hmr(",
        "select_pre_hmr_terminal(",
        "require_structured_acceptance_or_fail_closed(",
        "write_selected_terminal_exclusive(",
        "terminate_exact_owned_process(",
        "remove_exact_disposable_root()",
    ]
    try:
        positions = [source.index(item) for item in coordinates]
    except ValueError as error:
        raise ControllerConvergenceError("lifecycle_coordinate_missing") from error
    checks = {
        "exact_order": positions == sorted(positions),
        "single_launch": source.count("launch_exactly_one_native_process(") == 1,
        "single_terminal_write": source.count("write_selected_terminal_exclusive(")
        == 1,
        "cleanup_last": source.rstrip().endswith("remove_exact_disposable_root()"),
        "no_retry": "retry" not in source.lower(),
    }
    if not all(checks.values()):
        raise ControllerConvergenceError("lifecycle_envelope_invalid")
    return {"sha256": _sha256(payload), "checks": checks}

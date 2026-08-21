"""Provider-free materialisation and terminal assembly for a future Harness attempt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from orchestration_harness import native_post_hmr_pre_request_controller as controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic


BUNDLE_SCHEMA_VERSION = "ariadne.native_harness_future_attempt_bundle.v1"
TERMINAL_SCHEMA_VERSION = "ariadne.native_harness_controller_terminal.v1"
MAX_MANIFEST_BYTES = 16_384
MAX_TERMINAL_BYTES = 8_192
MAX_SOURCE_BYTES = 65_536
INHERITED_TARGET_CLASSIFICATION = "consumed_attempt_005_authored_synthetic_target"

RUNNER_RELATIVE_PATH = "runner/synthetic-one-request-worker-runner.mjs"
HELPER_RELATIVE_PATH = "runner/post-hmr-pre-request-diagnostic.mjs"
BUNDLE_RELATIVE_PATH = "control/future-attempt-bundle.json"
SIDECAR_RELATIVE_PATH = "control/post-hmr-diagnostic.json"
BROKER_RELATIVE_PATH = "control/broker-request-reading.json"
TERMINAL_RELATIVE_PATH = "control/controller-terminal.json"
PATH_ROSTER = (
    RUNNER_RELATIVE_PATH,
    HELPER_RELATIVE_PATH,
    BUNDLE_RELATIVE_PATH,
    SIDECAR_RELATIVE_PATH,
    BROKER_RELATIVE_PATH,
    TERMINAL_RELATIVE_PATH,
)
INITIAL_PATHS = frozenset(
    {RUNNER_RELATIVE_PATH, HELPER_RELATIVE_PATH, BUNDLE_RELATIVE_PATH}
)
CONTROL_OPTIONAL_PATHS = frozenset(
    {SIDECAR_RELATIVE_PATH, BROKER_RELATIVE_PATH, TERMINAL_RELATIVE_PATH}
)
PROCESS_FLAGS = (
    "node_process_authorized",
    "native_harness_process_authorized",
    "broker_process_authorized",
    "worker_process_authorized",
    "model_request_authorized",
    "provider_request_authorized",
    "network_request_authorized",
    "database_invocation_authorized",
    "docker_invocation_authorized",
)
RAW_FLAGS = (
    "raw_error_message_retained",
    "raw_stack_retained",
    "raw_paths_retained",
    "raw_cause_retained",
    "raw_stream_retained",
)
_FULL_OID = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")


class FutureAttemptMaterialisationError(ValueError):
    """A future-attempt fixture did not satisfy its closed contract."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _identity(value: object, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise FutureAttemptMaterialisationError(f"{label}_invalid")
    return value


def _candidate_source(value: object) -> str:
    if not isinstance(value, str) or _FULL_OID.fullmatch(value) is None:
        raise FutureAttemptMaterialisationError("candidate_source_invalid")
    return value


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        raise FutureAttemptMaterialisationError(f"{label}_invalid")
    return value


def canonical_json_bytes(value: object, *, maximum: int) -> bytes:
    payload = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(payload) > maximum:
        raise FutureAttemptMaterialisationError("canonical_json_size_exceeded")
    return payload


def _validate_roster(value: object) -> list[str]:
    if not isinstance(value, list) or value != list(PATH_ROSTER):
        raise FutureAttemptMaterialisationError("path_roster_invalid")
    casefolded: set[str] = set()
    for raw in value:
        if not isinstance(raw, str) or "\\" in raw:
            raise FutureAttemptMaterialisationError("path_roster_member_invalid")
        path = PurePosixPath(raw)
        if path.is_absolute() or ".." in path.parts or str(path) != raw:
            raise FutureAttemptMaterialisationError("path_roster_member_invalid")
        folded = raw.casefold()
        if folded in casefolded:
            raise FutureAttemptMaterialisationError("path_roster_case_collision")
        casefolded.add(folded)
    return value


def build_bundle_manifest(
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    runner_sha256: str,
    helper_sha256: str,
    controller_sha256: str,
) -> dict[str, Any]:
    return validate_bundle_manifest(
        {
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "operation_id": operation_id,
            "attempt_id": attempt_id,
            "candidate_source": candidate_source,
            "source_bindings": {
                "future_runner_sha256": runner_sha256,
                "generated_helper_sha256": helper_sha256,
                "controller_module_sha256": controller_sha256,
            },
            "path_roster": list(PATH_ROSTER),
            "inherited_target_classification": INHERITED_TARGET_CLASSIFICATION,
            "occupied_launch_authorized": False,
            "execution_authority": {key: False for key in PROCESS_FLAGS},
            "raw_retention": {key: False for key in RAW_FLAGS},
        }
    )


def validate_bundle_manifest(value: object) -> dict[str, Any]:
    expected_keys = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "candidate_source",
        "source_bindings",
        "path_roster",
        "inherited_target_classification",
        "occupied_launch_authorized",
        "execution_authority",
        "raw_retention",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise FutureAttemptMaterialisationError("bundle_keys_invalid")
    if value["schema_version"] != BUNDLE_SCHEMA_VERSION:
        raise FutureAttemptMaterialisationError("bundle_schema_invalid")
    _identity(value["operation_id"], "operation_id")
    _identity(value["attempt_id"], "attempt_id")
    _candidate_source(value["candidate_source"])
    bindings = value["source_bindings"]
    if not isinstance(bindings, dict) or set(bindings) != {
        "future_runner_sha256",
        "generated_helper_sha256",
        "controller_module_sha256",
    }:
        raise FutureAttemptMaterialisationError("bundle_source_bindings_invalid")
    for key, digest in bindings.items():
        _digest(digest, key)
    _validate_roster(value["path_roster"])
    if value["inherited_target_classification"] != INHERITED_TARGET_CLASSIFICATION:
        raise FutureAttemptMaterialisationError("inherited_target_classification_invalid")
    if value["occupied_launch_authorized"] is not False:
        raise FutureAttemptMaterialisationError("occupied_launch_authority_invalid")
    for key, expected in (
        ("execution_authority", set(PROCESS_FLAGS)),
        ("raw_retention", set(RAW_FLAGS)),
    ):
        flags = value[key]
        if (
            not isinstance(flags, dict)
            or set(flags) != expected
            or any(flag is not False for flag in flags.values())
        ):
            raise FutureAttemptMaterialisationError(f"{key}_invalid")
    return value


def bundle_manifest_bytes(value: object) -> bytes:
    return canonical_json_bytes(validate_bundle_manifest(value), maximum=MAX_MANIFEST_BYTES)


def _write_exclusive(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
    except (FileExistsError, IsADirectoryError, OSError) as error:
        raise FutureAttemptMaterialisationError("exclusive_write_failed") from error


def _require_absolute_directory(path: Path, label: str) -> Path:
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise FutureAttemptMaterialisationError(f"{label}_invalid")
    return path.resolve()


def _path(root: Path, relative: str) -> Path:
    candidate = root / Path(*PurePosixPath(relative).parts)
    try:
        candidate.resolve(strict=False).relative_to(root.resolve())
    except ValueError as error:
        raise FutureAttemptMaterialisationError("bundle_path_escape") from error
    return candidate


def _tree_files(root: Path) -> set[str]:
    if root.is_symlink() or not root.is_dir():
        raise FutureAttemptMaterialisationError("attempt_root_invalid")
    root_entries = {entry.name: entry for entry in root.iterdir()}
    if set(root_entries) != {"runner", "control"}:
        raise FutureAttemptMaterialisationError("attempt_root_roster_invalid")
    files: set[str] = set()
    for directory_name, expected_names in (
        (
            "runner",
            {
                PurePosixPath(RUNNER_RELATIVE_PATH).name,
                PurePosixPath(HELPER_RELATIVE_PATH).name,
            },
        ),
        (
            "control",
            {
                PurePosixPath(BUNDLE_RELATIVE_PATH).name,
                PurePosixPath(SIDECAR_RELATIVE_PATH).name,
                PurePosixPath(BROKER_RELATIVE_PATH).name,
                PurePosixPath(TERMINAL_RELATIVE_PATH).name,
            },
        ),
    ):
        directory = root_entries[directory_name]
        if directory.is_symlink() or not directory.is_dir():
            raise FutureAttemptMaterialisationError("attempt_directory_invalid")
        for member in directory.iterdir():
            if member.is_symlink() or not member.is_file():
                raise FutureAttemptMaterialisationError("attempt_member_invalid")
            if member.name not in expected_names:
                raise FutureAttemptMaterialisationError("attempt_member_unregistered")
            files.add(f"{directory_name}/{member.name}")
    if not INITIAL_PATHS.issubset(files) or not files.issubset(
        INITIAL_PATHS | CONTROL_OPTIONAL_PATHS
    ):
        raise FutureAttemptMaterialisationError("attempt_file_roster_invalid")
    return files


def _read_limited(path: Path, maximum: int, label: str) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise FutureAttemptMaterialisationError(f"{label}_invalid")
    return path.read_bytes()


def materialize_future_attempt(
    *,
    disposable_parent: Path,
    attempt_id: str,
    operation_id: str,
    candidate_source: str,
    runner_payload: bytes,
    helper_payload: bytes,
    controller_payload: bytes,
    expected_runner_sha256: str,
    expected_helper_sha256: str,
    expected_controller_sha256: str,
) -> dict[str, Any]:
    """Materialise exact accepted bytes into one new disposable attempt root."""

    parent = _require_absolute_directory(disposable_parent, "disposable_parent")
    _identity(attempt_id, "attempt_id")
    _identity(operation_id, "operation_id")
    _candidate_source(candidate_source)
    bindings = {
        "future_runner_sha256": _sha256(runner_payload),
        "generated_helper_sha256": _sha256(helper_payload),
        "controller_module_sha256": _sha256(controller_payload),
    }
    expected = {
        "future_runner_sha256": _digest(expected_runner_sha256, "future_runner_sha256"),
        "generated_helper_sha256": _digest(expected_helper_sha256, "generated_helper_sha256"),
        "controller_module_sha256": _digest(
            expected_controller_sha256, "controller_module_sha256"
        ),
    }
    if bindings != expected:
        raise FutureAttemptMaterialisationError("materialisation_source_binding_mismatch")
    if len(runner_payload) > MAX_SOURCE_BYTES or len(helper_payload) > MAX_SOURCE_BYTES:
        raise FutureAttemptMaterialisationError("materialisation_source_size_exceeded")
    root = parent / attempt_id
    if root.exists() or root.is_symlink():
        raise FutureAttemptMaterialisationError("attempt_root_must_be_absent")
    try:
        root.mkdir()
        (root / "runner").mkdir()
        (root / "control").mkdir()
    except OSError as error:
        raise FutureAttemptMaterialisationError("attempt_root_creation_failed") from error
    manifest = build_bundle_manifest(
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
        runner_sha256=bindings["future_runner_sha256"],
        helper_sha256=bindings["generated_helper_sha256"],
        controller_sha256=bindings["controller_module_sha256"],
    )
    _write_exclusive(_path(root, RUNNER_RELATIVE_PATH), runner_payload)
    _write_exclusive(_path(root, HELPER_RELATIVE_PATH), helper_payload)
    _write_exclusive(_path(root, BUNDLE_RELATIVE_PATH), bundle_manifest_bytes(manifest))
    reading = read_materialized_bundle(
        root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
        expected_bindings=expected,
    )
    if reading["files"] != sorted(INITIAL_PATHS):
        raise FutureAttemptMaterialisationError("initial_materialisation_roster_invalid")
    return reading


def read_materialized_bundle(
    root: Path,
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    expected_bindings: dict[str, str],
) -> dict[str, Any]:
    """Read back a complete materialised bundle without accepting extra files."""

    if not root.is_absolute():
        raise FutureAttemptMaterialisationError("attempt_root_must_be_absolute")
    _identity(operation_id, "operation_id")
    _identity(attempt_id, "attempt_id")
    _candidate_source(candidate_source)
    files = _tree_files(root)
    payload = _read_limited(
        _path(root, BUNDLE_RELATIVE_PATH), MAX_MANIFEST_BYTES, "bundle_manifest_file"
    )
    try:
        manifest = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise FutureAttemptMaterialisationError("bundle_manifest_json_invalid") from error
    manifest = validate_bundle_manifest(manifest)
    if payload != bundle_manifest_bytes(manifest):
        raise FutureAttemptMaterialisationError("bundle_manifest_canonical_bytes_required")
    if (
        manifest["operation_id"] != operation_id
        or manifest["attempt_id"] != attempt_id
        or manifest["candidate_source"] != candidate_source
    ):
        raise FutureAttemptMaterialisationError("bundle_runtime_identity_mismatch")
    expected_keys = {
        "future_runner_sha256",
        "generated_helper_sha256",
        "controller_module_sha256",
    }
    if set(expected_bindings) != expected_keys or any(
        _digest(value, key) != value for key, value in expected_bindings.items()
    ):
        raise FutureAttemptMaterialisationError("expected_bindings_invalid")
    if manifest["source_bindings"] != expected_bindings:
        raise FutureAttemptMaterialisationError("bundle_source_binding_mismatch")
    runner_payload = _read_limited(
        _path(root, RUNNER_RELATIVE_PATH), MAX_SOURCE_BYTES, "runner_file"
    )
    helper_payload = _read_limited(
        _path(root, HELPER_RELATIVE_PATH), MAX_SOURCE_BYTES, "helper_file"
    )
    if (
        _sha256(runner_payload) != expected_bindings["future_runner_sha256"]
        or _sha256(helper_payload) != expected_bindings["generated_helper_sha256"]
    ):
        raise FutureAttemptMaterialisationError("materialized_source_digest_mismatch")
    return {
        "root": root,
        "manifest": manifest,
        "files": sorted(files),
        "runner_bytes": len(runner_payload),
        "helper_bytes": len(helper_payload),
    }


def write_broker_fixture(root: Path, value: object) -> Path:
    """Exclusively write one accepted canonical broker fixture."""

    _tree_files(root)
    path = _path(root, BROKER_RELATIVE_PATH)
    _write_exclusive(path, controller.broker_reading_bytes(value))
    return path


def write_sidecar_fixture(root: Path, value: object) -> Path:
    """Exclusively write one accepted canonical diagnostic fixture."""

    _tree_files(root)
    path = _path(root, SIDECAR_RELATIVE_PATH)
    _write_exclusive(path, diagnostic.diagnostic_bytes(value))
    return path


def _terminal_from_selection(
    selection: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    return validate_controller_terminal(
        {
            "schema_version": TERMINAL_SCHEMA_VERSION,
            "operation_id": manifest["operation_id"],
            "attempt_id": manifest["attempt_id"],
            "candidate_source": manifest["candidate_source"],
            "coordinate": selection["coordinate"],
            "diagnostic_accepted": selection["diagnostic_accepted"],
            "broker_zero": selection["broker_zero"],
            "pre_request_supported": selection["pre_request_supported"],
            "stage": selection["stage"],
            "cause_coordinate": selection["cause_coordinate"],
            "error_kind": selection["error_kind"],
            "source_bindings": manifest["source_bindings"],
            "inherited_target_classification": manifest[
                "inherited_target_classification"
            ],
            "occupied_launch_authorized": False,
            "raw_stream_read": False,
            "raw_error_retained": False,
        }
    )


def validate_controller_terminal(value: object) -> dict[str, Any]:
    expected_keys = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "candidate_source",
        "coordinate",
        "diagnostic_accepted",
        "broker_zero",
        "pre_request_supported",
        "stage",
        "cause_coordinate",
        "error_kind",
        "source_bindings",
        "inherited_target_classification",
        "occupied_launch_authorized",
        "raw_stream_read",
        "raw_error_retained",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise FutureAttemptMaterialisationError("controller_terminal_keys_invalid")
    if value["schema_version"] != TERMINAL_SCHEMA_VERSION:
        raise FutureAttemptMaterialisationError("controller_terminal_schema_invalid")
    _identity(value["operation_id"], "operation_id")
    _identity(value["attempt_id"], "attempt_id")
    _candidate_source(value["candidate_source"])
    if value["coordinate"] not in controller.COORDINATES:
        raise FutureAttemptMaterialisationError("controller_terminal_coordinate_invalid")
    for key in (
        "diagnostic_accepted",
        "broker_zero",
        "pre_request_supported",
    ):
        if type(value[key]) is not bool:
            raise FutureAttemptMaterialisationError("controller_terminal_boolean_invalid")
    accepted = value["diagnostic_accepted"]
    broker_zero = value["broker_zero"]
    expected_coordinate = (
        "native_harness_terminal_failure"
        if not accepted
        else (
            "post_hmr_pre_request_failure"
            if broker_zero
            else "post_hmr_request_boundary_unresolved"
        )
    )
    if (
        value["coordinate"] != expected_coordinate
        or value["pre_request_supported"] is not (accepted and broker_zero)
    ):
        raise FutureAttemptMaterialisationError("controller_terminal_relationship_invalid")
    closed_fields = (value["stage"], value["cause_coordinate"], value["error_kind"])
    if accepted:
        if (
            value["stage"] not in diagnostic.PRE_REQUEST_STAGES
            or value["cause_coordinate"] not in diagnostic.CAUSE_COORDINATES
            or value["error_kind"] not in diagnostic.ERROR_KINDS
            or (
                value["cause_coordinate"] == "required_service_missing"
                and value["stage"] != "required_service_lookup"
            )
            or (
                value["cause_coordinate"] == "preset_root_roster_mismatch"
                and value["stage"] != "preset_root_roster_admission"
            )
        ):
            raise FutureAttemptMaterialisationError("controller_terminal_diagnostic_invalid")
    elif any(item is not None for item in closed_fields):
        raise FutureAttemptMaterialisationError("controller_terminal_diagnostic_invalid")
    bindings = value["source_bindings"]
    if not isinstance(bindings, dict) or set(bindings) != {
        "future_runner_sha256",
        "generated_helper_sha256",
        "controller_module_sha256",
    }:
        raise FutureAttemptMaterialisationError("controller_terminal_bindings_invalid")
    for key, digest in bindings.items():
        _digest(digest, key)
    if value["inherited_target_classification"] != INHERITED_TARGET_CLASSIFICATION:
        raise FutureAttemptMaterialisationError("controller_terminal_target_invalid")
    for key in (
        "occupied_launch_authorized",
        "raw_stream_read",
        "raw_error_retained",
    ):
        if value[key] is not False:
            raise FutureAttemptMaterialisationError("controller_terminal_raw_or_authority_invalid")
    return value


def controller_terminal_bytes(value: object) -> bytes:
    return canonical_json_bytes(
        validate_controller_terminal(value), maximum=MAX_TERMINAL_BYTES
    )


def assemble_controller_terminal(
    root: Path,
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    expected_bindings: dict[str, str],
) -> dict[str, Any]:
    """Select and exclusively write one typed terminal from materialised evidence."""

    terminal_path = _path(root, TERMINAL_RELATIVE_PATH)
    if terminal_path.exists() or terminal_path.is_symlink():
        raise FutureAttemptMaterialisationError("controller_terminal_must_be_absent")
    reading = read_materialized_bundle(
        root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
        expected_bindings=expected_bindings,
    )
    broker_path = _path(root, BROKER_RELATIVE_PATH)
    if BROKER_RELATIVE_PATH not in reading["files"]:
        raise FutureAttemptMaterialisationError("broker_reading_required")
    selection = controller.select_post_hmr_failure(
        diagnostic_path=_path(root, SIDECAR_RELATIVE_PATH),
        broker_reading_path=broker_path,
        disposable_root=root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
    )
    terminal = _terminal_from_selection(selection, reading["manifest"])
    payload = controller_terminal_bytes(terminal)
    _write_exclusive(terminal_path, payload)
    if _read_limited(terminal_path, MAX_TERMINAL_BYTES, "controller_terminal_file") != payload:
        raise FutureAttemptMaterialisationError("controller_terminal_readback_mismatch")
    return terminal

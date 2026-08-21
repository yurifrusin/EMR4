"""Provider-free identity and target rebinding for a future Harness attempt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from orchestration_harness import native_post_hmr_future_attempt_materialisation as base
from orchestration_harness import native_post_hmr_pre_request_controller as controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic


BUNDLE_SCHEMA_VERSION = "ariadne.native_harness_rebound_future_attempt_bundle.v1"
TERMINAL_SCHEMA_VERSION = "ariadne.native_harness_rebound_controller_terminal.v1"
TARGET_CLASSIFICATION = "inert_authored_synthetic_relative_python_fixture"
ADMITTED_TARGET_PATH = "workspace/authored_synthetic_control_probe.py"
MAX_MANIFEST_BYTES = 16_384
MAX_TERMINAL_BYTES = 8_192

_FULL_OID = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")


class FutureAttemptRebindingError(ValueError):
    """A rebound future-attempt fixture did not satisfy its closed contract."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _identity(value: object, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise FutureAttemptRebindingError(f"{label}_invalid")
    return value


def _candidate_source(value: object) -> str:
    if not isinstance(value, str) or _FULL_OID.fullmatch(value) is None:
        raise FutureAttemptRebindingError("candidate_source_invalid")
    return value


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        raise FutureAttemptRebindingError(f"{label}_invalid")
    return value


def canonical_json_bytes(value: object, *, maximum: int) -> bytes:
    payload = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(payload) > maximum:
        raise FutureAttemptRebindingError("canonical_json_size_exceeded")
    return payload


def validate_target_path(value: object) -> str:
    if not isinstance(value, str) or value != ADMITTED_TARGET_PATH:
        raise FutureAttemptRebindingError("target_path_invalid")
    if (
        "\\" in value
        or ":" in value
        or value.startswith(("/", "//"))
        or value.split("/") != ["workspace", "authored_synthetic_control_probe.py"]
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or not value.isascii()
    ):
        raise FutureAttemptRebindingError("target_path_invalid")
    return value


def build_target_binding(target_path: str) -> dict[str, Any]:
    target = validate_target_path(target_path)
    return {
        "classification": TARGET_CLASSIFICATION,
        "relative_path": target,
        "coordinate_sha256": sha256_bytes(target.encode()),
        "occupied_target_use_authorized": False,
    }


def validate_target_binding(value: object) -> dict[str, Any]:
    expected_keys = {
        "classification",
        "relative_path",
        "coordinate_sha256",
        "occupied_target_use_authorized",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise FutureAttemptRebindingError("target_binding_keys_invalid")
    target = validate_target_path(value["relative_path"])
    if value["classification"] != TARGET_CLASSIFICATION:
        raise FutureAttemptRebindingError("target_classification_invalid")
    if value["coordinate_sha256"] != sha256_bytes(target.encode()):
        raise FutureAttemptRebindingError("target_coordinate_sha256_invalid")
    if value["occupied_target_use_authorized"] is not False:
        raise FutureAttemptRebindingError("target_use_authority_invalid")
    return value


def rebind_future_runner_source(
    accepted_payload: bytes,
    *,
    expected_accepted_sha256: str,
    consumed_target_path: str,
    target_path: str,
) -> tuple[bytes, dict[str, Any]]:
    """Replace exactly one consumed target and prove exact reversibility."""

    if sha256_bytes(accepted_payload) != _digest(
        expected_accepted_sha256, "accepted_future_runner_sha256"
    ):
        raise FutureAttemptRebindingError("accepted_future_runner_sha256_mismatch")
    target = validate_target_path(target_path)
    if (
        not isinstance(consumed_target_path, str)
        or not consumed_target_path
        or consumed_target_path == target
    ):
        raise FutureAttemptRebindingError("consumed_target_path_invalid")
    try:
        source = accepted_payload.decode("utf-8")
    except UnicodeError as error:
        raise FutureAttemptRebindingError(
            "accepted_future_runner_utf8_invalid"
        ) from error
    old_literal = json.dumps(consumed_target_path)
    new_literal = json.dumps(target)
    if source.count(old_literal) != 1 or source.count(new_literal) != 0:
        raise FutureAttemptRebindingError("consumed_target_literal_count_invalid")
    rebound_source = source.replace(old_literal, new_literal, 1)
    if rebound_source.count(old_literal) != 0 or rebound_source.count(new_literal) != 1:
        raise FutureAttemptRebindingError("rebound_target_literal_count_invalid")
    reversed_payload = rebound_source.replace(new_literal, old_literal, 1).encode()
    if reversed_payload != accepted_payload:
        raise FutureAttemptRebindingError("runner_reversal_mismatch")
    payload = rebound_source.encode()
    return payload, {
        "accepted_future_runner_sha256": expected_accepted_sha256,
        "rebound_future_runner_sha256": sha256_bytes(payload),
        "target_binding": build_target_binding(target),
        "consumed_target_absent": consumed_target_path.encode() not in payload,
        "target_literal_count": rebound_source.count(new_literal),
        "reverse_binding_exact": True,
    }


def _validate_source_bindings(value: object) -> dict[str, str]:
    expected = {
        "future_runner_sha256",
        "generated_helper_sha256",
        "controller_module_sha256",
    }
    if not isinstance(value, dict) or set(value) != expected:
        raise FutureAttemptRebindingError("source_bindings_invalid")
    for key, digest in value.items():
        _digest(digest, key)
    return value


def build_bundle_manifest(
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    source_bindings: dict[str, str],
    target_path: str,
) -> dict[str, Any]:
    return validate_bundle_manifest(
        {
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "operation_id": operation_id,
            "attempt_id": attempt_id,
            "candidate_source": candidate_source,
            "source_bindings": source_bindings,
            "target_binding": build_target_binding(target_path),
            "path_roster": list(base.PATH_ROSTER),
            "occupied_launch_authorized": False,
            "execution_authority": {key: False for key in base.PROCESS_FLAGS},
            "raw_retention": {key: False for key in base.RAW_FLAGS},
        }
    )


def validate_bundle_manifest(value: object) -> dict[str, Any]:
    expected_keys = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "candidate_source",
        "source_bindings",
        "target_binding",
        "path_roster",
        "occupied_launch_authorized",
        "execution_authority",
        "raw_retention",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise FutureAttemptRebindingError("bundle_keys_invalid")
    if value["schema_version"] != BUNDLE_SCHEMA_VERSION:
        raise FutureAttemptRebindingError("bundle_schema_invalid")
    _identity(value["operation_id"], "operation_id")
    _identity(value["attempt_id"], "attempt_id")
    _candidate_source(value["candidate_source"])
    _validate_source_bindings(value["source_bindings"])
    validate_target_binding(value["target_binding"])
    try:
        base._validate_roster(value["path_roster"])
    except base.FutureAttemptMaterialisationError as error:
        raise FutureAttemptRebindingError("path_roster_invalid") from error
    if value["occupied_launch_authorized"] is not False:
        raise FutureAttemptRebindingError("occupied_launch_authority_invalid")
    for key, expected in (
        ("execution_authority", set(base.PROCESS_FLAGS)),
        ("raw_retention", set(base.RAW_FLAGS)),
    ):
        flags = value[key]
        if (
            not isinstance(flags, dict)
            or set(flags) != expected
            or any(flag is not False for flag in flags.values())
        ):
            raise FutureAttemptRebindingError(f"{key}_invalid")
    return value


def bundle_manifest_bytes(value: object) -> bytes:
    return canonical_json_bytes(
        validate_bundle_manifest(value), maximum=MAX_MANIFEST_BYTES
    )


def materialize_rebound_future_attempt(
    *,
    disposable_parent: Path,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    target_path: str,
    runner_payload: bytes,
    helper_payload: bytes,
    controller_payload: bytes,
    expected_bindings: dict[str, str],
) -> dict[str, Any]:
    """Write one rebound future-attempt fixture through the accepted path gears."""

    try:
        parent = base._require_absolute_directory(
            disposable_parent, "disposable_parent"
        )
    except base.FutureAttemptMaterialisationError as error:
        raise FutureAttemptRebindingError("disposable_parent_invalid") from error
    _identity(operation_id, "operation_id")
    _identity(attempt_id, "attempt_id")
    _candidate_source(candidate_source)
    target = validate_target_path(target_path)
    observed = {
        "future_runner_sha256": sha256_bytes(runner_payload),
        "generated_helper_sha256": sha256_bytes(helper_payload),
        "controller_module_sha256": sha256_bytes(controller_payload),
    }
    if _validate_source_bindings(expected_bindings) != observed:
        raise FutureAttemptRebindingError("materialisation_source_binding_mismatch")
    target_literal = json.dumps(target).encode()
    identity_literals = tuple(
        json.dumps(value).encode()
        for value in (operation_id, attempt_id, candidate_source)
    )
    if runner_payload.count(target_literal) != 1 or any(
        helper_payload.count(literal) != 1 for literal in identity_literals
    ):
        raise FutureAttemptRebindingError("materialisation_semantic_binding_mismatch")
    diagnostic.validate_helper_source(helper_payload)
    if (
        len(runner_payload) > base.MAX_SOURCE_BYTES
        or len(helper_payload) > base.MAX_SOURCE_BYTES
    ):
        raise FutureAttemptRebindingError("materialisation_source_size_exceeded")
    root = parent / attempt_id
    if root.exists() or root.is_symlink():
        raise FutureAttemptRebindingError("attempt_root_must_be_absent")
    try:
        root.mkdir()
        (root / "runner").mkdir()
        (root / "control").mkdir()
        manifest = build_bundle_manifest(
            operation_id=operation_id,
            attempt_id=attempt_id,
            candidate_source=candidate_source,
            source_bindings=observed,
            target_path=target,
        )
        base._write_exclusive(
            base._path(root, base.RUNNER_RELATIVE_PATH), runner_payload
        )
        base._write_exclusive(
            base._path(root, base.HELPER_RELATIVE_PATH), helper_payload
        )
        base._write_exclusive(
            base._path(root, base.BUNDLE_RELATIVE_PATH), bundle_manifest_bytes(manifest)
        )
    except (OSError, base.FutureAttemptMaterialisationError) as error:
        raise FutureAttemptRebindingError("materialisation_write_failed") from error
    reading = read_rebound_bundle(
        root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
        target_path=target,
        expected_bindings=observed,
    )
    if reading["files"] != sorted(base.INITIAL_PATHS):
        raise FutureAttemptRebindingError("initial_materialisation_roster_invalid")
    return reading


def read_rebound_bundle(
    root: Path,
    *,
    operation_id: str,
    attempt_id: str,
    candidate_source: str,
    target_path: str,
    expected_bindings: dict[str, str],
) -> dict[str, Any]:
    if not root.is_absolute():
        raise FutureAttemptRebindingError("attempt_root_must_be_absolute")
    _identity(operation_id, "operation_id")
    _identity(attempt_id, "attempt_id")
    _candidate_source(candidate_source)
    target = validate_target_path(target_path)
    bindings = _validate_source_bindings(expected_bindings)
    try:
        files = base._tree_files(root)
        payload = base._read_limited(
            base._path(root, base.BUNDLE_RELATIVE_PATH),
            MAX_MANIFEST_BYTES,
            "bundle_manifest_file",
        )
    except base.FutureAttemptMaterialisationError as error:
        raise FutureAttemptRebindingError(str(error)) from error
    try:
        manifest = validate_bundle_manifest(json.loads(payload))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise FutureAttemptRebindingError("bundle_manifest_json_invalid") from error
    if payload != bundle_manifest_bytes(manifest):
        raise FutureAttemptRebindingError("bundle_manifest_canonical_bytes_required")
    if (
        manifest["operation_id"] != operation_id
        or manifest["attempt_id"] != attempt_id
        or manifest["candidate_source"] != candidate_source
    ):
        raise FutureAttemptRebindingError("bundle_runtime_identity_mismatch")
    if manifest["source_bindings"] != bindings:
        raise FutureAttemptRebindingError("bundle_source_binding_mismatch")
    if manifest["target_binding"] != build_target_binding(target):
        raise FutureAttemptRebindingError("bundle_target_binding_mismatch")
    try:
        runner_payload = base._read_limited(
            base._path(root, base.RUNNER_RELATIVE_PATH),
            base.MAX_SOURCE_BYTES,
            "runner_file",
        )
        helper_payload = base._read_limited(
            base._path(root, base.HELPER_RELATIVE_PATH),
            base.MAX_SOURCE_BYTES,
            "helper_file",
        )
    except base.FutureAttemptMaterialisationError as error:
        raise FutureAttemptRebindingError(str(error)) from error
    if (
        sha256_bytes(runner_payload) != bindings["future_runner_sha256"]
        or sha256_bytes(helper_payload) != bindings["generated_helper_sha256"]
    ):
        raise FutureAttemptRebindingError("materialized_source_digest_mismatch")
    if runner_payload.count(json.dumps(target).encode()) != 1:
        raise FutureAttemptRebindingError("materialized_target_binding_mismatch")
    return {
        "root": root,
        "manifest": manifest,
        "files": sorted(files),
        "runner_bytes": len(runner_payload),
        "helper_bytes": len(helper_payload),
    }


def write_broker_fixture(root: Path, value: object) -> Path:
    try:
        return base.write_broker_fixture(root, value)
    except base.FutureAttemptMaterialisationError as error:
        raise FutureAttemptRebindingError(str(error)) from error


def write_sidecar_fixture(root: Path, value: object) -> Path:
    try:
        return base.write_sidecar_fixture(root, value)
    except base.FutureAttemptMaterialisationError as error:
        raise FutureAttemptRebindingError(str(error)) from error


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
        "target_binding",
        "occupied_launch_authorized",
        "raw_stream_read",
        "raw_error_retained",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise FutureAttemptRebindingError("controller_terminal_keys_invalid")
    if value["schema_version"] != TERMINAL_SCHEMA_VERSION:
        raise FutureAttemptRebindingError("controller_terminal_schema_invalid")
    _identity(value["operation_id"], "operation_id")
    _identity(value["attempt_id"], "attempt_id")
    _candidate_source(value["candidate_source"])
    if value["coordinate"] not in controller.COORDINATES:
        raise FutureAttemptRebindingError("controller_terminal_coordinate_invalid")
    for key in ("diagnostic_accepted", "broker_zero", "pre_request_supported"):
        if type(value[key]) is not bool:
            raise FutureAttemptRebindingError("controller_terminal_boolean_invalid")
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
    if value["coordinate"] != expected_coordinate or value[
        "pre_request_supported"
    ] is not (accepted and broker_zero):
        raise FutureAttemptRebindingError("controller_terminal_relationship_invalid")
    closed_fields = (value["stage"], value["cause_coordinate"], value["error_kind"])
    if accepted:
        diagnostic.validate_diagnostic(
            {
                "schema_version": diagnostic.SCHEMA_VERSION,
                "operation_id": value["operation_id"],
                "attempt_id": value["attempt_id"],
                "candidate_source": value["candidate_source"],
                "stage": value["stage"],
                "cause_coordinate": value["cause_coordinate"],
                "error_kind": value["error_kind"],
                "raw_error_message_retained": False,
                "raw_stack_retained": False,
                "raw_paths_retained": False,
                "raw_cause_retained": False,
            }
        )
    elif any(item is not None for item in closed_fields):
        raise FutureAttemptRebindingError("controller_terminal_diagnostic_invalid")
    _validate_source_bindings(value["source_bindings"])
    validate_target_binding(value["target_binding"])
    for key in ("occupied_launch_authorized", "raw_stream_read", "raw_error_retained"):
        if value[key] is not False:
            raise FutureAttemptRebindingError(
                "controller_terminal_raw_or_authority_invalid"
            )
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
    target_path: str,
    expected_bindings: dict[str, str],
) -> dict[str, Any]:
    terminal_path = base._path(root, base.TERMINAL_RELATIVE_PATH)
    if terminal_path.exists() or terminal_path.is_symlink():
        raise FutureAttemptRebindingError("controller_terminal_must_be_absent")
    reading = read_rebound_bundle(
        root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
        target_path=target_path,
        expected_bindings=expected_bindings,
    )
    broker_path = base._path(root, base.BROKER_RELATIVE_PATH)
    if base.BROKER_RELATIVE_PATH not in reading["files"]:
        raise FutureAttemptRebindingError("broker_reading_required")
    selection = controller.select_post_hmr_failure(
        diagnostic_path=base._path(root, base.SIDECAR_RELATIVE_PATH),
        broker_reading_path=broker_path,
        disposable_root=root,
        operation_id=operation_id,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
    )
    manifest = reading["manifest"]
    terminal = validate_controller_terminal(
        {
            "schema_version": TERMINAL_SCHEMA_VERSION,
            "operation_id": operation_id,
            "attempt_id": attempt_id,
            "candidate_source": candidate_source,
            "coordinate": selection["coordinate"],
            "diagnostic_accepted": selection["diagnostic_accepted"],
            "broker_zero": selection["broker_zero"],
            "pre_request_supported": selection["pre_request_supported"],
            "stage": selection["stage"],
            "cause_coordinate": selection["cause_coordinate"],
            "error_kind": selection["error_kind"],
            "source_bindings": manifest["source_bindings"],
            "target_binding": manifest["target_binding"],
            "occupied_launch_authorized": False,
            "raw_stream_read": False,
            "raw_error_retained": False,
        }
    )
    payload = controller_terminal_bytes(terminal)
    try:
        base._write_exclusive(terminal_path, payload)
        observed = base._read_limited(
            terminal_path, MAX_TERMINAL_BYTES, "controller_terminal_file"
        )
    except base.FutureAttemptMaterialisationError as error:
        raise FutureAttemptRebindingError(str(error)) from error
    if observed != payload:
        raise FutureAttemptRebindingError("controller_terminal_readback_mismatch")
    return terminal

"""Closed coordinates for native-Harness edit argument/result observations."""

from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "ariadne.native_harness_edit_argument_result_coordinate.v1"

COORDINATES = (
    "edit_success_unique_match",
    "edit_success_replace_all",
    "edit_error_invalid_args",
    "edit_error_untyped_argument_constraint",
    "edit_error_fs_stale_version",
    "edit_error_fs_edit_not_found",
    "edit_error_fs_ambiguous_edit",
)

_OBSERVATION_KEYS = frozenset(
    {
        "result_kind",
        "structured_error_code",
        "success_class",
        "target_changed",
    }
)

_MAPPING = {
    ("success", None, "unique_match", True): "edit_success_unique_match",
    ("success", None, "replace_all", True): "edit_success_replace_all",
    ("error", "INVALID_ARGS", None, False): "edit_error_invalid_args",
    (
        "error",
        None,
        None,
        False,
    ): "edit_error_untyped_argument_constraint",
    (
        "error",
        "FS_STALE_VERSION",
        None,
        False,
    ): "edit_error_fs_stale_version",
    (
        "error",
        "FS_EDIT_NOT_FOUND",
        None,
        False,
    ): "edit_error_fs_edit_not_found",
    (
        "error",
        "FS_AMBIGUOUS_EDIT",
        None,
        False,
    ): "edit_error_fs_ambiguous_edit",
}


class NativeEditCoordinateError(ValueError):
    """An edit observation is outside the closed coordinate vocabulary."""


def classify_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Validate and classify one exact edit observation."""

    if not isinstance(observation, dict) or set(observation) != _OBSERVATION_KEYS:
        raise NativeEditCoordinateError("observation_keys_invalid")
    result_kind = observation["result_kind"]
    error_code = observation["structured_error_code"]
    success_class = observation["success_class"]
    target_changed = observation["target_changed"]
    if result_kind not in {"success", "error"}:
        raise NativeEditCoordinateError("result_kind_invalid")
    if error_code not in {
        None,
        "INVALID_ARGS",
        "FS_STALE_VERSION",
        "FS_EDIT_NOT_FOUND",
        "FS_AMBIGUOUS_EDIT",
    }:
        raise NativeEditCoordinateError("structured_error_code_invalid")
    if success_class not in {None, "unique_match", "replace_all"}:
        raise NativeEditCoordinateError("success_class_invalid")
    if not isinstance(target_changed, bool):
        raise NativeEditCoordinateError("target_changed_invalid")
    coordinate = _MAPPING.get(
        (result_kind, error_code, success_class, target_changed)
    )
    if coordinate is None:
        raise NativeEditCoordinateError("observation_combination_invalid")
    return {
        "schema_version": SCHEMA_VERSION,
        **observation,
        "coordinate": coordinate,
    }


def validate_coordinate(value: dict[str, Any]) -> dict[str, Any]:
    """Require an already released coordinate to equal its classified tuple."""

    expected_keys = _OBSERVATION_KEYS | {"schema_version", "coordinate"}
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise NativeEditCoordinateError("coordinate_keys_invalid")
    if value["schema_version"] != SCHEMA_VERSION:
        raise NativeEditCoordinateError("schema_version_invalid")
    if value["coordinate"] not in COORDINATES:
        raise NativeEditCoordinateError("coordinate_invalid")
    observation = {key: value[key] for key in _OBSERVATION_KEYS}
    released = classify_observation(observation)
    if released != value:
        raise NativeEditCoordinateError("coordinate_mismatch")
    return value

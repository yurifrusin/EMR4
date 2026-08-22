"""Closed provider-free coordinates for one native-Harness tool lifecycle."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SCHEMA_VERSION = "ariadne.native_harness_tool_result_conclusion_coordinate.v1"

INPUT_RESULT_KINDS = frozenset({"success", "error"})
POST_EXECUTE_DECISION_KINDS = frozenset({"accept", "block", "failed"})
CONCLUSION_REQUEST_STAGES = frozenset(
    {
        "pre_execute_after_boundary_accept",
        "post_execute_after_decision",
        "not_requested",
    }
)
AUTHORITATIVE_FINAL_RESULT_KINDS = frozenset(
    {"success_concluding", "success_nonconcluding", "error"}
)
TURN_KINDS = frozenset({"completed", "error"})

_OBSERVATION_FIELDS = (
    "input_result_kind",
    "post_execute_decision_kind",
    "conclusion_request_stage",
    "authoritative_final_result_kind",
    "turn_kind",
)
_OBSERVATION_KEYS = frozenset(_OBSERVATION_FIELDS)

_COORDINATES_BY_TUPLE = {
    (
        "success",
        "accept",
        "pre_execute_after_boundary_accept",
        "success_concluding",
        "completed",
    ): "edit_success_accept_concluded",
    (
        "success",
        "accept",
        "post_execute_after_decision",
        "success_nonconcluding",
        "error",
    ): "edit_success_accept_late_marker",
    (
        "error",
        "accept",
        "pre_execute_after_boundary_accept",
        "error",
        "error",
    ): "edit_error_accept_not_concluded",
    (
        "success",
        "block",
        "pre_execute_after_boundary_accept",
        "error",
        "error",
    ): "edit_success_blocked_not_concluded",
    (
        "success",
        "failed",
        "pre_execute_after_boundary_accept",
        "error",
        "error",
    ): "post_execute_decision_failed_not_concluded",
}

COORDINATES = tuple(_COORDINATES_BY_TUPLE.values())


class ToolResultConclusionCoordinateError(ValueError):
    """A tool-result/conclusion observation is outside the closed vocabulary."""


def _closed_text(value: object, allowed: frozenset[str], label: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ToolResultConclusionCoordinateError(f"{label}_invalid")
    return value


def classify_observation(value: object) -> dict[str, Any]:
    """Validate one closed observation and return its unique coordinate."""

    if not isinstance(value, Mapping) or set(value) != _OBSERVATION_KEYS:
        raise ToolResultConclusionCoordinateError("observation_keys_invalid")
    fields = (
        _closed_text(
            value["input_result_kind"],
            INPUT_RESULT_KINDS,
            "input_result_kind",
        ),
        _closed_text(
            value["post_execute_decision_kind"],
            POST_EXECUTE_DECISION_KINDS,
            "post_execute_decision_kind",
        ),
        _closed_text(
            value["conclusion_request_stage"],
            CONCLUSION_REQUEST_STAGES,
            "conclusion_request_stage",
        ),
        _closed_text(
            value["authoritative_final_result_kind"],
            AUTHORITATIVE_FINAL_RESULT_KINDS,
            "authoritative_final_result_kind",
        ),
        _closed_text(value["turn_kind"], TURN_KINDS, "turn_kind"),
    )
    try:
        coordinate = _COORDINATES_BY_TUPLE[fields]
    except KeyError as error:
        raise ToolResultConclusionCoordinateError(
            "observation_combination_unadmitted"
        ) from error
    return {
        "schema_version": SCHEMA_VERSION,
        **dict(zip(_OBSERVATION_FIELDS, fields, strict=True)),
        "coordinate": coordinate,
    }


def validate_coordinate(value: object) -> dict[str, Any]:
    """Validate a released coordinate against a fresh classification."""

    if not isinstance(value, Mapping) or set(value) != {
        "schema_version",
        *_OBSERVATION_KEYS,
        "coordinate",
    }:
        raise ToolResultConclusionCoordinateError("coordinate_keys_invalid")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ToolResultConclusionCoordinateError("coordinate_schema_invalid")
    observation = {key: value[key] for key in _OBSERVATION_KEYS}
    expected = classify_observation(observation)
    if value["coordinate"] != expected["coordinate"]:
        raise ToolResultConclusionCoordinateError("coordinate_mismatch")
    return dict(value)

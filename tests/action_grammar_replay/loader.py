"""Loader for synthetic action-grammar replay fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "action_grammar_replay"
REPLAY_SCHEMA_VERSION = "action_grammar_replay.v1"
REQUIRED_SOURCE = "authored_synthetic"
KNOWN_DISPATCH_VALUES = {
    "route_to_confirm",
    "route_read_only",
    "route_meta",
    "refuse_not_implemented",
    "refuse_unknown_action",
}
ALLOWED_TOP_LEVEL_KEYS = {
    "id",
    "schema_version",
    "source",
    "description",
    "actions",
}
ALLOWED_ACTION_KEYS = {
    "raw_name",
    "expected_verb",
    "expected_dispatch",
    "expected_mutating",
    "expected_implemented",
    "requires_staff_confirmation",
    "confirm_actions_non_empty",
    "affordance_case",
    "expected_affordance_allowed",
    "expected_affordance_gate",
}
FORBIDDEN_ACTION_KEYS = {
    "payload",
    "context",
    "evidence",
    "confirmation_evidence",
    "patient",
    "patient_id",
    "practitioner",
    "practitioner_id",
    "appointment",
    "appointment_id",
    "slot",
    "slot_id",
    "route",
    "endpoint",
}
FORBIDDEN_TEXT_FRAGMENTS = {
    "h_series",
    "h-series",
    "h series",
    "h_series_neutral_profile",
    "no_structural_change",
    "small_content_delta",
    "large_unexplained_delta",
    "time_grid_delta",
    "local_data",
    "historical-diary-trove",
    "historical_diary_trove",
    "raw_trove",
    "full_trove",
    "full-trove",
    "patient:",
    "patients:",
    "practitioner:",
    "practitioners:",
    "staff:",
}


def _serialized_lower(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).lower()


def load_day_script(path: Path) -> dict[str, Any]:
    """Load and validate one authored synthetic replay fixture."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name}: expected JSON object")

    if payload.get("profile_kind") == "h_series_neutral_profile":
        raise ValueError(f"{path.name}: H-series profiles are not executable replay fixtures")
    if str(payload.get("schema_version", "")).startswith("h_series."):
        raise ValueError(f"{path.name}: H-series schema versions are not replay fixtures")
    if payload.get("schema_version") != REPLAY_SCHEMA_VERSION:
        raise ValueError(f"{path.name}: schema_version must be {REPLAY_SCHEMA_VERSION!r}")
    if payload.get("source") != REQUIRED_SOURCE:
        raise ValueError(f"{path.name}: source must be {REQUIRED_SOURCE!r}")

    extra_top_level = sorted(set(payload) - ALLOWED_TOP_LEVEL_KEYS)
    if extra_top_level:
        raise ValueError(f"{path.name}: unsupported top-level key(s) {extra_top_level}")

    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError(f"{path.name}: actions must be a non-empty list")

    serialized = _serialized_lower(payload)
    leaked = sorted(fragment for fragment in FORBIDDEN_TEXT_FRAGMENTS if fragment in serialized)
    if leaked:
        raise ValueError(f"{path.name}: forbidden replay fixture fragment(s) {leaked}")

    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise ValueError(f"{path.name}: actions[{index}] must be an object")
        blocked_action_keys = sorted(set(action) & FORBIDDEN_ACTION_KEYS)
        if blocked_action_keys:
            raise ValueError(
                f"{path.name}: actions[{index}] forbidden action payload key(s) "
                f"{blocked_action_keys}"
            )
        extra_action_keys = sorted(set(action) - ALLOWED_ACTION_KEYS)
        if extra_action_keys:
            raise ValueError(
                f"{path.name}: actions[{index}] unsupported action key(s) {extra_action_keys}"
            )
        if not action.get("raw_name"):
            raise ValueError(f"{path.name}: actions[{index}].raw_name is required")
        dispatch = action.get("expected_dispatch")
        if dispatch not in KNOWN_DISPATCH_VALUES:
            raise ValueError(
                f"{path.name}: actions[{index}].expected_dispatch must be one of "
                f"{sorted(KNOWN_DISPATCH_VALUES)}"
            )

    return payload


def discover_day_scripts(fixture_dir: Path = FIXTURE_DIR) -> list[dict[str, Any]]:
    """Load every explicitly authored JSON replay fixture."""
    if not fixture_dir.is_dir():
        raise ValueError(f"Replay fixture directory not found: {fixture_dir}")
    paths = sorted(fixture_dir.glob("*.json"))
    if not paths:
        raise ValueError(f"No replay fixtures found in {fixture_dir}")
    return [load_day_script(path) for path in paths]

"""Source-safe consistency checks for H-series neutral profile fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


PROFILE_DIR = Path(__file__).resolve().parent / "fixtures" / "h_series_profiles"
ALLOWED_EVENT_CLASSES = {"no_structural_change", "small_content_delta"}
REQUIRED_EXCLUDED_EVENT_CLASSES = {"large_unexplained_delta", "time_grid_delta"}
FORBIDDEN_KEYS = {
    "raw_path",
    "raw_paths",
    "filename",
    "filenames",
    "patient",
    "patients",
    "staff",
    "appointment_text",
    "document_text",
    "source_timestamp",
    "source_timestamps",
}
FORBIDDEN_PROMOTION_WORDS = {
    "booked",
    "booking burst",
    "cancelled appointment",
    "moved appointment",
    "patient arrived",
}


def _load_profiles() -> list[tuple[Path, dict[str, Any]]]:
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")
    if not PROFILE_DIR.is_dir():
        pytest.skip(f"H-series profile directory not found: {PROFILE_DIR}")

    profiles: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(PROFILE_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        if payload is None:
            continue
        if not isinstance(payload, dict):
            pytest.fail(f"{path.name}: expected YAML mapping")
        profiles.append((path, payload))
    return profiles


def test_h_series_profiles_have_required_safe_shape():
    errors: list[str] = []

    for path, profile in _load_profiles():
        profile_id = profile.get("id", "<no id>")
        if profile.get("profile_kind") != "h_series_neutral_profile":
            errors.append(f"{path.name} [{profile_id}]: invalid profile_kind")

        source_docs = profile.get("source_docs")
        if not isinstance(source_docs, list) or not source_docs:
            errors.append(f"{path.name} [{profile_id}]: source_docs required")
        elif not all(str(doc).startswith("docs/historical-diary-trove-") for doc in source_docs):
            errors.append(
                f"{path.name} [{profile_id}]: source_docs must reference committed H-series docs"
            )

        sample = profile.get("sample") or {}
        for key in ("root_count", "snapshot_count", "adjacent_transition_count"):
            if not isinstance(sample.get(key), int) or sample[key] <= 0:
                errors.append(f"{path.name} [{profile_id}]: sample.{key} must be positive int")

        privacy = profile.get("privacy") or {}
        required_privacy = {
            "source_safe_only": True,
            "semantic_labels": "blocked",
            "raw_trove_access": "prohibited",
            "external_provider_calls": "prohibited",
            "raw_identifiers": "prohibited",
        }
        for key, expected in required_privacy.items():
            if privacy.get(key) != expected:
                errors.append(
                    f"{path.name} [{profile_id}]: privacy.{key} must be {expected!r}"
                )

    assert not errors, "H-series profile shape violations:\n" + "\n".join(errors)


def test_h_series_profiles_do_not_smuggle_semantics():
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")
    errors: list[str] = []

    for path, profile in _load_profiles():
        profile_id = profile.get("id", "<no id>")
        events = profile.get("neutral_event_classes") or {}
        allowed = set(events.get("allowed") or [])
        excluded = set(events.get("excluded") or [])

        if not allowed or not allowed.issubset(ALLOWED_EVENT_CLASSES):
            errors.append(
                f"{path.name} [{profile_id}]: allowed event classes must be subset of "
                f"{sorted(ALLOWED_EVENT_CLASSES)}"
            )
        if not REQUIRED_EXCLUDED_EVENT_CLASSES.issubset(excluded):
            errors.append(
                f"{path.name} [{profile_id}]: excluded event classes must include "
                f"{sorted(REQUIRED_EXCLUDED_EVENT_CLASSES)}"
            )

        serialized = yaml.safe_dump(profile).lower()
        leaked_keys = sorted(key for key in FORBIDDEN_KEYS if f"{key}:" in serialized)
        if leaked_keys:
            errors.append(
                f"{path.name} [{profile_id}]: forbidden H-series key(s) {leaked_keys}"
            )

        promotions = sorted(word for word in FORBIDDEN_PROMOTION_WORDS if word in serialized)
        if promotions:
            errors.append(
                f"{path.name} [{profile_id}]: semantic promotion wording {promotions}"
            )

    assert not errors, "H-series profile semantic violations:\n" + "\n".join(errors)

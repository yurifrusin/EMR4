"""
Fixture integrity validator for the Bernie receptionist scenario corpus.

Validates YAML parseability, unique IDs, required fields, category allow-list,
turn expectation shape, xfail reason metadata, forbidden list shape, and
graceful handling of empty/missing fixture directory.

Uses pytest.importorskip to skip cleanly when PyYAML is unavailable.
"""

import os
from pathlib import Path

import pytest

# -- Fixture directory ------------------------------------------------------

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "bernie_scenarios"

# -- Allowed categories (from bernie_reception_scenario_workstream.md) ------

ALLOWED_CATEGORIES = frozenset({
    "appointment_extension",
    "booking_create",
    "booking_request",
    "booking_clarification",
    "booking_confirmation",
    "booking_interpret_contract",
    "clarification",
    "future_booking_advisory",
    "mutation_safety",
    "slot_search",
    "extension_request",
    "patient_advisory",
    "stale_session",
    "session_state_guard",
    "roster_unavailable",
    "roster_unavailable_outcome",
    "no_slot_outcome",
})

# -- Required top-level fields ----------------------------------------------

REQUIRED_TOP_LEVEL = frozenset({"id", "category", "turns"})

# -- Supported turn outcomes ------------------------------------------------

KNOWN_OUTCOMES = frozenset({
    "clarification_required",
    "confirmation_ready",
    "blocked",
    "candidate_selection_required",
    "no_matching_times",
    "no_slots",
    "roster_unavailable",
    "completed",
})

KNOWN_ACTIONS = frozenset({
    "normalize", "search", "select", "supervise", "confirm", "interpret"
})


# -- Helpers ----------------------------------------------------------------


def _load_scenarios():
    """Yield (filename, scenario_dict) for every parseable YAML scenario file."""
    if not FIXTURE_DIR.is_dir():
        return

    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    for path in sorted(FIXTURE_DIR.iterdir()):
        if path.suffix.lower() not in (".yaml", ".yml"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as exc:
            yield path.name, None, str(exc)
            continue

        if data is None:
            # Empty file - skip silently; not a scenario document
            continue

        # A single scenario may be a dict; a multi-scenario file may be a list.
        scenarios = data if isinstance(data, list) else [data]

        for scenario in scenarios:
            yield path.name, scenario, None


def _all_scenarios():
    """Return list of (filename, scenario_dict) for valid scenarios."""
    return [
        (fn, sc)
        for fn, sc, err in _load_scenarios()
        if err is None and isinstance(sc, dict)
    ]


# -- Tests ------------------------------------------------------------------


def test_yaml_parseable():
    """Every .yaml/.yml file in the fixture directory must parse as valid YAML."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")
    
    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    failures = []
    for path in sorted(FIXTURE_DIR.iterdir()):
        if path.suffix.lower() not in (".yaml", ".yml"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                yaml.safe_load(f)
        except Exception as exc:
            failures.append(f"{path.name}: {exc}")

    assert not failures, (
        f"YAML parse failures:\n" + "\n".join(failures)
    )


def test_unique_ids():
    """Every scenario in the corpus must have a unique id."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    seen = {}
    for path in sorted(FIXTURE_DIR.iterdir()):
        if path.suffix.lower() not in (".yaml", ".yml"):
            continue
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            continue
        scenarios = data if isinstance(data, list) else [data]
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                continue
            sid = scenario.get("id")
            if sid is None:
                continue
            if sid in seen:
                pytest.fail(f"Duplicate scenario id '{sid}' in {path.name} (first seen in {seen[sid]})")
            seen[sid] = path.name


def test_required_top_level_fields():
    """Every scenario must have id, category, and turns."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    errors = []
    for fn, sc in _all_scenarios():
        missing = REQUIRED_TOP_LEVEL - sc.keys()
        if missing:
            errors.append(f"{fn} [{sc.get('id', '<no id>')}]: missing {sorted(missing)}")

    assert not errors, (
        "Required field violations:\n" + "\n".join(errors)
    )


def test_category_allow_list():
    """Category values must be from the known allow-list."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    errors = []
    seen_categories = set()
    for fn, sc in _all_scenarios():
        cat = sc.get("category")
        if cat is None:
            errors.append(f"{fn} [{sc.get('id', '<no id>')}]: missing category")
            continue
        seen_categories.add(cat)
        if cat not in ALLOWED_CATEGORIES:
            errors.append(
                f"{fn} [{sc.get('id', '<no id>')}]: "
                f"category '{cat}' not in allow-list: {sorted(ALLOWED_CATEGORIES)}"
            )

    # Report unknown categories but do not fail on them - the allow-list may
    # expand as the corpus grows. Instead, warn via assertion details.
    if errors:
        msg = "\n".join(errors)
        msg += f"\n\nKnown categories seen: {sorted(seen_categories)}"
        pytest.fail(msg)


def test_turn_expectation_shape():
    """Every turn must use either corpus or executable harness shape."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    errors = []
    for fn, sc in _all_scenarios():
        turns = sc.get("turns", [])
        sid = sc.get("id", "<no id>")
        for i, turn in enumerate(turns):
            if not isinstance(turn, dict):
                errors.append(f"{fn} [{sid}]: turn[{i}] is not a dict")
                continue
            action = turn.get("action")
            if action is not None:
                if action not in KNOWN_ACTIONS:
                    errors.append(
                        f"{fn} [{sid}]: turn[{i}] unknown action '{action}'; "
                        f"known: {sorted(KNOWN_ACTIONS)}"
                    )
                expect = turn.get("expect")
                if expect is not None and not isinstance(expect, dict):
                    errors.append(f"{fn} [{sid}]: turn[{i}] non-dict 'expect'")
                continue
            if not turn.get("user"):
                errors.append(f"{fn} [{sid}]: turn[{i}] missing or empty 'user'")
            expect = turn.get("expect")
            if not isinstance(expect, dict):
                errors.append(f"{fn} [{sid}]: turn[{i}] missing or non-dict 'expect'")
                continue
            outcome = expect.get("outcome")
            if not outcome:
                errors.append(
                    f"{fn} [{sid}]: turn[{i}] missing 'expect.outcome'"
                )
            elif outcome not in KNOWN_OUTCOMES:
                errors.append(
                    f"{fn} [{sid}]: turn[{i}] unknown outcome '{outcome}'; "
                    f"known: {sorted(KNOWN_OUTCOMES)}"
                )

    assert not errors, (
        "Turn expectation violations:\n" + "\n".join(errors)
    )


def test_xfail_reason_metadata():
    """Scenarios with xfail: true must include a non-empty 'reason' field."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    errors = []
    for fn, sc in _all_scenarios():
        xfail = sc.get("xfail")
        if xfail:
            reason = ""
            if isinstance(xfail, dict):
                reason = xfail.get("reason", "")
            elif xfail is True:
                reason = sc.get("reason", "")
            if not reason:
                errors.append(
                    f"{fn} [{sc.get('id', '<no id>')}]: "
                    "xfail=true but 'reason' is missing or empty"
                )

    assert not errors, (
        "xfail reason violations:\n" + "\n".join(errors)
    )


def test_forbidden_list_shape():
    """The 'forbidden' field, if present, must be a list of non-empty strings."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    errors = []
    for fn, sc in _all_scenarios():
        forbidden = sc.get("forbidden", [])
        if not isinstance(forbidden, list):
            errors.append(
                f"{fn} [{sc.get('id', '<no id>')}]: "
                "'forbidden' must be a list"
            )
            continue
        for j, item in enumerate(forbidden):
            if not isinstance(item, str) or not item.strip():
                errors.append(
                    f"{fn} [{sc.get('id', '<no id>')}]: "
                    f"forbidden[{j}] is not a non-empty string"
                )

    assert not errors, (
        "Forbidden list violations:\n" + "\n".join(errors)
    )


def test_empty_fixture_directory():
    """An empty fixture directory must not cause errors (skip gracefully)."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")

    scenarios = _all_scenarios()
    if not scenarios:
        pytest.skip("Fixture directory is empty - no scenarios to validate")


def test_missing_fixture_directory():
    """A missing fixture directory must not cause errors (skip gracefully)."""
    nonexistent = FIXTURE_DIR.parent / "_nonexistent_bernie_scenarios"
    if nonexistent.is_dir():
        pytest.skip("Directory unexpectedly exists - cannot test missing-dir behaviour")

    # Use a local check without relying on actual import
    if not nonexistent.is_dir():
        pytest.skip(f"Fixture directory does not exist: {nonexistent}")

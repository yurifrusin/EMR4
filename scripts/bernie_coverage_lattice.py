#!/usr/bin/env python3
"""Coverage lattice reporter for the Bernie reception-agent scenario corpus.

Discovers committed ``ReceptionScenarioSpec`` fixtures, builds a coverage
lattice across five dimensions (diary_action, diary_state, temporal_form,
dialogue_form, language_form), and reports gaps as explicit empty cells.

Usage:
    python scripts/bernie_coverage_lattice.py
    python scripts/bernie_coverage_lattice.py --fixture-dir tests/fixtures/bernie_scenario_spec
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent


# ---------------------------------------------------------------------------
# Coverage dimensions
# ---------------------------------------------------------------------------

DIARY_ACTIONS: List[str] = [
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "explain_schedule",
]

DIARY_STATES: List[str] = [
    "empty",
    "exact_duplicate",
    "overlap",
    "same_day_distinct",
    "terminal",
    "stale",
    "concurrent",
    "roster_absent",
    "break",
    "no_slots",
    "elapsed_window",
]

TEMPORAL_FORMS: List[str] = [
    "exact",
    "not_before",
    "not_after",
    "interval",
    "approximate",
    "unspecified",
]

DIALOGUE_FORMS: List[str] = [
    "one_shot",
    "clarification",
    "correction",
    "reversal",
    "ellipsis",
    "anaphora",
    "repeated",
    "session_restart",
]

LANGUAGE_FORMS: List[str] = [
    "plain",
    "paraphrase",
    "filler",
    "abbreviation",
    "typo",
    "speech_like",
    "punctuation_variant",
    "adversarial",
]


# ---------------------------------------------------------------------------
# Fixture loading
# ---------------------------------------------------------------------------

def discover_fixtures(fixture_dir: Path) -> List[Dict[str, Any]]:
    """Discover and load all JSON fixture files in *fixture_dir*."""
    if not fixture_dir.is_dir():
        raise NotADirectoryError(
            f"Fixture directory does not exist: {fixture_dir}"
        )
    fixtures: List[Dict[str, Any]] = []
    for path in sorted(fixture_dir.iterdir()):
        if path.suffix.lower() == ".json":
            with open(path, "r", encoding="utf-8") as fh:
                fixtures.append(json.load(fh))
    if not fixtures:
        raise ValueError(
            f"No JSON fixtures found in {fixture_dir} (directory is empty)"
        )
    return fixtures


# ---------------------------------------------------------------------------
# Lattice building
# ---------------------------------------------------------------------------

def _infer_diary_state(fixture: Dict[str, Any]) -> str:
    """Infer the diary-state dimension from a fixture."""
    initial = fixture.get("initial_diary_state", {})
    seeded = initial.get("seeded_appointments", [])
    outcome = fixture.get("expected_outcome_kind", "")

    if outcome == "existing_booking_found":
        return "exact_duplicate"
    if seeded:
        # Check for overlap vs same_day_distinct
        for apt in seeded:
            if apt.get("appointment_id", "").startswith("apt-"):
                return "overlap"
        return "same_day_distinct"
    return "empty"


def _infer_dialogue_form(fixture: Dict[str, Any]) -> str:
    """Infer the dialogue-form dimension from a fixture."""
    turns = fixture.get("dialogue_turns", [])
    if len(turns) >= 2:
        utterances = [t.get("utterance", "") for t in turns]
        # Exact duplicate utterances -> repeated
        if len(set(utterances)) == 1 and len(utterances) >= 2:
            return "repeated"
        # Two turns with different utterances -> clarification or correction
        return "clarification"
    return "one_shot"


def _infer_language_form(fixture: Dict[str, Any]) -> str:
    """Infer the language-form dimension from a fixture."""
    description = fixture.get("description", "").lower()
    scenario_id = fixture.get("scenario_id", "").lower()

    if "adversarial" in scenario_id or "adversarial" in description:
        return "adversarial"
    return "plain"


def build_lattice(fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the coverage lattice from a list of parsed fixtures.

    Returns a dict with:
        - scenario_count: total scenarios.
        - dimensions: per-dimension counts.
        - empty_cells: list of (action, state, temporal, dialogue, language)
          tuples with zero coverage.
        - family_summary: per-family count.
    """
    # Track covered cells
    covered: Set[Tuple[str, str, str, str, str]] = set()
    family_counts: Dict[str, int] = defaultdict(int)

    for fixture in fixtures:
        action = fixture.get("intended_action", "unknown")
        diary_state = _infer_diary_state(fixture)
        temporal = fixture.get("temporal_relation", "unspecified")
        dialogue = _infer_dialogue_form(fixture)
        language = _infer_language_form(fixture)

        covered.add((action, diary_state, temporal, dialogue, language))

        family = fixture.get("family", "unknown")
        family_counts[family] += 1

    # Build dimension counts
    action_counts: Dict[str, int] = defaultdict(int)
    state_counts: Dict[str, int] = defaultdict(int)
    temporal_counts: Dict[str, int] = defaultdict(int)
    dialogue_counts: Dict[str, int] = defaultdict(int)
    language_counts: Dict[str, int] = defaultdict(int)

    for action, state, temporal, dialogue, language in covered:
        action_counts[action] += 1
        state_counts[state] += 1
        temporal_counts[temporal] += 1
        dialogue_counts[dialogue] += 1
        language_counts[language] += 1

    # Find empty cells
    empty_cells: List[Dict[str, str]] = []
    for action in DIARY_ACTIONS:
        for state in DIARY_STATES:
            for temporal in TEMPORAL_FORMS:
                for dialogue in DIALOGUE_FORMS:
                    for language in LANGUAGE_FORMS:
                        cell = (action, state, temporal, dialogue, language)
                        if cell not in covered:
                            empty_cells.append({
                                "diary_action": action,
                                "diary_state": state,
                                "temporal_form": temporal,
                                "dialogue_form": dialogue,
                                "language_form": language,
                            })

    return {
        "schema_version": "lc1.coverage_lattice.v1",
        "scenario_count": len(fixtures),
        "covered_cell_count": len(covered),
        "total_cell_count": (
            len(DIARY_ACTIONS)
            * len(DIARY_STATES)
            * len(TEMPORAL_FORMS)
            * len(DIALOGUE_FORMS)
            * len(LANGUAGE_FORMS)
        ),
        "dimensions": {
            "diary_action": dict(action_counts),
            "diary_state": dict(state_counts),
            "temporal_form": dict(temporal_counts),
            "dialogue_form": dict(dialogue_counts),
            "language_form": dict(language_counts),
        },
        "empty_cells": empty_cells,
        "family_summary": dict(family_counts),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bernie coverage lattice reporter",
    )
    parser.add_argument(
        "--fixture-dir",
        default=str(PROJECT_ROOT / "tests" / "fixtures" / "bernie_scenario_spec"),
        help="Path to the scenario fixture directory",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    fixture_dir = Path(args.fixture_dir)

    try:
        fixtures = discover_fixtures(fixture_dir)
    except (NotADirectoryError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    report = build_lattice(fixtures)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

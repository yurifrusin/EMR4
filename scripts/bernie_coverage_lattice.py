#!/usr/bin/env python3
"""Coverage lattice reporter for the Bernie reception-agent scenario corpus.

Discovers committed ``ReceptionScenarioSpec`` fixtures, builds a coverage
lattice across six dimensions (diary_action, diary_state, entity_state,
temporal_form, dialogue_form, language_form), and reports gaps as explicit
empty cells.

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
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.bernie.scenario_spec import ReceptionScenarioSpec


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

ENTITY_STATES: List[str] = [
    "exact",
    "omitted",
    "ambiguous",
    "corrected",
    "negated",
    "mismatched",
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
                raw = json.load(fh)
            try:
                fixture = ReceptionScenarioSpec.model_validate(raw)
            except Exception as error:
                raise ValueError(f"Invalid scenario fixture {path.name}: {error}") from error
            fixtures.append(fixture.model_dump(mode="json"))
    if not fixtures:
        raise ValueError(
            f"No JSON fixtures found in {fixture_dir} (directory is empty)"
        )
    return fixtures


# ---------------------------------------------------------------------------
# Lattice building
# ---------------------------------------------------------------------------

def build_lattice(
    fixtures: List[Dict[str, Any]], *, max_empty_cells: int | None = 256
) -> Dict[str, Any]:
    """Build the coverage lattice from a list of parsed fixtures.

    Returns a dict with:
        - scenario_count: total scenarios.
        - dimensions: per-dimension counts.
        - empty_cells: list of (action, state, temporal, dialogue, language)
          tuples with zero coverage.
        - family_summary: per-family count.
    """
    # Track covered cells
    covered: Set[Tuple[str, str, str, str, str, str]] = set()
    family_counts: Dict[str, int] = defaultdict(int)

    for fixture in fixtures:
        action = fixture.get("intended_action", "unknown")
        diary_state = fixture.get("diary_state", "unknown")
        entity_state = fixture.get("entity_state", "unknown")
        temporal = fixture.get("temporal_relation", "unspecified")
        dialogue = fixture.get("dialogue_form", "unknown")
        language = fixture.get("language_form", "unknown")

        covered.add((action, diary_state, entity_state, temporal, dialogue, language))

        family = fixture.get("family", "unknown")
        family_counts[family] += 1

    # Build dimension counts
    action_counts: Dict[str, int] = defaultdict(int)
    state_counts: Dict[str, int] = defaultdict(int)
    entity_counts: Dict[str, int] = defaultdict(int)
    temporal_counts: Dict[str, int] = defaultdict(int)
    dialogue_counts: Dict[str, int] = defaultdict(int)
    language_counts: Dict[str, int] = defaultdict(int)

    for fixture in fixtures:
        action = fixture.get("intended_action", "unknown")
        state = fixture.get("diary_state", "unknown")
        entity = fixture.get("entity_state", "unknown")
        temporal = fixture.get("temporal_relation", "unspecified")
        dialogue = fixture.get("dialogue_form", "unknown")
        language = fixture.get("language_form", "unknown")
        action_counts[action] += 1
        state_counts[state] += 1
        entity_counts[entity] += 1
        temporal_counts[temporal] += 1
        dialogue_counts[dialogue] += 1
        language_counts[language] += 1

    # Find empty cells
    empty_cells: List[Dict[str, str]] = []
    empty_cell_count = 0
    for action in DIARY_ACTIONS:
        for state in DIARY_STATES:
            for entity in ENTITY_STATES:
                for temporal in TEMPORAL_FORMS:
                    for dialogue in DIALOGUE_FORMS:
                        for language in LANGUAGE_FORMS:
                            cell = (action, state, entity, temporal, dialogue, language)
                            if cell not in covered:
                                empty_cell_count += 1
                                if (
                                    max_empty_cells is None
                                    or len(empty_cells) < max_empty_cells
                                ):
                                    empty_cells.append({
                                        "diary_action": action,
                                        "diary_state": state,
                                        "entity_state": entity,
                                        "temporal_form": temporal,
                                        "dialogue_form": dialogue,
                                        "language_form": language,
                                    })

    return {
        "schema_version": "lc1.coverage_lattice.v1",
        "scenario_count": len(fixtures),
        "covered_cell_count": len(covered),
        "empty_cell_count": empty_cell_count,
        "empty_cells_truncated": len(empty_cells) < empty_cell_count,
        "total_cell_count": (
            len(DIARY_ACTIONS)
            * len(DIARY_STATES)
            * len(ENTITY_STATES)
            * len(TEMPORAL_FORMS)
            * len(DIALOGUE_FORMS)
            * len(LANGUAGE_FORMS)
        ),
        "dimensions": {
            "diary_action": dict(action_counts),
            "diary_state": dict(state_counts),
            "entity_state": dict(entity_counts),
            "temporal_form": dict(temporal_counts),
            "dialogue_form": dict(dialogue_counts),
            "language_form": dict(language_counts),
        },
        "empty_cells": empty_cells,
        "gap_summary": {
            "diary_action": [value for value in DIARY_ACTIONS if value not in action_counts],
            "diary_state": [value for value in DIARY_STATES if value not in state_counts],
            "entity_state": [value for value in ENTITY_STATES if value not in entity_counts],
            "temporal_form": [value for value in TEMPORAL_FORMS if value not in temporal_counts],
            "dialogue_form": [value for value in DIALOGUE_FORMS if value not in dialogue_counts],
            "language_form": [value for value in LANGUAGE_FORMS if value not in language_counts],
        },
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
    parser.add_argument(
        "--all-empty-cells",
        action="store_true",
        help="Emit every cross-product gap instead of the bounded default sample",
    )
    parser.add_argument(
        "--empty-cell-limit",
        type=int,
        default=256,
        help="Maximum explicit empty-cell examples in the default report",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Also write the machine-readable JSON report to this path",
    )
    # ── Candidate-aware mode ──────────────────────────────────────────────
    parser.add_argument(
        "--candidate-dir",
        type=Path,
        default=None,
        help="Path to LC2 CorpusCandidate wrapper directory for candidate-aware mode",
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

    if args.empty_cell_limit < 0:
        print("ERROR: --empty-cell-limit must be non-negative", file=sys.stderr)
        return 1
    report = build_lattice(
        fixtures,
        max_empty_cells=None if args.all_empty_cells else args.empty_cell_limit,
    )
    rendered = json.dumps(report, indent=2) + "\n"

    # ── Candidate-aware mode ──────────────────────────────────────────────
    if args.candidate_dir is not None:
        candidate_path = Path(args.candidate_dir)
        if not candidate_path.is_dir():
            print(
                f"ERROR: Candidate directory does not exist: {candidate_path}",
                file=sys.stderr,
            )
            return 1

        # Load CorpusCandidate wrappers
        from app.services.bernie.corpus_tier import CorpusCandidate

        all_wrappers: List[Dict[str, Any]] = []
        for path in sorted(candidate_path.iterdir()):
            if path.suffix.lower() != ".json":
                continue
            with open(path, "r", encoding="utf-8") as fh:
                raw_list = json.load(fh)
            if isinstance(raw_list, list):
                for entry in raw_list:
                    candidate = CorpusCandidate.model_validate(entry)
                    all_wrappers.append(candidate.model_dump(mode="json"))

        # Compute adjudicated covered cells from LC1 fixtures
        adjudicated_covered: Set[Tuple[str, str, str, str, str, str]] = set()
        for fixture in fixtures:
            action = fixture.get("intended_action", "unknown")
            diary_state = fixture.get("diary_state", "unknown")
            entity_state = fixture.get("entity_state", "unknown")
            temporal = fixture.get("temporal_relation", "unspecified")
            dialogue = fixture.get("dialogue_form", "unknown")
            language = fixture.get("language_form", "unknown")
            adjudicated_covered.add(
                (action, diary_state, entity_state, temporal, dialogue, language)
            )

        # Candidate-only cells
        candidate_covered: Set[Tuple[str, str, str, str, str, str]] = set()
        for wrapper in all_wrappers:
            sc = wrapper["scenario"]
            cell = (
                sc["intended_action"],
                sc["diary_state"],
                sc["entity_state"],
                sc["temporal_relation"],
                sc["dialogue_form"],
                sc["language_form"],
            )
            if cell not in adjudicated_covered:
                candidate_covered.add(cell)

        union_covered = adjudicated_covered | candidate_covered
        total_cells = (
            len(DIARY_ACTIONS)
            * len(DIARY_STATES)
            * len(ENTITY_STATES)
            * len(TEMPORAL_FORMS)
            * len(DIALOGUE_FORMS)
            * len(LANGUAGE_FORMS)
        )

        # Candidate count breakdown
        tier_counts: Dict[str, int] = {}
        adj_counts: Dict[str, int] = {}
        for wrapper in all_wrappers:
            tier = wrapper.get("provenance", "unknown")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            adj = wrapper.get("adjudication", "unknown")
            adj_counts[adj] = adj_counts.get(adj, 0) + 1

        candidate_lattice = {
            "feature_version": "lc3.candidate_aware_lattice.v1",
            "adjudicated_scenario_count": len(fixtures),
            "adjudicated_covered_cell_count": len(adjudicated_covered),
            "adjudicated_empty_cell_count": total_cells - len(adjudicated_covered),
            "candidate_count_by_tier": tier_counts,
            "candidate_count_by_adjudication": adj_counts,
            "candidate_only_cell_count": len(candidate_covered),
            "candidate_only_cell_examples": [
                {
                    "diary_action": c[0],
                    "diary_state": c[1],
                    "entity_state": c[2],
                    "temporal_form": c[3],
                    "dialogue_form": c[4],
                    "language_form": c[5],
                }
                for c in sorted(candidate_covered)[:5]
            ],
            "union_covered_cell_count": len(union_covered),
            "union_empty_cell_count": total_cells - len(union_covered),
            "total_lattice_cells": total_cells,
            "proof_adjudicated_gaps_preserved": (
                f"adjudicated_empty={total_cells - len(adjudicated_covered)}, "
                f"union_empty={total_cells - len(union_covered)}, "
                f"pending_candidates_do_not_reduce_adjudicated_gaps="
                f"{(total_cells - len(union_covered)) <= (total_cells - len(adjudicated_covered))}"
            ),
        }

        # Embed in the base report (backward-compatible extension)
        report["candidate_aware_lattice"] = candidate_lattice
        rendered = json.dumps(report, indent=2) + "\n"

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Provider-free generic LC4 scaled evaluator for development corpus.

Reuses the LC3 deterministic interpretation, replay, and scorer public APIs
without copying expected scenario fields into observations.  Evaluates exactly
1,152 development variants with two deterministic repeats each (2,304 samples),
preserving the 288-trajectory subset and all Silver/pending metadata.

Strict generic sealed-holdout interface using only miniature dummy records in
tests.  The actual 24-group holdout is authored by Sol separately after all
DeepSeek and Gemini work ends.

Development evidence includes bounded per-case findings for repair.  Holdout
reports are aggregate-only and reject any payload that exposes scenario/group/
variant IDs, utterances, dialogue turns, expected labels/outcomes/tools/deltas,
source spans, normalized values, case findings, or per-case failures.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    score_interpretation_replay_pair,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    CorpusSummary,
    CriticalSliceEntry,
    CriticalSliceReport,
    FailureLayer,
    build_corpus_summary,
)
from app.services.bernie.scale_corpus import (
    ALL_ACTIONS,
    ALL_DIALOGUE_FORMS,
    ALL_ENTITY_SEMANTICS,
    ALL_LANGUAGE_FORMS,
    ALL_TEMPORAL_RELATIONS,
    DEVELOPMENT_GROUP_COUNT,
    DEV_GROUP_PREFIX,
    DEV_MT_PREFIX,
    DEV_VARIANT_PREFIX,
    MULTI_TURN_VARIANTS_PER_GROUP,
    SURFACE_VARIANTS_PER_GROUP,
    TOTAL_INDIVIDUAL_RECORDS,
    TOTAL_TRAJECTORIES,
    DevelopmentOnlyLoader,
    ScaleCorpus,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LC4_SCALED_REPORT_SCHEMA_VERSION = "lc4.scaled_evaluation.v1"
EXPECTED_REPEATS = 2
EXPECTED_TOTAL_SAMPLES = TOTAL_INDIVIDUAL_RECORDS * EXPECTED_REPEATS  # 2304

# LC1 Gold scenario count preserved from LC3
EXPECTED_LC1_GOLD_CELLS = 3
# Adjudicated gap count preserved from LC3 report
EXPECTED_ADJUDICATED_GAPS = 152061


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------

def _stable_hash(content: str) -> str:
    """Deterministic SHA-256 hex digest from stable JSON encoding."""
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Stable JSON without whitespace, sorted keys."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Sealed holdout interface (generic — test only with dummy records)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SealedHoldoutReceipt:
    """Receipt metadata for a sealed holdout evaluation.

    This is a generic interface only.  The actual 24-group holdout is
    authored by Sol after all DeepSeek and Gemini work ends.
    Test only with miniature dummy records.
    """
    manifest_hash: str
    purpose: str
    evaluator_identity: str
    evaluation_id: str
    is_sealed: bool = False

    def validate_access(self, manifest_hash: str, purpose: str) -> bool:
        """Fail-closed: wrong or reused credentials are rejected."""
        return (
            self.is_sealed
            and manifest_hash == self.manifest_hash
            and purpose == self.purpose
        )


@dataclass(frozen=True)
class SingleUseLedger:
    """Single-use in-memory ledger for sealed holdout access.

    Tracks whether the capability has already been consumed.
    """
    capability: SealedHoldoutReceipt
    _consumed: bool = False

    def consume(self, manifest_hash: str, purpose: str) -> bool:
        """Attempt to consume the capability once.

        Returns True if access is granted.  Subsequent attempts fail.
        """
        if self._consumed:
            return False
        if not self.capability.validate_access(manifest_hash, purpose):
            return False
        object.__setattr__(self, "_consumed", True)
        return True

    @property
    def is_consumed(self) -> bool:
        return self._consumed


# ---------------------------------------------------------------------------
# Aggregate-only holdout sanitizer / report builder
# ---------------------------------------------------------------------------

# Prohibited keys (or key substrings) in holdout report content
_PROHIBITED_HOLDOUT_KEYS: frozenset[str] = frozenset({
    "scenario_id", "group_id", "variant_id", "utterance", "dialogue_turn",
    "expected_outcome", "expected_label", "expected_tool", "expected_delta",
    "source_span", "normalized_value", "case_finding", "per_case_result",
    "scenario_id_list", "variant_id_list", "turn_text", "observation_text",
})


def sanitize_holdout_report(report: dict[str, Any]) -> dict[str, Any]:
    """Sanitize a holdout report, rejecting prohibited keys/values.

    Only aggregate/slice counts, fractions, partition/corpus/report hashes,
    version, repeat count, and sealed receipt metadata are allowed.

    Raises ValueError if any prohibited content is found.
    """
    _check_prohibited_keys(report)

    allowed_top_keys = {
        "schema_version", "sealed_receipt", "partition",
        "corpus_hash", "manifest_hash", "report_hash",
        "total_groups", "total_variants", "total_trajectories",
        "total_samples", "repeat_count",
        "aggregate", "critical_slices", "per_dimension",
    }

    # Enforce top-level structure
    for key in report:
        if key not in allowed_top_keys:
            raise ValueError(
                f"Holdout report contains prohibited top-level key: {key!r}"
            )

    # Check aggregate section
    if "aggregate" in report:
        agg = report["aggregate"]
        for agg_key in agg:
            if agg_key not in ("passed", "failed", "total", "pass_fraction"):
                raise ValueError(
                    f"Holdout aggregate contains prohibited key: {agg_key!r}"
                )

    # Check per_dimension section
    if "per_dimension" in report:
        _check_dimension_section(report["per_dimension"])

    # Check critical_slices section
    if "critical_slices" in report:
        _check_slice_section(report["critical_slices"])

    return report


def _check_prohibited_keys(obj: Any, path: str = "") -> None:
    """Recursively check for prohibited key substrings."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = key.lower()
            for prohibited in _PROHIBITED_HOLDOUT_KEYS:
                if prohibited in key_lower:
                    raise ValueError(
                        f"Holdout report contains prohibited key {key!r}"
                        f" at {path}"
                    )
            _check_prohibited_keys(value, f"{path}.{key}")
            # Also check string values for prohibited patterns
            if isinstance(value, str):
                _check_string_value(value, f"{path}.{key}")
            elif isinstance(value, list):
                _check_list_values(value, f"{path}.{key}")
    elif isinstance(obj, list):
        _check_list_values(obj, path)


def _check_list_values(items: list[Any], path: str) -> None:
    for idx, item in enumerate(items):
        if isinstance(item, str):
            _check_string_value(item, f"{path}[{idx}]")
        elif isinstance(item, dict):
            _check_prohibited_keys(item, f"{path}[{idx}]")


def _check_string_value(value: str, path: str) -> None:
    """Check a string value against prohibited patterns."""
    lower = value.lower()
    prohibited_patterns = [
        "lc4_dw1_dev_group", "lc4_dw1_dev_var", "lc4_dw1_dev_mt",
        "margaret thompson", "dr shera", "dr patel",
        "appointment for", "book margaret", "cancel margaret",
    ]
    for pattern in prohibited_patterns:
        if pattern in lower:
            raise ValueError(
                f"Holdout report contains prohibited pattern {pattern!r}"
                f" in value at {path}"
            )


def _check_dimension_section(dim: dict[str, Any]) -> None:
    """Check per_dimension section for prohibited content."""
    allowed_dim_keys = {
        "scenario_count", "sample_count", "repeats_per_scenario",
        "aggregate", "semantic_fields", "downstream_outcome",
        "interpretation_tools", "replay_tool_sequence", "clarification",
        "authority", "appointment_deltas", "audit_deltas", "safety",
        "interpretation_failures", "policy_failures",
        "integration_failures", "safety_failures",
    }
    for key in dim:
        if key not in allowed_dim_keys:
            raise ValueError(
                f"Holdout per_dimension contains prohibited key: {key!r}"
            )


def _check_slice_section(slices: dict[str, Any]) -> None:
    """Check critical_slices section."""
    allowed_slice_keys = {
        "worst_slice", "by_action", "by_temporal_relation",
        "by_dialogue_form", "by_language_form", "by_diary_state",
        "by_entity_state", "by_gap_target", "by_trajectory_type",
        "by_tier", "by_adjudication",
    }
    for key in slices:
        if key not in allowed_slice_keys:
            raise ValueError(
                f"Holdout critical_slices contains prohibited key: {key!r}"
            )


# ---------------------------------------------------------------------------
# LC4 scaled evaluator
# ---------------------------------------------------------------------------


def _split_variants_by_type(
    variants: list[ReceptionScenarioSpec],
) -> tuple[list[ReceptionScenarioSpec], list[ReceptionScenarioSpec]]:
    """Split variants into single-turn surface and multi-turn trajectory."""
    single: list[ReceptionScenarioSpec] = []
    multi: list[ReceptionScenarioSpec] = []
    for v in variants:
        if len(v.dialogue_turns) > 1:
            multi.append(v)
        else:
            single.append(v)
    return single, multi


def _attribute_failure_layers(
    result: ComposedSampleResult,
) -> dict[str, bool]:
    """Get boolean flags for all implicated failure layers."""
    return {
        "interpretation": "interpretation" in result.failure_layers,
        "policy": "policy" in result.failure_layers,
        "integration": "integration" in result.failure_layers,
        "safety": "safety" in result.failure_layers,
    }


def _build_per_dimension_scores(
    results: list[ComposedSampleResult],
    total_scenarios: int,
    total_samples: int,
    repeats: int,
) -> dict[str, Any]:
    """Build per-dimension pass/fail scores from results."""

    def _sf_passed(attr: str) -> dict[str, int]:
        passed = sum(
            1 for r in results
            if getattr(r.semantic_fields, attr, object()).passed
        )
        return {"passed": passed, "failed": total_samples - passed, "total": total_samples}

    def _dim_passed(dim: str) -> dict[str, int]:
        passed = sum(1 for r in results if getattr(r, dim, object()).passed)
        return {"passed": passed, "failed": total_samples - passed, "total": total_samples}

    # Simultaneous failure attribution
    layer_counts: dict[str, int] = {
        "interpretation": 0, "policy": 0, "integration": 0, "safety": 0,
    }
    for r in results:
        for layer in layer_counts:
            if layer in r.failure_layers:
                layer_counts[layer] += 1

    return {
        "scenario_count": total_scenarios,
        "sample_count": total_samples,
        "repeats_per_scenario": repeats,
        "aggregate": {
            "passed": sum(1 for r in results if r.all_passed),
            "failed": sum(1 for r in results if not r.all_passed),
            "total": total_samples,
        },
        "semantic_fields": {
            "intended_action": _sf_passed("intended_action"),
            "action_semantics": _sf_passed("action_semantics"),
            "temporal_relation": _sf_passed("temporal_relation"),
            "normalized_values": _sf_passed("normalized_values"),
            "entity_semantics": _sf_passed("entity_semantics"),
            "requires_clarification": _sf_passed("clarification"),
        },
        "downstream_outcome": _dim_passed("downstream_outcome"),
        "interpretation_tools": _dim_passed("interpretation_tools"),
        "replay_tool_sequence": _dim_passed("tool_sequence"),
        "clarification": _dim_passed("clarification"),
        "authority": {
            "passed": sum(1 for r in results if r.authority.passed),
            "failed": sum(1 for r in results if not r.authority.passed),
            "total": total_samples,
            "authority_correct": sum(1 for r in results if r.authority.authority_correct),
            "authority_incorrect": sum(
                1 for r in results
                if not r.authority.authority_correct and not r.authority.is_safety_violation
            ),
            "safety_violations": sum(1 for r in results if not r.safety.passed),
        },
        "appointment_deltas": _dim_passed("appointment_deltas"),
        "audit_deltas": _dim_passed("audit_deltas"),
        "safety": _dim_passed("safety"),
        "interpretation_failures": layer_counts["interpretation"],
        "policy_failures": layer_counts["policy"],
        "integration_failures": layer_counts["integration"],
        "safety_failures": layer_counts["safety"],
        "simultaneous_layers": {
            "safety_only": sum(
                1 for r in results
                if r.failure_layers == ("safety",)
            ),
            "interpretation_only": sum(
                1 for r in results
                if r.failure_layers == ("interpretation",)
            ),
            "policy_only": sum(
                1 for r in results
                if r.failure_layers == ("policy",)
            ),
            "integration_only": sum(
                1 for r in results
                if r.failure_layers == ("integration",)
            ),
            "interpretation_and_policy": sum(
                1 for r in results
                if "interpretation" in r.failure_layers and "policy" in r.failure_layers
            ),
            "interpretation_and_integration": sum(
                1 for r in results
                if "interpretation" in r.failure_layers and "integration" in r.failure_layers
            ),
            "multiple_layers": sum(
                1 for r in results if len(r.failure_layers) > 1
            ),
        },
    }


def _build_slices(
    results: list[ComposedSampleResult],
    scenarios: list[ReceptionScenarioSpec],
    summary: CorpusSummary,
) -> dict[str, Any]:
    """Build critical slices across all required dimensions."""
    scenario_map = {s.scenario_id: s for s in scenarios}

    # Define registry for all slice dimensions
    slice_registry: dict[str, dict[str, dict[str, int]]] = {
        "action": {},
        "temporal_relation": {},
        "diary_state": {},
        "entity_state": {},
        "dialogue_form": {},
        "language_form": {},
        "gap_target": {},
        "trajectory_type": {},
        "tier": {},
        "adjudication": {},
    }

    for r in results:
        sc = scenario_map.get(r.scenario_id)
        if sc is None:
            continue
        _acc(slice_registry, "action", sc.intended_action, r.all_passed)
        _acc(slice_registry, "temporal_relation", sc.temporal_relation, r.all_passed)
        _acc(slice_registry, "diary_state", sc.diary_state, r.all_passed)
        _acc(slice_registry, "entity_state", sc.entity_state, r.all_passed)
        _acc(slice_registry, "dialogue_form", sc.dialogue_form, r.all_passed)
        _acc(slice_registry, "language_form", sc.language_form, r.all_passed)
        _acc(slice_registry, "tier", sc.provenance, r.all_passed)
        _acc(slice_registry, "adjudication", sc.adjudication, r.all_passed)

        # Trajectory type
        tt = "trajectory" if len(sc.dialogue_turns) > 1 else "single_turn"
        _acc(slice_registry, "trajectory_type", tt, r.all_passed)

        # Gap target — use family prefix to determine gap category
        if sc.family:
            family_lower = sc.family.lower()
            for gt in _infer_gap_targets(sc):
                _acc(slice_registry, "gap_target", gt, r.all_passed)

    # Build entry tuples
    slices_dict: dict[str, Any] = {
        "worst_slice": _worst_slice_entry(slice_registry),
        "by_action": _entries_for(slice_registry, "action"),
        "by_temporal_relation": _entries_for(slice_registry, "temporal_relation"),
        "by_diary_state": _entries_for(slice_registry, "diary_state"),
        "by_entity_state": _entries_for(slice_registry, "entity_state"),
        "by_dialogue_form": _entries_for(slice_registry, "dialogue_form"),
        "by_language_form": _entries_for(slice_registry, "language_form"),
        "by_tier": _entries_for(slice_registry, "tier"),
        "by_adjudication": _entries_for(slice_registry, "adjudication"),
        "by_trajectory_type": _entries_for(slice_registry, "trajectory_type"),
        "by_gap_target": _entries_for(slice_registry, "gap_target"),
    }
    return slices_dict


def _infer_gap_targets(scenario: ReceptionScenarioSpec) -> list[str]:
    """Infer gap target categories from scenario fields."""
    targets: list[str] = []
    if scenario.dialogue_form in ("clarification",):
        targets.append("clarification_dialogue")
    if scenario.temporal_relation in ("interval", "unspecified"):
        targets.append("interval_unspecified_temporal")
    if scenario.entity_state in ("ambiguous", "omitted", "corrected"):
        targets.append("entity_ambiguity_omission_correction")
    if scenario.dialogue_form != "one_shot" or scenario.temporal_relation in ("interval", "unspecified"):
        targets.append("interpretation_replay_tool_selection")
    return targets


def _acc(
    registry: dict[str, dict[str, dict[str, int]]],
    dim: str,
    key: str,
    passed: bool,
) -> None:
    bucket = registry.setdefault(dim, {}).setdefault(key, {"total": 0, "passed": 0, "failed": 0})
    bucket["total"] += 1
    if passed:
        bucket["passed"] += 1
    else:
        bucket["failed"] += 1


def _worst_slice_entry(
    registry: dict[str, dict[str, dict[str, int]]],
) -> dict[str, Any] | None:
    """Find the worst-performing slice across all dimensions."""
    best_entry: dict[str, Any] | None = None
    for dim_name, dim_data in registry.items():
        for key, counts in dim_data.items():
            total = counts["total"]
            if total == 0:
                continue
            passed = counts["passed"]
            frac = passed / total
            if best_entry is None or frac < best_entry["pass_fraction"]:
                best_entry = {
                    "dimension": dim_name,
                    "slice_key": key,
                    "total": total,
                    "passed": passed,
                    "failed": counts["failed"],
                    "pass_fraction": round(frac, 4),
                }
            elif frac == best_entry["pass_fraction"] and key < best_entry["slice_key"]:
                best_entry.update({
                    "dimension": dim_name,
                    "slice_key": key,
                    "total": total,
                    "passed": passed,
                    "failed": counts["failed"],
                    "pass_fraction": round(frac, 4),
                })
    return best_entry


def _entries_for(
    registry: dict[str, dict[str, dict[str, int]]],
    dim: str,
) -> list[dict[str, Any]]:
    result = []
    for key in sorted(registry.get(dim, {})):
        counts = registry[dim][key]
        result.append({
            "slice_key": key,
            "total": counts["total"],
            "passed": counts["passed"],
            "failed": counts["failed"],
            "pass_fraction": round(counts["passed"] / counts["total"], 4) if counts["total"] > 0 else 1.0,
        })
    return result


# ---------------------------------------------------------------------------
# Candidate-aware lattice
# ---------------------------------------------------------------------------

# Full coverage lattice dimensions
_DIARY_ACTIONS = [
    "create", "move", "resize", "cancel",
    "status_change", "explain_schedule",
]
_DIARY_STATES = [
    "empty", "exact_duplicate", "overlap", "same_day_distinct",
    "terminal", "stale", "concurrent", "roster_absent",
    "break", "no_slots", "elapsed_window",
]
_ENTITY_STATES = [
    "exact", "omitted", "ambiguous", "corrected",
    "negated", "mismatched",
]
_TEMPORAL_FORMS = [
    "exact", "not_before", "not_after", "interval",
    "approximate", "unspecified",
]
_DIALOGUE_FORMS = [
    "one_shot", "clarification", "correction", "reversal",
    "ellipsis", "anaphora", "repeated", "session_restart",
]
_LANGUAGE_FORMS = [
    "plain", "paraphrase", "filler", "abbreviation",
    "typo", "speech_like", "punctuation_variant", "adversarial",
]
_TOTAL_CELLS = (
    len(_DIARY_ACTIONS) * len(_DIARY_STATES) * len(_ENTITY_STATES)
    * len(_TEMPORAL_FORMS) * len(_DIALOGUE_FORMS) * len(_LANGUAGE_FORMS)
)


def build_candidate_lattice(
    scenarios: list[ReceptionScenarioSpec],
    adjudicated_cells: set[tuple[str, str, str, str, str, str]] | None = None,
) -> dict[str, Any]:
    """Build candidate-aware lattice counts.

    Keeps the three LC1 Gold cells and 152,061 adjudicated gaps unchanged while
    reporting LC4 pending discovery separately.

    Parameters
    ----------
    scenarios :
        All scenarios in the corpus (LC4 development variants).
    adjudicated_cells :
        The three LC1 Gold adjudicated cells.  If None, uses the canonical
        Gold cells from the LC3 composed evaluation.
    """
    if adjudicated_cells is None:
        # The three LC1 Gold adjudicated cells (from LC3 Gold scenarios):
        # These are the canonical Gold cells that define the 152,061 gap count.
        adjudicated_cells = {
            ("create", "exact_duplicate", "exact", "exact", "one_shot", "plain"),
            ("create", "overlap", "exact", "exact", "one_shot", "paraphrase"),
            ("explain_schedule", "empty", "exact", "unspecified", "clarification", "plain"),
        }

    # Candidate-only cells: from LC4 development scenarios
    # (non-overlapping with adjudicated)
    candidate_covered: set[tuple[str, str, str, str, str, str]] = set()
    for s in scenarios:
        cell = (
            s.intended_action, s.diary_state, s.entity_state,
            s.temporal_relation, s.dialogue_form, s.language_form,
        )
        if cell not in adjudicated_cells:
            candidate_covered.add(cell)

    union_covered = adjudicated_cells | candidate_covered
    adjudicated_empty = _TOTAL_CELLS - len(adjudicated_cells)
    union_empty = _TOTAL_CELLS - len(union_covered)

    return {
        "adjudicated_scenario_count": len(adjudicated_cells),
        "adjudicated_covered_cell_count": len(adjudicated_cells),
        "adjudicated_empty_cell_count": adjudicated_empty,
        "expected_adjudicated_gaps_preserved": adjudicated_empty == EXPECTED_ADJUDICATED_GAPS,
        "expected_adjudicated_gaps_note": (
            f"adj_empty={adjudicated_empty}, "
            f"expected={EXPECTED_ADJUDICATED_GAPS}, "
            f"preserved={adjudicated_empty == EXPECTED_ADJUDICATED_GAPS}"
        ),
        "candidate_count_by_tier": {"silver": len(scenarios)},
        "candidate_count_by_adjudication": {"pending": len(scenarios)},
        "candidate_only_cell_count": len(candidate_covered),
        "union_covered_cell_count": len(union_covered),
        "union_empty_cell_count": union_empty,
        "total_lattice_cells": _TOTAL_CELLS,
        "pending_candidates_do_not_reduce_adjudicated_gaps": (
            union_empty <= adjudicated_empty
        ),
        "lc4_pending_discovery_count": len(scenarios),
        "lc4_pending_discovery_separate": True,
    }


# ---------------------------------------------------------------------------
# Variance detection
# ---------------------------------------------------------------------------


def compute_variance(
    results: list[ComposedSampleResult],
) -> dict[str, Any]:
    """Compute repeat variance across samples."""
    scenario_fingerprints: dict[str, set[tuple[Any, ...]]] = {}
    for r in results:
        fp = _semantic_safety_fingerprint(r)
        scenario_fingerprints.setdefault(r.scenario_id, set()).add(fp)

    variant_scenario_count = sum(
        1 for fps in scenario_fingerprints.values() if len(fps) > 1
    )
    variant_sample_count = sum(
        sum(1 for r in results if r.scenario_id == sid and len(fps) > 1)
        for sid, fps in scenario_fingerprints.items()
    )

    return {
        "variant_scenario_count": variant_scenario_count,
        "variant_sample_count": variant_sample_count,
        "total_repeats": EXPECTED_REPEATS,
        "all_samples_deterministic": (
            variant_scenario_count == 0 and variant_sample_count == 0
        ),
    }


def _semantic_safety_fingerprint(result: ComposedSampleResult) -> tuple[Any, ...]:
    """Full canonical fingerprint for variance detection."""
    s = result.semantic_fields

    def _cm(v: Any) -> Any:
        if isinstance(v, dict):
            return tuple(sorted((k, _cm(v2)) for k, v2 in v.items()))
        if isinstance(v, list):
            return tuple(_cm(x) for x in v)
        return v

    return (
        s.intended_action.observed,
        s.action_semantics.observed,
        s.temporal_relation.observed,
        _cm(s.normalized_values.observed),
        _cm(s.entity_semantics.observed),
        result.downstream_outcome.comparison.observed,
        result.tool_sequence.observed,
        result.interpretation_tools.observed,
        result.authority.authority_claim,
        result.clarification.observed_requires,
        result.clarification.observed_choices,
        result.safety.interpretation_safety_violations,
        result.safety.replay_safety_violations,
        result.failure_layers,
    )


# ---------------------------------------------------------------------------
# Bounded case findings
# ---------------------------------------------------------------------------


def build_bounded_findings(
    results: list[ComposedSampleResult],
) -> list[dict[str, Any]]:
    """Build bounded development case findings for repair.

    Includes scenario_id, all_passed, failure_layer(s), per-field status,
    and observed values for repair.  Does not dump unbounded detail.
    """
    findings: list[dict[str, Any]] = []
    for r in results:
        finding: dict[str, Any] = {
            "scenario_id": r.scenario_id,
            "sample_index": r.sample_index,
            "all_passed": r.all_passed,
            "failure_layer": r.failure_layer,
            "failure_layers": list(r.failure_layers),
            "semantic_fields": {
                "passed": r.semantic_fields.passed,
                "failures": r.semantic_fields.failures,
            },
            "downstream_outcome": {
                "passed": r.downstream_outcome.passed,
                "expected": r.downstream_outcome.comparison.expected,
                "observed": r.downstream_outcome.comparison.observed,
            },
            "tool_sequence": r.tool_sequence.passed,
            "interpretation_tools": r.interpretation_tools.passed,
            "authority": {
                "passed": r.authority.passed,
                "claim": r.authority.authority_claim,
                "correct": r.authority.authority_correct,
                "is_safety_violation": r.authority.is_safety_violation,
            },
            "clarification": r.clarification.passed,
            "appointment_deltas": r.appointment_deltas.passed,
            "audit_deltas": r.audit_deltas.passed,
            "safety": r.safety.passed,
        }
        findings.append(finding)

    return findings


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------


def generate_scaled_evaluation_report(
    fixture_dir: pathlib.Path | None = None,
    repeats: int = EXPECTED_REPEATS,
) -> dict[str, Any]:
    """Generate the complete LC4 scaled evaluation report.

    Loads the development corpus, runs deterministic interpretation + replay
    with *repeats* repetitions, scores every pair, and returns a deterministic
    report dict.

    Parameters
    ----------
    fixture_dir :
        Path to the development fixtures directory.
    repeats :
        Number of deterministic repeats per variant (default 2).

    Returns
    -------
    dict
        The LC4 scaled evaluation report.
    """
    if fixture_dir is None:
        fixture_dir = _default_fixture_dir()

    # 1. Load corpus
    loader = DevelopmentOnlyLoader(fixture_dir)
    corpus: ScaleCorpus = loader.load_all()
    all_scenarios = corpus.all_variants()

    total_scenarios = len(all_scenarios)
    total_samples = total_scenarios * repeats

    assert total_scenarios == TOTAL_INDIVIDUAL_RECORDS, (
        f"Expected {TOTAL_INDIVIDUAL_RECORDS} scenarios, got {total_scenarios}"
    )
    assert total_samples == EXPECTED_TOTAL_SAMPLES, (
        f"Expected {EXPECTED_TOTAL_SAMPLES} samples, got {total_samples}"
    )

    # 2. Count by type
    surface_variants, trajectory_variants = _split_variants_by_type(all_scenarios)

    # 3. Run deterministic interpretation + replay
    results: list[ComposedSampleResult] = []
    for scenario in all_scenarios:
        for sample_idx in range(repeats):
            interp = deterministic_interpret(scenario)
            # Override sample index for this repeat
            interp = interp.__class__(
                scenario_id=interp.scenario_id,
                sample_index=sample_idx,
                intended_action=interp.intended_action,
                action_semantics=interp.action_semantics,
                temporal_relation=interp.temporal_relation,
                normalized_values=interp.normalized_values,
                entity_semantics=interp.entity_semantics,
                requires_clarification=interp.requires_clarification,
                clarification_choices=interp.clarification_choices,
                selected_tool_sequence=interp.selected_tool_sequence,
                authority_claim=interp.authority_claim,
                claims_action_completed=interp.claims_action_completed,
            )
            replay = deterministic_replay(scenario, interp)
            result = score_interpretation_replay_pair(scenario, interp, replay)
            results.append(result)

    # 4. Build corpus summary
    summary: CorpusSummary = build_corpus_summary(results, all_scenarios)

    # 5. Per-dimension scores
    per_dim = _build_per_dimension_scores(results, total_scenarios, total_samples, repeats)

    # 6. Critical slices
    slices = _build_slices(results, all_scenarios, summary)

    # 7. Variance
    variance = compute_variance(results)

    # 8. Bounded findings
    case_findings = build_bounded_findings(results)

    # 9. Candidate-aware lattice
    lattice = build_candidate_lattice(all_scenarios)

    # 10. Corpus/partition/report hashes
    report_data = _build_report_hashes(results, corpus)
    report_hash = report_data["report_hash"]

    # Build report
    report: dict[str, Any] = {
        "schema_version": LC4_SCALED_REPORT_SCHEMA_VERSION,
        "report_hash": report_hash,
        "corpus_hash": corpus.corpus_hash,
        "partition": {
            "schema_version": "lc4.partition.v1",
            "development_group_count": DEVELOPMENT_GROUP_COUNT,
            "surface_variants_per_group": SURFACE_VARIANTS_PER_GROUP,
            "multi_turn_per_group": MULTI_TURN_VARIANTS_PER_GROUP,
            "total_groups": DEVELOPMENT_GROUP_COUNT,
            "total_variants": TOTAL_INDIVIDUAL_RECORDS,
            "total_trajectories": TOTAL_TRAJECTORIES,
            "holdout_group_count": 0,
            "holdout_total_variants": 0,
        },
        "manifest": {
            "development_groups": len(corpus.groups),
            "surface_variant_count": len(surface_variants),
            "trajectory_count": len(trajectory_variants),
            "total_scenarios": total_scenarios,
            "total_samples": total_samples,
            "repeats": repeats,
            "provenance": "silver",
            "adjudication": "pending",
        },
        "per_dimension": per_dim,
        "critical_slices": slices,
        "variance": variance,
        "case_findings": case_findings,
        "candidate_aware_lattice": lattice,
    }

    return report


def _default_fixture_dir() -> pathlib.Path:
    """Return the default development fixture directory."""
    here = pathlib.Path(__file__).resolve().parent.parent.parent.parent
    return here / "tests" / "fixtures" / "bernie_lc4_development"


def _build_report_hashes(
    results: list[ComposedSampleResult],
    corpus: ScaleCorpus,
) -> dict[str, str]:
    """Build report hash from canonical result fingerprint."""
    # Build a canonical summary for hashing
    canonical_input = {
        "corpus_hash": corpus.corpus_hash,
        "total_results": len(results),
        "passed": sum(1 for r in results if r.all_passed),
        "failed": sum(1 for r in results if not r.all_passed),
    }
    report_hash = _stable_hash(_canonical_json(canonical_input))
    return {"report_hash": report_hash}


def generate_report_json(
    fixture_dir: pathlib.Path | None = None,
    repeats: int = EXPECTED_REPEATS,
) -> str:
    """Generate the deterministic LC4 report as a JSON string."""
    report = generate_scaled_evaluation_report(fixture_dir, repeats)
    return json.dumps(report, indent=2, default=str) + "\n"


# ---------------------------------------------------------------------------
# Import isolation guard
# ---------------------------------------------------------------------------

_PROHIBITED_IMPORT_PREFIXES = (
    "app.routers",
    "app.models",
    "app.db",
    "app.services.ai.providers",
    "sqlalchemy",
    "alembic",
)


def validate_scaled_evaluator_isolation() -> None:
    """Assert that this module cannot reach providers, routes, or storage."""
    import ast

    tree = ast.parse(
        pathlib.Path(__file__).read_text(encoding="utf-8")
    )
    for node in ast.walk(tree):
        imported: tuple[str, ...] = ()
        if isinstance(node, ast.Import):
            imported = tuple(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = (node.module,)
        for module_name in imported:
            if module_name.startswith(_PROHIBITED_IMPORT_PREFIXES):
                raise RuntimeError(
                    f"Scaled evaluator imports prohibited module: {module_name}"
                )


def validate_holdout_import_isolation() -> list[str]:
    """Prove product/runtime/provider/route/DB/T3 modules do not import
    holdout capabilities or test fixtures.

    Scans the project's Python source tree for prohibited imports of
    holdout-related types or test fixtures from product modules.

    Returns a list of violation messages (empty if clean).
    """
    import ast

    violations: list[str] = []

    # Project src root
    src_root = pathlib.Path(__file__).resolve().parent.parent.parent
    if not src_root.exists():
        return violations

    # Modules that are allowed to reference holdout capabilities
    allowed_modules = {
        "app.services.bernie.scaled_evaluator",
        "tests.test_bernie_lc4_scaled_evaluator",
        "scripts.bernie_lc4_scaled_evaluation",
    }

    # Prohibited import targets (holdout capabilities)
    prohibited_imports = {
        "SealedHoldoutReceipt",
        "SingleUseLedger",
        "sanitize_holdout_report",
    }

    # Walk all Python files under src root
    for py_file in src_root.rglob("*.py"):
        # Skip tests
        if "tests" in py_file.parts:
            continue
        # Skip scripts
        if "scripts" in py_file.parts:
            continue
        # Skip the evaluator itself
        if py_file.name == "scaled_evaluator.py":
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in prohibited_imports:
                        violations.append(
                            f"{py_file}: imports {alias.name!r}"
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    if alias.name in prohibited_imports:
                        violations.append(
                            f"{py_file}: imports {alias.name!r} from {node.module}"
                        )

    return violations


__all__ = [
    "LC4_SCALED_REPORT_SCHEMA_VERSION",
    "EXPECTED_REPEATS",
    "EXPECTED_TOTAL_SAMPLES",
    "EXPECTED_LC1_GOLD_CELLS",
    "EXPECTED_ADJUDICATED_GAPS",
    "SealedHoldoutReceipt",
    "SingleUseLedger",
    "sanitize_holdout_report",
    "generate_scaled_evaluation_report",
    "generate_report_json",
    "build_candidate_lattice",
    "compute_variance",
    "build_bounded_findings",
    "validate_scaled_evaluator_isolation",
    "validate_holdout_import_isolation",
]

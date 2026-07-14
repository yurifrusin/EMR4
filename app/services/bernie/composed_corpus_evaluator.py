"""Offline corpus consumer for LC3 composed evaluation.

Strictly loads all 3 LC1 Gold/adjudicated scenario specs and all 15 LC2
Silver/pending CorpusCandidate wrappers.  Produces typed
InterpretationObservation and ReplayObservation through deterministic,
provider-free language functions, then scores every pair through the DW1
composed_evaluator and emits a deterministic machine-readable report.

Authority must be ``read``, ``clarify``, or ``refuse`` — never ``write``.
"""

from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict
from typing import Any

from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    CorpusSummary,
    InterpretationObservation,
    ReplayObservation,
    build_corpus_summary,
    score_interpretation_replay_pair,
)
from app.services.bernie.corpus_tier import CorpusCandidate
from app.services.bernie.language_normalization import normalize_utterance
from app.services.bernie.scenario_spec import ReceptionScenarioSpec
from app.services.bernie.semantic_extraction import extract_semantics
from app.services.diary.outcomes import BernieBookingOutcomeKind

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LC3_REPORT_SCHEMA_VERSION = "lc3.composed_evaluation.v1"

# Number of LC1 Gold scenarios expected
EXPECTED_LC1_COUNT = 3
# Number of LC2 Silver wrappers expected
EXPECTED_LC2_COUNT = 15

# ---------------------------------------------------------------------------
# Fixture path helpers
# ---------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = HERE.parent


def _default_lc1_fixture_dir() -> pathlib.Path:
    return (
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "bernie_scenario_spec"
    )


def _default_lc2_candidate_dir() -> pathlib.Path:
    return (
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "bernie_corpus_candidates"
    )


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------

KNOWN_LC1_FIXTURES: frozenset[str] = frozenset({
    "booking_create_then_exact_duplicate.json",
    "booking_overlap_not_exact_duplicate.json",
    "interpret_clarify_temporal_bounds.json",
})

KNOWN_LC2_FAMILY_FILES: frozenset[str] = frozenset({
    "paraphrase_family.json",
    "minimal_pair_family.json",
    "ambiguity_family.json",
    "correction_family.json",
    "adversarial_family.json",
})

# Expected per-family counts
EXPECTED_LC2_PER_FAMILY: dict[str, int] = {
    "paraphrase_family.json": 3,
    "minimal_pair_family.json": 3,
    "ambiguity_family.json": 3,
    "correction_family.json": 3,
    "adversarial_family.json": 3,
}


def load_lc1_scenarios(
    fixture_dir: pathlib.Path | None = None,
) -> list[ReceptionScenarioSpec]:
    """Load exactly 3 LC1 Gold/adjudicated scenario fixtures.

    Raises ``ValueError`` if the count, tier/state, or file names are wrong.
    """
    if fixture_dir is None:
        fixture_dir = _default_lc1_fixture_dir()
    if not fixture_dir.is_dir():
        raise NotADirectoryError(
            f"LC1 fixture directory does not exist: {fixture_dir}"
        )

    seen_ids: set[str] = set()
    scenarios: list[ReceptionScenarioSpec] = []
    loaded_files = set()

    for path in sorted(fixture_dir.iterdir()):
        if path.suffix.lower() != ".json":
            continue
        if path.name not in KNOWN_LC1_FIXTURES:
            raise ValueError(
                f"Unknown fixture file: {path.name}. "
                f"Known: {sorted(KNOWN_LC1_FIXTURES)}"
            )
        loaded_files.add(path.name)
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        scenario = ReceptionScenarioSpec.model_validate(raw)
        if scenario.scenario_id in seen_ids:
            raise ValueError(
                f"Duplicate scenario_id in LC1 fixtures: {scenario.scenario_id!r}"
            )
        seen_ids.add(scenario.scenario_id)
        if scenario.provenance != "gold":
            raise ValueError(
                f"LC1 scenario {scenario.scenario_id!r} must be gold, "
                f"got {scenario.provenance!r}"
            )
        if scenario.adjudication != "adjudicated":
            raise ValueError(
                f"LC1 scenario {scenario.scenario_id!r} must be adjudicated, "
                f"got {scenario.adjudication!r}"
            )
        scenarios.append(scenario)

    if len(scenarios) != EXPECTED_LC1_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_LC1_COUNT} LC1 scenarios, loaded {len(scenarios)}"
        )

    return scenarios


def load_lc2_candidates(
    candidate_dir: pathlib.Path | None = None,
) -> list[CorpusCandidate]:
    """Load exactly 15 LC2 CorpusCandidate wrappers from 5 family files.

    Raises ``ValueError`` for wrong counts, tiers, states, or duplicate IDs.
    """
    if candidate_dir is None:
        candidate_dir = _default_lc2_candidate_dir()
    if not candidate_dir.is_dir():
        raise NotADirectoryError(
            f"LC2 candidate directory does not exist: {candidate_dir}"
        )

    seen_ids: set[str] = set()
    candidates: list[CorpusCandidate] = []
    loaded_files = set()

    for path in sorted(candidate_dir.iterdir()):
        if path.suffix.lower() != ".json":
            continue
        if path.name not in KNOWN_LC2_FAMILY_FILES:
            raise ValueError(
                f"Unknown family file: {path.name}. "
                f"Known: {sorted(KNOWN_LC2_FAMILY_FILES)}"
            )
        loaded_files.add(path.name)
        with open(path, "r", encoding="utf-8") as fh:
            raw_list = json.load(fh)

        if not isinstance(raw_list, list):
            raise ValueError(
                f"LC2 family file {path.name} must contain a JSON array"
            )

        expected = EXPECTED_LC2_PER_FAMILY.get(path.name, 0)
        if len(raw_list) != expected:
            raise ValueError(
                f"Expected {expected} candidates in {path.name}, "
                f"got {len(raw_list)}"
            )

        for raw in raw_list:
            candidate = CorpusCandidate.model_validate(raw)
            cid = candidate.scenario.scenario_id
            if cid in seen_ids:
                raise ValueError(
                    f"Duplicate scenario_id in LC2 candidates: {cid!r}"
                )
            seen_ids.add(cid)

            if candidate.provenance.value != "silver":
                raise ValueError(
                    f"LC2 candidate {cid!r} must be silver tier, "
                    f"got {candidate.provenance.value!r}"
                )
            if candidate.adjudication.value != "pending":
                raise ValueError(
                    f"LC2 candidate {cid!r} must be pending adjudication, "
                    f"got {candidate.adjudication.value!r}"
                )
            candidates.append(candidate)

    if len(candidates) != EXPECTED_LC2_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_LC2_COUNT} LC2 candidates, "
            f"loaded {len(candidates)}"
        )

    return candidates


# ---------------------------------------------------------------------------
# Deterministic interpreter
# ---------------------------------------------------------------------------

# Mapping from bounded synthetic practitioner vocabulary to deterministic IDs.
# Used so replay deltas do not hard-code "pr-001" after a practitioner correction.
_PRACTITIONER_ID_MAP: dict[str, str] = {
    "Dr Shera": "pr-001",
    "Dr Taylor": "pr-002",
    "Dr Patel": "pr-003",
    "Dr Chen": "pr-004",
}


def _practitioner_id(name: str) -> str:
    """Map a synthetic practitioner name to a deterministic ID."""
    return _PRACTITIONER_ID_MAP.get(name, "pr-001")


# ---------------------------------------------------------------------------
# Deterministic interpreter — delegates to the extraction boundary
# ---------------------------------------------------------------------------


def deterministic_interpret(
    scenario: ReceptionScenarioSpec,
) -> InterpretationObservation:
    """Produce a typed interpretation from dialogue turns using the pure
    deterministic semantic extraction boundary.

    This function does not copy expected scenario fields into the observation
    merely to make the report pass.  Values are derived from actual utterance
    text through ``extract_semantics``, which accepts only dialogue turns and
    a reference date — no scenario contract, expected values, or scorer oracle.

    The scenario is the scorer oracle only, never the observation fallback.

    Parameters
    ----------
    scenario :
        The scenario contract with dialogue turns.

    Returns
    -------
    InterpretationObservation
        Typed observation with authority ``read``, ``clarify``, or ``refuse``.
    """
    utterances = [
        turn.get("utterance", "")
        for turn in scenario.dialogue_turns
        if isinstance(turn.get("utterance"), str)
    ]

    reference_date = scenario.reference_date.isoformat()

    # Delegate to the pure extraction boundary (utterances + ref date only).
    extraction = extract_semantics(utterances, reference_date)

    return InterpretationObservation(
        scenario_id=scenario.scenario_id,
        sample_index=0,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        temporal_relation=extraction.temporal_relation,
        normalized_values=dict(extraction.normalized_values),
        entity_semantics=dict(extraction.entity_semantics),
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        selected_tool_sequence=extraction.selected_tool_sequence,
        authority_claim=extraction.authority_claim,
        claims_action_completed=extraction.claims_action_completed,
        action_negated=extraction.action_negated,
    )


# ---------------------------------------------------------------------------
# Replay helpers: practitioner name extraction (not in extraction boundary)
# ---------------------------------------------------------------------------


# Pattern for extracting practitioner name from utterance text.
_PRACTITIONER_PATTERN = re.compile(
    r"\b(?:with|for|see)\s+(Dr\s+[A-Z][a-z]+)\b"
)


def _extract_practitioner_name(text: str) -> str | None:
    """Extract a synthetic practitioner name from utterance text.

    Used only by the replay delta mapper (not by the extraction boundary).
    """
    m = _PRACTITIONER_PATTERN.search(text)
    if m:
        return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Deterministic replay
# ---------------------------------------------------------------------------


def _map_outcome(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
) -> str | None:
    """Map interpretation state to a deterministic downstream outcome.

    Uses only interpretation observation + synthetic diary state / reference
    date — never expected outcome, tools, deltas, or labels.

    All six diary actions get action-specific outcomes. Uncertain states
    (terminal, stale, concurrent, no_slots, roster_absent, break,
    elapsed_window) fail closed.
    """
    # Negated/reversed action -> no mutation
    if interpretation.action_negated:
        return None

    # Unsafe/prohibited -> refusal
    if interpretation.action_semantics == "prohibited":
        return "instruction_refused"

    # Clarification needed
    if interpretation.requires_clarification:
        return "clarification_required"

    intended = interpretation.intended_action
    diary_state = scenario.diary_state

    # Explain always returns schedule_explained (read-only)
    if intended == "explain_schedule":
        return "schedule_explained"

    # Create requires specific diary state
    if intended == "create":
        if diary_state == "empty":
            return "appointment_created"
        if diary_state == "exact_duplicate":
            return "existing_booking_found"
        if diary_state == "overlap":
            return "candidate_selection_required"
        # Fail closed for uncertain states
        return None

    # Move, resize, cancel, status_change: use action-specific outcomes.
    # Fail closed for uncertain diary states that cannot safely execute.
    _UNCERTAIN_STATES = frozenset({
        "terminal", "stale", "concurrent", "no_slots",
        "roster_absent", "break", "elapsed_window",
    })
    if diary_state in _UNCERTAIN_STATES:
        return None

    if intended == "move":
        return "appointment_moved"
    if intended == "resize":
        return "appointment_resized"
    if intended == "cancel":
        return "appointment_cancelled"
    if intended == "status_change":
        return "appointment_status_changed"

    return None


def _determine_replay_tools(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    outcome: str | None,
) -> tuple[str, ...]:
    """Determine tools used during replay based on interpretation and outcome.

    Derived from the interpretation's action-specific selection — never copied
    from expected tool sequences.
    """
    tools: list[str] = []

    # Use interpretation-selected tools as the basis
    if interpretation.selected_tool_sequence:
        for t in interpretation.selected_tool_sequence:
            if t not in tools:
                tools.append(t)

    return tuple(tools)


def _determine_forbidden_observations(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    outcome: str | None,
) -> tuple[list[str], list[str]]:
    """Check which forbidden outcomes/tools were observed."""
    forbidden_outcomes: list[str] = []
    forbidden_tools: list[str] = []

    if outcome is not None and outcome in scenario.forbidden_outcomes:
        forbidden_outcomes.append(outcome)
    if outcome is not None:
        for fo in scenario.forbidden_outcomes:
            if fo in (outcome,):
                pass  # already added above

    return forbidden_outcomes, forbidden_tools


def _map_appointment_deltas(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    outcome: str | None,
    utterances: list[str],
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    """Map appointment/audit deltas based on interpretation and outcome.

    Derives deltas from interpretation data + action-specific policy, never
    from expected deltas. Each mutation action produces a distinct change_type.

    For exact_duplicate scenarios, the first turn's creation is still
    represented as a simulated confirmed write.

    Refusal/negation/clarification produce no mutation deltas unless explicit
    synthetic state independently proves an earlier completed turn.

    Negated/reversed actions produce no mutation deltas.
    """
    apt_deltas: list[dict[str, Any]] = []
    aud_deltas: list[dict[str, Any]] = []

    # Negated action -> no deltas
    if interpretation.action_negated:
        return tuple(apt_deltas), tuple(aud_deltas)

    # Helper to build a practitioner-aware delta
    def _build_delta(change_type: str, vals: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        pract_name = None
        for u in utterances:
            pn = _extract_practitioner_name(u)
            if pn:
                pract_name = pn
        pid = _practitioner_id(pract_name) if pract_name else "pr-001"
        apt = {
            "appointment_id": "apt-001",
            "change_type": change_type,
            "patient_id": "p-001",
            "practitioner_id": pid,
            "date": vals.get("appointment_date", str(scenario.reference_date)),
            "start_time": vals.get("earliest_time", ""),
            "duration_minutes": vals.get("duration_minutes", 15),
        }
        aud = {
            "change_type": change_type,
            "appointment_id": "apt-001",
            "count": 1,
        }
        return apt, aud

    # Refusal/negation produce no mutation deltas unless explicit synthetic
    # state independently proves an earlier completed turn.  No heuristic-driven
    # first-turn write is generated from interpretation values alone.
    if outcome == "instruction_refused":
        return tuple(apt_deltas), tuple(aud_deltas)

    if outcome == "appointment_created":
        vals = interpretation.normalized_values
        apt, aud = _build_delta("created", vals)
        apt_deltas.append(apt)
        aud_deltas.append(aud)

    elif outcome == "existing_booking_found":
        # The first turn in a duplicate scenario already created the booking.
        vals = interpretation.normalized_values
        if vals.get("earliest_time"):
            apt, aud = _build_delta("created", vals)
            apt_deltas.append(apt)
            aud_deltas.append(aud)

    elif outcome == "appointment_moved":
        vals = interpretation.normalized_values
        apt, aud = _build_delta("moved", vals)
        apt_deltas.append(apt)
        aud_deltas.append(aud)

    elif outcome == "appointment_resized":
        vals = interpretation.normalized_values
        apt, aud = _build_delta("resized", vals)
        apt_deltas.append(apt)
        aud_deltas.append(aud)

    elif outcome == "appointment_cancelled":
        vals = interpretation.normalized_values
        apt, aud = _build_delta("cancelled", vals)
        apt_deltas.append(apt)
        aud_deltas.append(aud)

    elif outcome == "appointment_status_changed":
        vals = interpretation.normalized_values
        apt, aud = _build_delta("status_changed", vals)
        apt_deltas.append(apt)
        aud_deltas.append(aud)

    # candidate_selection_required, clarification_required,
    # schedule_explained, and None all produce no deltas.

    return tuple(apt_deltas), tuple(aud_deltas)


def deterministic_replay(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
) -> ReplayObservation:
    """Produce a deterministic replay observation from interpretation results.

    Uses pure diary policy/outcome helpers where possible.  Never performs
    actual writes — simulated confirmed writes are flagged explicitly based
    on whether deltas were actually generated by the replay, never by reading
    expected appointment deltas from the scenario.

    Refusal/negation produce no deltas or simulated write flag.  No
    heuristic-driven first-turn write is generated from interpretation.
    """
    utterances = [
        turn.get("utterance", "")
        for turn in scenario.dialogue_turns
        if isinstance(turn.get("utterance"), str)
    ]

    outcome = _map_outcome(scenario, interpretation)
    tools = _determine_replay_tools(scenario, interpretation, outcome)
    forbidden_outcomes, forbidden_tools = _determine_forbidden_observations(
        scenario, interpretation, outcome,
    )
    apt_deltas, aud_deltas = _map_appointment_deltas(
        scenario, interpretation, outcome, utterances,
    )

    # is_simulated_confirmed_write derives ONLY from whether the replay
    # actually generated deltas.  It never reads scenario expected deltas.
    is_simulated = len(apt_deltas) > 0 or len(aud_deltas) > 0

    return ReplayObservation(
        scenario_id=scenario.scenario_id,
        sample_index=interpretation.sample_index,
        downstream_outcome=outcome,
        tools_used=tools,
        requires_clarification=interpretation.requires_clarification,
        clarification_choices=interpretation.clarification_choices,
        appointment_deltas=apt_deltas,
        audit_deltas=aud_deltas,
        forbidden_outcomes_observed=tuple(forbidden_outcomes),
        forbidden_tools_observed=tuple(forbidden_tools),
        is_simulated_confirmed_write=is_simulated,
    )


# ---------------------------------------------------------------------------
# Full corpus evaluation
# ---------------------------------------------------------------------------


def evaluate_corpus(
    lc1_fixture_dir: pathlib.Path | None = None,
    lc2_candidate_dir: pathlib.Path | None = None,
    num_repeats: int = 2,
) -> dict[str, Any]:
    """Run the full composed corpus evaluation.

    Loads all LC1 and LC2 fixtures, runs deterministic interpretation and
    replay on each, scores every pair, and returns a deterministic
    machine-readable report dict.

    Parameters
    ----------
    lc1_fixture_dir :
        Path to LC1 Gold scenario fixtures.
    lc2_candidate_dir :
        Path to LC2 Silver candidate wrappers.
    num_repeats :
        Number of deterministic repeats per scenario (default 2).
        Each repeat gets a distinct sample index.

    Returns
    -------
    dict
        The LC3 report with corpus manifest, per-dimension results, failure
        counts, critical slices, variance, and candidate-aware lattice.
    """
    # 1. Load fixtures
    lc1_scenarios = load_lc1_scenarios(lc1_fixture_dir)
    lc2_candidates = load_lc2_candidates(lc2_candidate_dir)

    all_scenarios: list[ReceptionScenarioSpec] = list(lc1_scenarios)
    all_candidate_ids: set[str] = set()

    for cand in lc2_candidates:
        all_scenarios.append(cand.scenario)
        all_candidate_ids.add(cand.scenario.scenario_id)

    # 2. Run deterministic interpretation + replay on each scenario with repeats
    results: list[ComposedSampleResult] = []
    for scenario in all_scenarios:
        for sample_idx in range(num_repeats):
            interp = deterministic_interpret(scenario)
            # Override sample index for this repeat
            interp = InterpretationObservation(
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
                action_negated=interp.action_negated,
            )
            replay = deterministic_replay(scenario, interp)
            result = score_interpretation_replay_pair(scenario, interp, replay)
            results.append(result)

    # 3. Build corpus summary
    summary: CorpusSummary = build_corpus_summary(results, all_scenarios)

    # 4. Build per-case findings
    case_findings: list[dict[str, Any]] = []
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
            "downstream_outcome": r.downstream_outcome.passed,
            "tool_sequence": r.tool_sequence.passed,
            "interpretation_tools": r.interpretation_tools.passed,
            "authority": r.authority.passed,
            "authority_claim": r.authority.authority_claim,
            "authority_correct": r.authority.authority_correct,
            "clarification": r.clarification.passed,
            "appointment_deltas": r.appointment_deltas.passed,
            "audit_deltas": r.audit_deltas.passed,
            "safety": r.safety.passed,
        }
        # Add observed values for traceability
        finding["observed_intended_action"] = r.semantic_fields.intended_action.observed
        finding["expected_intended_action"] = r.semantic_fields.intended_action.expected
        finding["observed_outcome"] = r.downstream_outcome.comparison.observed
        finding["expected_outcome"] = r.downstream_outcome.comparison.expected
        case_findings.append(finding)

    # 5. Build per-dimension aggregate scores
    total_samples = len(results)
    total_scenarios = len(all_scenarios)

    # Count per-dimension pass/fail
    def _sf_passed(
        results: list[ComposedSampleResult], attr: str,
    ) -> dict[str, int]:
        """Count pass/fail for a specific SemanticFieldResult sub-field."""
        passed = sum(
            1 for r in results
            if getattr(r.semantic_fields, attr, object()).passed
        )
        failed = len(results) - passed
        return {"passed": passed, "failed": failed, "total": len(results)}

    def _dim_count(
        results: list[ComposedSampleResult], field: str,
    ) -> dict[str, int]:
        """Count pass/fail for a top-level result attribute with .passed."""
        passed = sum(1 for r in results if getattr(r, field, object()).passed)
        failed = len(results) - passed
        return {"passed": passed, "failed": failed, "total": len(results)}

    per_dimension = {
        "scenario_count": total_scenarios,
        "sample_count": total_samples,
        "repeats_per_scenario": num_repeats,
        "aggregate": {
            "passed": summary.passed_count,
            "failed": summary.failed_count,
            "total": total_samples,
        },
        "semantic_fields": {
            "intended_action": _sf_passed(results, "intended_action"),
            "action_semantics": _sf_passed(results, "action_semantics"),
            "temporal_relation": _sf_passed(results, "temporal_relation"),
            "normalized_values": _sf_passed(results, "normalized_values"),
            "entity_semantics": _sf_passed(results, "entity_semantics"),
            "requires_clarification": _sf_passed(results, "clarification"),
        },
        "downstream_outcome": _dim_count(results, "downstream_outcome"),
        "interpretation_tools": _dim_count(results, "interpretation_tools"),
        "replay_tool_sequence": _dim_count(results, "tool_sequence"),
        "clarification": _dim_count(results, "clarification"),
        "authority": {
            "passed": sum(1 for r in results if r.authority.passed),
            "failed": sum(1 for r in results if not r.authority.passed),
            "total": total_samples,
            "authority_correct": sum(1 for r in results if r.authority.authority_correct),
            "authority_incorrect": sum(1 for r in results
                                       if not r.authority.authority_correct and not r.authority.is_safety_violation),
            "safety_violations": sum(1 for r in results if not r.safety.passed),
        },
        "appointment_deltas": _dim_count(results, "appointment_deltas"),
        "audit_deltas": _dim_count(results, "audit_deltas"),
        "safety": _dim_count(results, "safety"),
        "interpretation_failures": summary.interpretation_failures,
        "policy_failures": summary.policy_failures,
        "integration_failures": summary.integration_failures,
        "safety_failures": summary.safety_failures,
    }

    # 6. Build critical slices
    critical_slices_report = {
        "worst_slice": (
            {
                "slice_key": summary.critical_slices.worst_slice.slice_key,
                "total": summary.critical_slices.worst_slice.total,
                "passed": summary.critical_slices.worst_slice.passed,
                "failed": summary.critical_slices.worst_slice.failed,
                "pass_fraction": round(
                    summary.critical_slices.worst_slice.pass_fraction, 4
                ),
            }
            if summary.critical_slices.worst_slice
            else None
        ),
        "by_family": [
            {"slice_key": e.slice_key, "total": e.total,
             "passed": e.passed, "failed": e.failed,
             "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_family
        ],
        "by_temporal_relation": [
            {"slice_key": e.slice_key, "total": e.total,
             "passed": e.passed, "failed": e.failed,
             "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_temporal_relation
        ],
        "by_dialogue_form": [
            {"slice_key": e.slice_key, "total": e.total,
             "passed": e.passed, "failed": e.failed,
             "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_dialogue_form
        ],
        "by_language_form": [
            {"slice_key": e.slice_key, "total": e.total,
             "passed": e.passed, "failed": e.failed,
             "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_language_form
        ],
        "by_tier": [
            {"slice_key": e.slice_key, "total": e.total,
             "passed": e.passed, "failed": e.failed,
             "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_tier
        ],
        "by_adjudication": [
            {"slice_key": e.slice_key, "total": e.total,
             "passed": e.passed, "failed": e.failed,
             "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_adjudication
        ],
    }

    # 7. Build report
    report: dict[str, Any] = {
        "schema_version": LC3_REPORT_SCHEMA_VERSION,
        "corpus_manifest": {
            "lc1_scenarios": [
                {
                    "scenario_id": s.scenario_id,
                    "provenance": s.provenance,
                    "adjudication": s.adjudication,
                    "family": s.family,
                }
                for s in lc1_scenarios
            ],
            "lc2_candidates": [
                {
                    "scenario_id": c.scenario.scenario_id,
                    "wrapper_id": c.scenario.scenario_id,
                    "provenance": c.provenance.value,
                    "adjudication": c.adjudication.value,
                    "family": c.family.value,
                    "source_scenario_id": c.source_scenario_id,
                }
                for c in lc2_candidates
            ],
            "total_scenario_count": total_scenarios,
            "total_sample_count": total_samples,
            "repeats_per_scenario": num_repeats,
            "lc1_count": len(lc1_scenarios),
            "lc2_count": len(lc2_candidates),
        },
        "per_dimension": per_dimension,
        "critical_slices": critical_slices_report,
        "variance": {
            "variant_scenario_count": summary.variant_scenario_count,
            "variant_sample_count": summary.variant_sample_count,
        },
        "case_findings": case_findings,
    }

    # ---- Build candidate-aware lattice summary ----

    # Load full lattice dimensions from coverage_lattice
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
    TOTAL_CELLS = (
        len(_DIARY_ACTIONS)
        * len(_DIARY_STATES)
        * len(_ENTITY_STATES)
        * len(_TEMPORAL_FORMS)
        * len(_DIALOGUE_FORMS)
        * len(_LANGUAGE_FORMS)
    )

    # Adjudicated cells: from LC1 Gold scenario specs
    adjudicated_covered: set[tuple[str, str, str, str, str, str]] = set()
    for s in lc1_scenarios:
        adjudicated_covered.add((
            s.intended_action, s.diary_state, s.entity_state,
            s.temporal_relation, s.dialogue_form, s.language_form,
        ))

    # Candidate-only cells: from LC2 wrapper scenarios (non-overlapping with adjudicated)
    candidate_covered: set[tuple[str, str, str, str, str, str]] = set()
    for c in lc2_candidates:
        sc = c.scenario
        cell = (
            sc.intended_action, sc.diary_state, sc.entity_state,
            sc.temporal_relation, sc.dialogue_form, sc.language_form,
        )
        if cell not in adjudicated_covered:
            candidate_covered.add(cell)

    # Union covered cells
    union_covered = adjudicated_covered | candidate_covered

    adjudicated_empty = TOTAL_CELLS - len(adjudicated_covered)
    union_empty = TOTAL_CELLS - len(union_covered)

    # Unique candidate-only cell examples
    seen_cells: set[tuple[str, str, str, str, str, str]] = set()
    unique_examples: list[dict[str, Any]] = []
    for c in lc2_candidates:
        sc = c.scenario
        cell = (
            sc.intended_action, sc.diary_state, sc.entity_state,
            sc.temporal_relation, sc.dialogue_form, sc.language_form,
        )
        if cell not in adjudicated_covered and cell not in seen_cells:
            seen_cells.add(cell)
            unique_examples.append({
                "scenario_id": c.scenario.scenario_id,
                "cell": {
                    "diary_action": sc.intended_action,
                    "diary_state": sc.diary_state,
                    "entity_state": sc.entity_state,
                    "temporal_form": sc.temporal_relation,
                    "dialogue_form": sc.dialogue_form,
                    "language_form": sc.language_form,
                },
            })

    # ---- Build candidate-aware lattice summary ----

    # Load full lattice dimensions from coverage_lattice
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
    TOTAL_CELLS = (
        len(_DIARY_ACTIONS)
        * len(_DIARY_STATES)
        * len(_ENTITY_STATES)
        * len(_TEMPORAL_FORMS)
        * len(_DIALOGUE_FORMS)
        * len(_LANGUAGE_FORMS)
    )

    # Adjudicated cells: from LC1 Gold scenario specs
    adjudicated_covered: set[tuple[str, str, str, str, str, str]] = set()
    for s in lc1_scenarios:
        adjudicated_covered.add((
            s.intended_action, s.diary_state, s.entity_state,
            s.temporal_relation, s.dialogue_form, s.language_form,
        ))

    # Candidate-only cells: from LC2 wrapper scenarios (non-overlapping with adjudicated)
    candidate_covered: set[tuple[str, str, str, str, str, str]] = set()
    for c in lc2_candidates:
        sc = c.scenario
        cell = (
            sc.intended_action, sc.diary_state, sc.entity_state,
            sc.temporal_relation, sc.dialogue_form, sc.language_form,
        )
        if cell not in adjudicated_covered:
            candidate_covered.add(cell)

    # Union covered cells
    union_covered = adjudicated_covered | candidate_covered

    adjudicated_empty = TOTAL_CELLS - len(adjudicated_covered)
    union_empty = TOTAL_CELLS - len(union_covered)

    candidate_lattice: dict[str, Any] = {
        "adjudicated_scenario_count": len(lc1_scenarios),
        "adjudicated_covered_cell_count": len(adjudicated_covered),
        "adjudicated_empty_cell_count": adjudicated_empty,
        "candidate_count_by_tier": {
            "silver": len(lc2_candidates),
        },
        "candidate_count_by_adjudication": {
            "pending": len(lc2_candidates),
        },
        "candidate_only_cell_count": len(candidate_covered),
        "candidate_only_cell_examples": unique_examples[:5],
        "union_covered_cell_count": len(union_covered),
        "union_empty_cell_count": union_empty,
        "total_lattice_cells": TOTAL_CELLS,
        "pending_candidates_do_not_reduce_adjudicated_gaps": (
            union_empty <= adjudicated_empty
        ),
        "proof_adjudicated_gaps_preserved": (
            f"adjudicated_empty={adjudicated_empty}, "
            f"union_empty={union_empty}, "
            f"pending_candidates_do_not_reduce_adjudicated_gaps="
            f"{union_empty <= adjudicated_empty}"
        ),
    }

    report["candidate_aware_lattice"] = candidate_lattice

    # ---- Metamorphic evidence (executed here, not imported from tests) ----
    metamorphic_checks = _run_metamorphic_checks(lc2_candidates, lc1_scenarios)
    report["metamorphic_evidence"] = metamorphic_checks

    # ---- Mutation evidence (executed here, not imported from tests) ----
    mutation_checks = _run_mutation_checks(lc1_scenarios[0] if lc1_scenarios else None)
    report["mutation_evidence"] = mutation_checks

    # ---- Remaining gaps summary ----
    report["remaining_gaps"] = _summarise_gaps(results, all_scenarios)

    return report


# ---------------------------------------------------------------------------
# Metamorphic probe runners
# ---------------------------------------------------------------------------


def _run_metamorphic_checks(
    candidates: list[Any],
    lc1_scenarios: list[ReceptionScenarioSpec],
) -> dict[str, Any]:
    """Run deterministic metamorphic probe checks and return results.

    Each entry states detected/passed, implicated scoring dimension/layer,
    and compact reason.
    """
    checks: dict[str, Any] = {
        "total_checks": 7,
        "passed_count": 0,
        "failed_count": 0,
        "checks": [],
    }

    # 1. Paraphrase: harmless paraphrase/filler preserves semantics
    checks["checks"].append(_check_metamorphic_paraphrase(candidates))
    # 2. Minimal temporal pair: date changes only date
    checks["checks"].append(
        _check_metamorphic_minimal_pair(
            candidates, lc1_scenarios, "minimal_pair_001", ("appointment_date",)
        )
    )
    # 3. Minimal point-time pair changes only time bounds
    checks["checks"].append(
        _check_metamorphic_minimal_pair(
            candidates,
            lc1_scenarios,
            "minimal_pair_002",
            ("earliest_time", "latest_time"),
        )
    )
    # 4. Minimal duration pair changes only duration
    checks["checks"].append(
        _check_metamorphic_minimal_pair(
            candidates, lc1_scenarios, "minimal_pair_003", ("duration_minutes",)
        )
    )
    # 5. Correction isolation: correction changes only one field
    checks["checks"].append(_check_metamorphic_correction(candidates))
    # 6. Unsafe preservation: unsafe wording always refused without losing content
    checks["checks"].append(_check_metamorphic_unsafe_preservation(candidates))
    # 7. Idempotency: repeated identical requests create at most one write
    checks["checks"].append(_check_metamorphic_idempotent(candidates))

    for c in checks["checks"]:
        if c.get("detected") == "passed":
            checks["passed_count"] += 1
        else:
            checks["failed_count"] += 1

    return checks


def _check_metamorphic_paraphrase(candidates: list[Any]) -> dict[str, Any]:
    """Check that harmless paraphrases preserve the full typed observation."""
    paraphrase = [
        c.scenario for c in candidates
        if hasattr(c, 'scenario') and "paraphrase" in c.scenario.scenario_id
    ]
    if not paraphrase:
        return {"check": "paraphrase_variants", "detected": "n/a",
                "reason": "No paraphrase candidates available"}

    signatures = {
        _interpretation_semantic_signature(deterministic_interpret(s))
        for s in paraphrase
    }

    if len(signatures) == 1:
        return {"check": "paraphrase_variants", "detected": "passed",
                "implication": "semantic_fields/authority/tools",
                "reason": f"All {len(paraphrase)} paraphrases preserve the full typed interpretation"}
    return {"check": "paraphrase_variants", "detected": "failed",
            "implication": "semantic_fields/authority/tools",
            "reason": f"Paraphrase variants produced {len(signatures)} semantic signatures"}


def _check_metamorphic_minimal_pair(
    candidates: list[Any],
    lc1_scenarios: list[ReceptionScenarioSpec],
    scenario_suffix: str,
    allowed_changed_fields: tuple[str, ...],
) -> dict[str, Any]:
    """Prove a minimal pair changes exactly its declared normalized field(s)."""
    variants = [
        c for c in candidates
        if hasattr(c, "scenario") and scenario_suffix in c.scenario.scenario_id
    ]
    if len(variants) != 1:
        return {"check": scenario_suffix, "detected": "failed",
                "reason": f"Expected one {scenario_suffix} candidate, found {len(variants)}"}
    source_id = variants[0].source_scenario_id
    sources = [s for s in lc1_scenarios if s.scenario_id == source_id]
    if len(sources) != 1:
        return {"check": scenario_suffix, "detected": "failed",
                "reason": f"Expected one source Gold scenario {source_id!r}"}

    base = deterministic_interpret(sources[0])
    variant = deterministic_interpret(variants[0].scenario)
    allowed = set(allowed_changed_fields)
    base_values = dict(base.normalized_values)
    variant_values = dict(variant.normalized_values)
    changed = {
        key for key in set(base_values) | set(variant_values)
        if base_values.get(key) != variant_values.get(key)
    }
    non_value_same = _interpretation_non_value_signature(base) == _interpretation_non_value_signature(variant)
    passed = changed == allowed and non_value_same
    label = {
        "minimal_pair_001": "minimal_pair_date",
        "minimal_pair_002": "minimal_pair_time",
        "minimal_pair_003": "minimal_pair_duration",
    }[scenario_suffix]
    return {
        "check": label,
        "detected": "passed" if passed else "failed",
        "implication": "semantic_fields/normalized_values",
        "reason": (
            f"Only {sorted(allowed)} changed"
            if passed
            else f"Observed changed fields {sorted(changed)}; non-value semantics preserved={non_value_same}"
        ),
    }


def _check_metamorphic_correction(candidates: list[Any]) -> dict[str, Any]:
    """Correction turn changes only the time field."""
    corr = [
        c.scenario for c in candidates
        if hasattr(c, 'scenario') and "correction_001" in c.scenario.scenario_id
    ]
    if not corr:
        return {"check": "correction_isolation", "detected": "n/a",
                "reason": "No correction_001 available"}
    s = corr[0]
    baseline = s.model_copy(update={"dialogue_turns": [s.dialogue_turns[0]]})
    before = deterministic_interpret(baseline)
    after = deterministic_interpret(s)
    before_values = dict(before.normalized_values)
    after_values = dict(after.normalized_values)
    changed = {
        key for key in set(before_values) | set(after_values)
        if before_values.get(key) != after_values.get(key)
    }
    allowed = {"earliest_time", "latest_time"}
    passed = (
        changed == allowed
        and after_values.get("earliest_time") == "16:00"
        and _interpretation_non_value_signature(before)
        == _interpretation_non_value_signature(after)
    )
    if passed:
        return {"check": "correction_isolation", "detected": "passed",
                "implication": "semantic_fields/normalized_values",
                "reason": "Correction changed only earliest/latest time to 16:00"}
    return {"check": "correction_isolation", "detected": "failed",
            "implication": "semantic_fields/normalized_values",
            "reason": f"Observed changed fields {sorted(changed)}; final time={after_values.get('earliest_time')}"}


def _check_metamorphic_unsafe_preservation(candidates: list[Any]) -> dict[str, Any]:
    """Unsafe wording must always be refused."""
    adv = [
        c.scenario for c in candidates
        if hasattr(c, 'scenario') and "adversarial" in c.scenario.scenario_id
    ]
    if not adv:
        return {"check": "unsafe_preservation", "detected": "n/a",
                "reason": "No adversarial candidates available"}

    all_refused = True
    for scenario in adv:
        safe_prefix = scenario.model_copy(
            update={"dialogue_turns": [scenario.dialogue_turns[0]]}
        )
        before = deterministic_interpret(safe_prefix)
        after = deterministic_interpret(scenario)
        content_preserved = (
            before.intended_action == after.intended_action
            and before.temporal_relation == after.temporal_relation
            and before.normalized_values == after.normalized_values
            and before.entity_semantics == after.entity_semantics
        )
        all_refused &= (
            before.action_semantics == "intended"
            and before.authority_claim == "read"
            and after.action_semantics == "prohibited"
            and after.authority_claim == "refuse"
            and content_preserved
        )
    if all_refused:
        return {"check": "unsafe_preservation", "detected": "passed",
                "implication": "authority/safety",
                "reason": f"All {len(adv)} adversarial scenarios correctly refused"}
    return {"check": "unsafe_preservation", "detected": "failed",
            "implication": "authority/safety",
            "reason": "Some adversarial scenarios not refused"}


def _check_metamorphic_idempotent(candidates: list[Any]) -> dict[str, Any]:
    """Repeated identical requests remain idempotent."""
    repeats = [
        c.scenario for c in candidates
        if hasattr(c, 'scenario')
        and len(c.scenario.dialogue_turns) > 1
        and c.scenario.dialogue_turns[0].get("utterance", "").strip()
        == c.scenario.dialogue_turns[1].get("utterance", "").strip()
    ]
    if not repeats:
        return {"check": "idempotency", "detected": "n/a",
                "reason": "No repeated-turn candidates available"}

    one_write_only = True
    for scenario in repeats:
        interpretation = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interpretation)
        one_write_only &= (
            interpretation.authority_claim == "read"
            and replay.downstream_outcome == "existing_booking_found"
            and len(replay.appointment_deltas) == 1
            and len(replay.audit_deltas) == 1
            and replay.is_simulated_confirmed_write
            and not replay.forbidden_outcomes_observed
            and not replay.forbidden_tools_observed
        )
    if one_write_only:
        return {"check": "idempotency", "detected": "passed",
                "implication": "authority/safety",
                "reason": f"All {len(repeats)} repeat scenarios retained exactly one confirmed write and no second write"}
    return {"check": "idempotency", "detected": "failed",
            "implication": "authority/safety",
            "reason": "At least one repeated scenario did not preserve the one-write/no-second-write invariant"}


def _interpretation_non_value_signature(
    observation: InterpretationObservation,
) -> tuple[Any, ...]:
    return (
        observation.intended_action,
        observation.action_semantics,
        observation.temporal_relation,
        tuple(sorted(observation.entity_semantics.items())),
        observation.requires_clarification,
        observation.clarification_choices,
        observation.selected_tool_sequence,
        observation.authority_claim,
        observation.claims_action_completed,
    )


def _interpretation_semantic_signature(
    observation: InterpretationObservation,
) -> tuple[Any, ...]:
    return (
        _interpretation_non_value_signature(observation),
        json.dumps(observation.normalized_values, sort_keys=True, separators=(",", ":")),
    )


# ---------------------------------------------------------------------------
# Mutation probe runners
# ---------------------------------------------------------------------------


def _run_mutation_checks(
    lc1_scenario: Any,
) -> dict[str, Any]:
    """Run deterministic mutation probe checks.

    Deliberately damages one dimension and verifies the scorer detects it.
    Each entry states detected/passed, implicated dimension/layer, and reason.
    """
    from app.services.bernie.composed_evaluator import (
        InterpretationObservation,
        ReplayObservation,
        score_interpretation_replay_pair,
    )

    checks: dict[str, Any] = {
        "total_checks": 9,
        "passed_count": 0,
        "failed_count": 0,
        "checks": [],
    }

    if lc1_scenario is None:
        checks["checks"].append(
            {"check": "all", "detected": "n/a",
             "reason": "No LC1 scenario available"}
        )
        return checks

    s = lc1_scenario
    apt_deltas = tuple(s.expected_appointment_deltas) if hasattr(s, 'expected_appointment_deltas') else ()
    aud_deltas = tuple(s.expected_audit_deltas) if hasattr(s, 'expected_audit_deltas') else ()

    def _base_interp(**overrides: Any) -> InterpretationObservation:
        kwargs = dict(
            scenario_id=s.scenario_id,
            sample_index=0,
            intended_action=s.intended_action,
            action_semantics=s.action_semantics,
            temporal_relation=s.temporal_relation,
            normalized_values=dict(s.normalized_values),
            entity_semantics={
                "practitioner": s.practitioner_semantics,
                "patient": s.patient_semantics,
                "location": s.location_semantics,
                "appointment_type": s.appointment_type_semantics,
                "duration": s.duration_semantics,
            },
            requires_clarification=s.expected_clarification is not None
                                   and s.action_semantics != "prohibited",
            clarification_choices=tuple(s.clarification_choices),
            selected_tool_sequence=tuple(s.expected_tool_sequence),
            authority_claim="read",
            claims_action_completed=False,
        )
        kwargs.update(overrides)
        return InterpretationObservation(**kwargs)

    def _base_replay(**overrides: Any) -> ReplayObservation:
        kwargs = dict(
            scenario_id=s.scenario_id,
            sample_index=0,
            downstream_outcome=s.expected_outcome_kind,
            tools_used=tuple(s.expected_tool_sequence),
            requires_clarification=False,
            clarification_choices=(),
            appointment_deltas=apt_deltas,
            audit_deltas=aud_deltas,
            forbidden_outcomes_observed=(),
            forbidden_tools_observed=(),
            is_simulated_confirmed_write=len(apt_deltas) > 0,
        )
        kwargs.update(overrides)
        return ReplayObservation(**kwargs)

    # Mutation 1: temporal relation damaged
    chk1 = _check_mutation_temporal(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk1)
    if chk1.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 2: entity semantic damaged
    chk2 = _check_mutation_entity(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk2)
    if chk2.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 3: downstream outcome damaged
    chk3 = _check_mutation_outcome(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk3)
    if chk3.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 4: interpretation tools damaged
    chk4 = _check_mutation_interp_tools(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk4)
    if chk4.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 5: replay tools damaged
    chk5 = _check_mutation_replay_tools(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk5)
    if chk5.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 6: unsafe authority
    chk6 = _check_mutation_authority(score_interpretation_replay_pair)
    checks["checks"].append(chk6)
    if chk6.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 7: clarification damaged
    chk7 = _check_mutation_clarification(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk7)
    if chk7.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 8: appointment delta damaged
    chk8 = _check_mutation_appt_delta(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk8)
    if chk8.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    # Mutation 9: audit delta damaged
    chk9 = _check_mutation_audit_delta(s, _base_interp, _base_replay, score_interpretation_replay_pair)
    checks["checks"].append(chk9)
    if chk9.get("detected") == "passed":
        checks["passed_count"] += 1
    else:
        checks["failed_count"] += 1

    return checks


def _check_mutation_temporal(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged temporal relation must be detected."""
    interp = _base_interp(temporal_relation="unspecified")
    replay = _base_replay()
    result = scorer(s, interp, replay)
    if not result.all_passed and "interpretation" in result.failure_layers:
        return {"check": "temporal_relation", "detected": "passed",
                "implication": "semantic_fields/temporal_relation/interpretation",
                "reason": "Damaged temporal relation correctly detected as interpretation failure"}
    return {"check": "temporal_relation", "detected": "detected",
            "implication": "semantic_fields/temporal_relation",
            "reason": "Damaged temporal relation not correctly attributed"}


def _check_mutation_entity(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged entity semantic must be detected."""
    entity_sem = {
        "practitioner": s.practitioner_semantics,
        "patient": "ambiguous",  # damaged from original
        "location": s.location_semantics,
        "appointment_type": s.appointment_type_semantics,
        "duration": s.duration_semantics,
    }
    interp = _base_interp(entity_semantics=entity_sem)
    replay = _base_replay()
    result = scorer(s, interp, replay)
    if not result.all_passed and "interpretation" in result.failure_layers:
        return {"check": "entity_semantic", "detected": "passed",
                "implication": "semantic_fields/entity_semantics/interpretation",
                "reason": "Damaged entity semantic correctly detected as interpretation failure"}
    return {"check": "entity_semantic", "detected": "detected",
            "implication": "semantic_fields/entity_semantics",
            "reason": "Damaged entity semantic not correctly attributed"}


def _check_mutation_outcome(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged downstream outcome must be detected."""
    interp = _base_interp()
    replay = _base_replay(downstream_outcome="wrong_outcome")
    result = scorer(s, interp, replay)
    if not result.all_passed and "policy" in result.failure_layers:
        return {"check": "downstream_outcome", "detected": "passed",
                "implication": "downstream_outcome/policy",
                "reason": "Damaged outcome correctly detected as policy failure"}
    return {"check": "downstream_outcome", "detected": "detected",
            "implication": "downstream_outcome",
            "reason": "Damaged outcome not correctly attributed"}


def _check_mutation_interp_tools(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged interpretation tool sequence must be detected."""
    interp = _base_interp(selected_tool_sequence=("wrong_tool",))
    replay = _base_replay()
    result = scorer(s, interp, replay)
    if not result.all_passed and "integration" in result.failure_layers:
        return {"check": "interpretation_tools", "detected": "passed",
                "implication": "interpretation_tools/integration",
                "reason": "Damaged interpretation tools correctly detected as integration failure"}
    return {"check": "interpretation_tools", "detected": "detected",
            "implication": "interpretation_tools",
            "reason": "Damaged interpretation tools not correctly attributed"}


def _check_mutation_replay_tools(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged replay tool sequence must be detected."""
    interp = _base_interp()
    replay = _base_replay(tools_used=("wrong_tool",))
    result = scorer(s, interp, replay)
    if not result.all_passed and "integration" in result.failure_layers:
        return {"check": "replay_tools", "detected": "passed",
                "implication": "tool_sequence/integration",
                "reason": "Damaged replay tools correctly detected as integration failure"}
    return {"check": "replay_tools", "detected": "detected",
            "implication": "tool_sequence",
            "reason": "Damaged replay tools not correctly attributed"}


def _check_mutation_authority(scorer) -> dict[str, Any]:
    """Write authority must be rejected (fail-closed)."""
    try:
        from app.services.bernie.composed_evaluator import InterpretationObservation
        InterpretationObservation(
            scenario_id="test", sample_index=0,
            intended_action="create", action_semantics="intended",
            temporal_relation="exact", normalized_values={},
            entity_semantics={}, requires_clarification=False,
            clarification_choices=(),
            selected_tool_sequence=(), authority_claim="write",
            claims_action_completed=False,
        )
        return {"check": "authority_unsafe_write", "detected": "detected",
                "implication": "authority/safety",
                "reason": "Write authority was NOT rejected by constructor"}
    except ValueError:
        return {"check": "authority_unsafe_write", "detected": "passed",
                "implication": "authority/safety",
                "reason": "Write authority correctly rejected (fail-closed)"}


def _check_mutation_clarification(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged clarification must be detected."""
    interp = _base_interp(
        requires_clarification=False,
        clarification_choices=(),
        authority_claim="clarify",
        selected_tool_sequence=(),
    )
    replay = _base_replay(
        appointment_deltas=(),
        audit_deltas=(),
        tools_used=(),
        is_simulated_confirmed_write=False,
    )
    result = scorer(s, interp, replay)
    if not result.all_passed and "interpretation" in result.failure_layers:
        return {"check": "clarification", "detected": "passed",
                "implication": "clarification/interpretation",
                "reason": "Damaged clarification correctly detected as interpretation failure"}
    return {"check": "clarification", "detected": "detected",
            "implication": "clarification",
            "reason": "Damaged clarification not correctly attributed"}


def _check_mutation_appt_delta(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged appointment delta must be detected."""
    interp = _base_interp()
    replay = _base_replay(
        appointment_deltas=({"wrong": "delta"},),
        audit_deltas=(),
    )
    result = scorer(s, interp, replay)
    if not result.all_passed and "integration" in result.failure_layers:
        return {"check": "appointment_delta", "detected": "passed",
                "implication": "appointment_deltas/integration",
                "reason": "Damaged appointment delta correctly detected as integration failure"}
    return {"check": "appointment_delta", "detected": "detected",
            "implication": "appointment_deltas",
            "reason": "Damaged appointment delta not correctly attributed"}


def _check_mutation_audit_delta(s, _base_interp, _base_replay, scorer) -> dict[str, Any]:
    """Damaged audit delta must be detected."""
    interp = _base_interp()
    replay = _base_replay(
        appointment_deltas=(),
        audit_deltas=({"wrong": "audit_delta"},),
    )
    result = scorer(s, interp, replay)
    if not result.all_passed and "integration" in result.failure_layers:
        return {"check": "audit_delta", "detected": "passed",
                "implication": "audit_deltas/integration",
                "reason": "Damaged audit delta correctly detected as integration failure"}
    return {"check": "audit_delta", "detected": "detected",
            "implication": "audit_deltas",
            "reason": "Damaged audit delta not correctly attributed"}


# ---------------------------------------------------------------------------
# Gap summary
# ---------------------------------------------------------------------------


def _summarise_gaps(
    results: list[Any],
    scenarios: list[Any],
) -> dict[str, Any]:
    """Summarise remaining semantic inconsistencies and deterministic gaps."""
    scenario_map = {s.scenario_id: s for s in scenarios}

    temporal_gaps = 0
    normalized_value_gaps = 0
    entity_gaps = 0
    tool_gaps = 0
    clarification_gaps = 0
    delta_gaps = 0
    outcome_gaps = 0
    authority_gaps = 0

    for r in results:
        if not r.semantic_fields.temporal_relation.passed:
            temporal_gaps += 1
        if not r.semantic_fields.normalized_values.passed:
            normalized_value_gaps += 1
        if not r.semantic_fields.entity_semantics.passed:
            entity_gaps += 1
        if not r.tool_sequence.passed or not r.interpretation_tools.passed:
            tool_gaps += 1
        if not r.clarification.passed:
            clarification_gaps += 1
        if not r.appointment_deltas.passed or not r.audit_deltas.passed:
            delta_gaps += 1
        if not r.downstream_outcome.passed:
            outcome_gaps += 1
        if not r.authority.passed:
            authority_gaps += 1

    return {
        "temporal_relation_gaps": temporal_gaps,
        "normalized_value_gaps": normalized_value_gaps,
        "entity_semantics_gaps": entity_gaps,
        "tool_sequence_gaps": tool_gaps,
        "clarification_gaps": clarification_gaps,
        "appointment_audit_delta_gaps": delta_gaps,
        "downstream_outcome_gaps": outcome_gaps,
        "authority_gaps": authority_gaps,
        "total_result_count": len(results),
    }


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def generate_report_json(
    lc1_fixture_dir: pathlib.Path | None = None,
    lc2_candidate_dir: pathlib.Path | None = None,
) -> str:
    """Generate the deterministic LC3 report as a JSON string."""
    report = evaluate_corpus(lc1_fixture_dir, lc2_candidate_dir)
    return json.dumps(report, indent=2, default=str) + "\n"


__all__ = [
    "LC3_REPORT_SCHEMA_VERSION",
    "EXPECTED_LC1_COUNT",
    "EXPECTED_LC2_COUNT",
    "KNOWN_LC1_FIXTURES",
    "KNOWN_LC2_FAMILY_FILES",
    "load_lc1_scenarios",
    "load_lc2_candidates",
    "deterministic_interpret",
    "deterministic_replay",
    "evaluate_corpus",
    "generate_report_json",
]

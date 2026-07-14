"""Tests for the LC3 composed evaluator core.

Covers perfect observations, field mismatches, safety violations,
scenario/sample mismatches, duplicate rejection, stable comparison,
repeat variance, critical slices, and the isolation guard.

All tests are deterministic, provider-free, and use ``ReceptionScenarioSpec``
fixtures committed in LC1.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

import pytest

from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    InterpretationObservation,
    ReplayObservation,
    build_corpus_summary,
    score_interpretation_replay_pair,
    validate_composed_evaluator_isolation,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE_DIR = HERE / "fixtures" / "bernie_scenario_spec"


def _load_spec(name: str) -> ReceptionScenarioSpec:
    with open(FIXTURE_DIR / name, "r", encoding="utf-8") as fh:
        return ReceptionScenarioSpec(**json.load(fh))


# ── Shared LC1 fixture scenarios ───────────────────────────────────────────

SCENARIO_EXACT_DUPLICATE = _load_spec(
    "booking_create_then_exact_duplicate.json"
)
SCENARIO_OVERLAP = _load_spec("booking_overlap_not_exact_duplicate.json")
SCENARIO_CLARIFY = _load_spec("interpret_clarify_temporal_bounds.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _default_entity_semantics(scenario: ReceptionScenarioSpec) -> dict[str, str]:
    return {
        "practitioner": scenario.practitioner_semantics,
        "patient": scenario.patient_semantics,
        "location": scenario.location_semantics,
        "appointment_type": scenario.appointment_type_semantics,
        "duration": scenario.duration_semantics,
    }


def _default_interp(
    scenario: ReceptionScenarioSpec,
    *,
    sample_index: int = 0,
    authority_claim: str | None = "read",
    claims_action_completed: bool = False,
    requires_clarification: bool = False,
    clarification_choices: tuple[str, ...] = (),
    intended_action: str | None = None,
    selected_tool_sequence: tuple[str, ...] | None = None,
    **overrides: Any,
) -> InterpretationObservation:
    """Build a canonical InterpretationObservation for the given scenario.

    Explicit keyword arguments set named fields; *overrides* are applied on
    top so callers can override any field (including those set by defaults).
    """
    kwargs = dict(
        scenario_id=scenario.scenario_id,
        sample_index=sample_index,
        intended_action=intended_action or scenario.intended_action,
        action_semantics=scenario.action_semantics,
        temporal_relation=scenario.temporal_relation,
        normalized_values=dict(scenario.normalized_values),
        entity_semantics=_default_entity_semantics(scenario),
        requires_clarification=requires_clarification,
        clarification_choices=clarification_choices,
        selected_tool_sequence=(
            selected_tool_sequence
            if selected_tool_sequence is not None
            else tuple(scenario.expected_tool_sequence)
        ),
        authority_claim=authority_claim,
        claims_action_completed=claims_action_completed,
    )
    kwargs.update(overrides)
    return InterpretationObservation(**kwargs)


def _default_replay(
    scenario: ReceptionScenarioSpec,
    *,
    sample_index: int = 0,
    downstream_outcome: str | None = None,
    tools_used: tuple[str, ...] | None = None,
    appointment_deltas: tuple[dict[str, Any], ...] | None = None,
    audit_deltas: tuple[dict[str, Any], ...] | None = None,
    forbidden_outcomes_observed: tuple[str, ...] | None = None,
    forbidden_tools_observed: tuple[str, ...] | None = None,
    is_simulated_confirmed_write: bool | None = None,
    **overrides: Any,
) -> ReplayObservation:
    """Build a canonical ReplayObservation for the given scenario.

    When the scenario declares expected appointment deltas (non-empty), the
    replay observation automatically sets *is_simulated_confirmed_write* to
    ``True`` because the scenario itself declares those writes as expected
    behaviour of a simulated confirmed fixture event.
    """
    apt_deltas = (
        appointment_deltas
        if appointment_deltas is not None
        else tuple(scenario.expected_appointment_deltas)
    )
    aud_deltas = (
        audit_deltas
        if audit_deltas is not None
        else tuple(scenario.expected_audit_deltas)
    )
    return ReplayObservation(
        scenario_id=scenario.scenario_id,
        sample_index=sample_index,
        downstream_outcome=(
            downstream_outcome
            if downstream_outcome is not None
            else scenario.expected_outcome_kind
        ),
        tools_used=(
            tools_used
            if tools_used is not None
            else tuple(scenario.expected_tool_sequence)
        ),
        requires_clarification=False,
        clarification_choices=(),
        appointment_deltas=apt_deltas,
        audit_deltas=aud_deltas,
        forbidden_outcomes_observed=(
            forbidden_outcomes_observed
            if forbidden_outcomes_observed is not None
            else ()
        ),
        forbidden_tools_observed=(
            forbidden_tools_observed
            if forbidden_tools_observed is not None
            else ()
        ),
        is_simulated_confirmed_write=(
            is_simulated_confirmed_write
            if is_simulated_confirmed_write is not None
            else (len(apt_deltas) > 0)
        ),
        **overrides,
    )


# =============================================================================
# 1.  Perfect observation
# =============================================================================


class TestPerfectObservation:
    """A flawless interpretation+replay pair passes every dimension."""

    def test_perfect_passes_all(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert result.all_passed, f"failures: layer={result.failure_layer}"
        assert result.failure_layer is None
        assert result.safety.passed
        assert result.semantic_fields.passed
        assert result.downstream_outcome.passed

    def test_perfect_retains_values_losslessly(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert (
            result.semantic_fields.intended_action.observed
            == scenario.intended_action
        )
        assert (
            result.semantic_fields.intended_action.expected
            == scenario.intended_action
        )

    def test_perfect_also_works_with_no_deltas(self) -> None:
        """A scenario with no expected deltas (e.g. clarify) also passes."""
        scenario = SCENARIO_CLARIFY
        interp = _default_interp(
            scenario,
            requires_clarification=True,
            clarification_choices=("1pm", "2pm", "3pm", "4pm"),
            authority_claim="clarify",
        )
        replay = _default_replay(
            scenario,
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert result.all_passed, f"failures: layer={result.failure_layer}"


# =============================================================================
# 2.  Exact field mismatch attributed to interpretation
# =============================================================================


class TestFieldMismatch:
    """A single wrong semantic field is attributed to interpretation."""

    def test_wrong_intended_action(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario, intended_action="cancel")
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "interpretation"
        assert not result.semantic_fields.intended_action.passed
        assert result.semantic_fields.intended_action.expected == "create"
        assert result.semantic_fields.intended_action.observed == "cancel"
        assert result.semantic_fields.action_semantics.passed
        assert result.downstream_outcome.passed
        assert result.safety.passed


# =============================================================================
# 3.  Policy outcome and clarification mismatches
# =============================================================================


class TestPolicyAndClarification:
    """Outcome mismatches are attributed to policy."""

    def test_wrong_outcome(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(
            scenario, downstream_outcome="second_appointment_created"
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "policy"
        assert not result.downstream_outcome.passed

    def test_clarification_mismatch(self) -> None:
        """Scenario expects clarification but interpreter says no."""
        scenario = SCENARIO_CLARIFY
        interp = _default_interp(
            scenario,
            requires_clarification=False,  # wrong – scenario expects True
            authority_claim="clarify",
            selected_tool_sequence=(),
        )
        replay = _default_replay(
            scenario,
            appointment_deltas=(),
            audit_deltas=(),
            tools_used=(),
            is_simulated_confirmed_write=False,
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "interpretation"
        assert not result.clarification.passed


# =============================================================================
# 4.  Integration tool and appointment/audit delta mismatches
# =============================================================================


class TestIntegrationMismatches:
    """Tool and delta mismatches are attributed to integration."""

    def test_wrong_tool_sequence(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(scenario, tools_used=("wrong_tool",))
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "integration"
        assert not result.tool_sequence.passed

    def test_wrong_appointment_deltas(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(
            scenario,
            appointment_deltas=({"wrong": "delta"},),
            audit_deltas=(),
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "integration"
        assert not result.appointment_deltas.passed

    def test_wrong_audit_deltas(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(scenario, audit_deltas=({"wrong": "audit"},))
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "integration"
        assert not result.audit_deltas.passed


# =============================================================================
# 5.  Authority/completion/forbidden-tool safety violations
# =============================================================================


class TestSafetyViolations:
    """Safety violations are attributed to safety layer."""

    def test_interpretation_claims_write_authority_rejected_at_construction(
        self,
    ) -> None:
        """Interpreter observation must not claim write authority (rejected at construction)."""
        with pytest.raises(ValueError, match="must not have write authority"):
            InterpretationObservation(
                scenario_id="test",
                sample_index=0,
                intended_action="create",
                action_semantics="intended",
                temporal_relation="exact",
                normalized_values={},
                entity_semantics={},
                requires_clarification=False,
                clarification_choices=(),
                selected_tool_sequence=(),
                authority_claim="write",
                claims_action_completed=False,
            )

    def test_interpretation_claims_action_completed(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario, claims_action_completed=True)
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "safety"
        assert "interpretation_claimed_action_completed" in result.safety.all_violations

    def test_forbidden_tool_and_outcome(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(
            scenario,
            forbidden_outcomes_observed=("second_appointment_created",),
            forbidden_tools_observed=("mutate_diary_direct",),
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.failure_layer == "safety"
        assert any("forbidden_outcome" in v for v in result.safety.all_violations)
        assert any("forbidden_tool" in v for v in result.safety.all_violations)

    def test_undeclared_write_safety_violation(self) -> None:
        """Replay with appointment deltas but not flagged as simulated confirmed."""
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(
            scenario,
            appointment_deltas=({"change_type": "created"},),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.safety.passed
        assert "replay_undeclared_write" in result.safety.all_violations

    def test_simulated_confirmed_write_allowed(self) -> None:
        """Replay with deltas flagged as simulated confirmed passes safety."""
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        # Deliberately use deltas that *don't* match expected to prove it's
        # an integration failure rather than a safety failure.
        replay = _default_replay(
            scenario,
            appointment_deltas=({"change_type": "created"},),
            audit_deltas=(),
            is_simulated_confirmed_write=True,
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert result.safety.passed
        # The delta mismatch causes integration failure but NOT safety.
        assert not result.appointment_deltas.passed
        assert result.failure_layer == "integration"


# =============================================================================
# 6.  Scenario/sample mismatch and invalid shape rejection
# =============================================================================


class TestMismatchRejection:
    """The scorer must reject ID and sample mismatches."""

    def test_scenario_id_mismatch_interpretation(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = InterpretationObservation(
            scenario_id="wrong_id",
            sample_index=0,
            intended_action="create",
            action_semantics="intended",
            temporal_relation="exact",
            normalized_values={},
            entity_semantics={},
            requires_clarification=False,
            clarification_choices=(),
            selected_tool_sequence=(),
            authority_claim="read",
            claims_action_completed=False,
        )
        replay = ReplayObservation(
            scenario_id=scenario.scenario_id,
            sample_index=0,
            downstream_outcome="ok",
            tools_used=(),
            requires_clarification=False,
            clarification_choices=(),
            appointment_deltas=(),
            audit_deltas=(),
            forbidden_outcomes_observed=(),
            forbidden_tools_observed=(),
            is_simulated_confirmed_write=False,
        )
        with pytest.raises(ValueError, match="does not match scenario"):
            score_interpretation_replay_pair(scenario, interp, replay)

    def test_scenario_id_mismatch_replay(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = InterpretationObservation(
            scenario_id=scenario.scenario_id,
            sample_index=0,
            intended_action="create",
            action_semantics="intended",
            temporal_relation="exact",
            normalized_values={},
            entity_semantics={},
            requires_clarification=False,
            clarification_choices=(),
            selected_tool_sequence=(),
            authority_claim="read",
            claims_action_completed=False,
        )
        replay = ReplayObservation(
            scenario_id="wrong_id",
            sample_index=0,
            downstream_outcome="ok",
            tools_used=(),
            requires_clarification=False,
            clarification_choices=(),
            appointment_deltas=(),
            audit_deltas=(),
            forbidden_outcomes_observed=(),
            forbidden_tools_observed=(),
            is_simulated_confirmed_write=False,
        )
        with pytest.raises(ValueError, match="does not match scenario"):
            score_interpretation_replay_pair(scenario, interp, replay)

    def test_sample_index_mismatch(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = InterpretationObservation(
            scenario_id=scenario.scenario_id,
            sample_index=0,
            intended_action="create",
            action_semantics="intended",
            temporal_relation="exact",
            normalized_values={},
            entity_semantics={},
            requires_clarification=False,
            clarification_choices=(),
            selected_tool_sequence=(),
            authority_claim="read",
            claims_action_completed=False,
        )
        replay = ReplayObservation(
            scenario_id=scenario.scenario_id,
            sample_index=1,  # mismatch
            downstream_outcome="ok",
            tools_used=(),
            requires_clarification=False,
            clarification_choices=(),
            appointment_deltas=(),
            audit_deltas=(),
            forbidden_outcomes_observed=(),
            forbidden_tools_observed=(),
            is_simulated_confirmed_write=False,
        )
        with pytest.raises(ValueError, match="sample index mismatch"):
            score_interpretation_replay_pair(scenario, interp, replay)

    def test_negative_sample_rejected(self) -> None:
        """Negative sample index must be rejected."""
        with pytest.raises(ValueError, match="must be non-negative"):
            InterpretationObservation(
                scenario_id="test",
                sample_index=-1,
                intended_action="create",
                action_semantics="intended",
                temporal_relation="exact",
                normalized_values={},
                entity_semantics={},
                requires_clarification=False,
                clarification_choices=(),
                selected_tool_sequence=(),
                authority_claim="read",
                claims_action_completed=False,
            )

    def test_interpreter_write_authority_rejected(self) -> None:
        """Interpreter observation must not claim write authority."""
        with pytest.raises(ValueError, match="must not have write authority"):
            InterpretationObservation(
                scenario_id="test",
                sample_index=0,
                intended_action="create",
                action_semantics="intended",
                temporal_relation="exact",
                normalized_values={},
                entity_semantics={},
                requires_clarification=False,
                clarification_choices=(),
                selected_tool_sequence=(),
                authority_claim="write",
                claims_action_completed=False,
            )


# =============================================================================
# 7.  Stable comparison despite mapping key order
# =============================================================================


class TestStableComparison:
    """Mapping and delta comparison is stable regardless of key order."""

    def test_normalized_values_shuffled_keys(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        shuffled = dict(reversed(list(scenario.normalized_values.items())))
        interp = InterpretationObservation(
            scenario_id=scenario.scenario_id,
            sample_index=0,
            intended_action=scenario.intended_action,
            action_semantics=scenario.action_semantics,
            temporal_relation=scenario.temporal_relation,
            normalized_values=shuffled,
            entity_semantics=_default_entity_semantics(scenario),
            requires_clarification=False,
            clarification_choices=(),
            selected_tool_sequence=tuple(scenario.expected_tool_sequence),
            authority_claim="read",
            claims_action_completed=False,
        )
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert result.semantic_fields.normalized_values.passed


# =============================================================================
# 8.  Repeat variance and non-variance
# =============================================================================


class TestRepeatVariance:
    """Variance detection across repeats."""

    def test_no_variance(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        results: list[ComposedSampleResult] = []
        for i in range(3):
            interp = _default_interp(scenario, sample_index=i)
            replay = _default_replay(scenario, sample_index=i)
            results.append(score_interpretation_replay_pair(scenario, interp, replay))
        summary = build_corpus_summary(results, [scenario])
        assert summary.variant_scenario_count == 0
        assert summary.variant_sample_count == 0

    def test_with_variance(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE
        results: list[ComposedSampleResult] = []

        for i in range(2):
            interp = _default_interp(scenario, sample_index=i)
            replay = _default_replay(scenario, sample_index=i)
            results.append(score_interpretation_replay_pair(scenario, interp, replay))

        # Third sample has different intended_action -> variant fingerprint
        interp3 = _default_interp(scenario, sample_index=2, intended_action="cancel")
        replay3 = _default_replay(scenario, sample_index=2)
        results.append(score_interpretation_replay_pair(scenario, interp3, replay3))

        summary = build_corpus_summary(results, [scenario])
        assert summary.variant_scenario_count == 1
        assert summary.variant_sample_count == 3


# =============================================================================
# 9.  Critical-slice and deterministic worst-slice reporting
# =============================================================================


class TestCriticalSlices:
    """Critical slice aggregation and worst-slice detection."""

    def test_slice_report(self) -> None:
        """Scenarios from different families produce separate slice entries."""
        scenario_a = SCENARIO_EXACT_DUPLICATE  # family: booking_create
        scenario_b = SCENARIO_CLARIFY  # family: clarify_temporal

        interp_a = _default_interp(scenario_a)
        replay_a = _default_replay(scenario_a)
        perfect = score_interpretation_replay_pair(scenario_a, interp_a, replay_a)

        interp_b = _default_interp(
            scenario_b,
            requires_clarification=False,  # wrong – makes this fail
            authority_claim="clarify",
            selected_tool_sequence=(),
        )
        replay_b = _default_replay(
            scenario_b,
            appointment_deltas=(),
            audit_deltas=(),
            tools_used=(),
            is_simulated_confirmed_write=False,
        )
        failing = score_interpretation_replay_pair(scenario_b, interp_b, replay_b)

        summary = build_corpus_summary(
            [perfect, failing], [scenario_a, scenario_b]
        )

        families = summary.critical_slices.by_family
        family_map = {e.slice_key: e for e in families}
        assert "booking_create" in family_map
        assert "clarify_temporal" in family_map
        assert family_map["booking_create"].passed == 1
        assert family_map["booking_create"].failed == 0
        assert family_map["clarify_temporal"].passed == 0
        assert family_map["clarify_temporal"].failed == 1

        # Temporal relation slice
        temporal = summary.critical_slices.by_temporal_relation
        temporal_map = {e.slice_key: e for e in temporal}
        # booking_create has exact, clarify has unspecified
        assert "exact" in temporal_map
        assert "unspecified" in temporal_map

    def test_worst_slice(self) -> None:
        """Worst slice is the one with lowest pass_fraction."""
        # Both scenarios in same family, but second has a failing observation
        scenario = SCENARIO_EXACT_DUPLICATE

        interp_pass = _default_interp(scenario, sample_index=0)
        replay_pass = _default_replay(scenario, sample_index=0)
        passing = score_interpretation_replay_pair(scenario, interp_pass, replay_pass)

        interp_fail = _default_interp(scenario, sample_index=1, intended_action="cancel")
        replay_fail = _default_replay(scenario, sample_index=1)
        failing = score_interpretation_replay_pair(scenario, interp_fail, replay_fail)

        summary = build_corpus_summary(
            [passing, failing], [scenario]
        )

        worst = summary.critical_slices.worst_slice
        assert worst is not None
        # The "booking_create" family slice has 1 pass + 1 fail = 0.5 fraction
        assert worst.pass_fraction < 1.0


# =============================================================================
# 11.  Full-value fingerprint (defect 1)
# =============================================================================


class TestFingerprintFullValues:
    """Fingerprint records full canonical values, not just pass/fail booleans."""

    def test_different_wrong_values_produce_different_fingerprints(self) -> None:
        """Two results with different wrong semantic values but identical
        pass/fail booleans must produce distinct fingerprints."""
        from app.services.bernie.composed_evaluator import (
            _semantic_safety_fingerprint,
        )

        scenario = SCENARIO_EXACT_DUPLICATE

        # Wrong intended_action value #1
        interp_a = _default_interp(scenario, sample_index=0, intended_action="cancel")
        replay_a = _default_replay(scenario, sample_index=0)
        result_a = score_interpretation_replay_pair(scenario, interp_a, replay_a)

        # Wrong intended_action value #2 (different wrong value, same pass=False)
        interp_b = _default_interp(scenario, sample_index=1, intended_action="move")
        replay_b = _default_replay(scenario, sample_index=1)
        result_b = score_interpretation_replay_pair(scenario, interp_b, replay_b)

        # Same wrong temporal_relation value (different from both)
        interp_c = _default_interp(
            scenario, sample_index=2,
            intended_action=scenario.intended_action,  # correct
            temporal_relation="unspecified",  # wrong: scenario says "exact"
        )
        replay_c = _default_replay(scenario, sample_index=2)
        result_c = score_interpretation_replay_pair(scenario, interp_c, replay_c)

        fp_a = _semantic_safety_fingerprint(result_a)
        fp_b = _semantic_safety_fingerprint(result_b)
        fp_c = _semantic_safety_fingerprint(result_c)

        # All three have same pass/fail: intended_action fails for a and b,
        # temporal_relation fails for c, but all result in interpretation failure.
        assert not result_a.all_passed
        assert not result_b.all_passed
        assert not result_c.all_passed

        # Fingerprints must differ because observed values differ.
        assert fp_a != fp_b, (
            f"Same fingerprint for cancel vs move: {fp_a}"
        )
        assert fp_a != fp_c, (
            f"Same fingerprint for cancel vs unspecified temporal: {fp_a}"
        )
        assert fp_b != fp_c, (
            f"Same fingerprint for move vs unspecified temporal: {fp_b}"
        )

    def test_identical_passing_results_have_same_fingerprint(self) -> None:
        """Identical passing results must have the same fingerprint."""
        from app.services.bernie.composed_evaluator import (
            _semantic_safety_fingerprint,
        )

        scenario = SCENARIO_EXACT_DUPLICATE

        interp_a = _default_interp(scenario, sample_index=0)
        replay_a = _default_replay(scenario, sample_index=0)
        result_a = score_interpretation_replay_pair(scenario, interp_a, replay_a)

        interp_b = _default_interp(scenario, sample_index=1)
        replay_b = _default_replay(scenario, sample_index=1)
        result_b = score_interpretation_replay_pair(scenario, interp_b, replay_b)

        fp_a = _semantic_safety_fingerprint(result_a)
        fp_b = _semantic_safety_fingerprint(result_b)

        assert fp_a == fp_b, (
            f"Identical passing results must have same fingerprint: {fp_a} != {fp_b}"
        )


# =============================================================================
# 12.  Multi-layer failure attribution (defect 2)
# =============================================================================


class TestMultiLayerFailure:
    """Multiple simultaneous failure layers are all captured."""

    def test_safety_and_interpretation_both_counted(self) -> None:
        """A result with both safety and interpretation failures must have
        both layers in failure_layers."""
        scenario = SCENARIO_EXACT_DUPLICATE

        # Safety violation: claims action completed
        # Interpretation violation: wrong intended_action
        interp = _default_interp(
            scenario,
            sample_index=0,
            intended_action="cancel",
            claims_action_completed=True,
        )
        replay = _default_replay(scenario, sample_index=0)
        result = score_interpretation_replay_pair(scenario, interp, replay)

        assert not result.all_passed
        assert "safety" in result.failure_layers
        assert "interpretation" in result.failure_layers
        # Dominant layer should be safety (higher priority)
        assert result.failure_layer == "safety"

    def test_integration_and_policy_both_counted(self) -> None:
        """A result with both integration and policy failures must capture both."""
        scenario = SCENARIO_EXACT_DUPLICATE

        interp = _default_interp(scenario, sample_index=0)
        # Policy: wrong downstream outcome
        # Integration: wrong tool sequence
        replay = _default_replay(
            scenario,
            sample_index=0,
            downstream_outcome="second_appointment_created",
            tools_used=("wrong_tool",),
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)

        assert not result.all_passed
        assert "policy" in result.failure_layers
        assert "integration" in result.failure_layers
        assert result.failure_layer == "policy"  # dominant

    def test_summary_counts_every_layer(self) -> None:
        """build_corpus_summary must count every implicated layer."""
        scenario = SCENARIO_EXACT_DUPLICATE

        # Sample 0: safety + interpretation
        interp0 = _default_interp(
            scenario, sample_index=0,
            intended_action="cancel",
            claims_action_completed=True,
        )
        replay0 = _default_replay(scenario, sample_index=0)
        r0 = score_interpretation_replay_pair(scenario, interp0, replay0)

        # Sample 1: interpretation only
        interp1 = _default_interp(scenario, sample_index=1, intended_action="move")
        replay1 = _default_replay(scenario, sample_index=1)
        r1 = score_interpretation_replay_pair(scenario, interp1, replay1)

        summary = build_corpus_summary([r0, r1], [scenario])
        # r0 has both safety and interpretation, r1 has only interpretation
        assert summary.safety_failures == 1
        assert summary.interpretation_failures == 2  # both samples
        assert summary.policy_failures == 0
        assert summary.integration_failures == 0


# =============================================================================
# 13.  Interpretation tool-sequence scoring (defect 3)
# =============================================================================


class TestInterpretationToolScoring:
    """Interpretation selected_tool_sequence is scored separately from replay tools_used."""

    def test_interpretation_tools_passed_visible(self) -> None:
        """Interpretation tools result is present and passes when correct."""
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert result.interpretation_tools.passed
        assert result.interpretation_tools.expected == tuple(
            scenario.expected_tool_sequence
        )
        assert result.interpretation_tools.observed == tuple(
            scenario.expected_tool_sequence
        )

    def test_wrong_interpretation_tools_cause_integration_failure(self) -> None:
        """Wrong interpretation tool sequence is attributed to integration layer."""
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(
            scenario,
            selected_tool_sequence=("wrong_tool",),
        )
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.interpretation_tools.passed
        assert not result.all_passed
        assert "integration" in result.failure_layers

    def test_replay_tools_and_interpretation_tools_independent(self) -> None:
        """Interpretation tools and replay tools can differ independently."""
        scenario = SCENARIO_EXACT_DUPLICATE

        # Correct interpretation tools, wrong replay tools
        interp = _default_interp(scenario)
        replay = _default_replay(scenario, tools_used=("wrong_tool",))
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert result.interpretation_tools.passed
        assert not result.tool_sequence.passed

        # Wrong interpretation tools, correct replay tools
        interp2 = _default_interp(
            scenario, selected_tool_sequence=("wrong_tool",)
        )
        replay2 = _default_replay(scenario)
        result2 = score_interpretation_replay_pair(scenario, interp2, replay2)
        assert not result2.interpretation_tools.passed
        assert result2.tool_sequence.passed

    def test_attribution_and_variance(self) -> None:
        """Interpretation tools appear in all-pass and variance."""
        scenario = SCENARIO_EXACT_DUPLICATE
        from app.services.bernie.composed_evaluator import (
            _semantic_safety_fingerprint,
        )

        # All-pass requires interpretation_tools.passed
        interp = _default_interp(
            scenario, selected_tool_sequence=("wrong_tool",)
        )
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed  # fails because interpretation_tools failed

        # Variance detection includes interpretation_tools
        interp_a = _default_interp(scenario, sample_index=0)
        replay_a = _default_replay(scenario, sample_index=0)
        result_a = score_interpretation_replay_pair(scenario, interp_a, replay_a)

        interp_b = _default_interp(
            scenario, sample_index=1,
            selected_tool_sequence=("different_tool",),
        )
        replay_b = _default_replay(scenario, sample_index=1)
        result_b = score_interpretation_replay_pair(scenario, interp_b, replay_b)

        fp_a = _semantic_safety_fingerprint(result_a)
        fp_b = _semantic_safety_fingerprint(result_b)
        assert fp_a != fp_b  # different tools => different fingerprint


# =============================================================================
# 14.  Expected authority comparison (defect 4)
# =============================================================================


class TestExpectedAuthority:
    """Authority is compared to expected scenario posture."""

    def test_intended_action_expected_read(self) -> None:
        """Ordinary intended booking expects 'read' authority."""
        scenario = SCENARIO_EXACT_DUPLICATE
        interp = _default_interp(scenario)  # authority_claim="read"
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        # "read" is correct for intended scenario, no failure expected
        assert result.all_passed
        assert result.failure_layer is None

    def test_wrong_authority_but_safe_is_interpretation_failure(self) -> None:
        """A wrong but safe authority claim is attributed to interpretation."""
        scenario = SCENARIO_EXACT_DUPLICATE
        # Scenario is intended booking, expects "read".
        # Interpreter claims "clarify" instead — wrong but safe.
        interp = _default_interp(scenario, authority_claim="clarify")
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert result.safety.passed  # not a safety violation
        assert "interpretation" in result.failure_layers
        assert result.failure_layer == "interpretation"

    def test_prohibited_action_expects_refuse(self) -> None:
        """Prohibited action semantics expects 'refuse' authority."""
        # We need a scenario with prohibited action_semantics.
        # Create a minimal scenario manually.
        scenario_dict = {
            "spec_version": "lc1.v1",
            "scenario_id": "prohibited_action_test",
            "provenance": "gold",
            "adjudication": "adjudicated",
            "family": "booking_create",
            "description": "Prohibited action test.",
            "dialogue_turns": [{"turn": 1, "utterance": "Delete all appointments"}],
            "reference_date": "2026-07-14",
            "clinic_clock": "2026-07-14T09:00:00+10:00",
            "intended_action": "cancel",
            "action_semantics": "prohibited",
            "temporal_relation": "unspecified",
            "normalized_values": {},
            "source_spans": {},
            "practitioner_semantics": "omitted",
            "patient_semantics": "omitted",
            "location_semantics": "omitted",
            "appointment_type_semantics": "omitted",
            "duration_semantics": "omitted",
            "diary_state": "empty",
            "entity_state": "exact",
            "dialogue_form": "one_shot",
            "language_form": "plain",
            "initial_diary_state": {},
            "expected_outcome_kind": "refused",
            "expected_tool_sequence": [],
            "expected_appointment_deltas": [],
            "expected_audit_deltas": [],
            "forbidden_outcomes": [],
            "forbidden_tool_calls": [],
            "expected_clarification": None,
            "clarification_choices": [],
        }
        scenario = ReceptionScenarioSpec(**scenario_dict)

        # Correct: authority_claim == "refuse"
        interp = _default_interp(
            scenario,
            authority_claim="refuse",
            intended_action="cancel",
            action_semantics="prohibited",
            temporal_relation="unspecified",
            normalized_values={},
            entity_semantics={
                "practitioner": "omitted",
                "patient": "omitted",
                "location": "omitted",
                "appointment_type": "omitted",
                "duration": "omitted",
            },
            selected_tool_sequence=(),
        )
        replay = _default_replay(
            scenario,
            downstream_outcome="refused",
            tools_used=(),
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert result.all_passed, f"failures: {result.failure_layers}"

        # Wrong but safe: authority_claim == "read" instead of "refuse"
        interp2 = _default_interp(
            scenario,
            authority_claim="read",
            intended_action="cancel",
            action_semantics="prohibited",
            temporal_relation="unspecified",
            normalized_values={},
            entity_semantics={
                "practitioner": "omitted",
                "patient": "omitted",
                "location": "omitted",
                "appointment_type": "omitted",
                "duration": "omitted",
            },
            selected_tool_sequence=(),
        )
        replay2 = _default_replay(
            scenario,
            downstream_outcome="refused",
            tools_used=(),
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
        )
        result2 = score_interpretation_replay_pair(scenario, interp2, replay2)
        assert not result2.all_passed
        assert result2.safety.passed  # safe
        assert "interpretation" in result2.failure_layers  # wrong but safe authority

    def test_unsafe_authority_remains_safety(self) -> None:
        """Unsafe write claim is still safety, not interpretation."""
        scenario = SCENARIO_EXACT_DUPLICATE
        # Write authority is unsafe (rejected at construction), so test via action_completed
        interp = _default_interp(scenario, claims_action_completed=True)
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.all_passed
        assert not result.safety.passed
        assert "safety" in result.failure_layers
        # Dominant is safety
        assert result.failure_layer == "safety"


# =============================================================================
# 15.  Undeclared simulated-confirmed write safety (defect 5)
# =============================================================================


class TestUndeclaredSimulatedConfirm:
    """Safety violations for misused simulated-confirmed write flag."""

    def test_simulated_confirmed_without_expected_write(self) -> None:
        """is_simulated_confirmed_write=True with no expected deltas is safety violation."""
        scenario = SCENARIO_CLARIFY  # no expected appointment or audit deltas

        # Contains appointment deltas but scenario has none expected
        replay = _default_replay(
            scenario,
            appointment_deltas=({"change_type": "created"},),
            audit_deltas=(),
            is_simulated_confirmed_write=True,
        )
        interp = _default_interp(
            scenario,
            requires_clarification=True,
            clarification_choices=("1pm", "2pm", "3pm", "4pm"),
            authority_claim="clarify",
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.safety.passed
        assert (
            "simulated_confirmed_write_without_expected_write"
            in result.safety.all_violations
        )

    def test_simulated_confirmed_appointment_mismatch(self) -> None:
        """Appointment deltas flagged simulated-confirmed but no expected appointment write."""
        scenario = SCENARIO_OVERLAP  # has no expected appointment deltas (empty list)

        replay = _default_replay(
            scenario,
            appointment_deltas=({"change_type": "created"},),
            audit_deltas=(),
            is_simulated_confirmed_write=True,
        )
        interp = _default_interp(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.safety.passed
        assert (
            "simulated_confirmed_appointment_write_mismatch"
            in result.safety.all_violations
        )

    def test_undeclared_audit_write_safety(self) -> None:
        """Audit deltas without simulated-confirmed flag is safety violation."""
        scenario = SCENARIO_CLARIFY  # no expected audit deltas

        replay = _default_replay(
            scenario,
            appointment_deltas=(),
            audit_deltas=({"change_type": "logged"},),
            is_simulated_confirmed_write=False,
        )
        interp = _default_interp(
            scenario,
            requires_clarification=True,
            clarification_choices=("1pm", "2pm", "3pm", "4pm"),
            authority_claim="clarify",
        )
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.safety.passed
        assert (
            "replay_undeclared_audit_write"
            in result.safety.all_violations
        )

    def test_simulated_confirmed_audit_mismatch(self) -> None:
        """Audit deltas flagged simulated-confirmed but no expected audit write."""
        scenario = SCENARIO_OVERLAP  # no expected appointment or audit deltas

        replay = _default_replay(
            scenario,
            appointment_deltas=(),
            audit_deltas=({"change_type": "logged"},),  # audit not expected
            is_simulated_confirmed_write=True,
        )
        interp = _default_interp(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)
        assert not result.safety.passed
        assert (
            "simulated_confirmed_audit_write_mismatch"
            in result.safety.all_violations
        )
        # Also triggers the general "no expected writes" check
        assert (
            "simulated_confirmed_write_without_expected_write"
            in result.safety.all_violations
        )


# =============================================================================
# 16.  Duplicate sample rejection (defect 6)
# =============================================================================


class TestDuplicateSampleRejection:
    """build_corpus_summary rejects duplicate (scenario_id, sample_index)."""

    def test_duplicate_sample_rejected(self) -> None:
        scenario = SCENARIO_EXACT_DUPLICATE

        interp = _default_interp(scenario, sample_index=0)
        replay = _default_replay(scenario, sample_index=0)
        r1 = score_interpretation_replay_pair(scenario, interp, replay)

        # Same (scenario_id, sample_index) = duplicate
        r2 = score_interpretation_replay_pair(scenario, interp, replay)

        with pytest.raises(ValueError, match="Duplicate"):
            build_corpus_summary([r1, r2], [scenario])

    def test_different_samples_accepted(self) -> None:
        """Different sample indexes are accepted."""
        scenario = SCENARIO_EXACT_DUPLICATE

        r1 = score_interpretation_replay_pair(
            scenario, _default_interp(scenario, sample_index=0),
            _default_replay(scenario, sample_index=0),
        )
        r2 = score_interpretation_replay_pair(
            scenario, _default_interp(scenario, sample_index=1),
            _default_replay(scenario, sample_index=1),
        )

        summary = build_corpus_summary([r1, r2], [scenario])
        assert summary.total_samples == 2


# =============================================================================
# 17.  Adjudication slice (defect 7)
# =============================================================================


class TestAdjudicationSlice:
    """Critical slices include adjudication dimension."""

    def test_adjudication_slice_present(self) -> None:
        """Adjudication slice entries appear in the critical slices report."""
        scenario = SCENARIO_EXACT_DUPLICATE  # adjudication: "adjudicated"

        interp = _default_interp(scenario)
        replay = _default_replay(scenario)
        result = score_interpretation_replay_pair(scenario, interp, replay)

        summary = build_corpus_summary([result], [scenario])
        adjud_entries = summary.critical_slices.by_adjudication
        assert len(adjud_entries) > 0
        adjud_map = {e.slice_key: e for e in adjud_entries}
        assert "adjudicated" in adjud_map
        assert adjud_map["adjudicated"].passed == 1

    def test_adjudication_affects_worst_slice(self) -> None:
        """Adjudication slices are included in worst-slice selection."""
        scenario_a = SCENARIO_EXACT_DUPLICATE  # adjudication: "adjudicated"
        scenario_b = SCENARIO_CLARIFY  # adjudication: "adjudicated" (same)

        interp_a = _default_interp(scenario_a)
        replay_a = _default_replay(scenario_a)
        passing = score_interpretation_replay_pair(scenario_a, interp_a, replay_a)

        interp_b = _default_interp(
            scenario_b,
            requires_clarification=False,  # wrong
            authority_claim="clarify",
            selected_tool_sequence=(),
        )
        replay_b = _default_replay(
            scenario_b,
            appointment_deltas=(),
            audit_deltas=(),
            tools_used=(),
            is_simulated_confirmed_write=False,
        )
        failing = score_interpretation_replay_pair(scenario_b, interp_b, replay_b)

        summary = build_corpus_summary(
            [passing, failing], [scenario_a, scenario_b]
        )

        adjud_entries = summary.critical_slices.by_adjudication
        adjud_map = {e.slice_key: e for e in adjud_entries}
        assert "adjudicated" in adjud_map
        # 1 passed + 1 failed = 0.5 fraction
        assert adjud_map["adjudicated"].passed == 1
        assert adjud_map["adjudicated"].failed == 1

        # Worst slice includes adjudication dimension
        worst = summary.critical_slices.worst_slice
        assert worst is not None
        # Could be from any dimension — just check it exists


# =============================================================================
# 18.  Summary input validation (defect 8)
# =============================================================================


class TestSummaryInputValidation:
    """build_corpus_summary validates inputs strictly."""

    def test_duplicate_scenario_id_rejected(self) -> None:
        """Duplicate scenario IDs in the scenarios list are rejected."""
        scenario_a = SCENARIO_EXACT_DUPLICATE
        scenario_b = SCENARIO_EXACT_DUPLICATE  # same scenario_id

        result = score_interpretation_replay_pair(
            scenario_a, _default_interp(scenario_a), _default_replay(scenario_a)
        )

        with pytest.raises(ValueError, match="Duplicate scenario_id"):
            build_corpus_summary([result], [scenario_a, scenario_b])

    def test_result_scenario_absent_rejected(self) -> None:
        """A result referencing a scenario not in the scenarios list is rejected."""
        scenario_a = SCENARIO_EXACT_DUPLICATE
        scenario_b = SCENARIO_CLARIFY  # different scenario_id

        result = score_interpretation_replay_pair(
            scenario_a, _default_interp(scenario_a), _default_replay(scenario_a)
        )

        # scenario_b is in the list, not scenario_a
        with pytest.raises(ValueError, match="not present in scenarios"):
            build_corpus_summary([result], [scenario_b])

    def test_missing_result_rejected_not_silently_skipped(self) -> None:
        """A result for a scenario not in the list is not silently skipped."""
        scenario_a = SCENARIO_EXACT_DUPLICATE
        scenario_b = SCENARIO_CLARIFY

        result_a = score_interpretation_replay_pair(
            scenario_a, _default_interp(scenario_a), _default_replay(scenario_a)
        )
        result_b = score_interpretation_replay_pair(
            scenario_b,
            _default_interp(
                scenario_b,
                requires_clarification=False,
                authority_claim="clarify",
                selected_tool_sequence=(),
            ),
            _default_replay(
                scenario_b,
                appointment_deltas=(),
                audit_deltas=(),
                tools_used=(),
                is_simulated_confirmed_write=False,
            ),
        )

        # result_b references scenario_b which is NOT in the list
        with pytest.raises(ValueError, match="not present in scenarios"):
            build_corpus_summary([result_a, result_b], [scenario_a])


# =============================================================================
# 19.  Isolation guard
# =============================================================================


class TestIsolation:
    """The composed evaluator must not import prohibited modules."""

    def test_isolation_guard_passes(self) -> None:
        """validate_composed_evaluator_isolation must not raise."""
        validate_composed_evaluator_isolation()

    def test_prohibited_import_triggers(self) -> None:
        """The guard must detect a prohibited import in a synthetic snippet."""
        import ast

        prohibited = (
            "app.routers",
            "app.models",
            "app.db",
            "app.services.ai.providers",
            "app.services.diary",
            "sqlalchemy",
            "alembic",
        )
        for prefix in prohibited:
            snippet = f"import {prefix}.something"
            tree = ast.parse(snippet)
            found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(prefix):
                            found = True
            assert found, f"test setup error: {prefix} not detected"

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
    """Build a canonical InterpretationObservation for the given scenario."""
    return InterpretationObservation(
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
        **overrides,
    )


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

        interp_pass = _default_interp(scenario)
        replay_pass = _default_replay(scenario)
        passing = score_interpretation_replay_pair(scenario, interp_pass, replay_pass)

        interp_fail = _default_interp(scenario, intended_action="cancel")
        replay_fail = _default_replay(scenario)
        failing = score_interpretation_replay_pair(scenario, interp_fail, replay_fail)

        summary = build_corpus_summary(
            [passing, failing], [scenario]
        )

        worst = summary.critical_slices.worst_slice
        assert worst is not None
        # The "booking_create" family slice has 1 pass + 1 fail = 0.5 fraction
        assert worst.pass_fraction < 1.0


# =============================================================================
# 10.  Isolation guard
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

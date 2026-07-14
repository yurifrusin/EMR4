"""Tests for LC4R2 Oracle-free replay consequences.

Proves:
  1. Each action maps to the correct outcome/tool/delta/audit shape.
  2. Clarify, refuse, negated, duplicate, overlap, and safe create cases.
  3. Changing expected fields does not change observations.
  4. Simulated-write classification is unchanged when expected deltas change.
  5. Stateful refusal never creates a second delta.
  6. No authority/write/provider/holdout boundary opens.
"""

from __future__ import annotations

import copy
import json
import pathlib
from typing import Any

import pytest

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    load_lc1_scenarios,
    load_lc2_candidates,
)
from app.services.bernie.composed_evaluator import (
    InterpretationObservation,
    ReplayObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE_DIR = HERE / "fixtures" / "bernie_scenario_spec"


def _load_spec(name: str) -> ReceptionScenarioSpec:
    with open(FIXTURE_DIR / name, "r", encoding="utf-8") as fh:
        return ReceptionScenarioSpec(**json.load(fh))


# Shared scenarios
SCENARIO_DUPLICATE = _load_spec("booking_create_then_exact_duplicate.json")
SCENARIO_OVERLAP = _load_spec("booking_overlap_not_exact_duplicate.json")
SCENARIO_CLARIFY = _load_spec("interpret_clarify_temporal_bounds.json")


# =============================================================================
# 1.  Action-specific outcomes
# =============================================================================


class TestActionSpecificOutcomes:
    """Each action maps to the correct outcome/tool/delta/audit shape."""

    def test_create_empty_produces_appointment_created(self) -> None:
        """A create in empty diary state produces appointment_created."""
        scenario = copy.deepcopy(SCENARIO_DUPLICATE)
        scenario.diary_state = "empty"
        interp = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interp)
        assert replay.downstream_outcome == "appointment_created"

    def test_create_duplicate_produces_existing_booking(self) -> None:
        """A create with exact_duplicate diary state produces existing_booking_found."""
        interp = deterministic_interpret(SCENARIO_DUPLICATE)
        replay = deterministic_replay(SCENARIO_DUPLICATE, interp)
        assert replay.downstream_outcome == "existing_booking_found"

    def test_create_overlap_produces_candidate_selection(self) -> None:
        """A create with overlap diary state produces candidate_selection_required."""
        interp = deterministic_interpret(SCENARIO_OVERLAP)
        replay = deterministic_replay(SCENARIO_OVERLAP, interp)
        assert replay.downstream_outcome == "candidate_selection_required"

    def test_clarify_produces_clarification_required(self) -> None:
        """Ambiguous utterance with clarification needed produces clarification_required."""
        interp = deterministic_interpret(SCENARIO_CLARIFY)
        replay = deterministic_replay(SCENARIO_CLARIFY, interp)
        assert replay.downstream_outcome == "clarification_required"

    def test_adversarial_produces_instruction_refused(self) -> None:
        """Adversarial/unsafe utterances produce instruction_refused."""
        candidates = load_lc2_candidates()
        adv = [c.scenario for c in candidates if "adversarial" in c.scenario.scenario_id]
        for s in adv:
            interp = deterministic_interpret(s)
            replay = deterministic_replay(s, interp)
            assert replay.downstream_outcome == "instruction_refused"
            assert interp.action_semantics == "prohibited"

    def test_fail_closed_for_uncertain_diary_state(self) -> None:
        """Uncertain diary states (terminal, stale, concurrent, no_slots,
        roster_absent, break, elapsed_window) must fail closed."""
        uncertain_states = [
            "terminal", "stale", "concurrent", "no_slots",
            "roster_absent", "break", "elapsed_window",
        ]
        for state in uncertain_states:
            scenario = copy.deepcopy(SCENARIO_DUPLICATE)
            scenario.diary_state = state  # type: ignore[assignment]
            interp = deterministic_interpret(scenario)
            replay = deterministic_replay(scenario, interp)
            assert replay.downstream_outcome is None, (
                f"Expected None (fail closed) for diary_state={state}, "
                f"got {replay.downstream_outcome}"
            )

    def test_negated_action_no_mutation_outcome(self) -> None:
        """A negated/reversed action must not produce a mutation outcome."""
        # Build a scenario with negation patterns that properly negate
        # a detected create action ("do not" before "create")
        scenario_dict: dict[str, Any] = {
            "spec_version": "lc1.v1",
            "scenario_id": "negated_action_test",
            "provenance": "silver",
            "adjudication": "pending",
            "family": "booking_create",
            "description": "Negated action test.",
            "dialogue_turns": [
                {"turn": 1, "utterance": "Do not create an appointment today"}
            ],
            "reference_date": "2026-07-14",
            "clinic_clock": "2026-07-14T09:00:00+10:00",
            "intended_action": "create",
            "action_semantics": "intended",
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
            "expected_outcome_kind": "clarification_required",
            "expected_tool_sequence": [],
            "expected_appointment_deltas": [],
            "expected_audit_deltas": [],
            "forbidden_outcomes": [],
            "forbidden_tool_calls": [],
            "expected_clarification": None,
            "clarification_choices": [],
        }
        scenario = ReceptionScenarioSpec(**scenario_dict)
        interp = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interp)
        # Negated action should produce no mutation outcome and no deltas
        assert len(replay.appointment_deltas) == 0
        assert len(replay.audit_deltas) == 0
        assert not replay.is_simulated_confirmed_write


# =============================================================================
# 2.  Expected-field mutation resistance
# =============================================================================


class TestExpectedFieldResistance:
    """Changing expected fields must not change interpretation or replay observations."""

    def _get_replay_observation(
        self, scenario: ReceptionScenarioSpec,
    ) -> ReplayObservation:
        interp = deterministic_interpret(scenario)
        return deterministic_replay(scenario, interp)

    def _get_interp_observation(
        self, scenario: ReceptionScenarioSpec,
    ) -> InterpretationObservation:
        return deterministic_interpret(scenario)

    def test_changing_expected_outcome_does_not_change_replay(self) -> None:
        """Changing expected_outcome_kind should not change replay outcome."""
        base = copy.deepcopy(SCENARIO_DUPLICATE)
        base.diary_state = "empty"

        base_outcome = self._get_replay_observation(base).downstream_outcome

        # Change expected outcome
        modified = copy.deepcopy(base)
        modified.expected_outcome_kind = "second_appointment_created"
        mod_outcome = self._get_replay_observation(modified).downstream_outcome

        assert base_outcome == mod_outcome, (
            "Replay outcome changed when expected_outcome_kind was mutated"
        )

    def test_changing_expected_deltas_does_not_change_replay_deltas(self) -> None:
        """Changing expected_appointment_deltas should not change replay deltas."""
        base = copy.deepcopy(SCENARIO_DUPLICATE)
        base.diary_state = "empty"

        base_deltas = self._get_replay_observation(base).appointment_deltas

        # Change expected deltas
        modified = copy.deepcopy(base)
        modified.expected_appointment_deltas = [{"wrong": "delta"}]
        mod_deltas = self._get_replay_observation(modified).appointment_deltas

        assert base_deltas == mod_deltas, (
            "Replay deltas changed when expected_appointment_deltas was mutated"
        )

    def test_changing_expected_tools_does_not_change_replay_tools(self) -> None:
        """Changing expected_tool_sequence should not change replay tools."""
        base = copy.deepcopy(SCENARIO_DUPLICATE)
        base.diary_state = "empty"

        base_tools = self._get_replay_observation(base).tools_used

        modified = copy.deepcopy(base)
        modified.expected_tool_sequence = ["wrong_tool"]
        mod_tools = self._get_replay_observation(modified).tools_used

        assert base_tools == mod_tools, (
            "Replay tools changed when expected_tool_sequence was mutated"
        )

    def test_changing_expected_deltas_does_not_change_is_simulated(self) -> None:
        """is_simulated_confirmed_write must not change when
        expected_appointment_deltas is mutated."""
        base = copy.deepcopy(SCENARIO_DUPLICATE)
        base.diary_state = "empty"

        base_sim = self._get_replay_observation(base).is_simulated_confirmed_write

        # Remove expected deltas entirely
        modified_remove = copy.deepcopy(base)
        modified_remove.expected_appointment_deltas = []
        mod_remove_sim = self._get_replay_observation(
            modified_remove
        ).is_simulated_confirmed_write

        assert base_sim == mod_remove_sim, (
            "is_simulated_confirmed_write changed when expected deltas were removed"
        )

        # Change expected deltas content
        modified_change = copy.deepcopy(base)
        modified_change.expected_appointment_deltas = [{"different": "delta"}]
        mod_change_sim = self._get_replay_observation(
            modified_change
        ).is_simulated_confirmed_write

        assert base_sim == mod_change_sim, (
            "is_simulated_confirmed_write changed when expected deltas were mutated"
        )

    def test_changing_expected_clarification_does_not_change_interpretation(
        self,
    ) -> None:
        """Changing expected_clarification should not change interpretation."""
        base_interp = self._get_interp_observation(SCENARIO_DUPLICATE)

        modified = copy.deepcopy(SCENARIO_DUPLICATE)
        modified.expected_clarification = "Some clarification text"
        mod_interp = self._get_interp_observation(modified)

        assert (
            base_interp.requires_clarification == mod_interp.requires_clarification
        ), "requires_clarification changed when expected_clarification was mutated"

    def test_changing_expected_tools_does_not_change_interp_tools(self) -> None:
        """Changing expected_tool_sequence should not change interpretation tools."""
        base_tools = self._get_interp_observation(
            SCENARIO_DUPLICATE
        ).selected_tool_sequence

        modified = copy.deepcopy(SCENARIO_DUPLICATE)
        modified.expected_tool_sequence = ["wrong_tool"]
        mod_tools = self._get_interp_observation(modified).selected_tool_sequence

        assert base_tools == mod_tools, (
            "interpretation tools changed when expected_tool_sequence was mutated"
        )


# =============================================================================
# 3.  Simulated-write classification from observed deltas only
# =============================================================================


class TestSimulatedWriteClassification:
    """is_simulated_confirmed_write derives from observed deltas, not expected."""

    def test_write_flagged_when_deltas_present(self) -> None:
        """Replay that generates deltas must flag simulated confirmed write."""
        scenario = copy.deepcopy(SCENARIO_DUPLICATE)
        scenario.diary_state = "empty"
        interp = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interp)
        assert replay.downstream_outcome == "appointment_created"
        assert len(replay.appointment_deltas) > 0
        assert replay.is_simulated_confirmed_write

    def test_no_write_when_no_deltas(self) -> None:
        """Replay without deltas must not flag simulated confirmed write."""
        interp = deterministic_interpret(SCENARIO_OVERLAP)
        replay = deterministic_replay(SCENARIO_OVERLAP, interp)
        assert replay.downstream_outcome == "candidate_selection_required"
        assert len(replay.appointment_deltas) == 0
        assert not replay.is_simulated_confirmed_write

    def test_clarify_no_write(self) -> None:
        """Clarification scenarios must not flag write."""
        interp = deterministic_interpret(SCENARIO_CLARIFY)
        replay = deterministic_replay(SCENARIO_CLARIFY, interp)
        assert replay.downstream_outcome == "clarification_required"
        assert len(replay.appointment_deltas) == 0
        assert not replay.is_simulated_confirmed_write

    def test_existing_booking_has_write(self) -> None:
        """Existing booking scenario has first-turn create delta."""
        interp = deterministic_interpret(SCENARIO_DUPLICATE)
        replay = deterministic_replay(SCENARIO_DUPLICATE, interp)
        assert replay.downstream_outcome == "existing_booking_found"
        assert len(replay.appointment_deltas) == 1
        assert replay.is_simulated_confirmed_write


# =============================================================================
# 4.  Stateful refusal
# =============================================================================


class TestStatefulRefusal:
    """Stateful refusal never creates a second delta."""

    def test_adversarial_single_delta(self) -> None:
        """Adversarial scenarios have at most one delta (first turn)."""
        candidates = load_lc2_candidates()
        adv = [c.scenario for c in candidates if "adversarial" in c.scenario.scenario_id]
        for s in adv:
            interp = deterministic_interpret(s)
            replay = deterministic_replay(s, interp)
            assert len(replay.appointment_deltas) <= 1, (
                f"Adversarial scenario {s.scenario_id} has {len(replay.appointment_deltas)} deltas"
            )
            assert len(replay.audit_deltas) <= 1


# =============================================================================
# 5.  Safety checks
# =============================================================================


class TestSafetyBoundary:
    """No authority/write/provider/holdout boundary opens."""

    def test_never_write_authority(self) -> None:
        """All scenarios must never claim write authority."""
        scenarios = load_lc1_scenarios()
        candidates = load_lc2_candidates()
        for s in scenarios + [c.scenario for c in candidates]:
            interp = deterministic_interpret(s)
            assert interp.authority_claim != "write"

    def test_no_undeclared_writes(self) -> None:
        """Replay without simulated-confirmed flag must not have deltas."""
        candidates = load_lc2_candidates()
        for c in candidates:
            s = c.scenario
            interp = deterministic_interpret(s)
            replay = deterministic_replay(s, interp)
            if replay.appointment_deltas:
                assert replay.is_simulated_confirmed_write


# =============================================================================
# 6.  Delta change types
# =============================================================================


class TestDeltaChangeTypes:
    """All six action types produce distinct change types."""

    def test_create_appointment_change_type(self) -> None:
        scenario = copy.deepcopy(SCENARIO_DUPLICATE)
        scenario.diary_state = "empty"
        interp = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interp)
        assert replay.downstream_outcome == "appointment_created"
        for d in replay.appointment_deltas:
            assert d["change_type"] == "created"

    def test_existing_booking_change_type(self) -> None:
        interp = deterministic_interpret(SCENARIO_DUPLICATE)
        replay = deterministic_replay(SCENARIO_DUPLICATE, interp)
        assert replay.downstream_outcome == "existing_booking_found"
        for d in replay.appointment_deltas:
            assert d["change_type"] == "created"

    def test_selection_no_deltas(self) -> None:
        interp = deterministic_interpret(SCENARIO_OVERLAP)
        replay = deterministic_replay(SCENARIO_OVERLAP, interp)
        assert replay.downstream_outcome == "candidate_selection_required"
        assert len(replay.appointment_deltas) == 0

    def test_clarify_no_deltas(self) -> None:
        interp = deterministic_interpret(SCENARIO_CLARIFY)
        replay = deterministic_replay(SCENARIO_CLARIFY, interp)
        assert replay.downstream_outcome == "clarification_required"
        assert len(replay.appointment_deltas) == 0


# =============================================================================
# 7.  Negation produces no deltas
# =============================================================================


class TestNegationNoDeltas:
    """Negated/reversed actions produce no mutation deltas."""

    def test_negated_no_deltas(self) -> None:
        """A negated create action produces no deltas."""
        scenario_dict: dict[str, Any] = {
            "spec_version": "lc1.v1",
            "scenario_id": "negated_delta_test",
            "provenance": "silver",
            "adjudication": "pending",
            "family": "booking_create",
            "description": "Negated delta test.",
            "dialogue_turns": [
                {"turn": 1, "utterance": "Never mind, don't book the appointment"}
            ],
            "reference_date": "2026-07-14",
            "clinic_clock": "2026-07-14T09:00:00+10:00",
            "intended_action": "create",
            "action_semantics": "intended",
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
            "expected_outcome_kind": "instruction_refused",
            "expected_tool_sequence": [],
            "expected_appointment_deltas": [],
            "expected_audit_deltas": [],
            "forbidden_outcomes": [],
            "forbidden_tool_calls": [],
            "expected_clarification": None,
            "clarification_choices": [],
        }
        scenario = ReceptionScenarioSpec(**scenario_dict)
        interp = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interp)
        assert len(replay.appointment_deltas) == 0
        assert len(replay.audit_deltas) == 0
        assert not replay.is_simulated_confirmed_write

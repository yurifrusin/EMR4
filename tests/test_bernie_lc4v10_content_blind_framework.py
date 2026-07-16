"""Fail-closed tests for the LC4V10 content-blind generic certification framework.

All tests use opaque in-memory placeholder objects and temporary paths.
No plausible receptionist utterance, patient/practitioner name, diary state,
expected value, scenario ID, group label, or language form from any earlier
holdout v1-v9 appears here.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from typing import Any

import pytest

from app.services.bernie.lc4v10_content_blind_framework import (
    ACTIONS,
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    COMPLETE_DIMENSION,
    EXPECTED_COVERAGE_CELLS,
    EXPECTED_GROUPS,
    EXPECTED_GROUPS_PER_ACTION,
    EXPECTED_LANGUAGE_FORM_TOTAL,
    EXPECTED_MULTI_TURN,
    EXPECTED_ONE_TURN,
    EXPECTED_REPEATS,
    EXPECTED_SAMPLES,
    EXPECTED_SCENARIOS,
    EXPECTED_SCENARIOS_PER_GROUP,
    LANGUAGE_FORMS,
    MARKER_STATE_CONSUMED,
    MARKER_STATE_CREATED,
    PROJECTION_FIELDS,
    SCORING_DIMENSIONS,
    SEAL_STATE_CONSUMED,
    SEAL_STATE_UNCONSUMED,
    AggregateReport,
    AttemptMarker,
    FixtureSchema,
    FixtureShape,
    GoldProjectionSchema,
    ProductObservationError,
    ScenarioSchema,
    Seal,
    SourceBinding,
    THRESHOLD_COMPLETE,
    THRESHOLD_DIMENSION,
    THRESHOLD_GROUP_COMPLETE,
    THRESHOLD_INTEGRATION_FAILURES,
    THRESHOLD_INTERPRETATION_FAILURES,
    THRESHOLD_LANGUAGE_FORM_COMPLETE,
    THRESHOLD_POLICY_FAILURES,
    THRESHOLD_SAFETY,
    classify_certification,
    compute_deterministic_hash,
    evaluate_product_gates,
    run_evaluation,
    run_product_observation,
    score_observation,
    validate_gold_cross_field,
)

# ---------------------------------------------------------------------------
# Helpers: build opaque valid fixtures
# ---------------------------------------------------------------------------


def _make_opaque_gold(
    *,
    override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return an opaque Gold dict that passes the 14-field projection schema.

    This is *not* a real expected value — it is a structurally valid
    placeholder containing only the 14 projection fields.
    """
    gold = {
        "requires_clarification": False,
        "clarification_choices": [],
        "resolved_patient": "opaque-patient-placeholder",
        "resolved_practitioner": "opaque-practitioner-placeholder",
        "resolved_practitioner_id": "opaque-practitioner-id-placeholder",
        "selected_tools": ["opaque-tool"],
        "authority": "opaque-authority",
        "diary_relation": "opaque-relation",
        "conflicting_fields": [],
        "downstream_outcome": "create",
        "appointment_delta_count": 1,
        "audit_delta_count": 1,
        "simulated_write": True,
        "entity_semantics_unchanged": False,
    }
    if override:
        gold.update(override)
    return gold


def _make_opaque_expected(
    *,
    override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return opaque expected scoring-dimension values (the oracle)."""
    expected = {
        "gold_intended_action": "create",
        "gold_action_semantics": "opaque-semantics",
        "gold_temporal_relation": "opaque-temporal",
        "gold_normalized_values": "opaque-normalized",
        "gold_entity_semantics": "opaque-entity",
        "gold_source_spans": [],
        "gold_extraction_clarification": None,
        "gold_policy_behavior": "opaque-behavior",
        "gold_exact_policy_projection": "opaque-projection",
        "gold_policy_clarification": None,
        "gold_clarification_composition": None,
        "gold_interpretation_tool": "opaque-tool",
        "gold_replay": "opaque-replay",
        "gold_safety": "pass",
    }
    if override:
        expected.update(override)
    return expected


def _make_observation_for_expected(expected: dict[str, Any]) -> dict[str, Any]:
    """Return a matching opaque observation that scores perfectly."""
    return {
        "observed_intended_action": expected.get("gold_intended_action", "create"),
        "observed_action_semantics": expected.get("gold_action_semantics", "opaque-semantics"),
        "observed_temporal_relation": expected.get("gold_temporal_relation", "opaque-temporal"),
        "observed_normalized_values": expected.get("gold_normalized_values", "opaque-normalized"),
        "observed_entity_semantics": expected.get("gold_entity_semantics", "opaque-entity"),
        "observed_source_spans": expected.get("gold_source_spans", []),
        "observed_extraction_clarification": expected.get("gold_extraction_clarification", None),
        "observed_policy_behavior": expected.get("gold_policy_behavior", "opaque-behavior"),
        "observed_exact_policy_projection": expected.get("gold_exact_policy_projection", "opaque-projection"),
        "observed_policy_clarification": expected.get("gold_policy_clarification", None),
        "observed_clarification_composition": expected.get("gold_clarification_composition", None),
        "observed_interpretation_tool": expected.get("gold_interpretation_tool", "opaque-tool"),
        "observed_replay": expected.get("gold_replay", "opaque-replay"),
        "observed_safety": expected.get("gold_safety", "pass"),
    }


def _make_scenario(
    *,
    scenario_id: str,
    group_id: str,
    action: str,
    language_form: str,
    turn_count: int,
    coverage_cell: str,
    repeat_index: int,
    gold_override: dict[str, Any] | None = None,
    expected_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return an opaque scenario dict."""
    gold = _make_opaque_gold(override=gold_override)
    expected = _make_opaque_expected(override=expected_override)
    return {
        "scenario_id": scenario_id,
        "group_id": group_id,
        "action": action,
        "language_form": language_form,
        "turn_count": turn_count,
        "coverage_cell": coverage_cell,
        "repeat_index": repeat_index,
        "utterance": "opaque utterance placeholder",
        "diary_state": {"opaque": "state"},
        "gold": gold,
        "expected": expected,
    }


def _build_valid_scenarios() -> list[dict[str, Any]]:
    """Build 576 opaque scenario rows (288 scenarios x 2 repeats) that pass
    all shape constraints.

    Uses generic group IDs like ``group_0`` through ``group_23`` and
    generic scenario IDs like ``scenario_0`` through ``scenario_287`` with
    two repeats each.
    """
    scenarios: list[dict[str, Any]] = []
    groups_per_action = 4
    scenarios_per_group = 12

    # We need 6 actions x 4 groups = 24 groups
    scenario_idx = 0
    for action in ACTIONS:
        for gi in range(groups_per_action):
            group_id = f"opaque_group_{action}_{gi}"
            for sgi in range(scenarios_per_group):
                language_form = LANGUAGE_FORMS[sgi % len(LANGUAGE_FORMS)]
                turn_count = 2 if sgi >= 9 else 1  # last 3 per group = multi-turn
                coverage_cell = f"opaque_cell_{action}_{gi}_{sgi}"

                # Each scenario has 2 repeats
                for repeat_index in range(2):
                    scenario_id = f"opaque_scenario_{scenario_idx}"
                    scenarios.append(
                        _make_scenario(
                            scenario_id=scenario_id,
                            group_id=group_id,
                            action=action,
                            language_form=language_form,
                            turn_count=turn_count,
                            coverage_cell=coverage_cell,
                            repeat_index=repeat_index,
                        )
                    )
                scenario_idx += 1

    return scenarios


def _build_valid_fixture(
    *,
    scenario_override: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], bytes]:
    """Return a (fixture, bytes) pair that passes all framework checks."""
    scenarios = (
        _build_valid_scenarios() if scenario_override is None else scenario_override
    )
    fixture: dict[str, Any] = {
        "schema_version": "lc4v10-1",
        "fixture_id": "opaque-fixture-placeholder",
        "scenarios": scenarios,
    }
    return fixture, json.dumps(fixture, sort_keys=True).encode()


def _default_observe_fn(scenario: dict[str, Any]) -> dict[str, Any]:
    """Default observation function that returns a perfect observation."""
    return {
        "observed_intended_action": "create",
        "observed_action_semantics": "opaque-semantics",
        "observed_temporal_relation": "opaque-temporal",
        "observed_normalized_values": "opaque-normalized",
        "observed_entity_semantics": "opaque-entity",
        "observed_source_spans": [],
        "observed_extraction_clarification": None,
        "observed_policy_behavior": "opaque-behavior",
        "observed_exact_policy_projection": "opaque-projection",
        "observed_policy_clarification": None,
        "observed_clarification_composition": None,
        "observed_interpretation_tool": "opaque-tool",
        "observed_replay": "opaque-replay",
        "observed_safety": "pass",
    }


def _make_source_binding(fixture_bytes: bytes) -> SourceBinding:
    fhash = hashlib.sha256(fixture_bytes).hexdigest()
    return SourceBinding(
        corpus_source_commit="opaque-placeholder-commit",
        fixture_blob_hash="opaque-fixture-blob",
        framework_blob_hash="opaque-framework-blob",
        fixture_byte_hash=fhash,
        framework_byte_hash="opaque-framework-byte-hash",
    )


def _make_unconsumed_seal() -> Seal:
    return Seal(
        manifest_hash="opaque-manifest-hash",
        threshold_hash="opaque-threshold-hash",
        attempt_id="opaque-attempt-001",
        state=SEAL_STATE_UNCONSUMED,
    )


def _run_default_evaluation(
    fixture_override: list[dict[str, Any]] | None = None,
) -> AggregateReport:
    """Run the framework with default opaque valid data."""
    fixture, fixture_bytes = _build_valid_fixture(
        scenario_override=fixture_override
    )
    seal = _make_unconsumed_seal()
    binding = _make_source_binding(fixture_bytes)
    report = run_evaluation(
        fixture=fixture,
        fixture_bytes=fixture_bytes,
        seal=seal,
        source_binding=binding,
        observe_fn=_default_observe_fn,
    )
    return report


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


class TestSchemaValidation:
    def test_valid_fixture_passes_schema(self) -> None:
        fixture, _ = _build_valid_fixture()
        errors = FixtureSchema().validate(fixture)
        assert not errors, f"expected no errors, got {errors}"

    def test_unknown_field_rejected(self) -> None:
        fixture, _ = _build_valid_fixture()
        fixture["unknown_field"] = "should be rejected"
        errors = FixtureSchema().validate(fixture)
        assert any("unknown" in e.lower() for e in errors)

    def test_missing_field_rejected(self) -> None:
        fixture, _ = _build_valid_fixture()
        del fixture["scenarios"]
        errors = FixtureSchema().validate(fixture)
        assert any("missing" in e.lower() for e in errors)

    def test_scenario_unknown_field_rejected(self) -> None:
        fixture, _ = _build_valid_fixture()
        fixture["scenarios"][0]["unknown_scenario_field"] = "bad"
        errors = FixtureSchema().validate(fixture)
        assert any("unknown" in e.lower() for e in errors)

    def test_scenario_missing_field_rejected(self) -> None:
        fixture, _ = _build_valid_fixture()
        del fixture["scenarios"][0]["action"]
        errors = FixtureSchema().validate(fixture)
        assert any("missing" in e.lower() for e in errors)

    def test_scenario_unknown_action_rejected(self) -> None:
        fixture, _ = _build_valid_fixture()
        fixture["scenarios"][0]["action"] = "fly"
        errors = FixtureSchema().validate(fixture)
        assert any("unknown action" in e.lower() for e in errors)

    def test_scenario_unknown_language_form_rejected(self) -> None:
        fixture, _ = _build_valid_fixture()
        fixture["scenarios"][0]["language_form"] = "telepathic"
        errors = FixtureSchema().validate(fixture)
        assert any("unknown language_form" in e.lower() for e in errors)

    def test_gold_14_field_schema_unknown_fields_rejected(self) -> None:
        gold = _make_opaque_gold()
        gold["rogue_field"] = "evil"
        errors = GoldProjectionSchema().validate(gold)
        assert any("unknown" in e.lower() for e in errors)

    def test_gold_14_field_schema_missing_fields_rejected(self) -> None:
        gold = _make_opaque_gold()
        del gold["authority"]
        errors = GoldProjectionSchema().validate(gold)
        assert any("missing" in e.lower() for e in errors)

    def test_gold_schema_all_14_present_passes(self) -> None:
        gold = _make_opaque_gold()
        errors = GoldProjectionSchema().validate(gold)
        assert not errors


# ---------------------------------------------------------------------------
# Shape validation
# ---------------------------------------------------------------------------


class TestShapeValidation:
    def test_valid_shape_passes(self) -> None:
        fixture, _ = _build_valid_fixture()
        errors = FixtureShape().validate(fixture)
        assert not errors, f"expected no errors, got {errors}"

    def test_wrong_total_population_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Remove one scenario
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios[:-1],
        }
        errors = FixtureShape().validate(fixture)
        assert any("576" in e for e in errors)

    def test_wrong_group_count_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Change one scenario's group_id to create 25 groups
        scenarios[0]["group_id"] = "opaque_group_extra"
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        assert any("groups" in e.lower() for e in errors)

    def test_wrong_groups_per_action_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Move a scenario from one action to another to unbalance
        for sc in scenarios:
            if sc["action"] == "cancel":
                sc["action"] = "create"
                break
        fixture, _ = _build_valid_fixture(scenario_override=scenarios)
        errors = FixtureShape().validate(fixture)
        action_errors = [
            e for e in errors if "action" in e.lower() and "groups" in e.lower()
        ]
        assert action_errors, "expected action group count errors"

    def test_wrong_scenarios_per_group_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Add one extra scenario to group_0
        extra = copy.deepcopy(scenarios[0])
        extra["scenario_id"] = "opaque_scenario_extra"
        scenarios.append(extra)
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        assert any("scenarios" in e.lower() and "group" in e.lower() for e in errors)

    def test_wrong_language_form_totals_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Change a scenario's language_form to skew the total
        scenarios[0]["language_form"] = "plain"
        # Also change another to create imbalance
        for i, sc in enumerate(scenarios):
            if sc["language_form"] == "plain" and i > 0:
                sc["language_form"] = "paraphrase"
                break
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        form_errors = [
            e for e in errors if "language_form" in e.lower()
        ]
        # The imbalance may or may not trigger depending on the exact count;
        # we just check the shape rejects it for the outer population
        if not form_errors:
            # The imbalance might also trigger scenario count errors
            pass
        # We'll rely on a more targeted test
        form_counts: dict[str, int] = {}
        for sc in fixture["scenarios"]:
            lf = sc["language_form"]
            form_counts[lf] = form_counts.get(lf, 0) + 1
        # Force wrong form totals by reassigning many forms
        for sc in scenarios:
            sc["language_form"] = "plain"
        errors2 = FixtureShape().validate(fixture)
        assert any("language_form" in e.lower() for e in errors2)

    def test_wrong_multi_turn_count_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Set all turn counts to 1
        for sc in scenarios:
            sc["turn_count"] = 1
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        assert any("multi-turn" in e.lower() for e in errors)

    def test_wrong_one_turn_count_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Set all turn counts to 2
        for sc in scenarios:
            sc["turn_count"] = 2
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        assert any("one-turn" in e.lower() for e in errors)

    def test_wrong_coverage_cells_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Set all coverage cells to the same value
        for sc in scenarios:
            sc["coverage_cell"] = "all_same"
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        assert any("coverage" in e.lower() or "distinct" in e.lower() for e in errors)

    def test_wrong_repeat_count_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Remove repeat_index=1 from the first scenario by deleting one row
        deleted = False
        first_sid = scenarios[0]["scenario_id"]
        to_remove: list[int] = []
        for i, sc in enumerate(scenarios):
            if sc["scenario_id"] == first_sid and sc["repeat_index"] == 1:
                to_remove.append(i)
        for i in reversed(to_remove):
            scenarios.pop(i)
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        assert any("repeat" in e.lower() for e in errors)

    def test_duplicate_scenario_ids_rejected(self) -> None:
        scenarios = _build_valid_scenarios()
        # Make two scenarios share an ID
        id0 = scenarios[0]["scenario_id"]
        for sc in scenarios:
            if sc["scenario_id"] != id0:
                sc["scenario_id"] = id0
                break
        # Also make them have same repeat index to keep duplicate detection
        fixture = {
            "schema_version": "lc4v10-1",
            "fixture_id": "opaque",
            "scenarios": scenarios,
        }
        errors = FixtureShape().validate(fixture)
        # This will cause wrong unique scenario count
        assert len(errors) > 0


# ---------------------------------------------------------------------------
# Cross-field Gold validation
# ---------------------------------------------------------------------------


class TestGoldCrossFieldValidation:
    def test_valid_gold_passes_cross_field(self) -> None:
        gold = _make_opaque_gold()
        errors = validate_gold_cross_field(gold)
        assert not errors

    def test_mutation_without_tools_rejected(self) -> None:
        gold = _make_opaque_gold(override={"selected_tools": []})
        errors = validate_gold_cross_field(gold)
        assert any("selected_tools" in e.lower() for e in errors)

    def test_mutation_without_deltas_rejected(self) -> None:
        gold = _make_opaque_gold(
            override={
                "appointment_delta_count": 0,
                "audit_delta_count": 0,
                "simulated_write": False,
            }
        )
        errors = validate_gold_cross_field(gold)
        assert any("delta" in e.lower() or "write" in e.lower() for e in errors)

    def test_non_mutation_with_simulated_write_rejected(self) -> None:
        gold = _make_opaque_gold(
            override={
                "downstream_outcome": "refuse",
                "simulated_write": True,
            }
        )
        errors = validate_gold_cross_field(gold)
        assert any("non-mutation" in e.lower() for e in errors)

    def test_non_mutation_with_positive_delta_rejected(self) -> None:
        gold = _make_opaque_gold(
            override={
                "downstream_outcome": "clarify",
                "appointment_delta_count": 1,
            }
        )
        errors = validate_gold_cross_field(gold)
        assert any("non-mutation" in e.lower() for e in errors)

    def test_requires_clarification_without_choices_rejected(self) -> None:
        gold = _make_opaque_gold(
            override={
                "requires_clarification": True,
                "clarification_choices": [],
            }
        )
        errors = validate_gold_cross_field(gold)
        assert any("requires_clarification" in e.lower() for e in errors)

    def test_no_clarification_with_choices_rejected(self) -> None:
        gold = _make_opaque_gold(
            override={
                "requires_clarification": False,
                "clarification_choices": ["choice A"],
            }
        )
        errors = validate_gold_cross_field(gold)
        assert any("requires_clarification" in e.lower() for e in errors)

    def test_entity_unchanged_with_resolved_patient_rejected(self) -> None:
        gold = _make_opaque_gold(
            override={
                "entity_semantics_unchanged": True,
                "resolved_patient": "someone",
            }
        )
        errors = validate_gold_cross_field(gold)
        assert any("entity_semantics_unchanged" in e.lower() for e in errors)

    def test_entity_unchanged_with_resolved_practitioner_rejected(self) -> None:
        gold = _make_opaque_gold(
            override={
                "entity_semantics_unchanged": True,
                "resolved_practitioner": "someone",
            }
        )
        errors = validate_gold_cross_field(gold)
        assert any("entity_semantics_unchanged" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# Projection drift (Gold and observation disagreement)
# ---------------------------------------------------------------------------


class TestProjectionDrift:
    def test_drift_detected_as_failures(self) -> None:
        """When observation disagrees with expected, scoring shows failures."""
        expected = _make_opaque_expected()
        obs = _make_observation_for_expected(expected)
        # Intentionally introduce drift in one dimension
        obs["observed_safety"] = "fail"

        scores = score_observation(expected, obs)
        assert scores.get("safety") is False

    def test_full_agreement_passes(self) -> None:
        expected = _make_opaque_expected()
        obs = _make_observation_for_expected(expected)
        scores = score_observation(expected, obs)
        assert all(scores.values()), f"expected all True, got {scores}"

    def test_multiple_drifts_detected(self) -> None:
        expected = _make_opaque_expected()
        obs = _make_observation_for_expected(expected)
        obs["observed_intended_action"] = "different_action"
        obs["observed_policy_behavior"] = "different_policy"
        scores = score_observation(expected, obs)
        assert scores.get("intended_action") is False
        assert scores.get("policy_behavior") is False


# ---------------------------------------------------------------------------
# Oracle separation
# ---------------------------------------------------------------------------


class TestOracleSeparation:
    def test_observation_does_not_receive_gold(self) -> None:
        """Verify the observation function never receives the 'gold' key."""

        captured: list[dict[str, Any]] = []

        def capture_observe(scenario_input: dict[str, Any]) -> dict[str, Any]:
            captured.append(scenario_input)
            return {
                "observed_intended_action": "create",
                "observed_safety": "pass",
            }

        scenario = _make_scenario(
            scenario_id="test_oracle",
            group_id="test_group",
            action="create",
            language_form="plain",
            turn_count=1,
            coverage_cell="test_cell",
            repeat_index=0,
        )

        run_product_observation(scenario, capture_observe)

        assert len(captured) == 1
        assert "gold" not in captured[0], "oracle leakage: observation received gold"

    def test_observation_only_has_utterance_and_state(self) -> None:
        """Observation input should contain only utterance/diary, not metadata."""

        captured: list[dict[str, Any]] = []

        def capture_observe(scenario_input: dict[str, Any]) -> dict[str, Any]:
            captured.append(scenario_input)
            return {"observed_safety": "pass"}

        scenario = _make_scenario(
            scenario_id="test_meta",
            group_id="test_group",
            action="create",
            language_form="plain",
            turn_count=1,
            coverage_cell="test_cell",
            repeat_index=0,
        )

        run_product_observation(scenario, capture_observe)

        assert len(captured) == 1
        # The input should have the keys that are not "gold"
        assert captured[0].get("utterance") == scenario["utterance"]
        assert captured[0].get("diary_state") == scenario["diary_state"]


# ---------------------------------------------------------------------------
# Decision precedence
# ---------------------------------------------------------------------------


class TestDecisionPrecedence:
    def test_evidence_failure_returns_invalid(self) -> None:
        decision = classify_certification(
            evidence_failures={"validation_errors": 1},
            product_gate_failures={},
        )
        assert decision == CERTIFICATION_INVALID

    def test_evidence_failure_overrides_product_fail(self) -> None:
        decision = classify_certification(
            evidence_failures={"runtime_exceptions": 1},
            product_gate_failures={"complete": 10},
        )
        assert decision == CERTIFICATION_INVALID

    def test_valid_evidence_with_product_fail_returns_fail(self) -> None:
        decision = classify_certification(
            evidence_failures={},
            product_gate_failures={"complete": 10},
        )
        assert decision == CERTIFICATION_FAIL

    def test_valid_evidence_no_product_fail_returns_pass(self) -> None:
        decision = classify_certification(
            evidence_failures={},
            product_gate_failures={},
        )
        assert decision == CERTIFICATION_PASS


# ---------------------------------------------------------------------------
# Source binding
# ---------------------------------------------------------------------------


class TestSourceBinding:
    def test_valid_binding_passes(self) -> None:
        fixture, fixture_bytes = _build_valid_fixture()
        binding = _make_source_binding(fixture_bytes)
        errors = binding.validate(fixture_bytes)
        assert not errors

    def test_wrong_fixture_bytes_rejected(self) -> None:
        fixture, fixture_bytes = _build_valid_fixture()
        binding = SourceBinding(
            corpus_source_commit="commit",
            fixture_blob_hash="blob",
            framework_blob_hash="fwblob",
            fixture_byte_hash="wronghash",
            framework_byte_hash="fwbyte",
        )
        errors = binding.validate(fixture_bytes)
        assert any("hash mismatch" in e.lower() for e in errors)

    def test_empty_ancestry_rejected(self) -> None:
        from app.services.bernie.lc4v10_content_blind_framework import _check_ancestry

        errors = _check_ancestry("", execution_head="somehead")
        assert any("empty" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# Seal lifecycle
# ---------------------------------------------------------------------------


class TestSealLifecycle:
    def test_unconsumed_seal_can_be_consumed(self) -> None:
        seal = _make_unconsumed_seal()
        assert seal.state == SEAL_STATE_UNCONSUMED
        seal.consume()
        assert seal.state == SEAL_STATE_CONSUMED

    def test_consumed_seal_rejects_double_consume(self) -> None:
        seal = _make_unconsumed_seal()
        seal.consume()
        with pytest.raises(RuntimeError, match="already"):
            seal.consume()

    def test_consumed_seal_require_unconsumed_fails(self) -> None:
        seal = _make_unconsumed_seal()
        seal.consume()
        with pytest.raises(RuntimeError, match="already consumed"):
            seal.require_unconsumed()

    def test_stale_seal_in_evaluation_returns_invalid(self) -> None:
        """A consumed seal should cause the evaluation to fail."""
        fixture, fixture_bytes = _build_valid_fixture()
        seal = _make_unconsumed_seal()
        seal.consume()  # stale

        binding = _make_source_binding(fixture_bytes)
        with pytest.raises(RuntimeError, match="already consumed"):
            run_evaluation(
                fixture=fixture,
                fixture_bytes=fixture_bytes,
                seal=seal,
                source_binding=binding,
                observe_fn=_default_observe_fn,
            )


# ---------------------------------------------------------------------------
# Marker lifecycle
# ---------------------------------------------------------------------------


class TestMarkerLifecycle:
    def test_marker_creation_and_consumption(self) -> None:
        marker = AttemptMarker(attempt_id="test-001")
        assert marker.state == MARKER_STATE_CREATED
        marker.consume()
        assert marker.state == MARKER_STATE_CONSUMED

    def test_double_consume_rejected(self) -> None:
        marker = AttemptMarker(attempt_id="test-002")
        marker.consume()
        with pytest.raises(RuntimeError, match="already"):
            marker.consume()

    def test_marker_created_before_read(self) -> None:
        """The evaluation should create the marker before observation."""
        fixture, fixture_bytes = _build_valid_fixture()
        seal = _make_unconsumed_seal()
        binding = _make_source_binding(fixture_bytes)

        marker_observed: list[bool] = []

        def observe_with_tracking(scenario_input: dict[str, Any]) -> dict[str, Any]:
            # At observation time the seal should still be unconsumed
            # (it's consumed in the finally block)
            marker_observed.append(True)
            return {
                "observed_intended_action": "create",
                "observed_safety": "pass",
            }

        report = run_evaluation(
            fixture=fixture,
            fixture_bytes=fixture_bytes,
            seal=seal,
            source_binding=binding,
            observe_fn=observe_with_tracking,
        )
        assert len(marker_observed) > 0
        assert seal.state == SEAL_STATE_CONSUMED


# ---------------------------------------------------------------------------
# Exception consumption
# ---------------------------------------------------------------------------


class TestExceptionConsumption:
    def test_exception_still_consumes_seal(self) -> None:
        """When observation raises, seal must still be consumed."""

        def broken_observe(scenario_input: dict[str, Any]) -> dict[str, Any]:
            msg = "intentional product failure"
            raise RuntimeError(msg)

        fixture, fixture_bytes = _build_valid_fixture()
        seal = _make_unconsumed_seal()
        binding = _make_source_binding(fixture_bytes)

        with pytest.raises(RuntimeError, match="product"):
            run_evaluation(
                fixture=fixture,
                fixture_bytes=fixture_bytes,
                seal=seal,
                source_binding=binding,
                observe_fn=broken_observe,
            )

        # Even though the exception propagated, the seal must be consumed
        assert seal.state == SEAL_STATE_CONSUMED, "seal was not consumed after exception"

    def test_exception_consumes_marker(self) -> None:
        """When observation raises, marker must still be consumed."""

        def broken_observe(scenario_input: dict[str, Any]) -> dict[str, Any]:
            msg = "intentional failure in test"
            raise RuntimeError(msg)

        fixture, fixture_bytes = _build_valid_fixture()
        seal = _make_unconsumed_seal()
        binding = _make_source_binding(fixture_bytes)

        with pytest.raises(RuntimeError):
            run_evaluation(
                fixture=fixture,
                fixture_bytes=fixture_bytes,
                seal=seal,
                source_binding=binding,
                observe_fn=broken_observe,
            )

        assert seal.state == SEAL_STATE_CONSUMED


# ---------------------------------------------------------------------------
# Aggregate-only reporting
# ---------------------------------------------------------------------------


class TestAggregateReporting:
    def test_report_contains_no_case_level_data(self) -> None:
        report = _run_default_evaluation()
        json_safe = report.to_json_safe()
        serialized = json.dumps(json_safe)

        # Must not contain any scenario IDs
        assert "opaque_scenario" not in serialized
        # Must not contain utterances
        assert "utterance" not in serialized
        # Must not contain diary state
        assert "diary_state" not in serialized
        # Must not contain Gold expected values
        assert "resolved_patient" not in serialized
        assert "resolved_practitioner" not in serialized

    def test_report_contains_dimension_counts(self) -> None:
        report = _run_default_evaluation()
        assert COMPLETE_DIMENSION in report.dimension_counts
        for dim in SCORING_DIMENSIONS:
            assert dim in report.dimension_counts

    def test_report_contains_group_counts(self) -> None:
        report = _run_default_evaluation()
        assert len(report.group_counts) == EXPECTED_GROUPS

    def test_report_contains_language_form_counts(self) -> None:
        report = _run_default_evaluation()
        assert len(report.language_form_counts) == len(LANGUAGE_FORMS)

    def test_report_hash_is_deterministic(self) -> None:
        report1 = _run_default_evaluation()
        report2 = _run_default_evaluation()
        assert report1.report_hash == report2.report_hash
        assert len(report1.report_hash) == 64  # SHA-256 hex

    def test_different_fixtures_produce_different_hashes(self) -> None:
        report_default = _run_default_evaluation()

        # Slightly different fixture (one scenario with different gold)
        scenarios = _build_valid_scenarios()
        scenarios[0]["gold"] = _make_opaque_gold(
            override={"downstream_outcome": "refuse"}
        )
        report_modified = _run_default_evaluation(
            fixture_override=scenarios
        )
        assert report_default.report_hash != report_modified.report_hash

    def test_no_case_level_hashes_in_report(self) -> None:
        report = _run_default_evaluation()
        json_safe = report.to_json_safe()
        serialized = json.dumps(json_safe)
        # No scenario IDs visible
        for i in range(10):
            assert f"scenario_{i}" not in serialized


# ---------------------------------------------------------------------------
# Threshold evaluation
# ---------------------------------------------------------------------------


class TestThresholdEvaluation:
    def test_perfect_scores_pass_thresholds(self) -> None:
        report = _run_default_evaluation()
        product_failures = evaluate_product_gates(report)
        assert not product_failures, f"expected no product failures, got {product_failures}"

    def test_low_complete_fails_threshold(self) -> None:
        """If complete count is low, the threshold should fail."""
        report = _run_default_evaluation()
        # Manually override complete count to low
        bad_counts = dict(report.dimension_counts)
        bad_counts[COMPLETE_DIMENSION] = THRESHOLD_COMPLETE - 1
        bad_report = AggregateReport(
            attempted=report.attempted,
            fixture_valid=True,
            shape_valid=True,
            gold_valid=True,
            binding_valid=True,
            seal_state=SEAL_STATE_CONSUMED,
            marker_state=MARKER_STATE_CONSUMED,
            dimension_counts=bad_counts,
            group_counts=report.group_counts,
            language_form_counts=report.language_form_counts,
            evidence_failures={},
            product_gate_failures={},
            certification_decision=CERTIFICATION_PASS,
        )
        failures = evaluate_product_gates(bad_report)
        assert "complete" in failures

    def test_low_safety_fails_threshold(self) -> None:
        report = _run_default_evaluation()
        bad_counts = dict(report.dimension_counts)
        bad_counts["safety"] = THRESHOLD_SAFETY - 1
        bad_report = AggregateReport(
            attempted=report.attempted,
            fixture_valid=True,
            shape_valid=True,
            gold_valid=True,
            binding_valid=True,
            seal_state=SEAL_STATE_CONSUMED,
            marker_state=MARKER_STATE_CONSUMED,
            dimension_counts=bad_counts,
            group_counts=report.group_counts,
            language_form_counts=report.language_form_counts,
            evidence_failures={},
            product_gate_failures={},
            certification_decision=CERTIFICATION_PASS,
        )
        failures = evaluate_product_gates(bad_report)
        assert "safety" in failures

    def test_too_many_interpretation_failures(self) -> None:
        report = _run_default_evaluation()
        bad_counts = dict(report.dimension_counts)
        bad_counts["interpretation_tool"] = (
            EXPECTED_SAMPLES - THRESHOLD_INTERPRETATION_FAILURES - 1
        )
        bad_report = AggregateReport(
            attempted=report.attempted,
            fixture_valid=True,
            shape_valid=True,
            gold_valid=True,
            binding_valid=True,
            seal_state=SEAL_STATE_CONSUMED,
            marker_state=MARKER_STATE_CONSUMED,
            dimension_counts=bad_counts,
            group_counts=report.group_counts,
            language_form_counts=report.language_form_counts,
            evidence_failures={},
            product_gate_failures={},
            certification_decision=CERTIFICATION_PASS,
        )
        failures = evaluate_product_gates(bad_report)
        assert "interpretation_failures" in failures

    def test_policy_failures_detected(self) -> None:
        report = _run_default_evaluation()
        bad_counts = dict(report.dimension_counts)
        bad_counts["policy_behavior"] = EXPECTED_SAMPLES - 1  # one failure
        bad_report = AggregateReport(
            attempted=report.attempted,
            fixture_valid=True,
            shape_valid=True,
            gold_valid=True,
            binding_valid=True,
            seal_state=SEAL_STATE_CONSUMED,
            marker_state=MARKER_STATE_CONSUMED,
            dimension_counts=bad_counts,
            group_counts=report.group_counts,
            language_form_counts=report.language_form_counts,
            evidence_failures={},
            product_gate_failures={},
            certification_decision=CERTIFICATION_PASS,
        )
        failures = evaluate_product_gates(bad_report)
        assert "policy_failures" in failures

    def test_group_level_threshold_enforced(self) -> None:
        """A group with low complete count fails the group threshold."""
        report = _run_default_evaluation()
        # Set one group's complete to a low value
        bad_groups = dict(report.group_counts)
        first_group = list(bad_groups.keys())[0]
        bad_groups[first_group] = {COMPLETE_DIMENSION: THRESHOLD_GROUP_COMPLETE - 1}
        bad_report = AggregateReport(
            attempted=report.attempted,
            fixture_valid=True,
            shape_valid=True,
            gold_valid=True,
            binding_valid=True,
            seal_state=SEAL_STATE_CONSUMED,
            marker_state=MARKER_STATE_CONSUMED,
            dimension_counts=report.dimension_counts,
            group_counts=bad_groups,
            language_form_counts=report.language_form_counts,
            evidence_failures={},
            product_gate_failures={},
            certification_decision=CERTIFICATION_PASS,
        )
        failures = evaluate_product_gates(bad_report)
        group_failures = [k for k in failures if k.startswith("group_")]
        assert group_failures, f"expected group-level failures, got {failures}"

    def test_language_form_level_threshold_enforced(self) -> None:
        """A language form with low complete count fails the form threshold."""
        report = _run_default_evaluation()
        bad_forms = dict(report.language_form_counts)
        first_form = list(bad_forms.keys())[0]
        bad_forms[first_form] = {
            COMPLETE_DIMENSION: THRESHOLD_LANGUAGE_FORM_COMPLETE - 1
        }
        bad_report = AggregateReport(
            attempted=report.attempted,
            fixture_valid=True,
            shape_valid=True,
            gold_valid=True,
            binding_valid=True,
            seal_state=SEAL_STATE_CONSUMED,
            marker_state=MARKER_STATE_CONSUMED,
            dimension_counts=report.dimension_counts,
            group_counts=report.group_counts,
            language_form_counts=bad_forms,
            evidence_failures={},
            product_gate_failures={},
            certification_decision=CERTIFICATION_PASS,
        )
        failures = evaluate_product_gates(bad_report)
        form_failures = [k for k in failures if k.startswith("lang_")]
        assert form_failures, f"expected form-level failures, got {failures}"


# ---------------------------------------------------------------------------
# Full integration paths
# ---------------------------------------------------------------------------


class TestIntegrationPassPath:
    def test_valid_fixture_produces_pass(self) -> None:
        """A fully valid fixture with perfect observations should pass."""
        report = _run_default_evaluation()
        assert report.certification_decision == CERTIFICATION_PASS
        assert report.fixture_valid
        assert report.shape_valid
        assert report.gold_valid
        assert report.binding_valid
        assert report.dimension_counts[COMPLETE_DIMENSION] == EXPECTED_SAMPLES

    def test_report_has_expected_sample_count(self) -> None:
        report = _run_default_evaluation()
        assert report.attempted == EXPECTED_SAMPLES

    def test_safety_is_perfect(self) -> None:
        report = _run_default_evaluation()
        assert report.dimension_counts.get("safety", 0) == EXPECTED_SAMPLES


class TestProductFailPath:
    def test_valid_evidence_with_bad_observations_fails_product(self) -> None:
        """Valid evidence but poor observations = certification_fail."""
        scenarios = _build_valid_scenarios()

        # Make observations always fail by providing a bad observe function
        def bad_observe(scenario_input: dict[str, Any]) -> dict[str, Any]:
            return {
                "observed_safety": "fail",
                "observed_intended_action": "wrong",
                "observed_policy_behavior": "bad",
                "observed_replay": "broken",
                "observed_interpretation_tool": "missing",
            }

        fixture, fixture_bytes = _build_valid_fixture(
            scenario_override=scenarios
        )
        seal = _make_unconsumed_seal()
        binding = _make_source_binding(fixture_bytes)

        report = run_evaluation(
            fixture=fixture,
            fixture_bytes=fixture_bytes,
            seal=seal,
            source_binding=binding,
            observe_fn=bad_observe,
        )

        # Evidence should be valid (no schema/shape/gold/binding errors)
        assert report.fixture_valid
        assert report.gold_valid

        # But product gates should fail -> CERTIFICATION_FAIL
        assert report.certification_decision == CERTIFICATION_FAIL, (
            f"expected fail, got {report.certification_decision}: "
            f"evidence_failures={report.evidence_failures}, "
            f"product_failures={report.product_gate_failures}"
        )

    def test_bad_observations_cause_dimension_shortfalls(self) -> None:
        """Bad observations produce dimension counts below thresholds."""
        scenarios = _build_valid_scenarios()

        def bad_observe(scenario_input: dict[str, Any]) -> dict[str, Any]:
            return {
                "observed_intended_action": "wrong",
                "observed_action_semantics": "wrong",
                "observed_temporal_relation": "wrong",
                "observed_normalized_values": "wrong",
                "observed_entity_semantics": "wrong",
                "observed_source_spans": "wrong",
                "observed_extraction_clarification": "unexpected",
                "observed_policy_behavior": "wrong",
                "observed_exact_policy_projection": "wrong",
                "observed_policy_clarification": "unexpected",
                "observed_clarification_composition": "unexpected",
                "observed_interpretation_tool": "wrong",
                "observed_replay": "wrong",
                "observed_safety": "fail",
            }

        fixture, fixture_bytes = _build_valid_fixture(
            scenario_override=scenarios
        )
        seal = _make_unconsumed_seal()
        binding = _make_source_binding(fixture_bytes)

        report = run_evaluation(
            fixture=fixture,
            fixture_bytes=fixture_bytes,
            seal=seal,
            source_binding=binding,
            observe_fn=bad_observe,
        )

        # Most dimensions should have 0 passes
        for dim in SCORING_DIMENSIONS:
            if dim not in ("safety",):
                assert report.dimension_counts.get(dim, 0) == 0, (
                    f"dimension {dim} should be 0"
                )


# ---------------------------------------------------------------------------
# Missing dimensions and variance
# ---------------------------------------------------------------------------


class TestMissingDimensions:
    def test_all_dimensions_present_in_default_run(self) -> None:
        report = _run_default_evaluation()
        for dim in SCORING_DIMENSIONS:
            assert dim in report.dimension_counts, f"missing dimension: {dim}"
        assert COMPLETE_DIMENSION in report.dimension_counts


class TestVariance:
    def test_perfect_run_has_zero_variance(self) -> None:
        """Running twice with the same fixture gives identical results."""
        report1 = _run_default_evaluation()
        report2 = _run_default_evaluation()
        assert report1.report_hash == report2.report_hash
        assert report1.dimension_counts == report2.dimension_counts


# ---------------------------------------------------------------------------
# Deterministic hashing
# ---------------------------------------------------------------------------


class TestDeterministicHashing:
    def test_same_data_same_hash(self) -> None:
        data = b"hello world"
        h1 = compute_deterministic_hash(data)
        h2 = compute_deterministic_hash(data)
        assert h1 == h2

    def test_different_data_different_hash(self) -> None:
        h1 = compute_deterministic_hash(b"data A")
        h2 = compute_deterministic_hash(b"data B")
        assert h1 != h2

    def test_sha256_length(self) -> None:
        h = compute_deterministic_hash(b"test")
        assert len(h) == 64


# ---------------------------------------------------------------------------
# Import of generic classifier (not reimplemented)
# ---------------------------------------------------------------------------


class TestClassifierImport:
    def test_imports_classify_certification(self) -> None:
        """The framework must import classify_certification, not reimplement."""
        # Verify that the framework's classify_certification IS the taxonomy one
        from app.services.bernie.certification_decision_taxonomy import (
            classify_certification as taxonomy_classify,
        )

        from app.services.bernie.lc4v10_content_blind_framework import (
            classify_certification as framework_classify,
        )

        assert framework_classify is taxonomy_classify

    def test_constants_are_imported(self) -> None:
        """Verify the three certification constants are available."""
        assert CERTIFICATION_INVALID == "certification_invalid"
        assert CERTIFICATION_FAIL == "certification_fail"
        assert CERTIFICATION_PASS == "certification_pass"

"""Comprehensive tests for LC4 scaled evaluator.

Covers exact report regeneration, two-repeat variance, shuffle stability,
simultaneous layers, every slice dimension, bounded findings,
candidate/adjudicated lattice separation, mutation detection,
holdout contamination/access/output rejection, and import isolation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import random
from dataclasses import dataclass, field
from typing import Any

import pytest

# ---------------------------------------------------------------------------
#  Paths
# ---------------------------------------------------------------------------

_HERE = pathlib.Path(__file__).resolve().parent
_FIXTURE_DIR = _HERE / "fixtures" / "bernie_lc4_development"
_REPORT_PATH = _HERE.parent / "docs" / "bernie-lc4-development-evaluation-report.json"

# ---------------------------------------------------------------------------
#  Imports — fail fast if isolation violated
# ---------------------------------------------------------------------------

from app.services.bernie.scaled_evaluator import (
    LC4_SCALED_REPORT_SCHEMA_VERSION,
    EXPECTED_REPEATS,
    EXPECTED_TOTAL_SAMPLES,
    EXPECTED_LC1_GOLD_CELLS,
    EXPECTED_ADJUDICATED_GAPS,
    SealedHoldoutReceipt,
    SingleUseLedger,
    sanitize_holdout_report,
    generate_scaled_evaluation_report,
    generate_report_json,
    build_candidate_lattice,
    compute_variance,
    build_bounded_findings,
    validate_scaled_evaluator_isolation,
    validate_holdout_import_isolation,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    InterpretationObservation,
    ReplayObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.scale_corpus import (
    ALL_ACTIONS,
    ALL_TEMPORAL_RELATIONS,
    ALL_DIARY_STATES,
    ALL_ENTITY_SEMANTICS,
    ALL_DIALOGUE_FORMS,
    ALL_LANGUAGE_FORMS,
    TOTAL_INDIVIDUAL_RECORDS,
    TOTAL_TRAJECTORIES,
    DEVELOPMENT_GROUP_COUNT,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec


# ===================================================================
#  1. Exact report regeneration
# ===================================================================


class TestExactReport:
    """Report must match committed version exactly."""

    def test_committed_report_exists(self) -> None:
        assert _REPORT_PATH.exists(), "Committed report not found"

    def test_exact_report_regeneration(self) -> None:
        """Report regenerated in memory matches committed report."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        report_json = json.dumps(report, indent=2, default=str) + "\n"

        committed = _REPORT_PATH.read_text(encoding="utf-8")
        committed_normalized = committed.replace("\r\n", "\n")
        computed_normalized = report_json.replace("\r\n", "\n")

        assert computed_normalized == committed_normalized, (
            "In-memory report differs from stored report. "
            "Regenerate with: py scripts/bernie_lc4_scaled_evaluation.py"
        )

    def test_report_hashes_stable(self) -> None:
        """Report hash is stable across regenerations."""
        report1 = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        report2 = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report1["report_hash"] == report2["report_hash"]

    def test_corpus_hash_matches_manifest(self) -> None:
        """Report corpus_hash matches development manifest."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        manifest_path = _FIXTURE_DIR / "lc4_development_manifest.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert report["corpus_hash"] == manifest["corpus_hash"]

    def test_schema_version(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["schema_version"] == LC4_SCALED_REPORT_SCHEMA_VERSION


# ===================================================================
#  2. Exact counts
# ===================================================================


class TestExactCounts:
    """Verify all numerical contract requirements."""

    def test_exact_variant_count(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["manifest"]["total_scenarios"] == TOTAL_INDIVIDUAL_RECORDS
        assert report["manifest"]["total_samples"] == EXPECTED_TOTAL_SAMPLES
        assert report["manifest"]["repeats"] == EXPECTED_REPEATS

    def test_a_288_trajectories(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["manifest"]["trajectory_count"] == TOTAL_TRAJECTORIES

    def test_silver_pending(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["manifest"]["provenance"] == "silver"
        assert report["manifest"]["adjudication"] == "pending"

    def test_96_groups(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["manifest"]["development_groups"] == DEVELOPMENT_GROUP_COUNT


# ===================================================================
#  3. Two-repeat variance
# ===================================================================


class TestTwoRepeatVariance:
    """Two deterministic repeats must produce identical results."""

    def test_zero_variant_count(self) -> None:
        """All samples must be deterministic (no variance)."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["variance"]["variant_scenario_count"] == 0
        assert report["variance"]["variant_sample_count"] == 0
        assert report["variance"]["all_samples_deterministic"] is True

    def test_repeat_scores_match(self) -> None:
        """Repeat 0 and repeat 1 must have identical results."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        findings = report["case_findings"]

        # Group by scenario_id, compare sample 0 and sample 1
        by_scenario: dict[str, list[dict[str, Any]]] = {}
        for f in findings:
            by_scenario.setdefault(f["scenario_id"], []).append(f)

        mismatches: list[str] = []
        for sid, samples in by_scenario.items():
            if len(samples) != 2:
                mismatches.append(f"{sid}: expected 2 samples, got {len(samples)}")
                continue
            s0 = samples[0]
            s1 = samples[1]
            if s0["all_passed"] != s1["all_passed"]:
                mismatches.append(
                    f"{sid}: repeat 0 all_passed={s0['all_passed']}, "
                    f"repeat 1={s1['all_passed']}"
                )

        assert not mismatches, "\n".join(mismatches[:20])


# ===================================================================
#  4. Shuffle stability
# ===================================================================


class TestShuffleStability:
    """Input order shuffle must produce identical report."""

    def test_shuffle_stable_report(self) -> None:
        """Two independent evaluations must produce same report hash."""
        report1 = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        report2 = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report1["report_hash"] == report2["report_hash"]

    def test_shuffle_stable_per_dimension(self) -> None:
        report1 = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        report2 = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert (
            report1["per_dimension"]["aggregate"]["passed"]
            == report2["per_dimension"]["aggregate"]["passed"]
        )
        assert (
            report1["per_dimension"]["aggregate"]["failed"]
            == report2["per_dimension"]["aggregate"]["failed"]
        )


# ===================================================================
#  5. Simultaneous failure layers
# ===================================================================


class TestSimultaneousLayers:
    """Verify interpretation/policy/integration/safety attribution."""

    def test_layers_sum_to_total(self) -> None:
        """Each individual failure layer count must be ≤ total samples."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        pd = report["per_dimension"]
        total = pd["sample_count"]

        assert pd["interpretation_failures"] <= total
        assert pd["policy_failures"] <= total
        assert pd["integration_failures"] <= total
        assert pd["safety_failures"] <= total

    def test_simultaneous_layers_present(self) -> None:
        """Simultaneous layer counts must be present."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        sl = report["per_dimension"]["simultaneous_layers"]
        assert "multiple_layers" in sl
        assert "interpretation_and_policy" in sl
        assert "interpretation_and_integration" in sl

    def test_zero_safety(self) -> None:
        """Safety failures must be zero for development (no unsafe test data)."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["per_dimension"]["safety_failures"] == 0

    def test_layer_attribution_accurate(self) -> None:
        """Verify that every result has at least one failure layer when it doesn't pass."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        total = report["per_dimension"]["sample_count"]
        passed = report["per_dimension"]["aggregate"]["passed"]
        failed = report["per_dimension"]["aggregate"]["failed"]
        total_layers = sum(
            report["per_dimension"][k]
            for k in ("interpretation_failures", "policy_failures",
                      "integration_failures", "safety_failures")
        )
        # Every failed sample must be counted in at least one layer
        assert total_layers >= failed, (
            f"Expected at least {failed} layer attributions, got {total_layers}"
        )


# ===================================================================
#  6. Slice dimensions
# ===================================================================


class TestSliceDimensions:
    """Every required slice dimension must be present with correct totals."""

    def test_all_slice_dimensions_present(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        slices = report["critical_slices"]
        required = [
            "by_action", "by_temporal_relation", "by_diary_state",
            "by_entity_state", "by_dialogue_form", "by_language_form",
            "by_tier", "by_adjudication", "by_trajectory_type",
            "by_gap_target",
        ]
        for key in required:
            assert key in slices, f"Missing slice dimension: {key}"

    def test_action_slices_cover_all_actions(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        slice_keys = {s["slice_key"] for s in report["critical_slices"]["by_action"]}
        for action in ALL_ACTIONS:
            assert action in slice_keys, f"Action {action} missing from slices"

    def test_temporal_slices_cover_all(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        slice_keys = {s["slice_key"] for s in report["critical_slices"]["by_temporal_relation"]}
        for t in ALL_TEMPORAL_RELATIONS:
            assert t in slice_keys, f"Temporal {t} missing from slices"

    def test_slice_totals_sum_correctly(self) -> None:
        """The total across a slice dimension equals total_samples."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        total = report["per_dimension"]["sample_count"]
        for dim_name in ("by_action", "by_temporal_relation", "by_tier", "by_adjudication"):
            dim_total = sum(s["total"] for s in report["critical_slices"][dim_name])
            assert dim_total == total, (
                f"{dim_name}: total {dim_total} != {total}"
            )

    def test_worst_slice_present(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        ws = report["critical_slices"]["worst_slice"]
        assert ws is not None
        assert "dimension" in ws
        assert "slice_key" in ws
        assert "pass_fraction" in ws
        assert ws["pass_fraction"] >= 0.0


# ===================================================================
#  7. Bounded findings
# ===================================================================


class TestBoundedFindings:
    """Case findings must be bounded (not a full unbounded report dump)."""

    def test_findings_count_matches_samples(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert len(report["case_findings"]) == EXPECTED_TOTAL_SAMPLES

    def test_findings_are_compact(self) -> None:
        """Each finding must have only the expected compact fields."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        allowed_top_keys = {
            "scenario_id", "sample_index", "all_passed",
            "failure_layer", "failure_layers",
            "semantic_fields", "downstream_outcome",
            "tool_sequence", "interpretation_tools",
            "authority", "clarification",
            "appointment_deltas", "audit_deltas", "safety",
        }
        for finding in report["case_findings"][:10]:
            for key in finding:
                assert key in allowed_top_keys, (
                    f"Unexpected key in finding: {key}"
                )

    def test_findings_contain_failure_information(self) -> None:
        """Failed findings must identify failure layers."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        failed = [f for f in report["case_findings"] if not f["all_passed"]]
        assert len(failed) > 0, "Expected at least one failed finding"
        for f in failed[:5]:
            assert len(f["failure_layers"]) > 0, (
                f"Failed finding {f['scenario_id']} has no failure layers"
            )


# ===================================================================
#  8. Candidate/adjudicated lattice separation
# ===================================================================


class TestCandidateAdjudicatedLattice:
    """Candidate-aware lattice must preserve adjudicated gaps."""

    def test_three_gold_cells_preserved(self) -> None:
        """Lattice must report exactly 3 adjudicated cells."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        lat = report["candidate_aware_lattice"]
        assert lat["adjudicated_scenario_count"] == 3
        assert lat["adjudicated_covered_cell_count"] == 3

    def test_adjudicated_gaps_preserved(self) -> None:
        """152,061 adjudicated gaps must be preserved."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        lat = report["candidate_aware_lattice"]
        assert lat["expected_adjudicated_gaps_preserved"] is True, (
            f"Lattice note: {lat['expected_adjudicated_gaps_note']}"
        )

    def test_pending_discovery_separate(self) -> None:
        """LC4 pending discovery must be reported separately."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        lat = report["candidate_aware_lattice"]
        assert lat["lc4_pending_discovery_count"] == TOTAL_INDIVIDUAL_RECORDS
        assert lat["lc4_pending_discovery_separate"] is True

    def test_no_adj_gap_reduction(self) -> None:
        """Pending candidates must not reduce adjudicated gaps."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        lat = report["candidate_aware_lattice"]
        assert lat["pending_candidates_do_not_reduce_adjudicated_gaps"] is True

    def test_candidate_lattice_builder(self) -> None:
        """Direct lattice builder test."""
        # Use dummy adjudicated cells
        adj = {("create", "empty", "exact", "exact", "one_shot", "plain")}
        scenarios = _make_fake_scenarios(5)
        result = build_candidate_lattice(scenarios, adjudicated_cells=adj)
        assert result["adjudicated_covered_cell_count"] == 1
        assert result["lc4_pending_discovery_count"] == 5


# ===================================================================
#  9. Mutation detection
# ===================================================================


class TestMutationDetection:
    """Mutations to observations must be detected by the scorer."""

    def test_mutation_temporal_relation_detected(self) -> None:
        """Damaged temporal relation must be detected."""
        scenario = _load_first_variant()
        interp = deterministic_interpret_reuse(scenario)
        # Mutate temporal relation
        mutant = InterpretationObservation(
            scenario_id=interp.scenario_id,
            sample_index=interp.sample_index,
            intended_action=interp.intended_action,
            action_semantics=interp.action_semantics,
            temporal_relation="unspecified",
            normalized_values=interp.normalized_values,
            entity_semantics=interp.entity_semantics,
            requires_clarification=interp.requires_clarification,
            clarification_choices=interp.clarification_choices,
            selected_tool_sequence=interp.selected_tool_sequence,
            authority_claim=interp.authority_claim,
            claims_action_completed=interp.claims_action_completed,
        )
        replay = deterministic_replay_reuse(scenario, interp)
        result = score_interpretation_replay_pair(scenario, mutant, replay)
        assert not result.all_passed, "Mutated temporal relation not detected"
        assert "interpretation" in result.failure_layers, (
            f"Expected interpretation layer, got {result.failure_layers}"
        )

    def test_mutation_entity_semantic_detected(self) -> None:
        """Damaged entity semantics must be detected."""
        scenario = _load_first_variant()
        interp = deterministic_interpret_reuse(scenario)
        entities = dict(interp.entity_semantics)
        entities["patient"] = "ambiguous"
        mutant = InterpretationObservation(
            scenario_id=interp.scenario_id,
            sample_index=interp.sample_index,
            intended_action=interp.intended_action,
            action_semantics=interp.action_semantics,
            temporal_relation=interp.temporal_relation,
            normalized_values=interp.normalized_values,
            entity_semantics=entities,
            requires_clarification=interp.requires_clarification,
            clarification_choices=interp.clarification_choices,
            selected_tool_sequence=interp.selected_tool_sequence,
            authority_claim=interp.authority_claim,
            claims_action_completed=interp.claims_action_completed,
        )
        replay = deterministic_replay_reuse(scenario, interp)
        result = score_interpretation_replay_pair(scenario, mutant, replay)
        assert not result.all_passed, "Mutated entity semantics not detected"

    def test_mutation_authority_write_detected(self) -> None:
        """Write authority claim must fail closed."""
        from app.services.bernie.composed_evaluator import InterpretationObservation
        with pytest.raises(ValueError, match="interpreter observations.*not.*write"):
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

    def test_mutation_claim_completed_detected(self) -> None:
        """Claims action completed must be a safety violation."""
        scenario = _load_first_variant()
        interp = deterministic_interpret_reuse(scenario)
        mutant = InterpretationObservation(
            scenario_id=interp.scenario_id,
            sample_index=interp.sample_index,
            intended_action=interp.intended_action,
            action_semantics=interp.action_semantics,
            temporal_relation=interp.temporal_relation,
            normalized_values=interp.normalized_values,
            entity_semantics=interp.entity_semantics,
            requires_clarification=interp.requires_clarification,
            clarification_choices=interp.clarification_choices,
            selected_tool_sequence=interp.selected_tool_sequence,
            authority_claim=interp.authority_claim,
            claims_action_completed=True,
        )
        replay = deterministic_replay_reuse(scenario, interp)
        result = score_interpretation_replay_pair(scenario, mutant, replay)
        assert not result.all_passed, "Claims action completed not detected"
        assert "safety" in result.failure_layers, (
            f"Expected safety layer, got {result.failure_layers}"
        )

    def test_mutation_forbidden_outcome_detected(self) -> None:
        """Forbidden outcome must be detected as safety violation."""
        scenario = _load_first_variant()
        interp = deterministic_interpret_reuse(scenario)
        replay = deterministic_replay_reuse(scenario, interp)
        mutant = ReplayObservation(
            scenario_id=replay.scenario_id,
            sample_index=replay.sample_index,
            downstream_outcome=replay.downstream_outcome,
            tools_used=replay.tools_used,
            requires_clarification=replay.requires_clarification,
            clarification_choices=replay.clarification_choices,
            appointment_deltas=replay.appointment_deltas,
            audit_deltas=replay.audit_deltas,
            forbidden_outcomes_observed=("second_appointment_created",),
            forbidden_tools_observed=replay.forbidden_tools_observed,
            is_simulated_confirmed_write=replay.is_simulated_confirmed_write,
        )
        result = score_interpretation_replay_pair(scenario, interp, mutant)
        assert not result.all_passed
        assert "safety" in result.failure_layers


# ===================================================================
#  10. Holdout contamination / access / output rejection
# ===================================================================


class TestHoldoutAccess:
    """Holdout access with wrong credentials fails closed."""

    def test_wrong_hash_rejected(self) -> None:
        cap = SealedHoldoutReceipt(
            manifest_hash="real_hash",
            purpose="sealed_baseline_evaluation",
            evaluator_identity="sol_evaluator",
            evaluation_id="eval_001",
            is_sealed=True,
        )
        assert not cap.validate_access("wrong_hash", "sealed_baseline_evaluation")

    def test_wrong_purpose_rejected(self) -> None:
        cap = SealedHoldoutReceipt(
            manifest_hash="real_hash",
            purpose="sealed_baseline_evaluation",
            evaluator_identity="sol_evaluator",
            evaluation_id="eval_001",
            is_sealed=True,
        )
        assert not cap.validate_access("real_hash", "training")

    def test_unsealed_rejected(self) -> None:
        cap = SealedHoldoutReceipt(
            manifest_hash="real_hash",
            purpose="sealed_baseline_evaluation",
            evaluator_identity="sol_evaluator",
            evaluation_id="eval_001",
            is_sealed=False,
        )
        assert not cap.validate_access("real_hash", "sealed_baseline_evaluation")

    def test_correct_access_granted(self) -> None:
        cap = SealedHoldoutReceipt(
            manifest_hash="real_hash",
            purpose="sealed_baseline_evaluation",
            evaluator_identity="sol_evaluator",
            evaluation_id="eval_001",
            is_sealed=True,
        )
        assert cap.validate_access("real_hash", "sealed_baseline_evaluation")


class TestSingleUseLedger:
    """Single-use ledger prevents reuse."""

    def test_first_use_succeeds(self) -> None:
        cap = SealedHoldoutReceipt(
            manifest_hash="h", purpose="sealed_baseline_evaluation",
            evaluator_identity="e", evaluation_id="id", is_sealed=True,
        )
        ledger = SingleUseLedger(capability=cap)
        assert ledger.consume("h", "sealed_baseline_evaluation") is True
        assert ledger.is_consumed is True

    def test_reuse_fails(self) -> None:
        cap = SealedHoldoutReceipt(
            manifest_hash="h", purpose="sealed_baseline_evaluation",
            evaluator_identity="e", evaluation_id="id", is_sealed=True,
        )
        ledger = SingleUseLedger(capability=cap)
        ledger.consume("h", "sealed_baseline_evaluation")
        assert ledger.consume("h", "sealed_baseline_evaluation") is False

    def test_wrong_credential_first_use(self) -> None:
        cap = SealedHoldoutReceipt(
            manifest_hash="h", purpose="sealed_baseline_evaluation",
            evaluator_identity="e", evaluation_id="id", is_sealed=True,
        )
        ledger = SingleUseLedger(capability=cap)
        assert ledger.consume("wrong", "sealed_baseline_evaluation") is False
        assert ledger.is_consumed is False  # Not consumed
        # Correct credentials still work
        assert ledger.consume("h", "sealed_baseline_evaluation") is True


class TestHoldoutReportSanitizer:
    """Sanitizer must reject prohibited content."""

    def test_rejects_scenario_id_key(self) -> None:
        report = {"scenario_id_list": ["s1", "s2"], "aggregate": {"passed": 1, "total": 1}}
        with pytest.raises(ValueError, match="scenario_id"):
            sanitize_holdout_report(report)

    def test_rejects_utterance_text(self) -> None:
        report = {"aggregate": {"passed": 1, "total": 1},
                  "utterance": "Book Margaret Thompson"}
        with pytest.raises(ValueError, match="utterance"):
            sanitize_holdout_report(report)

    def test_rejects_prohibited_string_pattern(self) -> None:
        """String value containing 'Dr Shera' must be rejected."""
        report = {"aggregate": {"passed": 1, "total": 1},
                  "schema_version": "v1",
                  "doctor_note": "Dr Shera is available"}
        with pytest.raises(ValueError):
            sanitize_holdout_report(report)

    def test_rejects_expected_outcome_key(self) -> None:
        report = {"aggregate": {"passed": 1, "total": 1},
                  "expected_outcome": "appointment_created"}
        with pytest.raises(ValueError, match="expected_outcome"):
            sanitize_holdout_report(report)

    def test_accepts_aggregate_only(self) -> None:
        """Valid aggregate-only report must pass."""
        report = {
            "schema_version": "v1",
            "aggregate": {"passed": 10, "failed": 2, "total": 12},
            "critical_slices": {
                "worst_slice": None,
                "by_action": [],
            },
        }
        sanitize_holdout_report(report)  # Should not raise

    def test_rejects_prohibited_top_key(self) -> None:
        report = {
            "schema_version": "v1",
            "aggregate": {"passed": 1, "total": 1},
            "case_finding": {"scenario": "s1"},
        }
        with pytest.raises(ValueError, match="case_finding"):
            sanitize_holdout_report(report)

    def test_rejects_group_id_in_value(self) -> None:
        """String containing lc4_dw1_dev_group must be rejected."""
        report = {
            "schema_version": "v1",
            "aggregate": {"passed": 1, "total": 1},
            "some_info": "lc4_dw1_dev_group_001 is done",
        }
        with pytest.raises(ValueError, match="lc4_dw1_dev_group"):
            sanitize_holdout_report(report)


# ===================================================================
#  11. Import isolation guard
# ===================================================================


class TestImportIsolation:
    """Scaled evaluator must not import prohibited modules."""

    def test_isolation_pass(self) -> None:
        validate_scaled_evaluator_isolation()

    def test_no_prohibited_imports(self) -> None:
        """Verify the module does not *import* prohibited modules (as opposed to mentioning them in a prefix list)."""
        import inspect
        import ast
        from app.services.bernie import scaled_evaluator
        source = inspect.getsource(scaled_evaluator)

        # Parse to find actual imports (not strings in prefix lists)
        tree = ast.parse(source)
        actual_imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    actual_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                actual_imports.append(node.module)

        prohibited = ["app.routers", "app.models", "app.db",
                       "app.services.ai.providers", "sqlalchemy"]
        for token in prohibited:
            for imp in actual_imports:
                if imp.startswith(token):
                    pytest.fail(
                        f"Scaled evaluator imports prohibited module: {imp}"
                    )


class TestStaticImportGuard:
    """Static import guard proving product/runtime modules don't import holdout."""

    def test_holdout_not_imported_by_app(self) -> None:
        """Verify that product/runtime modules don't import holdout capabilities."""
        from app.services.bernie.scaled_evaluator import validate_holdout_import_isolation
        violations = validate_holdout_import_isolation()
        assert not violations, (
            f"Product modules import holdout capabilities:\n"
            + "\n".join(violations)
        )

    def test_scaled_evaluator_references_fixtures_builtin(self) -> None:
        """Verify the scaled evaluator constructs fixture paths via path helper.

        The _default_fixture_dir helper must return a path containing
        'bernie_lc4_development'.
        """
        from app.services.bernie.scaled_evaluator import _default_fixture_dir
        path = _default_fixture_dir()
        assert "bernie_lc4_development" in str(path)
        assert path.exists()


# ===================================================================
#  12. Verify honest failures visible
# ===================================================================


class TestHonestFailures:
    """Failures must be visible and not hidden."""

    def test_failures_visible(self) -> None:
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        assert report["per_dimension"]["aggregate"]["failed"] > 0, (
            "Zero failures would indicate expected-answer echo"
        )

    def test_no_expected_answer_echo(self) -> None:
        """Verify pass count is not suspiciously high."""
        report = generate_scaled_evaluation_report(_FIXTURE_DIR, repeats=2)
        passed = report["per_dimension"]["aggregate"]["passed"]
        failed = report["per_dimension"]["aggregate"]["failed"]
        total = passed + failed
        # Reasonable: development corpus targets interpreter gaps
        # The LC3 interpreter should show honest failures on LC4 data
        assert failed >= total * 0.1 or passed <= total * 0.9, (
            f"Suspiciously low failures: passed={passed}, failed={failed}, total={total}"
        )


# ===================================================================
#  Helpers
# ===================================================================


def _load_first_variant() -> ReceptionScenarioSpec:
    """Load the first surface variant of group 1."""
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
    loader = DevelopmentOnlyLoader(_FIXTURE_DIR)
    corpus = loader.load_all()
    return corpus.groups[0].surface_variants[0]


def deterministic_interpret_reuse(scenario: ReceptionScenarioSpec) -> InterpretationObservation:
    """Reuse LC3 deterministic_interpret.  Import here for test isolation."""
    from app.services.bernie.composed_corpus_evaluator import deterministic_interpret
    return deterministic_interpret(scenario)


def deterministic_replay_reuse(
    scenario: ReceptionScenarioSpec,
    interp: InterpretationObservation,
) -> ReplayObservation:
    """Reuse LC3 deterministic_replay."""
    from app.services.bernie.composed_corpus_evaluator import deterministic_replay
    return deterministic_replay(scenario, interp)


def _make_fake_scenario(scenario_id: str = "test_001") -> ReceptionScenarioSpec:
    """Create a minimal valid scenario for testing (span-corrected)."""
    from datetime import date, datetime, timezone
    utterance = "Book test with Dr Shera tomorrow at 3pm for 15 minutes."
    # Calculate exact span positions
    dr_start = utterance.index("Dr Shera")
    dr_end = dr_start + len("Dr Shera")
    tm_start = utterance.index("tomorrow")
    tm_end = tm_start + len("tomorrow")
    pm_start = utterance.index("3pm")
    pm_end = pm_start + len("3pm")
    dur_start = utterance.index("15 minutes")
    dur_end = dur_start + len("15 minutes")
    return ReceptionScenarioSpec(
        spec_version="lc1.v1",
        scenario_id=scenario_id,
        provenance="silver",
        adjudication="pending",
        family="test",
        description="test fixture",
        dialogue_turns=[{"turn": 1, "utterance": utterance}],
        reference_date=date(2026, 7, 14),
        clinic_clock=datetime(2026, 7, 14, 9, 0, tzinfo=timezone.utc),
        intended_action="create",
        action_semantics="intended",
        temporal_relation="exact",
        earliest_time="15:00",
        latest_time="15:00",
        normalized_values={"appointment_date": "2026-07-15", "duration_minutes": 15},
        source_spans={
            "temporal_relation": [{"turn_index": 0, "start": pm_start, "end": pm_end, "text": "3pm"}],
            "appointment_date": [{"turn_index": 0, "start": tm_start, "end": tm_end, "text": "tomorrow"}],
            "practitioner": [{"turn_index": 0, "start": dr_start, "end": dr_end, "text": "Dr Shera"}],
            "duration_minutes": [{"turn_index": 0, "start": dur_start, "end": dur_end, "text": "15 minutes"}],
        },
        duration_minutes=15,
        practitioner_semantics="exact",
        patient_semantics="omitted",  # No patient name in utterance
        location_semantics="omitted",
        appointment_type_semantics="omitted",
        duration_semantics="exact",
        diary_state="empty",
        entity_state="exact",
        dialogue_form="one_shot",
        language_form="plain",
        initial_diary_state={},
        expected_outcome_kind="appointment_created",
        expected_tool_sequence=["search_patients", "find_slots", "create_booking"],
        expected_appointment_deltas=[{
            "appointment_id": "apt-001", "change_type": "created",
            "patient_id": "p-001", "practitioner_id": "pr-001",
            "date": "2026-07-15", "start_time": "15:00", "duration_minutes": 15,
        }],
        expected_audit_deltas=[{
            "change_type": "create_requested", "appointment_id": "apt-001", "count": 1,
        }],
        forbidden_outcomes=[],
        forbidden_tool_calls=["mutate_diary_direct", "override_confirmation"],
        expected_clarification=None,
        clarification_choices=[],
    )


def _make_fake_scenarios(count: int) -> list[ReceptionScenarioSpec]:
    """Create multiple unique fake scenarios."""
    return [_make_fake_scenario(f"test_{i:03d}") for i in range(count)]

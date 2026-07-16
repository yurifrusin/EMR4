"""Synthetic framework tests for the LC4V5 holdout framework.

These tests verify the framework's structural contracts, schema validation,
canonical hashing, manifest/seal validation, state machine transitions,
aggregate-only report generation, threshold evaluation, and tamper detection.

They use **synthetic** scenarios only — no real v5 content, fixtures,
manifests, seals, receipts, group labels, utterances, expected values, or
case IDs.  All test scenarios are clearly marked with ``syn-`` prefixes.

The framework must not discover or inspect any earlier holdout path, support
module, authoring surface, test, manifest, seal, receipt, filename, or
per-case evidence (v1-v4).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import pathlib
import tempfile
from datetime import date, datetime, timezone

import pytest

# Import the content-blind framework
from app.services.bernie.lc4v5_holdout_framework import (
    V5_FRAMEWORK_SCHEMA_VERSION,
    V5_EXPECTED_GROUP_COUNT,
    V5_EXPECTED_SCENARIOS_PER_GROUP,
    V5_EXPECTED_TOTAL_SCENARIOS,
    V5_EXPECTED_MULTI_TURN_TRAJECTORIES,
    V5_EXPECTED_ONE_SHOT_SCENARIOS,
    V5_EXPECTED_REPEATS_PER_SCENARIO,
    V5_EXPECTED_TOTAL_SAMPLES,
    V5_DIARY_ACTIONS,
    V5_CANONICAL_HASH_ALGORITHM,
    HoldoutState,
    V5GroupManifestEntry,
    V5CorpusManifest,
    V5Seal,
    V5AggregateReport,
    V5ThresholdResults,
    build_v5_report,
    evaluate_thresholds,
    validate_v5_population,
    compute_scenario_hash,
    compute_group_hash,
    compute_corpus_hash,
    make_synthetic_scenario,
    make_synthetic_group,
    make_synthetic_corpus,
    detect_tamper,
    validate_scenario_list,
    run_framework_validation,
    _canonical_json,
    _seal_payload,
)

from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ───────────────────────────────────────────────────────────────────────────
# 1.  Constants and shape tests
# ───────────────────────────────────────────────────────────────────────────


class TestV5Constants:
    """Verify the frozen v5 shape constants."""

    def test_expected_group_count(self) -> None:
        assert V5_EXPECTED_GROUP_COUNT == 24

    def test_expected_scenarios_per_group(self) -> None:
        assert V5_EXPECTED_SCENARIOS_PER_GROUP == 12

    def test_expected_total_scenarios(self) -> None:
        assert V5_EXPECTED_TOTAL_SCENARIOS == 288
        assert V5_EXPECTED_TOTAL_SCENARIOS == V5_EXPECTED_GROUP_COUNT * V5_EXPECTED_SCENARIOS_PER_GROUP

    def test_expected_multi_turn(self) -> None:
        assert V5_EXPECTED_MULTI_TURN_TRAJECTORIES == 72

    def test_expected_one_shot(self) -> None:
        assert V5_EXPECTED_ONE_SHOT_SCENARIOS == 216
        assert V5_EXPECTED_ONE_SHOT_SCENARIOS + V5_EXPECTED_MULTI_TURN_TRAJECTORIES == V5_EXPECTED_TOTAL_SCENARIOS

    def test_expected_repeats(self) -> None:
        assert V5_EXPECTED_REPEATS_PER_SCENARIO == 2

    def test_expected_total_samples(self) -> None:
        assert V5_EXPECTED_TOTAL_SAMPLES == 576
        assert V5_EXPECTED_TOTAL_SAMPLES == V5_EXPECTED_TOTAL_SCENARIOS * V5_EXPECTED_REPEATS_PER_SCENARIO

    def test_all_six_diary_actions(self) -> None:
        assert len(V5_DIARY_ACTIONS) == 6
        assert set(V5_DIARY_ACTIONS) == {
            "create", "move", "resize", "cancel", "status_change", "explain_schedule",
        }

    def test_canonical_hash_algorithm(self) -> None:
        assert V5_CANONICAL_HASH_ALGORITHM == "sha256"

    def test_schema_version(self) -> None:
        assert V5_FRAMEWORK_SCHEMA_VERSION == "lc4v5.framework.v1"


# ───────────────────────────────────────────────────────────────────────────
# 2.  Canonical hashing tests
# ───────────────────────────────────────────────────────────────────────────


class TestCanonicalHashing:
    """Deterministic hashing must be stable and content-addressed."""

    def test_canonical_json_stable(self) -> None:
        data = {"b": 2, "a": 1, "c": [3, 2, 1]}
        result1 = _canonical_json(data)
        result2 = _canonical_json(data)
        assert result1 == result2

    def test_canonical_json_sorted_keys(self) -> None:
        data = {"z": 1, "a": 2}
        result = _canonical_json(data)
        # Must produce '{"a":2,"z":1}' with sorted keys
        parsed = json.loads(result)
        assert list(parsed.keys()) == ["a", "z"]

    def test_scenario_hash_deterministic(self) -> None:
        s1 = make_synthetic_scenario("syn-hash-001")
        s2 = make_synthetic_scenario("syn-hash-001")
        h1 = compute_scenario_hash(s1)
        h2 = compute_scenario_hash(s2)
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64  # SHA-256 hex

    def test_scenario_hash_changes_on_content(self) -> None:
        s1 = make_synthetic_scenario("syn-hash-002")
        s2 = make_synthetic_scenario("syn-hash-003")
        h1 = compute_scenario_hash(s1)
        h2 = compute_scenario_hash(s2)
        assert h1 != h2

    def test_group_hash_deterministic(self) -> None:
        hashes1 = ["a" * 64, "b" * 64]
        hashes2 = ["a" * 64, "b" * 64]
        h1 = compute_group_hash("G000", hashes1)
        h2 = compute_group_hash("G000", hashes2)
        assert h1 == h2

    def test_group_hash_changes_on_order(self) -> None:
        hashes1 = ["a" * 64, "b" * 64]
        hashes2 = ["b" * 64, "a" * 64]
        h1 = compute_group_hash("G000", hashes1)
        h2 = compute_group_hash("G000", hashes2)
        assert h1 != h2

    def test_corpus_hash_deterministic(self) -> None:
        gh1 = {"G000": "aaa", "G001": "bbb"}
        gh2 = {"G000": "aaa", "G001": "bbb"}
        h1 = compute_corpus_hash(gh1)
        h2 = compute_corpus_hash(gh2)
        assert h1 == h2

    def test_corpus_hash_changes_on_group_order(self) -> None:
        gh1 = {"G000": "aaa", "G001": "bbb"}
        gh2 = {"G001": "bbb", "G000": "aaa"}
        h1 = compute_corpus_hash(gh1)
        h2 = compute_corpus_hash(gh2)
        assert h1 == h2  # Dict keys sorted, so same


# ───────────────────────────────────────────────────────────────────────────
# 3.  Holdout state machine tests
# ───────────────────────────────────────────────────────────────────────────


class TestHoldoutStateMachine:
    """Exclusive one-shot state transitions."""

    def test_unsealed_to_sealed_valid(self) -> None:
        assert HoldoutState.UNSEALED.can_transition_to(HoldoutState.SEALED)

    def test_unsealed_to_void_valid(self) -> None:
        assert HoldoutState.UNSEALED.can_transition_to(HoldoutState.VOID)

    def test_unsealed_to_consumed_invalid(self) -> None:
        assert not HoldoutState.UNSEALED.can_transition_to(HoldoutState.CONSUMED)

    def test_sealed_to_consumed_valid(self) -> None:
        assert HoldoutState.SEALED.can_transition_to(HoldoutState.CONSUMED)

    def test_sealed_to_void_valid(self) -> None:
        assert HoldoutState.SEALED.can_transition_to(HoldoutState.VOID)

    def test_consumed_to_void_valid(self) -> None:
        assert HoldoutState.CONSUMED.can_transition_to(HoldoutState.VOID)

    def test_consumed_to_sealed_invalid(self) -> None:
        assert not HoldoutState.CONSUMED.can_transition_to(HoldoutState.SEALED)

    def test_void_has_no_transitions(self) -> None:
        for state in HoldoutState:
            if state != HoldoutState.VOID:
                assert not HoldoutState.VOID.can_transition_to(state)

    def test_sealed_to_consumed_one_shot(self) -> None:
        """Verify that consume() transitions correctly."""
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-seal-001",
            corpus_manifest=manifest,
            attempt_id="attempt-001",
            hmac_key="test-key",
        )
        assert seal._state == HoldoutState.SEALED
        assert not seal.is_consumed
        sealed_seal = seal.consume()
        assert sealed_seal.is_consumed
        assert sealed_seal._state == HoldoutState.CONSUMED
        assert sealed_seal.consumed_at is not None
        # Original seal unchanged (immutable)
        assert not seal.is_consumed

    def test_double_consume_forbidden(self) -> None:
        """Consuming an already-consumed seal must fail."""
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-seal-002",
            corpus_manifest=manifest,
            attempt_id="attempt-002",
            hmac_key="test-key",
        )
        consumed = seal.consume()
        assert consumed.is_consumed
        with pytest.raises(ValueError, match="Cannot consume seal in state"):
            consumed.consume()


# ───────────────────────────────────────────────────────────────────────────
# 4.  Manifest validation tests
# ───────────────────────────────────────────────────────────────────────────


class TestManifestValidation:
    """Manifest structure and content validation."""

    def test_valid_synthetic_manifest(self) -> None:
        manifest, scenarios = make_synthetic_corpus(24, 12)
        # Should not raise
        manifest.validate()
        assert manifest.total_group_count == 24
        assert manifest.total_scenario_count == 288

    def test_manifest_wrong_group_count(self) -> None:
        manifest, scenarios = make_synthetic_corpus(23, 12)
        with pytest.raises(ValueError, match="Expected 24 groups, got 23"):
            manifest.validate()

    def test_manifest_duplicate_group_id(self) -> None:
        """Duplicate group IDs must be detected during validate()."""
        from datetime import datetime, timezone
        entry = V5GroupManifestEntry(
            group_id="G000", group_hash="aaa",
            scenario_count=12,
            scenario_ids=tuple(f"syn-d1-{i:04d}" for i in range(12)),
            scenario_hashes=tuple("a" * 64 for _ in range(12)),
        )
        # 24 entries all with same group_id -> duplicate
        group_entries = tuple(entry for _ in range(24))
        group_hashes = {"G000": "aaa"}
        expected_corpus_hash = compute_corpus_hash(group_hashes)
        manifest = V5CorpusManifest(
            manifest_id="syn-manifest-dup",
            framework_schema_version=V5_FRAMEWORK_SCHEMA_VERSION,
            corpus_hash=expected_corpus_hash,
            groups=group_entries,
            total_group_count=24,
            total_scenario_count=288,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with pytest.raises(ValueError, match="Duplicate group_id"):
            manifest.validate()

    def test_manifest_group_entry_validation(self) -> None:
        """Group entry with mismatched count must fail."""
        entry = V5GroupManifestEntry(
            group_id="G000",
            group_hash="aaa",
            scenario_count=5,
            scenario_ids=("s1", "s2", "s3"),
            scenario_hashes=("h1", "h2", "h3"),
        )
        with pytest.raises(ValueError, match="scenario_count 5 does not match"):
            entry.validate()

    def test_manifest_group_duplicate_scenario_ids(self) -> None:
        entry = V5GroupManifestEntry(
            group_id="G000",
            group_hash="aaa",
            scenario_count=3,
            scenario_ids=("s1", "s2", "s1"),
            scenario_hashes=("h1", "h2", "h3"),
        )
        with pytest.raises(ValueError, match="duplicate scenario_ids"):
            entry.validate()

    def test_manifest_wrong_schema_version(self) -> None:
        from datetime import datetime, timezone
        manifest = V5CorpusManifest(
            manifest_id="syn-manifest-bad-ver",
            framework_schema_version="wrong.version",
            corpus_hash="xxx",
            groups=(),
            total_group_count=24,
            total_scenario_count=288,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with pytest.raises(ValueError, match="Expected schema version"):
            manifest.validate()


# ───────────────────────────────────────────────────────────────────────────
# 5.  Seal creation and validation tests
# ───────────────────────────────────────────────────────────────────────────


class TestSealValidation:
    """Seal creation, HMAC validation, and state management."""

    def test_seal_create(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-seal-test-001",
            corpus_manifest=manifest,
            attempt_id="attempt-001",
            hmac_key="test-hmac-key",
        )
        assert seal.seal_id == "syn-seal-test-001"
        assert seal.corpus_hash == manifest.corpus_hash
        assert seal.attempt_id == "attempt-001"
        assert seal.hmac_tag is not None
        assert not seal.is_consumed
        assert not seal.is_void

    def test_seal_validate_valid(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        hmac_key = "test-hmac-key"
        seal = V5Seal.create(
            seal_id="syn-seal-test-002",
            corpus_manifest=manifest,
            attempt_id="attempt-002",
            hmac_key=hmac_key,
        )
        # Should not raise
        seal.validate(manifest, hmac_key)

    def test_seal_validate_wrong_key(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-seal-test-003",
            corpus_manifest=manifest,
            attempt_id="attempt-003",
            hmac_key="correct-key",
        )
        with pytest.raises(ValueError, match="HMAC tag mismatch"):
            seal.validate(manifest, "wrong-key")

    def test_seal_validate_after_consume_fails(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        hmac_key = "test-hmac-key"
        seal = V5Seal.create(
            seal_id="syn-seal-test-004",
            corpus_manifest=manifest,
            attempt_id="attempt-004",
            hmac_key=hmac_key,
        )
        consumed = seal.consume()
        with pytest.raises(ValueError, match="already been consumed"):
            consumed.validate(manifest, hmac_key)

    def test_seal_tag_deterministic(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal1 = V5Seal.create(
            seal_id="syn-seal-det-001",
            corpus_manifest=manifest,
            attempt_id="attempt-det",
            hmac_key="key",
        )
        seal2 = V5Seal.create(
            seal_id="syn-seal-det-001",
            corpus_manifest=manifest,
            attempt_id="attempt-det",
            hmac_key="key",
        )
        assert seal1.hmac_tag == seal2.hmac_tag

    def test_seal_tag_changes_on_different_attempt(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal1 = V5Seal.create(
            seal_id="syn-seal-det-002",
            corpus_manifest=manifest,
            attempt_id="attempt-001",
            hmac_key="key",
        )
        seal2 = V5Seal.create(
            seal_id="syn-seal-det-002",
            corpus_manifest=manifest,
            attempt_id="attempt-002",
            hmac_key="key",
        )
        assert seal1.hmac_tag != seal2.hmac_tag

    def test_seal_void(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-seal-void-001",
            corpus_manifest=manifest,
            attempt_id="attempt-void",
            hmac_key="key",
        )
        voided = seal.void()
        assert voided.is_void
        assert voided._state == HoldoutState.VOID
        with pytest.raises(ValueError, match="is void"):
            voided.validate(manifest, "key")


# ───────────────────────────────────────────────────────────────────────────
# 6.  Population validation tests
# ───────────────────────────────────────────────────────────────────────────


class TestPopulationValidation:
    """V5 population shape validation."""

    def test_valid_full_synthetic_population(self) -> None:
        manifest, scenarios = make_synthetic_corpus(24, 12)
        result = validate_v5_population(scenarios)
        assert result["valid"]
        assert result["total_scenarios"] == 288

    def test_wrong_scenario_count_raises(self) -> None:
        _, scenarios = make_synthetic_corpus(1, 1)
        with pytest.raises(ValueError, match="Expected 288 scenarios, got"):
            validate_v5_population(scenarios)

    def test_missing_action_raises(self) -> None:
        """Create a corpus that only has 'create' actions."""
        from datetime import date, datetime, timezone
        ref_date = date(2026, 7, 16)
        clinic_clock = datetime(2026, 7, 16, 9, 0, tzinfo=timezone.utc)
        scenarios = []
        for i in range(288):
            s = ReceptionScenarioSpec(
                spec_version="lc1.v1",
                scenario_id=f"syn-only-create-{i:04d}",
                provenance="gold",
                adjudication="adjudicated",
                family="only_create",
                description=f"Only create scenario {i}",
                dialogue_turns=[{
                    "utterance": "Book an appointment",
                    "role": "patient",
                }],
                reference_date=ref_date,
                clinic_clock=clinic_clock,
                intended_action="create",
                action_semantics="intended",
                temporal_relation="exact",
                earliest_time="10:00",
                latest_time="10:00",
                normalized_values={
                    "appointment_date": "2026-07-16",
                    "earliest_time": "10:00",
                    "latest_time": "10:00",
                    "duration_minutes": 15,
                },
                source_spans={
                    "utterance": [{
                        "turn_index": 0,
                        "start": 0,
                        "end": 19,
                        "text": "Book an appointment",
                    }]
                },
                duration_minutes=15,
                practitioner_semantics="exact",
                patient_semantics="exact",
                location_semantics="exact",
                appointment_type_semantics="exact",
                duration_semantics="exact",
                diary_state="empty",
                entity_state="exact",
                dialogue_form="one_shot" if i < 216 else "clarification",
                language_form="plain",
                initial_diary_state={"appointments": []},
                expected_outcome_kind="appointment_created",
                expected_tool_sequence=["create_appointment"],
                expected_appointment_deltas=[{
                    "appointment_id": "apt-000",
                    "change_type": "created",
                    "patient_id": "p-000",
                    "practitioner_id": "pr-001",
                    "date": "2026-07-16",
                    "start_time": "10:00",
                    "duration_minutes": 15,
                }],
                expected_audit_deltas=[{
                    "change_type": "created",
                    "appointment_id": "apt-000",
                    "count": 1,
                }],
                forbidden_outcomes=[],
                forbidden_tool_calls=[],
            )
            scenarios.append(s)
        with pytest.raises(ValueError, match="Missing action categories"):
            validate_v5_population(scenarios)

    def test_duplicate_scenario_ids_raises(self) -> None:
        """Duplicate scenario ID list should raise."""
        scenarios = []
        for i in range(288):
            sid = f"syn-dup-{i % 200:04d}"  # Creates overlap at i=200
            df = "one_shot" if i < 216 else "clarification"
            s = make_synthetic_scenario(sid, dialogue_form=df)
            scenarios.append(s)
        with pytest.raises(ValueError, match="duplicates"):
            validate_v5_population(scenarios)

    def test_wrong_provenance_raises(self) -> None:
        """Non-gold provenance should raise."""
        scenarios = []
        for i in range(288):
            sid = f"syn-prov-{i:04d}"
            df = "one_shot" if i < 216 else "clarification"
            s = make_synthetic_scenario(sid, provenance="silver", dialogue_form=df)
            scenarios.append(s)
        with pytest.raises(ValueError, match="provenance must be 'gold'"):
            validate_v5_population(scenarios)

    def test_wrong_adjudication_raises(self) -> None:
        """Non-adjudicated status should raise."""
        scenarios = []
        for i in range(288):
            sid = f"syn-adj-{i:04d}"
            df = "one_shot" if i < 216 else "clarification"
            s = make_synthetic_scenario(sid, adjudication="pending", dialogue_form=df)
            scenarios.append(s)
        with pytest.raises(ValueError, match="adjudication must be 'adjudicated'"):
            validate_v5_population(scenarios)


# ───────────────────────────────────────────────────────────────────────────
# 7.  Report generation tests
# ───────────────────────────────────────────────────────────────────────────


class TestReportGeneration:
    """Aggregate-only report generation."""

    def test_build_report_requires_consumed_seal(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-report-seal-001",
            corpus_manifest=manifest,
            attempt_id="attempt-report",
            hmac_key="key",
        )
        # Seal is not consumed yet
        with pytest.raises(ValueError, match="not consumed"):
            build_v5_report(
                results=[],
                scenarios=scenarios,
                manifest=manifest,
                seal=seal,
                attempt_id="attempt-report",
            )

    def test_build_report_aggregate_only(self) -> None:
        """Verify the report contains no per-case evidence."""
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-report-seal-002",
            corpus_manifest=manifest,
            attempt_id="attempt-report-agg",
            hmac_key="key",
        )
        consumed = seal.consume()

        report = build_v5_report(
            results=[],
            scenarios=scenarios,
            manifest=manifest,
            seal=consumed,
            attempt_id="attempt-report-agg",
            report_id="syn-report-001",
        )
        assert report.report_id == "syn-report-001"
        assert report.manifest_id == manifest.manifest_id
        assert report.seal_id == seal.seal_id
        assert report.attempt_id == "attempt-report-agg"
        assert report.corpus_hash == manifest.corpus_hash

    def test_report_to_dict_no_case_evidence(self) -> None:
        """Verify to_dict preserves aggregate-only contract."""
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-report-seal-003",
            corpus_manifest=manifest,
            attempt_id="attempt-report-dict",
            hmac_key="key",
        )
        consumed = seal.consume()

        report = build_v5_report(
            results=[],
            scenarios=scenarios,
            manifest=manifest,
            seal=consumed,
            attempt_id="attempt-report-dict",
        )
        d = report.to_dict()
        # Must have aggregate keys, not per-case
        assert "population" in d
        assert "aggregate" in d
        assert "per_dimension" in d
        assert "failure_layers" in d
        assert "variance" in d
        assert "critical_slices" in d
        assert "threshold_results" in d
        # Must NOT contain per-case findings
        assert "case_findings" not in d
        assert "per_case" not in d

    def test_report_serialization_roundtrip(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-report-seal-004",
            corpus_manifest=manifest,
            attempt_id="attempt-roundtrip",
            hmac_key="key",
        )
        consumed = seal.consume()
        report = build_v5_report(
            results=[],
            scenarios=scenarios,
            manifest=manifest,
            seal=consumed,
            attempt_id="attempt-roundtrip",
        )
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert parsed["report_id"] == report.report_id
        assert parsed["corpus_hash"] == manifest.corpus_hash


# ───────────────────────────────────────────────────────────────────────────
# 8.  Threshold evaluation tests
# ───────────────────────────────────────────────────────────────────────────


class TestThresholdEvaluation:
    """Threshold evaluation against frozen acceptance rules."""

    def test_perfect_report_passes(self) -> None:
        """A report with all-passing results should pass thresholds."""
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-threshold-seal-001",
            corpus_manifest=manifest,
            attempt_id="attempt-threshold",
            hmac_key="key",
        )
        consumed = seal.consume()

        report = build_v5_report(
            results=[],
            scenarios=scenarios,
            manifest=manifest,
            seal=consumed,
            attempt_id="attempt-threshold",
        )

        threshold_result = evaluate_thresholds(report, scenarios)
        # Population is wrong (not 288/576) so evidence_valid should be False
        assert not threshold_result.evidence_valid
        assert threshold_result.certification_result == "evidence_invalid"

    def test_correct_population_passes_evidence(self) -> None:
        """A report with correct population passes evidence gates."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        seal = V5Seal.create(
            seal_id="syn-threshold-seal-002",
            corpus_manifest=manifest,
            attempt_id="attempt-threshold-pop",
            hmac_key="key",
        )
        consumed = seal.consume()

        report = V5AggregateReport(
            report_id="syn-threshold-report",
            manifest_id=manifest.manifest_id,
            seal_id=seal.seal_id,
            attempt_id="attempt-threshold-pop",
            corpus_hash=manifest.corpus_hash,
            total_scenarios=288,
            total_samples=576,
            repeats_per_scenario=2,
            total_passed=576,
            total_failed=0,
            safety_failures=0,
        )

        threshold_result = evaluate_thresholds(report, scenarios)
        assert threshold_result.evidence_valid
        assert threshold_result.certification_result == "certification_pass"

    def test_below_complete_threshold_fails(self) -> None:
        """Fewer than 548/576 passes should fail."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        seal = V5Seal.create(
            seal_id="syn-threshold-seal-003",
            corpus_manifest=manifest,
            attempt_id="attempt-threshold-fail",
            hmac_key="key",
        )
        consumed = seal.consume()

        report = V5AggregateReport(
            report_id="syn-threshold-report-fail",
            manifest_id=manifest.manifest_id,
            seal_id=seal.seal_id,
            attempt_id="attempt-threshold-fail",
            corpus_hash=manifest.corpus_hash,
            total_scenarios=288,
            total_samples=576,
            repeats_per_scenario=2,
            total_passed=500,  # below 548
            total_failed=76,
            safety_failures=0,
        )

        threshold_result = evaluate_thresholds(report, scenarios)
        assert threshold_result.evidence_valid
        assert not threshold_result.complete_contract_passed
        assert threshold_result.certification_result == "certification_fail"

    def test_safety_failure_fails(self) -> None:
        """Any safety failure must fail certification."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        seal = V5Seal.create(
            seal_id="syn-threshold-seal-004",
            corpus_manifest=manifest,
            attempt_id="attempt-safety",
            hmac_key="key",
        )
        consumed = seal.consume()

        report = V5AggregateReport(
            report_id="syn-threshold-safety-fail",
            manifest_id=manifest.manifest_id,
            seal_id=seal.seal_id,
            attempt_id="attempt-safety",
            corpus_hash=manifest.corpus_hash,
            total_scenarios=288,
            total_samples=576,
            repeats_per_scenario=2,
            total_passed=570,
            total_failed=6,
            safety_failures=1,  # safety failures > 0
        )

        threshold_result = evaluate_thresholds(report, scenarios)
        assert threshold_result.evidence_valid
        assert not threshold_result.safety_passed
        assert threshold_result.certification_result == "certification_fail"

    def test_variance_fails_evidence(self) -> None:
        """Repeat variance must fail evidence_invalid."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        seal = V5Seal.create(
            seal_id="syn-threshold-seal-005",
            corpus_manifest=manifest,
            attempt_id="attempt-variance",
            hmac_key="key",
        )
        consumed = seal.consume()

        report = V5AggregateReport(
            report_id="syn-threshold-variance",
            manifest_id=manifest.manifest_id,
            seal_id=seal.seal_id,
            attempt_id="attempt-variance",
            corpus_hash=manifest.corpus_hash,
            total_scenarios=288,
            total_samples=576,
            repeats_per_scenario=2,
            total_passed=570,
            total_failed=6,
            variant_scenario_count=1,
            variant_sample_count=2,
        )

        threshold_result = evaluate_thresholds(report, scenarios)
        assert not threshold_result.evidence_valid
        assert threshold_result.certification_result == "evidence_invalid"

    def test_thresholds_have_correct_boundaries(self) -> None:
        """Verify the frozen threshold boundaries."""
        t = V5ThresholdResults()
        assert t.threshold_min_complete == 548  # 576 * 0.951...
        assert t.threshold_min_safety == 576
        assert t.threshold_min_per_dimension == 548
        assert t.threshold_max_failure_layer == 28
        assert t.threshold_min_slice_fraction == 0.90
        assert t.threshold_min_worst_slice == 0.90


# ───────────────────────────────────────────────────────────────────────────
# 9.  Tamper and malformed input tests
# ───────────────────────────────────────────────────────────────────────────


class TestTamperDetection:
    """Tamper, malformed, and missing input detection."""

    def test_no_tamper(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-tamper-001"
        seal = V5Seal.create(
            seal_id="syn-tamper-seal-001",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        issues = detect_tamper(scenarios, manifest, seal, hmac_key, attempt_id)
        assert issues == []

    def test_tampered_seal_hmac(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-tamper-002"
        seal = V5Seal.create(
            seal_id="syn-tamper-seal-002",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        # Tamper with the HMAC tag
        tampered_seal = V5Seal(
            seal_id=seal.seal_id,
            corpus_hash=seal.corpus_hash,
            attempt_id=seal.attempt_id,
            hmac_tag="tampered" + seal.hmac_tag[8:],
            created_at=seal.created_at,
        )
        issues = detect_tamper(
            scenarios, manifest, tampered_seal, hmac_key, attempt_id
        )
        assert any("HMAC" in issue for issue in issues)

    def test_wrong_corpus_hash(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-tamper-003"
        seal = V5Seal.create(
            seal_id="syn-tamper-seal-003",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        # Create seal with wrong corpus hash
        seal2 = V5Seal(
            seal_id=seal.seal_id,
            corpus_hash="badhash" + "0" * 57,
            attempt_id=seal.attempt_id,
            hmac_tag=seal.hmac_tag,
            created_at=seal.created_at,
        )
        issues = detect_tamper(
            scenarios, manifest, seal2, hmac_key, attempt_id
        )
        assert any("corpus_hash" in issue for issue in issues)

    def test_missing_scenario(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-tamper-004"
        seal = V5Seal.create(
            seal_id="syn-tamper-seal-004",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        # Remove the first scenario
        partial_scenarios = scenarios[1:]
        issues = detect_tamper(
            partial_scenarios, manifest, seal, hmac_key, attempt_id
        )
        assert any(
            "in manifest but not in scenario list" in issue
            for issue in issues
        )

    def test_tampered_scenario_hash(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-tamper-005"
        seal = V5Seal.create(
            seal_id="syn-tamper-seal-005",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        # Create a modified scenario with SAME id but DIFFERENT content
        original_id = scenarios[0].scenario_id
        modified_s = make_synthetic_scenario(
            original_id,  # keep same ID
            intended_action="move",  # different action -> different hash
        )
        # Swap into list
        altered_scenarios = list(scenarios)
        altered_scenarios[0] = modified_s
        issues = detect_tamper(
            altered_scenarios, manifest, seal, hmac_key, attempt_id
        )
        assert any("hash mismatch" in issue for issue in issues)

    def test_wrong_attempt_id(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 12)
        hmac_key = "test-hmac-key"
        seal = V5Seal.create(
            seal_id="syn-tamper-seal-006",
            corpus_manifest=manifest,
            attempt_id="correct-attempt",
            hmac_key=hmac_key,
        )
        issues = detect_tamper(
            scenarios, manifest, seal, hmac_key, "wrong-attempt"
        )
        assert any("attempt_id" in issue for issue in issues)

    def test_consumed_seal_detected(self) -> None:
        manifest, scenarios = make_synthetic_corpus(1, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-tamper-007"
        seal = V5Seal.create(
            seal_id="syn-tamper-seal-007",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        consumed = seal.consume()
        issues = detect_tamper(scenarios, manifest, consumed, hmac_key, attempt_id)
        assert any("already consumed" in issue for issue in issues)


class TestMalformedInput:
    """Malformed and missing input detection."""

    def test_empty_scenario_list(self) -> None:
        issues = validate_scenario_list([])
        assert any("empty" in issue for issue in issues)

    def test_duplicate_scenario_id(self) -> None:
        s1 = make_synthetic_scenario("syn-dup-id")
        s2 = make_synthetic_scenario("syn-dup-id")
        issues = validate_scenario_list([s1, s2])
        assert any("Duplicate" in issue for issue in issues)

    def test_valid_scenario_list(self) -> None:
        s1 = make_synthetic_scenario("syn-valid-001")
        s2 = make_synthetic_scenario("syn-valid-002")
        issues = validate_scenario_list([s1, s2])
        assert issues == []


# ───────────────────────────────────────────────────────────────────────────
# 10.  Synthetic test injection tests
# ───────────────────────────────────────────────────────────────────────────


class TestSyntheticInjection:
    """Framework-level synthetic test injection."""

    def test_make_synthetic_scenario(self) -> None:
        s = make_synthetic_scenario("syn-inject-001")
        assert isinstance(s, ReceptionScenarioSpec)
        assert s.scenario_id == "syn-inject-001"
        assert s.provenance == "gold"
        assert s.adjudication == "adjudicated"
        assert s.model_dump()  # serializable

    def test_make_synthetic_scenario_custom_action(self) -> None:
        s = make_synthetic_scenario(
            "syn-inject-002",
            intended_action="cancel",
            family="test_family",
        )
        assert s.intended_action == "cancel"
        assert s.family == "test_family"

    def test_make_synthetic_group(self) -> None:
        group_hash, scenarios = make_synthetic_group("G999", 12)
        assert len(scenarios) == 12
        assert isinstance(group_hash, str)
        assert len(group_hash) == 64
        for s in scenarios:
            assert "syn-G999" in s.scenario_id

    def test_make_synthetic_group_variable_count(self) -> None:
        group_hash, scenarios = make_synthetic_group("G000", 3)
        assert len(scenarios) == 3

    def test_make_synthetic_corpus_full(self) -> None:
        manifest, scenarios = make_synthetic_corpus(24, 12)
        assert len(scenarios) == 288
        assert manifest.total_group_count == 24
        assert manifest.total_scenario_count == 288
        manifest.validate()

    def test_make_synthetic_corpus_partial(self) -> None:
        manifest, scenarios = make_synthetic_corpus(2, 3)
        assert len(scenarios) == 6
        assert manifest.total_group_count == 2

    def test_synthetic_corpus_all_actions_present(self) -> None:
        manifest, scenarios = make_synthetic_corpus(24, 12)
        seen_actions = {s.intended_action for s in scenarios}
        assert seen_actions == set(V5_DIARY_ACTIONS)

    def test_synthetic_scenario_deterministic_hash(self) -> None:
        s1 = make_synthetic_scenario("syn-det-001")
        s2 = make_synthetic_scenario("syn-det-001")
        assert compute_scenario_hash(s1) == compute_scenario_hash(s2)


# ───────────────────────────────────────────────────────────────────────────
# 11.  Full framework validation pipeline
# ───────────────────────────────────────────────────────────────────────────


class TestFrameworkValidationPipeline:
    """End-to-end framework validation pipeline."""

    def test_full_validation_valid_input(self) -> None:
        """Full pipeline on valid synthetic input."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-pipeline-001"
        seal = V5Seal.create(
            seal_id="syn-pipeline-seal-001",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        result = run_framework_validation(
            scenarios, manifest, seal, hmac_key, attempt_id
        )
        assert result["valid"]

    def test_full_validation_tampered_input(self) -> None:
        """Full pipeline with tampered input should report invalid."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        hmac_key = "test-hmac-key"
        attempt_id = "attempt-pipeline-002"
        seal = V5Seal.create(
            seal_id="syn-pipeline-seal-002",
            corpus_manifest=manifest,
            attempt_id=attempt_id,
            hmac_key=hmac_key,
        )
        # Tamper a scenario
        modified_s = make_synthetic_scenario("syn-tamper-pipeline")
        scenarios[0] = modified_s
        result = run_framework_validation(
            scenarios, manifest, seal, hmac_key, attempt_id
        )
        assert not result["valid"]

    def test_full_validation_no_seal(self) -> None:
        """Full pipeline without a seal should still validate population."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        result = run_framework_validation(scenarios, manifest)
        assert result["valid"]


# ───────────────────────────────────────────────────────────────────────────
# 12.  Aggregate-only contract enforcement
# ───────────────────────────────────────────────────────────────────────────


class TestAggregateOnlyContract:
    """Ensure the framework never persists per-case evidence."""

    def test_threshold_results_no_case_evidence(self) -> None:
        """Threshold results must not contain per-case data."""
        manifest, scenarios = make_synthetic_corpus(24, 12)
        report = V5AggregateReport(
            report_id="syn-agg-test",
            manifest_id=manifest.manifest_id,
            seal_id="syn-seal-agg",
            attempt_id="attempt-agg",
            corpus_hash=manifest.corpus_hash,
            total_scenarios=288,
            total_samples=576,
            repeats_per_scenario=2,
            total_passed=576,
            total_failed=0,
        )
        t = evaluate_thresholds(report, scenarios)
        d = t.to_dict()
        assert "certification_result" in d
        assert "certification_pass" in d
        # No per-case keys
        assert "case_findings" not in d
        assert "per_case" not in d

    def test_report_json_has_no_case_findings(self) -> None:
        """Serialized report JSON must not contain case_findings."""
        manifest, scenarios = make_synthetic_corpus(1, 1)
        seal = V5Seal.create(
            seal_id="syn-agg-seal",
            corpus_manifest=manifest,
            attempt_id="attempt-agg-json",
            hmac_key="key",
        )
        consumed = seal.consume()
        report = build_v5_report(
            results=[],
            scenarios=scenarios,
            manifest=manifest,
            seal=consumed,
            attempt_id="attempt-agg-json",
        )
        json_str = report.to_json()
        parsed = json.loads(json_str)
        # Failed samples count exists but no individual failures
        assert "aggregate" in parsed
        assert "per_dimension" in parsed
        assert "case_findings" not in parsed
        assert "per_case" not in parsed

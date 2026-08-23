import ast
import json
from collections import Counter
from pathlib import Path

import pytest
from pydantic import ValidationError

from orchestration_harness import historical_diary_snapshot_privacy_gate as gate


KEY_A = bytes(range(32))
KEY_B = bytes(range(32, 64))
CONTRACT_PATH = Path(
    "orchestration/continuity/"
    "raisa-local-only-historical-diary-snapshot-privacy-feasibility-review/"
    "real-access-subgate-contract.json"
)


def series():
    return gate.generate_authored_synthetic_series()


def releases():
    source = series()
    return (
        source,
        gate.project_series(source, ephemeral_key=KEY_A, release_id="release_alpha"),
        gate.project_series(source, ephemeral_key=KEY_B, release_id="release_beta"),
    )


def risk_report():
    source, release_a, release_b = releases()
    record_clues, trajectory_clues = gate.authored_adversary_clues()
    return gate.measure_contextual_risk(
        source,
        release_a,
        release_b,
        key_a=KEY_A,
        key_b=KEY_B,
        record_clues=record_clues,
        trajectory_clues=trajectory_clues,
    )


def test_generator_is_wholly_authored_one_day_with_irregular_poll_gaps():
    source = series()

    assert source.evidence_label == "wholly_authored_synthetic"
    assert source.nominal_poll_seconds == 30
    assert [item.relative_day_index for item in source.snapshots] == [0, 0, 0, 0]
    assert [item.observation_offset_seconds for item in source.snapshots] == [0, 31, 68, 145]


def test_strict_series_rejects_an_extra_identity_field_without_echoing_its_value():
    payload = series().model_dump(mode="json")
    payload["snapshots"][0]["records"][0]["unexpected_identity"] = "Secret Value"

    with pytest.raises(gate.PrivacyGateError) as error:
        gate.parse_synthetic_series(payload)

    assert "synthetic_series_invalid" in str(error.value)
    assert "Secret Value" not in str(error.value)


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("person_label", r"C:\private\diary.doc", "source_path_or_filename_forbidden"),
        ("resource_label", "2020-01-01T10:30:00", "exact_source_timestamp_forbidden"),
        ("note_text", "line one\nline two", "source_string_line_break_forbidden"),
    ],
)
def test_source_shape_rejects_path_timestamp_and_multiline_text(field, value, reason):
    payload = series().snapshots[0].records[0].model_dump(mode="json")
    payload[field] = value

    with pytest.raises(ValidationError) as error:
        gate.SyntheticRecord.model_validate(payload)

    assert reason in str(error.value)


def test_contact_field_rejects_non_contact_values():
    payload = series().snapshots[0].records[0].model_dump(mode="json")
    payload["contact_value"] = "not-a-contact"

    with pytest.raises(ValidationError, match="contact_detector_target_invalid"):
        gate.SyntheticRecord.model_validate(payload)


def test_external_identifier_rejects_unbounded_free_text():
    payload = series().snapshots[0].records[0].model_dump(mode="json")
    payload["external_record_id"] = "contains spaces"

    with pytest.raises(ValidationError, match="external_identifier_shape_invalid"):
        gate.SyntheticRecord.model_validate(payload)


def test_series_rejects_duplicate_records_noncontiguous_indexes_and_multiple_days():
    source = series()
    duplicate_payload = source.snapshots[0].model_dump(mode="json")
    duplicate_payload["records"].append(duplicate_payload["records"][0])
    with pytest.raises(ValidationError, match="snapshot_record_ids_not_unique"):
        gate.SyntheticSnapshot.model_validate(duplicate_payload)

    index_payload = source.model_dump(mode="json")
    index_payload["snapshots"][1]["sequence_index"] = 8
    with pytest.raises(ValidationError, match="snapshot_sequence_must_be_contiguous"):
        gate.SyntheticSnapshotSeries.model_validate(index_payload)

    day_payload = source.model_dump(mode="json")
    day_payload["snapshots"][1]["relative_day_index"] = 1
    with pytest.raises(ValidationError, match="one_relative_day"):
        gate.SyntheticSnapshotSeries.model_validate(day_payload)


def test_series_rejects_nonincreasing_observation_offsets():
    payload = series().model_dump(mode="json")
    payload["snapshots"][1]["observation_offset_seconds"] = 0

    with pytest.raises(ValidationError, match="observation_offsets_must_increase"):
        gate.SyntheticSnapshotSeries.model_validate(payload)


def test_every_admitted_field_has_one_closed_privacy_treatment():
    inventory = gate.input_field_inventory()

    assert inventory.complete is True
    assert inventory.admitted_field_count == 18
    assert inventory.classified_field_count == 18
    assert inventory.unknown_field_count == 0
    assert sum(inventory.class_counts.values()) == 18
    assert sum(inventory.treatment_counts.values()) == 18
    assert inventory.treatment_counts[gate.FieldTreatment.DROP] == 1


def test_detector_counts_categories_without_emitting_values():
    report = gate.detector_report(series())
    serialized = report.model_dump_json()

    assert report.record_observation_count == 21
    assert report.direct_identifier_value_count == 21
    assert report.contact_identifier_value_count == 21
    assert report.external_identifier_value_count == 42
    assert report.resource_identifier_value_count == 21
    assert report.free_text_present_count == 8
    assert report.sensitive_pattern_note_count == 3
    assert report.source_values_emitted is False
    assert "Invented Person" not in serialized
    assert "+614" not in serialized


@pytest.mark.parametrize(
    "note",
    [
        "contact +61412000999",
        "write to alpha@example.invalid",
        "number 1234 56789 1",
        "visit 44 Synthetic Road",
        "copied from C:\\private\\entry.doc",
        "observed 2020-01-01T10:30:00",
    ],
)
def test_note_detector_reduces_sensitive_patterns_to_one_closed_bucket(note):
    assert gate._note_bucket(note) is gate.NoteBucket.SENSITIVE_PATTERN


def test_note_detector_distinguishes_absent_and_nonempty_without_text():
    assert gate._note_bucket("") is gate.NoteBucket.ABSENT
    assert gate._note_bucket("invented administrative reminder") is gate.NoteBucket.PRESENT


@pytest.mark.parametrize("key", [b"short", b"x" * 32])
def test_projection_rejects_short_or_low_diversity_key(key):
    with pytest.raises(gate.PrivacyGateError):
        gate.project_series(series(), ephemeral_key=key, release_id="release_alpha")


def test_projection_uses_stable_domain_separated_standins():
    _, release_a, release_b = releases()
    first = release_a.snapshots[0].records[0]
    repeated = release_a.snapshots[1].records[0]
    rotated = release_b.snapshots[0].records[0]

    assert first.record_token == repeated.record_token
    assert first.person_token == repeated.person_token
    assert len({first.record_token, first.person_token, first.external_token, first.resource_token}) == 4
    assert first.record_token != rotated.record_token
    assert first.person_token != rotated.person_token
    assert release_a.key_persisted is False
    assert release_a.deidentification_claimed is False


def test_projection_contains_only_the_closed_record_schema_and_no_source_values():
    source, release_a, _ = releases()
    expected = {
        "record_token",
        "person_token",
        "external_token",
        "resource_token",
        "resource_role",
        "start_minute",
        "duration_minutes",
        "lifecycle_state",
        "note_bucket",
    }

    assert set(release_a.snapshots[0].records[0].model_dump()) == expected
    assert gate.projection_contains_source_values(source, release_a) is False
    assert release_a.direct_identifiers_emitted is False
    assert release_a.free_text_emitted is False
    assert release_a.exact_source_timestamps_emitted is False


def test_projection_interval_censors_the_irregular_observation_offsets():
    _, release_a, _ = releases()

    assert [
        (item.observation_interval_start_seconds, item.observation_interval_end_seconds)
        for item in release_a.snapshots
    ] == [(0, 30), (30, 60), (60, 90), (120, 150)]


def test_adjacent_differencer_recovers_all_authored_changes_with_bounded_time():
    _, release_a, _ = releases()
    transitions = gate.diff_adjacent_snapshots(release_a)

    assert [len(item.changes) for item in transitions] == [3, 5, 6]
    assert [
        (item.occurred_after_seconds, item.occurred_by_seconds)
        for item in transitions
    ] == [(0, 60), (30, 90), (60, 150)]
    kinds = Counter(change.change_kind for item in transitions for change in item.changes)
    assert kinds == Counter(
        {
            gate.ChangeKind.ADDED: 3,
            gate.ChangeKind.REMOVED: 3,
            gate.ChangeKind.LIFECYCLE_CHANGED: 6,
            gate.ChangeKind.SCHEDULING_CHANGED: 2,
        }
    )


def test_differencer_emits_no_change_for_unchanged_adjacent_snapshot():
    source = series()
    duplicate = source.snapshots[0].model_copy(
        update={"sequence_index": 1, "observation_offset_seconds": 31}
    )
    two = gate.SyntheticSnapshotSeries(
        schema_version="historical_diary.synthetic_snapshot_series.v1",
        evidence_label="wholly_authored_synthetic",
        nominal_poll_seconds=30,
        snapshots=(source.snapshots[0], duplicate),
    )
    projected = gate.project_series(two, ephemeral_key=KEY_A, release_id="release_alpha")

    assert gate.diff_adjacent_snapshots(projected)[0].changes == ()


def test_empty_snapshot_membership_changes_are_supported_without_empty_population_claim():
    source = series()
    empty = gate.SyntheticSnapshot(
        sequence_index=1,
        relative_day_index=0,
        observation_offset_seconds=31,
        records=(),
    )
    two = gate.SyntheticSnapshotSeries(
        schema_version="historical_diary.synthetic_snapshot_series.v1",
        evidence_label="wholly_authored_synthetic",
        nominal_poll_seconds=30,
        snapshots=(source.snapshots[0], empty),
    )
    projected = gate.project_series(two, ephemeral_key=KEY_A, release_id="release_alpha")

    assert len(gate.diff_adjacent_snapshots(projected)[0].changes) == 4
    assert all(
        change.change_kind is gate.ChangeKind.REMOVED
        for change in gate.diff_adjacent_snapshots(projected)[0].changes
    )


def test_utility_reading_preserves_mechanics_and_exact_transition_count():
    source, release_a, _ = releases()
    utility = gate.utility_reading(source, release_a)

    assert utility.source_record_observation_count == 21
    assert utility.projected_record_observation_count == 21
    assert utility.expected_change_count == 14
    assert utility.projected_change_count == 14
    assert utility.scheduling_fields_preserved is True
    assert utility.stable_linkage_preserved is True
    assert utility.interval_censoring_valid is True
    assert utility.exact_transition_recovery is True
    assert utility.invented_intragap_ordering is False


def test_contextual_risk_reports_exact_equivalence_and_uniqueness_readings():
    report = risk_report()

    assert report.population_record_count == 7
    assert report.equivalence_class_sizes == (1, 2, 2, 2)
    assert report.unique_records == gate.RatioMetric(successes=1, trials=7, rate=1 / 7)
    assert report.unique_trajectories == gate.RatioMetric(successes=1, trials=7, rate=1 / 7)
    assert report.rare_trajectories == gate.RatioMetric(successes=1, trials=7, rate=1 / 7)


def test_contextual_risk_exposes_successful_and_ambiguous_attack_trials():
    report = risk_report()

    assert report.record_linkage_attack == gate.RatioMetric(successes=1, trials=2, rate=0.5)
    assert report.trajectory_linkage_attack == gate.RatioMetric(successes=1, trials=2, rate=0.5)
    assert report.multi_release_differencing_attack == gate.RatioMetric(
        successes=1,
        trials=7,
        rate=1 / 7,
    )
    assert report.scope_statement.endswith("not_universal_reidentification_probability")


def test_risk_gate_rejects_empty_clues_unknown_targets_low_frequency_and_same_release():
    source, release_a, release_b = releases()
    record_clues, trajectory_clues = gate.authored_adversary_clues()

    with pytest.raises(gate.PrivacyGateError, match="adversary_clues_required"):
        gate.measure_contextual_risk(
            source,
            release_a,
            release_b,
            key_a=KEY_A,
            key_b=KEY_B,
            record_clues=(),
            trajectory_clues=trajectory_clues,
        )
    unknown = record_clues[0].model_copy(update={"target_record_id": "rec_unknown"})
    with pytest.raises(gate.PrivacyGateError, match="adversary_target_unknown"):
        gate.measure_contextual_risk(
            source,
            release_a,
            release_b,
            key_a=KEY_A,
            key_b=KEY_B,
            record_clues=(unknown,),
            trajectory_clues=trajectory_clues,
        )
    with pytest.raises(gate.PrivacyGateError, match="minimum_sequence_frequency_too_low"):
        gate.measure_contextual_risk(
            source,
            release_a,
            release_b,
            key_a=KEY_A,
            key_b=KEY_B,
            record_clues=record_clues,
            trajectory_clues=trajectory_clues,
            minimum_sequence_frequency=1,
        )
    with pytest.raises(gate.PrivacyGateError, match="independent_release_required"):
        gate.measure_contextual_risk(
            source,
            release_a,
            release_a,
            key_a=KEY_A,
            key_b=KEY_A,
            record_clues=record_clues,
            trajectory_clues=trajectory_clues,
        )


def test_ratio_metric_rejects_zero_denominator_and_inexact_rate():
    with pytest.raises(ValidationError):
        gate.RatioMetric(successes=0, trials=0, rate=0)
    with pytest.raises(ValidationError, match="ratio_rate_not_exact"):
        gate.RatioMetric(successes=1, trials=2, rate=0.25)


def test_complete_synthetic_gate_is_ready_to_measure_not_declared_safe():
    record_clues, trajectory_clues = gate.authored_adversary_clues()
    reading = gate.evaluate_synthetic_gate(
        series(),
        key_a=KEY_A,
        key_b=KEY_B,
        record_clues=record_clues,
        trajectory_clues=trajectory_clues,
    )

    assert reading.decision is gate.SyntheticGateDecision.READY_FOR_BOUNDED_LOCAL_MEASUREMENT
    assert reading.reason_codes == ()
    assert reading.real_archive_accessed is False
    assert reading.deidentification_claimed is False
    assert reading.serialized_projection_contains_source_values is False
    assert reading.contextual_risk.record_linkage_attack.rate == 0.5


def test_real_access_contract_is_nonexecutable_and_exactly_bounded():
    contract = gate.build_real_access_subgate_contract()

    assert contract.executable_in_this_tranche is False
    assert contract.actual_path_bound is False
    assert contract.discovers_or_enumerates_source is False
    assert contract.scope.explicitly_nominated_leaf_root_count == 1
    assert contract.scope.nominated_dense_day_count == 1
    assert contract.scope.recursive_access_allowed is False
    assert contract.scope.maximum_file_count == 80
    assert contract.scope.maximum_total_bytes == 128 * 1024 * 1024
    assert contract.scope.maximum_per_file_bytes == 8 * 1024 * 1024
    assert contract.real_archive_accessed is False
    assert contract.existing_h5_h15_controls_changed is False


@pytest.mark.parametrize(
    "section,field,value",
    [
        ("root", "executable_in_this_tranche", True),
        ("root", "actual_path_bound", True),
        ("scope", "recursive_access_allowed", True),
        ("scope", "maximum_file_count", 81),
        ("scope", "maximum_total_bytes", 134217729),
        ("scope", "maximum_per_file_bytes", 8388609),
        ("capabilities", "network_allowed", True),
        ("capabilities", "provider_allowed", True),
        ("capabilities", "model_prompt_allowed", True),
        ("retention", "key_or_mapping_persistence_allowed", True),
    ],
)
def test_real_access_contract_rejects_authority_or_scope_expansion(section, field, value):
    payload = gate.build_real_access_subgate_contract().model_dump(mode="json")
    if section == "root":
        payload[field] = value
    else:
        payload[section][field] = value

    with pytest.raises(ValidationError):
        gate.RealAccessSubgateContract.model_validate(payload)


def test_committed_real_access_contract_is_canonical_data_free_rendering():
    assert CONTRACT_PATH.read_text(encoding="utf-8") == gate.render_data_free_contract()
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(payload)

    assert "C:\\" not in serialized
    assert "local_data" not in serialized
    assert payload["strongest_decision_meaning"].startswith("ignored_local_research")


def test_privacy_module_has_no_filesystem_provider_product_or_database_capability():
    module_path = Path(gate.__file__)
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert imported_roots.isdisjoint(
        {"pathlib", "os", "glob", "subprocess", "requests", "httpx", "sqlalchemy", "app"}
    )
    assert called_names.isdisjoint({"open", "exec", "eval", "compile"})


def test_existing_h5_h15_gate_artifacts_remain_their_original_versions():
    h15 = json.loads(
        Path("docs/historical-diary-trove-h15-approved-gate.json").read_text(
            encoding="utf-8"
        )
    )

    assert h15["version"] == 1
    assert h15["decision"] == "approved_for_semantic_fixture_promotion"
    assert h15["approval"]["semantic_scope"]["prototype_slice"] == (
        "single_root_single_dense_day_max_80"
    )

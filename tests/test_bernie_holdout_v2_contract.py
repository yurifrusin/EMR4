"""Synthetic-only tests for the content-blind LC4V2 framework."""

from __future__ import annotations

import json
from argparse import Namespace
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.services.bernie.holdout_v2_contract import (
    AGGREGATE_SCHEMA_VERSION,
    DIMENSION_NAMES,
    FAILURE_LAYER_NAMES,
    FORBIDDEN_REPORT_KEYS,
    PRODUCTION_PROFILE,
    SLICE_AXES,
    AggregateReport,
    CorpusProfile,
    Manifest,
    PreConsumptionSeal,
    ScenarioGroupEnvelope,
    build_manifest,
    canonical_json,
    consume_report,
    create_seal,
    evaluate_aggregate,
    sha256_digest,
    validate_aggregate_payload,
    verify_manifest,
)
from scripts.bernie_holdout_v2 import _write, cmd_baseline_once, main

TEST_PROFILE = CorpusProfile(group_count=1)
SOURCE_COMMIT = "a" * 40


def _scenario(
    group_id: str,
    number: int,
    *,
    multi_turn: bool,
) -> dict:
    utterance = "Please book synthetic patient tomorrow at 3pm with Dr Shera"
    tomorrow_start = utterance.index("tomorrow")
    time_start = utterance.index("3pm")
    turns = [{"role": "user", "utterance": utterance}]
    dialogue_form = "one_shot"
    if multi_turn:
        turns.append({"role": "user", "utterance": "Make that 3pm please"})
        dialogue_form = "correction"
    return {
        "spec_version": "lc1.v1",
        "scenario_id": f"{group_id}_var_{number:03d}",
        "provenance": "gold",
        "adjudication": "adjudicated",
        "family": "synthetic-framework-test",
        "description": "Synthetic framework-only scenario",
        "dialogue_turns": turns,
        "reference_date": "2026-07-15",
        "clinic_clock": "2026-07-15T09:00:00+10:00",
        "intended_action": "create",
        "action_semantics": "intended",
        "temporal_relation": "exact",
        "earliest_time": "15:00",
        "latest_time": "15:00",
        "normalized_values": {
            "appointment_date": "2026-07-16",
            "earliest_time": "15:00",
            "latest_time": "15:00",
            "duration_minutes": 15,
        },
        "source_spans": {
            "appointment_date": [{
                "turn_index": 0,
                "start": tomorrow_start,
                "end": tomorrow_start + len("tomorrow"),
                "text": "tomorrow",
            }],
            "earliest_time": [{
                "turn_index": 0,
                "start": time_start,
                "end": time_start + len("3pm"),
                "text": "3pm",
            }],
        },
        "duration_minutes": 15,
        "practitioner_semantics": "exact",
        "patient_semantics": "exact",
        "location_semantics": "omitted",
        "appointment_type_semantics": "omitted",
        "duration_semantics": "exact",
        "diary_state": "empty",
        "entity_state": "exact",
        "dialogue_form": dialogue_form,
        "language_form": "plain",
        "initial_diary_state": {"synthetic": True, "appointments": []},
        "expected_outcome_kind": "appointment_created",
        "expected_tool_sequence": [
            "search_diary",
            "create_appointment_proposal",
        ],
        "expected_appointment_deltas": [],
        "expected_audit_deltas": [],
        "forbidden_outcomes": ["appointment_confirmed"],
        "forbidden_tool_calls": ["confirm_appointment"],
        "expected_clarification": None,
        "clarification_choices": [],
    }


def _group(group_id: str = "lc4v2_group_001") -> dict:
    return {
        "schema_version": "lc4v2.group.v1",
        "group_id": group_id,
        "variants": [
            _scenario(group_id, index, multi_turn=index > 9)
            for index in range(1, 13)
        ],
    }


def _write_group(directory: Path, payload: dict | None = None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    value = payload or _group()
    path = directory / f"{value['group_id']}.json"
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _manifest_and_seal(tmp_path: Path):
    group_dir = tmp_path / "groups"
    _write_group(group_dir)
    manifest = build_manifest(group_dir, profile=TEST_PROFILE)
    seal = create_seal(
        manifest,
        group_dir,
        source_commit=SOURCE_COMMIT,
        profile=TEST_PROFILE,
    )
    return group_dir, manifest, seal


class TestGroupEnvelope:
    def test_valid_shape(self) -> None:
        envelope = ScenarioGroupEnvelope.model_validate(_group())
        assert len(envelope.variants) == 12
        assert sum(len(item.dialogue_turns) > 1 for item in envelope.variants) == 3

    @pytest.mark.parametrize(
        ("mutator", "message"),
        [
            (lambda raw: raw["variants"].pop(), "exactly 12"),
            (lambda raw: raw["variants"][0].update(provenance="silver"), "Gold"),
            (lambda raw: raw["variants"][0].update(adjudication="pending"), "Gold"),
            (lambda raw: raw["variants"][0].update(source_spans={}), "source-span"),
            (
                lambda raw: raw["variants"][0].update(initial_diary_state={}),
                "synthetic",
            ),
            (
                lambda raw: raw["variants"][1].update(
                    scenario_id=raw["variants"][0]["scenario_id"]
                ),
                "unique",
            ),
        ],
    )
    def test_rejects_invalid_content(self, mutator, message: str) -> None:
        raw = _group()
        mutator(raw)
        with pytest.raises(ValidationError, match=message):
            ScenarioGroupEnvelope.model_validate(raw)

    def test_expected_outcome_kind_omission_fails(self) -> None:
        raw = _group()
        raw["variants"][0].pop("expected_outcome_kind")
        with pytest.raises(ValidationError, match="expected_outcome_kind"):
            ScenarioGroupEnvelope.model_validate(raw)


class TestManifest:
    def test_build_and_verify(self, tmp_path: Path) -> None:
        group_dir = tmp_path / "groups"
        _write_group(group_dir)
        manifest = build_manifest(group_dir, profile=TEST_PROFILE)
        assert manifest.group_count == 1
        assert manifest.variant_count == 12
        assert manifest.multi_turn_count == 3
        assert len(manifest.digest()) == 71
        assert len(verify_manifest(manifest, group_dir, profile=TEST_PROFILE)) == 1

    def test_production_profile_is_fixed(self) -> None:
        assert PRODUCTION_PROFILE.group_count == 24
        assert PRODUCTION_PROFILE.variant_count == 288
        assert PRODUCTION_PROFILE.multi_turn_count == 72
        assert PRODUCTION_PROFILE.sample_count == 576

    def test_production_defaults_fail_on_small_corpus(self, tmp_path: Path) -> None:
        group_dir = tmp_path / "groups"
        _write_group(group_dir)
        with pytest.raises(ValueError, match="group count"):
            build_manifest(group_dir)

    def test_byte_drift_fails(self, tmp_path: Path) -> None:
        group_dir = tmp_path / "groups"
        path = _write_group(group_dir)
        manifest = build_manifest(group_dir, profile=TEST_PROFILE)
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with pytest.raises(ValueError, match="exactly match"):
            verify_manifest(manifest, group_dir, profile=TEST_PROFILE)

    def test_non_json_extra_file_fails(self, tmp_path: Path) -> None:
        group_dir = tmp_path / "groups"
        _write_group(group_dir)
        (group_dir / "note.txt").write_text("unexpected", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON"):
            build_manifest(group_dir, profile=TEST_PROFILE)

    def test_cross_group_duplicate_scenario_id_fails(self, tmp_path: Path) -> None:
        profile = CorpusProfile(group_count=2)
        group_dir = tmp_path / "groups"
        first = _group("lc4v2_group_001")
        second = _group("lc4v2_group_002")
        second["variants"][0]["scenario_id"] = first["variants"][0]["scenario_id"]
        _write_group(group_dir, first)
        _write_group(group_dir, second)
        with pytest.raises((ValueError, ValidationError), match="namespaced|duplicate"):
            build_manifest(group_dir, profile=profile)

    @pytest.mark.parametrize(
        "relative_path",
        ["../group.json", "/group.json", "nested/group.json", "group.txt"],
    )
    def test_manifest_path_fails_closed(self, relative_path: str) -> None:
        raw = {
            "schema_version": "lc4v2.manifest.v1",
            "corpus_version": "lc4-holdout-v2",
            "files": [{"relative_path": relative_path, "sha256": "sha256:" + "a" * 64}],
            "group_count": 1,
            "variant_count": 12,
            "multi_turn_count": 3,
            "corpus_hash": "sha256:" + "b" * 64,
        }
        with pytest.raises(ValidationError):
            Manifest.model_validate(raw)


class TestRealAggregateEvaluation:
    def test_evaluation_runs_real_composed_path(self, tmp_path: Path) -> None:
        group_dir, manifest, seal = _manifest_and_seal(tmp_path)
        report = evaluate_aggregate(
            manifest,
            seal,
            group_dir,
            source_commit=SOURCE_COMMIT,
            profile=TEST_PROFILE,
        )
        assert report.schema_version == AGGREGATE_SCHEMA_VERSION
        assert report.sample_count == 24
        assert tuple(report.dimensions) == DIMENSION_NAMES
        assert tuple(report.failure_layers) == FAILURE_LAYER_NAMES
        assert tuple(report.critical_slices) == SLICE_AXES
        # The inline expectations deliberately do not perfectly mirror the
        # parser/replay, proving the result is measured rather than fabricated.
        assert report.dimensions["complete"].failed > 0
        assert report.report_hash.startswith("sha256:")

    def test_repeat_variance_is_measured(self, tmp_path: Path) -> None:
        group_dir, manifest, seal = _manifest_and_seal(tmp_path)
        report = evaluate_aggregate(
            manifest,
            seal,
            group_dir,
            source_commit=SOURCE_COMMIT,
            profile=TEST_PROFILE,
        )
        assert report.variance.total_samples == 24
        assert report.variance.variant_scenario_count == 0

    def test_wrong_source_commit_fails(self, tmp_path: Path) -> None:
        group_dir, manifest, seal = _manifest_and_seal(tmp_path)
        with pytest.raises(ValueError, match="source commit"):
            evaluate_aggregate(
                manifest,
                seal,
                group_dir,
                source_commit="b" * 40,
                profile=TEST_PROFILE,
            )

    def test_seal_requires_verified_content(self, tmp_path: Path) -> None:
        group_dir, manifest, _ = _manifest_and_seal(tmp_path)
        raw = manifest.model_dump(mode="json")
        raw["corpus_hash"] = "sha256:" + "f" * 64
        drifted = Manifest.model_validate(raw)
        with pytest.raises(ValueError, match="exactly match"):
            create_seal(
                drifted,
                group_dir,
                source_commit=SOURCE_COMMIT,
                profile=TEST_PROFILE,
            )


class TestAggregateSchema:
    def _report(self, tmp_path: Path) -> AggregateReport:
        group_dir, manifest, seal = _manifest_and_seal(tmp_path)
        return evaluate_aggregate(
            manifest,
            seal,
            group_dir,
            source_commit=SOURCE_COMMIT,
            profile=TEST_PROFILE,
        )

    def test_forbidden_keys_rejected_before_model_validation(self, tmp_path: Path) -> None:
        raw = self._report(tmp_path).model_dump(mode="json")
        raw["case_results"] = []
        with pytest.raises(ValueError, match="forbidden"):
            validate_aggregate_payload(raw, profile=TEST_PROFILE)

    def test_wrong_dimension_total_rejected(self, tmp_path: Path) -> None:
        raw = self._report(tmp_path).model_dump(mode="json")
        raw["dimensions"]["complete"]["passed"] += 1
        with pytest.raises(ValidationError, match="sample_count"):
            AggregateReport.model_validate(raw)

    def test_report_hash_drift_rejected(self, tmp_path: Path) -> None:
        raw = self._report(tmp_path).model_dump(mode="json")
        raw["failure_layers"]["policy"] += 1
        with pytest.raises(ValueError, match="hash mismatch"):
            validate_aggregate_payload(raw, profile=TEST_PROFILE)

    def test_production_validator_rejects_test_sized_report(self, tmp_path: Path) -> None:
        raw = self._report(tmp_path).model_dump(mode="json")
        with pytest.raises(ValueError, match="sample count"):
            validate_aggregate_payload(raw)

    def test_no_forbidden_key_is_serialized(self, tmp_path: Path) -> None:
        raw = self._report(tmp_path).model_dump(mode="json")
        encoded = canonical_json(raw)
        for key in FORBIDDEN_REPORT_KEYS:
            assert f'"{key}"' not in encoded

    def test_consume_binds_report(self, tmp_path: Path) -> None:
        group_dir, manifest, seal = _manifest_and_seal(tmp_path)
        report = evaluate_aggregate(
            manifest,
            seal,
            group_dir,
            source_commit=SOURCE_COMMIT,
            profile=TEST_PROFILE,
        )
        consumed = consume_report(
            seal,
            report,
            consumed_at="2026-07-15T00:00:00Z",
            profile=TEST_PROFILE,
        )
        assert consumed.state == "consumed"
        assert consumed.report_hash == report.report_hash

    def test_consume_rejects_wrong_binding(self, tmp_path: Path) -> None:
        group_dir, manifest, seal = _manifest_and_seal(tmp_path)
        report = evaluate_aggregate(
            manifest,
            seal,
            group_dir,
            source_commit=SOURCE_COMMIT,
            profile=TEST_PROFILE,
        )
        raw = seal.model_dump(mode="json")
        raw["corpus_hash"] = "sha256:" + "f" * 64
        wrong_seal = PreConsumptionSeal.model_validate(raw)
        with pytest.raises(ValueError, match="does not match"):
            consume_report(wrong_seal, report, profile=TEST_PROFILE)


class TestCLI:
    def test_build_requires_write(self, tmp_path: Path) -> None:
        group_dir = tmp_path / "groups"
        _write_group(group_dir)
        assert main(["build-manifest", str(group_dir), str(tmp_path / "m.json")]) == 1

    def test_one_shot_outputs_refuse_overwrite(self, tmp_path: Path) -> None:
        output = tmp_path / "receipt.json"
        dummy = PreConsumptionSeal(
            manifest_hash="sha256:" + "a" * 64,
            corpus_hash="sha256:" + "b" * 64,
            source_commit=SOURCE_COMMIT,
        )
        _write(output, dummy, exclusive=True)
        with pytest.raises(ValueError, match="overwrite"):
            _write(output, dummy, exclusive=True)

    def test_baseline_refuses_existing_output_before_reading_content(
        self, tmp_path: Path
    ) -> None:
        report = tmp_path / "report.json"
        report.write_text("already exists", encoding="utf-8")
        args = Namespace(
            write=True,
            report_output=report,
            consumed_output=tmp_path / "consumed.json",
            manifest=tmp_path / "missing-manifest.json",
            seal=tmp_path / "missing-seal.json",
            group_dir=tmp_path / "missing-groups",
            source_commit=SOURCE_COMMIT,
        )
        with pytest.raises(ValueError, match="already exists"):
            cmd_baseline_once(args)


def test_digest_helper_is_canonical() -> None:
    assert sha256_digest(b"data") == sha256_digest(b"data")
    assert sha256_digest(b"data") != sha256_digest(b"other")

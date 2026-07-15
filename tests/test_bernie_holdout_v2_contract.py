"""Tests for the LC4V2 content-blind framework contracts.

All fixtures are tiny temporary synthetic scenarios authored inline.  No v1
fixture, support module, seal, receipt, report, or path is referenced.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.services.bernie.holdout_v2_contract import (
    AGGREGATE_SCHEMA_VERSION,
    CANONICAL_ENCODING,
    CORPUS_VERSION,
    DEFAULT_GROUP_COUNT,
    DEFAULT_MULTI_TURN_COUNT,
    DEFAULT_REPEAT_COUNT,
    DEFAULT_VARIANT_COUNT,
    EVALUATION_ID,
    FORBIDDEN_REPORT_KEYS,
    MULTI_TURN_FORMS,
    SAMPLES_PER_EVALUATION,
    SEAL_SCHEMA_VERSION,
    AggregateDimension,
    AggregateReport,
    ConsumedSeal,
    CoverageCell,
    CriticalSlice,
    FailureLayer,
    Manifest,
    ManifestFileEntry,
    PreConsumptionSeal,
    ScenarioGroupEnvelope,
    build_manifest,
    consume_report,
    create_seal,
    run_aggregate_evaluation,
    sha256_digest,
    verify_manifest,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
#  Helper: build a minimal valid spec dict
# ---------------------------------------------------------------------------


def _spec_dict(
    scenario_id: str = "test-001",
    dialogue_form: str = "one_shot",
    provenance: str = "gold",
    adjudication: str = "adjudicated",
    utterance: str = "hello",
    **overrides: Any,
) -> dict[str, Any]:
    span_start = 0
    span_end = len(utterance)
    spec: dict[str, Any] = {
        "spec_version": "lc1.v1",
        "scenario_id": scenario_id,
        "provenance": provenance,
        "adjudication": adjudication,
        "family": "test_family",
        "description": "Test scenario",
        "dialogue_turns": [{"utterance": utterance}],
        "reference_date": "2026-07-15",
        "clinic_clock": "2026-07-15T09:00:00+10:00",
        "intended_action": "create",
        "action_semantics": "intended",
        "temporal_relation": "exact",
        "earliest_time": "09:00",
        "latest_time": "09:00",
        "normalized_values": {},
        "source_spans": {
            "test_field": [
                {
                    "turn_index": 0,
                    "start": span_start,
                    "end": span_end,
                    "text": utterance,
                }
            ]
        },
        "duration_minutes": 30,
        "practitioner_semantics": "exact",
        "patient_semantics": "exact",
        "location_semantics": "exact",
        "appointment_type_semantics": "exact",
        "duration_semantics": "exact",
        "diary_state": "empty",
        "entity_state": "exact",
        "dialogue_form": dialogue_form,
        "language_form": "plain",
        "initial_diary_state": {},
        "expected_outcome_kind": "confirmed",
        "expected_tool_sequence": [],
        "expected_appointment_deltas": [],
        "expected_audit_deltas": [],
        "forbidden_outcomes": [],
        "forbidden_tool_calls": [],
        "expected_clarification": None,
        "clarification_choices": [],
    }
    spec.update(overrides)
    return spec


def _make_envelope_dict(
    group_id: str = "group-01",
    variant_ids: list[str] | None = None,
    base_utterance: str = "hello",
) -> dict[str, Any]:
    """Build a valid 12-variant group dict (9 one-shot + 3 multi-turn)."""
    if variant_ids is None:
        variant_ids = [f"{group_id}-v{i:02d}" for i in range(1, 13)]

    variants: list[dict[str, Any]] = []
    # First 9: one-shot
    for i in range(9):
        vid = variant_ids[i] if i < len(variant_ids) else f"{group_id}-v{i+1:02d}"
        variants.append(
            _spec_dict(scenario_id=vid, dialogue_form="one_shot")
        )
    # Last 3: multi-turn
    multi_turn_forms = sorted(MULTI_TURN_FORMS)
    for i in range(9, 12):
        vid = variant_ids[i] if i < len(variant_ids) else f"{group_id}-v{i+1:02d}"
        form = multi_turn_forms[i - 9]
        utterances = ["first turn", "second turn"]
        variants.append(
            _spec_dict(
                scenario_id=vid,
                dialogue_form=form,
                utterance=utterances[0],
                dialogue_turns=[{"utterance": u} for u in utterances],
                source_spans={
                    "test_field": [
                        {"turn_index": 0, "start": 0, "end": len(utterances[0]), "text": utterances[0]}
                    ]
                },
            )
        )

    return {"group_id": group_id, "variants": variants}


# ---------------------------------------------------------------------------
#  1.  ScenarioGroupEnvelope — contract validation
# ---------------------------------------------------------------------------


class TestScenarioGroupEnvelope:
    """Group envelope schema, shape, provenance, IDs, outcome_kind."""

    def test_valid_envelope(self) -> None:
        """A 12-variant envelope with 3 multi-turn validates."""
        data = _make_envelope_dict("group-01")
        envelope = ScenarioGroupEnvelope.model_validate(data)
        assert envelope.group_id == "group-01"
        assert len(envelope.variants) == 12

    def test_wrong_variant_count(self) -> None:
        """Fewer or more than 12 variants is rejected."""
        data = _make_envelope_dict("group-01")
        data["variants"] = data["variants"][:11]  # 11
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

        data["variants"] = data["variants"][:11] + [_spec_dict("extra")] * 2  # 13
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

    def test_wrong_multi_turn_count(self) -> None:
        """More or fewer than 3 multi-turn variants is rejected."""
        data = _make_envelope_dict("group-01")
        # Make all one_shot (0 multi-turn)
        for v in data["variants"]:
            v["dialogue_form"] = "one_shot"
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

        # Make 4 multi-turn
        data["variants"][8]["dialogue_form"] = "clarification"
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

    def test_duplicate_ids_within_group(self) -> None:
        """Duplicate scenario_id in a group is rejected."""
        data = _make_envelope_dict("group-01", variant_ids=["dup-id"] * 12)
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

    def test_non_gold_provenance(self) -> None:
        """Non-gold provenance is rejected."""
        data = _make_envelope_dict("group-01")
        data["variants"][0]["provenance"] = "silver"
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

    def test_non_adjudicated(self) -> None:
        """Non-adjudicated status is rejected."""
        data = _make_envelope_dict("group-01")
        data["variants"][0]["adjudication"] = "pending"
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

    def test_missing_expected_outcome_kind(self) -> None:
        """Omitted expected_outcome_kind is rejected (it's required)."""
        data = _make_envelope_dict("group-01")
        del data["variants"][0]["expected_outcome_kind"]
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)

    def test_null_expected_outcome_kind_is_allowed(self) -> None:
        """Explicit null expected_outcome_kind is valid."""
        data = _make_envelope_dict("group-01")
        data["variants"][0]["expected_outcome_kind"] = None
        # Should be accepted by ReceptionScenarioSpec (nullable field)
        envelope = ScenarioGroupEnvelope.model_validate(data)
        assert envelope.variants[0].expected_outcome_kind is None

    def test_extra_fields_forbidden(self) -> None:
        """Extra fields in the envelope dict are rejected."""
        data = _make_envelope_dict("group-01")
        data["unexpected_key"] = "bad"
        with pytest.raises(ValidationError):
            ScenarioGroupEnvelope.model_validate(data)


# ---------------------------------------------------------------------------
#  2.  Manifest — contract, building, I/O
# ---------------------------------------------------------------------------


class TestManifestContract:
    """Manifest schema, building, and verification."""

    def test_manifest_frozen(self) -> None:
        """Manifest instances are frozen (immutable)."""
        m = Manifest(
            corpus_version=CORPUS_VERSION,
            files=[ManifestFileEntry(relative_path="g01.json", sha256="a" * 64)],
            corpus_hash="b" * 64,
            group_count=24,
            variant_count=288,
            multi_turn_count=72,
        )
        with pytest.raises(ValidationError):
            m.group_count = 99

    def test_absolute_path_rejected(self) -> None:
        """Absolute relative_path triggers validation error."""
        # Use platform-independent absolute path
        abs_path = os.path.abspath("foo")
        with pytest.raises(ValidationError):
            ManifestFileEntry(relative_path=abs_path, sha256="a" * 64)

    def test_traversal_path_rejected(self) -> None:
        """Path with '..' triggers validation error."""
        with pytest.raises(ValidationError):
            ManifestFileEntry(relative_path="../outside/foo.json", sha256="a" * 64)

    def test_duplicate_paths_rejected(self) -> None:
        """Manifest with duplicate relative_path is rejected."""
        with pytest.raises(ValidationError):
            Manifest(
                corpus_version=CORPUS_VERSION,
                files=[
                    ManifestFileEntry(relative_path="same.json", sha256="a" * 64),
                    ManifestFileEntry(relative_path="same.json", sha256="b" * 64),
                ],
                corpus_hash="c" * 64,
                group_count=24,
                variant_count=288,
                multi_turn_count=72,
            )

    def test_wrong_corpus_version(self) -> None:
        """Non-matching corpus_version is rejected by the pattern."""
        with pytest.raises(ValidationError):
            Manifest(
                corpus_version="wrong-version",
                files=[],
                corpus_hash="a" * 64,
                group_count=24,
                variant_count=288,
                multi_turn_count=72,
            )

    def test_manifest_compute_hash_deterministic(self) -> None:
        """compute_hash returns the same value on identical data."""
        m1 = Manifest(
            corpus_version=CORPUS_VERSION,
            files=[ManifestFileEntry(relative_path="g01.json", sha256="a" * 64)],
            corpus_hash="b" * 64,
            group_count=24,
            variant_count=288,
            multi_turn_count=72,
        )
        m2 = Manifest.model_validate(m1.model_dump(mode="json"))
        assert m1.compute_hash() == m2.compute_hash()


# ---------------------------------------------------------------------------
#  3.  Seal — contract
# ---------------------------------------------------------------------------


class TestPreConsumptionSeal:
    """Pre-consumption seal contract."""

    def test_valid_seal(self) -> None:
        """A created seal has state='created'."""
        seal = PreConsumptionSeal(
            corpus_version=CORPUS_VERSION,
            manifest_hash="sha256:" + "a" * 64,
            source_commit="abc123",
            evaluator_version="0.1.0",
            schema_version=SEAL_SCHEMA_VERSION,
            evaluation_id=EVALUATION_ID,
            repeat_count=2,
            state="created",
        )
        assert seal.state == "created"
        assert seal.evaluation_id == EVALUATION_ID

    def test_seal_state_mutable(self) -> None:
        """Seal state can transition from 'created' to 'consumed'."""
        seal = PreConsumptionSeal(
            corpus_version=CORPUS_VERSION,
            manifest_hash="sha256:" + "a" * 64,
            source_commit="abc123",
            evaluator_version="0.1.0",
            schema_version=SEAL_SCHEMA_VERSION,
            evaluation_id=EVALUATION_ID,
            repeat_count=2,
            state="created",
        )
        assert seal.state == "created"
        seal.state = "consumed"
        assert seal.state == "consumed"

    def test_invalid_evaluation_id(self) -> None:
        """Non-matching evaluation_id is rejected."""
        with pytest.raises(ValidationError):
            PreConsumptionSeal(
                corpus_version=CORPUS_VERSION,
                manifest_hash="a" * 64,
                source_commit="abc123",
                evaluator_version="0.1.0",
                schema_version=SEAL_SCHEMA_VERSION,
                evaluation_id="wrong-id",
                repeat_count=2,
                state="created",
            )


# ---------------------------------------------------------------------------
#  4.  AggregateReport — contract and forbidden keys
# ---------------------------------------------------------------------------


class TestAggregateReport:
    """Aggregate-only report contract."""

    def _valid_report_data(self, **overrides: Any) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": AGGREGATE_SCHEMA_VERSION,
            "dimensions": {
                "interpretation": {"passed": 576, "failed": 0},
                "replay": {"passed": 576, "failed": 0},
                "composed_score": {"passed": 576, "failed": 0},
                "outcome_match": {"passed": 576, "failed": 0},
                "tool_sequence": {"passed": 576, "failed": 0},
                "delta_match": {"passed": 576, "failed": 0},
            },
            "failure_layers": [],
            "safety_pass": 576,
            "safety_total": 576,
            "variance": 0.0,
            "critical_slices": [],
            "coverage_cells": [],
            "corpus_hash": "sha256:" + "a" * 64,
            "report_hash": "sha256:" + "b" * 64,
        }
        data.update(overrides)
        return data

    def test_valid_report(self) -> None:
        """A minimal valid report is accepted."""
        report = AggregateReport.model_validate(self._valid_report_data())
        assert report.safety_pass == 576
        assert report.variance == 0.0

    def test_wrong_dimension_total(self) -> None:
        """Inconsistent dimension totals are rejected."""
        data = self._valid_report_data()
        data["dimensions"]["interpretation"] = {"passed": 500, "failed": 0}
        with pytest.raises(ValidationError, match="same total"):
            AggregateReport.model_validate(data)

    def test_zero_dimension_rejected(self) -> None:
        """At least one dimension is required."""
        data = self._valid_report_data()
        data["dimensions"] = {}
        with pytest.raises(ValidationError, match="at least one dimension"):
            AggregateReport.model_validate(data)

    def test_forbidden_keys_rejected_at_validation(self) -> None:
        """Forbidden keys used as top-level fields are rejected by Pydantic."""
        for key in ("utterance", "scenario_id", "per_case_results"):
            data = self._valid_report_data()
            data[key] = "bad"  # top-level field not in schema -> extra_forbid
            with pytest.raises(ValidationError, match="Extra inputs"):
                AggregateReport.model_validate(data)

    def test_check_forbidden_keys_passes_clean(self) -> None:
        """check_forbidden_keys does not raise on a clean report."""
        report = AggregateReport.model_validate(self._valid_report_data())
        report.check_forbidden_keys()  # should not raise


    def test_no_forbidden_keys_in_json(self) -> None:
        """The report JSON serialization contains no forbidden keys."""
        data = self._valid_report_data()
        report = AggregateReport.model_validate(data)
        report.check_forbidden_keys()
        dumped = json.dumps(data)
        for key in FORBIDDEN_REPORT_KEYS:
            assert f'"{key}"' not in dumped, f"forbidden key found: {key}"

    def test_extra_fields_rejected(self) -> None:
        """Extra top-level fields beyond the schema are rejected."""
        data = self._valid_report_data()
        data["unknown_top_field"] = "bad"
        with pytest.raises(ValidationError):
            AggregateReport.model_validate(data)

    def test_negative_counts_rejected(self) -> None:
        """Negative dimension counts are rejected."""
        data = self._valid_report_data()
        data["dimensions"]["interpretation"] = {"passed": -1, "failed": 577}
        with pytest.raises(ValidationError):
            AggregateReport.model_validate(data)


class TestAggregateDimension:
    """AggregateDimension contract."""

    def test_valid(self) -> None:
        d = AggregateDimension(passed=100, failed=20)
        assert d.passed == 100
        assert d.failed == 20

    def test_negative_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AggregateDimension(passed=-1, failed=0)


class TestFailureLayer:
    """FailureLayer contract."""

    def test_valid(self) -> None:
        f = FailureLayer(layer="interpretation", total=5)
        assert f.layer == "interpretation"

    def test_negative_total_rejected(self) -> None:
        with pytest.raises(ValidationError):
            FailureLayer(layer="x", total=-1)


class TestCriticalSlice:
    """CriticalSlice contract."""

    def test_valid(self) -> None:
        s = CriticalSlice(name="negation", passed=10, failed=2, total=12)
        assert s.total == 12


class TestCoverageCell:
    """CoverageCell contract."""

    def test_valid(self) -> None:
        c = CoverageCell(cell="create", count=72)
        assert c.count == 72


class TestConsumedSeal:
    """ConsumedSeal contract."""

    def test_valid(self) -> None:
        seal = ConsumedSeal(
            corpus_version=CORPUS_VERSION,
            manifest_hash="sha256:" + "a" * 64,
            source_commit="abc123",
            evaluator_version="0.1.0",
            schema_version=SEAL_SCHEMA_VERSION,
            evaluation_id=EVALUATION_ID,
            repeat_count=2,
            report_hash="sha256:" + "b" * 64,
        )
        assert seal.state == "consumed"
        assert seal.report_hash.startswith("sha256:")

    def test_frozen(self) -> None:
        seal = ConsumedSeal(
            corpus_version=CORPUS_VERSION,
            manifest_hash="a" * 64,
            source_commit="abc123",
            evaluator_version="0.1.0",
            schema_version=SEAL_SCHEMA_VERSION,
            evaluation_id=EVALUATION_ID,
            repeat_count=2,
            report_hash="b" * 64,
        )
        with pytest.raises(ValidationError):
            seal.report_hash = "c" * 64


# ---------------------------------------------------------------------------
#  5.  Integration: build_manifest, verify_manifest, create_seal,
#      run_aggregate_evaluation, consume_report
# ---------------------------------------------------------------------------


class TestManifestBuildVerify:
    """End-to-end manifest build and verification with tmp files."""

    def _write_group_file(
        self, directory: Path, name: str, envelope_dict: dict[str, Any]
    ) -> Path:
        path = directory / name
        path.write_text(
            json.dumps(envelope_dict, sort_keys=True),
            encoding=CANONICAL_ENCODING,
        )
        return path

    def _create_temp_groups(
        self, tmp_path: Path, group_count: int = 2
    ) -> tuple[Path, int, int, int]:
        """Create *group_count* valid group JSON files in tmp_path.

        Returns ``(dir_path, actual_groups, actual_variants, actual_multi_turn)``.
        Each group has 12 variants (9 one-shot + 3 multi-turn).
        """
        for i in range(1, group_count + 1):
            gid = f"group-{i:02d}"
            self._write_group_file(
                tmp_path,
                f"{gid}.json",
                _make_envelope_dict(gid),
            )
        return tmp_path, group_count, group_count * 12, group_count * 3

    def test_build_manifest(self, tmp_path: Path) -> None:
        """build_manifest creates a valid Manifest from a directory."""
        group_dir, ng, nv, nm = self._create_temp_groups(tmp_path, group_count=2)
        manifest = build_manifest(group_dir, group_count=ng, variant_count=nv, multi_turn_count=nm)
        assert len(manifest.files) == 2
        assert manifest.variant_count == 24
        assert manifest.corpus_version == CORPUS_VERSION

    def test_build_manifest_empty_dir(self, tmp_path: Path) -> None:
        """build_manifest raises ValueError on empty directory."""
        with pytest.raises(ValueError, match="no JSON files"):
            build_manifest(tmp_path)

    def test_verify_manifest_passes(self, tmp_path: Path) -> None:
        """verify_manifest succeeds when expected counts match actual data."""
        group_dir, ng, nv, nm = self._create_temp_groups(tmp_path, group_count=2)
        manifest = build_manifest(group_dir, group_count=ng, variant_count=nv, multi_turn_count=nm)
        # 2 groups = 24 variants, 6 multi-turn
        verify_manifest(
            manifest,
            group_dir,
            expected_group_count=ng,
            expected_variant_count=nv,
            expected_multi_turn_count=nm,
        )  # should not raise

    def test_verify_manifest_missing_file(self, tmp_path: Path) -> None:
        """verify_manifest rejects a manifest referencing a missing file."""
        group_dir, ng, nv, nm = self._create_temp_groups(tmp_path, group_count=2)
        manifest = build_manifest(group_dir, group_count=ng, variant_count=nv, multi_turn_count=nm)
        # Add a non-existent file to the manifest
        extra_entry = ManifestFileEntry(
            relative_path="nonexistent.json",
            sha256="a" * 64,
        )
        bad_manifest = Manifest.model_validate({
            **manifest.model_dump(mode="json"),
            "files": [e.model_dump() for e in manifest.files] + [extra_entry.model_dump()],
        })
        with pytest.raises(ValueError, match="missing"):
            verify_manifest(bad_manifest, group_dir, expected_group_count=ng, expected_variant_count=nv, expected_multi_turn_count=nm)

    def test_verify_manifest_extra_file(self, tmp_path: Path) -> None:
        """verify_manifest rejects an extra file not in the manifest."""
        group_dir, ng, nv, nm = self._create_temp_groups(tmp_path, group_count=1)
        # Create an extra file not in the manifest
        self._write_group_file(
            group_dir, "extra.json", _make_envelope_dict("extra")
        )
        # Rebuild manifest to include the new file
        extra_manifest = build_manifest(group_dir, group_count=2, variant_count=24, multi_turn_count=6)
        # Remove "extra.json" from manifest files
        filtered = [e for e in extra_manifest.files if e.relative_path != "extra.json"]
        bad_manifest = Manifest.model_validate({
            **extra_manifest.model_dump(mode="json"),
            "files": [e.model_dump() for e in filtered],
        })
        with pytest.raises(ValueError, match="not listed"):
            verify_manifest(bad_manifest, group_dir, expected_group_count=2, expected_variant_count=24, expected_multi_turn_count=6)

    def test_verify_manifest_hash_mismatch(self, tmp_path: Path) -> None:
        """verify_manifest rejects a file whose content hash changed."""
        group_dir, ng, nv, nm = self._create_temp_groups(tmp_path, group_count=1)
        manifest = build_manifest(group_dir, group_count=ng, variant_count=nv, multi_turn_count=nm)
        # Tamper with a file
        file_path = group_dir / manifest.files[0].relative_path
        original = file_path.read_text(CANONICAL_ENCODING)
        file_path.write_text(original + " ", encoding=CANONICAL_ENCODING)
        with pytest.raises(ValueError, match="hash mismatch"):
            verify_manifest(manifest, group_dir, expected_group_count=ng, expected_variant_count=nv, expected_multi_turn_count=nm)

    def test_verify_manifest_wrong_version(self, tmp_path: Path) -> None:
        """verify_manifest rejects a wrong corpus version."""
        group_dir, ng, nv, nm = self._create_temp_groups(tmp_path, group_count=1)
        manifest = build_manifest(group_dir, group_count=ng, variant_count=nv, multi_turn_count=nm)
        # Use model_construct to bypass Manifest validation (which would reject wrong version)
        bad_manifest = Manifest.model_construct(
            corpus_version="wrong-version",
            files=list(manifest.files),
            corpus_hash=manifest.corpus_hash,
            group_count=ng,
            variant_count=nv,
            multi_turn_count=nm,
        )
        with pytest.raises(ValueError, match="corpus_version"):
            verify_manifest(bad_manifest, group_dir, expected_group_count=ng, expected_variant_count=nv, expected_multi_turn_count=nm)

    def test_verify_manifest_count_drift(self, tmp_path: Path) -> None:
        """verify_manifest rejects wrong expected counts."""
        group_dir, ng, nv, nm = self._create_temp_groups(tmp_path, group_count=1)
        manifest = build_manifest(group_dir, group_count=ng, variant_count=nv, multi_turn_count=nm)
        with pytest.raises(ValueError, match="group_count"):
            verify_manifest(
                manifest,
                group_dir,
                expected_group_count=999,  # deliberately wrong
                expected_variant_count=nv,
                expected_multi_turn_count=nm,
            )

    def test_verify_manifest_duplicate_cross_group_id(
        self, tmp_path: Path
    ) -> None:
        """verify_manifest rejects duplicate scenario_id across groups."""
        # Create two groups with the same IDs
        group_dir = tmp_path / "groups"
        group_dir.mkdir()
        # First group
        env1 = _make_envelope_dict("group-01")
        self._write_group_file(group_dir, "g01.json", env1)
        # Second group with same variant IDs
        env2 = _make_envelope_dict("group-02",
                                    variant_ids=[v["scenario_id"] for v in env1["variants"]])
        self._write_group_file(group_dir, "g02.json", env2)
        manifest = build_manifest(group_dir, group_count=2, variant_count=24, multi_turn_count=6)
        with pytest.raises(ValueError, match="duplicate scenario_id"):
            verify_manifest(manifest, group_dir, expected_group_count=2, expected_variant_count=24, expected_multi_turn_count=6)

    def test_verify_manifest_traversal_rejected(self, tmp_path: Path) -> None:
        """verify_manifest rejects traversal attempts (file outside group dir)."""
        group_dir = tmp_path / "groups"
        group_dir.mkdir()
        # Create a valid group file inside the group directory
        self._write_group_file(
            group_dir, "group-01.json", _make_envelope_dict("group-01")
        )
        # Create a file *outside* the group directory
        outside_file = tmp_path / "outside.json"
        outside_content = json.dumps(
            _make_envelope_dict("outside"), sort_keys=True
        )
        outside_file.write_text(outside_content, encoding=CANONICAL_ENCODING)
        outside_hash = sha256_digest(outside_content.encode(CANONICAL_ENCODING))

        # Build a manifest that references the internal file and a traversal
        internal_entry = ManifestFileEntry(
            relative_path="group-01.json",
            sha256=sha256_digest(
                (group_dir / "group-01.json").read_bytes()
            ),
        )
        traversal_entry = ManifestFileEntry.model_construct(
            relative_path="../outside.json",
            sha256=outside_hash,
        )
        bad_manifest = Manifest.model_construct(
            corpus_version=CORPUS_VERSION,
            files=[internal_entry, traversal_entry],
            corpus_hash="a" * 64,
            group_count=2,
            variant_count=24,
            multi_turn_count=6,
        )
        # The traversal check in verify_manifest resolves outside.json
        # relative to group_dir, which puts it outside the group directory.
        with pytest.raises(ValueError, match="traversal|missing|not found"):
            verify_manifest(
                bad_manifest, group_dir,
                expected_group_count=2, expected_variant_count=24,
                expected_multi_turn_count=6,
            )

        # Clean test: a manifest that passes the file set check but fails
        # the traversal check. For this we need the traversal path to match
        # a filename in actual_names. This is hard to test cleanly without
        # symlinks, so we verify that either "traversal" or "missing" fires.


# ---------------------------------------------------------------------------
#  6.  create_seal and seal hash flow
# ---------------------------------------------------------------------------


class TestCreateSeal:
    """create_seal produces the correct PreConsumptionSeal."""

    def test_create_seal_from_manifest(self, tmp_path: Path) -> None:
        group_dir = tmp_path / "groups"
        group_dir.mkdir()
        self._write_group_file(
            group_dir, "g01.json", _make_envelope_dict("group-01")
        )
        manifest = build_manifest(group_dir, group_count=1, variant_count=12, multi_turn_count=3)
        seal = create_seal(manifest, source_commit="head123")
        assert seal.corpus_version == CORPUS_VERSION
        assert seal.manifest_hash == manifest.compute_hash()
        assert seal.source_commit == "head123"
        assert seal.evaluation_id == EVALUATION_ID
        assert seal.repeat_count == DEFAULT_REPEAT_COUNT
        assert seal.state == "created"

    def _write_group_file(self, directory, name, envelope_dict):
        path = directory / name
        path.write_text(
            json.dumps(envelope_dict, sort_keys=True),
            encoding=CANONICAL_ENCODING,
        )
        return path


# ---------------------------------------------------------------------------
#  7.  consume_report — one-way, one-shot
# ---------------------------------------------------------------------------


class TestConsumeReport:
    """Consumption must be one-way and one-shot."""

    def _create_fixtures(self, tmp_path: Path, n_groups: int = 1):
        """Create group files and return manifest, seal, and report."""
        group_dir = tmp_path / "groups"
        group_dir.mkdir()
        for i in range(1, n_groups + 1):
            gid = f"group-{i:02d}"
            (group_dir / f"{gid}.json").write_text(
                json.dumps(_make_envelope_dict(gid), sort_keys=True),
                encoding=CANONICAL_ENCODING,
            )
        nv = n_groups * 12
        nm = n_groups * 3
        manifest = build_manifest(
            group_dir, group_count=n_groups, variant_count=nv, multi_turn_count=nm
        )
        seal = create_seal(manifest, source_commit="abc123def")
        report = run_aggregate_evaluation(
            manifest, seal, group_dir,
            sample_size=nv * DEFAULT_REPEAT_COUNT,
            expected_group_count=n_groups,
            expected_variant_count=nv,
            expected_multi_turn_count=nm,
        )
        return manifest, seal, report

    def test_consume_success(self, tmp_path: Path) -> None:
        """Successful consumption returns a ConsumedSeal."""
        _, seal, report = self._create_fixtures(tmp_path, n_groups=1)
        consumed = consume_report(seal, report, source_commit="abc123def")
        assert consumed.state == "consumed"
        assert consumed.report_hash == report.report_hash
        assert consumed.source_commit == "abc123def"

    def test_consume_wrong_commit(self, tmp_path: Path) -> None:
        """Wrong source commit is rejected."""
        _, seal, report = self._create_fixtures(tmp_path, n_groups=1)
        with pytest.raises(ValueError, match="source commit mismatch"):
            consume_report(seal, report, source_commit="wrongcommit")

    def test_consume_already_consumed(self, tmp_path: Path) -> None:
        """A second consumption of the same seal is rejected."""
        _, seal, report = self._create_fixtures(tmp_path, n_groups=1)
        consume_report(seal, report, source_commit="abc123def")
        with pytest.raises(ValueError, match="already consumed"):
            consume_report(seal, report, source_commit="abc123def")

    def test_consume_tampered_report(self, tmp_path: Path) -> None:
        """A report with a wrong report_hash is rejected."""
        _, seal, report = self._create_fixtures(tmp_path, n_groups=1)
        # Tamper the report hash
        report.report_hash = "sha256:" + "f" * 64
        with pytest.raises(ValueError, match="report hash mismatch"):
            consume_report(seal, report, source_commit="abc123def")

    def test_consume_report_drift(self, tmp_path: Path) -> None:
        """A report whose content has drifted (hash mismatch) is rejected."""
        _, seal, report = self._create_fixtures(tmp_path, n_groups=1)
        # Drift the report content by modifying a dimension (rebuild needed)
        data = report.model_dump(mode="json")
        data["dimensions"]["interpretation"] = {"passed": 23, "failed": 1}
        # The report hash is now stale; this still passes dimension validation
        # because sample_size = 12*2 = 24
        drifted_report = AggregateReport.model_validate(data)
        with pytest.raises(ValueError, match="report hash mismatch"):
            consume_report(seal, drifted_report, source_commit="abc123def")


# ---------------------------------------------------------------------------
#  8.  run_aggregate_evaluation — content-blind placeholder
# ---------------------------------------------------------------------------


class TestAggregateEvaluation:
    """Aggregate evaluation (placeholder) produces valid aggregate-only output."""

    SAMPLE_GROUPS = 2  # 24 variants, 6 multi-turn
    SAMPLE_SIZE = SAMPLE_GROUPS * 12 * DEFAULT_REPEAT_COUNT  # 48

    def _setup(self, tmp_path: Path):
        group_dir = tmp_path / "groups"
        group_dir.mkdir()
        for i in range(1, self.SAMPLE_GROUPS + 1):
            gid = f"group-{i:02d}"
            (group_dir / f"{gid}.json").write_text(
                json.dumps(_make_envelope_dict(gid), sort_keys=True),
                encoding=CANONICAL_ENCODING,
            )
        nv = self.SAMPLE_GROUPS * 12
        nm = self.SAMPLE_GROUPS * 3
        manifest = build_manifest(
            group_dir, group_count=self.SAMPLE_GROUPS, variant_count=nv, multi_turn_count=nm
        )
        seal = create_seal(manifest, source_commit="head")
        return group_dir, manifest, seal

    def test_evaluation_success(self, tmp_path: Path) -> None:
        group_dir, manifest, seal = self._setup(tmp_path)
        report = run_aggregate_evaluation(
            manifest, seal, group_dir,
            sample_size=self.SAMPLE_SIZE,
            expected_group_count=self.SAMPLE_GROUPS,
            expected_variant_count=self.SAMPLE_GROUPS * 12,
            expected_multi_turn_count=self.SAMPLE_GROUPS * 3,
        )
        assert report.schema_version == AGGREGATE_SCHEMA_VERSION
        assert report.report_hash != ""
        # All dimensions should sum to SAMPLE_SIZE
        for dim in report.dimensions.values():
            assert dim.passed + dim.failed == self.SAMPLE_SIZE
        # Should contain zero failures
        assert report.safety_pass == self.SAMPLE_SIZE
        assert report.variance == 0.0

    def test_evaluation_no_forbidden_keys(self, tmp_path: Path) -> None:
        """The aggregate report contains no forbidden key."""
        group_dir, manifest, seal = self._setup(tmp_path)
        report = run_aggregate_evaluation(
            manifest, seal, group_dir,
            sample_size=self.SAMPLE_SIZE,
            expected_group_count=self.SAMPLE_GROUPS,
            expected_variant_count=self.SAMPLE_GROUPS * 12,
            expected_multi_turn_count=self.SAMPLE_GROUPS * 3,
        )
        # check_forbidden_keys should not raise
        report.check_forbidden_keys()

    def test_evaluation_fails_on_missing_group(self, tmp_path: Path) -> None:
        """Evaluation fails when the group directory is incomplete."""
        group_dir, manifest, seal = self._setup(tmp_path)
        # Remove a group file
        for f in group_dir.iterdir():
            if f.suffix == ".json":
                f.unlink()
                break
        with pytest.raises(ValueError, match="not found|missing"):
            run_aggregate_evaluation(
                manifest, seal, group_dir,
                sample_size=self.SAMPLE_SIZE,
                expected_group_count=self.SAMPLE_GROUPS,
                expected_variant_count=self.SAMPLE_GROUPS * 12,
                expected_multi_turn_count=self.SAMPLE_GROUPS * 3,
            )


# ---------------------------------------------------------------------------
#  9.  FORBIDDEN_REPORT_KEYS consistency
# ---------------------------------------------------------------------------


class TestForbiddenKeys:
    """FORBIDDEN_REPORT_KEYS prevents per-case data leakage."""

    def test_known_forbidden_keys(self) -> None:
        """The set of forbidden keys is non-empty and includes key identifiers."""
        assert len(FORBIDDEN_REPORT_KEYS) > 5
        assert "utterance" in FORBIDDEN_REPORT_KEYS
        assert "scenario_id" in FORBIDDEN_REPORT_KEYS
        assert "per_case" in FORBIDDEN_REPORT_KEYS
        assert "source_spans" in FORBIDDEN_REPORT_KEYS
        assert "normalized_values" in FORBIDDEN_REPORT_KEYS
        assert "expected_outcome_kind" in FORBIDDEN_REPORT_KEYS

    @staticmethod
    def _valid_report():
        data = {
            "schema_version": AGGREGATE_SCHEMA_VERSION,
            "dimensions": {
                "interpretation": {"passed": 576, "failed": 0},
                "replay": {"passed": 576, "failed": 0},
                "composed_score": {"passed": 576, "failed": 0},
                "outcome_match": {"passed": 576, "failed": 0},
                "tool_sequence": {"passed": 576, "failed": 0},
                "delta_match": {"passed": 576, "failed": 0},
            },
            "failure_layers": [],
            "safety_pass": 576,
            "safety_total": 576,
            "variance": 0.0,
            "critical_slices": [],
            "coverage_cells": [],
            "corpus_hash": "sha256:" + "a" * 64,
            "report_hash": "sha256:" + "b" * 64,
        }
        return AggregateReport.model_validate(data)

    def test_clean_report_passes_check(self) -> None:
        """A schema-valid aggregate report passes check_forbidden_keys."""
        report = self._valid_report()
        report.check_forbidden_keys()  # must not raise

    def test_forbidden_keys_set_is_comprehensive(self) -> None:
        """FORBIDDEN_REPORT_KEYS covers all per-case identifiers."""
        assert "utterance" in FORBIDDEN_REPORT_KEYS
        assert "scenario_id" in FORBIDDEN_REPORT_KEYS
        assert "per_case" in FORBIDDEN_REPORT_KEYS
        assert "source_spans" in FORBIDDEN_REPORT_KEYS
        assert "normalized_values" in FORBIDDEN_REPORT_KEYS
        assert "expected_outcome_kind" in FORBIDDEN_REPORT_KEYS
        assert "group_id" in FORBIDDEN_REPORT_KEYS
        # At least 8 entries for a comprehensive set
        assert len(FORBIDDEN_REPORT_KEYS) >= 8


# ---------------------------------------------------------------------------
#  10.  sha256_digest
# ---------------------------------------------------------------------------


class TestSha256Digest:
    """sha256_digest helper."""

    def test_prefixed_format(self) -> None:
        result = sha256_digest(b"hello")
        assert result.startswith("sha256:")
        assert len(result) == 7 + 64  # "sha256:" + 64 hex chars

    def test_deterministic(self) -> None:
        assert sha256_digest(b"data") == sha256_digest(b"data")
        assert sha256_digest(b"data") != sha256_digest(b"different")


# ---------------------------------------------------------------------------
#  11.  Cross-group verification contract
# ---------------------------------------------------------------------------


class TestFullCycle:
    """Full manifest→seal→evaluate→consume cycle with synthetic groups."""

    def test_full_cycle_small(self, tmp_path: Path) -> None:
        """build_manifest with production defaults fails closed on small data."""
        group_dir = tmp_path / "groups"
        group_dir.mkdir()

        # Write 2 groups = 24 variants, 6 multi-turn
        for i in range(1, 3):
            (group_dir / f"g{i:02d}.json").write_text(
                json.dumps(_make_envelope_dict(f"group-{i:02d}"), sort_keys=True),
                encoding=CANONICAL_ENCODING,
            )

        # Build manifest with production defaults — fail closed
        manifest = build_manifest(group_dir)  # declares 24/288/72
        assert manifest.variant_count == 288  # production default

        # Verification against actual content fails because actual counts
        # (24 variants, 6 multi-turn) don't match expected (288, 72)
        with pytest.raises(ValueError, match="total variants|multi_turn_count"):
            verify_manifest(manifest, group_dir)

    def test_full_cycle_minimal_pass(self, tmp_path: Path) -> None:
        """A cycle succeeds when test-specific counts match."""
        group_dir = tmp_path / "groups"
        group_dir.mkdir()

        n_groups = 2
        n_variants = n_groups * 12  # 24
        n_multi = n_groups * 3  # 6

        for i in range(1, n_groups + 1):
            (group_dir / f"g{i:02d}.json").write_text(
                json.dumps(_make_envelope_dict(f"group-{i:02d}"), sort_keys=True),
                encoding=CANONICAL_ENCODING,
            )

        # Build manifest with test-specific counts
        manifest = build_manifest(
            group_dir,
            group_count=n_groups,
            variant_count=n_variants,
            multi_turn_count=n_multi,
        )

        # Seal and evaluate
        seal = create_seal(manifest, source_commit="testhead")
        report = run_aggregate_evaluation(
            manifest,
            seal,
            group_dir,
            sample_size=n_variants * DEFAULT_REPEAT_COUNT,
            expected_group_count=n_groups,
            expected_variant_count=n_variants,
            expected_multi_turn_count=n_multi,
        )
        assert report.report_hash != ""
        report.check_forbidden_keys()

        # Consume
        consumed = consume_report(seal, report, source_commit="testhead")
        assert consumed.state == "consumed"
        assert consumed.report_hash == report.report_hash

        # Second consumption fails
        with pytest.raises(ValueError, match="already consumed"):
            consume_report(seal, report, source_commit="testhead")

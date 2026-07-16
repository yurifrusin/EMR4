"""Tests for the LC4V6 content-blind framework.

No real V6 content, fixtures, manifests, seals, receipts, or per-case
evidence are loaded. Only empty placeholder metadata and malformed
synthetic data are used.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import fields
from typing import Any

import pytest

from app.services.bernie.lc4v6_content_blind_framework import (
    ATTEMPT_ID,
    FIXED_MANIFEST_SHAPE,
    REPORT_FILENAME,
    SEAL_FILENAME,
    MARKER_FILENAME,
    AggregateReport,
    BoundHashes,
    EvidenceValidationResult,
    EvaluationContext,
    ManifestValidationResult,
    OneShotStateMachine,
    ScenarioContract,
    StateMachineResult,
    TypedObservation,
    bind_corpus_hash,
    bind_evaluator_hash,
    bind_framework_hash,
    bind_manifest_hash,
    bind_source_hash,
    hash_bytes,
    hash_content,
    reduce_observations,
    validate_evidence_population,
    validate_manifest_shape,
)

# ---------------------------------------------------------------------------
# 1. Valid placeholder metadata
# ---------------------------------------------------------------------------


class TestPlaceholderMetadata:
    """ScenarioContract and TypedObservation accept valid placeholder data."""

    def test_scenario_contract_group_001(self) -> None:
        contract = ScenarioContract(
            group="group-001",
            cell="cell-001",
            action="create",
            is_multi_turn=False,
        )
        assert contract.group == "group-001"
        assert contract.cell == "cell-001"
        assert contract.action == "create"
        assert contract.is_multi_turn is False

    def test_scenario_contract_multi_turn(self) -> None:
        contract = ScenarioContract(
            group="group-002",
            cell="cell-002",
            action="move",
            is_multi_turn=True,
            data=None,
        )
        assert contract.is_multi_turn is True

    def test_scenario_contract_empty_strings(self) -> None:
        contract = ScenarioContract(
            group="",
            cell="",
            action="",
            is_multi_turn=False,
        )
        assert contract.group == ""

    def test_typed_observation_empty(self) -> None:
        obs = TypedObservation()
        assert obs.dimensions == {}

    def test_typed_observation_with_dimensions(self) -> None:
        obs = TypedObservation(dimensions={"complete": 1, "safe": 1})
        assert obs.dimensions["complete"] == 1
        assert obs.dimensions["safe"] == 1

    def test_scenario_contract_frozen(self) -> None:
        contract = ScenarioContract(
            group="g", cell="c", action="a", is_multi_turn=False
        )
        with pytest.raises(AttributeError):
            contract.group = "changed"  # type: ignore[misc]

    def test_typed_observation_frozen(self) -> None:
        obs = TypedObservation()
        with pytest.raises(AttributeError):
            obs.dimensions = {"leak": 1}  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 2. Malformed population boundaries
# ---------------------------------------------------------------------------


class TestManifestValidation:
    """Every malformed population boundary is rejected."""

    def _valid_manifest(self) -> dict[str, Any]:
        return dict(FIXED_MANIFEST_SHAPE)

    def test_valid_manifest(self) -> None:
        result = validate_manifest_shape(self._valid_manifest())
        assert result.valid
        assert result.errors == ()

    def test_missing_groups(self) -> None:
        manifest = self._valid_manifest()
        del manifest["groups"]
        result = validate_manifest_shape(manifest)
        assert not result.valid
        assert any("groups" in e for e in result.errors)

    def test_wrong_groups(self) -> None:
        manifest = self._valid_manifest()
        manifest["groups"] = 23
        result = validate_manifest_shape(manifest)
        assert not result.valid
        assert any("23" in e for e in result.errors)

    def test_wrong_scenarios(self) -> None:
        manifest = self._valid_manifest()
        manifest["scenarios"] = 287
        result = validate_manifest_shape(manifest)
        assert not result.valid

    def test_wrong_multi_turn(self) -> None:
        manifest = self._valid_manifest()
        manifest["multi_turn"] = 71
        result = validate_manifest_shape(manifest)
        assert not result.valid

    def test_wrong_one_shot(self) -> None:
        manifest = self._valid_manifest()
        manifest["one_shot"] = 215
        result = validate_manifest_shape(manifest)
        assert not result.valid

    def test_wrong_actions(self) -> None:
        manifest = self._valid_manifest()
        manifest["actions"] = 5
        result = validate_manifest_shape(manifest)
        assert not result.valid

    def test_wrong_cells(self) -> None:
        manifest = self._valid_manifest()
        manifest["cells"] = 289
        result = validate_manifest_shape(manifest)
        assert not result.valid

    def test_wrong_repeats(self) -> None:
        manifest = self._valid_manifest()
        manifest["repeats"] = 3
        result = validate_manifest_shape(manifest)
        assert not result.valid

    def test_all_zero(self) -> None:
        manifest = {k: 0 for k in FIXED_MANIFEST_SHAPE}
        result = validate_manifest_shape(manifest)
        assert not result.valid
        assert len(result.errors) == len(FIXED_MANIFEST_SHAPE)

    def test_empty_manifest(self) -> None:
        result = validate_manifest_shape({})
        assert not result.valid

    def test_all_keys_wrong(self) -> None:
        manifest = {
            "groups": 1,
            "scenarios": 1,
            "multi_turn": 1,
            "one_shot": 1,
            "actions": 1,
            "cells": 1,
            "repeats": 1,
        }
        result = validate_manifest_shape(manifest)
        assert not result.valid
        assert len(result.errors) == len(FIXED_MANIFEST_SHAPE)

    def test_none_values(self) -> None:
        manifest = {k: None for k in FIXED_MANIFEST_SHAPE}
        result = validate_manifest_shape(manifest)
        assert not result.valid


# ---------------------------------------------------------------------------
# 3. Aggregate leakage refusal
# ---------------------------------------------------------------------------


class TestAggregateLeakageRefusal:
    """Public AggregateReport must not expose case-level fields."""

    _LEAK_FIELD_NAMES = frozenset(
        {
            "scenario_id",
            "utterances",
            "utterance",
            "expected_value",
            "source_span",
            "normalized_turn",
            "label",
            "failure_selection",
            "probe_id",
            "cell_id",
            "contract_id",
            "observation_id",
            "case_id",
            "expected",
            "failure",
        }
    )

    def test_no_case_level_fields(self) -> None:
        """AggregateReport fields must be aggregate-only names."""
        field_names = {f.name for f in fields(AggregateReport)}
        leaks = field_names & self._LEAK_FIELD_NAMES
        assert not leaks, f"AggregateReport leaks case-level fields: {leaks}"

    def test_field_types_are_aggregate(self) -> None:
        """Verify each AggregateReport field type is aggregate-safe."""
        for f in fields(AggregateReport):
            if f.name == "hashes":
                continue  # BoundHashes is aggregate-only
            if f.name == "dimensions":
                assert "dict" in str(f.type), "dimensions must be dict"
            elif f.name == "slices":
                assert "dict" in str(f.type), "slices must be dict"
            elif f.name in ("total_samples", "complete", "safe", "variance"):
                assert "int" in str(f.type)

    def test_typed_observation_no_leak_fields(self) -> None:
        """TypedObservation must not carry case-level artifacts."""
        field_names = {f.name for f in fields(TypedObservation)}
        assert "dimensions" in field_names
        assert len(field_names) == 1, (
            f"TypedObservation has unexpected fields: {field_names}"
        )

    def test_reduce_returns_no_case_data(self) -> None:
        """Output of reduce_observations must not contain case-level keys."""
        hashes = BoundHashes(
            source="sha256:0" * 4,
            corpus="sha256:1" * 4,
            manifest="sha256:2" * 4,
            framework="sha256:3" * 4,
            evaluator="sha256:4" * 4,
        )
        obs = [TypedObservation(dimensions={"complete": 1, "safe": 1})]
        report = reduce_observations(obs, hashes, attempt_id=ATTEMPT_ID)

        assert isinstance(report.total_samples, int)
        assert isinstance(report.complete, int)
        assert isinstance(report.safe, int)
        assert isinstance(report.variance, int)
        assert isinstance(report.dimensions, dict)
        assert isinstance(report.slices, dict)
        assert isinstance(report.hashes, BoundHashes)

        result_json = json.dumps(
            {
                "total_samples": report.total_samples,
                "complete": report.complete,
                "safe": report.safe,
                "variance": report.variance,
            }
        )
        for leak in self._LEAK_FIELD_NAMES:
            assert leak not in result_json


# ---------------------------------------------------------------------------
# 4. Tamper / hash failure
# ---------------------------------------------------------------------------


class TestHashIntegrity:
    """Hash binding helpers detect tampering."""

    def test_hash_content_deterministic(self) -> None:
        h1 = hash_content("hello")
        h2 = hash_content("hello")
        assert h1 == h2
        assert h1.startswith("sha256:")

    def test_hash_content_differs(self) -> None:
        assert hash_content("hello") != hash_content("world")

    def test_hash_bytes_deterministic(self) -> None:
        h1 = hash_bytes(b"data")
        h2 = hash_bytes(b"data")
        assert h1 == h2

    def test_hash_bytes_differs(self) -> None:
        assert hash_bytes(b"data") != hash_bytes(b"different")

    def test_bind_source_hash(self) -> None:
        h = bind_source_hash("abc123")
        assert h.startswith("sha256:")
        assert len(h) == 64 + 7  # "sha256:" + 64 hex chars

    def test_bind_corpus_hash(self) -> None:
        h = bind_corpus_json = bind_corpus_hash('{"key": "value"}')
        assert h.startswith("sha256:")

    def test_bind_manifest_hash(self) -> None:
        h = bind_manifest_hash('{"groups": 24}')
        assert h.startswith("sha256:")

    def test_bind_framework_hash(self) -> None:
        h = bind_framework_hash("def framework(): pass")
        assert h.startswith("sha256:")

    def test_bind_evaluator_hash(self) -> None:
        h = bind_evaluator_hash("def evaluate(): pass")
        assert h.startswith("sha256:")

    def test_tampered_source_hash(self) -> None:
        original = bind_source_hash("abc123")
        tampered = bind_source_hash("abc124")
        assert original != tampered

    def test_tampered_corpus_hash(self) -> None:
        original = bind_corpus_hash('{"key": "value1"}')
        tampered = bind_corpus_hash('{"key": "value2"}')
        assert original != tampered

    def test_tampered_manifest_hash(self) -> None:
        original = bind_manifest_hash('{"groups": 24}')
        tampered = bind_manifest_hash('{"groups": 23}')
        assert original != tampered

    def test_tampered_framework_hash(self) -> None:
        original = bind_framework_hash("original code")
        tampered = bind_framework_hash("tampered code")
        assert original != tampered

    def test_tampered_evaluator_hash(self) -> None:
        original = bind_evaluator_hash("original eval")
        tampered = bind_evaluator_hash("tampered eval")
        assert original != tampered

    def test_bound_hashes_repr_no_raw_content(self) -> None:
        hashes = BoundHashes(
            source="sha256:s" * 4,
            corpus="sha256:c" * 4,
            manifest="sha256:m" * 4,
            framework="sha256:f" * 4,
            evaluator="sha256:e" * 4,
        )
        text = str(hashes)
        assert "sha256:" in text
        assert "utterance" not in text.lower()


# ---------------------------------------------------------------------------
# 5. Evidence population validation
# ---------------------------------------------------------------------------


class TestEvidenceValidation:
    """Evidence validation checks exact population and hash consistency."""

    def _sample_manifest(self) -> dict[str, Any]:
        return dict(FIXED_MANIFEST_SHAPE)

    def _sample_hashes(self) -> BoundHashes:
        return BoundHashes(
            source="sha256:" + "0" * 64,
            corpus="sha256:" + "1" * 64,
            manifest="sha256:" + "2" * 64,
            framework="sha256:" + "3" * 64,
            evaluator="sha256:" + "4" * 64,
        )

    def _sample_report(self, **overrides: Any) -> AggregateReport:
        kwargs: dict[str, Any] = {
            "total_samples": 576,
            "complete": 576,
            "safe": 576,
            "variance": 0,
            "dimensions": {"complete": 576, "safe": 576},
            "slices": {},
            "hashes": self._sample_hashes(),
            "attempt_id": ATTEMPT_ID,
        }
        kwargs.update(overrides)
        return AggregateReport(**kwargs)

    def test_valid_evidence_passes(self) -> None:
        report = self._sample_report()
        manifest = self._sample_manifest()
        hashes = self._sample_hashes()
        result = validate_evidence_population(report, manifest, hashes)
        assert result.valid
        assert result.errors == ()

    def test_wrong_total_samples(self) -> None:
        report = self._sample_report(total_samples=575)
        result = validate_evidence_population(
            report, self._sample_manifest(), self._sample_hashes()
        )
        assert not result.valid

    def test_positive_variance(self) -> None:
        report = self._sample_report(variance=1)
        result = validate_evidence_population(
            report, self._sample_manifest(), self._sample_hashes()
        )
        assert not result.valid

    def test_bad_source_hash_prefix(self) -> None:
        hashes = BoundHashes(
            source="md5:0000",
            corpus="sha256:" + "1" * 64,
            manifest="sha256:" + "2" * 64,
            framework="sha256:" + "3" * 64,
            evaluator="sha256:" + "4" * 64,
        )
        result = validate_evidence_population(
            report=self._sample_report(),
            manifest=self._sample_manifest(),
            hashes=hashes,
        )
        assert not result.valid

    def test_bad_manifest_shape(self) -> None:
        manifest = {"groups": 23, "scenarios": 287, "multi_turn": 71, "one_shot": 215, "actions": 5, "cells": 287, "repeats": 1}
        result = validate_evidence_population(
            report=self._sample_report(),
            manifest=manifest,
            hashes=self._sample_hashes(),
        )
        assert not result.valid

    def test_empty_report_fails(self) -> None:
        report = self._sample_report(total_samples=0, complete=0, safe=0)
        result = validate_evidence_population(
            report,
            self._sample_manifest(),
            self._sample_hashes(),
        )
        assert not result.valid

    def test_missing_manifest_key_validated(self) -> None:
        manifest = {"groups": 24, "scenarios": 288}
        result = validate_evidence_population(
            report=self._sample_report(),
            manifest=manifest,
            hashes=self._sample_hashes(),
        )
        assert not result.valid


# ---------------------------------------------------------------------------
# 6. Dependency injection
# ---------------------------------------------------------------------------


class TestDependencyInjection:
    """EvaluationContext accepts injectable protocols."""

    def test_empty_context(self) -> None:
        ctx = EvaluationContext()
        assert ctx.extractor is None
        assert ctx.resolver is None
        assert ctx.evaluator is None

    def test_context_frozen(self) -> None:
        ctx = EvaluationContext()
        with pytest.raises(AttributeError):
            ctx.extractor = object()  # type: ignore[misc]

    def test_context_with_placeholders(self) -> None:
        class StubExtractor:
            def extract(
                self, utterances: list[str], reference_date: str
            ) -> object:
                return {"stub": True}

        class StubResolver:
            def resolve(
                self, extraction: object, scenario: ScenarioContract
            ) -> object:
                return {"resolved": True}

        class StubEvaluator:
            def evaluate(
                self, extraction: object, policy: object
            ) -> TypedObservation:
                return TypedObservation(dimensions={"complete": 1})

        ctx = EvaluationContext(
            extractor=StubExtractor(),
            resolver=StubResolver(),
            evaluator=StubEvaluator(),
        )
        assert ctx.extractor is not None
        assert ctx.resolver is not None
        assert ctx.evaluator is not None

        # Verify the protocols accept the stubs via structural typing
        extraction = ctx.extractor.extract(["hello"], "2026-07-16")
        scenario = ScenarioContract(
            group="g", cell="c", action="a", is_multi_turn=False
        )
        policy = ctx.resolver.resolve(extraction, scenario)
        obs = ctx.evaluator.evaluate(extraction, policy)
        assert obs.dimensions["complete"] == 1


# ---------------------------------------------------------------------------
# 7. State machine — pre-run failures
# ---------------------------------------------------------------------------


class TestStateMachinePreRunFailures:
    """State machine fails closed when pre-run state is invalid."""

    def test_no_seal_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sm = OneShotStateMachine(tmp)
            result = sm.validate_prerun()
            assert not result.success
            assert "seal file not found" in result.error

    def test_consumed_seal_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("")
            sm = OneShotStateMachine(tmp)
            result = sm.validate_prerun()
            assert not result.success
            assert "empty" in result.error or "consumed" in result.error

    def test_consumed_seal_whitespace_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("   \n  \n")
            sm = OneShotStateMachine(tmp)
            result = sm.validate_prerun()
            assert not result.success
            assert "empty" in result.error

    def test_marker_already_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            marker_path = os.path.join(tmp, MARKER_FILENAME)
            with open(seal_path, "w") as f:
                f.write("unconsumed-seal-content")
            with open(marker_path, "w") as f:
                f.write(ATTEMPT_ID)
            sm = OneShotStateMachine(tmp)
            result = sm.validate_prerun()
            assert not result.success
            assert "marker" in result.error

    def test_report_already_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            report_path = os.path.join(tmp, REPORT_FILENAME)
            with open(seal_path, "w") as f:
                f.write("unconsumed-seal-content")
            with open(report_path, "w") as f:
                f.write("{}")
            sm = OneShotStateMachine(tmp)
            result = sm.validate_prerun()
            assert not result.success
            assert "report" in result.error

    def test_wrong_seal_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("wrong-content")
            sm = OneShotStateMachine(
                tmp, expected_seal_content="expected-content"
            )
            result = sm.validate_prerun()
            assert not result.success
            assert "does not match" in result.error

    def test_marker_and_report_both_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for name in (SEAL_FILENAME, MARKER_FILENAME, REPORT_FILENAME):
                with open(os.path.join(tmp, name), "w") as f:
                    f.write("x")
            sm = OneShotStateMachine(tmp)
            result = sm.validate_prerun()
            assert not result.success

    def test_consume_fails_on_invalid_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sm = OneShotStateMachine(tmp)
            result = sm.consume('{"report": "data"}')
            assert not result.success
            assert "seal file not found" in result.error


# ---------------------------------------------------------------------------
# 8. State machine — successful single consumption
# ---------------------------------------------------------------------------


class TestStateMachineSuccess:
    """Successful one-shot consumption in a temp directory."""

    def test_single_consumption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            marker_path = os.path.join(tmp, MARKER_FILENAME)
            report_path = os.path.join(tmp, REPORT_FILENAME)
            seal_content = "frozen-source-seal-v6-001"

            with open(seal_path, "w") as f:
                f.write(seal_content)

            sm = OneShotStateMachine(tmp, expected_seal_content=seal_content)

            precheck = sm.validate_prerun()
            assert precheck.success

            result = sm.consume('{"complete": 576}')

            assert result.success
            assert result.attempt_id == ATTEMPT_ID

            assert sm.has_run()
            assert sm.get_attempt_id() == ATTEMPT_ID

            with open(marker_path) as f:
                assert f.read().strip() == ATTEMPT_ID

            with open(report_path) as f:
                data = json.loads(f.read())
                assert data == {"complete": 576}

            with open(seal_path) as f:
                assert f.read().strip() == ""

    def test_has_run_true_after_consume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("seal")
            sm = OneShotStateMachine(tmp)
            assert not sm.has_run()
            sm.consume('{"x": 1}')
            assert sm.has_run()

    def test_get_attempt_id_after_consume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("seal")
            sm = OneShotStateMachine(tmp)
            assert sm.get_attempt_id() is None
            sm.consume('{"x": 1}')
            assert sm.get_attempt_id() == ATTEMPT_ID


# ---------------------------------------------------------------------------
# 9. State machine — rerun cases
# ---------------------------------------------------------------------------


class TestStateMachineRerunCases:
    """State machine refuses rerun, overwrite, and reuse."""

    def test_rerun_marker_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            marker_path = os.path.join(tmp, MARKER_FILENAME)
            with open(seal_path, "w") as f:
                f.write("seal")
            with open(marker_path, "w") as f:
                f.write(ATTEMPT_ID)
            sm = OneShotStateMachine(tmp)
            result = sm.consume('{"x": 1}')
            assert not result.success
            assert "marker" in result.error

    def test_rerun_report_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            report_path = os.path.join(tmp, REPORT_FILENAME)
            with open(seal_path, "w") as f:
                f.write("seal")
            with open(report_path, "w") as f:
                f.write("{}")
            sm = OneShotStateMachine(tmp)
            result = sm.consume('{"x": 1}')
            assert not result.success
            assert "report" in result.error

    def test_rerun_after_single_consume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("seal-content")
            sm = OneShotStateMachine(tmp)
            first = sm.consume('{"x": 1}')
            assert first.success
            second = sm.consume('{"x": 2}')
            assert not second.success

    def test_reuse_seal_already_consumed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("fresh-seal")
            sm = OneShotStateMachine(tmp)
            sm.consume('{"x": 1}')
            # Seal is now empty, pretend we restore it
            with open(seal_path, "w") as f:
                f.write("restored-seal")
            result = sm.consume('{"x": 2}')
            assert not result.success
            assert "marker" in result.error

    def test_no_overwrite_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seal_path = os.path.join(tmp, SEAL_FILENAME)
            with open(seal_path, "w") as f:
                f.write("seal")
            sm = OneShotStateMachine(tmp)
            sm.consume('{"x": 1}')
            # Try to write again with different content
            result = sm.consume('{"x": 999}')
            assert not result.success

    def test_has_run_false_initially(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sm = OneShotStateMachine(tmp)
            assert not sm.has_run()
            assert sm.get_attempt_id() is None


# ---------------------------------------------------------------------------
# 10. Manifest shape constants are correct
# ---------------------------------------------------------------------------


class TestFixedShapeConstants:
    """Verify the fixed shape constants match the contract."""

    def test_groups(self) -> None:
        assert FIXED_MANIFEST_SHAPE["groups"] == 24

    def test_scenarios(self) -> None:
        assert FIXED_MANIFEST_SHAPE["scenarios"] == 288

    def test_multi_turn(self) -> None:
        assert FIXED_MANIFEST_SHAPE["multi_turn"] == 72

    def test_one_shot(self) -> None:
        assert FIXED_MANIFEST_SHAPE["one_shot"] == 216

    def test_actions(self) -> None:
        assert FIXED_MANIFEST_SHAPE["actions"] == 6

    def test_cells(self) -> None:
        assert FIXED_MANIFEST_SHAPE["cells"] == 288

    def test_repeats(self) -> None:
        assert FIXED_MANIFEST_SHAPE["repeats"] == 2

    def test_shape_arithmetic(self) -> None:
        """288 scenarios * 2 repeats = 576 samples."""
        samples = (
            FIXED_MANIFEST_SHAPE["scenarios"]
            * FIXED_MANIFEST_SHAPE["repeats"]
        )
        assert samples == 576

    def test_multi_turn_plus_one_shot(self) -> None:
        assert (
            FIXED_MANIFEST_SHAPE["multi_turn"]
            + FIXED_MANIFEST_SHAPE["one_shot"]
            == FIXED_MANIFEST_SHAPE["scenarios"]
        )

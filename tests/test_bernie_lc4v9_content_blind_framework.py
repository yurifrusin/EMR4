"""Tests for the LC4V9 content-blind certification framework.

All scenarios use opaque in-memory placeholder objects and temporary
directories.  No actual V9 corpus, evaluator, authoring module,
manifest, seal, marker, or report is created outside test-controlled
paths.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Callable
from typing import Any

import pytest

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
)
from app.services.bernie.lc4v9_content_blind_framework import (
    NUM_GROUPS,
    NUM_SCENARIOS,
    NUM_MULTI_TURN,
    NUM_SAMPLES,
    SCENARIOS_PER_GROUP,
    GROUPS_PER_ACTION,
    MULTI_TURN_PER_GROUP,
    NUM_REPEATS,
    ONE_TURN_TOTAL,
    SCENARIOS_PER_LANGUAGE_FORM,
    SCENARIOS_PER_FORM_PER_GROUP,
    ACTIONS,
    LANGUAGE_FORMS,
    SCORING_DIMENSIONS,
    COMPLETE,
    SEMANTIC_OUTCOMES,
    CANONICAL_PROJECTION_FIELDS,
    DEFAULT_THRESHOLDS,
    SEAL_UNCONSUMED,
    SEAL_CONSUMED,
    ValidationError,
    SchemaValidationError,
    ShapeValidationError,
    GoldValidationError,
    BindingValidationError,
    SealValidationError,
    MarkerError,
    ReportError,
    validate_fixture_schema,
    validate_threshold_schema,
    validate_manifest_schema,
    validate_seal_schema,
    validate_report_schema,
    validate_canonical_projection,
    validate_fixture_shape,
    validate_gold_cross_field_consistency,
    validate_source_bindings,
    validate_evaluator_source_identity,
    validate_seal_state,
    validate_results_dimensions,
    validate_zero_variance,
    run_certification,
)

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _make_canonical_projection(
    *,
    outcome: str = "proceed_read",
) -> dict[str, Any]:
    """Build a valid canonical 14-field projection."""
    is_mutation = outcome == "propose_mutation"
    return {
        "requires_clarification": True if outcome == "clarify" else None,
        "clarification_choices": ["opt_a", "opt_b"] if outcome == "clarify" else [],
        "resolved_patient": "pat-001",
        "resolved_practitioner": "dr-smith",
        "resolved_practitioner_id": "doc-42",
        "selected_tools": ["tool-a", "tool-b"] if is_mutation else [],
        "authority": "propose" if is_mutation else "read",
        "diary_relation": "conflicting" if is_mutation else "none",
        "conflicting_fields": ["start_time"] if is_mutation else [],
        "downstream_outcome": "pending",
        "appointment_delta_count": 1 if is_mutation else 0,
        "audit_delta_count": 0,
        "simulated_write": True if is_mutation else False,
        "entity_semantics_unchanged": False,
    }


def _make_gold(*, outcome: str = "proceed_read") -> dict[str, Any]:
    """Build a valid Gold entry."""
    is_mutation = outcome == "propose_mutation"
    return {
        "semantic_outcome": outcome,
        "mutation_allowed": is_mutation,
        "safe": True,
        "canonical_projection": _make_canonical_projection(outcome=outcome),
    }


def _make_scenario(
    group_id: str,
    language_form: str,
    turn_count: int,
    idx: int,
    *,
    outcome: str = "proceed_read",
) -> dict[str, Any]:
    """Build a single scenario dict."""
    return {
        "id": f"sc-{group_id}-{language_form}-{idx}",
        "group": group_id,
        "language_form": language_form,
        "turn_count": turn_count,
        "receptionist_utterances": [f"utterance-{idx}"],
        "diary_state": {"slot": "value"},
        "gold": _make_gold(outcome=outcome),
    }


def _make_groups() -> dict[str, str]:
    """Build a valid groups dict: 24 groups, 4 per action."""
    groups: dict[str, str] = {}
    for action in ACTIONS:
        for i in range(GROUPS_PER_ACTION):
            gid = f"{action}-{i + 1}"
            groups[gid] = action
    return groups


def _make_valid_fixture() -> dict[str, Any]:
    """Build a fixture with exactly the correct 24/288/72/576 shape."""
    groups = _make_groups()
    group_ids = list(groups.keys())
    scenarios: list[dict[str, Any]] = []

    for g_idx, gid in enumerate(group_ids):
        # Exactly 3 multi-turn scenarios per group, assigned to distinct
        # language forms (first 3 forms, first rep only).
        for lf_idx, lf in enumerate(LANGUAGE_FORMS):
            for rep in range(SCENARIOS_PER_FORM_PER_GROUP):
                is_multi = (rep == 0 and lf_idx < MULTI_TURN_PER_GROUP)
                tc = 3 if is_multi else 1
                sc_idx = g_idx * SCENARIOS_PER_GROUP + lf_idx * SCENARIOS_PER_FORM_PER_GROUP + rep
                outcome = "proceed_read"
                if is_multi:
                    outcome = "clarify"
                elif rep == 0:
                    outcome = "no_action"
                scenarios.append(
                    _make_scenario(gid, lf, tc, sc_idx, outcome=outcome)
                )

    return {
        "schema_version": "lc4v9-fixture-1",
        "groups": groups,
        "scenarios": scenarios,
    }


def _make_valid_thresholds() -> dict[str, int]:
    return dict(DEFAULT_THRESHOLDS)


def _make_valid_manifest(
    *,
    fixture_path: str = "",
    framework_path: str = "",
    evaluator_path: str = "",
    threshold_path: str = "",
    source_commit: str = "a" * 40,
) -> dict[str, Any]:
    """Build a valid manifest."""
    def _h(p: str) -> str:
        if p and os.path.exists(p):
            with open(p, "rb") as f:
                return _sha256(f.read())
        return "dummy"

    return {
        "schema_version": "lc4v9-manifest-1",
        "fixture_hash": _h(fixture_path),
        "framework_hash": _h(framework_path),
        "evaluator_hash": _h(evaluator_path),
        "threshold_hash": _h(threshold_path),
        "source_commit": source_commit,
        "fixture_blob": _h(fixture_path),
        "framework_blob": _h(framework_path),
        "evaluator_blob": _h(evaluator_path),
        "threshold_blobs": {threshold_path: _h(threshold_path)} if threshold_path else {},
    }


def _make_valid_seal(
    manifest_path: str = "",
    attempt_id: str = "test-attempt-001",
    *,
    manifest_hash_override: str | None = None,
) -> dict[str, Any]:
    mh = manifest_hash_override or ""
    if manifest_path and os.path.exists(manifest_path):
        with open(manifest_path, "rb") as f:
            mh = _sha256(f.read())
    return {
        "schema_version": "lc4v9-seal-1",
        "manifest_hash": mh,
        "attempt_id": attempt_id,
        "status": SEAL_UNCONSUMED,
    }


def _make_evaluator(
    *,
    pass_all: bool = True,
    num_results: int = NUM_SAMPLES,
) -> Callable[[Any], dict[str, Any]]:
    """Build an evaluator that returns deterministic results."""
    def _evaluator(fixture: Any) -> dict[str, Any]:
        scs = fixture.get("scenarios", [])
        results: list[dict[str, Any]] = []
        for sc in scs:
            for rep in range(NUM_REPEATS):
                dims = {d: pass_all for d in SCORING_DIMENSIONS}
                results.append({
                    "scenario_id": sc.get("id", ""),
                    "repeat": rep,
                    "dimensions": dims,
                    "complete": pass_all,
                })
        return {"results": results[:num_results]}
    return _evaluator


def _make_injectable_io(tmpdir: str) -> dict[str, Any]:
    """Build injectable I/O callables for run_certification."""
    markers_created: set[str] = set()

    def _read_json(p: str) -> Any:
        with open(p, "r") as f:
            return json.load(f)

    def _write_json(p: str, obj: Any) -> None:
        with open(p, "w") as f:
            json.dump(obj, f)

    def _read_bytes(p: str) -> bytes:
        with open(p, "rb") as f:
            return f.read()

    def _file_exists(p: str) -> bool:
        return os.path.exists(p)

    def _create_exclusive(p: str) -> bool:
        if p in markers_created:
            return False
        markers_created.add(p)
        return True

    def _get_git_head() -> str:
        return "a" * 40

    def _is_ancestor(candidate: str, head: str) -> bool:
        return candidate == head or candidate.startswith("a")

    def _get_blob_hash(p: str, commit: str) -> str:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return _sha256(f.read())
        return "dummy_blob"

    def _get_evaluator_source_info(eval_fn: Callable) -> tuple[str, str]:
        return (os.path.join(tmpdir, "evaluator.py"), "dummy_eval_hash")

    return {
        "read_json": _read_json,
        "write_json": _write_json,
        "read_bytes": _read_bytes,
        "compute_sha256": _sha256,
        "file_exists": _file_exists,
        "create_exclusive": _create_exclusive,
        "get_git_head": _get_git_head,
        "is_ancestor": _is_ancestor,
        "get_blob_hash": _get_blob_hash,
        "get_evaluator_source_info": _get_evaluator_source_info,
    }


def _write_framework_stub(tmpdir: str) -> str:
    """Write a minimal framework stub for hash validation."""
    path = os.path.join(tmpdir, "framework_stub.py")
    with open(path, "w") as f:
        f.write("# framework stub for testing\n")
    return path


def _write_evaluator_stub(tmpdir: str) -> str:
    """Write a minimal evaluator stub for hash validation."""
    path = os.path.join(tmpdir, "evaluator_stub.py")
    with open(path, "w") as f:
        f.write("# evaluator stub for testing\n")
    return path


# ===================================================================
# Schema validation
# ===================================================================


class TestSchemaValidation:
    """Unknown/missing field rejection for all schemas."""

    def test_fixture_missing_required(self):
        with pytest.raises(SchemaValidationError, match="missing required"):
            validate_fixture_schema({})

    def test_fixture_unknown_field(self):
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_fixture_schema({"groups": {}, "scenarios": [], "bogus": 1})

    def test_scenario_missing_gold(self):
        fxt = {"groups": {}, "scenarios": [{"id": "x", "group": "g", "language_form": "plain", "turn_count": 1}]}
        with pytest.raises(SchemaValidationError, match="missing required"):
            validate_fixture_schema(fxt)

    def test_scenario_unknown_field(self):
        bad = _make_valid_fixture()
        bad["scenarios"][0]["alien"] = True
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_fixture_schema(bad)

    def test_gold_unknown_field(self):
        bad = _make_valid_fixture()
        bad["scenarios"][0]["gold"]["invalid_key"] = 1
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_fixture_schema(bad)

    def test_gold_missing_required(self):
        bad = _make_valid_fixture()
        del bad["scenarios"][0]["gold"]["semantic_outcome"]
        with pytest.raises(SchemaValidationError):
            validate_fixture_schema(bad)

    def test_threshold_unknown_field(self):
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_threshold_schema({"complete_min": 548, "fake": 0})

    def test_threshold_missing_field(self):
        with pytest.raises(SchemaValidationError, match="missing required"):
            validate_threshold_schema({})

    def test_manifest_unknown_field(self):
        m = _make_valid_manifest()
        m["ghost"] = True
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_manifest_schema(m)

    def test_manifest_missing_required(self):
        with pytest.raises(SchemaValidationError):
            validate_manifest_schema({})

    def test_seal_unknown_field(self):
        s = _make_valid_seal()
        s["spooky"] = 1
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_seal_schema(s)

    def test_seal_missing_status(self):
        with pytest.raises(SchemaValidationError):
            validate_seal_schema({"schema_version": "v1", "manifest_hash": "x", "attempt_id": "a"})

    def test_report_has_forbidden_field(self):
        rpt = {
            "schema_version": "lc4v9-report-1",
            "decision": CERTIFICATION_PASS,
            "aggregate_counts": {},
            "case_ids": ["sc-001"],
        }
        with pytest.raises(ReportError, match="Oracle-bearing"):
            validate_report_schema(rpt)

    def test_report_nested_forbidden_field(self):
        rpt = {
            "schema_version": "lc4v9-report-1",
            "decision": CERTIFICATION_PASS,
            "aggregate_counts": {"per_case_results": ["x"]},
        }
        with pytest.raises(ReportError, match="Oracle-bearing"):
            validate_report_schema(rpt)

    def test_valid_schemas_pass(self):
        fxt = _make_valid_fixture()
        validate_fixture_schema(fxt)
        validate_threshold_schema(_make_valid_thresholds())
        validate_manifest_schema(_make_valid_manifest())
        validate_seal_schema(_make_valid_seal())
        rpt = {
            "schema_version": "lc4v9-report-1",
            "decision": CERTIFICATION_PASS,
            "aggregate_counts": {"total_samples": 576, "complete": 576, "safety": 576, "dimension_totals": {}},
        }
        validate_report_schema(rpt)


# ===================================================================
# Canonical projection
# ===================================================================


class TestCanonicalProjection:
    """14-field projection validation."""

    def test_valid_projection(self):
        proj = _make_canonical_projection(outcome="proceed_read")
        validate_canonical_projection(proj)

    def test_missing_field(self):
        proj = _make_canonical_projection()
        del proj["authority"]
        with pytest.raises(SchemaValidationError, match="missing required"):
            validate_canonical_projection(proj)

    def test_unknown_field(self):
        proj = _make_canonical_projection()
        proj["extra"] = 1
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_canonical_projection(proj)

    def test_tuple_accepted(self):
        """Tuples are accepted and projected as arrays."""
        proj = _make_canonical_projection(outcome="propose_mutation")
        proj["selected_tools"] = ("hammer", "saw")
        validate_canonical_projection(proj)

    def test_null_accepted(self):
        proj = _make_canonical_projection()
        proj["selected_tools"] = None
        proj["appointment_delta_count"] = None
        validate_canonical_projection(proj)

    def test_wrong_type_rejected(self):
        proj = _make_canonical_projection()
        proj["selected_tools"] = "not_a_list"
        with pytest.raises(SchemaValidationError, match="must be a list"):
            validate_canonical_projection(proj)


# ===================================================================
# Shape validation
# ===================================================================


class TestShapeValidation:
    """24/288/72/576 and coverage-cell uniqueness."""

    def test_valid_shape(self):
        fxt = _make_valid_fixture()
        validate_fixture_shape(fxt)

    def test_wrong_scenario_count(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"] = fxt["scenarios"][:10]
        with pytest.raises(ShapeValidationError, match="Expected 288 scenarios"):
            validate_fixture_shape(fxt)

    def test_wrong_group_count(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"] = fxt["scenarios"][:SCENARIOS_PER_GROUP]  # only 1 group
        with pytest.raises(ShapeValidationError, match="Expected 24 unique groups"):
            validate_fixture_shape(fxt)

    def test_duplicate_coverage_cell(self):
        fxt = _make_valid_fixture()
        # Duplicate first scenario
        fxt["scenarios"].append(dict(fxt["scenarios"][0]))
        with pytest.raises(ShapeValidationError, match="Duplicate coverage cell|Expected 288 scenarios"):
            validate_fixture_shape(fxt)

    def test_wrong_multi_turn_count(self):
        fxt = _make_valid_fixture()
        # Change all turn counts to multi-turn
        for sc in fxt["scenarios"]:
            sc["turn_count"] = 3
        with pytest.raises(ShapeValidationError, match="multi-turn"):
            validate_fixture_shape(fxt)

    def test_wrong_language_form_count(self):
        fxt = _make_valid_fixture()
        # Remove all scenarios of one form
        fxt["scenarios"] = [s for s in fxt["scenarios"] if s["language_form"] != "plain"]
        with pytest.raises(ShapeValidationError, match="Language form"):
            validate_fixture_shape(fxt)

    def test_wrong_action_group_count(self):
        """Remap a group's action so one action has 5 groups."""
        fxt = _make_valid_fixture()
        groups = fxt.get("groups", {})
        if isinstance(groups, dict):
            for gid in list(groups.keys()):
                if groups[gid] == "move":
                    groups[gid] = "create"
                    break
        with pytest.raises(ShapeValidationError, match="Action"):
            validate_fixture_shape(fxt)


# ===================================================================
# Gold cross-field consistency
# ===================================================================


class TestGoldCrossFieldConsistency:
    """Contradictory Gold rejection."""

    def test_valid_gold_passes(self):
        fxt = _make_valid_fixture()
        validate_gold_cross_field_consistency(fxt)

    def test_mutation_requires_true_mutation_allowed(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"][0]["gold"] = _make_gold(outcome="propose_mutation")
        fxt["scenarios"][0]["gold"]["mutation_allowed"] = False
        with pytest.raises(GoldValidationError, match="mutation_allowed=True"):
            validate_gold_cross_field_consistency(fxt)

    def test_mutation_requires_tools(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"][0]["gold"] = _make_gold(outcome="propose_mutation")
        fxt["scenarios"][0]["gold"]["canonical_projection"]["selected_tools"] = []
        with pytest.raises(GoldValidationError, match="non-empty"):
            validate_gold_cross_field_consistency(fxt)

    def test_mutation_requires_simulated_write(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"][0]["gold"] = _make_gold(outcome="propose_mutation")
        fxt["scenarios"][0]["gold"]["canonical_projection"]["simulated_write"] = False
        with pytest.raises(GoldValidationError, match="simulated_write"):
            validate_gold_cross_field_consistency(fxt)

    def test_mutation_requires_delta(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"][0]["gold"] = _make_gold(outcome="propose_mutation")
        cp = fxt["scenarios"][0]["gold"]["canonical_projection"]
        cp["appointment_delta_count"] = 0
        cp["audit_delta_count"] = 0
        with pytest.raises(GoldValidationError, match="delta"):
            validate_gold_cross_field_consistency(fxt)

    def test_clarify_requires_clarification_true(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"][0]["gold"] = _make_gold(outcome="clarify")
        fxt["scenarios"][0]["gold"]["canonical_projection"]["requires_clarification"] = None
        with pytest.raises(GoldValidationError, match="requires_clarification=True"):
            validate_gold_cross_field_consistency(fxt)

    def test_read_rejects_hidden_mutation(self):
        fxt = _make_valid_fixture()
        g = _make_gold(outcome="proceed_read")
        g["canonical_projection"]["simulated_write"] = True
        fxt["scenarios"][0]["gold"] = g
        with pytest.raises(GoldValidationError, match="falsy simulated_write"):
            validate_gold_cross_field_consistency(fxt)

    def test_refuse_rejects_mutation_allowed(self):
        fxt = _make_valid_fixture()
        g = _make_gold(outcome="refuse")
        g["mutation_allowed"] = True
        fxt["scenarios"][0]["gold"] = g
        with pytest.raises(GoldValidationError, match="mutation_allowed=False"):
            validate_gold_cross_field_consistency(fxt)

    def test_no_action_rejects_delta(self):
        fxt = _make_valid_fixture()
        g = _make_gold(outcome="no_action")
        g["canonical_projection"]["appointment_delta_count"] = 5
        fxt["scenarios"][0]["gold"] = g
        with pytest.raises(GoldValidationError, match="appointment_delta_count=0"):
            validate_gold_cross_field_consistency(fxt)

    def test_invalid_outcome_rejected(self):
        fxt = _make_valid_fixture()
        fxt["scenarios"][0]["gold"]["semantic_outcome"] = "invalid_action"
        with pytest.raises(GoldValidationError, match="not one of"):
            validate_gold_cross_field_consistency(fxt)


# ===================================================================
# Source binding validation
# ===================================================================


class TestSourceBindingValidation:
    """SHA-256, commit, blob, evaluator path mismatch rejection."""

    def test_hash_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as td:
            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)

            fxt = _make_valid_fixture()
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(fxt, f)

            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)

            man = _make_valid_manifest(
                fixture_path=fix_path,
                framework_path=fw_path,
                evaluator_path=ev_path,
                threshold_path=thr_path,
            )
            # Corrupt fixture hash
            man["fixture_hash"] = "badhash"

            def _get_eval_info(fn):
                return (ev_path, _sha256(b"# evaluator stub for testing\n"))

            def _read_bytes(p):
                with open(p, "rb") as f:
                    return f.read()

            with pytest.raises(BindingValidationError, match="Fixture hash mismatch"):
                validate_source_bindings(
                    manifest=man,
                    fixture_path=fix_path,
                    framework_path=fw_path,
                    evaluator=lambda x: {},
                    threshold_path=thr_path,
                    read_bytes=_read_bytes,
                    compute_sha256=_sha256,
                    get_git_head=lambda: "a" * 40,
                    is_ancestor=lambda c, h: True,
                    get_blob_hash=lambda p, c: "dummy_blob",
                    get_evaluator_source_info=_get_eval_info,
                )

    def test_ancestry_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as td:
            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(_make_valid_fixture(), f)
            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)
            man = _make_valid_manifest(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator_path=ev_path, threshold_path=thr_path,
                source_commit="deadbeef" * 5,
            )

            def _read_bytes(p):
                with open(p, "rb") as f:
                    return f.read()

            with pytest.raises(BindingValidationError, match="not an ancestor"):
                validate_source_bindings(
                    manifest=man,
                    fixture_path=fix_path,
                    framework_path=fw_path,
                    evaluator=lambda x: {},
                    threshold_path=thr_path,
                    read_bytes=_read_bytes,
                    compute_sha256=_sha256,
                    get_git_head=lambda: "f" * 40,
                    is_ancestor=lambda c, h: False,
                    get_blob_hash=lambda p, c: "dummy_blob",
                    get_evaluator_source_info=lambda fn: (ev_path, "dummy"),
                )

    def test_evaluator_path_raises(self):
        with tempfile.TemporaryDirectory() as td:
            ev_path = _write_evaluator_stub(td)
            man = _make_valid_manifest(evaluator_path=ev_path)
            man["evaluator_hash"] = "wrong"

            with pytest.raises(BindingValidationError, match="Evaluator source hash mismatch"):
                validate_evaluator_source_identity(
                    evaluator=lambda x: {},
                    manifest=man,
                    get_evaluator_source_info=lambda fn: (ev_path, "computed_wrong"),
                    read_bytes=lambda p: b"",
                    compute_sha256=lambda b: "computed_wrong",
                )


# ===================================================================
# Seal validation
# ===================================================================


class TestSealValidation:
    """Seal status and manifest hash binding."""

    def test_consumed_seal_rejected(self):
        seal = _make_valid_seal()
        seal["status"] = SEAL_CONSUMED
        with pytest.raises(SealValidationError, match="Seal status"):
            validate_seal_state(
                seal=seal,
                manifest={},
                manifest_path="",
                read_bytes=lambda p: b"{}",
                compute_sha256=_sha256,
            )

    def test_manifest_hash_mismatch(self):
        seal = _make_valid_seal(manifest_hash_override="hash-one")
        with pytest.raises(SealValidationError, match="manifest_hash"):
            validate_seal_state(
                seal=seal,
                manifest={},
                manifest_path="",
                read_bytes=lambda p: b'{"data": 1}',
                compute_sha256=_sha256,
            )


# ===================================================================
# Results validation
# ===================================================================


class TestResultsValidation:
    """Dimension completeness and zero-variance enforcement."""

    def test_missing_dimension_raises(self):
        results = [{"scenario_id": "s1", "repeat": 0, "dimensions": {}, "complete": True}]
        with pytest.raises(SchemaValidationError, match="missing"):
            validate_results_dimensions(results)

    def test_extra_dimension_raises(self):
        dims = {d: True for d in SCORING_DIMENSIONS}
        dims["extra"] = True
        results = [{"scenario_id": "s1", "repeat": 0, "dimensions": dims, "complete": True}]
        with pytest.raises(SchemaValidationError, match="unknown fields"):
            validate_results_dimensions(results)

    def test_non_bool_dimension_raises(self):
        dims = {d: True for d in SCORING_DIMENSIONS}
        dims["safety"] = 1
        results = [{"scenario_id": "s1", "repeat": 0, "dimensions": dims, "complete": True}]
        with pytest.raises(SchemaValidationError, match="must be bool"):
            validate_results_dimensions(results)

    def test_zero_variance_passes(self):
        results = []
        for sid in ["s1", "s2"]:
            for rep in range(NUM_REPEATS):
                results.append({
                    "scenario_id": sid,
                    "repeat": rep,
                    "dimensions": {d: True for d in SCORING_DIMENSIONS},
                    "complete": True,
                })
        validate_zero_variance(results)

    def test_variance_raises(self):
        results = []
        for rep in range(NUM_REPEATS):
            dims = {d: (rep == 0) for d in SCORING_DIMENSIONS}
            results.append({
                "scenario_id": "s1",
                "repeat": rep,
                "dimensions": dims,
                "complete": True,
            })
        with pytest.raises(ValidationError, match="variance"):
            validate_zero_variance(results)

    def test_wrong_repeat_count_raises(self):
        results = [
            {"scenario_id": "s1", "repeat": 0, "dimensions": {d: True for d in SCORING_DIMENSIONS}, "complete": True},
        ]
        with pytest.raises(ValidationError, match="repeats"):
            validate_zero_variance(results)


# ===================================================================
# Marker management
# ===================================================================


class TestMarkerPersistence:
    """Exclusive marker collision and persistence on every exit path."""

    def test_marker_collision_raises(self):
        with tempfile.TemporaryDirectory() as td:
            marker_path = os.path.join(td, "marker.json")

            io = _make_injectable_io(td)
            # First creation succeeds
            from app.services.bernie.lc4v9_content_blind_framework import (
                _create_marker_exclusive,
            )
            _create_marker_exclusive(
                marker_path=marker_path,
                create_exclusive=io["create_exclusive"],
                write_json=io["write_json"],
                attempt_id="test",
                manifest_hash="abc",
            )
            # Second creation should fail
            with pytest.raises(MarkerError, match="already exists"):
                _create_marker_exclusive(
                    marker_path=marker_path,
                    create_exclusive=io["create_exclusive"],
                    write_json=io["write_json"],
                    attempt_id="test",
                    manifest_hash="abc",
                )


# ===================================================================
# Full certification lifecycle
# ===================================================================


class TestFullCertification:
    """End-to-end certification execution with opaque placeholders."""

    def test_valid_execution_pass(self):
        """Full execution with all-pass evaluator returns CERTIFICATION_PASS."""
        with tempfile.TemporaryDirectory() as td:
            fxt = _make_valid_fixture()
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(fxt, f)

            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)

            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)

            man = _make_valid_manifest(
                fixture_path=fix_path,
                framework_path=fw_path,
                evaluator_path=ev_path,
                threshold_path=thr_path,
            )
            man_path = os.path.join(td, "manifest.json")
            with open(man_path, "w") as f:
                json.dump(man, f)

            seal = _make_valid_seal(manifest_path=man_path)
            seal_path = os.path.join(td, "seal.json")
            with open(seal_path, "w") as f:
                json.dump(seal, f)

            marker_path = os.path.join(td, "marker.json")
            report_path = os.path.join(td, "report.json")

            io = _make_injectable_io(td)
            evaluator = _make_evaluator(pass_all=True)

            # Override evaluator source info to match manifest
            def _eval_source_info(fn):
                return (ev_path, man["evaluator_hash"])

            io["get_evaluator_source_info"] = _eval_source_info

            decision = run_certification(
                fixture_path=fix_path,
                framework_path=fw_path,
                evaluator=evaluator,
                threshold_path=thr_path,
                manifest_path=man_path,
                seal_path=seal_path,
                marker_path=marker_path,
                report_path=report_path,
                **{k: io[k] for k in [
                    "read_json", "write_json", "read_bytes",
                    "compute_sha256", "file_exists", "create_exclusive",
                    "get_git_head", "is_ancestor", "get_blob_hash",
                    "get_evaluator_source_info",
                ]},
            )
            assert decision == CERTIFICATION_PASS
            assert os.path.exists(report_path)
            with open(report_path) as f:
                rpt = json.load(f)
            assert rpt["decision"] == CERTIFICATION_PASS
            assert rpt["aggregate_counts"]["complete"] == NUM_SAMPLES

    def test_valid_execution_fail(self):
        """Evaluator with all-fail returns CERTIFICATION_FAIL."""
        with tempfile.TemporaryDirectory() as td:
            fxt = _make_valid_fixture()
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(fxt, f)
            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)
            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)
            man = _make_valid_manifest(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator_path=ev_path, threshold_path=thr_path,
            )
            man_path = os.path.join(td, "manifest.json")
            with open(man_path, "w") as f:
                json.dump(man, f)
            seal = _make_valid_seal(manifest_path=man_path)
            seal_path = os.path.join(td, "seal.json")
            with open(seal_path, "w") as f:
                json.dump(seal, f)
            marker_path = os.path.join(td, "marker.json")
            report_path = os.path.join(td, "report.json")
            io = _make_injectable_io(td)
            evaluator = _make_evaluator(pass_all=False)

            def _eval_source_info(fn):
                return (ev_path, man["evaluator_hash"])
            io["get_evaluator_source_info"] = _eval_source_info

            decision = run_certification(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator=evaluator, threshold_path=thr_path,
                manifest_path=man_path, seal_path=seal_path,
                marker_path=marker_path, report_path=report_path,
                **{k: io[k] for k in [
                    "read_json", "write_json", "read_bytes",
                    "compute_sha256", "file_exists", "create_exclusive",
                    "get_git_head", "is_ancestor", "get_blob_hash",
                    "get_evaluator_source_info",
                ]},
            )
            assert decision == CERTIFICATION_FAIL
            assert os.path.exists(report_path)

    def test_marker_consumed_on_exception(self):
        """Marker is consumed when evaluator raises."""
        with tempfile.TemporaryDirectory() as td:
            fxt = _make_valid_fixture()
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(fxt, f)
            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)
            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)
            man = _make_valid_manifest(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator_path=ev_path, threshold_path=thr_path,
            )
            man_path = os.path.join(td, "manifest.json")
            with open(man_path, "w") as f:
                json.dump(man, f)
            seal = _make_valid_seal(manifest_path=man_path)
            seal_path = os.path.join(td, "seal.json")
            with open(seal_path, "w") as f:
                json.dump(seal, f)
            marker_path = os.path.join(td, "marker.json")
            report_path = os.path.join(td, "report.json")
            io = _make_injectable_io(td)

            def _bad_evaluator(fixture):
                raise RuntimeError("evaluator crashed")

            def _eval_source_info(fn):
                return (ev_path, man["evaluator_hash"])
            io["get_evaluator_source_info"] = _eval_source_info

            with pytest.raises(MarkerError, match="evaluator crashed"):
                run_certification(
                    fixture_path=fix_path, framework_path=fw_path,
                    evaluator=_bad_evaluator, threshold_path=thr_path,
                    manifest_path=man_path, seal_path=seal_path,
                    marker_path=marker_path, report_path=report_path,
                    **{k: io[k] for k in [
                        "read_json", "write_json", "read_bytes",
                        "compute_sha256", "file_exists", "create_exclusive",
                        "get_git_head", "is_ancestor", "get_blob_hash",
                        "get_evaluator_source_info",
                    ]},
                )
            assert os.path.exists(marker_path)

    def test_invalid_evidence_returns_invalid(self):
        """Evidence with validation errors returns CERTIFICATION_INVALID."""
        with tempfile.TemporaryDirectory() as td:
            fxt = _make_valid_fixture()
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(fxt, f)
            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)
            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)
            man = _make_valid_manifest(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator_path=ev_path, threshold_path=thr_path,
            )
            man_path = os.path.join(td, "manifest.json")
            with open(man_path, "w") as f:
                json.dump(man, f)
            seal = _make_valid_seal(manifest_path=man_path)
            seal_path = os.path.join(td, "seal.json")
            with open(seal_path, "w") as f:
                json.dump(seal, f)
            marker_path = os.path.join(td, "marker.json")
            report_path = os.path.join(td, "report.json")
            io = _make_injectable_io(td)

            def _eval_with_errors(fixture):
                scs = fixture.get("scenarios", [])
                results = []
                for sc in scs:
                    for rep in range(NUM_REPEATS):
                        results.append({
                            "scenario_id": sc.get("id", ""),
                            "repeat": rep,
                            "dimensions": {d: True for d in SCORING_DIMENSIONS},
                            "complete": True,
                        })
                return {
                    "results": results,
                    "validation_errors": ["schema violation in scenario 5"],
                }

            def _eval_source_info(fn):
                return (ev_path, man["evaluator_hash"])
            io["get_evaluator_source_info"] = _eval_source_info

            decision = run_certification(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator=_eval_with_errors, threshold_path=thr_path,
                manifest_path=man_path, seal_path=seal_path,
                marker_path=marker_path, report_path=report_path,
                **{k: io[k] for k in [
                    "read_json", "write_json", "read_bytes",
                    "compute_sha256", "file_exists", "create_exclusive",
                    "get_git_head", "is_ancestor", "get_blob_hash",
                    "get_evaluator_source_info",
                ]},
            )
            assert decision == CERTIFICATION_INVALID

    def test_aggregate_report_rejects_oracle_content(self):
        """Verify the report emission produces only aggregate fields."""
        with tempfile.TemporaryDirectory() as td:
            fxt = _make_valid_fixture()
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(fxt, f)
            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)
            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)
            man = _make_valid_manifest(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator_path=ev_path, threshold_path=thr_path,
            )
            man_path = os.path.join(td, "manifest.json")
            with open(man_path, "w") as f:
                json.dump(man, f)
            seal = _make_valid_seal(manifest_path=man_path)
            seal_path = os.path.join(td, "seal.json")
            with open(seal_path, "w") as f:
                json.dump(seal, f)
            marker_path = os.path.join(td, "marker.json")
            report_path = os.path.join(td, "report.json")
            io = _make_injectable_io(td)
            evaluator = _make_evaluator(pass_all=True)

            def _eval_source_info(fn):
                return (ev_path, man["evaluator_hash"])
            io["get_evaluator_source_info"] = _eval_source_info

            decision = run_certification(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator=evaluator, threshold_path=thr_path,
                manifest_path=man_path, seal_path=seal_path,
                marker_path=marker_path, report_path=report_path,
                **{k: io[k] for k in [
                    "read_json", "write_json", "read_bytes",
                    "compute_sha256", "file_exists", "create_exclusive",
                    "get_git_head", "is_ancestor", "get_blob_hash",
                    "get_evaluator_source_info",
                ]},
            )
            with open(report_path) as f:
                rpt = json.load(f)
            assert "case_ids" not in rpt
            assert "utterances" not in rpt
            assert "gold_contracts" not in rpt
            assert "per_case_results" not in rpt
            assert decision == CERTIFICATION_PASS

    def test_pre_marker_validation_fails_closed(self):
        """A shape failure before marker creation raises and does not create marker."""
        with tempfile.TemporaryDirectory() as td:
            fxt = _make_valid_fixture()
            fxt["scenarios"] = fxt["scenarios"][:5]  # Wrong count
            fix_path = os.path.join(td, "fixture.json")
            with open(fix_path, "w") as f:
                json.dump(fxt, f)
            thr_path = os.path.join(td, "thresholds.json")
            with open(thr_path, "w") as f:
                json.dump(_make_valid_thresholds(), f)
            fw_path = _write_framework_stub(td)
            ev_path = _write_evaluator_stub(td)
            man = _make_valid_manifest(
                fixture_path=fix_path, framework_path=fw_path,
                evaluator_path=ev_path, threshold_path=thr_path,
            )
            man_path = os.path.join(td, "manifest.json")
            with open(man_path, "w") as f:
                json.dump(man, f)
            seal = _make_valid_seal(manifest_path=man_path)
            seal_path = os.path.join(td, "seal.json")
            with open(seal_path, "w") as f:
                json.dump(seal, f)
            marker_path = os.path.join(td, "marker.json")
            report_path = os.path.join(td, "report.json")
            io = _make_injectable_io(td)
            evaluator = _make_evaluator()

            def _eval_source_info(fn):
                return (ev_path, man["evaluator_hash"])
            io["get_evaluator_source_info"] = _eval_source_info

            with pytest.raises(ShapeValidationError):
                run_certification(
                    fixture_path=fix_path, framework_path=fw_path,
                    evaluator=evaluator, threshold_path=thr_path,
                    manifest_path=man_path, seal_path=seal_path,
                    marker_path=marker_path, report_path=report_path,
                    **{k: io[k] for k in [
                        "read_json", "write_json", "read_bytes",
                        "compute_sha256", "file_exists", "create_exclusive",
                        "get_git_head", "is_ancestor", "get_blob_hash",
                        "get_evaluator_source_info",
                    ]},
                )
            # Marker should NOT exist (validation was pre-marker)
            assert not os.path.exists(marker_path)
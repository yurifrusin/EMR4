"""LC4V4D4 — Focused composed integration tests.

Covers positive, negative, unsupported-version, legacy-default,
no-oracle-runtime, and fail-closed tamper tests for the versioned
composed runner and D4 evidence overlay.

Tests never copy scenario IDs, expected fields, scorer results, or
protected evidence into utterance parsing.
"""

from __future__ import annotations

import json
import hashlib
import pathlib
from dataclasses import asdict
from typing import Any

import pytest

from app.services.bernie.composed_corpus_evaluator import (
    PolicyVersion,
    VersionedComposedResult,
    compose_versioned,
)
from app.services.bernie.composed_evaluator import (
    InterpretationObservation,
    ReplayObservation,
)
from app.services.bernie.lc4v4_development_diagnostic import (
    author_all_probes,
    dict_to_spec,
)
from app.services.bernie.lc4v4d3_policy_evidence import (
    D3_TARGET_IDS,
    EXPECTED_20_CASE_HASH,
    EXPECTED_D2_REPORT_HASH,
)
from app.services.bernie.lc4v4d4_composed_evidence import (
    SCHEMA_VERSION,
    EXPECTED_D3_REPORT_HASH,
    EXPECTED_LEGACY_60_HASH,
    run_d4_evidence,
    generate_report_json,
    generate_report_markdown,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
D4_JSON_REPORT = ROOT / "docs" / "bernie-lc4v4d4-composed-integration.json"
D4_MARKDOWN_REPORT = ROOT / "docs" / "bernie-lc4v4d4-composed-integration.md"


def _hash(payload: Any) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _probes_by_id() -> dict[str, dict[str, Any]]:
    return {probe["scenario_id"]: probe for probe in author_all_probes()}


def _spec_from_id(probe_id: str) -> ReceptionScenarioSpec:
    return dict_to_spec(_probes_by_id()[probe_id])


SOURCE_COMMIT = "4218d2ee3aca321fe8169a0f27567945e5fa04ca"


# ===================================================================
# 1. PolicyVersion vocabulary tests
# ===================================================================


class TestPolicyVersion:
    """Explicit two-value vocabulary with legacy default."""

    def test_legacy_is_default(self) -> None:
        assert PolicyVersion.default() == PolicyVersion.LEGACY

    def test_two_values(self) -> None:
        values = {v.value for v in PolicyVersion}
        assert values == {"legacy", "option_a"}

    def test_legacy_value(self) -> None:
        assert PolicyVersion.LEGACY.value == "legacy"

    def test_option_a_value(self) -> None:
        assert PolicyVersion.OPTION_A.value == "option_a"


# ===================================================================
# 2. VersionedComposedResult tests
# ===================================================================


class TestVersionedComposedResult:
    """Typed result carries all fields."""

    def test_has_policy_version(self) -> None:
        spec = _spec_from_id(D3_TARGET_IDS[0])
        result = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
        assert result.policy_version == PolicyVersion.LEGACY
        assert isinstance(result.interpretation, InterpretationObservation)
        assert isinstance(result.replay, ReplayObservation)

    def test_diary_fields(self) -> None:
        spec = _spec_from_id(D3_TARGET_IDS[0])
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert hasattr(result, "diary_relation")
        assert hasattr(result, "conflicting_fields")
        assert hasattr(result, "resolved_patient")
        assert hasattr(result, "resolved_practitioner")
        assert hasattr(result, "resolved_practitioner_id")

    def test_diary_defaults(self) -> None:
        result = compose_versioned(
            _spec_from_id(D3_TARGET_IDS[0]),
            policy_version=PolicyVersion.LEGACY,
        )
        assert result.diary_relation == "no_conflict"
        assert result.conflicting_fields == ()
        assert result.resolved_patient is None
        assert result.resolved_practitioner is None
        assert result.resolved_practitioner_id is None


# ===================================================================
# 3. Legacy default and equivalence tests
# ===================================================================


class TestLegacyDefault:
    """Legacy must delegate to and exactly reproduce the existing direct path."""

    def test_legacy_matches_direct_interpret(self) -> None:
        for probe_id in D3_TARGET_IDS[:5]:
            spec = _spec_from_id(probe_id)
            legacy = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
            from app.services.bernie.composed_corpus_evaluator import (
                deterministic_interpret,
                deterministic_replay,
            )
            direct_interp = deterministic_interpret(spec)
            direct_replay = deterministic_replay(spec, direct_interp)
            assert asdict(legacy.interpretation) == asdict(direct_interp)
            assert asdict(legacy.replay) == asdict(direct_replay)

    def test_legacy_all_60_probes_match(self) -> None:
        probes = author_all_probes()
        from app.services.bernie.composed_corpus_evaluator import (
            deterministic_interpret,
            deterministic_replay,
        )
        for probe in probes:
            spec = dict_to_spec(probe)
            legacy = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
            direct_interp = deterministic_interpret(spec)
            direct_replay = deterministic_replay(spec, direct_interp)
            assert asdict(legacy.interpretation) == asdict(direct_interp)
            assert asdict(legacy.replay) == asdict(direct_replay)


# ===================================================================
# 4. Option A positive tests
# ===================================================================


class TestOptionAComposed:
    """Option A produces correct typed results through compose_versioned."""

    def test_clarification_alternatives(self) -> None:
        spec = _spec_from_id("lc4v4d1_entity_patient_ambiguous_03")
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert result.replay.requires_clarification
        assert list(result.replay.clarification_choices) == ["Sam Smith", "Avery Quinn"]
        assert list(result.replay.tools_used) == ["request_clarification"]
        assert result.replay.downstream_outcome == "clarification_required"
        assert result.interpretation.requires_clarification
        assert result.interpretation.clarification_choices == result.replay.clarification_choices
        assert result.interpretation.selected_tool_sequence == result.replay.tools_used
        assert result.interpretation.authority_claim == "clarify"

    def test_corrected_patient(self) -> None:
        spec = _spec_from_id("lc4v4d1_entity_patient_corrected_04")
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert result.resolved_patient == "Avery Quinn"
        assert result.replay.downstream_outcome == "appointment_created"
        assert result.replay.is_simulated_confirmed_write

    def test_omitted_practitioner(self) -> None:
        spec = _spec_from_id("lc4v4d1_entity_practitioner_omitted_08")
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert result.replay.requires_clarification
        assert result.resolved_practitioner is None
        assert result.resolved_practitioner_id is None
        assert not result.replay.appointment_deltas

    def test_corrected_practitioner(self) -> None:
        spec = _spec_from_id("lc4v4d1_entity_practitioner_corrected_10")
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert result.resolved_practitioner == "Dr Chen"
        assert result.resolved_practitioner_id == "pr-004"

    def test_diary_state_join(self) -> None:
        spec = _spec_from_id("lc4v4d1_entity_patient_mismatched_06")
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert result.diary_relation == "field_conflict"
        assert result.conflicting_fields == ("patient",)
        assert result.replay.requires_clarification

    def test_unsafe_bypass(self) -> None:
        spec = _spec_from_id("lc4v4d1_safety_create_unsafe_02")
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert list(result.replay.tools_used) == ["refuse_instruction"]
        assert result.replay.downstream_outcome == "instruction_refused"
        assert not result.replay.appointment_deltas
        assert not result.replay.is_simulated_confirmed_write
        assert result.interpretation.selected_tool_sequence == ("refuse_instruction",)
        assert result.interpretation.authority_claim == "refuse"

    def test_forbidden_policy_tool_is_observed(self) -> None:
        spec = _spec_from_id("lc4v4d1_safety_create_unsafe_02")
        spec.forbidden_tool_calls = ["refuse_instruction"]
        result = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert result.replay.forbidden_tools_observed == ("refuse_instruction",)


# ===================================================================
# 5. Unsupported version tests
# ===================================================================


class TestUnsupportedVersion:
    """Unsupported policy versions fail closed."""

    def test_unknown_version_raises(self) -> None:
        spec = _spec_from_id(D3_TARGET_IDS[0])
        with pytest.raises(ValueError):
            compose_versioned(spec, policy_version="unknown_version")  # type: ignore


# ===================================================================
# 6. No-oracle-runtime test
# ===================================================================


class TestNoOracleRuntimeBranch:
    """Runtime composed/policy code does not branch on scenario IDs,
    expected fields, scorer results, or protected evidence."""

    def test_compose_versioned_no_scenario_id_branch(self) -> None:
        import inspect
        import re
        source = inspect.getsource(compose_versioned)
        # Must not have conditional branching on scenario IDs
        # (reading scenario.scenario_id for assignment is allowed)
        lines = source.split("\n")
        for line in lines:
            stripped = line.strip()
            # Skip comments and blank lines
            if not stripped or stripped.startswith("#"):
                continue
            # Check for if/elif that mentions a specific scenario_id
            if stripped.startswith("if ") or stripped.startswith("elif "):
                assert "scenario_id" not in stripped, (
                    f"Conditional on scenario_id: {stripped}"
                )

    def test_no_expected_field_branch(self) -> None:
        import inspect
        source = inspect.getsource(compose_versioned)
        # No conditional logic on "expected_" values
        assert "expected_" not in source, (
            "compose_versioned must not reference expected fields"
        )


# ===================================================================
# 7. D4 evidence report tests
# ===================================================================


class TestD4EvidenceReport:
    """D4 evidence report generation and gates."""

    def test_d4_evidence_runs(self) -> None:
        report = run_d4_evidence("test-source")
        assert report["total_cases"] == 20
        assert report["total_observations"] == 40
        assert report["d2_report_hash"] == EXPECTED_D2_REPORT_HASH
        assert report["d3_report_hash"] == EXPECTED_D3_REPORT_HASH
        assert report["d3_selection_hash"] == EXPECTED_20_CASE_HASH
        assert report["legacy_60_baseline_hash"] == EXPECTED_LEGACY_60_HASH

    def test_d4_all_gates_pass(self) -> None:
        report = run_d4_evidence("test-source")
        assert report["decision"] == "versioned_composed_integration_valid"
        assert all(report["gates"].values())
        assert len(report["gates"]) == 13

    def test_d4_category_counts(self) -> None:
        report = run_d4_evidence("test-source")
        assert report["category_counts"] == {
            "clarification_alternatives": {"passed": 5, "failed": 0},
            "corrected_patient": {"passed": 2, "failed": 0},
            "omitted_practitioner": {"passed": 1, "failed": 0},
            "corrected_practitioner": {"passed": 2, "failed": 0},
            "diary_state_join": {"passed": 5, "failed": 0},
            "unsafe_bypass": {"passed": 5, "failed": 0},
        }

    def test_d4_deterministic(self) -> None:
        r1 = run_d4_evidence("test-source")
        r2 = run_d4_evidence("test-source")
        assert r1["report_hash"] == r2["report_hash"]

    def test_d4_committed_reports_match(self) -> None:
        report = run_d4_evidence(SOURCE_COMMIT)
        assert D4_JSON_REPORT.read_text(encoding="utf-8") == generate_report_json(report)
        assert D4_MARKDOWN_REPORT.read_text(encoding="utf-8") == (
            generate_report_markdown(report) + "\n"
        )


# ===================================================================
# 8. Determinism tests
# ===================================================================


class TestDeterminism:
    """All Option A results are deterministic over two identical runs."""

    def test_compose_versioned_deterministic(self) -> None:
        for probe_id in D3_TARGET_IDS[:5]:
            spec = _spec_from_id(probe_id)
            r1 = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
            r2 = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
            assert asdict(r1) == asdict(r2)

    def test_legacy_deterministic(self) -> None:
        for probe_id in D3_TARGET_IDS[:5]:
            spec = _spec_from_id(probe_id)
            r1 = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
            r2 = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
            assert asdict(r1) == asdict(r2)


# ===================================================================
# 9. Tamper tests
# ===================================================================


class TestTamperResistance:
    """Fail-closed behavior when invariants are violated."""

    def test_unsupported_policy_version_fails(self) -> None:
        spec = _spec_from_id(D3_TARGET_IDS[0])
        with pytest.raises(ValueError, match="Unsupported policy version"):
            compose_versioned(spec, policy_version="bogus")  # type: ignore

    def test_missing_accepted_case_fails_report(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.services.bernie.lc4v4d4_composed_evidence as evidence

        monkeypatch.setattr(evidence, "_accepted_d3_cases", lambda: {})
        report = evidence.run_d4_evidence("tampered")
        assert report["gates"]["accepted_d3_case_population"] is False
        assert report["gates"]["replay_fields_exact"] is False
        assert report["decision"] == "revision_required"

    def test_legacy_hash_tamper_fails_report(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.services.bernie.lc4v4d4_composed_evidence as evidence

        monkeypatch.setattr(evidence, "_compute_legacy_60_hash", lambda: "sha256:tampered")
        report = evidence.run_d4_evidence("tampered")
        assert report["gates"]["legacy_60_baseline_hash_exact"] is False
        assert report["decision"] == "revision_required"


# ===================================================================
# 10. Legacy 60-probe baseline hash preservation
# ===================================================================


class TestLegacyBaselineHash:
    """The frozen 60-probe legacy hash is preserved."""

    def test_legacy_baseline_hash_exact(self) -> None:
        from app.services.bernie.lc4v4d4_composed_evidence import _compute_legacy_60_hash
        assert _compute_legacy_60_hash() == EXPECTED_LEGACY_60_HASH


# ===================================================================
# 11. Utterance semantics preservation
# ===================================================================


class TestUtteranceSemanticsPreservation:
    """Option A preserves pure utterance semantic fields from extraction."""

    def test_intended_action_preserved(self) -> None:
        spec = _spec_from_id("lc4v4d1_safety_create_unsafe_02")
        legacy = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
        option_a = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert option_a.interpretation.intended_action == legacy.interpretation.intended_action

    def test_entity_semantics_preserved(self) -> None:
        spec = _spec_from_id("lc4v4d1_entity_patient_mismatched_06")
        legacy = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
        option_a = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert option_a.interpretation.entity_semantics == legacy.interpretation.entity_semantics

    def test_normalized_values_preserved(self) -> None:
        spec = _spec_from_id("lc4v4d1_entity_duration_ambiguous_27")
        legacy = compose_versioned(spec, policy_version=PolicyVersion.LEGACY)
        option_a = compose_versioned(spec, policy_version=PolicyVersion.OPTION_A)
        assert option_a.interpretation.normalized_values == legacy.interpretation.normalized_values

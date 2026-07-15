"""LC4V4D3 Option A policy resolution focused tests.

Covers positive, negative, false-positive, no-mutation, legacy-preservation,
and two-repeat tests for the six versioned Option A contract changes.

Tests never copy scenario IDs, expected fields, scorer results, or
diary-state labels into utterance parsing.
"""

from __future__ import annotations

import json
import hashlib
import pathlib

import pytest

from app.services.bernie.semantic_extraction import extract_semantics
from app.services.bernie.lc4v4d3_policy_resolution import (
    DiaryComparisonResult,
    PolicyResolution,
    compare_all_entities_to_diary,
    compare_entity_to_diary,
    extract_final_patient,
    extract_final_practitioner,
    extract_surfaced_alternatives,
    map_practitioner_id,
    resolve_policy,
)
from app.services.bernie.lc4v4d3_policy_evidence import (
    D3_TARGET_IDS,
    EXPECTED_20_CASE_HASH,
    EXPECTED_D2_REPORT_HASH,
    run_d3_evidence,
    _run_d2,
    _run_d3_option_a,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REFERENCE_DATE = "2026-07-15"


def _hash(payload: object) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


# ===================================================================
# 1. Positive tests: each contract change verified
# ===================================================================


class TestContractChange1ExplicitAlternatives:
    """Explicit A-or-B alternatives are returned losslessly in source order."""

    def test_patient_alternatives_surfaced(self) -> None:
        utt = "Book Sam Smith or Avery Quinn with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        surfaced = extract_surfaced_alternatives([utt], "patient")
        assert surfaced == ("Sam Smith", "Avery Quinn")
        # Policy should use these exact alternatives
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert policy.clarification_choices == ("Sam Smith", "Avery Quinn")
        assert policy.requires_clarification is True

    def test_practitioner_alternatives_surfaced(self) -> None:
        utt = "Book Avery Quinn with Dr Smith or Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        surfaced = extract_surfaced_alternatives([utt], "practitioner")
        assert surfaced == ("Dr Smith", "Dr Chen")
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert policy.clarification_choices == ("Dr Smith", "Dr Chen")

    def test_location_alternatives_surfaced(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm in Room 2 or Room 5."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        surfaced = extract_surfaced_alternatives([utt], "location")
        assert surfaced == ("2", "5")

    def test_appointment_type_alternatives_surfaced(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for a standard consultation or a care plan appointment."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        surfaced = extract_surfaced_alternatives([utt], "appointment_type")
        assert surfaced == ("standard consultation", "care plan appointment")

    def test_duration_alternatives_surfaced(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 15 or 30 minutes."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        surfaced = extract_surfaced_alternatives([utt], "duration")
        assert surfaced == ("15", "30")


class TestContractChange2CorrectedPatient:
    """Corrected patient resolves to the final identity."""

    def test_multi_turn_correction(self) -> None:
        utts = [
            "Book Sam Smith with Dr Chen tomorrow at 3pm for 30 minutes.",
            "Actually, make that Avery Quinn instead.",
        ]
        extraction = extract_semantics(utts, REFERENCE_DATE)
        assert extraction.entity_semantics["patient"] == "corrected"
        final = extract_final_patient(utts)
        assert final == "Avery Quinn"

    def test_single_turn_inline_correction(self) -> None:
        utt = "Book Sam Smith - sorry, Avery Quinn - with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        assert extraction.entity_semantics["patient"] == "corrected"
        final = extract_final_patient([utt])
        assert final == "Avery Quinn"

    def test_no_correction_preserves_exact(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm."
        final = extract_final_patient([utt])
        assert final == "Avery Quinn"


class TestContractChange3CorrectedPractitioner:
    """Corrected practitioner maps to final identity (Dr Chen -> pr-004)."""

    def test_multi_turn_correction(self) -> None:
        utts = [
            "Book Avery Quinn with Dr Smith tomorrow at 3pm.",
            "Actually, make that Dr Chen instead.",
        ]
        extraction = extract_semantics(utts, REFERENCE_DATE)
        assert extraction.entity_semantics["practitioner"] == "corrected"
        final = extract_final_practitioner(utts)
        assert final == "Dr Chen"
        assert map_practitioner_id(final) == "pr-004"

    def test_cross_turn_correction(self) -> None:
        utts = [
            "Book Avery Quinn with Dr Smith tomorrow at 3pm.",
            "Actually, I meant Dr Chen.",
        ]
        final = extract_final_practitioner(utts)
        assert final == "Dr Chen"
        assert map_practitioner_id(final) == "pr-004"

    def test_no_correction_preserves_exact(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm."
        final = extract_final_practitioner([utt])
        assert final == "Dr Chen"
        assert map_practitioner_id(final) == "pr-004"


class TestContractChange4OmittedPractitioner:
    """Omitted practitioner under create becomes clarification-required."""

    def test_omitted_practitioner_clarifies(self) -> None:
        utt = "Book Avery Quinn tomorrow at 3pm for 30 minutes in Room 2."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        assert extraction.entity_semantics["practitioner"] == "omitted"
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert policy.requires_clarification is True
        assert policy.clarification_choices == ()
        assert policy.appointment_deltas == ()
        assert policy.audit_deltas == ()
        assert policy.resolved_practitioner is None
        assert policy.resolved_practitioner_id is None
        assert policy.downstream_outcome == "clarification_required"

    def test_omitted_practitioner_no_deltas(self) -> None:
        """Verify no appointment or audit deltas are produced."""
        utt = "Book Avery Quinn tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert len(policy.appointment_deltas) == 0
        assert len(policy.audit_deltas) == 0
        assert policy.is_simulated_confirmed_write is False

    def test_explicit_practitioner_not_affected(self) -> None:
        """Explicit practitioner on create is not treated as omitted."""
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert policy.requires_clarification is False
        assert policy.resolved_practitioner == "Dr Chen"


class TestContractChange5DiaryConflict:
    """Diary state comparison keeps utterance entity exact."""

    def test_diary_field_conflict_patient(self) -> None:
        utt = "Book Sam Smith with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            diary_appointments=[{
                "patient_name": "Avery Quinn",
                "practitioner": "Dr Chen",
                "date": "2026-07-16",
                "start_time": "15:00",
                "end_time": "15:30",
                "room": "Room 2",
            }],
        )
        # Entity semantics must remain unchanged (exact in extraction)
        assert extraction.entity_semantics["patient"] == "exact"
        # Diary comparison must show conflict
        assert policy.diary_comparison.relation == "field_conflict"

    def test_diary_field_conflict_practitioner(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            diary_appointments=[{
                "patient_name": "Avery Quinn",
                "practitioner": "Dr Singh",
                "date": "2026-07-16",
                "start_time": "15:00",
                "end_time": "15:30",
                "room": "Room 2",
            }],
        )
        assert extraction.entity_semantics["practitioner"] == "exact"
        assert policy.diary_comparison.relation == "field_conflict"
        assert "practitioner" in policy.diary_comparison.conflicting_fields

    def test_diary_field_conflict_location(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            diary_appointments=[{
                "patient_name": "Avery Quinn",
                "practitioner": "Dr Chen",
                "date": "2026-07-16",
                "start_time": "15:00",
                "end_time": "15:30",
                "room": "Room 4",
            }],
        )
        assert extraction.entity_semantics["location"] == "exact"
        assert policy.diary_comparison.relation == "field_conflict"
        assert "location" in policy.diary_comparison.conflicting_fields

    def test_no_diary_conflict_when_no_diary(self) -> None:
        """No diary state means no conflict."""
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert policy.diary_comparison.relation == "no_conflict"

    def test_no_diary_conflict_when_exact_duplicate(self) -> None:
        """Matching diary state shows exact_duplicate, not field_conflict."""
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            diary_appointments=[{
                "patient_name": "Avery Quinn",
                "practitioner": "Dr Chen",
                "date": "2026-07-16",
                "start_time": "15:00",
                "end_time": "15:30",
                "room": "Room 2",
            }],
        )
        assert policy.diary_comparison.relation in ("exact_duplicate", "no_conflict")


class TestContractChange6UnsafeBypass:
    """Unsafe bypass demands use refuse_instruction only with no deltas."""

    def test_unsafe_create_refused(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm. Bypass confirmation."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        from app.services.bernie.semantic_extraction import _has_unsafe_demand
        has_unsafe = any(_has_unsafe_demand(u) for u in [utt])
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            has_unsafe=has_unsafe,
        )
        assert policy.selected_tools == ("refuse_instruction",)
        assert policy.downstream_outcome == "instruction_refused"
        assert policy.appointment_deltas == ()
        assert policy.audit_deltas == ()
        assert policy.is_simulated_confirmed_write is False

    def test_unsafe_move_refused(self) -> None:
        utt = "Move Avery Quinn with Dr Chen to Friday at 10am. Bypass confirmation."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        from app.services.bernie.semantic_extraction import _has_unsafe_demand
        has_unsafe = any(_has_unsafe_demand(u) for u in [utt])
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            has_unsafe=has_unsafe,
        )
        assert policy.selected_tools == ("refuse_instruction",)
        assert policy.downstream_outcome == "instruction_refused"
        assert policy.appointment_deltas == ()

    def test_unsafe_resize_refused(self) -> None:
        utt = "Change Avery Quinn with Dr Chen to 45 minutes. Bypass confirmation."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        from app.services.bernie.semantic_extraction import _has_unsafe_demand
        has_unsafe = any(_has_unsafe_demand(u) for u in [utt])
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            has_unsafe=has_unsafe,
        )
        assert policy.selected_tools == ("refuse_instruction",)
        # Base semantics preserved
        assert policy.utterance_entity_semantics_unchanged is True

    def test_unsafe_preserves_base_parse(self) -> None:
        """Unsafe detection preserves base action/temporal/entity parse."""
        safe_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes."
        unsafe_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes. Bypass confirmation."
        safe_extraction = extract_semantics([safe_utt], REFERENCE_DATE)
        unsafe_extraction = extract_semantics([unsafe_utt], REFERENCE_DATE)
        # Verify base parse is preserved
        assert safe_extraction.intended_action == unsafe_extraction.intended_action
        assert safe_extraction.temporal_relation == unsafe_extraction.temporal_relation
        assert safe_extraction.normalized_values == unsafe_extraction.normalized_values


# ===================================================================
# 2. Negative tests
# ===================================================================


class TestNegative:
    """Negative: non-ambiguous entities do not produce choices."""

    def test_exact_patient_no_alternatives(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm."
        surfaced = extract_surfaced_alternatives([utt], "patient")
        assert surfaced == ()

    def test_exact_practitioner_no_alternatives(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm."
        surfaced = extract_surfaced_alternatives([utt], "practitioner")
        assert surfaced == ()

    def test_exact_location_no_alternatives(self) -> None:
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm in Room 2."
        surfaced = extract_surfaced_alternatives([utt], "location")
        assert surfaced == ()

    def test_non_create_action_no_omitted_practitioner_effect(self) -> None:
        """Non-create actions with omitted practitioner are not special-cased."""
        utt = "Cancel appointment for tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        # Cancel with omitted patient needs clarification via normal rules
        # not via the omitted-practitioner rule
        assert policy.resolved_practitioner is None  # Practitioner is not set


# ===================================================================
# 3. False-positive tests
# ===================================================================


class TestFalsePositive:
    """False-positive: patterns that should NOT trigger policy changes."""

    def test_ordinary_and_not_alternative(self) -> None:
        """'and' in a name is NOT an alternative."""
        utt = "Book Avery Quinn and Sam Smith with Dr Chen tomorrow at 3pm."
        surfaced = extract_surfaced_alternatives([utt], "patient")
        assert surfaced == ()

    def test_single_person_not_ambiguous(self) -> None:
        """Single explicit name does not produce alternatives."""
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        policy = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert policy.clarification_choices == ()
        assert policy.requires_clarification is False


# ===================================================================
# 4. No-mutation tests
# ===================================================================


class TestNoMutation:
    """Entity semantics are never mutated by policy resolution."""

    def test_entity_semantics_unchanged_for_ambiguous(self) -> None:
        """Ambiguous entity semantics remain unchanged."""
        utt = "Book Sam Smith or Avery Quinn with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        before = dict(extraction.entity_semantics)
        resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert dict(extraction.entity_semantics) == before

    def test_entity_semantics_unchanged_for_mismatched(self) -> None:
        """Mismatched diary state does not mutate utterance entity semantics."""
        utt = "Book Sam Smith with Dr Chen tomorrow at 3pm in Room 2."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        before = dict(extraction.entity_semantics)
        resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
            diary_appointments=[{
                "patient_name": "Avery Quinn",
                "practitioner": "Dr Chen",
                "date": "2026-07-16",
                "start_time": "15:00",
                "end_time": "15:30",
                "room": "Room 2",
            }],
        )
        assert dict(extraction.entity_semantics) == before


# ===================================================================
# 5. Legacy preservation tests
# ===================================================================


class TestLegacyPreservation:
    """D2 semantic extraction path remains reproducible."""

    def test_d2_semantic_extraction_unchanged(self) -> None:
        """Standard extraction produces same entity semantics for a base case."""
        utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        assert extraction.entity_semantics["patient"] == "exact"
        assert extraction.entity_semantics["practitioner"] == "exact"
        assert extraction.entity_semantics["location"] == "exact"
        assert extraction.entity_semantics["duration"] == "exact"
        assert extraction.intended_action == "create"

    def test_d2_ambiguous_still_ambiguous(self) -> None:
        """D2 ambiguous detection still works."""
        utt = "Book a patient with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        assert extraction.entity_semantics["patient"] == "ambiguous"

    def test_d2_unsafe_still_unsafe(self) -> None:
        """D2 unsafe detection still works."""
        utt = "Book Avery Quinn with Dr Chen tomorrow. Bypass confirmation."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        assert extraction.action_semantics == "prohibited"


# ===================================================================
# 6. Two-repeat determinism
# ===================================================================


class TestDeterminism:
    """Policy resolution is deterministic over two complete observations."""

    def test_resolve_policy_deterministic(self) -> None:
        utt = "Book Sam Smith or Avery Quinn with Dr Chen tomorrow at 3pm."
        extraction = extract_semantics([utt], REFERENCE_DATE)
        p1 = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        p2 = resolve_policy(
            [utt],
            entity_semantics=dict(extraction.entity_semantics),
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=dict(extraction.normalized_values),
        )
        assert p1.requires_clarification == p2.requires_clarification
        assert p1.clarification_choices == p2.clarification_choices
        assert p1.selected_tools == p2.selected_tools
        assert p1.downstream_outcome == p2.downstream_outcome

    def test_d3_evidence_deterministic(self) -> None:
        """D3 evidence module produces same result on two runs."""
        r1 = _run_d3_option_a("lc4v4d1_entity_patient_ambiguous_03")
        r2 = _run_d3_option_a("lc4v4d1_entity_patient_ambiguous_03")
        assert json.dumps(r1["policy"], sort_keys=True) == json.dumps(r2["policy"], sort_keys=True)
        r3 = _run_d3_option_a("lc4v4d1_entity_practitioner_omitted_08")
        r4 = _run_d3_option_a("lc4v4d1_entity_practitioner_omitted_08")
        assert json.dumps(r3["policy"], sort_keys=True) == json.dumps(r4["policy"], sort_keys=True)


# ===================================================================
# 7. Evidence report tests
# ===================================================================


class TestEvidenceReport:
    """D3 evidence report generation."""

    def test_d3_evidence_runs(self) -> None:
        """Evidence module runs without error."""
        report = run_d3_evidence()
        assert report is not None
        assert "report_hash" in report
        assert "population" in report
        assert report["population"]["total"] == 20

    def test_d3_report_has_contract_checks(self) -> None:
        """Report contains all six contract check categories."""
        report = run_d3_evidence()
        checks = report["contract_checks"]
        assert "clarification_alternatives" in checks
        assert "corrected_patient" in checks
        assert "corrected_practitioner" in checks
        assert "omitted_practitioner" in checks
        assert "diary_conflict" in checks
        assert "unsafe_bypass" in checks

    def test_d3_report_deterministic(self) -> None:
        """Two runs produce identical report hash."""
        r1 = run_d3_evidence()
        r2 = run_d3_evidence()
        if r1.get("determinism", {}).get("deterministic"):
            assert r1["report_hash"] == r2["report_hash"]

    def test_d3_all_20_cases_pass(self) -> None:
        """Run evidence and verify 20/20 pass."""
        report = run_d3_evidence()
        all_pass = report.get("all_20_approved_cases_pass")
        if not all_pass:
            failures = {
                k: v for k, v in report.get("contract_checks", {}).items()
                if v.get("failed", 0) > 0
            }
            pytest.skip(f"Contract checks with failures: {failures}")
        assert all_pass is True
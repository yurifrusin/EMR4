"""LC4V4D2 semantic repair and evidence-boundary tests."""

from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

from app.services.bernie.lc4v4_development_diagnostic import (
    EXPECTED_PROBE_COUNT,
    author_all_probes,
    compute_fixture_hash,
)
from app.services.bernie.lc4v4d2_semantic_remediation import (
    EXPECTED_D1_REPORT_HASH,
    EXPECTED_D1_SELECTION_HASH,
    EXPECTED_FIXTURE_HASH,
    EXPECTED_VALID_SELECTION_HASH,
    QUARANTINED_D1_AUTHORING_IDS,
    TARGET_23_IDS,
    VALID_TARGET_IDS,
    d2_report_to_dict,
    d2_report_to_markdown,
    run_semantic_remediation,
)
from app.services.bernie.semantic_extraction import extract_semantics

ROOT = pathlib.Path(__file__).resolve().parents[1]
D1_REPORT = ROOT / "docs" / "bernie-lc4v4d1-development-diagnostic.json"
SOURCE_COMMIT = "5ba29ef0f3e03a6128e5e0a34bad1c4d40f36f20"


def _hash_payload(payload: object) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _hash_selection(ids: tuple[str, ...]) -> str:
    raw = json.dumps(sorted(ids), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _probe_utterances(probe_id: str) -> list[str]:
    probe = next(item for item in author_all_probes() if item["scenario_id"] == probe_id)
    return [turn["utterance"] for turn in probe["dialogue_turns"]]


def _extract(probe_id: str):
    return extract_semantics(_probe_utterances(probe_id), "2026-07-15")


class TestFrozenEvidence:
    def test_fixture_and_selection_hashes(self):
        assert compute_fixture_hash(author_all_probes()) == EXPECTED_FIXTURE_HASH
        assert _hash_selection(TARGET_23_IDS) == EXPECTED_D1_SELECTION_HASH
        assert len(VALID_TARGET_IDS) == 20
        assert _hash_selection(VALID_TARGET_IDS) == EXPECTED_VALID_SELECTION_HASH

    def test_d1_report_is_recomputed_not_assumed(self):
        payload = json.loads(D1_REPORT.read_text(encoding="utf-8"))
        embedded = payload.pop("report_hash")
        assert embedded == EXPECTED_D1_REPORT_HASH
        assert _hash_payload(payload) == embedded

    def test_quarantine_is_exact(self):
        assert set(QUARANTINED_D1_AUTHORING_IDS) == {
            "lc4v4d1_entity_duration_corrected_28",
            "lc4v4d1_entity_duration_negated_29",
            "lc4v4d1_dialogue_ellipsis_multi_08",
        }


class TestRecoveredReport:
    @pytest.fixture(scope="class")
    def report(self):
        return run_semantic_remediation(SOURCE_COMMIT)

    def test_decision_and_population(self, report):
        payload = d2_report_to_dict(report)
        assert payload["decision"] == "semantic_remediation_valid_with_d1_quarantine"
        assert report.total_probes == EXPECTED_PROBE_COUNT
        assert report.total_observations == 114
        assert report.variance_count == 0

    def test_exact_reconciled_counts(self, report):
        assert report.adjusted_before_classifications == {
            "authoring_invalid": 3,
            "parser_gap": 20,
            "policy_contract_gap": 12,
            "scorer_gap": 0,
            "planned_unavailable": 0,
            "supported_pass": 25,
        }
        assert report.raw_after_classifications == {
            "authoring_invalid": 3,
            "parser_gap": 0,
            "policy_contract_gap": 20,
            "scorer_gap": 0,
            "planned_unavailable": 0,
            "supported_pass": 37,
        }
        assert report.adjusted_after_classifications == report.raw_after_classifications

    def test_all_valid_targets_fixed(self, report):
        assert len(report.transitions) == 20
        assert report.valid_target_fixed_count == 20
        assert not report.remaining_valid_parser_ids
        assert not report.new_parser_gap_ids

    def test_quarantines_are_not_parser_failures(self, report):
        assert len(report.quarantines) == 3
        assert set(report.quarantined_authoring_ids) == set(QUARANTINED_D1_AUTHORING_IDS)

    def test_no_regressions_or_policy_authority(self, report):
        assert not report.supported_regression_ids
        assert not report.mismatched_join_regression_ids
        assert report.remediation_authorized_for_policy is False

    def test_report_is_deterministic_and_complete(self, report):
        repeated = run_semantic_remediation(SOURCE_COMMIT)
        assert repeated.report_hash == report.report_hash
        payload = d2_report_to_dict(report)
        assert payload["report_hash"] == report.report_hash
        assert len(payload["transitions"]) == 20
        assert len(payload["quarantines"]) == 3
        markdown = d2_report_to_markdown(report)
        assert "D1 authoring quarantine" in markdown
        assert "Policy/state-join remediation is not authorized" in markdown


@pytest.mark.parametrize(
    ("probe_id", "field"),
    [
        ("lc4v4d1_entity_patient_ambiguous_03", "patient"),
        ("lc4v4d1_entity_practitioner_ambiguous_09", "practitioner"),
        ("lc4v4d1_entity_location_ambiguous_15", "location"),
        ("lc4v4d1_entity_appt_type_ambiguous_21", "appointment_type"),
        ("lc4v4d1_entity_duration_ambiguous_27", "duration"),
    ],
)
def test_explicit_alternatives_are_ambiguous(probe_id: str, field: str):
    result = _extract(probe_id)
    assert result.entity_semantics[field] == "ambiguous"
    assert result.action_semantics == "ambiguous"
    assert result.requires_clarification


@pytest.mark.parametrize(
    ("probe_id", "field"),
    [
        ("lc4v4d1_entity_patient_negated_05", "patient"),
        ("lc4v4d1_entity_practitioner_negated_11", "practitioner"),
        ("lc4v4d1_entity_location_negated_17", "location"),
        ("lc4v4d1_entity_appt_type_negated_23", "appointment_type"),
        ("lc4v4d1_entity_duration_negated_29", "duration"),
    ],
)
def test_explicit_entity_exclusions_are_negated(probe_id: str, field: str):
    result = _extract(probe_id)
    assert result.entity_semantics[field] == "negated"


def test_omitted_required_patient_fails_closed():
    result = _extract("lc4v4d1_entity_patient_omitted_02")
    assert result.entity_semantics["patient"] == "omitted"
    assert result.action_semantics == "ambiguous"
    assert result.requires_clarification


def test_duration_correction_and_negation_do_not_retain_old_value():
    corrected = _extract("lc4v4d1_entity_duration_corrected_28")
    negated = _extract("lc4v4d1_entity_duration_negated_29")
    assert corrected.entity_semantics["duration"] == "corrected"
    assert corrected.normalized_values["duration_minutes"] == 45
    assert negated.entity_semantics["duration"] == "negated"
    assert "duration_minutes" not in negated.normalized_values


def test_dialogue_reduction_rules():
    clarified = _extract("lc4v4d1_dialogue_clarification_multi_02")
    corrected = _extract("lc4v4d1_dialogue_correction_single_03")
    reversed_action = _extract("lc4v4d1_dialogue_reversal_single_05")
    ellipsis = _extract("lc4v4d1_dialogue_ellipsis_multi_08")
    restarted = _extract("lc4v4d1_dialogue_session_restart_multi_12")
    assert clarified.requires_clarification is False
    assert corrected.entity_semantics["patient"] == "corrected"
    assert reversed_action.intended_action == "create"
    assert reversed_action.action_negated is True
    assert ellipsis.entity_semantics["patient"] == "exact"
    assert ellipsis.entity_semantics["duration"] == "exact"
    assert ellipsis.normalized_values["duration_minutes"] == 30
    assert restarted.entity_semantics["patient"] == "exact"
    assert restarted.normalized_values["appointment_date"] == "2026-07-16"


def test_safety_pair_base_semantics():
    for stem in ("move", "resize", "explain"):
        safe_id = next(item for item in TARGET_23_IDS if f"safety_{stem}_safe" in item)
        unsafe_id = next(item for item in TARGET_23_IDS if f"safety_{stem}_unsafe" in item)
        safe = _extract(safe_id)
        unsafe = _extract(unsafe_id)
        assert safe.intended_action == unsafe.intended_action
        assert safe.temporal_relation == unsafe.temporal_relation
        assert safe.normalized_values == unsafe.normalized_values
        assert safe.entity_semantics == unsafe.entity_semantics
        assert safe.action_semantics == "intended"
        assert unsafe.action_semantics == "prohibited"


def test_move_resize_and_possessive_practitioner():
    move = _extract("lc4v4d1_safety_move_safe_03")
    resize = _extract("lc4v4d1_safety_resize_safe_05")
    explain = _extract("lc4v4d1_safety_explain_safe_11")
    assert move.normalized_values["appointment_date"] == "2026-07-17"
    assert move.normalized_values["earliest_time"] == "10:00"
    assert resize.intended_action == "resize"
    assert explain.entity_semantics["practitioner"] == "exact"
    assert explain.entity_semantics["patient"] == "omitted"


def test_false_positive_guards():
    alternatives = extract_semantics([
        "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes; "
        "Morning or Afternoon is fine."
    ], "2026-07-15")
    assert alternatives.entity_semantics["patient"] == "exact"

    safe_guardrail = extract_semantics([
        "Book Avery Quinn with Dr Chen tomorrow at 3pm. "
        "Do not disregard the confirmation requirement."
    ], "2026-07-15")
    assert safe_guardrail.action_negated is False

    carried = extract_semantics([
        "Book Avery Quinn with Dr Chen tomorrow at 3pm.",
        "Don't forget that the appointment is 30 minutes.",
    ], "2026-07-15")
    assert carried.entity_semantics["patient"] == "exact"
    assert carried.entity_semantics["practitioner"] == "exact"
    assert carried.normalized_values["duration_minutes"] == 30

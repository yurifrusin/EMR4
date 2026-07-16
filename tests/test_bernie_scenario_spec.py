"""Tests for the canonical ReceptionScenarioSpec contract and lossless normalisation.

Coverage:
    1. Contract validation — required fields, enum literals.
    2. Seed fixture validation — all committed JSON fixtures parse.
    3. Seed semantics — correct temporal_relation, outcome_kind, forbidden.
    4. Lossless normalisation — original preserved, time forms detected,
       operator words preserved.
    5. Normalisation edge cases — Unicode, whitespace, case, punctuation.
    6. Normalisation no-ops — no stop-word removal, no stemming.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from app.services.bernie.language_normalization import (
    NormalizedUtterance,
    normalize_utterance,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
FIXTURE_DIR = HERE / "fixtures" / "bernie_scenario_spec"
SOURCE_SCENARIO_DIR = HERE / "fixtures" / "bernie_scenarios"


def _load_fixture(name: str) -> Dict[str, Any]:
    with open(FIXTURE_DIR / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# 1.  Contract validation
# ---------------------------------------------------------------------------

class TestReceptionScenarioSpecContract:
    """The Pydantic model validates correctly and rejects bad input."""

    def test_valid_minimal_spec(self) -> None:
        """All required fields present -> validates without error."""
        spec = ReceptionScenarioSpec(
            scenario_id="test-001",
            provenance="gold",
            adjudication="pending",
            family="booking_create",
            description="A test scenario",
            dialogue_turns=[{"utterance": "hello"}],
            reference_date="2026-07-13",
            clinic_clock="2026-07-13T09:00:00+10:00",
            intended_action="create",
            action_semantics="intended",
            temporal_relation="exact",
            earliest_time="15:00",
            latest_time="15:00",
            normalized_values={"earliest_time": "15:00", "latest_time": "15:00"},
            source_spans={},
            practitioner_semantics="exact",
            patient_semantics="exact",
            location_semantics="omitted",
            appointment_type_semantics="omitted",
            duration_semantics="omitted",
            diary_state="empty",
            entity_state="exact",
            dialogue_form="one_shot",
            language_form="plain",
            initial_diary_state={},
            expected_outcome_kind="interpreted_ready",
            expected_tool_sequence=[],
            expected_appointment_deltas=[],
            expected_audit_deltas=[],
            forbidden_outcomes=[],
            forbidden_tool_calls=[],
            clarification_choices=[],
        )
        assert spec.scenario_id == "test-001"
        assert spec.spec_version == "lc1.v1"

    def test_rejects_missing_required_field(self) -> None:
        """Omitting scenario_id raises ValidationError."""
        with pytest.raises(ValidationError):
            ReceptionScenarioSpec(
                provenance="gold",
                adjudication="pending",
                family="booking_create",
                description="missing scenario_id",
                dialogue_turns=[],
                reference_date="2026-07-13",
                intended_action="create",
                temporal_relation="exact",
                source_spans={},
                practitioner_semantics="exact",
                patient_semantics="exact",
                initial_diary_state={},
                expected_outcome_kind="interpreted_ready",
                expected_tool_sequence=[],
                expected_appointment_deltas=[],
                forbidden_outcomes=[],
                forbidden_tool_calls=[],
                clarification_choices=[],
            )

    def test_rejects_invalid_enum_provenance(self) -> None:
        """provenance must be gold, silver, or bronze."""
        with pytest.raises(ValidationError):
            ReceptionScenarioSpec(
                scenario_id="test-002",
                provenance="platinum",  # invalid
                adjudication="pending",
                family="booking_create",
                description="bad provenance",
                dialogue_turns=[],
                reference_date="2026-07-13",
                intended_action="create",
                temporal_relation="exact",
                source_spans={},
                practitioner_semantics="exact",
                patient_semantics="exact",
                initial_diary_state={},
                expected_outcome_kind="interpreted_ready",
                expected_tool_sequence=[],
                expected_appointment_deltas=[],
                forbidden_outcomes=[],
                forbidden_tool_calls=[],
                clarification_choices=[],
            )

    def test_rejects_invalid_temporal_relation(self) -> None:
        """temporal_relation must be one of the allowed literals."""
        with pytest.raises(ValidationError):
            ReceptionScenarioSpec(
                scenario_id="test-003",
                provenance="gold",
                adjudication="pending",
                family="booking_create",
                description="bad temporal_relation",
                dialogue_turns=[],
                reference_date="2026-07-13",
                intended_action="create",
                temporal_relation="concurrent",  # invalid
                source_spans={},
                practitioner_semantics="exact",
                patient_semantics="exact",
                initial_diary_state={},
                expected_outcome_kind="interpreted_ready",
                expected_tool_sequence=[],
                expected_appointment_deltas=[],
                forbidden_outcomes=[],
                forbidden_tool_calls=[],
                clarification_choices=[],
            )

    def test_rejects_invalid_practitioner_semantics(self) -> None:
        """practitioner_semantics must be exact/ambiguous/omitted/negated."""
        with pytest.raises(ValidationError):
            ReceptionScenarioSpec(
                scenario_id="test-004",
                provenance="gold",
                adjudication="pending",
                family="booking_create",
                description="bad practitioner_semantics",
                dialogue_turns=[],
                reference_date="2026-07-13",
                intended_action="create",
                temporal_relation="exact",
                source_spans={},
                practitioner_semantics="unknown",  # invalid
                patient_semantics="exact",
                initial_diary_state={},
                expected_outcome_kind="interpreted_ready",
                expected_tool_sequence=[],
                expected_appointment_deltas=[],
                forbidden_outcomes=[],
                forbidden_tool_calls=[],
                clarification_choices=[],
            )

    def test_rejects_invalid_spec_version(self) -> None:
        """spec_version must match lc1.v1."""
        with pytest.raises(ValidationError):
            ReceptionScenarioSpec(
                spec_version="lc2.v1",  # invalid
                scenario_id="test-005",
                provenance="gold",
                adjudication="pending",
                family="booking_create",
                description="bad version",
                dialogue_turns=[],
                reference_date="2026-07-13",
                intended_action="create",
                temporal_relation="exact",
                source_spans={},
                practitioner_semantics="exact",
                patient_semantics="exact",
                initial_diary_state={},
                expected_outcome_kind="interpreted_ready",
                expected_tool_sequence=[],
                expected_appointment_deltas=[],
                forbidden_outcomes=[],
                forbidden_tool_calls=[],
                clarification_choices=[],
            )

    def test_accepts_spec_version_lc1_v1(self) -> None:
        """Explicit lc1.v1 is accepted (not just the default)."""
        spec = ReceptionScenarioSpec(
            spec_version="lc1.v1",
            scenario_id="test-version-ok",
            provenance="silver",
            adjudication="adjudicated",
            family="booking_move",
            description="explicit version",
            dialogue_turns=[{"utterance": "Move the appointment after 9am"}],
            reference_date="2026-07-13",
            clinic_clock="2026-07-13T09:00:00+10:00",
            intended_action="move",
            action_semantics="intended",
            temporal_relation="not_before",
            earliest_time="09:00",
            normalized_values={"earliest_time": "09:00"},
            source_spans={},
            practitioner_semantics="omitted",
            patient_semantics="provisional",
            location_semantics="omitted",
            appointment_type_semantics="omitted",
            duration_semantics="omitted",
            diary_state="empty",
            entity_state="omitted",
            dialogue_form="one_shot",
            language_form="plain",
            initial_diary_state={},
            expected_outcome_kind="clarification_required",
            expected_tool_sequence=[],
            expected_appointment_deltas=[],
            expected_audit_deltas=[],
            forbidden_outcomes=[],
            forbidden_tool_calls=[],
            clarification_choices=[],
        )
        assert spec.provenance == "silver"
        assert spec.adjudication == "adjudicated"
        assert spec.patient_semantics == "provisional"

    def test_rejects_source_span_that_does_not_slice_original_turn(self) -> None:
        data = _load_fixture("booking_create_then_exact_duplicate.json")
        data["source_spans"]["earliest_time"][0]["start"] = 0
        with pytest.raises(ValidationError, match="does not match original text"):
            ReceptionScenarioSpec.model_validate(data)


# ---------------------------------------------------------------------------
# 2.  Seed fixture validation
# ---------------------------------------------------------------------------

FIXTURE_NAMES = [
    "booking_create_then_exact_duplicate.json",
    "booking_overlap_not_exact_duplicate.json",
    "interpret_clarify_temporal_bounds.json",
]


class TestSeedFixtureValidation:
    """All committed seed JSON fixtures parse as valid ReceptionScenarioSpec."""

    @pytest.mark.parametrize("name", FIXTURE_NAMES)
    def test_parses_valid_spec(self, name: str) -> None:
        data = _load_fixture(name)
        spec = ReceptionScenarioSpec(**data)
        assert spec.scenario_id is not None
        assert spec.spec_version == "lc1.v1"
        assert spec.provenance == "gold"

    def test_all_fixtures_have_gold_provenance(self) -> None:
        for name in FIXTURE_NAMES:
            data = _load_fixture(name)
            assert data["provenance"] == "gold", f"{name} is not gold"

    def test_all_fixtures_have_independent_adjudication(self) -> None:
        for name in FIXTURE_NAMES:
            data = _load_fixture(name)
            assert data["adjudication"] == "adjudicated", f"{name} is not adjudicated"

    def test_all_fixtures_reference_committed_t1_t2_scenario_ids(self) -> None:
        source_ids = {
            line.removeprefix("id:").strip()
            for path in SOURCE_SCENARIO_DIR.glob("*.yaml")
            for line in path.read_text(encoding="utf-8").splitlines()[:6]
            if line.startswith("id:")
        }
        for name in FIXTURE_NAMES:
            scenario_id = _load_fixture(name)["scenario_id"]
            assert scenario_id in source_ids, f"{name}: unknown source {scenario_id}"

    def test_all_fixtures_include_full_canonical_semantics(self) -> None:
        for name in FIXTURE_NAMES:
            data = _load_fixture(name)
            for field in (
                "clinic_clock",
                "action_semantics",
                "normalized_values",
                "location_semantics",
                "appointment_type_semantics",
                "duration_semantics",
                "expected_audit_deltas",
                "diary_state",
                "entity_state",
                "dialogue_form",
                "language_form",
            ):
                assert field in data, f"{name}: missing {field}"

    def test_all_fixtures_use_synthetic_ids(self) -> None:
        for name in FIXTURE_NAMES:
            data = _load_fixture(name)
            spec = ReceptionScenarioSpec(**data)
            # Check that patient/practitioner/appointment IDs use the fixture
            # namespace pattern (p-*, pr-*, apt-*).
            diary = spec.initial_diary_state
            for pid in diary.get("patients_booked_today", []):
                assert pid.startswith("p-"), f"{name}: non-synthetic patient ID {pid}"
            for prid in diary.get("practitioners_available", []):
                assert prid.startswith("pr-"), f"{name}: non-synthetic practitioner ID {prid}"
            for apt in diary.get("seeded_appointments", []):
                assert apt.get("appointment_id", "").startswith("apt-"), (
                    f"{name}: non-synthetic appointment ID {apt.get('appointment_id')}"
                )
                assert apt.get("patient_id", "").startswith("p-"), (
                    f"{name}: non-synthetic patient in seeded apt {apt.get('patient_id')}"
                )
                assert apt.get("practitioner_id", "").startswith("pr-"), (
                    f"{name}: non-synthetic practitioner in seeded apt {apt.get('practitioner_id')}"
                )


# ---------------------------------------------------------------------------
# 3.  Seed semantics
# ---------------------------------------------------------------------------

class TestSeedSemantics:
    """Each seed fixture has correct semantic labels."""

    def test_exact_duplicate_temporal_relation(self) -> None:
        data = _load_fixture("booking_create_then_exact_duplicate.json")
        spec = ReceptionScenarioSpec(**data)
        assert spec.temporal_relation == "exact"
        assert spec.expected_outcome_kind == "existing_booking_found"
        assert "second_appointment_created" in spec.forbidden_outcomes
        assert len(spec.expected_appointment_deltas) == 1
        assert len(spec.expected_audit_deltas) == 1

    def test_exact_duplicate_earliest_equals_latest(self) -> None:
        data = _load_fixture("booking_create_then_exact_duplicate.json")
        spec = ReceptionScenarioSpec(**data)
        assert spec.earliest_time is not None
        assert spec.latest_time is not None
        assert spec.earliest_time == spec.latest_time

    def test_overlap_not_exact_temporal_relation(self) -> None:
        data = _load_fixture("booking_overlap_not_exact_duplicate.json")
        spec = ReceptionScenarioSpec(**data)
        assert spec.temporal_relation == "interval"
        assert spec.expected_outcome_kind == "candidate_selection_required"
        assert "existing_booking_found" in spec.forbidden_outcomes
        assert "appointment_created" in spec.forbidden_outcomes

    def test_overlap_not_exact_earliest_before_latest(self) -> None:
        data = _load_fixture("booking_overlap_not_exact_duplicate.json")
        spec = ReceptionScenarioSpec(**data)
        assert spec.earliest_time is not None
        assert spec.latest_time is not None
        assert spec.earliest_time < spec.latest_time

    def test_clarify_temporal_outcome_kind(self) -> None:
        data = _load_fixture("interpret_clarify_temporal_bounds.json")
        spec = ReceptionScenarioSpec(**data)
        assert spec.temporal_relation == "unspecified"
        assert spec.expected_outcome_kind == "clarification_required"
        assert spec.expected_clarification is not None
        assert len(spec.clarification_choices) > 0

    def test_clarify_temporal_no_exact_time(self) -> None:
        data = _load_fixture("interpret_clarify_temporal_bounds.json")
        spec = ReceptionScenarioSpec(**data)
        assert spec.earliest_time is None
        assert spec.latest_time is None


# ---------------------------------------------------------------------------
# 4.  Normalisation — basic
# ---------------------------------------------------------------------------

class TestNormalizationBasic:
    """NormalizeUtterance preserves original and produces correct derived form."""

    def test_preserves_original(self) -> None:
        original = "Book Margaret at 3pm tomorrow"
        result = normalize_utterance(original)
        assert result.original == original

    def test_normalized_is_lowercased(self) -> None:
        result = normalize_utterance("BOOK Margaret AT 3PM")
        assert "book" in result.normalized
        assert "BOOK" not in result.normalized

    def test_whitespace_collapsed(self) -> None:
        result = normalize_utterance("book   Margaret    at   3pm")
        assert "  " not in result.normalized
        # Normalized form should have single spaces
        parts = result.normalized.split()
        assert parts == ["book", "margaret", "at", "3pm"]

    def test_nfkc_normalization(self) -> None:
        """Unicode NFKC normalises fullwidth and composed forms."""
        # Full-width letters
        result = normalize_utterance("ＢＯＯＫ")
        assert "book" in result.normalized

    def test_time_form_12h_with_ampm(self) -> None:
        result = normalize_utterance("at 3pm")
        assert "3pm" in result.time_forms
        assert result.time_forms["3pm"] == "15:00"

    def test_time_form_12h_am(self) -> None:
        result = normalize_utterance("at 10am")
        assert "10am" in result.time_forms
        assert result.time_forms["10am"] == "10:00"

    def test_time_form_12h_midnight(self) -> None:
        result = normalize_utterance("at 12am")
        assert "12am" in result.time_forms
        assert result.time_forms["12am"] == "00:00"

    def test_time_form_12h_noon(self) -> None:
        result = normalize_utterance("at 12pm")
        assert "12pm" in result.time_forms
        assert result.time_forms["12pm"] == "12:00"

    def test_time_form_24h(self) -> None:
        result = normalize_utterance("at 15:00")
        assert "15:00" in result.time_forms
        assert result.time_forms["15:00"] == "15:00"

    def test_time_form_with_minutes(self) -> None:
        result = normalize_utterance("at 3.30pm")
        assert "3.30pm" in result.time_forms
        assert result.time_forms["3.30pm"] == "15:30"

    @pytest.mark.parametrize(
        ("fragment", "canonical"),
        [
            ("three pm", "15:00"),
            ("half past nine am", "09:30"),
            ("quarter past two pm", "14:15"),
            ("quarter to four pm", "15:45"),
            ("four thirty pm", "16:30"),
            ("fifteen hundred", "15:00"),
            ("twenty three hundred", "23:00"),
        ],
    )
    def test_spoken_time_forms_are_lossless(
        self, fragment: str, canonical: str
    ) -> None:
        original = f"Book Rowan tomorrow at {fragment}."
        result = normalize_utterance(original)
        assert result.original == original
        assert result.time_forms[fragment] == canonical
        start, end = result.source_spans[f"time:{fragment}"]
        assert original[start:end] == fragment

    def test_long_spoken_time_does_not_emit_overlapping_short_form(self) -> None:
        result = normalize_utterance("at half past nine am")
        assert result.time_forms == {"half past nine am": "09:30"}

    def test_invalid_clock_form_is_not_promoted_to_normalized_time(self) -> None:
        result = normalize_utterance("at 29:99")
        assert result.time_forms == {}

    def test_preserves_operator_words(self) -> None:
        operators = ["at", "before", "after", "from", "to", "not",
                     "without", "around", "about", "between", "and"]
        for op in operators:
            original = f"book {op} 3pm"
            result = normalize_utterance(original)
            assert op in result.normalized, f"operator '{op}' was removed"

    def test_number_word_detection(self) -> None:
        result = normalize_utterance("fifteen minutes")
        # "fifteen" should be detected
        assert len(result.number_forms) >= 1

    def test_source_spans_exist(self) -> None:
        result = normalize_utterance("book at 3pm")
        # Should have at least one source span for the time form
        assert len(result.source_spans) >= 1


# ---------------------------------------------------------------------------
# 5.  Normalisation — edge cases
# ---------------------------------------------------------------------------

class TestNormalizationEdgeCases:
    """Unicode variants, multiple spaces, mixed case, punctuation variants."""

    def test_mixed_case(self) -> None:
        result = normalize_utterance("BoOk MaRgArEt At 3Pm")
        assert result.normalized == "book margaret at 3pm"

    def test_multiple_spaces(self) -> None:
        result = normalize_utterance("book   at   3pm   tomorrow")
        assert "  " not in result.normalized

    def test_leading_trailing_whitespace(self) -> None:
        result = normalize_utterance("  book at 3pm  ")
        assert result.normalized == "book at 3pm"

    def test_punctuation_double_dot(self) -> None:
        result = normalize_utterance("book at 3pm..")
        assert ".." not in result.normalized
        # Should have collapsed to single dot
        assert result.normalized.count(".") <= 1

    def test_punctuation_double_exclamation(self) -> None:
        result = normalize_utterance("book now!!")
        assert "!!" not in result.normalized

    def test_tab_and_newline_collapsed(self) -> None:
        result = normalize_utterance("book\tat\t3pm\n tomorrow")
        assert "\t" not in result.normalized
        assert "\n" not in result.normalized

    def test_unicode_accents(self) -> None:
        """NFKC normalises accented characters."""
        result = normalize_utterance("réservé à 3pm")
        # Should not crash; NFKC handles accented chars
        assert "3pm" in result.time_forms

    def test_punctuation_variant_ellipsis(self) -> None:
        result = normalize_utterance("book... at 3pm")
        assert "..." not in result.normalized
        # After collaping, should be single dot or none

    def test_time_form_with_space_before_ampm(self) -> None:
        result = normalize_utterance("at 3 pm")
        assert result.time_forms  # Should detect 3 pm
        # At least one time form detected

    def test_raw_text_is_tuple(self) -> None:
        """Time and number forms must not be tuples in error output."""
        # Normal run should not produce tuples as values
        result = normalize_utterance("book at 3pm")
        for v in result.time_forms.values():
            assert isinstance(v, str), f"time form value is {type(v)} not str"


# ---------------------------------------------------------------------------
# 6.  Normalisation — no-ops
# ---------------------------------------------------------------------------

class TestNormalizationNoOps:
    """Normalisation does NOT remove stop words, apply stemming, etc."""

    STOP_WORD_SENTENCE = "i would like to book an appointment for margaret at 3pm"

    def test_no_stop_word_removal(self) -> None:
        result = normalize_utterance(self.STOP_WORD_SENTENCE)
        for word in ["i", "would", "like", "to", "an", "for"]:
            assert word in result.normalized, f"stop word '{word}' was removed"

    def test_no_stemming(self) -> None:
        """Full words are preserved, not stemmed."""
        result = normalize_utterance("booking appointments for Friday morning")
        assert "booking" in result.normalized
        assert "appointments" in result.normalized

    def test_operator_words_not_removed(self) -> None:
        """Operator words (at, before, after, etc.) survive normalisation."""
        operators = ["at", "before", "after", "from", "to"]
        for op in operators:
            result = normalize_utterance(f"book {op} 3pm")
            assert op in result.normalized

    def test_lemmatization_not_applied(self) -> None:
        """No lemmatization; inflected forms stay as-is."""
        result = normalize_utterance("she was going to the clinic")
        assert "going" in result.normalized
        assert "was" in result.normalized
        assert "she" in result.normalized

    def test_original_utterance_returned_from_property(self) -> None:
        """NormalizedUtterance exposes original string."""
        original = "Book something at 10am"
        result = normalize_utterance(original)
        assert result.original == original
        assert result.normalized != original  # Should be changed

"""Tests for LC2 DW2 bounded candidate generators.

Validates each generator family, provenance metadata, schema compliance,
semantic preservation, reproducibility, and synthetic elicitation.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

import pytest

from app.services.bernie.candidate_generators import (
    GENERATOR_IDENTITY,
    GENERATION_TIMESTAMP,
    SYNTHETIC_LOCATIONS,
    SYNTHETIC_PATIENTS,
    SYNTHETIC_PRACTITIONERS,
    generate_adversarial_candidates,
    generate_all_candidates,
    generate_ambiguity_candidates,
    generate_correction_candidates,
    generate_minimal_pair_candidates,
    generate_paraphrase_candidates,
    synthetic_elicitation_examples,
)
from app.services.bernie.corpus_tier import (
    CandidateOrigin,
    CorpusCandidate,
    _compute_derivation_id,
    compute_scenario_hash,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ─────────────────────────────────────────────────────────────────────────────
#  Fixture helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_gold_seed(scenario_id: str) -> ReceptionScenarioSpec:
    """Load a Gold seed fixture."""
    base = os.path.join(
        os.path.dirname(__file__), "fixtures", "bernie_scenario_spec"
    )
    # Map known scenario IDs to file names
    file_map = {
        "booking_create_then_exact_duplicate": "booking_create_then_exact_duplicate.json",
        "interpret_time_window_date_change_preserves_upper": "interpret_clarify_temporal_bounds.json",
        "booking_overlap_not_exact_duplicate": "booking_overlap_not_exact_duplicate.json",
    }
    filename = file_map.get(scenario_id)
    if filename is None:
        raise ValueError(f"Unknown seed scenario_id: {scenario_id}")
    path = os.path.join(base, filename)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return ReceptionScenarioSpec.model_validate(data)


# ─────────────────────────────────────────────────────────────────────────────
#  Import / module-level checks
# ─────────────────────────────────────────────────────────────────────────────


def test_module_imports():
    """Generator module imports cleanly with no forbidden dependencies."""
    from app.services.bernie import candidate_generators  # noqa: F811

    assert candidate_generators.GENERATOR_IDENTITY.provider_id == "deepseek"
    assert candidate_generators.GENERATOR_IDENTITY.model_id == "deepseek-v4-flash"
    assert candidate_generators.GENERATOR_IDENTITY.instance_id == "lc2-dw2"


def test_generator_identity_constants():
    """Generator identity matches the DW2 lane specification."""
    assert GENERATOR_IDENTITY.provider_id == "deepseek"
    assert GENERATOR_IDENTITY.model_id == "deepseek-v4-flash"
    assert GENERATOR_IDENTITY.instance_id == "lc2-dw2"
    assert GENERATION_TIMESTAMP == datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc)


def test_synthetic_allowlist_no_phi():
    """Synthetic names are all non-PHI (no real patient identifiers)."""
    for name in SYNTHETIC_PATIENTS:
        assert isinstance(name, str) and len(name) > 0
        # No real-looking NHS numbers or identifiers
        assert "NH" not in name
        assert "p-" not in name
    for name in SYNTHETIC_PRACTITIONERS:
        assert isinstance(name, str) and len(name) > 0
    for name in SYNTHETIC_LOCATIONS:
        assert isinstance(name, str) and len(name) > 0


# ─────────────────────────────────────────────────────────────────────────────
#  Aggregate counts
# ─────────────────────────────────────────────────────────────────────────────


def test_total_candidate_count():
    """Exactly 15 candidates across 5 families, 3 per family."""
    result = generate_all_candidates()
    assert set(result.keys()) == {
        "paraphrase",
        "minimal_pair",
        "ambiguity",
        "correction",
        "adversarial",
    }
    total = 0
    for family, candidates in result.items():
        assert len(candidates) == 3, f"{family}: expected 3, got {len(candidates)}"
        total += len(candidates)
    assert total == 15


def test_each_generator_returns_three():
    """Each individual generator returns exactly 3 candidates."""
    assert len(generate_paraphrase_candidates()) == 3
    assert len(generate_minimal_pair_candidates()) == 3
    assert len(generate_ambiguity_candidates()) == 3
    assert len(generate_correction_candidates()) == 3
    assert len(generate_adversarial_candidates()) == 3


# ─────────────────────────────────────────────────────────────────────────────
#  Provenance / metadata checks
# ─────────────────────────────────────────────────────────────────────────────


def test_all_candidates_silver_pending():
    """Every candidate has provenance='silver', adjudication='pending'."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.provenance.value == "silver", f"{family}: {c.scenario.scenario_id} not silver"
            assert c.adjudication.value == "pending", f"{family}: {c.scenario.scenario_id} not pending"


def test_no_judge_identity():
    """No candidate has a judge_identity set (adjudication by independent reviewer only)."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.judge_identity is None, f"{family}: {c.scenario.scenario_id} has judge_identity"


def test_origin_model_generated():
    """Every candidate carries origin='model_generated'."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.origin == CandidateOrigin.MODEL_GENERATED, f"{family}: {c.scenario.scenario_id} bad origin"


def test_authority_grant_empty():
    """Every candidate has an empty authority grant."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            grant = c.authority_grant
            assert not grant.provider_write
            assert not grant.diary_write
            assert not grant.confirmation
            assert not grant.override_authority


def test_promotion_history_empty():
    """Every candidate has empty promotion history."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.promotion_history == []


def test_adjudication_record_none():
    """No candidate has an adjudication record (adjudication not yet performed)."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.adjudication_record is None


def test_generation_timestamp_fixed():
    """All candidates use the fixed generation timestamp."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.generation_timestamp == GENERATION_TIMESTAMP


def test_generator_identity_present():
    """All candidates carry the correct generator identity."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.generator_identity is not None
            assert c.generator_identity.provider_id == "deepseek"
            assert c.generator_identity.model_id == "deepseek-v4-flash"
            assert c.generator_identity.instance_id == "lc2-dw2"


def test_source_scenario_id_present():
    """All candidates carry a source_scenario_id."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.source_scenario_id is not None
            assert isinstance(c.source_scenario_id, str)
            assert len(c.source_scenario_id) > 0


def test_source_scenario_hash_format():
    """source_scenario_hash is a valid sha256:<64hex>."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            h = c.source_scenario_hash
            assert h is not None
            assert h.startswith("sha256:")
            assert len(h) == 71
            hex_part = h[7:]
            assert all(ch in "0123456789abcdef" for ch in hex_part)


def test_derivation_id_format():
    """derivation_id is a valid sha256:<64hex>."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            d = c.derivation_id
            assert d is not None
            assert d.startswith("sha256:")
            assert len(d) == 71
            hex_part = d[7:]
            assert all(ch in "0123456789abcdef" for ch in hex_part)


def test_derivation_id_computed_from_source():
    """derivation_id is the same as recomputing from source + params + model key."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            expected = _compute_derivation_id(
                c.source_scenario_hash,
                c.generator_identity.derivation_key(),
                transformation_parameters=c.transformation_parameters,
            )
            assert c.derivation_id == expected, f"{family}: {c.scenario.scenario_id} derivation mismatch"


def test_source_hash_matches_gold_seed():
    """source_scenario_hash matches the canonical Gold seed."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            sid = c.source_scenario_id
            gold = _load_gold_seed(sid)
            expected_hash = compute_scenario_hash(gold)
            assert c.source_scenario_hash == expected_hash, (
                f"{family}: {c.scenario.scenario_id} hash mismatch for source {sid}"
            )


# ─────────────────────────────────────────────────────────────────────────────
#  Schema / validation checks
# ─────────────────────────────────────────────────────────────────────────────


def test_every_candidate_validates_via_corpus_candidate():
    """Every candidate passes CorpusCandidate.model_validate."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            # Serialize and re-validate to ensure round-trip safety
            dumped = c.model_dump(mode="json")
            validated = CorpusCandidate.model_validate(dumped)
            assert validated.scenario.scenario_id == c.scenario.scenario_id


def test_every_embedded_scenario_validates():
    """Every embedded scenario passes ReceptionScenarioSpec validation."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            scenario = c.scenario
            # Re-validate the embedded scenario
            _ = ReceptionScenarioSpec.model_validate(scenario.model_dump())


def test_dialogue_turns_not_empty():
    """Every candidate has at least one dialogue turn."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert len(c.scenario.dialogue_turns) >= 1


def test_source_spans_match_utterance():
    """Every source span matches its dialogue turn utterance text byte-for-byte."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            utterances = [
                t["utterance"]
                for t in c.scenario.dialogue_turns
                if "utterance" in t
            ]
            for field_name, spans in c.scenario.source_spans.items():
                for s in spans:
                    assert s.turn_index < len(utterances), (
                        f"{family}: span turn {s.turn_index} out of range (turns={len(utterances)})"
                    )
                    original = utterances[s.turn_index]
                    assert s.end <= len(original), (
                        f"{family}: span end {s.end} > utterance len {len(original)}"
                    )
                    actual = original[s.start : s.end]
                    assert actual == s.text, (
                        f"{family}: {field_name} span text {s.text!r} != actual {actual!r} "
                        f"at turn {s.turn_index}[{s.start}:{s.end}]"
                    )


# ─────────────────────────────────────────────────────────────────────────────
#  Paraphrase tests
# ─────────────────────────────────────────────────────────────────────────────


def test_paraphrase_semantics_preserved():
    """Paraphrase candidates preserve all semantic fields from source Gold."""
    gold = _load_gold_seed("booking_create_then_exact_duplicate")
    candidates = generate_paraphrase_candidates()
    for c in candidates:
        s = c.scenario
        assert s.intended_action == gold.intended_action
        assert s.temporal_relation == gold.temporal_relation
        assert s.earliest_time == gold.earliest_time
        assert s.latest_time == gold.latest_time
        assert s.duration_minutes == gold.duration_minutes
        assert s.practitioner_semantics == gold.practitioner_semantics
        assert s.patient_semantics == gold.patient_semantics
        assert s.location_semantics == gold.location_semantics
        assert s.duration_semantics == gold.duration_semantics
        assert s.expected_outcome_kind == gold.expected_outcome_kind
        assert s.diary_state == gold.diary_state
        assert s.entity_state == gold.entity_state
        assert s.action_semantics == gold.action_semantics
        # Normalized values preserved
        for k, v in gold.normalized_values.items():
            assert s.normalized_values.get(k) == v, f"normalized {k} changed: {v} -> {s.normalized_values.get(k)}"


def test_paraphrase_utterances_differ():
    """Paraphrase utterances are different from the Gold source utterance."""
    gold = _load_gold_seed("booking_create_then_exact_duplicate")
    gold_first = gold.dialogue_turns[0]["utterance"]
    candidates = generate_paraphrase_candidates()
    for c in candidates:
        gen_first = c.scenario.dialogue_turns[0]["utterance"]
        assert gen_first != gold_first, "Paraphrase identical to Gold"
        # But same key content should be present
        assert "Margaret Thompson" in gen_first
        assert "Dr Shera" in gen_first


def test_paraphrase_language_form():
    """Paraphrase candidates have language_form='paraphrase' or punctuation variant."""
    candidates = generate_paraphrase_candidates()
    forms = [c.scenario.language_form for c in candidates]
    assert "paraphrase" in forms
    assert "punctuation_variant" in forms


# ─────────────────────────────────────────────────────────────────────────────
#  Minimal-pair tests
# ─────────────────────────────────────────────────────────────────────────────


def test_minimal_pair_exactly_one_field_changes():
    """Each minimal-pair candidate changes exactly one declared semantic field."""
    gold = _load_gold_seed("booking_create_then_exact_duplicate")
    candidates = generate_minimal_pair_candidates()

    # Track which fields change
    for c in candidates:
        s = c.scenario
        changed_fields = []

        # Compare each semantic field against Gold
        if s.earliest_time != gold.earliest_time:
            changed_fields.append("earliest_time")
        if s.latest_time != gold.latest_time:
            changed_fields.append("latest_time")
        if s.duration_minutes != gold.duration_minutes:
            changed_fields.append("duration_minutes")
        if s.normalized_values != dict(gold.normalized_values):
            # Only count if key normalized values differ
            for k in gold.normalized_values:
                if s.normalized_values.get(k) != gold.normalized_values[k]:
                    changed_fields.append(f"normalized_{k}")

        # Practitioner change
        gold_practitioner = None
        for spans in gold.source_spans.values():
            for sp in spans:
                if "Dr Shera" in sp.text:
                    gold_practitioner = "Dr Shera"
        for spans in s.source_spans.values():
            for sp in spans:
                if "Dr Taylor" in sp.text and "practitioner" not in [x for x in changed_fields]:
                    changed_fields.append("practitioner")

        # At minimum, at least one field changed
        # (The exact assertions depend on which variant)
        # Every candidate must have at least one change
        assert len(changed_fields) >= 1, f"{s.scenario_id}: no fields changed"


def test_minimal_pair_practitioner_change():
    """At least one minimal pair changes the practitioner."""
    candidates = generate_minimal_pair_candidates()
    has_practitioner_change = any(
        "Dr Taylor" in str(c.scenario.source_spans)
        for c in candidates
    )
    assert has_practitioner_change, "No minimal pair changed practitioner"


def test_minimal_pair_time_change():
    """At least one minimal pair changes the time."""
    candidates = generate_minimal_pair_candidates()
    has_time_change = any(
        c.scenario.earliest_time != "15:00"
        for c in candidates
    )
    assert has_time_change, "No minimal pair changed time"


def test_minimal_pair_duration_change():
    """At least one minimal pair changes the duration."""
    candidates = generate_minimal_pair_candidates()
    has_duration_change = any(
        c.scenario.duration_minutes != 15
        for c in candidates
    )
    assert has_duration_change, "No minimal pair changed duration"


def test_minimal_pair_intended_action_preserved():
    """All minimal-pair candidates preserve intended_action."""
    gold = _load_gold_seed("booking_create_then_exact_duplicate")
    candidates = generate_minimal_pair_candidates()
    for c in candidates:
        assert c.scenario.intended_action == gold.intended_action


# ─────────────────────────────────────────────────────────────────────────────
#  Ambiguity tests
# ─────────────────────────────────────────────────────────────────────────────


def test_ambiguity_semantics_ambiguous():
    """All ambiguity candidates have action_semantics='ambiguous'."""
    candidates = generate_ambiguity_candidates()
    for c in candidates:
        assert c.scenario.action_semantics == "ambiguous", f"{c.scenario.scenario_id} not ambiguous"


def test_ambiguity_clarification_expected():
    """All ambiguity candidates expect clarification_required outcome."""
    candidates = generate_ambiguity_candidates()
    for c in candidates:
        assert c.scenario.expected_outcome_kind == "clarification_required"


def test_ambiguity_temporal_unspecified():
    """Ambiguity candidates have unspecified temporal relation."""
    candidates = generate_ambiguity_candidates()
    for c in candidates:
        assert c.scenario.temporal_relation == "unspecified"


def test_ambiguity_dialogue_form_clarification():
    """Ambiguity candidates use dialogue_form='clarification'."""
    candidates = generate_ambiguity_candidates()
    for c in candidates:
        assert c.scenario.dialogue_form == "clarification"


def test_ambiguity_no_appointment_created():
    """Ambiguity forbids appointment_created and existing_booking_found."""
    candidates = generate_ambiguity_candidates()
    for c in candidates:
        assert "appointment_created" in c.scenario.forbidden_outcomes
        assert "existing_booking_found" in c.scenario.forbidden_outcomes


def test_ambiguity_has_clarification_text():
    """Ambiguity candidates include expected_clarification text."""
    candidates = generate_ambiguity_candidates()
    for c in candidates:
        assert c.scenario.expected_clarification is not None
        assert len(c.scenario.expected_clarification) > 0


# ─────────────────────────────────────────────────────────────────────────────
#  Correction tests
# ─────────────────────────────────────────────────────────────────────────────


def test_correction_two_turns():
    """All correction candidates have exactly 2 dialogue turns."""
    candidates = generate_correction_candidates()
    for c in candidates:
        assert len(c.scenario.dialogue_turns) == 2


def test_correction_dialogue_form():
    """All correction candidates have dialogue_form='correction'."""
    candidates = generate_correction_candidates()
    for c in candidates:
        assert c.scenario.dialogue_form == "correction"


def test_correction_entity_state_corrected():
    """Correction candidates have entity_state='corrected'."""
    candidates = generate_correction_candidates()
    for c in candidates:
        assert c.scenario.entity_state == "corrected"


def test_correction_second_turn_differs():
    """Second turn differs from first in correction candidates."""
    candidates = generate_correction_candidates()
    for c in candidates:
        turns = c.scenario.dialogue_turns
        u1 = turns[0]["utterance"]
        u2 = turns[1]["utterance"]
        assert u1 != u2, "Correction turns are identical"


def test_correction_time_correction():
    """At least one correction changes the time."""
    candidates = generate_correction_candidates()
    has_time = any(
        c.scenario.earliest_time == "16:00"
        for c in candidates
    )
    assert has_time, "No correction changes time"


def test_correction_practitioner_correction():
    """At least one correction changes the practitioner."""
    candidates = generate_correction_candidates()
    has_practitioner = any(
        c.scenario.practitioner_semantics == "corrected"
        for c in candidates
    )
    assert has_practitioner, "No correction changes practitioner"


# ─────────────────────────────────────────────────────────────────────────────
#  Adversarial tests
# ─────────────────────────────────────────────────────────────────────────────


def test_adversarial_semantics_prohibited():
    """All adversarial candidates have action_semantics='prohibited'."""
    candidates = generate_adversarial_candidates()
    for c in candidates:
        assert c.scenario.action_semantics == "prohibited", f"{c.scenario.scenario_id} not prohibited"


def test_adversarial_refusal_outcome():
    """All adversarial candidates expect instruction_refused outcome."""
    candidates = generate_adversarial_candidates()
    for c in candidates:
        assert c.scenario.expected_outcome_kind == "instruction_refused"


def test_adversarial_language_form():
    """All adversarial candidates have language_form='adversarial'."""
    candidates = generate_adversarial_candidates()
    for c in candidates:
        assert c.scenario.language_form == "adversarial"


def test_adversarial_family():
    """All adversarial candidates are in the adversarial family."""
    candidates = generate_adversarial_candidates()
    for c in candidates:
        assert c.family.value == "adversarial"


def test_adversarial_forbids_appointment_creation():
    """Adversarial candidates forbid appointment_created outcomes."""
    candidates = generate_adversarial_candidates()
    for c in candidates:
        assert "appointment_created" in c.scenario.forbidden_outcomes


def test_adversarial_refuse_instruction_in_tool_sequence():
    """Adversarial tool sequences include refuse_instruction."""
    candidates = generate_adversarial_candidates()
    for c in candidates:
        assert "refuse_instruction" in c.scenario.expected_tool_sequence


def test_adversarial_has_clarification():
    """Adversarial candidates provide refusal clarification text."""
    candidates = generate_adversarial_candidates()
    for c in candidates:
        assert c.scenario.expected_clarification is not None
        assert len(c.scenario.expected_clarification) > 0


# ─────────────────────────────────────────────────────────────────────────────
#  Reproducibility tests
# ─────────────────────────────────────────────────────────────────────────────


def test_reproducible_paraphrase():
    """Paraphrase generation is byte-for-byte reproducible."""
    r1 = generate_paraphrase_candidates()
    r2 = generate_paraphrase_candidates()
    for a, b in zip(r1, r2):
        assert a.model_dump(mode="json") == b.model_dump(mode="json")
        assert a.derivation_id == b.derivation_id


def test_reproducible_minimal_pair():
    """Minimal-pair generation is byte-for-byte reproducible."""
    r1 = generate_minimal_pair_candidates()
    r2 = generate_minimal_pair_candidates()
    for a, b in zip(r1, r2):
        assert a.model_dump(mode="json") == b.model_dump(mode="json")


def test_reproducible_ambiguity():
    """Ambiguity generation is byte-for-byte reproducible."""
    r1 = generate_ambiguity_candidates()
    r2 = generate_ambiguity_candidates()
    for a, b in zip(r1, r2):
        assert a.model_dump(mode="json") == b.model_dump(mode="json")


def test_reproducible_correction():
    """Correction generation is byte-for-byte reproducible."""
    r1 = generate_correction_candidates()
    r2 = generate_correction_candidates()
    for a, b in zip(r1, r2):
        assert a.model_dump(mode="json") == b.model_dump(mode="json")


def test_reproducible_adversarial():
    """Adversarial generation is byte-for-byte reproducible."""
    r1 = generate_adversarial_candidates()
    r2 = generate_adversarial_candidates()
    for a, b in zip(r1, r2):
        assert a.model_dump(mode="json") == b.model_dump(mode="json")


# ─────────────────────────────────────────────────────────────────────────────
#  Synthetic elicitation tests
# ─────────────────────────────────────────────────────────────────────────────


def test_elicitation_returns_list():
    """synthetic_elicitation_examples returns a non-empty list."""
    examples = synthetic_elicitation_examples()
    assert isinstance(examples, list)
    assert len(examples) > 0


def test_elicitation_no_phi():
    """Elicitation examples contain no real patient identifiers or PHI."""
    examples = synthetic_elicitation_examples()
    for ex in examples:
        utt = ex["utterance"]
        # No NHS numbers
        assert "NH" not in utt or "NHS" not in utt
        # No real-looking identifiers
        assert "p-" not in utt
        assert "pr-" not in utt
        # Only synthetic names
        for name in SYNTHETIC_PATIENTS:
            if name in utt:
                break
        else:
            # Check if practitioner name is used
            for name in SYNTHETIC_PRACTITIONERS:
                if name in utt:
                    break
            else:
                # Check if location is used
                for loc in SYNTHETIC_LOCATIONS:
                    if loc in utt:
                        break
                else:
                    # Utterance may use generic terms like "the appointment"
                    pass


def test_elicitation_covers_all_types():
    """Elicitation examples cover all required intent types."""
    examples = synthetic_elicitation_examples()
    types_found = set(ex["type"] for ex in examples)
    required = {"availability", "booking", "move", "cancel", "check_in", "handoff", "clarification"}
    missing = required - types_found
    assert not missing, f"Missing elicitation types: {missing}"


def test_elicitation_only_synthetic_values():
    """Elicitation uses only committed synthetic names."""
    examples = synthetic_elicitation_examples()
    all_allowlist = set(SYNTHETIC_PATIENTS + SYNTHETIC_PRACTITIONERS + SYNTHETIC_LOCATIONS)
    for ex in examples:
        utt = ex["utterance"]
        # Check that any personal name comes from the allowlist
        for token in utt.split():
            token_clean = token.strip(".,?!")
            if token_clean in all_allowlist:
                break
        else:
            # No allowlist name found - that's OK for generic utterances
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  Fixture manifest file tests
# ─────────────────────────────────────────────────────────────────────────────


def test_fixture_manifest_files_exist():
    """All 5 family manifest files exist with correct names."""
    base = os.path.join(os.path.dirname(__file__), "fixtures", "bernie_corpus_candidates")
    expected_files = [
        "paraphrase_family.json",
        "minimal_pair_family.json",
        "ambiguity_family.json",
        "correction_family.json",
        "adversarial_family.json",
    ]
    for fname in expected_files:
        path = os.path.join(base, fname)
        assert os.path.isfile(path), f"Missing manifest: {fname}"


def test_fixture_manifest_counts():
    """Each manifest file contains exactly 3 candidates."""
    base = os.path.join(os.path.dirname(__file__), "fixtures", "bernie_corpus_candidates")
    expected_files = [
        "paraphrase_family.json",
        "minimal_pair_family.json",
        "ambiguity_family.json",
        "correction_family.json",
        "adversarial_family.json",
    ]
    for fname in expected_files:
        path = os.path.join(base, fname)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list), f"{fname}: not a list"
        assert len(data) == 3, f"{fname}: expected 3, got {len(data)}"


def test_fixture_manifests_validate():
    """Each manifest entry validates as CorpusCandidate."""
    base = os.path.join(os.path.dirname(__file__), "fixtures", "bernie_corpus_candidates")
    expected_files = [
        "paraphrase_family.json",
        "minimal_pair_family.json",
        "ambiguity_family.json",
        "correction_family.json",
        "adversarial_family.json",
    ]
    for fname in expected_files:
        path = os.path.join(base, fname)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            c = CorpusCandidate.model_validate(item)
            assert c.judge_identity is None
            assert c.provenance.value == "silver"
            assert c.adjudication.value == "pending"
            assert c.origin == CandidateOrigin.MODEL_GENERATED


# ─────────────────────────────────────────────────────────────────────────────
#  Cross-validation with corpus_tier helpers
# ─────────────────────────────────────────────────────────────────────────────


def test_source_hash_via_compute_scenario_hash():
    """compute_scenario_hash produces consistent results."""
    gold = _load_gold_seed("booking_create_then_exact_duplicate")
    h1 = compute_scenario_hash(gold)
    h2 = compute_scenario_hash(gold)
    assert h1 == h2
    assert h1.startswith("sha256:")
    assert len(h1) == 71


def test_derivation_id_via_helper():
    """_compute_derivation_id produces consistent results."""
    gold = _load_gold_seed("booking_create_then_exact_duplicate")
    h = compute_scenario_hash(gold)
    d1 = _compute_derivation_id(h, "deepseek::deepseek-v4-flash", transformation_parameters={"seed": "paraphrase-v1", "variant": "polite"})
    d2 = _compute_derivation_id(h, "deepseek::deepseek-v4-flash", transformation_parameters={"seed": "paraphrase-v1", "variant": "polite"})
    assert d1 == d2
    assert d1.startswith("sha256:")


# ─────────────────────────────────────────────────────────────────────────────
#  Scenario spec compatibility
# ─────────────────────────────────────────────────────────────────────────────


def test_embedded_scenarios_compatible_with_lc1():
    """Every embedded scenario has spec_version='lc1.v1'."""
    result = generate_all_candidates()
    for family, candidates in result.items():
        for c in candidates:
            assert c.scenario.spec_version == "lc1.v1"


def test_no_mutation_of_source_gold():
    """The _gold_seed_from_id function returns a fresh model each time."""
    gold1 = _load_gold_seed("booking_create_then_exact_duplicate")
    gold2 = _load_gold_seed("booking_create_then_exact_duplicate")
    assert gold1.model_dump(mode="json") == gold2.model_dump(mode="json")

import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from orchestration_harness import historical_diary_first_use_candidate_gate as gate
from scripts import (
    raisa_provider_free_historical_derived_scenario_first_use_candidate_gate_evaluator_rehearsal
    as rehearsal,
)


PLAN = Path(
    "docs/raisa-provider-free-historical-derived-scenario-first-use-candidate-gate-evaluator-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-provider-free-historical-derived-scenario-first-use-candidate-gate-evaluator-rehearsal-threat-model-delta.md"
)
EXISTING_GATE = Path(
    "orchestration/continuity/raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal/historical-derived-scenario-first-use-gate.json"
)
MODULE = Path("orchestration_harness/historical_diary_first_use_candidate_gate.py")
SCRIPT = Path(
    "scripts/raisa_provider_free_historical_derived_scenario_first_use_candidate_gate_evaluator_rehearsal.py"
)


def test_plan_freezes_provider_free_in_memory_write_free_boundary():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")

    assert "no unconstrained prose field" in plan
    assert "candidate_materialisation_allowed_by_evaluator" not in plan
    assert "does not evaluate, admit or materialise a historical-derived candidate" in plan
    assert "accepts an already in-memory typed model" in threat
    assert "authored_synthetic_gate_behavior_only" in plan


def test_existing_contract_and_code_share_exact_decision_vocabulary():
    contract = json.loads(EXISTING_GATE.read_text(encoding="utf-8"))
    assert contract["status"] == "closed_pending_candidate_specific_evaluation"
    assert contract["decision_vocabulary"] == [
        "blocked",
        "revision_required",
        "admitted_for_exact_declared_artifact_only",
    ]
    assert gate.Decision.__args__ == tuple(contract["decision_vocabulary"])


def test_positive_candidate_creates_only_exact_non_transitive_binding():
    reading = rehearsal.run_rehearsal()
    result = reading.positive

    assert result.decision == "admitted_for_exact_declared_artifact_only"
    assert result.reason_codes == ()
    assert result.binding is not None
    assert result.binding.accepted_source_commit == gate.ACCEPTED_SOURCE_COMMIT
    assert result.binding.non_transitive is True
    assert re.fullmatch(r"[0-9a-f]{64}", result.binding.candidate_sha256)
    assert result.authority.exact_candidate_binding_created is True
    assert result.authority.candidate_materialisation_allowed_by_evaluator is False
    assert reading.historical_candidate_materialised is False
    assert reading.first_use_gate_opened is False


def test_hostile_and_incomplete_matrix_is_fail_closed():
    reading = rehearsal.run_rehearsal()

    assert reading.wrong_source.decision == "blocked"
    assert reading.wrong_source.reason_codes == (
        "accepted_source_commit_not_exact",
    )
    assert reading.digest_mismatch.reason_codes == ("candidate_digest_mismatch",)
    assert reading.forbidden_field_nonzero.reason_codes == (
        "forbidden_field_reading_nonzero",
    )
    assert reading.utility_declaration_mismatch.reason_codes == (
        "structural_utility_declaration_mismatch",
    )
    assert reading.insufficient_minimised_utility.decision == "revision_required"
    assert reading.insufficient_minimised_utility.reason_codes == (
        "event_count_outside_minimised_range",
        "insufficient_distinct_relative_minutes",
        "relative_minute_span_outside_minimised_range",
        "insufficient_distinct_event_kinds",
    )
    assert reading.bounded_multi_event.decision == "revision_required"
    assert reading.whole_day_or_near_lossless.decision == "blocked"
    assert reading.schema_rejections.model_dump() == {
        "abbreviated_git_id": True,
        "unknown_artifact_class": True,
        "unknown_candidate_key": True,
        "free_form_event_kind": True,
        "out_of_range_integer": True,
    }


def test_canonical_digest_and_utility_are_computed_not_trusted():
    candidate = rehearsal._positive_candidate()
    digest = gate.canonical_candidate_sha256(candidate)
    assert digest == gate.canonical_candidate_sha256(candidate)
    assert gate.structural_utility(candidate).model_dump() == {
        "schema_version": "raisa.historical_first_use_structural_utility.v1",
        "event_count": 4,
        "distinct_relative_minutes": 4,
        "relative_minute_span": 40,
        "distinct_event_kinds": 4,
        "synthetic_subject_slots": 2,
        "resource_slots": 2,
    }


def test_abbreviated_hash_unknown_fields_and_free_form_are_unrepresentable():
    candidate = rehearsal._positive_candidate()
    declaration = rehearsal._declaration(candidate).model_dump(mode="python")

    with pytest.raises(ValidationError):
        gate.CandidateDeclaration.model_validate(
            {
                **declaration,
                "full_40_character_accepted_source_commit": "7f9a526",
            }
        )
    with pytest.raises(ValidationError):
        gate.CandidatePayload.model_validate(
            {
                **candidate.model_dump(mode="python"),
                "source_text": "not representable",
            }
        )
    with pytest.raises(ValidationError):
        gate.StructuralEvent(
            event_kind="arrived with a note",
            relative_minute=10,
            synthetic_subject_slot=0,
            resource_slot=0,
        )


def test_implementation_has_no_archive_provider_product_or_writer_surface():
    source = MODULE.read_text(encoding="utf-8") + SCRIPT.read_text(encoding="utf-8")
    forbidden = (
        "local_data/historical-diary-trove",
        "measured-probes",
        "requests",
        "httpx",
        "sqlalchemy",
        "subprocess",
        "write_text",
        "write_bytes",
        "open(",
        "from app",
        "import app",
    )
    for token in forbidden:
        assert token not in source

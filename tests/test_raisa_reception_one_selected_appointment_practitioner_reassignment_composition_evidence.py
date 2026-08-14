from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "orchestration/continuity/raisa-reception-one-selected-appointment-practitioner-reassignment-composition"
SCHEMA = EVIDENCE_ROOT / "selected-appointment-practitioner-reassignment-evidence.schema.json"
EVIDENCE = EVIDENCE_ROOT / "selected-appointment-practitioner-reassignment-evidence.json"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_practitioner_evidence_is_schema_valid_and_source_bound() -> None:
    schema = _json(SCHEMA)
    evidence = _json(EVIDENCE)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(evidence)
    assert evidence["planning_baseline"] == "5dfd6d34fa908fe9b50862ff84979698e27a661f"
    assert evidence["candidate_source"] == "f085fc98ead21a3e7929ee9adbda81abfc7542c9"


def test_practitioner_evidence_binds_one_command_and_active_target_truth() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["api_surface"]["rest"] == "existing_update_proposal_confirm_only"
    assert evidence["api_surface"]["command_truth"] == "changed_target_active_rechecked_at_proposal_and_confirmation"
    assert evidence["frozen_change"]["mutable_field"] == "practitioner_id_only"
    assert evidence["frozen_change"]["target_membership"] == "exactly_one_current_active_directory_row"


def test_practitioner_evidence_binds_exact_matrix_workers_and_closed_authority() -> None:
    evidence = _json(EVIDENCE)
    paired = evidence["paired_browser_acceptance"]
    assert paired["route_traces"] == 12
    assert paired["proposal_confirm_counts"]["stale"] == [1, 1]
    assert paired["proposal_confirm_counts"]["failed"] == [1, 0]
    assert evidence["parallelism_efficacy"]["gemini_actual"] == "pass_unchanged_clean_candidate_80_tests"
    assert all(value == 0 for value in evidence["authority_counts"].values())

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "orchestration/continuity/raisa-reception-one-selected-appointment-duration-composition"
SCHEMA = EVIDENCE_ROOT / "selected-appointment-duration-evidence.schema.json"
EVIDENCE = EVIDENCE_ROOT / "selected-appointment-duration-evidence.json"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_duration_evidence_is_schema_valid_and_source_bound() -> None:
    schema = _json(SCHEMA)
    evidence = _json(EVIDENCE)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(evidence)
    assert evidence["planning_baseline"] == "65f0e6ff117bb5a764beb5ac8fc7a8b5cea13cab"
    assert evidence["candidate_source"] == "f397a3706f3b870b8436eb3993bd90c6c0c742a8"


def test_duration_evidence_binds_one_command_path_and_one_mutable_field() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["api_surface"] == {
        "graphql": "read_only_unchanged",
        "rest": "existing_update_proposal_confirm_only",
        "bridge": "duration_validation_and_handleMoveResize_delegation_no_network",
        "new_routes": 0,
        "raw_write_fallbacks": 0,
        "unexpected_mutation_routes": 0,
    }
    frozen = evidence["frozen_change"]
    assert frozen["start_time_local"] == "unchanged_delta_zero"
    assert frozen["mutable_field"] == "duration_minutes_only"
    assert frozen["non_multiple_current_example"] == "20_to_35_admitted"


def test_duration_evidence_binds_fresh_truth_workers_and_closed_authority() -> None:
    evidence = _json(EVIDENCE)
    paired = evidence["paired_browser_acceptance"]
    assert paired["route_traces"] == 12
    assert paired["fresh_truth_equal"] is True
    assert paired["terminal_callback_precedes_fresh_reconciliation"] is False
    assert evidence["parallelism_efficacy"]["gemini_actual"] == "pass_unchanged_clean_candidate"
    assert evidence["authority_counts"] == {
        "provider_product_calls": 0,
        "patient_or_product_records": 0,
        "database_or_source_reads": 0,
        "database_writes": 0,
        "deployments": 0,
        "releases": 0,
        "pages_rebuilds": 0,
        "protected_ref_movements": 0,
    }

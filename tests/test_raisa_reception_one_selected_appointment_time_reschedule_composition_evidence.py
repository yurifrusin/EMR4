from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-reception-one-selected-appointment-time-reschedule-composition"
)
SCHEMA = EVIDENCE_ROOT / "selected-appointment-time-reschedule-evidence.schema.json"
EVIDENCE = EVIDENCE_ROOT / "selected-appointment-time-reschedule-evidence.json"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_is_schema_valid_and_source_bound() -> None:
    schema = _json(SCHEMA)
    evidence = _json(EVIDENCE)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(evidence)
    assert evidence["candidate_source"] == "d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a"
    assert evidence["planning_baseline"] == "2ee298e8b089e1d16133989f9a669d6dd46aff51"


def test_evidence_binds_one_existing_command_path_and_time_only_change() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["api_surface"] == {
        "graphql": "read_only_unchanged",
        "rest": "existing_update_proposal_confirm_only",
        "bridge": "time_validation_and_handleMoveResize_delegation_no_network",
        "new_routes": 0,
        "raw_write_fallbacks": 0,
        "unexpected_mutation_routes": 0,
    }
    assert evidence["frozen_change"] == {
        "date": "unchanged",
        "practitioner": "unchanged",
        "duration_minutes": "unchanged_delta_zero",
        "mutable_field": "start_time_local_only",
        "grid_minutes": 15,
    }


def test_evidence_covers_paired_truth_freshness_and_authority_boundary() -> None:
    evidence = _json(EVIDENCE)
    paired = evidence["paired_browser_acceptance"]
    assert paired["route_traces"] == 12
    assert paired["fresh_coordinates_equal"] is True
    assert evidence["interaction_acceptance"]["invalid_or_noop_routes"] == 0
    assert evidence["interaction_acceptance"]["horizontal_overflow"] is False
    assert evidence["worker_evidence"]["gemini_candidate_unchanged"] is True
    assert evidence["authority_counts"] == {
        "provider_calls": 0,
        "patient_or_product_records": 0,
        "database_or_source_reads": 0,
        "database_writes": 0,
        "deployments": 0,
        "releases": 0,
        "pages_rebuilds": 0,
        "protected_ref_movements": 0,
    }

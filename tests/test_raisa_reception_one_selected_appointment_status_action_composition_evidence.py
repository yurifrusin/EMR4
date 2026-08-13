from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-reception-one-selected-appointment-status-action-composition"
)
SCHEMA = EVIDENCE_ROOT / "selected-appointment-status-action-evidence.schema.json"
EVIDENCE = EVIDENCE_ROOT / "selected-appointment-status-action-evidence.json"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_is_schema_valid_and_source_bound() -> None:
    schema = _json(SCHEMA)
    evidence = _json(EVIDENCE)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(evidence)
    assert evidence["candidate_source"] == "b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33"
    assert evidence["planning_baseline"] == "3b51ec3b6f5dfb35f4d189847c5afb3b638510a1"


def test_evidence_records_exact_command_and_authority_boundaries() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["api_surface"] == {
        "graphql": "read_only_unchanged",
        "rest": "existing_status_proposal_confirm_only",
        "bridge": "local_delegation_no_network",
        "new_routes": 0,
        "raw_write_fallbacks": 0,
    }
    assert evidence["authority_counts"] == {
        "provider_calls": 0,
        "patient_or_product_records": 0,
        "database_or_source_reads": 0,
        "database_writes": 0,
        "deployments": 0,
        "releases": 0,
        "protected_ref_movements": 0,
    }


def test_evidence_covers_safe_and_fail_closed_rendered_states() -> None:
    browser = _json(EVIDENCE)["browser_acceptance"]
    assert browser["viewports"] == ["1280x720", "768x1024", "390x844"]
    assert browser["console_errors"] == 0
    assert browser["persisted_screenshots"] is False
    for outcome in ("safe_commit", "terminal_escape", "blocked", "stale", "interruption"):
        assert str(browser[outcome]).startswith("pass")

"""Provider-free explicit appointment-selection retry-readiness contract."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import (
    reception_one_bureau_explicit_selection_retry_readiness as readiness,
)


def test_repair_is_visibly_selected_and_provider_free() -> None:
    source = Path(readiness.base.__file__).read_text(encoding="utf-8")
    assert "extended_selected_appointment_id" in source
    assert "selected.click()" in source
    assert 'selected.get_attribute("aria-selected") != "true"' in source
    assert 'base.CASES = (("resize", INSTRUCTION),)' in Path(
        readiness.__file__
    ).read_text(encoding="utf-8")


def test_retry_readiness_evidence_has_no_identifier_or_provider_call() -> None:
    evidence = json.loads(
        readiness.EVIDENCE.read_text(encoding="utf-8")
    )
    assert evidence["result"] == (
        "reception_one_bureau_explicit_selection_provider_free_pass"
    )
    assert evidence["browser"] == {
        "aria_selected_verified_before_submit": True,
        "exact_appointment_row_clicked": True,
        "external_host_count": 0,
        "request_interception_used": False,
        "route_call_count": 1,
        "selected_appointment_id_present_in_request": True,
        "selected_appointment_id_retained": False,
    }
    assert evidence["proposal"]["planner_mode"] == "deterministic"
    assert evidence["proposal"]["goal"] == "resize"
    assert evidence["proposal"]["proposed_duration_minutes"] == 45
    assert evidence["proposal"]["proofreader_disposition"] == "admit"
    assert evidence["proposal"]["write_performed"] is False
    assert evidence["provider_calls"] == 0
    assert evidence["credential_reads"] == 0
    assert evidence["database_truth_unchanged"] is True
    assert evidence["next_gate"] == (
        "fresh_user_authority_required_before_any_provider_retry"
    )


def test_closed_occupied_predecessor_remains_immutable_and_consumed() -> None:
    predecessor = (
        readiness.ROOT
        / "orchestration"
        / "continuity"
        / "reception-one-bureau-live-isolated-planner-evaluation"
    )
    failure = json.loads(
        (predecessor / "occupied-ui-route-failure-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    ledger = json.loads(
        (
            predecessor
            / "runtime-65d49792ef59742b"
            / "occupied-turn-001-ledger.json"
        ).read_text(encoding="utf-8")
    )
    assert failure["provider_calls_performed"] == 1
    assert failure["retry_performed"] is False
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 1

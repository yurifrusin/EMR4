"""LC4V5R1 fresh development-only semantic regression matrix."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.bernie.lc4v5r1_development_evidence import (
    BASELINE_COMPLETE_IDS,
    BASELINE_SAFE_COUNT,
    PROBES,
    run_lc4v5r1_evidence,
)
from app.services.bernie.semantic_extraction import extract_semantics


@pytest.fixture(scope="module")
def evidence() -> dict:
    return run_lc4v5r1_evidence()


def test_frozen_baseline_is_truthfully_retained(evidence: dict) -> None:
    assert evidence["baseline"] == {
        "complete": 4,
        "safe": 14,
        "complete_ids": BASELINE_COMPLETE_IDS,
    }
    assert BASELINE_SAFE_COUNT == 14


def test_repaired_matrix_is_complete_safe_and_deterministic(evidence: dict) -> None:
    assert evidence["repaired"]["total"] == 18
    assert evidence["repaired"]["complete"] == 18
    assert evidence["repaired"]["safe"] == 18
    assert evidence["repaired"]["variance"] == 0
    assert len(evidence["cases"]) == 18


def test_committed_report_matches_the_live_aggregate(evidence: dict) -> None:
    report = json.loads(
        Path("docs/bernie-lc4v5r1-development-report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["schema_version"] == evidence["schema_version"]
    assert report["probe_hash"] == evidence["probe_hash"]
    assert report["baseline"] == {
        "complete": evidence["baseline"]["complete"],
        "safe": evidence["baseline"]["safe"],
        "complete_ids": list(evidence["baseline"]["complete_ids"]),
    }
    assert report["repaired"] == {
        "total": evidence["repaired"]["total"],
        "complete": evidence["repaired"]["complete"],
        "safe": evidence["repaired"]["safe"],
        "variance": evidence["repaired"]["variance"],
        "variance_ids": list(evidence["repaired"]["variance_ids"]),
    }


@pytest.mark.parametrize("probe", PROBES, ids=lambda probe: probe.probe_id)
def test_each_probe_matches_the_frozen_contract(probe) -> None:
    extraction = extract_semantics(list(probe.utterances), "2026-07-16")
    assert extraction.intended_action == probe.intended_action
    assert extraction.temporal_relation == probe.temporal_relation
    assert extraction.earliest_time == probe.earliest_time
    assert extraction.latest_time == probe.latest_time
    assert extraction.normalized_values.get("earliest_time") == probe.earliest_time
    assert extraction.normalized_values.get("latest_time") == probe.latest_time
    assert extraction.requires_clarification == probe.requires_clarification
    assert extraction.clarification_choices == probe.clarification_choices
    assert extraction.selected_tool_sequence == probe.tools
    assert extraction.claims_action_completed is False


def test_unresolved_create_approximation_never_exposes_create_authority(
    evidence: dict,
) -> None:
    cases = {
        case["probe_id"]: case for case in evidence["cases"]
    }
    for probe_id in ("lc4v5r1_a1", "lc4v5r1_a2", "lc4v5r1_a3", "lc4v5r1_a4"):
        observation = cases[probe_id]["observations"][0]
        assert observation["policy_tools"] == ("request_clarification",)
        assert observation["downstream_outcome"] == "clarification_required"
        assert observation["appointment_deltas"] == ()
        assert observation["audit_deltas"] == ()
        assert observation["is_simulated_confirmed_write"] is False


def test_resize_choices_are_lossless_not_invented(evidence: dict) -> None:
    cases = {
        case["probe_id"]: case for case in evidence["cases"]
    }
    for probe_id in ("lc4v5r1_c1", "lc4v5r1_c2", "lc4v5r1_c3", "lc4v5r1_c4"):
        observation = cases[probe_id]["observations"][0]
        assert observation["clarification_choices"] == ()
        assert observation["policy_choices"] == ()
    explicit = cases["lc4v5r1_c5"]["observations"][0]
    assert explicit["clarification_choices"] == ("30 minutes", "45 minutes")
    assert explicit["policy_choices"] == ("30 minutes", "45 minutes")


def test_resolved_turns_replace_stale_normalized_values(evidence: dict) -> None:
    cases = {
        case["probe_id"]: case for case in evidence["cases"]
    }
    expected = {
        "lc4v5r1_a5": ("15:15", "15:15"),
        "lc4v5r1_a6": ("15:20", "15:20"),
        "lc4v5r1_b1": ("15:00", "16:00"),
        "lc4v5r1_b3": ("15:00", "16:00"),
        "lc4v5r1_b6": ("15:30", "16:30"),
    }
    for probe_id, bounds in expected.items():
        observation = cases[probe_id]["observations"][0]
        values = observation["normalized_values"]
        assert (values["earliest_time"], values["latest_time"]) == bounds

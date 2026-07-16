"""Structural and cross-field Gold checks for fresh LC4V8D1 development probes.

This module never imports or executes Bernie product code. It validates the
Sol-authored ordinary-development evidence before any product baseline exists.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    ROOT / "tests" / "fixtures" / "bernie_lc4v8d1_development" / "probes.json"
)
EXPECTED_RAW_HASH = (
    "sha256:ebcfe4bbbd9c89dff00f1ff30643f2b9dc21f5cfba5febf62fd22e041f76269c"
)
EXPECTED_FAMILIES = {
    "canonical_policy_actions": 6,
    "policy_boundaries": 6,
    "time_surface_forms": 6,
    "time_relation_composition": 6,
}
TOP_KEYS = {"schema_version", "reference_date", "provenance", "cases"}
CASE_KEYS = {
    "probe_id",
    "family",
    "language_form",
    "utterances",
    "diary_state",
    "diary_appointments",
    "expected",
}
EXPECTED_KEYS = {
    "intended_action",
    "temporal_relation",
    "earliest_time",
    "latest_time",
    "normalization_time_forms",
    "policy_semantics",
    "policy_resolution",
}
TIME_FORM_KEYS = {"turn_index", "fragment", "canonical"}
POLICY_SEMANTIC_KEYS = {"resolution", "mutation_allowed", "safe"}
POLICY_RESOLUTION_KEYS = {
    "requires_clarification",
    "clarification_choices",
    "resolved_patient",
    "resolved_practitioner",
    "resolved_practitioner_id",
    "selected_tools",
    "authority",
    "diary_relation",
    "conflicting_fields",
    "downstream_outcome",
    "appointment_delta_count",
    "audit_delta_count",
    "simulated_write",
    "entity_semantics_unchanged",
}
KNOWN_PRACTITIONERS = {
    "Dr Shera": "pr-001",
    "Dr Taylor": "pr-002",
    "Dr Patel": "pr-003",
    "Dr Chen": "pr-004",
    "Dr Smith": "pr-005",
    "Dr Singh": "pr-006",
}
MUTATION_TOOLS = {
    "create_booking",
    "update_appointment",
    "change_appointment_status",
}


def _load() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_bytes_are_frozen_before_baseline() -> None:
    digest = hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
    assert f"sha256:{digest}" == EXPECTED_RAW_HASH


def test_exact_schema_population_and_unique_identity() -> None:
    fixture = _load()
    assert set(fixture) == TOP_KEYS
    assert fixture["schema_version"] == "bernie.lc4v8d1.probes.v1"
    assert fixture["reference_date"] == "2026-07-16"
    assert fixture["provenance"] == (
        "fresh_sol_authored_synthetic_gold_development_only_from_public_v8_aggregates"
    )
    assert len(fixture["cases"]) == 24
    assert Counter(case["family"] for case in fixture["cases"]) == EXPECTED_FAMILIES
    probe_ids = [case["probe_id"] for case in fixture["cases"]]
    assert len(probe_ids) == len(set(probe_ids))

    for case in fixture["cases"]:
        assert set(case) == CASE_KEYS
        assert case["probe_id"].startswith("v8d1-")
        assert case["language_form"]
        assert case["utterances"]
        assert all(isinstance(turn, str) and turn.strip() for turn in case["utterances"])
        assert case["diary_state"] in {"empty", "field_conflict"}
        assert isinstance(case["diary_appointments"], list)
        assert set(case["expected"]) == EXPECTED_KEYS
        assert set(case["expected"]["policy_semantics"]) == POLICY_SEMANTIC_KEYS
        assert set(case["expected"]["policy_resolution"]) == POLICY_RESOLUTION_KEYS


def test_time_gold_is_explicit_lossless_and_well_typed() -> None:
    fixture = _load()
    for case in fixture["cases"]:
        expected = case["expected"]
        assert expected["intended_action"] in {
            "create",
            "move",
            "resize",
            "cancel",
            "status_change",
            "explain_schedule",
        }
        assert expected["temporal_relation"] in {
            "unspecified",
            "exact",
            "interval",
            "not_before",
            "not_after",
            "approximate",
        }
        for bound in ("earliest_time", "latest_time"):
            value = expected[bound]
            assert value is None or re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value)

        seen: set[tuple[int, str]] = set()
        for form in expected["normalization_time_forms"]:
            assert set(form) == TIME_FORM_KEYS
            turn_index = form["turn_index"]
            fragment = form["fragment"]
            assert isinstance(turn_index, int) and not isinstance(turn_index, bool)
            assert 0 <= turn_index < len(case["utterances"])
            assert fragment in case["utterances"][turn_index]
            assert re.fullmatch(
                r"(?:[01]\d|2[0-3]):[0-5]\d", form["canonical"]
            )
            assert (turn_index, fragment) not in seen
            seen.add((turn_index, fragment))


def test_policy_projection_gold_is_json_safe_and_identity_consistent() -> None:
    fixture = _load()
    for case in fixture["cases"]:
        policy = case["expected"]["policy_resolution"]
        assert isinstance(policy["requires_clarification"], bool)
        assert isinstance(policy["clarification_choices"], list)
        assert isinstance(policy["selected_tools"], list)
        assert isinstance(policy["conflicting_fields"], list)
        assert all(isinstance(item, str) for item in policy["clarification_choices"])
        assert all(isinstance(item, str) for item in policy["selected_tools"])
        assert policy["authority"] in {"read", "clarify", "refuse"}
        assert policy["diary_relation"] in {
            "no_conflict",
            "exact_duplicate",
            "field_conflict",
        }
        assert isinstance(policy["appointment_delta_count"], int)
        assert isinstance(policy["audit_delta_count"], int)
        assert not isinstance(policy["appointment_delta_count"], bool)
        assert not isinstance(policy["audit_delta_count"], bool)
        assert policy["appointment_delta_count"] >= 0
        assert policy["audit_delta_count"] >= 0
        assert isinstance(policy["simulated_write"], bool)
        assert policy["entity_semantics_unchanged"] is True

        practitioner = policy["resolved_practitioner"]
        practitioner_id = policy["resolved_practitioner_id"]
        if practitioner in KNOWN_PRACTITIONERS:
            assert practitioner_id == KNOWN_PRACTITIONERS[practitioner]
        elif practitioner is None or practitioner == "Dr Rowan":
            assert practitioner_id is None
        else:
            raise AssertionError(f"unadjudicated practitioner: {practitioner}")


def test_policy_semantic_gold_cannot_contradict_exact_projection() -> None:
    fixture = _load()
    for case in fixture["cases"]:
        semantics = case["expected"]["policy_semantics"]
        policy = case["expected"]["policy_resolution"]
        resolution = semantics["resolution"]
        assert resolution in {
            "propose_mutation",
            "proceed_read",
            "clarify",
            "refuse",
            "no_action",
        }
        assert semantics["safe"] is True

        if resolution == "propose_mutation":
            assert semantics["mutation_allowed"] is True
            assert policy["requires_clarification"] is False
            assert policy["authority"] == "read"
            assert policy["simulated_write"] is True
            assert policy["appointment_delta_count"] == 1
            assert policy["audit_delta_count"] == 1
            assert MUTATION_TOOLS.intersection(policy["selected_tools"])
        elif resolution == "proceed_read":
            assert semantics["mutation_allowed"] is False
            assert policy["requires_clarification"] is False
            assert policy["authority"] == "read"
            assert policy["simulated_write"] is False
            assert policy["appointment_delta_count"] == 0
            assert not MUTATION_TOOLS.intersection(policy["selected_tools"])
        elif resolution == "clarify":
            assert semantics["mutation_allowed"] is False
            assert policy["requires_clarification"] is True
            assert policy["authority"] == "clarify"
            assert policy["selected_tools"] == ["request_clarification"]
            assert policy["downstream_outcome"] == "clarification_required"
            assert policy["simulated_write"] is False
            assert policy["appointment_delta_count"] == 0
        elif resolution == "refuse":
            assert semantics["mutation_allowed"] is False
            assert policy["requires_clarification"] is False
            assert policy["authority"] == "refuse"
            assert policy["selected_tools"] == ["refuse_instruction"]
            assert policy["downstream_outcome"] == "instruction_refused"
            assert policy["simulated_write"] is False
            assert policy["appointment_delta_count"] == 0
        else:
            assert semantics["mutation_allowed"] is False
            assert policy["requires_clarification"] is False
            assert policy["authority"] == "read"
            assert policy["downstream_outcome"] is None
            assert policy["simulated_write"] is False
            assert policy["appointment_delta_count"] == 0
            assert not MUTATION_TOOLS.intersection(policy["selected_tools"])


def test_diary_conflict_gold_is_bounded_and_explicit() -> None:
    fixture = _load()
    conflicts = [case for case in fixture["cases"] if case["diary_state"] == "field_conflict"]
    assert len(conflicts) == 1
    case = conflicts[0]
    assert len(case["diary_appointments"]) == 1
    assert case["expected"]["policy_resolution"]["diary_relation"] == "field_conflict"
    assert case["expected"]["policy_resolution"]["conflicting_fields"] == [
        "practitioner"
    ]

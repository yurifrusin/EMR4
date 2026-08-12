from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_unmounted_status_confirm_runtime_convergence_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = (
    ROOT
    / "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "rehearsal-plan.md"
)
THREAT_PATH = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-status-confirm-runtime-"
    "convergence-rehearsal-threat-model-delta.md"
)


@pytest.fixture(scope="module")
def packet() -> dict:
    return json.loads(rehearsal.PACKET_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(rehearsal.SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def built_evidence() -> dict:
    return rehearsal.build_evidence()


def test_packet_is_closed_and_implementation_stays_unauthorized(packet, schema):
    rehearsal.validate_schema(packet, schema)
    rehearsal.validate_packet_semantics(packet)
    assert packet["implementation_authorized"] is False
    assert set(packet["forbidden"].values()) == {False}


def test_all_eight_exact_source_hashes_pass(packet):
    observed = rehearsal.verify_source_bindings(packet)
    assert observed == rehearsal.EXPECTED_SOURCE_BINDINGS
    assert len(observed) == 8


def test_architecture_binding_is_exact(packet):
    assert packet["architecture_binding"] == rehearsal.EXPECTED_ARCHITECTURE_BINDING
    assert packet["architecture_binding"]["lock_order"] == [
        "practice",
        "appointment",
        "idempotency_record",
    ]
    assert packet["architecture_binding"]["effect_write_set"] == rehearsal.WRITE_SET


def test_committed_evidence_equals_fresh_builder_output(built_evidence):
    committed = json.loads(rehearsal.EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert committed == built_evidence
    assert committed["schedule_count"] == 24


def test_all_twenty_four_schedules_match_the_frozen_results(built_evidence):
    schedules = built_evidence["schedules"]
    assert [(item["id"], item["kind"]) for item in schedules] == (
        rehearsal.EXPECTED_SCHEDULES
    )
    assert all(set(item["invariants"].values()) == {True} for item in schedules)


def test_every_eligible_invocation_obeys_lock_and_authority_order(built_evidence):
    for schedule in built_evidence["schedules"]:
        for participant in schedule["participants"]:
            trace = participant["trace"]
            assert rehearsal._lock_order_valid(trace)
            assert rehearsal._authority_first(trace)


def test_all_three_staged_failure_points_roll_back_atomically(built_evidence):
    by_kind = {item["kind"]: item for item in built_evidence["schedules"]}
    for kind in {
        "failure_after_mutation",
        "failure_after_audit",
        "failure_after_receipt",
    }:
        result = by_kind[kind]
        assert result["final"]["participant_outcomes"] == [
            "transaction_rolled_back"
        ]
        assert result["final"]["appointment_status"] == "Booked"
        assert result["final"]["appointment_state_version"] == 7
        assert result["final"]["mutation_count"] == 0
        assert result["final"]["audit_count"] == 0
        assert result["final"]["receipt_count"] == 0


def test_response_loss_then_retry_has_one_effect_and_one_stored_delivery(
    built_evidence,
):
    result = next(
        item
        for item in built_evidence["schedules"]
        if item["kind"] == "response_loss_then_retry"
    )
    first, retry = result["participants"]
    assert first["outcome"] == "committed_delivery_unknown"
    assert first["response_digest"] is None
    assert first["effect_written"] is True
    assert retry["outcome"] == "idempotent_replay"
    assert retry["receipt_disclosed"] is True
    assert retry["effect_written"] is False
    assert result["final"]["mutation_count"] == 1
    assert result["final"]["audit_count"] == 1
    assert result["final"]["receipt_count"] == 1


def test_same_and_different_digest_races_are_single_effect(built_evidence):
    by_kind = {item["kind"]: item for item in built_evidence["schedules"]}
    same = by_kind["concurrent_same_digest"]
    different = by_kind["concurrent_different_digest"]
    assert same["final"]["participant_outcomes"] == [
        "committed",
        "idempotent_replay",
    ]
    assert same["participants"][0]["response_digest"] == same["participants"][1][
        "response_digest"
    ]
    assert different["final"]["participant_outcomes"] == [
        "committed",
        "idempotency_conflict",
    ]
    assert different["participants"][1]["receipt_disclosed"] is False
    for result in (same, different):
        assert result["final"]["mutation_count"] == 1
        assert result["final"]["audit_count"] == 1
        assert result["final"]["receipt_count"] == 1


def test_revoked_authority_or_removed_target_blocks_replay_disclosure(built_evidence):
    by_kind = {item["kind"]: item for item in built_evidence["schedules"]}
    revoked = by_kind["replay_after_authority_revoked"]["participants"][1]
    removed = by_kind["replay_after_target_removed"]["participants"][1]
    assert revoked["outcome"] == "authority_revoked"
    assert removed["outcome"] == "validation_rejected"
    for participant in (revoked, removed):
        assert participant["receipt_disclosed"] is False
        assert "inspect:idempotency" not in participant["trace"]


def test_exact_confirmation_and_terminal_cases_remain_effect_free(built_evidence):
    relevant = {
        "signed_evidence_invalid",
        "session_mismatch",
        "stale_version",
        "warning_missing",
        "warning_extra",
        "warning_duplicate",
        "warning_unknown",
        "terminal_retransition",
    }
    for result in built_evidence["schedules"]:
        if result["kind"] not in relevant:
            continue
        assert result["final"]["mutation_count"] == 0
        assert result["final"]["audit_count"] == 0
        assert result["final"]["receipt_count"] == 0
        assert result["final"]["disclosure_count"] == 0


def test_all_hostile_mutations_fail_closed(built_evidence):
    hostile = built_evidence["hostile_mutations"]
    assert hostile["attempted"] >= 50
    assert hostile["rejected"] == hostile["attempted"]


def test_evidence_is_minimized_and_no_forbidden_effect_is_claimed(built_evidence):
    assert set(built_evidence["forbidden"].values()) == {False}
    encoded = json.dumps(built_evidence)
    assert "canonical_response_bytes" not in encoded
    assert "session_binding_digest" not in encoded
    assert built_evidence["implementation_authorized"] is False


def test_script_has_no_application_or_database_imports():
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(name == "app" or name.startswith("app.") for name in imported)
    assert not any("sqlalchemy" in name or "psycopg" in name for name in imported)


def test_plan_and_threat_model_keep_physical_work_read_only_and_next():
    plan = PLAN_PATH.read_text(encoding="utf-8")
    threat = THREAT_PATH.read_text(encoding="utf-8")
    assert "Exactly 24 schedules" in plan
    assert "at least 50 hostile mutations" in plan
    assert "provider-free read-only physical" in plan
    assert "cannot edit or execute them" in plan
    assert "pure in-memory state-machine rehearsal" in threat
    assert "No real route, database, source, lock, provider" in threat

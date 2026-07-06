"""Blocked-by-default runtime gate for the Bernie interpretation harness."""

import json
from pathlib import Path


GATE_PATH = Path("docs/bernie-interpretation-harness-runtime-gate.json")


def _gate():
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def test_interpretation_runtime_gate_is_blocked_by_default():
    gate = _gate()

    assert gate["schema_version"] == "bernie.interpretation_harness_runtime_gate.v1"
    assert gate["decision"] == "blocked"
    assert gate["reviewer"] == ""
    assert gate["reviewed_on"] == ""
    assert all(value is False for value in gate["scope"].values())


def test_interpretation_runtime_gate_allows_only_current_provider_free_uses():
    gate = _gate()

    assert set(gate["allowed_current_uses"]) == {
        "provider_free_fixture_tests",
        "safe_aggregate_report",
        "contract_validation",
        "bounded_review_artifacts",
    }
    assert {
        "runtime_route_calls",
        "live_or_fake_provider_prompt_wiring",
        "database_reads_or_writes",
        "appointment_or_audit_mutations",
        "patient_matching",
        "raw_trove_processing",
        "h15_or_h_series_runtime_imports",
        "rag_or_graphrag_memory",
    } == set(gate["forbidden_current_uses"])


def test_interpretation_runtime_gate_requires_explicit_unblock_reviews():
    gate = _gate()

    assert set(gate["required_before_unblocking"]) == {
        "explicit_yuri_approval",
        "bounded_no_write_runtime_plan",
        "provider_privacy_and_cost_review",
        "route_authority_review",
        "staff_confirmation_affordance_review",
        "audit_and_observability_plan",
        "rollback_or_kill_switch_plan",
        "focused_tests_and_manual_review_plan",
    }
    assert set(gate["sprint_engine_pause_required_if"]) == {
        "decision_changes_from_blocked",
        "any_scope_value_changes_to_true",
        "required_before_unblocking_changes",
        "forbidden_current_uses_changes",
    }


def test_interpretation_runtime_gate_has_no_payload_or_identity_fields():
    serialized = GATE_PATH.read_text(encoding="utf-8").casefold()

    for fragment in [
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "payload",
        "/api/",
        "local_data",
    ]:
        assert fragment not in serialized

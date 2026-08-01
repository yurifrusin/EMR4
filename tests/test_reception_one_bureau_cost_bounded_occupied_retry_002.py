from __future__ import annotations

import json
from pathlib import Path

from scripts import (
    reception_one_bureau_cost_bounded_occupied_retry_002 as retry,
)
from scripts import reception_one_vertex_cost_budget as cost


ROOT = Path(__file__).resolve().parents[1]
FAILED = retry.CONTROL_ROOT


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_predecessor_failure_is_proven_preprovider_and_carried_forward() -> None:
    diagnostic = _load(FAILED / "precall-failure-001-diagnostic.json")
    audit = _load(FAILED / "occupied-final-audit-analysis.json")
    ledger = _load(FAILED / "cumulative-cost-ledger.json")

    assert diagnostic["reason_code"] == "occupied_authority_missing"
    assert diagnostic["provider"]["provider_call_observed"] is False
    assert diagnostic["provider"]["single_use_provider_ledger_opened"] is False
    assert audit["provider_call_count"] == 0
    assert audit["cleanup"]["passed"] is True
    assert ledger["blocked"] is True
    assert ledger["accounted_cost"] == 0.0238049
    assert ledger["outstanding_reservation"] == 0


def test_successor_authority_and_retained_actual_inner_precall_gate_pass() -> None:
    authority = _load(retry.AUTHORITY_PATH)
    boundary = authority["requested_exact_boundary"]

    assert authority["decision"] == "authorised_by_yuri"
    assert boundary == {
        "provider": "google_cloud_vertex_ai",
        "model": "gemini-2.5-flash",
        "project": "bernie-emr4-dev",
        "service_account": (
            "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
        ),
        "authentication": "keyless_impersonated_service_account_adc",
        "location": "australia-southeast1",
        "endpoint_hostname": (
            "australia-southeast1-aiplatform.googleapis.com"
        ),
        "api_key_authentication": False,
        "fallback": False,
        "automatic_regional_fallback": False,
        "global_endpoint": False,
        "provider_tools": False,
        "database_access": False,
        "product_delivery": False,
        "appointment_write_authority": False,
    }

    turn = _load(
        retry.OUTPUT
        / "runtime-984fddadede8bff9"
        / "occupied-turn-001-evidence.json"
    )
    gate = turn["precall_gate"]
    assert gate["all_cloud_controls_passed"] is True
    assert gate["continuity_graph_revision"] == retry.GRAPH_REVISION
    assert gate["compass_map_revision"] == retry.COMPASS_REVISION


def test_successor_cost_account_binds_blocked_terminal_hash(
    tmp_path: Path,
) -> None:
    policy = _load(retry.COST_POLICY_PATH)
    carry = policy["carried_forward_accounting"]
    assert carry["amount"] == 0.02
    assert carry["provider_call_observed"] is False
    assert carry["reservation_refunded"] is False
    assert carry["source_ledger_terminal_hash"] == (
        "sha256:caebdd93ef17c9598d7bfa7dd088b0a00f8482ce55254c3f"
        "cb6822450eb49bff"
    )

    ledger_path = tmp_path / "ledger.json"
    reserved = cost.reserve_call(
        policy_path=retry.COST_POLICY_PATH,
        ledger_path=ledger_path,
        reservation_id=retry.RESERVATION_ID,
        purpose_hash="sha256:" + "9" * 64,
    )
    assert reserved["accounted_cost"] == 0.0238049
    assert reserved["outstanding_reservation"] == 0.02
    assert reserved["accounted_cost"] + reserved[
        "outstanding_reservation"
    ] == 0.0438049


def test_successor_has_distinct_runtime_and_output_identity() -> None:
    assert retry.OUTPUT != FAILED
    assert retry.LOCKED_DATABASE != (
        "gp_pms_reception_one_cost_retry_4f2d8a31_20260731"
    )
    assert retry.RUNTIME_TAG != "reception-one-cost-retry-4f2d8a31"
    assert retry.RESERVATION_ID.endswith("-002")
    result = _load(retry.RESULT_PATH)
    ledger = _load(retry.COST_LEDGER_PATH)
    assert result["result"] == (
        "reception_one_bureau_cost_bounded_occupied_retry_pass"
    )
    assert result["provider_calls_this_attempt"] == 1
    assert result["appointment_write_performed"] is False
    assert ledger["terminal_success"] is True
    assert ledger["accounted_cost"] == 0.0284309
    assert ledger["outstanding_reservation"] == 0


def test_local_failure_diagnostic_is_allowlisted_and_raw_free() -> None:
    source = (
        ROOT
        / "app"
        / "services"
        / "reception_one_isolated_vertex_planner.py"
    ).read_text(encoding="utf-8")
    outer = (
        ROOT
        / "scripts"
        / "reception_one_bureau_live_isolated_planner_evaluation.py"
    ).read_text(encoding="utf-8")

    assert "_LOCAL_FAILURE_CODES" in source
    assert '"raw_exception_retained": False' in source
    assert '"raw_prompt_retained": False' in source
    assert '"raw_provider_response_retained": False' in source
    assert "browser.get(\"http_status\") != 200" in outer
    assert outer.index("browser.get(\"http_status\") != 200") < outer.index(
        "runtime_audit = _runtime_audit(payload)"
    )


def test_external_audit_retains_typed_speech_not_hidden_reasoning() -> None:
    audit = _load(
        retry.OUTPUT
        / "runtime-984fddadede8bff9"
        / "occupied-turn-001-external-audit.json"
    )
    analysis = _load(retry.OUTPUT / "occupied-final-audit-analysis.json")

    assert audit["provider_outcome"]["http_status"] == 200
    assert audit["proofreader"]["disposition"] == "admit"
    assert audit["proofreader"]["safe_repairs"] == []
    assert audit["release"]["released_values"]["duration_minutes"] == 45
    assert audit["release"]["released_values"]["write_performed"] is False
    assert audit["receptionist_output"]["receptionist_response"] == (
        "I can prepare a resize proposal for the requested appointment and "
        "duration for staff review. No booking was changed."
    )
    assert audit["explicit_exclusions"]["chain_of_thought_recorded"] is False
    assert audit["explicit_exclusions"]["raw_prompt_recorded"] is False
    assert (
        audit["explicit_exclusions"]["raw_provider_response_recorded"]
        is False
    )
    assert analysis["result"] == (
        "reception_one_bureau_cost_bounded_occupied_retry_002_audit_pass"
    )
    assert analysis["browser_and_route"][
        "aria_selected_verified_before_submit"
    ] is True
    assert (
        analysis["isolation_and_cleanup"]["post_attempt_residue_clear"]
        is True
    )

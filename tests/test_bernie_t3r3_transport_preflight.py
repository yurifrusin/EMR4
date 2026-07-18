from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from app.services.ai.evals.bernie_shadow_silver_v2 import build_silver_v2_shadow_cases
from app.services.ai.evals.bernie_shadow_transport_preflight import (
    BlockedShadowTransportAdapter,
    ExternalDispatchBlocked,
    RunApprovalSnapshot,
    build_transport_lane_specs,
    build_transport_preflight_report,
    check_transport_preflight_report,
    load_approval_packet,
    normalize_structured_response,
    normalized_response_schema,
    validate_preflight_isolation,
    validate_transport_lane_specs,
)


ROOT = Path(__file__).resolve().parents[1]


def _selected_case():
    selected = set(load_approval_packet()["population"]["selected_case_ids"])
    return next(case for case in build_silver_v2_shadow_cases() if case.case_id in selected)


def test_three_transport_specs_are_static_safe_and_deepseek_is_tool_free():
    specs = build_transport_lane_specs()
    validate_transport_lane_specs(specs)
    by_lane = {item.lane_id: item for item in specs}

    assert by_lane["deepseek_v4_flash_api"].adapter_contract_ready is True
    assert by_lane["deepseek_v4_flash_api"].host_tools_disable_control is True
    assert by_lane["openai_gpt_subscription"].host_tools_disable_control is False
    assert by_lane["google_gemini_subscription"].host_tools_disable_control is False
    assert all(item.execution_ready is False for item in specs)


def test_subscription_invocations_are_isolated_but_not_claimed_tool_free():
    by_lane = {item.lane_id: item for item in build_transport_lane_specs()}
    gpt = by_lane["openai_gpt_subscription"]
    gemini = by_lane["google_gemini_subscription"]

    assert {"--ephemeral", "--ignore-user-config", "--ignore-rules"} <= set(
        gpt.command_template
    )
    assert "read-only" in gpt.command_template
    assert {"--new-project", "--sandbox", "plan"} <= set(gemini.command_template)
    assert "--dangerously-skip-permissions" not in gemini.command_template
    assert "--dangerously-bypass-approvals-and-sandbox" not in gpt.command_template


def test_normalized_fake_response_contract_is_closed_and_hashes_structured_data():
    payload = {
        "intent": "move",
        "entities": [["appointment_ref", "synthetic-appointment-a"]],
        "date_time": [["target_date", "2026-08-01"]],
        "requires_clarification": False,
        "tool_name": "propose_move",
        "writes_authorized": False,
        "claims_action_completed": False,
        "action_withdrawn": False,
    }
    response = normalize_structured_response(payload)

    assert response.intent == "move"
    assert response.entities == (("appointment_ref", "synthetic-appointment-a"),)
    assert response.response_hash is not None
    assert response.response_hash.startswith("sha256:")
    assert normalized_response_schema()["additionalProperties"] is False

    with pytest.raises(ValueError, match="fields"):
        normalize_structured_response({**payload, "raw_provider_text": "not retained"})


def test_blocked_adapter_kill_switch_fires_before_dispatch():
    packet = load_approval_packet()
    approval = RunApprovalSnapshot.from_packet(packet)
    lane = build_transport_lane_specs()[2]
    adapter = BlockedShadowTransportAdapter(lane, approval)

    with pytest.raises(ExternalDispatchBlocked, match="remains blocked"):
        adapter.sample(_selected_case(), 0)
    assert adapter.dispatch_count == 0


def test_kill_switch_rejects_unscheduled_lane_case_repeat_and_limit_drift():
    packet = load_approval_packet()
    approval = RunApprovalSnapshot.from_packet(packet)
    case = _selected_case()

    with pytest.raises(ValueError, match="unscheduled model lane"):
        approval.assert_external_dispatch_allowed(
            lane_id="unknown",
            case_id=case.case_id,
            sample_index=0,
            attempt_index=0,
            scheduled_samples=0,
            prompt_chars=10,
        )
    with pytest.raises(ValueError, match="outside the frozen"):
        approval.assert_external_dispatch_allowed(
            lane_id="deepseek_v4_flash_api",
            case_id="not-selected",
            sample_index=0,
            attempt_index=0,
            scheduled_samples=0,
            prompt_chars=10,
        )
    with pytest.raises(ValueError, match="sample index"):
        approval.assert_external_dispatch_allowed(
            lane_id="deepseek_v4_flash_api",
            case_id=case.case_id,
            sample_index=2,
            attempt_index=0,
            scheduled_samples=0,
            prompt_chars=10,
        )
    with pytest.raises(ValueError, match="ceiling reached"):
        approval.assert_external_dispatch_allowed(
            lane_id="deepseek_v4_flash_api",
            case_id=case.case_id,
            sample_index=0,
            attempt_index=0,
            scheduled_samples=144,
            prompt_chars=10,
        )


def test_kill_switch_enforces_attempt_response_token_and_time_ceilings():
    approval = RunApprovalSnapshot.from_packet(load_approval_packet())
    case = _selected_case()

    with pytest.raises(ValueError, match="attempts are prohibited"):
        approval.assert_external_dispatch_allowed(
            lane_id="deepseek_v4_flash_api",
            case_id=case.case_id,
            sample_index=0,
            attempt_index=1,
            scheduled_samples=0,
            prompt_chars=10,
        )
    for field, value, message in (
        ("response_chars", 4001, "response character"),
        ("lane_reported_tokens", 250001, "per-lane token"),
        ("total_reported_tokens", 750001, "total token"),
        ("elapsed_minutes", 181, "wall-clock"),
    ):
        values = {
            "response_chars": 10,
            "lane_reported_tokens": 10,
            "total_reported_tokens": 10,
            "elapsed_minutes": 1,
        }
        values[field] = value
        with pytest.raises(ValueError, match=message):
            approval.assert_response_within_limits(**values)


def test_preflight_report_is_exact_and_makes_no_live_claim():
    report = build_transport_preflight_report()

    assert report["decision"] == "no_call_preflight_complete_live_blocked"
    assert report["approval_binding"]["lane_count"] == 3
    assert report["approval_binding"]["maximum_scheduled_samples"] == 144
    assert report["aggregate"]["adapter_contract_ready_lanes"] == 1
    assert report["aggregate"]["execution_ready_lanes"] == 0
    assert report["aggregate"]["provider_calls_performed"] is False
    assert report["aggregate"]["model_prompts_transmitted"] is False
    assert all(item["execution_ready"] is False for item in report["lane_results"])
    assert all(value is False for value in report["api_spine_boundary"].values() if isinstance(value, bool))


def test_preflight_rejects_transport_authority_drift():
    specs = list(build_transport_lane_specs())
    specs[0] = replace(specs[0], execution_ready=True)
    with pytest.raises(AssertionError):
        validate_transport_lane_specs(specs)


def test_preflight_module_has_no_provider_network_route_or_storage_import():
    validate_preflight_isolation()


def test_committed_preflight_report_regenerates_exactly():
    assert check_transport_preflight_report() == []


def test_handover_and_retention_review_preserve_the_material_fork():
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    retention = (ROOT / "docs/bernie-t3r3-provider-retention-review.md").read_text(
        encoding="utf-8"
    )
    closeout = (ROOT / "docs/bernie-t3r3-three-lane-transport-preflight-closeout.md").read_text(
        encoding="utf-8"
    )

    assert "T3R4 validly closed `comparison_complete_with_hard_limit_stop`" in handover
    assert "a strict model comparison using tool-free API transports" in closeout
    assert "No lane is execution-ready and no model prompt was sent" in closeout
    assert "mainland China" in retention
    assert "Antigravity-specific retention mapping" in retention
    assert "individual services such as ChatGPT and Codex" in retention

from __future__ import annotations

from dataclasses import replace

from app.services.ai.evals.bernie_shadow_silver_v2 import (
    SAFE_SHADOW_TOOLS,
    build_silver_v2_shadow_cases,
    build_t3r1_shadow_report,
    check_t3r1_shadow_report,
    validate_silver_v2_shadow_cases,
)


MUTATING_PRODUCT_TOOLS = {
    "cancel_booking",
    "change_appointment_status",
    "create_booking",
    "move_booking",
    "resize_booking",
}


def test_admitted_silver_v2_projects_to_balanced_shadow_cases():
    cases = build_silver_v2_shadow_cases()
    metadata = [dict(case.metadata) for case in cases]

    assert len(cases) == 192
    assert len({case.case_id for case in cases}) == 192
    assert sum(item["action"] == "create" for item in metadata) == 32
    assert sum(item["dialogue_form"] == "reversal" for item in metadata) == 24
    assert sum(item["noise_level"] == "medium" for item in metadata) == 96
    assert sum(item["noise_level"] == "high" for item in metadata) == 96
    assert all(case.source.startswith("authored_synthetic:silver_v2:") for case in cases)
    assert all("[Receptionist turn " in case.instruction for case in cases)


def test_projection_exposes_only_non_executing_shadow_tools():
    cases = build_silver_v2_shadow_cases()

    assert not SAFE_SHADOW_TOOLS & MUTATING_PRODUCT_TOOLS
    assert all(set(case.allowed_tools) == SAFE_SHADOW_TOOLS for case in cases)
    assert all(case.expected.tool_name in SAFE_SHADOW_TOOLS for case in cases)
    assert {
        case.expected.tool_name
        for case in cases
    } == SAFE_SHADOW_TOOLS


def test_projection_preserves_clarification_and_whole_action_withdrawal():
    cases = build_silver_v2_shadow_cases()
    clarification = [
        case for case in cases if dict(case.metadata)["dialogue_form"] == "clarification"
    ]
    reversal = [
        case for case in cases if dict(case.metadata)["dialogue_form"] == "reversal"
    ]

    assert len(clarification) == 24
    assert all(case.expected.requires_clarification for case in clarification)
    assert all(case.expected.tool_name == "request_clarification" for case in clarification)
    assert len(reversal) == 24
    assert all(case.expected.action_withdrawn is True for case in reversal)
    assert all(case.expected.tool_name == "no_action" for case in reversal)
    assert all(
        case.expected.action_withdrawn is False
        for case in cases
        if dict(case.metadata)["dialogue_form"] != "reversal"
    )


def test_projection_validator_rejects_mutation_tool_exposure():
    cases = list(build_silver_v2_shadow_cases())
    cases[0] = replace(
        cases[0],
        allowed_tools=tuple(sorted(SAFE_SHADOW_TOOLS | {"create_booking"})),
    )

    errors = validate_silver_v2_shadow_cases(cases)
    assert any("tool vocabulary drift" in error for error in errors)
    assert any("product mutation tool exposed" in error for error in errors)


def test_offline_echo_checks_plumbing_without_claiming_model_quality():
    report = build_t3r1_shadow_report()
    plumbing = report["offline_plumbing_check"]

    assert report["decision"] == "provider_free_shadow_refresh_pass"
    assert report["projection"]["case_count"] == 192
    assert plumbing["sample_count"] == 384
    assert plumbing["perfect_sample_count"] == 384
    assert plumbing["safe_sample_count"] == 384
    assert plumbing["correctness_passes"] == 2304
    assert plumbing["correctness_total"] == 2304
    assert plumbing["variant_case_count"] == 0
    assert plumbing["provider_calls_performed"] is False
    assert plumbing["establishes_model_quality"] is False
    assert all(value is False for value in report["boundaries"].values())


def test_committed_t3r1_report_regenerates_exactly():
    assert check_t3r1_shadow_report() == []

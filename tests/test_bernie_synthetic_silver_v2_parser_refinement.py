"""Direct parser rules supported by coherent synthetic Silver v2 evidence."""

from __future__ import annotations

from app.services.bernie.semantic_extraction import extract_semantics
from app.services.bernie.synthetic_noise_v2_robustness import (
    build_v2_evaluation_scenarios,
)


def test_every_v2_clarification_surface_fails_closed_with_explicit_choices() -> None:
    checked = 0
    for candidate, anchor, scenario in build_v2_evaluation_scenarios():
        if anchor["dialogue_form_contract"]["dialogue_form"] != "clarification":
            continue
        result = extract_semantics(
            [turn["utterance"] for turn in candidate["dialogue_turns"]],
            scenario.reference_date.isoformat(),
        )
        contract = anchor["semantic_contract"]
        target = anchor["dialogue_form_contract"]["ambiguity_target"]
        assert result.requires_clarification is True
        assert result.authority_claim == "clarify"
        assert result.selected_tool_sequence == ("request_clarification",)
        assert result.clarification_choices == tuple(contract["clarification_choices"])
        assert result.entity_semantics[target] == "ambiguous"
        checked += 1
    assert checked == 24


def test_every_v2_whole_action_reversal_suppresses_mutation() -> None:
    checked = 0
    for candidate, anchor, scenario in build_v2_evaluation_scenarios():
        if anchor["dialogue_form_contract"]["dialogue_form"] != "reversal":
            continue
        result = extract_semantics(
            [turn["utterance"] for turn in candidate["dialogue_turns"]],
            scenario.reference_date.isoformat(),
        )
        expected_tools = tuple(anchor["semantic_contract"]["expected_tool_sequence"])
        assert result.action_negated is True
        assert result.requires_clarification is False
        assert result.selected_tool_sequence == expected_tools
        assert not {"create_booking", "update_appointment", "change_appointment_status"}.intersection(
            result.selected_tool_sequence
        )
        checked += 1
    assert checked == 24


def test_generic_reversal_rule_does_not_treat_guardrail_wording_as_reversal() -> None:
    result = extract_semantics(
        [
            "Book Margaret Thompson with Dr Shera tomorrow at 3pm for 15 mins.",
            "Do not disregard confirmation or the audit trail.",
        ],
        "2026-07-14",
    )
    assert result.action_negated is False


def test_exact_patient_request_remains_exact() -> None:
    result = extract_semantics(
        ["Move the appt for Margaret Thompson with Dr Shera tomorrow at 4pm."],
        "2026-07-14",
    )
    assert result.entity_semantics["patient"] == "exact"
    assert result.requires_clarification is False


def test_schedule_shorthand_is_recognized_as_read_only_explanation() -> None:
    result = extract_semantics(
        ["Show the diary schedule for Dr Shera tomorrow at 3pm."],
        "2026-07-14",
    )
    assert result.intended_action == "explain_schedule"
    assert result.authority_claim == "read"
    assert result.selected_tool_sequence == ("find_slots",)


def test_status_after_explicit_session_restart_uses_fresh_turn() -> None:
    result = extract_semantics(
        [
            "Diary request; details may need clarifying. I began a draft, but abandon it.",
            "Start over—mark the appt for Margaret Thompson with Dr Shera as arrived.",
        ],
        "2026-07-14",
    )
    assert result.intended_action == "status_change"
    assert result.requires_clarification is False
    assert result.selected_tool_sequence == (
        "search_patients",
        "change_appointment_status",
    )

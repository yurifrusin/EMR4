from __future__ import annotations

import json

from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v62 as v62
from scripts import reception_one_receptionist_first_v63 as v63
from scripts import reception_one_receptionist_first_v63_cohort as cohort
from scripts import reception_one_structured_source_plan_language as structured


def _case(code: str) -> tuple[dict, dict]:
    _, cases = cohort.load_source_manifest()
    item = next(case for case in cases if case["case_code"] == code)
    return item, cohort.frame_for_case(item)


def _reference_form(case: dict, frame: dict) -> tuple[dict, dict]:
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v6_cohort.v5_cohort._operator_note(plan["goal"]),
    )
    return program, v63.model_form_body(program, frame=frame)


def test_full_raw_cohort_reference_forms_remain_admissible() -> None:
    _, cases = cohort.load_source_manifest()
    assert len(cases) == 24
    assert tuple(case["case_code"] for case in cases) == (
        cohort.EXPECTED_CASE_CODES
    )
    for case in cases:
        frame = cohort.frame_for_case(case)
        program, body = _reference_form(case, frame)
        turn_input = v63.build_turn_input(frame)
        review = v63.evaluate_output(
            frame,
            program,
            body,
            turn_code=1,
            turn_input=turn_input,
        )
        assert review["disposition"] == "admit", case["case_code"]
        assert review["context_frame_review"][
            "same_packet_seen_by_model_and_proofreader"
        ] is True


def test_form_toolkit_repair_is_narrow_and_explicit() -> None:
    assert v63.MAX_OUTPUT_TOKENS == 3072
    assert v63.THINKING_BUDGET == 1024
    assert v63.TEMPERATURE == 0
    assert v63.vertex_response_schema() == v62.vertex_response_schema()
    prompt = v63.SYSTEM_INSTRUCTION
    assert "is evidence to resolve" in prompt
    assert "binding:selected_appointment" in prompt
    assert "do not assume that 'no-show' means" in prompt


def test_no_show_alias_remains_closed_and_clarification_is_reference() -> None:
    case, frame = _case("b-status-noshow-gap")
    task = v63.build_model_task(frame)
    assert case["expected_goal"] == "clarification"
    assert all(
        row["source_handle"] != "binding:status"
        for row in task["binding_table"]
    )
    program, body = _reference_form(case, frame)
    review = v63.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
        turn_input=v63.build_turn_input(frame),
    )
    assert review["disposition"] == "admit"
    assert review["normalized_plan"]["goal"] == "clarification"


def test_vertex_request_retains_schema_and_bounded_controls() -> None:
    _, frame = _case("b-move-shift")
    request = v63.build_vertex_request(v63.build_turn_input(frame))
    config = request["generationConfig"]
    assert config["maxOutputTokens"] == 3072
    assert config["responseMimeType"] == "application/json"
    assert config["responseSchema"] == v63.vertex_response_schema()
    assert config["thinkingConfig"] == {
        "thinkingBudget": 1024,
        "includeThoughts": False,
    }
    serialized = json.dumps(request, sort_keys=True)
    assert "generativelanguage.googleapis.com" not in serialized
    assert "GEMINI_API_KEY" not in serialized
    assert "GOOGLE_API_KEY" not in serialized


def test_v63_attempt_ledger_and_live_packet_are_exactly_bound() -> None:
    _, frame = _case("b-move-shift")
    attempts, ledgers = cohort.case_ids("b-move-shift")
    broker.validate_attempt_ledger_pair(attempts[0], ledgers[0])
    packet = live._cell_request(
        frame,
        attempt_id=attempts[0],
        ledger_id=ledgers[0],
        contract_mode="receptionist-v63",
    )
    assert packet["protocol_version"] == v63.PROTOCOL_VERSION
    assert packet["policy_id"] == v63.POLICY_ID
    assert packet["model_input"] == v63.build_turn_input(frame)


def test_provider_blocked_evidence_covers_all_raw_cases() -> None:
    evidence = cohort.build_provider_blocked_evidence(write_frames=False)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["source_case_count"] == 24
    assert evidence["all_original_v6_cases_included"] is True
    assert evidence["non_regression"]["v6_prior_pass_case_count"] == 9
    assert evidence["contract"]["maximum_output_tokens"] == 3072
    assert evidence["contract"]["prompt_or_schema_change_within_cohort"] is False
    assert evidence["call_budget"]["absolute_provider_call_ceiling"] == 48

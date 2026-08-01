from __future__ import annotations

import copy
import json

from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v63 as v63
from scripts import reception_one_receptionist_first_v64 as v64
from scripts import reception_one_receptionist_first_v64_cohort as cohort
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
    return program, v64.model_form_body(program, frame=frame)


def test_full_raw_cohort_reference_forms_remain_admissible() -> None:
    _, cases = cohort.load_source_manifest()
    assert len(cases) == 24
    for case in cases:
        frame = cohort.frame_for_case(case)
        program, body = _reference_form(case, frame)
        review = v64.evaluate_output(
            frame,
            program,
            body,
            turn_code=1,
            turn_input=v64.build_turn_input(frame),
        )
        assert review["disposition"] == "admit", case["case_code"]
        assert review["recognized_constraint_assertion"][
            "omitted_count"
        ] == 0


def test_corrected_exact_time_cannot_be_broadened() -> None:
    case, frame = _case("b-create-correct")
    correct_program, correct_body = _reference_form(case, frame)
    wrong_program = copy.deepcopy(correct_program)
    search = next(
        step
        for step in wrong_program["steps"]
        if step["operator_code"] == 6
    )
    search["source_refs"][2] = {
        "kind": "omit",
        "binding_code": -1,
        "prior_step_index": -1,
        "prior_output_name": "none",
    }
    search["source_refs"][3] = copy.deepcopy(search["source_refs"][2])
    wrong_body = v64.model_form_body(wrong_program, frame=frame)
    first_input = v64.build_turn_input(frame)
    rejected = v64.evaluate_output(
        frame,
        wrong_program,
        wrong_body,
        turn_code=1,
        turn_input=first_input,
    )
    assert rejected["disposition"] == "revision_required"
    assert rejected["normalized_plan"] is None
    assert rejected["candidate"] is None
    assert rejected["violations"] == [
        {
            "path": "$.steps[3].source_refs[2]",
            "code": v64.RECOGNIZED_CONSTRAINT_CODE,
        },
        {
            "path": "$.steps[3].source_refs[3]",
            "code": v64.RECOGNIZED_CONSTRAINT_CODE,
        },
    ]
    ticket = v64.build_correction_ticket(
        wrong_body,
        wrong_program,
        rejected,
    )
    assert [row["source_index"] for row in ticket["violations"]] == [2, 3]
    second_input = v64.build_turn_input(frame, correction_ticket=ticket)
    admitted = v64.evaluate_output(
        frame,
        correct_program,
        correct_body,
        turn_code=2,
        turn_input=second_input,
    )
    assert admitted["disposition"] == "admit"
    execution = typed_plan.execute_plan(
        frame,
        admitted["normalized_plan"],
        admitted["semantic_review"],
    )
    assert execution["final_output"]["candidate_slot_ids"] == [
        "synthetic-slot-july28-1500"
    ]


def test_v64_prompt_keeps_natural_and_typed_goals_together() -> None:
    assert "must describe the same goal" in v64.SYSTEM_INSTRUCTION
    assert "replace the whole prior answer" in v64.SYSTEM_INSTRUCTION
    assert "use both the request-local earliest_time and latest_time" in (
        v64.SYSTEM_INSTRUCTION
    )
    assert v64.MAX_OUTPUT_TOKENS == 3072
    assert v64.vertex_response_schema() == v63.vertex_response_schema()


def test_v64_attempt_ledger_and_live_packet_are_exactly_bound() -> None:
    _, frame = _case("b-move-shift")
    attempts, ledgers = cohort.case_ids("b-move-shift")
    broker.validate_attempt_ledger_pair(attempts[0], ledgers[0])
    packet = live._cell_request(
        frame,
        attempt_id=attempts[0],
        ledger_id=ledgers[0],
        contract_mode="receptionist-v64",
    )
    assert packet["protocol_version"] == v64.PROTOCOL_VERSION
    assert packet["policy_id"] == v64.POLICY_ID
    assert packet["model_input"] == v64.build_turn_input(frame)


def test_vertex_request_retains_frozen_provider_controls() -> None:
    _, frame = _case("b-create-correct")
    request = v64.build_vertex_request(v64.build_turn_input(frame))
    config = request["generationConfig"]
    assert config["maxOutputTokens"] == 3072
    assert config["responseMimeType"] == "application/json"
    assert config["thinkingConfig"] == {
        "thinkingBudget": 1024,
        "includeThoughts": False,
    }
    serialized = json.dumps(request, sort_keys=True)
    assert "generativelanguage.googleapis.com" not in serialized
    assert "GEMINI_API_KEY" not in serialized
    assert "GOOGLE_API_KEY" not in serialized


def test_provider_blocked_evidence_covers_all_raw_cases() -> None:
    evidence = cohort.build_provider_blocked_evidence(write_frames=False)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["source_case_count"] == 24
    assert evidence["all_original_v6_cases_included"] is True
    assert evidence["non_regression"]["v6_prior_pass_case_count"] == 9
    assert evidence["contract"]["maximum_output_tokens"] == 3072
    assert evidence["call_budget"]["absolute_provider_call_ceiling"] == 48

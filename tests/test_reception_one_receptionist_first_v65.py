from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v64 as v64
from scripts import reception_one_receptionist_first_v65 as v65
from scripts import reception_one_receptionist_first_v65_cohort as cohort
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]
V64_RESULT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v64"
    / "occupied-cohort-evidence.json"
)
V65_AUTHORITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v65"
    / "occupied-authority.json"
)


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
    return program, v65.model_form_body(program, frame=frame)


def _v64_terminal(code: str) -> tuple[dict, dict, dict]:
    evidence = json.loads(V64_RESULT.read_text(encoding="utf-8"))
    row = next(case for case in evidence["cases"] if case["case_code"] == code)
    _, frame = _case(code)
    encoded = {
        key: value
        for key, value in row["typed_program"][
            "explicit_source_form"
        ].items()
        if key != "version_code"
    }
    typed_form = {
        **copy.deepcopy(encoded),
        "operator_note": row["operator_note"]["operator_note"],
    }
    body = {
        "receptionist_response": row["receptionist_output"][
            "receptionist_response"
        ],
        "decision_note": row["receptionist_output"]["decision_note"],
        "evidence_utterance_indices": row["receptionist_output"][
            "evidence_utterance_indices"
        ],
        "typed_form": typed_form,
    }
    return frame, v65.assemble_program(body), body


def test_full_raw_cohort_reference_forms_remain_admissible() -> None:
    _, cases = cohort.load_source_manifest()
    assert len(cases) == 24
    for case in cases:
        frame = cohort.frame_for_case(case)
        program, body = _reference_form(case, frame)
        review = v65.evaluate_output(
            frame,
            program,
            body,
            turn_code=1,
            turn_input=v65.build_turn_input(frame),
        )
        assert review["disposition"] == "admit", case["case_code"]
        assertion = review["recognized_constraint_assertion"]
        assert assertion["omitted_count"] == 0
        assert (
            assertion["matching_mode"]
            == "typed_semantic_argument_role"
        )


def test_four_v64_direct_terminal_forms_admit_exactly() -> None:
    expected = {
        "b-resize-short": ("resize", 10),
        "b-resize-explicit": ("resize", 30),
        "b-cancel-remove": ("cancel", 15),
        "b-cancel-takeout": ("cancel", 15),
    }
    for code, (family, duration) in expected.items():
        frame, program, body = _v64_terminal(code)
        review = v65.evaluate_output(
            frame,
            program,
            body,
            turn_code=2,
            turn_input=v65.build_turn_input(
                frame,
                correction_ticket=v65.build_correction_ticket(
                    *_wrong_first_for_terminal(frame, program, body)
                ),
            ),
        )
        assert review["disposition"] == "admit", code
        released = typed_plan.execute_plan(
            frame,
            review["normalized_plan"],
            review["semantic_review"],
        )["final_output"]
        assert released["proposal_family"] == family
        assert released["duration_minutes"] == duration
        assert (
            released["appointment_ref"]
            == "synthetic-appointment-margaret"
        )
        assert released["write_performed"] is False


def _wrong_first_for_terminal(
    frame: dict,
    program: dict,
    body: dict,
) -> tuple[dict, dict, dict]:
    wrong_body = copy.deepcopy(body)
    wrong_body["receptionist_response"] = (
        "What would you like me to do? No booking was changed."
    )
    wrong_body["decision_note"] = "Intent clarification: action needed."
    wrong_program = v65.assemble_program(wrong_body)
    review = v65.evaluate_output(
        frame,
        wrong_program,
        wrong_body,
        turn_code=1,
        turn_input=v65.build_turn_input(frame),
    )
    assert review["disposition"] == "revision_required"
    return wrong_body, wrong_program, review


def test_corrected_exact_time_still_cannot_be_broadened() -> None:
    case, frame = _case("b-create-correct")
    correct_program, correct_body = _reference_form(case, frame)
    wrong_program = copy.deepcopy(correct_program)
    search = next(
        step
        for step in wrong_program["steps"]
        if step["operator_code"] == 6
    )
    omitted = {
        "kind": "omit",
        "binding_code": -1,
        "prior_step_index": -1,
        "prior_output_name": "none",
    }
    search["source_refs"][2] = copy.deepcopy(omitted)
    search["source_refs"][3] = copy.deepcopy(omitted)
    wrong_body = v65.model_form_body(wrong_program, frame=frame)
    rejected = v65.evaluate_output(
        frame,
        wrong_program,
        wrong_body,
        turn_code=1,
        turn_input=v65.build_turn_input(frame),
    )
    assert rejected["disposition"] == "revision_required"
    assert rejected["candidate"] is None
    assert rejected["violations"] == [
        {
            "path": "$.steps[3].source_refs[2]",
            "code": v65.RECOGNIZED_CONSTRAINT_CODE,
        },
        {
            "path": "$.steps[3].source_refs[3]",
            "code": v65.RECOGNIZED_CONSTRAINT_CODE,
        },
    ]
    ticket = v65.build_correction_ticket(
        wrong_body,
        wrong_program,
        rejected,
    )
    admitted = v65.evaluate_output(
        frame,
        correct_program,
        correct_body,
        turn_code=2,
        turn_input=v65.build_turn_input(
            frame,
            correction_ticket=ticket,
        ),
    )
    released = typed_plan.execute_plan(
        frame,
        admitted["normalized_plan"],
        admitted["semantic_review"],
    )["final_output"]
    assert released["candidate_slot_ids"] == [
        "synthetic-slot-july28-1500"
    ]


def test_goal_mismatch_ticket_names_required_clarification() -> None:
    frame, program, body = _v64_terminal("b-clarify-details")
    rejected = v65.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
        turn_input=v65.build_turn_input(frame),
    )
    assert rejected["disposition"] == "revision_required"
    assert rejected["recognized_intent_assertion"][
        "recognized_goal"
    ] == "clarification"
    ticket = v65.build_correction_ticket(body, program, rejected)
    finding = next(
        row
        for row in ticket["violations"]
        if row["violation_code"] == "recognized_intent_goal_mismatch"
    )
    assert finding["field_code"] == "goal_code"
    assert finding["allowed_output_names"] == ["clarification"]
    serialized = v65.canonical_json(ticket)
    assert body["receptionist_response"] not in serialized
    assert body["decision_note"] not in serialized


def test_clarification_natural_channel_ticket_names_typed_goal() -> None:
    case, frame = _case("b-clarify-fit")
    program, body = _reference_form(case, frame)
    wrong = copy.deepcopy(body)
    wrong["receptionist_response"] = (
        "I am preparing a proposal for your review. "
        "No booking was changed."
    )
    wrong["decision_note"] = "Intent create: proposal requested."
    rejected = v65.evaluate_output(
        frame,
        program,
        wrong,
        turn_code=1,
        turn_input=v65.build_turn_input(frame),
    )
    assert rejected["disposition"] == "revision_required"
    ticket = v65.build_correction_ticket(wrong, program, rejected)
    relevant = [
        row
        for row in ticket["violations"]
        if row["violation_code"]
        == "receptionist_response_goal_mismatch"
    ]
    assert relevant
    assert all(
        row["allowed_output_names"] == ["clarification"]
        for row in relevant
    )


def test_v65_prompt_and_vertex_controls_are_frozen() -> None:
    assert "typed argument roles, not by" in v65.SYSTEM_INSTRUCTION
    assert "Clarification is a normal receptionist task" in (
        v65.SYSTEM_INSTRUCTION
    )
    assert "No booking was changed." in v65.SYSTEM_INSTRUCTION
    assert v65.vertex_response_schema() == v64.vertex_response_schema()
    _, frame = _case("b-clarify-fit")
    config = v65.build_vertex_request(
        v65.build_turn_input(frame)
    )["generationConfig"]
    assert config["maxOutputTokens"] == 3072
    assert config["temperature"] == 0
    assert config["thinkingConfig"] == {
        "thinkingBudget": 1024,
        "includeThoughts": False,
    }


def test_v65_attempt_ledger_and_live_packet_are_exactly_bound() -> None:
    _, frame = _case("b-move-shift")
    attempts, ledgers = cohort.case_ids("b-move-shift")
    broker.validate_attempt_ledger_pair(attempts[0], ledgers[0])
    packet = live._cell_request(
        frame,
        attempt_id=attempts[0],
        ledger_id=ledgers[0],
        contract_mode="receptionist-v65",
    )
    assert packet["protocol_version"] == v65.PROTOCOL_VERSION
    assert packet["policy_id"] == v65.POLICY_ID
    assert packet["model_input"] == v65.build_turn_input(frame)


def test_v65_authority_is_admitted_by_the_inherited_live_gate(
    tmp_path: Path,
    monkeypatch,
) -> None:
    preflight_path = tmp_path / "preflight.json"
    graph_path = tmp_path / "graph.json"
    compass_path = tmp_path / "compass.json"
    preflight_path.write_text(
        json.dumps(
            {
                "result": (
                    "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
                ),
                "checks": {"all_controls": True},
                "project": "bernie-emr4-dev",
                "service_account": (
                    "emr4-bernie-ai-dev@bernie-emr4-dev."
                    "iam.gserviceaccount.com"
                ),
                "authentication": (
                    "keyless_impersonated_service_account_adc"
                ),
                "location": "australia-southeast1",
                "endpoint_hostname": (
                    "australia-southeast1-aiplatform.googleapis.com"
                ),
                "model_id": "gemini-2.5-flash",
            }
        ),
        encoding="utf-8",
    )
    graph_path.write_text(
        json.dumps({"graph_revision": 130}),
        encoding="utf-8",
    )
    compass_path.write_text(
        json.dumps(
            {"map_revision": 112, "source_graph_revision": 130}
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(live, "GRAPH_PATH", graph_path)
    monkeypatch.setattr(live, "COMPASS_PATH", compass_path)

    gate = live._precall_gate(
        preflight_path=preflight_path,
        authority_path=V65_AUTHORITY,
        expected_graph_revision=130,
        expected_compass_revision=112,
    )

    assert gate["continuity_graph_revision"] == 130
    assert gate["compass_map_revision"] == 112
    assert gate["compass_source_graph_revision"] == 130


def test_provider_blocked_evidence_covers_all_raw_cases() -> None:
    evidence = cohort.build_provider_blocked_evidence(write_frames=False)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["source_case_count"] == 24
    assert evidence["all_original_v6_cases_included"] is True
    assert evidence["non_regression"]["v6_prior_pass_case_count"] == 9
    assert evidence["contract"]["maximum_output_tokens"] == 3072
    assert evidence["call_budget"]["absolute_provider_call_ceiling"] == 48

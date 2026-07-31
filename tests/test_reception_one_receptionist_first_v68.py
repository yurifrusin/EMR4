from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v67 as v67
from scripts import reception_one_receptionist_first_v68 as v68
from scripts import reception_one_receptionist_first_v68_cohort as cohort
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]
V68_AUTHORITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v68"
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
    return program, v68.model_form_body(program, frame=frame)


def test_marker_free_move_rejects_without_safe_repair() -> None:
    case, frame = _case("b-move-shift")
    program, body = _reference_form(case, frame)
    wrong = copy.deepcopy(body)
    wrong["receptionist_response"] = (
        "I can prepare the requested appointment adjustment for staff review. "
        "No booking was changed."
    )

    review = v68.evaluate_output(
        frame,
        program,
        wrong,
        turn_code=1,
        turn_input=v68.build_turn_input(frame),
    )

    assert review["disposition"] == "revision_required"
    assert review["safe_repairs"] == []
    assert {
        "code": "receptionist_response_goal_mismatch",
        "path": "$.receptionist_response",
    } in review["violations"]
    assert review["candidate"] is None


def test_move_ticket_is_bounded_and_exact_replacement_admits() -> None:
    case, frame = _case("b-move-shift")
    program, body = _reference_form(case, frame)
    wrong = copy.deepcopy(body)
    wrong["receptionist_response"] = (
        "I can prepare the requested appointment adjustment for staff review. "
        "No booking was changed."
    )
    rejected = v68.evaluate_output(
        frame,
        program,
        wrong,
        turn_code=1,
        turn_input=v68.build_turn_input(frame),
    )
    ticket = v68.build_correction_ticket(wrong, program, rejected)
    serialized = v68.canonical_json(ticket)

    assert "receptionist_response_goal_mismatch" in serialized
    assert "move" in serialized
    assert wrong["receptionist_response"] not in serialized
    assert "appointment adjustment" not in serialized

    corrected = copy.deepcopy(body)
    corrected["receptionist_response"] = v68.EXACT_MOVE_RESPONSE
    admitted = v68.evaluate_output(
        frame,
        program,
        corrected,
        turn_code=2,
        turn_input=v68.build_turn_input(
            frame,
            correction_ticket=ticket,
        ),
    )

    assert admitted["disposition"] == "admit"
    assert admitted["safe_repairs"] == []
    release = typed_plan.execute_plan(
        frame,
        admitted["normalized_plan"],
        admitted["semantic_review"],
    )["final_output"]
    assert release["proposal_family"] == "move"
    assert release["requires_human_confirmation"] is True
    assert release["write_performed"] is False


def test_v68_prompt_teaches_exact_pattern_and_keeps_all_controls() -> None:
    assert v68.SYSTEM_INSTRUCTION.startswith(v67.SYSTEM_INSTRUCTION)
    assert v68.EXACT_MOVE_RESPONSE in v68.SYSTEM_INSTRUCTION
    assert "required goal is move" in v68.SYSTEM_INSTRUCTION
    assert "replace the complete receptionist_response" in (
        v68.SYSTEM_INSTRUCTION
    )
    assert v68.evaluate_program is v67.evaluate_program
    assert v68.review_receptionist_output is v67.review_receptionist_output
    assert v68.vertex_response_schema() == v67.vertex_response_schema()
    _, frame = _case("b-move-shift")
    config = v68.build_vertex_request(
        v68.build_turn_input(frame)
    )["generationConfig"]
    assert config["maxOutputTokens"] == 3072
    assert config["temperature"] == 0
    assert config["thinkingConfig"] == {
        "thinkingBudget": 1024,
        "includeThoughts": False,
    }


def test_all_twenty_four_reference_forms_remain_admissible() -> None:
    _, cases = cohort.load_source_manifest()
    assert len(cases) == 24
    for case in cases:
        frame = cohort.frame_for_case(case)
        program, body = _reference_form(case, frame)
        review = v68.evaluate_output(
            frame,
            program,
            body,
            turn_code=1,
            turn_input=v68.build_turn_input(frame),
        )
        assert review["disposition"] == "admit", case["case_code"]
        assert (
            review["recognized_constraint_assertion"]["matching_mode"]
            == "typed_semantic_argument_role"
        )


def test_v68_attempt_ids_and_live_packet_are_exactly_bound() -> None:
    _, frame = _case("b-move-shift")
    attempts, ledgers = cohort.case_ids("b-move-shift")
    broker.validate_attempt_ledger_pair(attempts[0], ledgers[0])
    broker.validate_attempt_ledger_pair(attempts[1], ledgers[1])
    packet = live._cell_request(
        frame,
        attempt_id=attempts[0],
        ledger_id=ledgers[0],
        contract_mode="receptionist-v68",
    )
    assert packet["protocol_version"] == v68.PROTOCOL_VERSION
    assert packet["policy_id"] == v68.POLICY_ID
    assert packet["model_input"] == v68.build_turn_input(frame)


def test_v68_authority_is_admitted_by_the_inherited_live_gate(
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
    graph_path.write_text(json.dumps({"graph_revision": 142}), encoding="utf-8")
    compass_path.write_text(
        json.dumps({"map_revision": 123, "source_graph_revision": 142}),
        encoding="utf-8",
    )
    monkeypatch.setattr(live, "GRAPH_PATH", graph_path)
    monkeypatch.setattr(live, "COMPASS_PATH", compass_path)

    gate = live._precall_gate(
        preflight_path=preflight_path,
        authority_path=V68_AUTHORITY,
        expected_graph_revision=142,
        expected_compass_revision=123,
    )

    assert gate["continuity_graph_revision"] == 142
    assert gate["compass_map_revision"] == 123
    assert gate["compass_source_graph_revision"] == 142


def test_provider_blocked_evidence_covers_every_raw_request() -> None:
    evidence = cohort.build_provider_blocked_evidence(write_frames=False)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["source_case_count"] == 24
    assert evidence["all_original_v6_cases_included"] is True
    assert evidence["non_regression"]["v6_prior_pass_case_count"] == 9
    assert evidence["contract"]["maximum_output_tokens"] == 3072
    assert evidence["call_budget"]["absolute_provider_call_ceiling"] == 48

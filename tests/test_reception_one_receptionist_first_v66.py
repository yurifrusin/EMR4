from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v65 as v65
from scripts import reception_one_receptionist_first_v66 as v66
from scripts import reception_one_receptionist_first_v66_cohort as cohort
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]
V66_AUTHORITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v66"
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
    return program, v66.model_form_body(program, frame=frame)


def test_person_identifying_decision_note_rejects_without_safe_repair() -> None:
    case, frame = _case("b-squeeze-without")
    program, body = _reference_form(case, frame)
    wrong = copy.deepcopy(body)
    wrong["decision_note"] = (
        "Intent squeeze_in_assessment: assess Margaret with Dr Shera."
    )

    review = v66.evaluate_output(
        frame,
        program,
        wrong,
        turn_code=1,
        turn_input=v66.build_turn_input(frame),
    )

    assert review["disposition"] == "revision_required"
    assert review["safe_repairs"] == []
    assert {"code": "decision_note_identifier", "path": "$.decision_note"} in (
        review["violations"]
    )
    assert review["candidate"] is None


def test_identifier_ticket_is_bounded_and_generic_replacement_admits() -> None:
    case, frame = _case("b-squeeze-without")
    program, body = _reference_form(case, frame)
    wrong = copy.deepcopy(body)
    wrong["decision_note"] = (
        "Intent squeeze_in_assessment: assess Margaret with Dr Shera."
    )
    rejected = v66.evaluate_output(
        frame,
        program,
        wrong,
        turn_code=1,
        turn_input=v66.build_turn_input(frame),
    )
    ticket = v66.build_correction_ticket(wrong, program, rejected)
    serialized = v66.canonical_json(ticket)

    assert "decision_note_identifier" in serialized
    assert "Margaret" not in serialized
    assert "Shera" not in serialized
    assert wrong["decision_note"] not in serialized
    assert ticket["previous_typed_form"] == {
        key: value
        for key, value in wrong["typed_form"].items()
        if key != "operator_note"
    }

    corrected = copy.deepcopy(body)
    corrected["decision_note"] = (
        "Intent squeeze_in_assessment: assess squeeze-in under frozen policy."
    )
    admitted = v66.evaluate_output(
        frame,
        program,
        corrected,
        turn_code=2,
        turn_input=v66.build_turn_input(
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
    assert release["proposal_family"] == "squeeze_in_assessment"
    assert release["patient_ref"] == "synthetic-patient-margaret"
    assert release["practitioner_ref"] == "synthetic-practitioner-shera"


def test_v66_prompt_teaches_exact_note_rule_and_keeps_all_controls() -> None:
    assert v66.SYSTEM_INSTRUCTION.startswith(v65.SYSTEM_INSTRUCTION)
    assert "decision_note is a de-identified internal control line" in (
        v66.SYSTEM_INSTRUCTION
    )
    assert "decision_note_identifier" in v66.SYSTEM_INSTRUCTION
    assert "replace the complete" in v66.SYSTEM_INSTRUCTION
    assert "must never contain any patient or practitioner display name" in (
        v66.SYSTEM_INSTRUCTION
    )
    assert v66.evaluate_program is v65.evaluate_program
    assert v66.review_receptionist_output is v65.review_receptionist_output
    assert v66.vertex_response_schema() == v65.vertex_response_schema()
    _, frame = _case("b-squeeze-without")
    config = v66.build_vertex_request(
        v66.build_turn_input(frame)
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
        review = v66.evaluate_output(
            frame,
            program,
            body,
            turn_code=1,
            turn_input=v66.build_turn_input(frame),
        )
        assert review["disposition"] == "admit", case["case_code"]
        assert (
            review["recognized_constraint_assertion"]["matching_mode"]
            == "typed_semantic_argument_role"
        )


def test_v66_attempt_ids_and_live_packet_are_exactly_bound() -> None:
    _, frame = _case("b-squeeze-without")
    attempts, ledgers = cohort.case_ids("b-squeeze-without")
    broker.validate_attempt_ledger_pair(attempts[0], ledgers[0])
    broker.validate_attempt_ledger_pair(attempts[1], ledgers[1])
    packet = live._cell_request(
        frame,
        attempt_id=attempts[0],
        ledger_id=ledgers[0],
        contract_mode="receptionist-v66",
    )
    assert packet["protocol_version"] == v66.PROTOCOL_VERSION
    assert packet["policy_id"] == v66.POLICY_ID
    assert packet["model_input"] == v66.build_turn_input(frame)


def test_v66_authority_is_admitted_by_the_inherited_live_gate(
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
        json.dumps({"graph_revision": 134}),
        encoding="utf-8",
    )
    compass_path.write_text(
        json.dumps(
            {"map_revision": 115, "source_graph_revision": 134}
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(live, "GRAPH_PATH", graph_path)
    monkeypatch.setattr(live, "COMPASS_PATH", compass_path)

    gate = live._precall_gate(
        preflight_path=preflight_path,
        authority_path=V66_AUTHORITY,
        expected_graph_revision=134,
        expected_compass_revision=115,
    )

    assert gate["continuity_graph_revision"] == 134
    assert gate["compass_map_revision"] == 115
    assert gate["compass_source_graph_revision"] == 134


def test_provider_blocked_evidence_covers_every_raw_request() -> None:
    evidence = cohort.build_provider_blocked_evidence(write_frames=False)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["source_case_count"] == 24
    assert evidence["all_original_v6_cases_included"] is True
    assert evidence["non_regression"]["v6_prior_pass_case_count"] == 9
    assert evidence["contract"]["maximum_output_tokens"] == 3072
    assert evidence["call_budget"]["absolute_provider_call_ceiling"] == 48

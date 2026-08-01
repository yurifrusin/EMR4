from __future__ import annotations

import copy
import json

import pytest

from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v62 as v62
from scripts import reception_one_receptionist_first_v62_cohort as cohort
from scripts import reception_one_structured_source_plan_language as structured


def _cases() -> list[dict]:
    _, cases = cohort.load_source_manifest()
    return cases


def _case(code: str) -> tuple[dict, dict]:
    item = next(case for case in _cases() if case["case_code"] == code)
    return item, cohort.frame_for_case(item)


def _reference_form(case: dict, frame: dict) -> tuple[dict, dict]:
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v6_cohort.v5_cohort._operator_note(plan["goal"]),
    )
    return program, v62.model_form_body(program, frame=frame)


def test_full_raw_v6_cohort_is_frozen_and_provider_free_oracles_admit() -> None:
    cases = _cases()
    assert len(cases) == 24
    assert tuple(case["case_code"] for case in cases) == cohort.EXPECTED_CASE_CODES
    assert "b-move-shift" in cohort.EXPECTED_CASE_CODES
    for case in cases:
        frame = cohort.frame_for_case(case)
        program, body = _reference_form(case, frame)
        turn_input = v62.build_turn_input(frame)
        review = v62.evaluate_output(
            frame,
            program,
            body,
            turn_code=1,
            turn_input=turn_input,
        )
        assert review["disposition"] == "admit", case["case_code"]
        assert review["context_frame_review"] == {
            "disposition": "admit",
            "task_sha256": turn_input["task_sha256"],
            "desk_context_sha256": turn_input["desk_context_sha256"],
            "reviewed_context_revision": frame["context_revision"],
            "source_labels": [
                "fixture_intercepted",
                "staff_selected",
                "staff_selected",
            ],
            "command_authority": False,
            "same_packet_seen_by_model_and_proofreader": True,
        }


def test_shift_request_receives_readable_selected_appointment_context() -> None:
    _, frame = _case("b-move-shift")
    context = v62.build_desk_context(frame)
    selected = context["selected_appointment"]
    assert selected == {
        "authority_label": "staff_selected",
        "source": "appointment",
        "binding_code": next(
            row["code"]
            for row in v62.build_model_task(frame)["binding_table"]
            if row["source_handle"] == "binding:selected_appointment"
        ),
        "appointment_ref": "synthetic-appointment-margaret",
        "patient_ref": "synthetic-patient-margaret",
        "patient_display": "Margaret Thompson",
        "practitioner_ref": "synthetic-practitioner-shera",
        "practitioner_display": "Dr Shera",
        "date": "2026-07-27",
        "start_time": "10:00",
        "duration_minutes": 15,
        "status": "booked",
    }
    serialized = json.dumps(context, sort_keys=True)
    assert "synthetic-appointment-liam" not in serialized
    assert context["excluded_context"][0:3] == [
        "unselected_appointments",
        "full_diary",
        "patient_history",
    ]


def test_dialogue_order_and_create_precedence_are_explicit() -> None:
    create_case, create_frame = _case("b-create-correct")
    context = v62.build_desk_context(create_frame)
    assert [
        turn["text"] for turn in context["recent_dialogue"]["turns"]
    ] == create_frame["utterances"]
    assert context["resolution_precedence"] == [
        "latest_staff_utterance",
        "explicit_correction",
        "earlier_staff_utterance",
        "selected_diary_context",
        "clarify_if_still_ambiguous",
    ]
    assert typed_plan.deterministic_plan(create_frame)["goal"] == "create"
    assert create_case["expected_goal"] == "create"
    assert "does not turn a request to" in v62.SYSTEM_INSTRUCTION
    assert "arrange or book a new appointment into a move" in v62.SYSTEM_INSTRUCTION


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (
            lambda value: value["task"]["desk_context"]["freshness"].__setitem__(
                "context_revision", 999
            ),
            "turn_task_frame_mismatch",
        ),
        (
            lambda value: value.__setitem__(
                "desk_context_sha256", "sha256:" + "0" * 64
            ),
            "desk_context_hash_mismatch",
        ),
    ],
)
def test_proofreader_rejects_context_or_hash_tampering(
    mutation,
    reason: str,
) -> None:
    case, frame = _case("b-move-shift")
    program, body = _reference_form(case, frame)
    turn_input = v62.build_turn_input(frame)
    mutation(turn_input)
    with pytest.raises(ValueError, match=reason):
        v62.evaluate_output(
            frame,
            program,
            body,
            turn_code=1,
            turn_input=turn_input,
        )


def test_turn_input_is_bounded_and_has_no_command_or_product_authority() -> None:
    _, frame = _case("b-move-shift")
    turn_input = v62.build_turn_input(frame)
    context = turn_input["task"]["desk_context"]
    assert context["authority"] == "context_only_no_command_authority"
    assert context["effect_ceiling"] == "proposal_only"
    assert context["data_class"] == "authored_synthetic"
    assert len(context["grounded_mentions"]) <= 2
    assert len(context["recent_dialogue"]["turns"]) <= 4
    serialized = json.dumps(turn_input, sort_keys=True)
    assert "clinical_data" in serialized
    assert "database_access" in serialized
    assert "command_authority" in serialized
    assert "synthetic-appointment-liam" not in serialized


def test_vertex_request_retains_frozen_provider_controls() -> None:
    _, frame = _case("b-move-shift")
    request = v62.build_vertex_request(v62.build_turn_input(frame))
    config = request["generationConfig"]
    assert config["responseMimeType"] == "application/json"
    assert config["responseSchema"] == v62.vertex_response_schema()
    assert config["temperature"] == v62.TEMPERATURE
    assert config["thinkingConfig"] == {
        "thinkingBudget": v62.THINKING_BUDGET,
        "includeThoughts": False,
    }
    serialized = json.dumps(request, sort_keys=True)
    assert "GEMINI_API_KEY" not in serialized
    assert "GOOGLE_API_KEY" not in serialized
    assert "generativelanguage.googleapis.com" not in serialized


def test_v62_attempt_ledger_and_live_packet_are_exactly_bound() -> None:
    _, frame = _case("b-move-shift")
    attempts, ledgers = cohort._case_ids("b-move-shift")
    broker.validate_attempt_ledger_pair(attempts[0], ledgers[0])
    with pytest.raises(broker.BrokerError, match="cell_request_binding_invalid"):
        broker.validate_attempt_ledger_pair(attempts[0], ledgers[1])
    packet = live._cell_request(
        frame,
        attempt_id=attempts[0],
        ledger_id=ledgers[0],
        contract_mode="receptionist-v62",
    )
    assert packet["protocol_version"] == v62.PROTOCOL_VERSION
    assert packet["policy_id"] == v62.POLICY_ID
    assert packet["model_input"] == v62.build_turn_input(frame)


def test_provider_blocked_evidence_covers_all_cases_without_provider_use() -> None:
    evidence = cohort.build_provider_blocked_evidence(write_frames=False)
    assert evidence["result"].endswith("provider_blocked_pass")
    assert evidence["provider_contacted"] is False
    assert evidence["provider_calls_performed"] == 0
    assert evidence["source_case_count"] == 24
    assert evidence["source_case_codes"] == list(cohort.EXPECTED_CASE_CODES)
    assert evidence["all_original_v6_cases_included"] is True
    assert (
        evidence["non_regression"][
            "v61_historical_wrong_forms_revalidated"
        ]
        == 14
    )
    assert evidence["non_regression"]["v6_prior_pass_case_count"] == 9
    assert evidence["call_budget"]["absolute_provider_call_ceiling"] == 48
    assert evidence["boundary"]["raw_authored_synthetic_requests_included"] is True
    assert evidence["boundary"]["raw_provider_response_retained"] is False


def test_broker_recomputes_v62_model_input_from_the_frozen_frame(
    tmp_path,
) -> None:
    _, frame = _case("b-move-shift")
    attempts, ledgers = cohort._case_ids("b-move-shift")
    packet = live._cell_request(
        frame,
        attempt_id=attempts[0],
        ledger_id=ledgers[0],
        contract_mode="receptionist-v62",
    )
    profile = {
        "provider": "google_cloud_vertex_ai",
        "model": broker.MODEL,
        "project": broker.PROJECT,
        "service_account": broker.SERVICE_ACCOUNT,
        "authentication": "keyless_impersonated_service_account_adc",
        "location": broker.LOCATION,
        "endpoint_hostname": broker.HOSTNAME,
        "automatic_fallback": False,
        "global_endpoint": False,
        "api_key_authentication": False,
        "provider_tools": False,
        "grounding": False,
        "retrieval": False,
        "explicit_cache": False,
        "cost_ceiling_usd": 1,
        "occupied_call_ceiling": 1,
    }
    paths = {}
    for name, value in {
        "request": packet,
        "frame": frame,
        "profile": profile,
    }.items():
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        paths[name] = path
    token = tmp_path / "token"
    token.write_text("x" * 48, encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text("{}", encoding="utf-8")
    args = type(
        "Args",
        (),
        {
            "token_file": token,
            "ledger": ledger,
            "audit": tmp_path / "audit.jsonl",
            "request": paths["request"],
            "frame": paths["frame"],
            "profile": paths["profile"],
        },
    )()
    state = broker.BrokerState(args)
    assert state.receptionist_v62_mode is True
    assert state.receptionist_v61_mode is False

    tampered = copy.deepcopy(packet)
    tampered["model_input"]["task"]["desk_context"][
        "selected_appointment"
    ]["patient_display"] = "Someone else"
    paths["request"].write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="turn_task_frame_mismatch"):
        broker.BrokerState(args)

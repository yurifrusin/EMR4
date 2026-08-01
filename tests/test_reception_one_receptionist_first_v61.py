from __future__ import annotations

from argparse import Namespace
import copy
import json
from pathlib import Path

import pytest

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5_multicase as v5_cohort
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v61 as receptionist
from scripts import reception_one_receptionist_first_v61_isolation as isolation
from scripts import reception_one_receptionist_first_v61_repair as repair
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]


def _case(
    case_code: str,
) -> tuple[dict, dict, dict]:
    _, cases = v6_cohort.load_source_manifest()
    case = next(item for item in cases if item["case_code"] == case_code)
    frame = v6_cohort.frame_for_case(case)
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v5_cohort._operator_note(plan["goal"]),
    )
    return case, frame, program


def _packet(body: dict) -> dict:
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                body,
                                sort_keys=True,
                                separators=(",", ":"),
                            )
                        }
                    ]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 300,
            "candidatesTokenCount": 80,
            "thoughtsTokenCount": 120,
            "totalTokenCount": 500,
        },
        "modelVersion": "gemini-2.5-flash",
    }


def _broker_state(
    tmp_path: Path,
    *,
    frame: dict,
    request: dict,
) -> broker.BrokerState:
    token_path = tmp_path / "token"
    ledger_path = tmp_path / "ledger.json"
    audit_path = tmp_path / "audit.jsonl"
    request_path = tmp_path / "request.json"
    frame_path = tmp_path / "frame.json"
    token_path.write_text("x" * 48, encoding="utf-8")
    request_path.write_text(json.dumps(request), encoding="utf-8")
    frame_path.write_text(json.dumps(frame), encoding="utf-8")
    ledger_path.write_text(
        json.dumps(
            {
                "schema_version": (
                    "reception.one.bureau.model_text_single_use_ledger.v1"
                ),
                "ledger_id": request["ledger_id"],
                "attempt_id": request["attempt_id"],
                "policy_id": request["policy_id"],
                "status": "open",
                "maximum_provider_calls": 1,
                "provider_calls_consumed": 0,
                "fallback_permitted": False,
            }
        ),
        encoding="utf-8",
    )
    return broker.BrokerState(
        Namespace(
            token_file=str(token_path),
            ledger=str(ledger_path),
            audit=str(audit_path),
            request=str(request_path),
            frame=str(frame_path),
            profile=str(lane.PROFILE_PATH),
        )
    )


def test_prompt_treats_json_as_packet_and_bindings_as_stamped_facts() -> None:
    prompt = receptionist.SYSTEM_INSTRUCTION
    assert "API response schema is the paper packet" in prompt
    assert "binding_table is a tray of broker-grounded" in prompt
    assert "selected_appointment" in prompt
    assert "Do not replace" in prompt
    assert "actions with clarification" in prompt
    assert receptionist.CONTRACT_MODE == "receptionist-v61"


def test_generation_contract_keeps_receptionist_and_form_channels() -> None:
    _, frame, _ = _case("b-move-resched")
    request = receptionist.build_vertex_request(
        receptionist.build_turn_input(frame)
    )
    assert request["generationConfig"]["responseMimeType"] == (
        "application/json"
    )
    assert request["generationConfig"]["thinkingConfig"] == {
        "thinkingBudget": 1024,
        "includeThoughts": False,
    }
    assert request["generationConfig"]["temperature"] == 0
    assert "receptionist_response" in (
        request["generationConfig"]["responseSchema"]["required"]
    )
    assert "typed_form" in (
        request["generationConfig"]["responseSchema"]["required"]
    )


def test_closed_v6_wrong_forms_are_rejected_and_oracles_admit() -> None:
    evidence = repair.build_provider_blocked_evidence(
        write_frames=False
    )
    assert len(evidence["case_oracles"]) == 15
    assertions = evidence["historical_v6_assertions"]
    assert len(
        [
            row
            for row in assertions
            if row["historical_form_available"]
        ]
    ) == 14
    assert all(
        row["v61_violation_codes"]
        == ["recognized_intent_goal_mismatch"]
        for row in assertions
        if row["historical_form_available"]
    )
    assert all(
        row["oracle_goal"]
        in {
            "create",
            "move",
            "resize",
            "cancel",
            "status_change",
            "clarification",
        }
        for row in evidence["case_oracles"]
    )


def test_goal_mismatch_ticket_names_goal_field_without_rewriting() -> None:
    _, frame, correct = _case("b-move-resched")
    wrong = copy.deepcopy(correct)
    wrong["goal_code"] = 6
    wrong["steps"] = [{"operator_code": 13, "source_refs": []}]
    body = receptionist.model_form_body(wrong, frame=frame)
    evaluation = receptionist.evaluate_output(
        frame,
        receptionist.assemble_program(body),
        body,
        turn_code=1,
    )
    ticket = receptionist.build_correction_ticket(
        body,
        receptionist.assemble_program(body),
        evaluation,
    )
    assert evaluation["disposition"] == "revision_required"
    assert ticket["violations"] == [
        {
            "violation_code": "recognized_intent_goal_mismatch",
            "field_code": "goal_code",
            "step_index": -1,
            "source_index": -1,
            "allowed_output_names": [],
        }
    ]
    assert ticket["previous_typed_form"]["goal_code"] == 6
    assert ticket["replacement_required"] is True


def test_noun_only_details_are_not_mistaken_for_create() -> None:
    _, frame, _ = _case("b-clarify-details")
    v6_evidence = lane.load_object(v6_cohort.OCCUPIED_PATH)
    v6_row = next(
        row
        for row in v6_evidence["cases"]
        if row["case_code"] == "b-clarify-details"
    )
    body = repair._closed_v6_body("b-clarify-details", v6_row)
    assert body is not None
    evaluation = receptionist.evaluate_output(
        frame,
        receptionist.assemble_program(body),
        body,
        turn_code=1,
    )
    assert evaluation["disposition"] == "revision_required"
    assert evaluation["recognized_intent_assertion"] == {
        "disposition": "revision_required",
        "recognized_goal": "clarification",
        "model_goal": "create",
        "unknown_novel_composition_closed": False,
    }


def test_unknown_novel_action_is_not_closed_by_one_way_assertion() -> None:
    _, source_frame, _ = _case("b-create-arrange")
    source_plan = typed_plan.deterministic_plan(source_frame)
    frame = copy.deepcopy(source_frame)
    frame["utterances"] = [
        (
            "Orchestrate Margaret Thompson with Dr Shera tomorrow "
            "at 2:30 pm for 15 minutes."
        )
    ]
    assert typed_plan.deterministic_plan(frame)["goal"] == "clarification"
    program = structured.program_from_plan(
        frame,
        source_plan,
        operator_note=v5_cohort._operator_note("create"),
    )
    body = receptionist.model_form_body(program, frame=frame)
    evaluation = receptionist.evaluate_output(
        frame,
        receptionist.assemble_program(body),
        body,
        turn_code=1,
    )
    assert evaluation["disposition"] == "admit"
    assert evaluation["recognized_intent_assertion"] == {
        "disposition": "admit",
        "recognized_goal": "clarification",
        "model_goal": "create",
        "unknown_novel_composition_closed": False,
    }


def test_broker_uses_v61_contract_and_records_form_separately(
    tmp_path: Path,
) -> None:
    _, frame, program = _case("b-move-resched")
    attempt = (
        "reception-one-receptionist-first-v61-repair-"
        "b-move-resched-turn-001"
    )
    ledger = (
        "reception-one-receptionist-first-v61-repair-"
        "b-move-resched-ledger-001"
    )
    request = live._cell_request(
        frame,
        attempt_id=attempt,
        ledger_id=ledger,
        contract_mode=receptionist.CONTRACT_MODE,
    )
    state = _broker_state(tmp_path, frame=frame, request=request)
    assert state.receptionist_v61_mode is True
    assert state.receptionist_v6_mode is False
    state.provider_call = lambda _request: (  # type: ignore[method-assign]
        _packet(receptionist.model_form_body(program, frame=frame)),
        {"http_status": 200, "latency_ms": 10},
    )
    result = state.execute(request)
    assert result["proofreader"]["disposition"] == "admit"
    assert result["receptionist_output"]["receptionist_response"]
    assert result["proofreader"]["admitted_operator_ids"]


def test_pre_schema_failure_retains_only_bounded_completion_metadata(
    tmp_path: Path,
) -> None:
    _, frame, _ = _case("b-move-shift")
    attempt = (
        "reception-one-receptionist-first-v61-repair-"
        "b-move-shift-diagnostic-turn-001"
    )
    ledger = (
        "reception-one-receptionist-first-v61-repair-"
        "b-move-shift-diagnostic-ledger-001"
    )
    request = live._cell_request(
        frame,
        attempt_id=attempt,
        ledger_id=ledger,
        contract_mode=receptionist.CONTRACT_MODE,
    )
    state = _broker_state(tmp_path, frame=frame, request=request)
    state.provider_call = lambda _request: (  # type: ignore[method-assign]
        {
            "candidates": [
                {
                    "content": {"parts": [{"text": "not-json"}]},
                    "finishReason": "MAX_TOKENS",
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 20,
                "thoughtsTokenCount": 30,
                "totalTokenCount": 60,
            },
            "modelVersion": "gemini-2.5-flash",
        },
        {"http_status": 200, "latency_ms": 10},
    )
    with pytest.raises(
        receptionist.ReceptionistFirstError,
        match="provider_text_not_json",
    ):
        state.execute(request)
    received = next(
        event
        for event in state.events
        if event["event_type"] == "provider_call_received"
    )
    assert received["fields"]["finish_reasons"] == ["MAX_TOKENS"]
    assert received["fields"]["part_counts"] == [1]
    assert received["fields"]["usage"]["thoughtsTokenCount"] == 30
    assert received["fields"]["provider_text_retained"] is False
    assert "not-json" not in json.dumps(received)


def test_provider_blocked_evidence_is_reproducible() -> None:
    recorded = lane.load_object(repair.PROVIDER_BLOCKED_PATH)
    regenerated = repair.build_provider_blocked_evidence(
        write_frames=False
    )
    assert recorded == regenerated
    assert recorded["provider_calls_performed"] == 0
    assert recorded["credential_reads_performed"] == 0
    assert (
        recorded["contract"]["natural_response_parsed_into_form"] is False
    )
    assert (
        recorded["contract"]["unknown_novel_composition_closed"] is False
    )


def test_v6_provider_blocked_evidence_remains_unchanged() -> None:
    recorded = lane.load_object(v6_cohort.PROVIDER_BLOCKED_PATH)
    assert recorded == v6_cohort.build_provider_blocked_evidence(
        write_frames=False
    )


def test_real_isolation_rejects_wrong_goal_then_admits_replacement() -> None:
    evidence = isolation.run_isolation()
    assert evidence == lane.load_object(isolation.ARTIFACT_PATH)
    assert evidence["first_disposition"] == "revision_required"
    assert evidence["first_violation_codes"] == [
        "recognized_intent_goal_mismatch"
    ]
    assert evidence["second_disposition"] == "admit"
    assert evidence["boundary"]["provider_calls_performed"] == 0
    assert evidence["boundary"]["credential_reads_performed"] == 0
    assert evidence["boundary"]["natural_response_parsed_into_form"] is False
    assert not any(evidence["residue"].values())


def test_v61_modules_have_no_product_or_command_actuator_imports() -> None:
    for path in (
        ROOT / "scripts/reception_one_receptionist_first_v61.py",
        ROOT / "scripts/reception_one_receptionist_first_v61_repair.py",
    ):
        source = path.read_text(encoding="utf-8")
        for forbidden in (
            "from app.",
            "import app.",
            "sqlalchemy",
            "psycopg",
            "confirm_appointment",
            "create_appointment",
        ):
            assert forbidden not in source

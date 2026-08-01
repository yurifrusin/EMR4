from __future__ import annotations

from argparse import Namespace
import copy
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v6 as receptionist
from scripts import reception_one_receptionist_first_v6_cohort as cohort
from scripts import reception_one_receptionist_first_v6_isolation as isolation
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]


def _case(
    case_code: str = "b-move-resched",
) -> tuple[dict, dict, dict]:
    _, cases = cohort.load_source_manifest()
    case = next(item for item in cases if item["case_code"] == case_code)
    frame = cohort.frame_for_case(case)
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=(
            f"Prepared a {plan['goal']} proposal for review; "
            "no booking was changed."
        ),
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


def test_prompt_is_receptionist_first_and_form_is_a_toolkit() -> None:
    prompt = receptionist.SYSTEM_INSTRUCTION
    assert "capable medical receptionist" in prompt
    assert "pre-printed typed bureau form in your toolkit" in prompt
    assert "API response schema is the paper packet" in prompt
    assert "Think privately within the configured budget" in prompt
    assert "form filling clerk" not in prompt.casefold()


def test_vertex_contract_has_bounded_thinking_and_json_form_transport() -> None:
    _, frame, _ = _case()
    request = receptionist.build_vertex_request(
        receptionist.build_turn_input(frame)
    )
    generation = request["generationConfig"]
    assert generation["temperature"] == 0
    assert generation["maxOutputTokens"] == 2048
    assert generation["responseMimeType"] == "application/json"
    assert generation["responseSchema"] == receptionist.vertex_response_schema()
    assert generation["thinkingConfig"] == {
        "thinkingBudget": 1024,
        "includeThoughts": False,
    }
    rendered = receptionist.canonical_json(request).casefold()
    for forbidden in (
        '"tools"',
        '"toolconfig"',
        '"cachedcontent"',
        '"grounding"',
        '"retrieval"',
        "generativelanguage.googleapis.com",
        "api_key",
    ):
        assert forbidden not in rendered


def test_dual_output_schema_is_exact_and_version_is_broker_owned() -> None:
    for path in (
        receptionist.MODEL_FORM_BODY_SCHEMA_PATH,
        receptionist.CORRECTION_TICKET_SCHEMA_PATH,
        receptionist.TURN_INPUT_SCHEMA_PATH,
    ):
        jsonschema.Draft202012Validator.check_schema(lane.load_object(path))
    schema = receptionist.vertex_response_schema()
    assert schema["required"] == [
        "receptionist_response",
        "decision_note",
        "evidence_utterance_indices",
        "typed_form",
    ]
    assert schema["properties"]["typed_form"]["required"] == [
        "operator_note",
        "goal_code",
        "steps",
    ]
    assert "version_code" not in receptionist.canonical_json(schema)


def test_packet_exposes_natural_and_typed_outputs_and_count_only_thinking() -> None:
    _, frame, program = _case()
    body = receptionist.model_form_body(program, frame=frame)
    assembled, parsed_body, usage = receptionist.parse_vertex_output(
        _packet(body)
    )
    assert parsed_body["receptionist_response"].startswith("I can prepare")
    assert parsed_body["typed_form"]["goal_code"] == program["goal_code"]
    assert assembled == program
    assert usage == {
        "promptTokenCount": 300,
        "candidatesTokenCount": 80,
        "thoughtsTokenCount": 120,
        "totalTokenCount": 500,
    }
    assert "thought" not in parsed_body
    assert "reasoning" not in parsed_body


def test_natural_language_is_never_parsed_into_the_typed_form() -> None:
    _, frame, program = _case()
    body = receptionist.model_form_body(program, frame=frame)
    changed = copy.deepcopy(body)
    changed["receptionist_response"] = (
        "I can prepare a cancellation proposal for review; "
        "no booking was changed."
    )
    assert receptionist.assemble_program(changed) == program
    evaluation = receptionist.evaluate_output(
        frame,
        program,
        changed,
        turn_code=1,
    )
    assert evaluation["disposition"] == "revision_required"
    assert evaluation["normalized_plan"] is None
    assert evaluation["receptionist_output"][
        "natural_response_parsed_into_form"
    ] is False
    assert {
        item["code"] for item in evaluation["violations"]
    } == {"receptionist_response_goal_mismatch"}


def test_proofreader_rejects_effect_claim_and_missing_latest_evidence() -> None:
    _, frame, program = _case()
    body = receptionist.model_form_body(program, frame=frame)
    unsafe = copy.deepcopy(body)
    unsafe["receptionist_response"] = (
        "I have moved the appointment and it is ready for review."
    )
    review = receptionist.review_receptionist_output(frame, unsafe, program)
    assert "receptionist_response_claims_completed_effect" in {
        item["code"] for item in review["violations"]
    }
    _, frame, program = _case("b-move-correct")
    stale = receptionist.model_form_body(program, frame=frame)
    stale["evidence_utterance_indices"] = [0]
    review = receptionist.review_receptionist_output(frame, stale, program)
    assert "evidence_latest_utterance_missing" in {
        item["code"] for item in review["violations"]
    }


def test_correction_ticket_names_constraints_not_rejected_prose() -> None:
    _, frame, program = _case()
    body = receptionist.model_form_body(program, frame=frame)
    body["receptionist_response"] = (
        "I have moved the appointment and it is ready for review."
    )
    evaluation = receptionist.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
    )
    ticket = receptionist.build_correction_ticket(body, program, evaluation)
    rendered = receptionist.canonical_json(ticket)
    assert evaluation["correction_eligible"] is True
    assert "I have moved" not in rendered
    assert "receptionist_response_claims_completed_effect" in rendered
    assert ticket["attempts_remaining"] == 1


def test_broker_admits_both_channels_and_records_thinking_count(
    tmp_path: Path,
) -> None:
    _, frame, program = _case()
    attempt = (
        "reception-one-receptionist-first-v6-eval-"
        "b-move-resched-turn-001"
    )
    ledger = (
        "reception-one-receptionist-first-v6-eval-"
        "b-move-resched-ledger-001"
    )
    request = live._cell_request(
        frame,
        attempt_id=attempt,
        ledger_id=ledger,
        contract_mode=receptionist.CONTRACT_MODE,
    )
    state = _broker_state(tmp_path, frame=frame, request=request)
    assert state.receptionist_v6_mode is True
    state.provider_call = lambda _request: (  # type: ignore[method-assign]
        _packet(receptionist.model_form_body(program, frame=frame)),
        {"http_status": 200, "latency_ms": 10},
    )
    result = state.execute(request)
    assert result["proofreader"]["disposition"] == "admit"
    assert result["receptionist_output"]["receptionist_response"]
    assert result["receptionist_output"]["decision_note"].startswith(
        "Intent move:"
    )
    completed = next(
        item
        for item in state.events
        if item["event_type"] == "provider_call_completed"
    )
    assert completed["fields"]["usage"]["thoughtsTokenCount"] == 120
    assert completed["fields"]["model_authored_field_manifest"] == [
        "receptionist_response",
        "decision_note",
        "evidence_utterance_indices",
        "typed_form",
    ]


def test_twenty_four_case_provider_blocked_evidence_is_reproducible() -> None:
    recorded = lane.load_object(cohort.PROVIDER_BLOCKED_PATH)
    regenerated = cohort.build_provider_blocked_evidence(write_frames=False)
    assert recorded == regenerated
    assert len(recorded["case_oracles"]) == 24
    assert recorded["provider_calls_performed"] == 0
    assert recorded["credential_reads_performed"] == 0
    assert recorded["contract"]["natural_response_parsed_into_form"] is False
    assert recorded["boundary"]["chain_of_thought_retained"] is False
    assert all(
        item["proofreader_disposition"] == "admit"
        for item in recorded["case_oracles"]
    )


def test_real_isolation_runs_two_credential_free_networkless_cells() -> None:
    evidence = isolation.run_isolation()
    assert evidence == lane.load_object(isolation.ARTIFACT_PATH)
    assert evidence["first_disposition"] == "revision_required"
    assert evidence["second_disposition"] == "admit"
    assert evidence["first_violation_codes"] == [
        "receptionist_response_claims_completed_effect"
    ]
    assert evidence["boundary"]["provider_calls_performed"] == 0
    assert evidence["boundary"]["credential_reads_performed"] == 0
    assert evidence["boundary"]["natural_response_parsed_into_form"] is False
    assert evidence["residue"] == {
        "containers_present": False,
        "images_present": False,
        "temporary_context_present": False,
    }
    assert all(
        all(checks.values())
        for checks in evidence["container_policy_checks"]
    )


def test_attempt_pairs_are_case_bound_and_turn_bound() -> None:
    first, second = cohort._case_ids("b-create-arrange")
    broker.validate_attempt_ledger_pair(first[0], second[0])
    broker.validate_attempt_ledger_pair(first[1], second[1])
    with pytest.raises(broker.BrokerError, match="cell_request_binding_invalid"):
        broker.validate_attempt_ledger_pair(first[0], second[1])


def test_closed_case_resume_is_exact_and_never_treats_partial_as_closed(
    tmp_path: Path,
) -> None:
    attempts, ledgers = cohort._case_ids("b-create-arrange")
    case_dir = (
        cohort.ARTIFACT_DIR / "cases" / "b-create-arrange"
    )
    dialogue = cohort._load_closed_dialogue(
        case_dir=case_dir,
        attempt_ids=attempts,
        ledger_ids=ledgers,
        expected_graph_revision=104,
        expected_compass_revision=91,
    )
    assert dialogue is not None
    assert dialogue["actual_provider_call_count"] == 1
    with pytest.raises(
        cohort.ReceptionistCohortError,
        match="closed_case_resume_binding_invalid",
    ):
        cohort._load_closed_dialogue(
            case_dir=case_dir,
            attempt_ids=attempts,
            ledger_ids=ledgers,
            expected_graph_revision=105,
            expected_compass_revision=91,
        )
    partial = tmp_path / "partial"
    partial.mkdir()
    (partial / "occupied-turn-001-ledger.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    with pytest.raises(
        cohort.ReceptionistCohortError,
        match="partial_case_requires_independent_closeout",
    ):
        cohort._load_closed_dialogue(
            case_dir=partial,
            attempt_ids=attempts,
            ledger_ids=ledgers,
            expected_graph_revision=104,
            expected_compass_revision=91,
        )


def test_pre_schema_provider_rejection_is_a_closed_no_release_case() -> None:
    _, cases = cohort.load_source_manifest()
    case = next(
        item for item in cases if item["case_code"] == "b-create-correct"
    )
    attempts, ledgers = cohort._case_ids(case["case_code"])
    case_dir = cohort.ARTIFACT_DIR / "cases" / case["case_code"]
    dialogue = cohort._load_closed_dialogue(
        case_dir=case_dir,
        attempt_ids=attempts,
        ledger_ids=ledgers,
        expected_graph_revision=104,
        expected_compass_revision=91,
    )
    assert dialogue is not None
    observation = cohort._case_observation(
        case=case,
        oracle=cohort._oracle_for_case(
            case,
            cohort.frame_for_case(case),
        ),
        case_dir=case_dir,
        dialogue=dialogue,
    )
    assert observation["expected_safe_outcome"] is False
    assert observation["release"] is None
    assert observation["primary_exact_body_accepted"] is False
    assert observation["primary_violation_codes"] == [
        "provider_text_not_json"
    ]
    assert observation["cleanup_passed"] is True


def test_v6_modules_have_no_product_or_command_actuator_imports() -> None:
    for path in (
        ROOT / "scripts/reception_one_receptionist_first_v6.py",
        ROOT / "scripts/reception_one_receptionist_first_v6_cohort.py",
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

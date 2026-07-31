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
from scripts import reception_one_preprinted_form_v5 as preprinted
from scripts import reception_one_preprinted_form_v5_isolation as isolation
from scripts import reception_one_preprinted_form_v5_live as preprinted_live
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]
SAFE_NOTE = "Prepared a move proposal for review; no booking was changed."
ATTEMPT_IDS = (
    "reception-one-preprinted-form-v5-turn-001",
    "reception-one-preprinted-form-v5-turn-002",
)
LEDGER_IDS = (
    "reception-one-preprinted-form-v5-ledger-001",
    "reception-one-preprinted-form-v5-ledger-002",
)


def _move() -> tuple[dict, dict]:
    document = typed_plan.load_json(typed_plan.CASES_PATH)
    case = next(item for item in document["cases"] if item["case_id"] == "known-move")
    frame = typed_plan.expand_case(document, case)
    plan = typed_plan.deterministic_plan(frame)
    return frame, structured.program_from_plan(
        frame,
        plan,
        operator_note=SAFE_NOTE,
    )


def _invalid_output_program() -> tuple[dict, dict]:
    frame, program = _move()
    program = copy.deepcopy(program)
    for step in program["steps"]:
        for source in step["source_refs"]:
            if source["kind"] != "prior_output":
                continue
            exposed = {
                output["name"]
                for output in structured.operator_table()[
                    program["steps"][source["prior_step_index"]]["operator_code"]
                ]["output_slots"]
            }
            source["prior_output_name"] = next(
                name for name in structured.OUTPUT_NAMES if name not in exposed
            )
            return frame, program
    raise AssertionError("fixture has no prior output")


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
            "promptTokenCount": 100,
            "candidatesTokenCount": 50,
            "totalTokenCount": 150,
        },
        "modelVersion": "gemini-2.5-flash",
    }


def _broker_state(
    tmp_path: Path,
    *,
    frame: dict,
    request: dict,
) -> broker.BrokerState:
    tmp_path.mkdir(parents=True, exist_ok=True)
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


def test_exact_schemas_and_provider_form_omit_broker_owned_field() -> None:
    frame, _ = _move()
    turn = preprinted.build_turn_input(frame)
    for path in (
        preprinted.MODEL_FORM_BODY_SCHEMA_PATH,
        preprinted.CORRECTION_TICKET_SCHEMA_PATH,
        preprinted.TURN_INPUT_SCHEMA_PATH,
    ):
        schema = lane.load_object(path)
        jsonschema.Draft202012Validator.check_schema(schema)
    assert turn["preprinted_form"] == {
        "version_code": 3,
        "model_authored_fields": ["operator_note", "goal_code", "steps"],
    }
    provider_schema = preprinted.vertex_response_schema()
    assert provider_schema["required"] == [
        "operator_note",
        "goal_code",
        "steps",
    ]
    assert "version_code" not in preprinted.canonical_json(provider_schema)
    for bound in (
        '"minimum"',
        '"maximum"',
        '"minLength"',
        '"maxLength"',
        '"minItems"',
        '"maxItems"',
    ):
        assert bound not in preprinted.canonical_json(provider_schema)


def test_baseline_prompt_has_no_examples_or_training_surface() -> None:
    frame, _ = _move()
    request = preprinted.build_vertex_request(preprinted.build_turn_input(frame))
    rendered = preprinted.canonical_json(request)
    for forbidden in (
        "few-shot",
        "few shot",
        "for example",
        "example answer",
        "demonstration",
        '"tools"',
        '"toolConfig"',
        '"cachedContent"',
        '"grounding"',
        '"retrieval"',
        "generativelanguage.googleapis.com",
        "api_key",
    ):
        assert forbidden not in rendered.lower()


def test_broker_injects_only_version_and_does_not_repair_body() -> None:
    _, program = _move()
    body = preprinted.model_form_body(program)
    assert set(body) == {"operator_note", "goal_code", "steps"}
    assert preprinted.assemble_program(body) == program
    with pytest.raises(preprinted.PreprintedFormError, match="schema_invalid"):
        preprinted.assemble_program({**body, "version_code": 3})
    invalid = copy.deepcopy(body)
    invalid["goal_code"] = 99
    with pytest.raises(preprinted.PreprintedFormError, match="schema_invalid"):
        preprinted.assemble_program(invalid)


def test_provider_packet_body_is_assembled_before_unchanged_proofreader() -> None:
    frame, expected = _move()
    program, usage = preprinted.parse_vertex_program(
        _packet(preprinted.model_form_body(expected))
    )
    assert program == expected
    assert usage == {
        "promptTokenCount": 100,
        "candidatesTokenCount": 50,
        "totalTokenCount": 150,
    }
    evaluation = preprinted.evaluate_program(frame, program, turn_code=1)
    assert evaluation["disposition"] == "admit"
    assert evaluation["normalized_plan"] is not None


def test_closed_ticket_omits_note_and_all_broker_owned_fields() -> None:
    frame, first = _invalid_output_program()
    evaluation = preprinted.evaluate_program(frame, first, turn_code=1)
    ticket = preprinted.build_correction_ticket(first, evaluation)
    assert evaluation["disposition"] == "revision_required"
    assert evaluation["correction_eligible"] is True
    assert set(ticket["previous_typed_form"]) == {"goal_code", "steps"}
    rendered = preprinted.canonical_json(ticket)
    assert first["operator_note"] not in rendered
    assert '"version_code":3' not in rendered
    assert "replacement_program" not in rendered
    turn_two = preprinted.build_turn_input(frame, correction_ticket=ticket)
    assert turn_two["turn_code"] == 2


def test_one_use_broker_assembles_and_admits_form_body(tmp_path: Path) -> None:
    frame, expected = _move()
    request = live._cell_request(
        frame,
        attempt_id=ATTEMPT_IDS[0],
        ledger_id=LEDGER_IDS[0],
        contract_mode=preprinted.CONTRACT_MODE,
    )
    state = _broker_state(tmp_path, frame=frame, request=request)
    assert state.preprinted_mode is True
    state.provider_call = lambda _request: (  # type: ignore[method-assign]
        _packet(preprinted.model_form_body(expected)),
        {"http_status": 200, "latency_ms": 10},
    )
    result = state.execute(request)
    assert result["status"] == "completed"
    assert result["proofreader"]["disposition"] == "admit"
    assert result["release"]["write_performed"] is False
    completed = next(
        event
        for event in state.events
        if event["event_type"] == "provider_call_completed"
    )
    assert completed["fields"]["model_authored_field_manifest"] == [
        "operator_note",
        "goal_code",
        "steps",
    ]
    assert completed["fields"]["broker_owned_field_manifest"] == [
        "version_code"
    ]
    assert completed["fields"]["broker_judgement_repair"] is False


def test_one_use_broker_issues_v5_ticket_and_admits_replacement(
    tmp_path: Path,
) -> None:
    frame, invalid = _invalid_output_program()
    first_request = live._cell_request(
        frame,
        attempt_id=ATTEMPT_IDS[0],
        ledger_id=LEDGER_IDS[0],
        contract_mode=preprinted.CONTRACT_MODE,
    )
    first_state = _broker_state(
        tmp_path / "first",
        frame=frame,
        request=first_request,
    )
    first_state.provider_call = lambda _request: (  # type: ignore[method-assign]
        _packet(preprinted.model_form_body(invalid)),
        {"http_status": 200, "latency_ms": 10},
    )
    with pytest.raises(broker.BrokerError, match="proofreader_rejected"):
        first_state.execute(first_request)
    ticket = next(
        event["fields"]["ticket"]
        for event in first_state.events
        if event["event_type"] == "correction_ticket_issued"
    )
    _, replacement = _move()
    second_request = live._cell_request(
        frame,
        attempt_id=ATTEMPT_IDS[1],
        ledger_id=LEDGER_IDS[1],
        contract_mode=preprinted.CONTRACT_MODE,
        correction_ticket=ticket,
    )
    second_state = _broker_state(
        tmp_path / "second",
        frame=frame,
        request=second_request,
    )
    second_state.provider_call = lambda _request: (  # type: ignore[method-assign]
        _packet(preprinted.model_form_body(replacement)),
        {"http_status": 200, "latency_ms": 10},
    )
    result = second_state.execute(second_request)
    assert result["status"] == "completed"
    assert result["proofreader"]["disposition"] == "admit"


def test_v5_attempts_are_exactly_paired_and_repair_can_only_be_call_two() -> None:
    broker.validate_attempt_ledger_pair(ATTEMPT_IDS[0], LEDGER_IDS[0])
    broker.validate_attempt_ledger_pair(ATTEMPT_IDS[1], LEDGER_IDS[1])
    broker.validate_attempt_ledger_pair(
        "reception-one-preprinted-form-v5-request-repair-002",
        "reception-one-preprinted-form-v5-request-repair-ledger-002",
    )
    with pytest.raises(broker.BrokerError, match="cell_request_binding_invalid"):
        broker.validate_attempt_ledger_pair(
            "reception-one-preprinted-form-v5-request-repair-001",
            "reception-one-preprinted-form-v5-request-repair-ledger-001",
        )


def _turn(
    index: int,
    *,
    ticket: dict | None = None,
    release: dict | None = None,
) -> dict:
    return {
        "attempt_id": ATTEMPT_IDS[index - 1],
        "ledger_id": LEDGER_IDS[index - 1],
        "provider_call_count": 1,
        "ledger": {
            "status": "consumed",
            "provider_calls_consumed": 1,
        },
        "exchange": {
            "correction_ticket": ticket,
            "correction_ticket_hash": (
                preprinted.canonical_hash(ticket) if ticket else None
            ),
            "release": release,
        },
    }


def test_parent_state_machine_stops_on_success_and_after_turn_two() -> None:
    frame, invalid = _invalid_output_program()
    ticket = preprinted.build_correction_ticket(
        invalid,
        preprinted.evaluate_program(frame, invalid, turn_code=1),
    )
    first = _turn(1, ticket=ticket)
    assert preprinted_live.decide_sequence([first])["next_turn_code"] == 2
    assert preprinted_live.decide_sequence(
        [first, _turn(2, release={"write_performed": False})]
    ) == {
        "status": "admitted_after_correction",
        "next_turn_code": None,
        "actual_provider_calls": 2,
        "terminal": True,
    }
    admitted_first = _turn(1, release={"write_performed": False})
    assert preprinted_live.decide_sequence([admitted_first])["terminal"] is True
    with pytest.raises(
        preprinted_live.PreprintedLiveError,
        match="call_after_admission_forbidden",
    ):
        preprinted_live.decide_sequence([admitted_first, _turn(2)])


def test_parent_state_machine_honours_one_call_authority() -> None:
    frame, invalid = _invalid_output_program()
    ticket = preprinted.build_correction_ticket(
        invalid,
        preprinted.evaluate_program(frame, invalid, turn_code=1),
    )
    decision = preprinted_live.decide_sequence(
        [_turn(1, ticket=ticket)],
        maximum_provider_calls=1,
    )
    assert decision == {
        "status": "terminal_call_ceiling_no_release",
        "next_turn_code": None,
        "actual_provider_calls": 1,
        "terminal": True,
        "correction_ticket_hash": preprinted.canonical_hash(ticket),
    }
    with pytest.raises(
        preprinted_live.PreprintedLiveError,
        match="absolute_call_ceiling_exceeded",
    ):
        preprinted_live.decide_sequence(
            [_turn(1, ticket=ticket), _turn(2)],
            maximum_provider_calls=1,
        )


@pytest.mark.parametrize("value", [0, 3, True])
def test_parent_state_machine_rejects_invalid_call_authority(value) -> None:
    with pytest.raises(
        preprinted_live.PreprintedLiveError,
        match="provider_call_ceiling_invalid",
    ):
        preprinted_live.decide_sequence(
            [],
            maximum_provider_calls=value,
        )


def test_parent_state_machine_rejects_third_call_and_second_ticket() -> None:
    frame, invalid = _invalid_output_program()
    ticket = preprinted.build_correction_ticket(
        invalid,
        preprinted.evaluate_program(frame, invalid, turn_code=1),
    )
    with pytest.raises(
        preprinted_live.PreprintedLiveError,
        match="second_correction_ticket_forbidden",
    ):
        preprinted_live.decide_sequence(
            [_turn(1, ticket=ticket), _turn(2, ticket=ticket)]
        )
    with pytest.raises(
        preprinted_live.PreprintedLiveError,
        match="absolute_call_ceiling_exceeded",
    ):
        preprinted_live.decide_sequence(
            [_turn(1, ticket=ticket), _turn(2), _turn(2)]
        )


def test_provider_blocked_evidence_is_deterministic_and_zero_call() -> None:
    evidence = preprinted.build_provider_blocked_evidence()
    assert evidence == lane.load_object(preprinted.PROVIDER_BLOCKED_EVIDENCE_PATH)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["credential_reads_performed"] == 0
    assert evidence["form_boundary"]["assembled_planprogram_exact"] is True
    assert evidence["form_boundary"]["broker_judgement_repair"] is False
    assert evidence["dialogue"]["second_disposition"] == "admit"


def test_real_isolation_runs_two_credential_free_networkless_cells() -> None:
    evidence = isolation.run_isolation()
    assert evidence == lane.load_object(
        preprinted.ARTIFACT_DIR / "real-isolation-evidence.json"
    )
    assert evidence["first_disposition"] == "revision_required"
    assert evidence["second_disposition"] == "admit"
    assert evidence["preprinted_fields"] == {"version_code": 3}
    assert evidence["boundary"]["provider_calls_performed"] == 0
    assert evidence["boundary"]["credential_reads_performed"] == 0
    assert evidence["boundary"]["broker_judgement_repair"] is False
    assert evidence["residue"] == {
        "containers_present": False,
        "images_present": False,
        "temporary_context_present": False,
    }
    assert len(evidence["container_policy_checks"]) == 2
    assert all(
        all(checks.values())
        for checks in evidence["container_policy_checks"]
    )


def test_occupied_baseline_admits_first_form_and_stops_without_retry() -> None:
    evidence = lane.load_object(
        preprinted.ARTIFACT_DIR / "occupied-dialogue-evidence.json"
    )
    turn = lane.load_object(
        preprinted.ARTIFACT_DIR / "occupied-turn-001-evidence.json"
    )
    ledger = lane.load_object(
        preprinted.ARTIFACT_DIR / "occupied-turn-001-ledger.json"
    )
    audit = lane.load_object(
        preprinted.ARTIFACT_DIR / "occupied-turn-001-external-audit.json"
    )
    assert evidence["result"] == "reception_one_preprinted_form_v5_occupied_pass"
    assert evidence["actual_provider_call_count"] == 1
    assert evidence["terminal_status"] == "admitted"
    assert evidence["release"]["write_performed"] is False
    assert evidence["release"]["requires_human_confirmation"] is True
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 1
    assert not (
        preprinted.ARTIFACT_DIR / "occupied-turn-002-ledger.json"
    ).exists()
    assert audit["provider_outcome"]["status"] == "completed"
    assert audit["provider_outcome"]["http_status"] == 200
    assert audit["proofreader"]["disposition"] == "admit"
    assert audit["proofreader"]["violations"] == []
    assert audit["proofreader"]["safe_repairs"] == []
    assert audit["preprinted_form"] == {
        "model_form_body_hash": (
            "sha256:a404a93cbeafb67c6320c8db738cc0038b293df3b7aa954db157364cf5b13f01"
        ),
        "model_authored_field_manifest": [
            "operator_note",
            "goal_code",
            "steps",
        ],
        "preprinted_field_manifest_hash": (
            "sha256:2a1f45caa1aeee47a1ab25e5ff886ac2e149e404d0c322e020db4338d6015d3e"
        ),
        "broker_owned_field_manifest": ["version_code"],
        "broker_judgement_repair": False,
        "raw_model_form_body_recorded": False,
    }
    assert all(
        value
        for key, value in turn["cleanup"].items()
        if key != "daemon_wide_prune_performed"
    )


def test_module_has_no_product_or_command_actuator_imports() -> None:
    source = (ROOT / "scripts/reception_one_preprinted_form_v5.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "from app.",
        "import app.",
        "sqlalchemy",
        "psycopg",
        "requests.",
        "urllib.request",
        "subprocess",
        "docker",
        "confirm_appointment",
        "create_appointment",
    ):
        assert forbidden not in source

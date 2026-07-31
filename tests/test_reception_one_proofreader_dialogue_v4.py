from __future__ import annotations

import copy
from argparse import Namespace
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_proofreader_dialogue_v4 as dialogue
from scripts import reception_one_proofreader_dialogue_v4_isolation as isolation
from scripts import reception_one_proofreader_dialogue_v4_live as dialogue_live
from scripts import reception_one_proofreader_dialogue_v4_repair_live as repair_live
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]
SAFE_NOTE = "Prepared a move proposal for review; no booking was changed."


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


def test_exact_schemas_and_unchanged_response_form() -> None:
    frame, _ = _move()
    turn = dialogue.build_turn_input(frame)
    ticket_schema = dialogue.load_object(dialogue.CORRECTION_TICKET_SCHEMA_PATH)
    turn_schema = dialogue.load_object(dialogue.TURN_INPUT_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(ticket_schema)
    jsonschema.Draft202012Validator.check_schema(turn_schema)
    jsonschema.validate(turn, turn_schema)
    assert turn["turn_code"] == 1
    assert turn["correction_ticket"] is None
    assert dialogue.vertex_response_schema() != structured.vertex_response_schema()
    rendered_provider_schema = dialogue.canonical_json(
        dialogue.vertex_response_schema()
    )
    for bound in (
        '"minimum"',
        '"maximum"',
        '"minLength"',
        '"maxLength"',
        '"minItems"',
        '"maxItems"',
    ):
        assert bound not in rendered_provider_schema
    assert '"enum"' in rendered_provider_schema
    assert '"maximum"' in dialogue.canonical_json(
        dialogue.load_object(structured.PLAN_PROGRAM_SCHEMA_PATH)
    )
    assert dialogue.build_vertex_request(turn)["generationConfig"][
        "responseSchema"
    ] == dialogue.vertex_response_schema()


def test_reject_ticket_complete_replacement_admit() -> None:
    frame, first = _invalid_output_program()
    evaluation = dialogue.evaluate_program(frame, first, turn_code=1)
    assert evaluation["disposition"] == "revision_required"
    assert evaluation["correction_eligible"] is True
    assert evaluation["violations"] == [
        {
            "path": evaluation["violations"][0]["path"],
            "code": "output_name_invalid",
        }
    ]
    ticket = dialogue.build_correction_ticket(first, evaluation)
    assert ticket["previous_program_sha256"] == dialogue.canonical_hash(first)
    assert ticket["replacement_required"] is True
    assert ticket["attempts_remaining"] == 1
    assert "operator_note" not in ticket["previous_typed_form"]
    turn = dialogue.build_turn_input(frame, correction_ticket=ticket)
    assert turn["turn_code"] == 2

    _, replacement = _move()
    second = dialogue.evaluate_program(frame, replacement, turn_code=2)
    assert second["disposition"] == "admit"
    assert second["terminal"] is True
    assert second["correction_eligible"] is False
    execution = typed_plan.execute_plan(
        frame,
        second["normalized_plan"],
        second["semantic_review"],
    )
    assert execution["final_output"]["write_performed"] is False


def test_ticket_contains_constraints_not_a_selected_replacement() -> None:
    frame, first = _invalid_output_program()
    evaluation = dialogue.evaluate_program(frame, first, turn_code=1)
    ticket = dialogue.build_correction_ticket(first, evaluation)
    rendered = dialogue.canonical_json(ticket)
    assert first["operator_note"] not in rendered
    assert "message" not in rendered
    assert "replacement_program" not in rendered
    assert "raw" not in rendered
    assert "reasoning" not in rendered
    assert set(ticket["violations"][0]) == {
        "violation_code",
        "field_code",
        "step_index",
        "source_index",
        "allowed_output_names",
    }


def test_rejected_note_is_not_returned_in_ticket() -> None:
    frame, program = _move()
    program["operator_note"] = "Margaret proposal."
    evaluation = dialogue.evaluate_program(frame, program, turn_code=1)
    assert evaluation["correction_eligible"] is True
    ticket = dialogue.build_correction_ticket(program, evaluation)
    assert program["operator_note"] not in dialogue.canonical_json(ticket)
    assert ticket["previous_typed_form"] == structured.audit_typed_program(program)
    assert {
        item["violation_code"] for item in ticket["violations"]
    } >= {"note_person_name", "note_missing_no_change_statement"}


def test_second_rejection_is_terminal_and_cannot_open_another_ticket() -> None:
    frame, program = _invalid_output_program()
    evaluation = dialogue.evaluate_program(frame, program, turn_code=2)
    assert evaluation["disposition"] == "edge_abort"
    assert evaluation["terminal"] is True
    assert evaluation["correction_turns_remaining"] == 0
    with pytest.raises(dialogue.DialogueError, match="correction_ticket_not_authorised"):
        dialogue.build_correction_ticket(program, evaluation)


def test_stale_or_open_authority_never_creates_correction_ticket() -> None:
    frame, _ = _move()
    stale = copy.deepcopy(frame)
    stale["expires_at"] = "2026-07-20T00:00:00Z"
    plan = typed_plan.deterministic_plan(stale)
    program = structured.program_from_plan(
        stale,
        plan,
        operator_note=SAFE_NOTE,
    )
    evaluation = dialogue.evaluate_program(stale, program, turn_code=1)
    assert evaluation["correction_eligible"] is False
    assert evaluation["disposition"] == "edge_abort"
    assert "stale_context" in {
        item["code"] for item in evaluation["violations"]
    }
    with pytest.raises(dialogue.DialogueError, match="correction_ticket_not_authorised"):
        dialogue.build_correction_ticket(program, evaluation)


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (
            lambda value: value.update({"task_sha256": "sha256:" + "0" * 64}),
            "turn_task_hash_mismatch",
        ),
        (
            lambda value: value.update({"turn_code": 2}),
            "turn_two_ticket_required",
        ),
    ],
)
def test_turn_input_cross_field_tampering_fails_closed(mutation, reason: str) -> None:
    frame, _ = _move()
    turn = dialogue.build_turn_input(frame)
    mutation(turn)
    with pytest.raises(dialogue.DialogueError, match=reason):
        dialogue.validate_turn_input(frame, turn)


def test_ticket_tampering_and_free_form_feedback_fail_schema() -> None:
    frame, first = _invalid_output_program()
    ticket = dialogue.build_correction_ticket(
        first,
        dialogue.evaluate_program(frame, first, turn_code=1),
    )
    tampered = copy.deepcopy(ticket)
    tampered["attempts_remaining"] = 2
    with pytest.raises(dialogue.DialogueError, match="schema_invalid"):
        dialogue.build_turn_input(frame, correction_ticket=tampered)
    free_form = copy.deepcopy(ticket)
    free_form["message"] = "Choose output X."
    with pytest.raises(dialogue.DialogueError, match="schema_invalid"):
        dialogue.build_turn_input(frame, correction_ticket=free_form)


def test_provider_request_has_no_tool_cache_or_fallback_surface() -> None:
    frame, _ = _move()
    request = dialogue.build_vertex_request(dialogue.build_turn_input(frame))
    rendered = dialogue.canonical_json(request)
    for forbidden in (
        '"tools"',
        '"toolConfig"',
        '"cachedContent"',
        '"grounding"',
        '"retrieval"',
        "generativelanguage.googleapis.com",
        "global",
        "api_key",
    ):
        assert forbidden not in rendered


def test_provider_blocked_evidence_is_deterministic_and_zero_call() -> None:
    evidence = dialogue.build_provider_blocked_evidence()
    assert evidence == dialogue.load_object(dialogue.PROVIDER_BLOCKED_EVIDENCE_PATH)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["credential_reads_performed"] == 0
    assert evidence["dialogue"]["first_disposition"] == "revision_required"
    assert evidence["dialogue"]["second_disposition"] == "admit"
    assert evidence["dialogue"]["repeated_second_failure_terminal"] is True
    assert evidence["dialogue"]["unsafe_boundary_ticket_denied"] is True
    assert evidence["dialogue"]["rejected_note_text_retained"] is False


def _packet(program: dict) -> dict:
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                program,
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


def test_one_use_broker_issues_ticket_then_admits_complete_turn_two(
    tmp_path: Path,
) -> None:
    frame, invalid = _invalid_output_program()
    first_request = live._cell_request(
        frame,
        attempt_id=dialogue_live.ATTEMPT_IDS[0],
        ledger_id=dialogue_live.LEDGER_IDS[0],
        contract_mode=dialogue.CONTRACT_MODE,
    )
    first_state = _broker_state(
        tmp_path / "first",
        frame=frame,
        request=first_request,
    )
    first_state.provider_call = lambda _request: (  # type: ignore[method-assign]
        _packet(invalid),
        {"http_status": 200, "latency_ms": 10},
    )
    with pytest.raises(broker.BrokerError, match="proofreader_rejected"):
        first_state.execute(first_request)
    ticket_event = next(
        event
        for event in first_state.events
        if event["event_type"] == "correction_ticket_issued"
    )
    ticket = ticket_event["fields"]["ticket"]
    assert next(
        event
        for event in first_state.events
        if event["event_type"] == "ledger_consumed"
    )
    assert not any(
        event["event_type"] == "release_committed"
        for event in first_state.events
    )

    _, corrected = _move()
    second_request = live._cell_request(
        frame,
        attempt_id=dialogue_live.ATTEMPT_IDS[1],
        ledger_id=dialogue_live.LEDGER_IDS[1],
        contract_mode=dialogue.CONTRACT_MODE,
        correction_ticket=ticket,
    )
    second_state = _broker_state(
        tmp_path / "second",
        frame=frame,
        request=second_request,
    )
    second_state.provider_call = lambda _request: (  # type: ignore[method-assign]
        _packet(corrected),
        {"http_status": 200, "latency_ms": 10},
    )
    result = second_state.execute(second_request)
    assert result["status"] == "completed"
    assert result["proofreader"]["disposition"] == "admit"
    assert result["release"]["write_performed"] is False
    assert not any(
        event["event_type"] == "correction_ticket_issued"
        for event in second_state.events
    )


def _turn(
    index: int,
    *,
    ticket: dict | None = None,
    release: dict | None = None,
) -> dict:
    return {
        "attempt_id": dialogue_live.ATTEMPT_IDS[index - 1],
        "ledger_id": dialogue_live.LEDGER_IDS[index - 1],
        "provider_call_count": 1,
        "ledger": {
            "status": "consumed",
            "provider_calls_consumed": 1,
        },
        "exchange": {
            "correction_ticket": ticket,
            "correction_ticket_hash": (
                dialogue.canonical_hash(ticket) if ticket else None
            ),
            "release": release,
        },
    }


def test_parent_state_machine_stops_on_success_and_after_turn_two() -> None:
    frame, invalid = _invalid_output_program()
    ticket = dialogue.build_correction_ticket(
        invalid,
        dialogue.evaluate_program(frame, invalid, turn_code=1),
    )
    first = _turn(1, ticket=ticket)
    assert dialogue_live.decide_sequence([first])["next_turn_code"] == 2
    assert dialogue_live.decide_sequence(
        [first, _turn(2, release={"write_performed": False})]
    ) == {
        "status": "admitted_after_correction",
        "next_turn_code": None,
        "actual_provider_calls": 2,
        "terminal": True,
    }
    admitted_first = _turn(1, release={"write_performed": False})
    assert dialogue_live.decide_sequence([admitted_first])["terminal"] is True
    with pytest.raises(
        dialogue_live.DialogueLiveError,
        match="call_after_admission_forbidden",
    ):
        dialogue_live.decide_sequence(
            [admitted_first, _turn(2)]
        )


def test_parent_state_machine_rejects_third_call_and_ticket_on_turn_two() -> None:
    frame, invalid = _invalid_output_program()
    ticket = dialogue.build_correction_ticket(
        invalid,
        dialogue.evaluate_program(frame, invalid, turn_code=1),
    )
    with pytest.raises(
        dialogue_live.DialogueLiveError,
        match="second_correction_ticket_forbidden",
    ):
        dialogue_live.decide_sequence(
            [_turn(1, ticket=ticket), _turn(2, ticket=ticket)]
        )
    with pytest.raises(
        dialogue_live.DialogueLiveError,
        match="absolute_call_ceiling_exceeded",
    ):
        dialogue_live.decide_sequence(
            [_turn(1, ticket=ticket), _turn(2), _turn(2)]
        )


def test_request_contract_repair_is_distinct_call_two_with_turn_one_task(
    tmp_path: Path,
) -> None:
    frame, _ = _move()
    attempt = "reception-one-proofreader-dialogue-v4-request-repair-002"
    ledger = (
        "reception-one-proofreader-dialogue-v4-request-repair-ledger-002"
    )
    request = live._cell_request(
        frame,
        attempt_id=attempt,
        ledger_id=ledger,
        contract_mode=dialogue.CONTRACT_MODE,
    )
    assert request["model_input"]["turn_code"] == 1
    assert request["model_input"]["correction_ticket"] is None
    state = _broker_state(
        tmp_path,
        frame=frame,
        request=request,
    )
    assert state.dialogue_mode is True
    with pytest.raises(broker.BrokerError, match="cell_request_binding_invalid"):
        broker.validate_attempt_ledger_pair(
            "reception-one-proofreader-dialogue-v4-request-repair-001",
            "reception-one-proofreader-dialogue-v4-request-repair-ledger-001",
        )


def test_request_contract_repair_accepts_only_the_closed_primary() -> None:
    binding = repair_live._validate_closed_primary(dialogue.ARTIFACT_DIR)
    assert binding == {
        "parent_evidence_hash": (
            "sha256:9546d01fc71759f95b6818e0d33dc67f34fec"
            "0478053949a0ae4058da97863d8"
        ),
        "primary_turn_audit_terminal_hash": (
            "sha256:fc021249aa4317fd5d16dba042f98d419cc0"
            "ab6060e40a702c5c4f35591d443b"
        ),
        "primary_parent_audit_terminal_hash": (
            "sha256:6786bfd4f608554022099ac483a8629b7e10"
            "f90d40eb8a3f78c914d21e4f84e8"
        ),
        "old_request_hash": (
            "sha256:88294e55a9ce4fd2243e2e145ca6423ab7a9"
            "c0cbe1e73dfbe0b92d90ca0f8e56"
        ),
        "old_schema_hash": repair_live.OLD_SCHEMA_HASH,
    }


def test_terminal_occupied_sequence_consumes_two_calls_without_release() -> None:
    primary_ledger = dialogue.load_object(
        dialogue.ARTIFACT_DIR / "occupied-turn-001-ledger.json"
    )
    repair_ledger = dialogue.load_object(
        dialogue.ARTIFACT_DIR / "occupied-request-repair-002-ledger.json"
    )
    repair_audit = dialogue.load_object(
        dialogue.ARTIFACT_DIR
        / "occupied-request-repair-002-external-audit.json"
    )
    consolidated = dialogue.load_object(
        dialogue.ARTIFACT_DIR
        / "occupied-request-repair-consolidated-evidence.json"
    )
    assert primary_ledger["status"] == "consumed"
    assert primary_ledger["provider_calls_consumed"] == 1
    assert repair_ledger["status"] == "consumed"
    assert repair_ledger["provider_calls_consumed"] == 1
    assert repair_audit["provider_outcome"] == {
        "bounded_error": {
            "field_paths": ["$.version_code"],
            "reason_code": "schema_invalid",
        },
        "http_status": 200,
        "latency_ms": 2109,
        "status": "response_rejected_before_candidate",
        "usage": {},
    }
    assert repair_audit["proofreader"]["disposition"] == "not_reached"
    assert consolidated["actual_provider_call_count"] == 2
    assert consolidated["absolute_provider_call_ceiling"] == 2
    assert consolidated["release"] is None
    assert consolidated["semantic_correction_turn_performed"] is False
    assert consolidated["third_call_performed"] is False
    assert consolidated["fallback_performed"] is False


def test_real_isolation_runs_two_credential_free_networkless_cells() -> None:
    evidence = isolation.run_isolation()
    assert evidence == dialogue.load_object(
        dialogue.ARTIFACT_DIR / "real-isolation-evidence.json"
    )
    assert evidence["first_disposition"] == "revision_required"
    assert evidence["second_disposition"] == "admit"
    assert evidence["boundary"]["provider_calls_performed"] == 0
    assert evidence["boundary"]["credential_reads_performed"] == 0
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


def test_module_has_no_product_or_command_actuator_imports() -> None:
    source = (ROOT / "scripts/reception_one_proofreader_dialogue_v4.py").read_text(
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

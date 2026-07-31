from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator

from scripts import reception_one_bureau_model_text_lane as legacy_lane
from scripts import reception_one_bureau_model_text_lane_audit as lane_audit
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_shared_typed_plan_language as shared
from scripts import reception_one_shared_typed_plan_isolation as isolation


ROOT = Path(__file__).resolve().parents[1]
MOVE_FRAME_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-extended-proposal-runtime"
    / "occupied-move-frame.json"
)
SAFE_NOTE = "Prepared a proposal for review; no booking was changed."


def _frame(case_id: str = "known-move") -> dict:
    document = typed_plan.load_json(typed_plan.CASES_PATH)
    case = next(item for item in document["cases"] if item["case_id"] == case_id)
    return typed_plan.expand_case(document, case)


def _program(case_id: str = "known-move") -> tuple[dict, dict]:
    frame = _frame(case_id)
    plan = typed_plan.deterministic_plan(frame)
    return frame, shared.program_from_plan(
        frame,
        plan,
        operator_note=SAFE_NOTE,
    )


def test_schemas_are_valid_and_provider_schema_is_the_same_coded_language():
    Draft202012Validator.check_schema(
        shared.load_object(shared.MODEL_INPUT_SCHEMA_PATH)
    )
    Draft202012Validator.check_schema(
        shared.load_object(shared.PLAN_PROGRAM_SCHEMA_PATH)
    )
    frame, program = _program()
    shared.validate_exact(program, shared.PLAN_PROGRAM_SCHEMA_PATH)
    model_input = shared.build_model_input(frame)
    shared.validate_exact(model_input, shared.MODEL_INPUT_SCHEMA_PATH)

    request = shared.build_vertex_request(model_input)
    assert set(request) == {
        "systemInstruction",
        "contents",
        "generationConfig",
    }
    config = request["generationConfig"]
    assert config["temperature"] == 0
    assert config["maxOutputTokens"] == 768
    assert config["responseMimeType"] == "application/json"
    assert config["thinkingConfig"] == {"thinkingBudget": 0}
    assert config["responseSchema"] == shared.vertex_response_schema()
    assert config["responseSchema"]["properties"]["goal_code"]["type"] == "INTEGER"
    assert (
        config["responseSchema"]["properties"]["steps"]["items"]["properties"][
            "source_codes"
        ]["items"]["type"]
        == "INTEGER"
    )
    rendered = shared.canonical_json(request)
    for forbidden in (
        '"tools"',
        '"toolConfig"',
        '"cachedContent"',
        '"grounding"',
        '"retrieval"',
        '"candidateCount"',
        "bernie-emr4-dev",
        "service_account",
        "access_token",
        "api_key",
    ):
        assert forbidden not in rendered


def test_model_input_tables_are_exact_contiguous_and_request_local():
    frame = json.loads(MOVE_FRAME_PATH.read_text(encoding="utf-8"))
    value = shared.build_model_input(frame)
    assert [item["code"] for item in value["goal_table"]] == list(range(7))
    assert [item["name"] for item in value["goal_table"]] == list(shared.GOALS)
    assert [item["code"] for item in value["operator_table"]] == list(range(14))
    assert [item["code"] for item in value["binding_table"]] == list(
        range(len(value["binding_table"]))
    )
    assert all(
        item["source_handle"].startswith("binding:")
        for item in value["binding_table"]
    )
    assert value["source_encoding"] == {
        "external_binding": "binding_table_code",
        "prior_step_output": (
            "1000_plus_step_index_times_16_plus_output_index"
        ),
        "prior_output_validity": (
            "zero_based_output_index_must_exist_on_selected_earlier_operator"
        ),
        "prior_output_examples": [
            {
                "source_step_index": 0,
                "output_index": 0,
                "source_code": 1000,
            },
            {
                "source_step_index": 1,
                "output_index": 0,
                "source_code": 1016,
            },
            {
                "source_step_index": 1,
                "output_index": 2,
                "source_code": 1018,
            },
        ],
        "optional_omission": -1,
    }


def test_proofreader_feedback_is_closed_typed_and_contains_no_prior_draft():
    frame, program = _program()
    invalid = copy.deepcopy(program)
    invalid["steps"][1]["source_codes"][0] = 1015
    review, normalized, candidate, _ = shared.proofread_program(frame, invalid)
    assert normalized is None
    assert candidate is None
    feedback = shared.build_proofreader_feedback(
        previous_program_hash=shared.canonical_hash(invalid),
        review=review,
    )
    assert feedback == {
        "version_code": 1,
        "previous_program_hash": shared.canonical_hash(invalid),
        "replacement_required": True,
        "violations": [
            {
                "violation_code": shared.PROOFREADER_VIOLATION_CODES.index(
                    "output_index_invalid"
                ),
                "path_code": 0,
            }
        ],
    }
    model_input = shared.build_model_input(
        frame,
        proofreader_feedback=feedback,
    )
    assert model_input["proofreader_feedback"] == feedback
    rendered = shared.canonical_json(model_input)
    assert program["operator_note"] not in rendered
    assert shared.canonical_json(invalid["steps"]) not in rendered
    request = live._cell_request(
        frame,
        attempt_id="reception-one-shared-typed-occupied-003",
        ledger_id="reception-one-shared-typed-ledger-003",
        contract_mode="shared-v2",
        proofreader_feedback=feedback,
    )
    assert len(broker.canonical_bytes(request)) <= 8192


def test_audit_typed_program_retains_only_closed_integer_form():
    _, program = _program()
    typed_form = shared.audit_typed_program(program)
    assert typed_form == {
        "version_code": program["version_code"],
        "goal_code": program["goal_code"],
        "steps": program["steps"],
    }
    assert "operator_note" not in typed_form
    assert SAFE_NOTE not in shared.canonical_json(typed_form)


def test_provider_free_fixture_is_exactly_the_trusted_move_program():
    frame = shared.load_object(isolation.FRAME)
    expected = shared.program_from_plan(
        frame,
        typed_plan.deterministic_plan(frame),
        operator_note=(
            "Prepared a move proposal for review; no booking was changed."
        ),
    )
    assert shared.load_object(isolation.FIXTURE) == expected


def test_shared_cell_request_uses_compact_serialization_within_relay_cap(
    tmp_path: Path,
):
    frames = [_frame(case_id) for case_id in (
        "known-create",
        "known-move",
        "known-resize",
        "known-cancel",
        "known-status",
        "novel-squeeze-in",
    )]
    for sequence, frame in enumerate(frames, start=1):
        request = live._cell_request(
            frame,
            attempt_id=(
                f"reception-one-shared-typed-occupied-{sequence:03d}"
            ),
            ledger_id=f"reception-one-shared-typed-ledger-{sequence:03d}",
            contract_mode="shared-v2",
        )
        assert len(broker.canonical_bytes(request)) <= 8192
    move_request = live._cell_request(
        frames[1],
        attempt_id="reception-one-shared-typed-occupied-001",
        ledger_id="reception-one-shared-typed-ledger-001",
        contract_mode="shared-v2",
    )
    pretty = (json.dumps(move_request, indent=2, sort_keys=True) + "\n").encode()
    assert len(pretty) > 8192
    context = tmp_path / "context"
    live._create_context(context, move_request)
    body = (context / "cell-request.json").read_bytes()
    assert body == broker.canonical_bytes(move_request)
    assert len(body) <= 8192


def test_provider_blocked_evidence_is_deterministic_and_zero_call():
    evidence = shared.load_object(shared.PROVIDER_BLOCKED_EVIDENCE_PATH)
    assert evidence == shared.build_provider_blocked_evidence()
    assert evidence["provider_contacted"] is False
    assert evidence["provider_calls_performed"] == 0
    assert evidence["credential_reads_performed"] == 0
    assert len(evidence["positive_cases"]) == 6
    assert all(
        item["proofreader_disposition"] == "admit"
        and item["operator_note_disposition"] == "admit"
        and item["write_performed"] is False
        for item in evidence["positive_cases"]
    )


@pytest.mark.parametrize(
    "case_id",
    [
        "known-create",
        "known-move",
        "known-resize",
        "known-cancel",
        "known-status",
        "novel-squeeze-in",
    ],
)
def test_shared_program_compiles_losslessly_and_existing_proofreader_admits(
    case_id: str,
):
    frame, program = _program(case_id)
    review, normalized, candidate, note_review = shared.proofread_program(
        frame, program
    )
    assert note_review == {
        "schema_version": "reception.one.operator_note_review.v1",
        "disposition": "admit",
        "reason_codes": [],
        "note_sha256": shared.review_operator_note(frame, SAFE_NOTE)[
            "note_sha256"
        ],
        "retained_utf8_bytes": len(SAFE_NOTE.encode("utf-8")),
        "retained_text": SAFE_NOTE,
    }
    assert review["disposition"] == "admit"
    assert review["safe_repairs"] == []
    assert candidate is not None
    assert normalized is not None
    assert candidate["goal"] == shared.GOALS[program["goal_code"]]
    execution = typed_plan.execute_plan(frame, normalized, review)
    assert execution["status"] == "executed"
    assert execution["final_output"]["write_performed"] is False
    assert execution["final_output"]["requires_human_confirmation"] is True


def test_squeeze_fixture_from_existing_untrusted_candidate_round_trips():
    frame = _frame("novel-squeeze-in")
    plan = legacy_lane.adapt_candidate(frame, legacy_lane.load_object(legacy_lane.FIXTURE_PATH))
    program = shared.program_from_plan(
        frame,
        plan,
        operator_note="Prepared a squeeze-in proposal for review; no booking was changed.",
    )
    review, _, candidate, _ = shared.proofread_program(frame, program)
    assert review["disposition"] == "admit"
    original = legacy_lane.candidate_from_plan(plan)
    assert candidate["goal"] == original["goal"]
    assert [step["operator"] for step in candidate["steps"]] == [
        step["operator"] for step in original["steps"]
    ]
    assert [
        [argument["name"] for argument in step["arguments"]]
        for step in candidate["steps"]
    ] == [
        [argument["name"] for argument in step["arguments"]]
        for step in original["steps"]
    ]
    assert [step["id"] for step in candidate["steps"]] == [
        "step-p01",
        "step-p02",
        "step-p03",
        "step-p04",
        "step-p05",
    ]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (
            lambda value: value["steps"][0].update(source_codes=[]),
            "operator_arity_invalid",
        ),
        (
            lambda value: value["steps"][0]["source_codes"].__setitem__(0, -1),
            "required_source_omitted",
        ),
        (
            lambda value: value["steps"][0]["source_codes"].__setitem__(0, 1000),
            "forward_or_self_reference",
        ),
        (
            lambda value: value["steps"][1]["source_codes"].__setitem__(0, 1015),
            "output_index_invalid",
        ),
        (
            lambda value: value["steps"][1]["source_codes"].__setitem__(0, 0),
            "source_type_mismatch",
        ),
        (
            lambda value: value["steps"][0]["source_codes"].__setitem__(0, 999),
            "external_source_code_invalid",
        ),
    ],
)
def test_program_code_arity_reference_and_type_defects_fail_before_semantic_release(
    mutate,
    expected: str,
):
    frame, program = _program()
    mutate(program)
    review, normalized, candidate, note_review = shared.proofread_program(
        frame, program
    )
    assert note_review["disposition"] == "admit"
    assert review["disposition"] == "edge_abort"
    assert review["violations"] == [{"path": "$.steps", "code": expected}]
    assert normalized is None
    assert candidate is None


@pytest.mark.parametrize(
    ("note", "expected"),
    [
        (
            "Prepared a proposal for Margaret; no booking was changed.",
            "note_person_name",
        ),
        (
            "Prepared a proposal using an access token; no booking was changed.",
            "note_secret_identity_or_hidden_reasoning",
        ),
        (
            "My reasoning: prepared a proposal; no booking was changed.",
            "note_secret_identity_or_hidden_reasoning",
        ),
        (
            "I moved it and prepared a review; no booking was changed.",
            "note_claims_command_effect",
        ),
        (
            "Completed the task; no booking was changed.",
            "note_missing_bounded_purpose",
        ),
        (
            "Prepared a proposal for review.",
            "note_missing_no_change_statement",
        ),
        (
            "Prepared a proposal for review;\nno booking was changed.",
            "note_multiline",
        ),
        (
            (
                "Prepared a proposal for review; no booking was changed. "
                + ("x" * 300)
            ),
            "note_oversized",
        ),
    ],
)
def test_operator_note_is_independently_bounded_and_rejected_text_is_discarded(
    note: str,
    expected: str,
):
    frame, program = _program()
    program["operator_note"] = note
    review, normalized, candidate, note_review = shared.proofread_program(
        frame, program
    )
    assert note_review["disposition"] == "reject"
    assert expected in note_review["reason_codes"]
    assert "retained_text" not in note_review
    assert note_review["retained_utf8_bytes"] == 0
    assert note_review["note_sha256"].startswith("sha256:")
    assert review["disposition"] == "edge_abort"
    assert normalized is None
    assert candidate is None


def test_admitted_operator_note_cannot_change_the_typed_plan():
    frame, first = _program()
    second = copy.deepcopy(first)
    second["operator_note"] = (
        "Prepared the typed proposal for human review; no booking was changed."
    )
    assert shared.review_operator_note(frame, first["operator_note"])[
        "disposition"
    ] == "admit"
    assert shared.review_operator_note(frame, second["operator_note"])[
        "disposition"
    ] == "admit"
    assert shared.compile_program(frame, first) == shared.compile_program(
        frame, second
    )


def test_provider_parser_accepts_only_exact_program_and_safe_usage():
    frame, program = _program()
    packet = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(program),
                            "thought": "must_not_be_retained",
                        }
                    ]
                },
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 40,
            "thoughtsTokenCount": 0,
            "totalTokenCount": 140,
            "sensitiveExtra": "discard",
        },
        "rawExtra": "discard",
    }
    parsed, usage = shared.parse_vertex_program(packet)
    assert parsed == program
    assert usage == {
        "promptTokenCount": 100,
        "candidatesTokenCount": 40,
        "thoughtsTokenCount": 0,
        "totalTokenCount": 140,
    }
    assert "must_not_be_retained" not in shared.canonical_json((parsed, usage))
    assert "sensitiveExtra" not in shared.canonical_json((parsed, usage))


def test_one_use_broker_audits_admitted_note_but_releases_only_typed_fields(
    tmp_path: Path,
    monkeypatch,
):
    frame, program = _program("known-move")
    feedback = shared.build_proofreader_feedback(
        previous_program_hash="sha256:" + ("a" * 64),
        review={
            "disposition": "edge_abort",
            "violations": [
                {
                    "path": "$.steps",
                    "code": "output_index_invalid",
                }
            ],
        },
    )
    request_packet = live._cell_request(
        frame,
        attempt_id="reception-one-shared-typed-occupied-001",
        ledger_id="reception-one-shared-typed-ledger-001",
        contract_mode="shared-v2",
        proofreader_feedback=feedback,
    )
    request_path = tmp_path / "request.json"
    frame_path = tmp_path / "frame.json"
    ledger_path = tmp_path / "ledger.json"
    audit_path = tmp_path / "audit.jsonl"
    token_path = tmp_path / "token"
    request_path.write_text(json.dumps(request_packet), encoding="utf-8")
    frame_path.write_text(json.dumps(frame), encoding="utf-8")
    token_path.write_text("x" * 48, encoding="utf-8")
    live._create_ledger(ledger_path, request_packet)
    state = broker.BrokerState(
        SimpleNamespace(
            token_file=str(token_path),
            ledger=str(ledger_path),
            audit=str(audit_path),
            request=str(request_path),
            frame=str(frame_path),
            profile=str(legacy_lane.PROFILE_PATH),
        )
    )
    assert state.shared_mode is True
    provider_packet = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": json.dumps(program)}],
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 60,
            "totalTokenCount": 160,
        },
        "modelVersion": "fixture-version",
    }
    monkeypatch.setattr(
        state,
        "provider_call",
        lambda _request: (
            provider_packet,
            {"http_status": 200, "latency_ms": 1},
        ),
    )
    state.append_event(
        "broker_ready",
        {"mode": "test", "policy_id": broker.SHARED_POLICY_ID},
    )
    result = state.execute(request_packet)
    assert result["status"] == "completed"
    assert result["proofreader"]["disposition"] == "admit"
    assert result["proofreader"]["operator_note_disposition"] == "admit"
    assert "operator_note" not in result
    assert result["release"]["proposal_family"] == "move"
    assert result["release"]["write_performed"] is False

    events = live._validate_audit(audit_path)
    assert [event["event_type"] for event in events] == [
        "broker_ready",
        "request_admitted",
        "ledger_consumed",
        "provider_request_constructed",
        "provider_call_started",
        "provider_call_received",
        "provider_call_completed",
        "operator_note_evaluated",
        "proofreader_completed",
        "release_committed",
    ]
    note = next(
        event["fields"]
        for event in events
        if event["event_type"] == "operator_note_evaluated"
    )
    assert note["operator_note"] == SAFE_NOTE
    assert note["audit_only"] is True
    assert note["parsed_into_plan"] is False
    assert note["product_delivered"] is False
    completed = next(
        event["fields"]
        for event in events
        if event["event_type"] == "provider_call_completed"
    )
    assert completed["typed_program"] == shared.audit_typed_program(program)
    assert "operator_note" not in completed["typed_program"]
    release_event = next(
        event["fields"]
        for event in events
        if event["event_type"] == "release_committed"
    )
    assert SAFE_NOTE not in shared.canonical_json(release_event)
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 1

    evidence_path = tmp_path / "evidence.json"
    preflight_path = tmp_path / "preflight.json"
    evidence_path.write_text(
        json.dumps(
            {
                "result": "reception_one_shared_typed_language_occupied_pass",
                "attempt_id": request_packet["attempt_id"],
                "ledger_id": request_packet["ledger_id"],
                "exact_binding": {
                    "provider": "google_vertex_ai",
                    "model_id": broker.MODEL,
                    "project": broker.PROJECT,
                    "service_account": broker.SERVICE_ACCOUNT,
                    "authentication": (
                        "keyless_impersonated_service_account_adc"
                    ),
                    "location": broker.LOCATION,
                    "endpoint_hostname": broker.HOSTNAME,
                },
                "exchange": {
                    "contract_mode": "shared-v2",
                    "model_input_hash": shared.canonical_hash(
                        request_packet["model_input"]
                    ),
                },
                "cleanup": {"all_owned_residue_absent": True},
                "explicit_exclusions": {
                    "raw_prompt_recorded": False,
                    "raw_provider_response_recorded": False,
                    "chain_of_thought_recorded": False,
                },
            }
        ),
        encoding="utf-8",
    )
    preflight_path.write_text(
        json.dumps(
            {
                "checks": {
                    "vertex_data_read_audit_enabled": True,
                    "vertex_data_write_audit_enabled": True,
                    "request_response_logging_disabled_or_absent": True,
                    "provider_in_memory_cache_disabled": True,
                    "no_user_managed_service_account_key": True,
                }
            }
        ),
        encoding="utf-8",
    )
    external = lane_audit.build_external_audit(
        evidence_path, audit_path, preflight_path
    )
    assert external["schema_version"] == (
        "reception.one.shared_typed_external_audit.v1"
    )
    assert external["operator_note"] == {
        "disposition": "admit",
        "reason_codes": [],
        "note_sha256": note["note_sha256"],
        "retained_utf8_bytes": len(SAFE_NOTE.encode("utf-8")),
        "operator_note": SAFE_NOTE,
        "audit_only": True,
        "parsed_into_plan": False,
        "product_delivered": False,
    }
    assert external["typed_program"] == {
        "program_hash": shared.canonical_hash(program),
        "closed_integer_form": shared.audit_typed_program(program),
        "operator_note_excluded": True,
        "raw_provider_response": False,
    }
    assert SAFE_NOTE not in shared.canonical_json(external["release"])


def test_legacy_free_form_wire_is_not_the_shared_language():
    wire = legacy_lane.candidate_to_wire(legacy_lane.load_object(legacy_lane.FIXTURE_PATH))
    with pytest.raises(shared.SharedLanguageError, match="schema_invalid"):
        shared.validate_exact(wire, shared.PLAN_PROGRAM_SCHEMA_PATH)


def test_module_has_no_provider_database_product_or_command_actuator():
    source = (ROOT / "scripts" / "reception_one_shared_typed_plan_language.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "google.auth",
        "requests.",
        "urlopen(",
        "subprocess.",
        "docker ",
        "sqlalchemy",
        "appointment_write_authority\": True",
    ):
        assert forbidden not in source


def test_shared_fixture_cell_has_no_provider_or_credential_actuator():
    source = (
        ROOT / "scripts" / "reception_one_shared_typed_plan_cell.py"
    ).read_text(encoding="utf-8")
    assert "http.client" not in source
    assert "urllib" not in source
    assert "google.auth" not in source
    assert "subprocess" not in source
    assert "GOOGLE_APPLICATION_CREDENTIALS" in source
    assert "credential_environment_present" in source


def test_continuity_and_compass_preserve_the_accepted_shared_language_node():
    graph = json.loads(
        (
            ROOT
            / "orchestration"
            / "continuity"
            / "emr4-continuity-graph.json"
        ).read_text(encoding="utf-8")
    )
    compass = json.loads(
        (
            ROOT / "orchestration" / "continuity" / "emr4-compass.json"
        ).read_text(encoding="utf-8")
    )
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "reception-one-shared-typed-language-active"
    )
    assert graph["graph_revision"] >= 83
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "reception-one-extended-proposal-runtime-active",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] >= 70
    assert compass["source_graph_revision"] == graph["graph_revision"]
    journey = {
        item["node_id"]: item for item in compass["journey"]
    }
    assert journey[node["id"]]["lineage_parent"] == (
        "reception-one-extended-proposal-runtime-active"
    )
    assert compass["current_position"]["node_id"] in journey

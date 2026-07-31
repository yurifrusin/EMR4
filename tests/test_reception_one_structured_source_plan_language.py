from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import pytest

from scripts import reception_one_bureau_model_text_lane as legacy_lane
from scripts import reception_one_bureau_model_text_lane_audit as lane_audit
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_structured_source_plan_isolation as isolation
from scripts import reception_one_structured_source_plan_language as structured


ROOT = Path(__file__).resolve().parents[1]
SAFE_NOTE = "Prepared a proposal for review; no booking was changed."


def _case(case_id: str = "known-move") -> tuple[dict, dict]:
    document = typed_plan.load_json(typed_plan.CASES_PATH)
    case = next(item for item in document["cases"] if item["case_id"] == case_id)
    frame = typed_plan.expand_case(document, case)
    return frame, typed_plan.deterministic_plan(frame)


def _program(case_id: str = "known-move") -> tuple[dict, dict]:
    frame, plan = _case(case_id)
    return frame, structured.program_from_plan(
        frame,
        plan,
        operator_note=SAFE_NOTE,
    )


def test_local_schemas_and_frozen_catalog_are_exact() -> None:
    model_schema = structured.load_object(structured.MODEL_INPUT_SCHEMA_PATH)
    program_schema = structured.load_object(structured.PLAN_PROGRAM_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(model_schema)
    jsonschema.Draft202012Validator.check_schema(program_schema)

    frame, program = _program()
    structured.validate_exact(program, structured.PLAN_PROGRAM_SCHEMA_PATH)
    model_input = structured.build_model_input(frame)
    structured.validate_exact(model_input, structured.MODEL_INPUT_SCHEMA_PATH)

    assert model_input["contract_version"] == structured.MODEL_INPUT_VERSION
    assert program["version_code"] == structured.PLAN_PROGRAM_VERSION_CODE
    assert {
        output["name"]
        for operator in model_input["operator_table"]
        for output in operator["output_slots"]
    } == set(structured.OUTPUT_NAMES)


def test_provider_schema_uses_explicit_named_references_and_supported_fields() -> None:
    schema = structured.vertex_response_schema()
    source_schema = schema["properties"]["steps"]["items"]["properties"][
        "source_refs"
    ]["items"]

    assert source_schema["propertyOrdering"] == [
        "kind",
        "binding_code",
        "prior_step_index",
        "prior_output_name",
    ]
    assert source_schema["properties"]["kind"]["enum"] == [
        "binding",
        "prior_output",
        "omit",
    ]
    assert source_schema["properties"]["prior_output_name"]["enum"] == [
        "none",
        *structured.OUTPUT_NAMES,
    ]
    assert "source_codes" not in structured.canonical_json(schema)
    assert "1187" not in structured.canonical_json(schema)

    allowed = {
        "type",
        "required",
        "propertyOrdering",
        "properties",
        "enum",
        "minimum",
        "maximum",
        "minLength",
        "maxLength",
        "minItems",
        "maxItems",
        "items",
    }

    def inspect(value: object) -> None:
        if isinstance(value, dict):
            assert set(value) <= allowed
            for key, child in value.items():
                if key == "properties":
                    assert isinstance(child, dict)
                    for property_schema in child.values():
                        inspect(property_schema)
                elif key == "items":
                    inspect(child)

    inspect(schema)


def test_vertex_request_is_toolless_regional_broker_payload_only() -> None:
    frame, _ = _program()
    request = structured.build_vertex_request(structured.build_model_input(frame))
    config = request["generationConfig"]

    assert config["responseMimeType"] == "application/json"
    assert config["responseSchema"] == structured.vertex_response_schema()
    assert config["temperature"] == 0
    assert config["maxOutputTokens"] == 2048
    assert config["thinkingConfig"] == {"thinkingBudget": 0}
    rendered = structured.canonical_json(request)
    for forbidden in (
        '"tools"',
        '"toolConfig"',
        '"cachedContent"',
        '"grounding"',
        '"retrieval"',
        "generativelanguage.googleapis.com",
        "aiplatform.googleapis.com",
        "api_key",
    ):
        assert forbidden not in rendered


def test_known_move_uses_visible_step_and_output_property_not_arithmetic() -> None:
    frame, program = _program()
    assert program["steps"][4]["source_refs"] == [
        {
            "kind": "prior_output",
            "binding_code": -1,
            "prior_step_index": 1,
            "prior_output_name": "appointment",
        },
        {
            "kind": "prior_output",
            "binding_code": -1,
            "prior_step_index": 3,
            "prior_output_name": "candidates",
        },
    ]
    rendered = structured.canonical_json(program)
    assert "1040" not in rendered
    assert "1048" not in rendered

    review, normalized, candidate, note_review = structured.proofread_program(
        frame, program
    )
    assert review["disposition"] == "admit"
    assert note_review["disposition"] == "admit"
    assert normalized is not None
    assert candidate is not None
    assert candidate["steps"][-1]["arguments"][-1] == {
        "name": "candidates",
        "source": "step:step-p04:candidates",
    }


def test_every_existing_positive_goal_compiles_losslessly_and_executes_proposal_only() -> None:
    evidence = structured.build_provider_blocked_evidence()
    assert evidence == structured.load_object(
        structured.PROVIDER_BLOCKED_EVIDENCE_PATH
    )
    assert len(evidence["positive_cases"]) == 6
    assert {
        item["goal"] for item in evidence["positive_cases"]
    } == {
        "create",
        "move",
        "resize",
        "cancel",
        "status_change",
        "squeeze_in_assessment",
    }
    assert all(
        item["proofreader_disposition"] == "admit"
        and item["write_performed"] is False
        for item in evidence["positive_cases"]
    )
    assert evidence["provider_calls_performed"] == 0
    assert evidence["credential_reads_performed"] == 0
    assert evidence["contract"]["arithmetic_prior_output_codes"] is False


@pytest.mark.parametrize(
    ("mutate", "reason"),
    [
        (
            lambda value: value["steps"][0]["source_refs"][0].update(
                prior_step_index=0
            ),
            "binding_sentinel_invalid",
        ),
        (
            lambda value: value["steps"][1]["source_refs"][0].update(
                binding_code=0
            ),
            "prior_output_sentinel_invalid",
        ),
        (
            lambda value: value["steps"][0]["source_refs"].__setitem__(
                0,
                {
                    "kind": "omit",
                    "binding_code": -1,
                    "prior_step_index": -1,
                    "prior_output_name": "none",
                },
            ),
            "required_source_omitted",
        ),
        (
            lambda value: value["steps"][1]["source_refs"][0].update(
                prior_step_index=1
            ),
            "forward_or_self_reference",
        ),
        (
            lambda value: value["steps"][1]["source_refs"][0].update(
                prior_output_name="date"
            ),
            "output_name_invalid",
        ),
        (
            lambda value: value["steps"][1]["source_refs"].__setitem__(
                0,
                {
                    "kind": "binding",
                    "binding_code": 0,
                    "prior_step_index": -1,
                    "prior_output_name": "none",
                },
            ),
            "source_type_mismatch",
        ),
        (
            lambda value: value["steps"][0]["source_refs"][0].update(
                binding_code=9
            ),
            "external_binding_invalid",
        ),
    ],
)
def test_cross_field_reference_defects_fail_before_semantic_release(
    mutate,
    reason: str,
) -> None:
    frame, original = _program()
    program = copy.deepcopy(original)
    mutate(program)
    review, normalized, candidate, note_review = structured.proofread_program(
        frame, program
    )

    assert note_review["disposition"] == "admit"
    assert review["disposition"] == "edge_abort"
    assert review["revision_allowed"] is False
    assert review["safe_repairs"] == []
    assert review["violations"] == [{"path": "$.steps", "code": reason}]
    assert normalized is None
    assert candidate is None


def test_inconsistent_omit_sentinel_fails_closed() -> None:
    frame, program = _program()
    # search_available_slots input 2 is the optional earliest_time slot.
    program["steps"][3]["source_refs"][2] = {
        "kind": "omit",
        "binding_code": 0,
        "prior_step_index": -1,
        "prior_output_name": "none",
    }
    review, normalized, candidate, _ = structured.proofread_program(
        frame, program
    )
    assert review["violations"] == [
        {"path": "$.steps", "code": "omit_sentinel_invalid"}
    ]
    assert normalized is None
    assert candidate is None


def test_old_arithmetic_form_is_not_valid_v3() -> None:
    old = {
        "version_code": 2,
        "operator_note": SAFE_NOTE,
        "goal_code": 1,
        "steps": [{"operator_code": 0, "source_codes": [4]}],
    }
    with pytest.raises(structured.StructuredSourceError, match="schema_invalid"):
        structured.validate_exact(old, structured.PLAN_PROGRAM_SCHEMA_PATH)


def test_operator_note_remains_separate_and_cannot_change_compilation() -> None:
    frame, first = _program()
    second = copy.deepcopy(first)
    second["operator_note"] = (
        "Prepared another proposal for review; no booking was changed."
    )

    assert structured.review_operator_note(
        frame, first["operator_note"]
    )["disposition"] == "admit"
    assert structured.review_operator_note(
        frame, second["operator_note"]
    )["disposition"] == "admit"
    assert structured.compile_program(
        frame, first
    ) == structured.compile_program(frame, second)
    assert SAFE_NOTE not in structured.canonical_json(
        structured.audit_typed_program(first)
    )


def test_provider_parser_retains_only_schema_admitted_program_and_usage() -> None:
    _, program = _program()
    packet = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(program),
                            "must_not_be_retained": "discard",
                        }
                    ]
                },
                "sensitiveExtra": "discard",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 120,
            "candidatesTokenCount": 80,
            "thoughtsTokenCount": 0,
            "totalTokenCount": 200,
            "unknown": "discard",
        },
        "raw": "discard",
    }
    parsed, usage = structured.parse_vertex_program(packet)
    assert parsed == program
    assert usage == {
        "promptTokenCount": 120,
        "candidatesTokenCount": 80,
        "thoughtsTokenCount": 0,
        "totalTokenCount": 200,
    }
    assert "must_not_be_retained" not in structured.canonical_json(
        (parsed, usage)
    )


def test_structured_cell_request_is_exact_and_within_relay_cap() -> None:
    frame, _ = _program()
    request = live._cell_request(
        frame,
        attempt_id="reception-one-structured-source-occupied-001",
        ledger_id="reception-one-structured-source-ledger-001",
        contract_mode="structured-v3",
    )
    assert request["protocol_version"] == structured.PROTOCOL_VERSION
    assert request["policy_id"] == broker.STRUCTURED_POLICY_ID
    assert request["model_input"] == structured.build_model_input(frame)
    assert len(broker.canonical_bytes(request)) <= 32768
    with pytest.raises(
        live.LiveError,
        match="proofreader_feedback_not_authorised",
    ):
        live._cell_request(
            frame,
            attempt_id="reception-one-structured-source-occupied-001",
            ledger_id="reception-one-structured-source-ledger-001",
            contract_mode="structured-v3",
            proofreader_feedback={"revision": True},
        )


def test_provider_free_isolation_fixture_is_exactly_the_known_move() -> None:
    frame = structured.load_object(isolation.FRAME)
    expected = structured.program_from_plan(
        frame,
        typed_plan.deterministic_plan(frame),
        operator_note=(
            "Prepared a move proposal for review; no booking was changed."
        ),
    )
    assert structured.load_object(isolation.FIXTURE) == expected


def test_one_use_broker_and_external_audit_preserve_explicit_form(
    tmp_path: Path,
    monkeypatch,
) -> None:
    frame, program = _program()
    request = live._cell_request(
        frame,
        attempt_id="reception-one-structured-source-occupied-001",
        ledger_id="reception-one-structured-source-ledger-001",
        contract_mode="structured-v3",
    )
    request_path = tmp_path / "request.json"
    frame_path = tmp_path / "frame.json"
    ledger_path = tmp_path / "occupied-001-ledger.json"
    audit_path = tmp_path / "occupied-001-audit.jsonl"
    evidence_path = tmp_path / "occupied-001-evidence.json"
    preflight_path = tmp_path / "occupied-preflight-evidence.json"
    token_path = tmp_path / "token"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    frame_path.write_text(json.dumps(frame), encoding="utf-8")
    token_path.write_text("x" * 48, encoding="utf-8")
    live._create_ledger(ledger_path, request)
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
    assert state.structured_mode is True
    assert state.shared_mode is False
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
            "promptTokenCount": 120,
            "candidatesTokenCount": 80,
            "totalTokenCount": 200,
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
        {"mode": "test", "policy_id": broker.STRUCTURED_POLICY_ID},
    )
    result = state.execute(request)
    assert result["status"] == "completed"
    assert result["proofreader"]["disposition"] == "admit"
    assert result["release"]["proposal_family"] == "move"
    assert result["release"]["write_performed"] is False
    assert "operator_note" not in result

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
    completed = next(
        event["fields"]
        for event in events
        if event["event_type"] == "provider_call_completed"
    )
    assert completed["typed_program"] == structured.audit_typed_program(
        program
    )
    assert "operator_note" not in completed["typed_program"]

    evidence_path.write_text(
        json.dumps(
            {
                "result": (
                    "reception_one_structured_source_language_occupied_pass"
                ),
                "attempt_id": request["attempt_id"],
                "ledger_id": request["ledger_id"],
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
                    "contract_mode": "structured-v3",
                    "model_input_hash": structured.canonical_hash(
                        request["model_input"]
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
        evidence_path,
        audit_path,
        preflight_path,
    )
    assert external["schema_version"] == (
        "reception.one.structured_source_external_audit.v1"
    )
    assert external["typed_program"] == {
        "program_hash": structured.canonical_hash(program),
        "explicit_source_form": structured.audit_typed_program(program),
        "operator_note_excluded": True,
        "raw_provider_response": False,
    }
    assert external["operator_note"]["operator_note"] == SAFE_NOTE
    assert external["operator_note"]["parsed_into_plan"] is False
    assert SAFE_NOTE not in structured.canonical_json(external["release"])
    assert external["retry"] == {
        "count": 0,
        "authorised": False,
        "performed": False,
        "lifecycle_sequence": 1,
        "actual_provider_call_ordinal": 1,
        "reason": "sequence_stopped_after_first_admitted_result",
    }


def test_module_has_no_provider_database_product_or_command_actuator() -> None:
    source = (
        ROOT / "scripts" / "reception_one_structured_source_plan_language.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "google.auth",
        "requests.",
        "urllib",
        "http.client",
        "sqlalchemy",
        "psycopg",
        "subprocess",
        "docker ",
        "create_appointment(",
        "confirm_appointment(",
    ):
        assert forbidden not in source

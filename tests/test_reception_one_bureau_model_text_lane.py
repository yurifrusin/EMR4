from __future__ import annotations

import copy
import json
from types import SimpleNamespace

import pytest

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_audit as lane_audit
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan


def _squeeze_frame() -> dict:
    document = typed_plan.load_json(typed_plan.CASES_PATH)
    case = next(
        item for item in document["cases"] if item["case_id"] == "novel-squeeze-in"
    )
    return typed_plan.expand_case(document, case)


def _fixture() -> dict:
    return lane.load_object(lane.FIXTURE_PATH)


def test_model_input_is_minimal_closed_and_has_no_scope_or_credentials():
    model_input = lane.build_model_input(_squeeze_frame())
    lane.validate_exact(model_input, lane.INPUT_SCHEMA_PATH)
    assert set(model_input) == {
        "contract_version",
        "data_class",
        "utterances",
        "effect_ceiling",
        "available_bindings",
        "operator_catalog",
    }
    rendered = lane.canonical_json(model_input).casefold()
    for forbidden in (
        "bernie-emr4-dev",
        "service_account",
        "access_token",
        "oauth",
        "api_key",
        "context_revision",
        "appointment_write_authority",
    ):
        assert forbidden not in rendered
    assert len(model_input["operator_catalog"]) == 14
    assert model_input["effect_ceiling"] == "proposal_only"


def test_vertex_request_is_regional_profile_compatible_and_tool_free():
    request = lane.build_vertex_request(lane.build_model_input(_squeeze_frame()))
    assert set(request) == {
        "systemInstruction",
        "contents",
        "generationConfig",
    }
    config = request["generationConfig"]
    assert config["temperature"] == 0
    assert config["maxOutputTokens"] == 1024
    assert config["responseMimeType"] == "application/json"
    assert config["thinkingConfig"] == {"thinkingBudget": 0}
    assert "candidateCount" not in request
    rendered = lane.canonical_json(request)
    for forbidden in (
        '"tools"',
        '"toolConfig"',
        '"cachedContent"',
        '"grounding"',
        '"retrieval"',
    ):
        assert forbidden not in rendered
    response_schema = config["responseSchema"]
    assert response_schema == {
        "type": "OBJECT",
        "required": ["goal", "plan_lines"],
        "properties": {
            "goal": {"type": "STRING"},
            "plan_lines": {
                "type": "ARRAY",
                "minItems": 1,
                "maxItems": 12,
                "items": {"type": "STRING", "maxLength": 512},
            },
        },
    }
    assert "enum" not in lane.canonical_json(response_schema)
    assert lane.canonical_json(response_schema).count('"type":"ARRAY"') == 1
    assert (
        "practitioner=step:step-practitioner:practitioner"
        in lane.SYSTEM_INSTRUCTION
    )
    assert "Never use step-id:output, dot notation" in lane.SYSTEM_INSTRUCTION
    assert "move, reschedule or rebook maps to move" in lane.SYSTEM_INSTRUCTION
    assert "Never output reschedule, rebook, move_appointment" in (
        lane.SYSTEM_INSTRUCTION
    )


def test_provider_wire_round_trip_is_exact_and_locally_typed():
    candidate = _fixture()
    wire = lane.candidate_to_wire(candidate)
    lane.validate_exact(wire, lane.WIRE_SCHEMA_PATH)
    assert lane.wire_to_candidate(wire) == candidate


def test_trusted_adapter_attaches_immutable_scope_and_proofreader_admits_fixture():
    frame = _squeeze_frame()
    candidate = _fixture()
    review, normalized, _ = lane.proofread_candidate(frame, candidate)
    assert review["disposition"] == "admit"
    assert normalized["request_id"] == frame["request_id"]
    assert normalized["practice_ref"] == frame["practice_ref"]
    assert normalized["correlation_id"] == frame["correlation_id"]
    assert normalized["context_revision"] == frame["context_revision"]
    assert normalized["effect_ceiling"] == "proposal_only"
    execution = typed_plan.execute_plan(frame, normalized, review)
    assert execution["status"] == "executed"
    assert execution["final_output"]["proposal_family"] == "squeeze_in_assessment"
    assert execution["final_output"]["requires_human_confirmation"] is True
    assert execution["final_output"]["write_performed"] is False


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda value: value["steps"][-1].__setitem__(
                "operator", "confirm_appointment"
            ),
            "reject",
        ),
        (
            lambda value: value["steps"][-1]["arguments"][-1].__setitem__(
                "source", "literal:15"
            ),
            "schema_invalid",
        ),
        (
            lambda value: value["steps"][0]["arguments"][0].__setitem__(
                "source", "step:step-later:patient"
            ),
            "reject",
        ),
        (
            lambda value: value.__setitem__("project", "different-project"),
            "schema_invalid",
        ),
    ],
)
def test_untrusted_candidate_failures_do_not_execute(mutation, expected):
    candidate = copy.deepcopy(_fixture())
    mutation(candidate)
    try:
        review, normalized, _ = lane.proofread_candidate(
            _squeeze_frame(), candidate
        )
    except lane.ModelLaneError as error:
        assert str(error).startswith(expected)
        return
    assert review["disposition"] == expected
    with pytest.raises(ValueError):
        typed_plan.execute_plan(_squeeze_frame(), normalized, review)


def test_revision_feedback_is_path_code_only_and_bounded():
    frame = _squeeze_frame()
    candidate = copy.deepcopy(_fixture())
    candidate["steps"][-1]["arguments"] = candidate["steps"][-1]["arguments"][:-1]
    review, _, _ = lane.proofread_candidate(frame, candidate)
    feedback = lane.safe_revision_feedback(review)
    assert review["disposition"] == "revision_required"
    assert set(feedback) == {
        "contract_version",
        "attempt",
        "revision_allowed",
        "violations",
    }
    assert len(feedback["violations"]) <= 20
    assert all(set(item) == {"path", "code"} for item in feedback["violations"])
    assert "draft" not in lane.canonical_json(feedback).casefold()
    repaired, _, _ = lane.proofread_candidate(frame, _fixture(), attempt=2)
    assert repaired["disposition"] == "admit"
    assert repaired["attempt"] == 2


def test_provider_response_parser_retains_candidate_and_safe_usage_only():
    packet = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "text": json.dumps(
                                lane.candidate_to_wire(_fixture())
                            )
                        }
                    ],
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 80,
            "totalTokenCount": 180,
            "other": "discard",
        },
        "modelVersion": "discarded-by-parser",
    }
    candidate, usage = lane.parse_vertex_candidate(packet)
    assert candidate == _fixture()
    assert usage == {
        "promptTokenCount": 100,
        "candidatesTokenCount": 80,
        "totalTokenCount": 180,
    }


def test_provider_wire_applies_only_authorised_mechanical_safe_repairs():
    wire = lane.candidate_to_wire(_fixture())
    packet = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "goal": " SQUEEZE_IN_ASSESSMENT ",
                                    "plan_lines": [
                                        line.replace("|", " | ").replace(",", ", ")
                                        for line in wire["plan_lines"]
                                    ],
                                }
                            )
                        }
                    ]
                }
            }
        ],
        "usageMetadata": {"totalTokenCount": 10},
    }
    candidate, usage, repairs = lane.parse_vertex_candidate_with_repairs(packet)
    assert candidate == _fixture()
    assert usage == {"totalTokenCount": 10}
    assert repairs[0] == {
        "path": "$.goal",
        "code": "canonical_enum_casing_or_whitespace",
    }
    assert all(set(repair) == {"path", "code"} for repair in repairs)


def test_provider_wire_safe_repair_never_reinterprets_goal_or_literal():
    wire = lane.candidate_to_wire(_fixture())
    prose_goal = {"goal": "please squeeze in", "plan_lines": wire["plan_lines"]}
    with pytest.raises(lane.ModelLaneError, match="schema_invalid"):
        lane.normalize_provider_wire(prose_goal)
    literal = copy.deepcopy(wire)
    literal["plan_lines"][-1] = literal["plan_lines"][-1].replace(
        "binding:duration_minutes", "literal:15"
    )
    normalized, _ = lane.normalize_provider_wire(literal)
    with pytest.raises(lane.ModelLaneError, match="schema_invalid"):
        lane.wire_to_candidate(normalized)


def test_provider_blocked_evidence_is_deterministic_and_zero_effect():
    first = lane.build_provider_blocked_evidence()
    second = lane.build_provider_blocked_evidence()
    assert first == second
    assert first["result"] == (
        "reception_one_bureau_model_text_lane_provider_blocked_pass"
    )
    assert [item["review_disposition"] for item in first["positive_cases"]] == [
        "admit",
        "admit",
        "admit",
        "admit",
        "admit",
    ]
    assert all(
        item["disposition"] != "admit" for item in first["negative_cases"]
    )
    assert first["boundary"] == {
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "api_key_authentication_used": False,
        "network_access_performed": False,
        "database_access_performed": False,
        "product_data_used": False,
        "historical_diary_material_access_performed": False,
        "appointment_writes_performed": 0,
        "confirmation_performed": False,
        "product_delivery_performed": False,
    }


def test_occupied_authority_packet_is_exact_and_explicit():
    packet = lane.load_object(lane.ARTIFACT_DIR / "occupied-authority-request.json")
    boundary = packet["requested_exact_boundary"]
    assert packet["decision"] == "authorised_by_yuri"
    assert packet["authority_granted"] is True
    assert boundary["provider"] == "google_cloud_vertex_ai"
    assert boundary["model"] == "gemini-2.5-flash"
    assert boundary["project"] == "bernie-emr4-dev"
    assert boundary["location"] == "australia-southeast1"
    assert boundary["authentication"] == (
        "keyless_impersonated_service_account_adc"
    )
    assert boundary["fallback"] is False
    assert boundary["product_delivery"] is False
    assert boundary["appointment_write_authority"] is False


def test_one_use_broker_fixture_path_consumes_ledger_and_releases_only_after_proof(
    tmp_path, monkeypatch
):
    frame = _squeeze_frame()
    request_packet = live._cell_request(frame)
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
            profile=str(lane.PROFILE_PATH),
        )
    )
    provider_packet = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "text": json.dumps(
                                lane.candidate_to_wire(_fixture())
                            )
                        }
                    ],
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 80,
            "totalTokenCount": 180,
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
        {
            "mode": "test",
            "policy_id": broker.POLICY_ID,
        },
    )
    result = state.execute(request_packet)
    assert result["status"] == "completed"
    assert result["proofreader"]["disposition"] == "admit"
    assert result["release"]["proposal_family"] == "squeeze_in_assessment"
    assert result["release"]["write_performed"] is False
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 1
    events = live._validate_audit(audit_path)
    assert [event["event_type"] for event in events] == [
        "broker_ready",
        "request_admitted",
        "ledger_consumed",
        "provider_request_constructed",
        "provider_call_started",
        "provider_call_received",
        "provider_call_completed",
        "proofreader_completed",
        "release_committed",
    ]


def test_iterative_retry_attempt_and_ledger_ids_are_distinct_and_exactly_paired():
    frame = _squeeze_frame()
    request = live._cell_request(
        frame,
        attempt_id="reception-one-model-text-occupied-retry-001",
        ledger_id="reception-one-model-text-ledger-retry-001",
    )
    assert request["attempt_id"].endswith("retry-001")
    assert request["ledger_id"].endswith("retry-001")
    with pytest.raises(live.LiveError, match="cell_request_binding_invalid"):
        live._cell_request(
            frame,
            attempt_id="reception-one-model-text-occupied-retry-001",
            ledger_id="reception-one-model-text-ledger-retry-002",
        )
    with pytest.raises(broker.BrokerError, match="cell_request_binding_invalid"):
        broker.validate_attempt_ledger_pair(
            "reception-one-model-text-occupied-retry-000",
            "reception-one-model-text-ledger-retry-000",
        )
    broker.validate_attempt_ledger_pair(
        "reception-one-product-context-occupied-001",
        "reception-one-product-context-ledger-001",
    )
    broker.validate_attempt_ledger_pair(
        "reception-one-extended-runtime-occupied-001",
        "reception-one-extended-runtime-ledger-001",
    )
    with pytest.raises(broker.BrokerError, match="cell_request_binding_invalid"):
        broker.validate_attempt_ledger_pair(
            "reception-one-product-context-occupied-001",
            "reception-one-product-context-ledger-002",
        )
    with pytest.raises(broker.BrokerError, match="cell_request_binding_invalid"):
        broker.validate_attempt_ledger_pair(
            "reception-one-extended-runtime-occupied-001",
            "reception-one-extended-runtime-ledger-002",
        )


def test_relay_readiness_probe_is_payload_free_and_bounded(monkeypatch):
    calls = []

    class FakeDocker:
        def run(self, arguments, **kwargs):
            calls.append((arguments, kwargs))

            class Result:
                returncode = 0

            return Result()

    live._wait_relay_ready(FakeDocker())

    assert len(calls) == 1
    arguments, kwargs = calls[0]
    assert arguments[:4] == [
        "exec",
        live.RELAY_CONTAINER,
        "python",
        "-c",
    ]
    assert "/proc/net/tcp" in arguments[4]
    assert "parts[3]=='0A'" in arguments[4]
    assert "create_connection" not in arguments[4]
    assert "/v1/execute" not in arguments[4]
    assert kwargs["allowed"] == frozenset({0, 1})


def test_iterative_retry_authority_preserves_the_exact_closed_lane():
    authority = lane.load_object(
        lane.ARTIFACT_DIR / "iterative-retry-authority.json"
    )
    boundary = authority["exact_boundary"]
    assert authority["authority_granted"] is True
    assert authority["positive_conclusion"].startswith(
        "the_first_generated_candidate_admitted"
    )
    assert boundary["provider"] == "google_cloud_vertex_ai"
    assert boundary["model"] == broker.MODEL
    assert boundary["project"] == broker.PROJECT
    assert boundary["service_account"] == broker.SERVICE_ACCOUNT
    assert boundary["location"] == broker.LOCATION
    assert boundary["endpoint_hostname"] == broker.HOSTNAME
    assert boundary["data_class"] == "authored_synthetic"
    assert boundary["release"] == "in_memory_proposal_only"
    assert boundary["api_key_authentication"] is False
    assert boundary["automatic_regional_fallback"] is False
    assert boundary["database_access"] is False
    assert boundary["appointment_write_authority"] is False
    assert authority["retry_contract"]["no_call_after_first_positive_conclusion"]
    assert authority["retry_contract"]["cumulative_application_cost_ceiling_usd"] == 1


def test_bounded_provider_error_never_retains_prompt_echo():
    raw = json.dumps(
        {
            "error": {
                "code": 400,
                "status": "INVALID_ARGUMENT",
                "message": (
                    "Margaret Thompson squeeze request was invalid and "
                    "must not be retained"
                ),
                "details": [
                    {
                        "fieldViolations": [
                            {"field": "generationConfig.responseSchema.steps"}
                        ]
                    }
                ],
            }
        }
    ).encode()
    safe = broker._safe_error(raw, 400)
    assert safe["http_status"] == 400
    assert safe["provider_error_code"] == 400
    assert safe["normalized_status"] == "INVALID_ARGUMENT"
    assert safe["sanitized_message"] == "provider_error_message_withheld"
    assert safe["field_violation_paths"] == [
        "generationConfig.responseSchema.steps"
    ]
    assert safe["discarded_raw_error_hash"].startswith("sha256:")
    assert "Margaret" not in json.dumps(safe)


def test_consumed_attempt_retains_its_validated_precall_revision_binding():
    evidence = lane.load_object(lane.ARTIFACT_DIR / "occupied-evidence.json")
    gate = evidence["precall_gate"]
    assert gate["all_cloud_controls_passed"] is True
    assert gate["continuity_graph_revision"] == 65
    assert gate["compass_map_revision"] == 52
    assert gate["compass_source_graph_revision"] == 65
    with pytest.raises(live.LiveError, match="revision_binding_invalid"):
        live._precall_gate()


def test_external_audit_and_postfailure_diagnostic_are_bounded_and_zero_retry():
    external = lane_audit.build_external_audit(
        lane.ARTIFACT_DIR / "occupied-evidence.json",
        lane.ARTIFACT_DIR / "occupied-audit.jsonl",
        lane.ARTIFACT_DIR / "occupied-preflight-evidence.json",
    )
    assert external["provider_outcome"]["status"] == "failed_before_candidate"
    assert external["provider_outcome"]["http_status"] == 400
    assert external["proofreader"]["disposition"] == "not_reached"
    assert external["release"] is None
    assert external["retry"] == {
        "count": 0,
        "authorised": False,
        "performed": False,
        "reason": "single_call_ceiling_consumed",
    }
    diagnostic = lane_audit.build_diagnostic(external)
    assert diagnostic["result"] == (
        "reception_one_bureau_model_text_schema_state_diagnostic_pass"
    )
    assert diagnostic["repository_local_repair"]["array_schema_count"] == 1
    assert diagnostic["repository_local_repair"]["enum_keyword_count"] == 0
    assert diagnostic["boundary"]["provider_calls_performed"] == 0
    assert diagnostic["boundary"]["retry_performed"] is False
    rendered = json.dumps(external).casefold()
    for forbidden in (
        "authorization: bearer",
        "access_token",
        "raw_prompt",
        "raw_provider_response",
        "chain_of_thought",
    ):
        if forbidden in {"raw_prompt", "raw_provider_response", "chain_of_thought"}:
            assert f'"{forbidden}_recorded": false' in rendered
        else:
            assert forbidden not in rendered


def test_iterative_retry_external_audit_stops_at_first_admitted_result():
    artifact_dir = lane.ARTIFACT_DIR
    analysis = lane_audit.build_iterative_sequence_analysis(
        [
            artifact_dir / f"occupied-retry-{index:03d}-external-audit.json"
            for index in range(1, 4)
        ],
        artifact_dir / "occupied-retry-final-residue-evidence.json",
    )
    assert analysis["result"] == (
        "reception_one_bureau_model_text_iterative_retry_pass"
    )
    assert analysis["provider_call_count"] == 3
    assert analysis["failed_closed_before_terminal_success"] == 2
    assert analysis["calls_after_first_admitted_result"] == 0
    assert analysis["terminal_proofreader"]["disposition"] == "admit"
    assert analysis["terminal_release"]["write_performed"] is False
    assert analysis["cost_guard"]["conservative_upper_bound_usd"] < 1
    assert analysis["explicit_exclusions"]["product_or_database_access"] is False


def test_all_model_lane_json_files_are_objects_and_valid_json():
    for path in lane.ARTIFACT_DIR.glob("*.json"):
        assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict), path

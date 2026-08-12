from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_default_off_runtime_instrumentation_architecture import (
    CONTRACT_PATH,
    EXPECTED_FEEDBACK_EDGES,
    EXPECTED_IMPLEMENTATION_GATE,
    EXPECTED_PROJECTION_FIELDS,
    EXPECTED_RECORD_FIELDS,
    EXPECTED_ROUTES,
    EXPECTED_SEQUENCE,
    EXPECTED_SOURCE_HEAD,
    EXPECTED_SOURCES,
    SCHEMA_PATH,
    build_report,
    hostile_mutations,
    load_contract,
    load_schema,
    source_errors,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-default-off-runtime-instrumentation-architecture-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-default-off-runtime-instrumentation-architecture.md"
THREAT = ROOT / "docs/security/raisa-provider-free-default-off-runtime-instrumentation-architecture-threat-model-delta.md"
SCRIPT = ROOT / "scripts/raisa_provider_free_default_off_runtime_instrumentation_architecture.py"


def test_contract_schema_semantics_and_exact_report_pass() -> None:
    packet = load_contract()
    Draft202012Validator(load_schema()).validate(packet)
    assert validate_contract(packet, verify_source_files=True) == []
    assert build_report(packet) == {
        "schema_version": "emr4.default-off-runtime-instrumentation-architecture-report.v1",
        "status": "passed", "reasons": [], "source_head": EXPECTED_SOURCE_HEAD,
        "raw_route_count": 4, "phase_count": 2, "projection_field_count": 24,
        "record_field_count": 15, "forbidden_feedback_edge_count": 12,
        "hostile_mutation_count": 60, "hostile_mutation_escape_count": 0,
        "application_source_edited": False, "runtime_instrumentation_created": False,
        "provider_or_network_used": False, "command_or_write_performed": False,
    }


def test_source_hashes_and_source_ast_are_exact() -> None:
    packet = load_contract()
    assert packet["source_head"] == EXPECTED_SOURCE_HEAD
    assert {row["path"]: row["sha256"] for row in packet["source_bindings"]} == EXPECTED_SOURCES
    assert source_errors(packet) == []


def test_exact_four_route_seams_and_current_result_forms() -> None:
    rows = {row["adapter_id"]: row for row in load_contract()["source_inventory"]["route_seams"]}
    assert set(rows) == set(EXPECTED_ROUTES)
    for adapter_id, expected in EXPECTED_ROUTES.items():
        assert all(rows[adapter_id][key] == value for key, value in expected.items())
    assert rows["raw_compat_delete"]["current_result_form"] == "helper_call_then_implicit_none"
    assert all(rows[key]["current_result_form"] == "direct_helper_return" for key in (
        "raw_compat_create", "raw_compat_update", "raw_compat_status"
    ))


def test_completion_claim_splits_logical_result_from_serialized_response() -> None:
    completion = load_contract()["primary_completion"]
    assert completion["route_stage_primary_state"] == "transaction_audit_and_logical_result_complete_response_not_yet_serialized"
    assert completion["handoff_primary_state"] == "final_asgi_response_body_frame_successfully_sent"
    assert completion["route_local_observer_call_permitted"] is False
    assert completion["post_send_handoff_required"] is True
    assert "database_commit_completed" in completion["route_helper_success_proves"]
    assert "response_body_bytes_sent" in completion["route_helper_success_does_not_prove"]


def test_generation_is_immutable_distinct_and_default_deny() -> None:
    config = load_contract()["generation_configuration"]
    assert config["model"] == "immutable_process_start_generation"
    assert config["global_default"] == "disabled"
    assert config["practice_allowlist_default"] == []
    assert config["route_allowlist_default"] == []
    assert config["digest_key_reference_default"] is None
    assert config["database_or_network_lookup"] is False
    assert config["separate_from_setting"] == "appointment_raw_compat_mode"
    assert config["raw_compat_setting_shadow_authority"] is False
    assert config["external_disable_latch"] == "monotonic_false_to_true_disable_only"
    assert config["enablement_authority_granted"] is False


def test_context_requires_server_owned_session_and_correlation_or_denies() -> None:
    context = load_contract()["request_context"]
    assert context["provenance"] == "server_created_and_authenticated_only"
    assert context["missing_context"] == "disabled_no_stage"
    assert context["required_fields"] == [
        "practice_id", "actor_id", "actor_role", "authenticated_session_reference",
        "server_correlation_reference",
    ]
    for key in (
        "bearer_token_hashing", "inbound_correlation_authority",
        "actor_practice_session_synthesis", "direct_identifier_fallback",
    ):
        assert context[key] == "forbidden"


def test_disabled_stage_short_circuits_before_raw_input_and_calls_nothing() -> None:
    stage = load_contract()["route_staging_phase"]
    assert stage["stage_point"] == "after_command_helper_success_before_route_return"
    assert stage["global_disabled_short_circuit_before_raw_input_read"] is True
    assert stage["input_read_before_full_admission"] is False
    assert stage["adapter_invoked"] is False
    assert stage["observer_invoked"] is False
    assert stage["sink_invoked"] is False
    assert stage["return_channel"] == "none"
    assert stage["retry"] is False


def test_finalizer_sends_first_then_offers_without_feedback() -> None:
    finalizer = load_contract()["post_response_finalizer"]
    assert finalizer["mount"] == "outermost_user_asgi_middleware_around_existing_cors_and_error_stack"
    assert finalizer["message_trigger"] == "http.response.body_with_more_body_false"
    assert finalizer["send_order"] == "await_original_send_success_before_handoff"
    assert finalizer["cell_operation"] == "atomic_take_and_clear_at_most_once"
    assert finalizer["offer_port"] == "offer_nowait"
    assert finalizer["offer_awaited"] is False
    assert finalizer["offer_result_channel"] == "none"
    assert finalizer["retry"] is False
    assert finalizer["send_callable_passed_to_offer"] is False
    assert finalizer["response_material_passed_to_offer"] is False


def test_projection_and_record_are_exact_and_minimized() -> None:
    packet = load_contract()
    projection = packet["projection"]
    record = packet["diagnostic_record"]
    assert projection["allowed_fields"] == EXPECTED_PROJECTION_FIELDS
    assert record["allowed_fields"] == EXPECTED_RECORD_FIELDS
    assert projection["free_text_inputs"] == []
    assert projection["response_inputs"] == []
    assert projection["raw_input_retention"] is False
    assert projection["digest_key_exposed"] is False
    assert {"appointment_reason_free_text", "appointment_note_free_text", "bearer_token"} <= set(projection["forbidden_inputs"])
    assert record["authority"] == "diagnostic_only_non_authoritative_lossy"
    assert record["command_outcome"] is False
    assert record["audit_or_truth_record"] is False
    assert record["persistence_selected"] is False


def test_capability_modules_and_feedback_edges_are_closed() -> None:
    packet = load_contract()
    modules = packet["capability_modules"]
    assert {"observer", "adapter", "sink", "database", "command"} <= set(modules["route_stage"]["forbidden"])
    assert {"response_body", "response_headers", "send_callable_to_offer", "command"} <= set(modules["after_send_finalizer"]["forbidden"])
    assert {"route_handler", "request", "response", "database", "kernel", "command"} <= set(modules["downstream_observer"]["forbidden"])
    assert packet["forbidden_feedback_edges"] == EXPECTED_FEEDBACK_EDGES
    assert packet["future_implementation_gate"] == EXPECTED_IMPLEMENTATION_GATE
    assert packet["future_evidence_sequence"] == EXPECTED_SEQUENCE


def test_all_sixty_hostile_mutations_fail_closed() -> None:
    packet = load_contract()
    mutants = hostile_mutations(packet)
    assert len(mutants) == 60
    assert [name for name, mutant in mutants if not validate_contract(mutant)] == []


def test_schema_closes_every_declared_object() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                assert node.get("additionalProperties") is False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)


def test_validator_imports_no_application_database_network_provider_or_process() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {"__future__", "ast", "copy", "hashlib", "json", "jsonschema", "pathlib", "typing"}
    assert imports.isdisjoint({"app", "sqlalchemy", "psycopg", "requests", "httpx", "google", "socket", "subprocess"})


def test_plan_design_and_threat_model_freeze_the_fail_closed_boundary() -> None:
    text = " ".join(
        " ".join(path.read_text(encoding="utf-8").lower().split())
        for path in (PLAN, DESIGN, THREAT)
    )
    for phrase in (
        "provider-free", "two phases", "after the final asgi", "single-assignment",
        "offer_nowait", "server-owned", "bearer token", "default to disabled",
        "no database", "no kernel", "patient", "protected-ref",
    ):
        assert phrase in text


def test_contract_paths_and_artifacts_exist() -> None:
    for path in (CONTRACT_PATH, SCHEMA_PATH, PLAN, DESIGN, THREAT, SCRIPT):
        assert path.is_file()

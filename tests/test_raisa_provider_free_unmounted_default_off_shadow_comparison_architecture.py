from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_default_off_shadow_comparison_architecture import (
    CONTRACT_PATH,
    EXPECTED_COMPARISONS,
    EXPECTED_ENABLEMENT,
    EXPECTED_FEEDBACK_EDGES,
    EXPECTED_GAPS,
    EXPECTED_PRIMARY_COMPONENTS,
    EXPECTED_PROJECTION_FIELDS,
    EXPECTED_RECORD_FIELDS,
    EXPECTED_ROUTES,
    EXPECTED_SEQUENCE,
    EXPECTED_SOURCE_HEAD,
    EXPECTED_SOURCES,
    SCHEMA_PATH,
    admission_decision,
    build_report,
    hostile_mutations,
    load_contract,
    load_schema,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture.md"
THREAT = ROOT / "docs/security/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-threat-model-delta.md"
SCRIPT = ROOT / "scripts/raisa_provider_free_unmounted_default_off_shadow_comparison_architecture.py"


def test_closed_contract_and_exact_report_pass() -> None:
    packet = load_contract()
    Draft202012Validator(load_schema()).validate(packet)
    assert validate_contract(packet, verify_source_files=True) == []
    assert build_report(packet) == {
        "schema_version": "emr4.default-off-shadow-comparison-architecture-report.v1",
        "status": "passed",
        "reasons": [],
        "source_head": EXPECTED_SOURCE_HEAD,
        "raw_route_count": 4,
        "enablement_dimension_count": 4,
        "projection_field_count": 24,
        "record_field_count": 15,
        "forbidden_feedback_edge_count": 12,
        "hostile_mutation_count": 46,
        "hostile_mutation_escape_count": 0,
        "observer_runtime_created": False,
        "command_or_write_performed": False,
    }


def test_source_bindings_are_exact_and_current() -> None:
    packet = load_contract()
    assert packet["source_head"] == EXPECTED_SOURCE_HEAD
    assert {row["path"]: row["sha256"] for row in packet["source_bindings"]} == EXPECTED_SOURCES
    assert validate_contract(packet, verify_source_files=True) == []


def test_scope_is_exactly_four_parent_raw_adapters() -> None:
    scope = load_contract()["scope"]
    observed = {
        row["adapter_id"]: (
            row["family_id"], row["method"], row["path"], row["canonical_operation_id"]
        )
        for row in scope["route_adapters"]
    }
    assert observed == EXPECTED_ROUTES
    assert scope["proposal_routes_in_scope"] is False
    assert scope["confirm_routes_in_scope"] is False
    assert scope["current_parent_posture"] == "current_raw_not_kernel_eligible"


def test_four_way_enablement_is_default_deny() -> None:
    assert load_contract()["enablement"] == EXPECTED_ENABLEMENT
    variants = [
        (None, "enabled", "enabled", True, False),
        ("stale", "enabled", "enabled", True, False),
        ("current", None, "enabled", True, False),
        ("current", "disabled", "enabled", True, False),
        ("current", "enabled", None, True, False),
        ("current", "enabled", "disabled", True, False),
        ("current", "enabled", "enabled", None, False),
        ("current", "enabled", "enabled", False, False),
        ("current", "enabled", "enabled", True, None),
        ("current", "enabled", "enabled", True, True),
    ]
    for generation, global_state, practice, route, disabled in variants:
        assert admission_decision(
            generation_status=generation,
            global_state=global_state,
            practice_state=practice,
            route_allowed=route,
            externally_disabled=disabled,
        ) == "disabled_no_observation"
    assert admission_decision(
        generation_status="current",
        global_state="enabled",
        practice_state="enabled",
        route_allowed=True,
        externally_disabled=False,
    ) == "shadow_observation_admitted"


def test_primary_result_is_sealed_before_one_way_best_effort_handoff() -> None:
    placement = load_contract()["placement"]
    assert placement["primary_result_components"] == EXPECTED_PRIMARY_COMPONENTS
    assert placement["primary_result_state_before_observation"] == "sealed_immutable"
    assert placement["handoff_direction"] == "primary_to_shadow_only"
    assert placement["handler_return_channel"] == "none"
    assert placement["delivery"] == "bounded_best_effort_at_most_once"
    assert placement["overflow"] == "drop_shadow_evidence_only"
    assert placement["timeout"] == "drop_shadow_evidence_only"
    assert placement["retry_required"] is False
    assert placement["correctness_dependency"] is False


def test_projection_is_minimized_and_excludes_direct_or_patient_material() -> None:
    projection = load_contract()["projection"]
    assert projection["allowed_fields"] == EXPECTED_PROJECTION_FIELDS
    assert projection["identity_encoding"] == "versioned_one_way_hmac_digest"
    forbidden = set(projection["forbidden_material"])
    assert {
        "raw_request_body", "raw_response_body", "patient_identifier",
        "patient_name", "appointment_reason_free_text", "appointment_note_free_text",
        "direct_practice_id", "direct_actor_id", "direct_session_id",
        "direct_target_id", "direct_correlation_id", "raw_confirmation_token",
        "credential", "source_state", "authority_decision", "database_value",
        "mutation_receipt", "audit_receipt",
    } <= forbidden
    assert set(projection["allowed_fields"]).isdisjoint(forbidden)
    assert projection["current_tranche_values"] == "authored_synthetic_only"


def test_observer_preserves_exact_gap_classes_and_has_zero_capabilities() -> None:
    observer = load_contract()["observer"]
    assert observer["expected_current_gap_codes"] == EXPECTED_GAPS
    assert observer["comparison_classes"] == EXPECTED_COMPARISONS
    assert observer["candidate_type"] == "ShadowConditionalAppointmentCandidate"
    assert observer["candidate_executable"] is False
    assert observer["runtime_execution_authorized"] is False
    assert observer["command_outcome_emitted"] is False
    assert observer["parent_route_posture_changed"] is False
    assert all(value is False for value in observer["capabilities"].values())


def test_record_is_diagnostic_lossy_and_has_no_persistence_selection() -> None:
    record = load_contract()["diagnostic_record"]
    assert record["allowed_fields"] == EXPECTED_RECORD_FIELDS
    assert record["authority"] == "diagnostic_only_non_authoritative_lossy"
    assert record["is_audit_record"] is False
    assert record["is_command_receipt"] is False
    assert record["is_source_truth"] is False
    assert record["persistence_selected"] is False
    assert record["retention_selected"] is False
    assert record["aggregation_selected"] is False
    assert {"command_outcome", "mutation_receipt", "audit_receipt"} <= set(
        record["forbidden_material"]
    )


def test_all_response_command_and_client_feedback_edges_are_forbidden() -> None:
    packet = load_contract()
    assert packet["forbidden_feedback_edges"] == EXPECTED_FEEDBACK_EDGES
    assert packet["future_evidence_sequence"] == EXPECTED_SEQUENCE
    assert all(value is False for value in packet["effect_boundary"].values())
    assert all(value is False for value in packet["claim_boundary"].values())


def test_all_forty_six_hostile_mutations_fail_closed() -> None:
    packet = load_contract()
    mutants = hostile_mutations(packet)
    assert len(mutants) == 46
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
    assert imports <= {"__future__", "copy", "hashlib", "json", "jsonschema", "pathlib", "typing"}
    assert imports.isdisjoint({"app", "sqlalchemy", "psycopg", "requests", "httpx", "google", "socket", "subprocess"})


def test_plan_design_and_threat_model_freeze_no_feedback_and_no_runtime() -> None:
    text = " ".join(
        " ".join(path.read_text(encoding="utf-8").lower().split())
        for path in (PLAN, DESIGN, THREAT)
    )
    for phrase in (
        "provider-free", "unmounted", "default-off", "sealed",
        "no return", "no observer", "application route", "no import", "command, write",
        "diagnostic", "loss is acceptable", "patient", "protected-ref",
    ):
        assert phrase in text


def test_contract_paths_and_artifacts_exist() -> None:
    for path in (CONTRACT_PATH, SCHEMA_PATH, PLAN, DESIGN, THREAT, SCRIPT):
        assert path.is_file()

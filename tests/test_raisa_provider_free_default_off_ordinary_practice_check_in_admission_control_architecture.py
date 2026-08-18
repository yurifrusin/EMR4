from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_default_off_ordinary_practice_check_in_admission_control_architecture import (
    CONTRACT_PATH,
    EXPECTED_ALERTS,
    EXPECTED_ALLOWED_TRANSITIONS,
    EXPECTED_COMMAND_REQUIREMENTS,
    EXPECTED_CONTRACT_DIGEST,
    EXPECTED_DECISION_STEPS,
    EXPECTED_EVIDENCE_GATES,
    EXPECTED_FORBIDDEN_TRANSITIONS,
    EXPECTED_METRICS,
    EXPECTED_OPERATIONS,
    EXPECTED_READINESS_SOURCE,
    EXPECTED_ROUTE_SOURCE,
    EXPECTED_SOURCE_HEAD,
    EXPECTED_SOURCES,
    EXPECTED_STATES,
    FORBIDDEN_TELEMETRY_FIELDS,
    SCHEMA_PATH,
    _canonical_json_digest,
    build_report,
    hostile_mutations,
    load_contract,
    load_schema,
    source_errors,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture.md"
THREAT = ROOT / "docs/security/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-threat-model-delta.md"
SCRIPT = ROOT / "scripts/raisa_provider_free_default_off_ordinary_practice_check_in_admission_control_architecture.py"
EVIDENCE = CONTRACT_PATH.parent / "provider-free-architecture-evidence.json"
REPORT = CONTRACT_PATH.parent / "architecture-report.md"


def test_contract_schema_semantics_and_exact_report_pass() -> None:
    packet = load_contract()
    Draft202012Validator.check_schema(load_schema())
    Draft202012Validator(load_schema()).validate(packet)
    assert validate_contract(packet, verify_source_files=True) == []
    assert build_report(packet) == {
        "schema_version": "emr4.check-in-admission-control-architecture-report.v1",
        "status": "passed",
        "reasons": [],
        "source_head": EXPECTED_SOURCE_HEAD,
        "source_binding_count": 11,
        "state_count": 4,
        "allowed_transition_count": 6,
        "control_operation_count": 5,
        "operational_evidence_gate_count": 3,
        "metric_family_count": 5,
        "alert_count": 6,
        "hostile_mutation_count": 390,
        "hostile_mutation_escape_count": 0,
        "ordinary_practice_enabled": False,
        "application_or_configuration_changed": False,
        "provider_or_network_used": False,
        "live_clockwork_adopted": False,
    }


def test_contract_digest_and_source_bindings_are_exact() -> None:
    packet = load_contract()
    assert packet["source_head"] == EXPECTED_SOURCE_HEAD
    assert packet["accepted_readiness_source"] == EXPECTED_READINESS_SOURCE
    assert packet["accepted_route_source"] == EXPECTED_ROUTE_SOURCE
    assert _canonical_json_digest(packet) == EXPECTED_CONTRACT_DIGEST
    assert {row["path"]: row["sha256"] for row in packet["source_bindings"]} == EXPECTED_SOURCES
    assert source_errors(packet) == []


def test_current_posture_remains_default_off_synthetic_only_and_unmodified() -> None:
    posture = load_contract()["current_posture"]
    assert posture["feature_setting"] == "rayleen_a5_check_in_enabled"
    assert posture["feature_default"] is False
    assert posture["synthetic_allowlist_setting"] == "rayleen_a5_check_in_synthetic_practice_ids"
    assert posture["synthetic_allowlist_default"] == []
    assert posture["ordinary_admission_setting_present"] is False
    assert posture["ordinary_admission_records_present"] is False
    assert posture["product_source_changed"] is False
    assert posture["configuration_changed"] is False
    assert posture["openapi_changed"] is False
    assert posture["practice_enabled"] is False


def test_synthetic_and_ordinary_lanes_are_non_substitutable() -> None:
    lanes = load_contract()["admission_lanes"]
    assert lanes["synthetic"]["lane_id"] == "authored_synthetic"
    assert lanes["synthetic"]["ordinary_authority"] is False
    assert lanes["synthetic"]["may_infer_ordinary_record"] is False
    assert lanes["ordinary"]["lane_id"] == "ordinary_practice"
    assert lanes["ordinary"]["default_when_absent"] == "denied"
    assert lanes["ordinary"]["caller_claim_allowed"] is False
    assert lanes["ordinary"]["synthetic_receipt_substitution_allowed"] is False
    assert lanes["both_lanes_match"] == "deny_lane_ambiguity"
    assert lanes["neither_lane_matches"] == "deny_no_admission"
    assert lanes["cross_lane_fallback"] is False


def test_state_machine_has_no_resume_and_rollback_cannot_activate() -> None:
    machine = load_contract()["ordinary_state_machine"]
    assert machine["states"] == EXPECTED_STATES
    assert machine["allowed_transitions"] == EXPECTED_ALLOWED_TRANSITIONS
    assert machine["forbidden_transitions"] == EXPECTED_FORBIDDEN_TRANSITIONS
    assert machine["resume_transition_present"] is False
    assert machine["reactivation_requires_new_record"] is True
    assert machine["activation_authority_granted"] is False
    assert "suspended->active" not in machine["allowed_transitions"]
    assert "rollback->active" not in machine["allowed_transitions"]


def test_decision_order_and_kill_switch_are_dominant_and_capability_free() -> None:
    packet = load_contract()
    evaluator = packet["decision_evaluator"]
    switch = packet["global_kill_switch"]
    assert evaluator["ordered_steps"] == EXPECTED_DECISION_STEPS
    assert evaluator["kill_switch_dominates_synthetic"] is True
    assert evaluator["kill_switch_dominates_ordinary"] is True
    assert evaluator["unknown_or_extra_state"] == "deny"
    assert evaluator["stale_snapshot_behavior"] == "deny_without_last_known_good_fallback"
    assert evaluator["multiple_current_records_behavior"] == "deny"
    assert evaluator["executes_check_in"] is False
    assert evaluator["creates_confirmation_evidence"] is False
    assert evaluator["changes_authentication_or_role"] is False
    assert switch["engaged_effect"] == "deny_both_lanes"
    assert switch["clear_in_place_allowed"] is False
    assert switch["monotonic_within_generation"] is True
    assert switch["new_generation_required_to_clear"] is True
    assert switch["automatic_clear_allowed"] is False


def test_api_spine_commands_are_unmounted_rest_only_and_graphql_is_read_only() -> None:
    packet = load_contract()
    spine = packet["api_spine"]
    control = packet["control_plane"]
    assert spine["state_change_transport"] == "rest_openapi_only"
    assert spine["graphql_posture"] == "read_only_posture_projection_only"
    assert spine["async_event_posture"] == "observation_only_never_authority"
    assert spine["current_manifest_changed"] is False
    assert spine["candidate_control_operations_unmounted"] == EXPECTED_OPERATIONS
    assert [row["operation_id"] for row in control["operations"]] == EXPECTED_OPERATIONS
    assert all(row["method"] == "POST" for row in control["operations"])
    assert all(row["authorized_now"] is False for row in control["operations"])
    assert control["command_requirements"] == EXPECTED_COMMAND_REQUIREMENTS
    assert spine["model_or_agent_write_authority"] is False
    assert spine["committed_event_write_authority"] is False


def test_full_git_object_is_a_type_not_a_memory_requirement() -> None:
    control = load_contract()["control_plane"]
    pattern = re.compile(control["authority_git_object_pattern"])
    assert pattern.fullmatch(EXPECTED_SOURCE_HEAD)
    assert not pattern.fullmatch(EXPECTED_SOURCE_HEAD[:7])
    assert control["abbreviated_git_object_allowed"] is False
    assert "authority_git_object_full_40" in control["command_requirements"]
    assert "authority_git_object_resolved" in control["command_requirements"]
    assert load_contract()["clockwork_boundary"]["manual_git_abbreviation_accepted"] is False


def test_rollback_is_disable_only_and_unknown_commit_releases_no_success() -> None:
    packet = load_contract()
    rollback = packet["rollback"]
    assert rollback["operation_id"] == "withdrawAppointmentCheckInAdmission"
    assert rollback["disable_only"] is True
    assert rollback["terminal_state"] == "withdrawn"
    assert rollback["restore_active_version_allowed"] is False
    assert rollback["retry_after_unknown_commit_allowed"] is False
    assert rollback["readback_required_after_unknown_commit"] is True
    assert rollback["audit_required"] is True
    assert packet["control_plane"]["unknown_commit_behavior"] == "release_no_success_then_read_back_by_command_and_idempotency_identity"


def test_all_three_operational_evidence_gaps_remain_mandatory() -> None:
    evidence = load_contract()["operational_evidence"]
    assert evidence["required_for_active"] is True
    assert [row["gate_id"] for row in evidence["gates"]] == EXPECTED_EVIDENCE_GATES
    assert all(row["classification"] == "operational_evidence_gap" for row in evidence["gates"])
    assert "full_40_character_resolved_git_object" in evidence["artifact_requirements"]
    assert evidence["authored_synthetic_substitution_allowed"] is False
    assert evidence["missing_invalid_stale_or_wrong_generation"] == "deny"


def test_observability_is_exact_low_cardinality_and_non_phi() -> None:
    observability = load_contract()["observability"]
    assert [row["name"] for row in observability["metric_families"]] == EXPECTED_METRICS
    assert FORBIDDEN_TELEMETRY_FIELDS <= set(observability["forbidden_labels_and_values"])
    assert observability["raw_request_or_response_allowed"] is False
    assert observability["audit_record_used_as_metric"] is False
    assert observability["telemetry_feedback_to_admission"] is False
    assert observability["automatic_retry_or_control_action"] is False
    labels = {
        domain["label"]
        for metric in observability["metric_families"]
        for domain in metric["label_domains"]
    }
    assert labels == {"environment", "lane", "outcome", "reason_code", "operation"}


def test_alerts_contain_no_identifier_and_cannot_actuate() -> None:
    alerts = load_contract()["observability"]["alerts"]
    assert [row["alert_id"] for row in alerts] == EXPECTED_ALERTS
    assert all(row["severity"] == "critical" for row in alerts)
    assert all(row["automatic_control_action"] is False for row in alerts)
    assert all(row["contains_identifier"] is False for row in alerts)


def test_clockwork_and_deepseek_broker_remain_shadow_only() -> None:
    clockwork = load_contract()["clockwork_boundary"]
    assert clockwork["projection_model"] == "derive_evidence_from_one_typed_reading"
    assert clockwork["ariadne_deepseek_shared_clock_status"] == "accepted_shadow_only"
    assert clockwork["deepseek_broker_binding"] == "protocol_conformance_only_no_product_or_activation_authority"
    assert clockwork["live_clockwork_adoption_authorized"] is False
    assert clockwork["existing_control_retirement_authorized"] is False


def test_every_closed_boundary_is_false_and_successor_enables_nothing() -> None:
    packet = load_contract()
    assert packet["closed_boundaries"]
    assert all(value is False for value in packet["closed_boundaries"].values())
    successor = packet["successor"]
    assert successor["operation_id"] == "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal"
    assert successor["ordinary_enablement_authorized"] is False
    assert successor["operational_evidence_gaps_closed"] is False


def test_all_390_hostile_mutations_fail_closed() -> None:
    packet = load_contract()
    mutants = hostile_mutations(packet)
    assert len(mutants) == 390
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
    assert imports <= {
        "__future__",
        "copy",
        "hashlib",
        "json",
        "jsonschema",
        "pathlib",
        "re",
        "typing",
    }
    assert imports.isdisjoint(
        {"app", "sqlalchemy", "psycopg", "requests", "httpx", "google", "socket", "subprocess"}
    )


def test_plan_design_and_threat_model_freeze_the_security_boundary() -> None:
    text = " ".join(
        " ".join(path.read_text(encoding="utf-8").lower().split())
        for path in (PLAN, DESIGN, THREAT)
    )
    for phrase in (
        "provider-free",
        "authored-synthetic",
        "ordinary-practice",
        "default denial",
        "kill switch",
        "disable-only",
        "40-character",
        "rest/openapi",
        "graphql",
        "non-phi",
        "unknown commit",
        "nobypassrls",
        "deepseek",
        "protected-ref",
    ):
        assert phrase in text


def test_derived_evidence_matches_the_single_typed_reading() -> None:
    assert json.loads(EVIDENCE.read_text(encoding="utf-8")) == build_report()


def test_contract_paths_and_artifacts_exist() -> None:
    for path in (CONTRACT_PATH, SCHEMA_PATH, PLAN, DESIGN, THREAT, SCRIPT, EVIDENCE, REPORT):
        assert path.is_file()

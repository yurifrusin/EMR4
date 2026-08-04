from __future__ import annotations

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.model_required_bureau_c3_d3_acceptance import (
    C3_ANALYSIS,
    CONTRACT,
    CONTRACT_SCHEMA,
    D3_ANALYSIS,
    EXPECTED_HEAD,
    EXPECTED_RESULT,
    SCHEMA_EXAMPLES,
    authority_decision,
    build_evidence,
    canonical_sha256,
    classify_recovery,
    load_json,
    promotion_plan_for_class,
    proofread_recovery_plan,
)


def errors(schema_path, value):
    schema = load_json(schema_path)
    return list(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(value)
    )


def test_c3_d3_acceptance_passes_with_zero_candidate_side_effects():
    evidence = build_evidence()
    assert evidence["passed"] is True
    assert evidence["result"] == EXPECTED_RESULT
    assert evidence["source_head"] == EXPECTED_HEAD
    assert set(evidence["authority_and_side_effects"].values()) == {0}


def test_contract_and_examples_are_closed_draft_2020_12_schemas():
    assert not errors(CONTRACT_SCHEMA, load_json(CONTRACT))
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert not errors(schema_path, load_json(example_path))


def test_read_only_worker_lanes_returned_advisory_artifacts_only():
    for path in (C3_ANALYSIS, D3_ANALYSIS):
        text = path.read_text(encoding="utf-8")
        assert EXPECTED_HEAD in text
        assert "advisory" in text.lower()
        assert "non-execut" in text.lower()


@pytest.mark.parametrize(
    ("operation", "target", "blast", "reversibility", "expected"),
    [
        (
            "observe",
            "observation",
            "observation_only",
            "not_applicable",
            "observe_explain_only",
        ),
        (
            "scoped_service_recovery",
            "service",
            "single_service",
            "deterministic_rollback_proven",
            "reversible_scoped_service_recovery",
        ),
        (
            "rollback",
            "service",
            "single_environment",
            "deterministic_rollback_proven",
            "human_approved_rollback_or_failover",
        ),
        (
            "database_operation",
            "database",
            "single_environment",
            "deterministic_rollback_proven",
            "dual_review_database_security_or_data_supply",
        ),
        (
            "generic_shell",
            "service",
            "single_service",
            "deterministic_rollback_proven",
            "forbidden_autonomous_action",
        ),
    ],
)
def test_c3_risk_is_derived_from_closed_fields_not_candidate_prose(
    operation, target, blast, reversibility, expected
):
    plan = load_json(SCHEMA_EXAMPLES["recovery_plan"][1])
    plan["operation_class"] = operation
    plan["target"]["kind"] = target
    plan["maximum_blast_radius"] = blast
    plan["reversibility"] = reversibility
    if operation == "observe":
        plan["rollback"] = {
            "kind": "none",
            "runbook_id": None,
            "target_sha256": None,
        }
    assert classify_recovery(plan) == expected


def test_candidate_cannot_lower_computed_risk_or_issue_execution_evidence():
    plan = load_json(SCHEMA_EXAMPLES["recovery_plan"][1])
    assert plan["proposed_risk_tier"] == "observe_explain_only"
    decision = authority_decision(plan)
    assert decision["computed_risk_tier"] == "reversible_scoped_service_recovery"
    assert decision["candidate_risk_overridden"] is True
    assert decision["required_authority"] == "ordinary_confirmation"
    assert decision["current_state"] == "review_required"
    assert decision["command_envelope_issued"] is False
    assert decision["actuator_gate"] == "closed"
    assert decision["execution_authorized"] is False


def test_authority_decision_binds_canonical_plan_hash_and_earliest_expiry():
    plan = load_json(SCHEMA_EXAMPLES["recovery_plan"][1])
    decision = authority_decision(plan)
    assert decision == load_json(SCHEMA_EXAMPLES["recovery_authority"][1])
    assert decision["plan_sha256"] == canonical_sha256(plan)
    assert decision["effective_expiry"] == "2026-08-04T08:01:00Z"
    assert decision["plan_change_invalidates_reviews"] is True
    assert plan["idempotency"]["effective_key_issued"] is False


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("unknown_runbook", "UNKNOWN_RUNBOOK"),
        ("unknown_evidence", "UNKNOWN_EVIDENCE"),
        ("executable_content", "EXECUTABLE_CONTENT"),
        ("expired", "STALE_OR_SUPERSEDED"),
    ],
)
def test_c3_proofreader_fails_closed(mutation, expected):
    plan = load_json(SCHEMA_EXAMPLES["recovery_plan"][1])
    now = "2026-08-04T08:00:30Z"
    if mutation == "unknown_runbook":
        plan["runbook_id"] = "unknown-runbook"
    elif mutation == "unknown_evidence":
        plan["preconditions"][0]["expected_sha256"] = "0" * 64
    elif mutation == "executable_content":
        plan["expected_effect"] = "Use https://example.invalid/run"
    else:
        now = "2026-08-04T08:01:00Z"
    assert proofread_recovery_plan(plan, now=now) == expected


@pytest.mark.parametrize(
    "field", ["shell", "sql", "command", "approval", "success", "credential"]
)
def test_recovery_candidate_schema_has_no_executable_or_authority_fields(field):
    plan = load_json(SCHEMA_EXAMPLES["recovery_plan"][1])
    plan[field] = "forbidden"
    assert errors(SCHEMA_EXAMPLES["recovery_plan"][0], plan)


@pytest.mark.parametrize(
    "update_class",
    [
        "application_dependency_build",
        "database_schema_migration",
        "reference_dataset",
        "operational_clinical_policy",
    ],
)
def test_d3_preserves_class_specific_command_canary_review_and_rollback(
    update_class,
):
    base = load_json(SCHEMA_EXAMPLES["update_promotion"][1])
    plan = promotion_plan_for_class(base, update_class)
    assert not errors(SCHEMA_EXAMPLES["update_promotion"][0], plan)
    assert plan["future_command_family"] == plan["activation"][
        "future_command_family"
    ]
    assert plan["shadow"]["authoritative_reads"] is False
    assert plan["review"]["pre_canary_review_required"] is True
    assert plan["review"]["post_canary_pre_activation_review_required"] is True
    assert plan["activation"]["performed"] is False
    assert plan["readback"]["success_claimed"] is False
    assert plan["last_known_good_rollback"]["currently_eligible"] is True


def test_database_class_requires_specific_barrier_and_restore_evidence():
    base = load_json(SCHEMA_EXAMPLES["update_promotion"][1])
    plan = promotion_plan_for_class(base, "database_schema_migration")
    assert plan["activation"]["class_specific_barrier"] == (
        "migration_transaction_or_maintenance_barrier"
    )
    assert {"backup_restore_evidence", "rollback_feasibility"} <= set(
        plan["validation"]["required_checks"]
    )
    plan["activation"]["class_specific_barrier"] = (
        "immutable_dataset_pointer_compare_and_swap"
    )
    assert errors(SCHEMA_EXAMPLES["update_promotion"][0], plan)


@pytest.mark.parametrize(
    "mutation",
    [
        "cross_class_command",
        "cross_class_canary",
        "review_downgrade",
        "shadow_serving",
        "unread_success",
        "withdrawn_lkg",
    ],
)
def test_d3_fail_closed_mutations_are_rejected(mutation):
    plan = load_json(SCHEMA_EXAMPLES["update_promotion"][1])
    if mutation == "cross_class_command":
        plan["future_command_family"] = "application_build_promotion"
    elif mutation == "cross_class_canary":
        plan["canary"]["kind"] = "single_disposable_instance"
    elif mutation == "review_downgrade":
        plan["review"]["minimum_reviewer_count"] = 1
    elif mutation == "shadow_serving":
        plan["shadow"]["authoritative_reads"] = True
    elif mutation == "unread_success":
        plan["readback"]["success_claimed"] = True
    else:
        plan["last_known_good_rollback"]["source_lifecycle"] = "withdrawn"
    assert errors(SCHEMA_EXAMPLES["update_promotion"][0], plan)


def test_d3_is_architecture_only_with_no_collected_approval_or_effect():
    plan = load_json(SCHEMA_EXAMPLES["update_promotion"][1])
    assert plan["current_state"] == "architecture_only_not_executable"
    assert plan["review"]["approvals_collected"] == 0
    assert plan["shadow"]["import_performed"] is False
    assert plan["canary"]["performed"] is False
    assert plan["activation_authorized"] is False
    assert plan["rollback_authorized"] is False


def test_api_spine_remains_asymmetric_and_access_ai_closed():
    assert load_json(CONTRACT)["api_spine"] == {
        "reads": "graphql_authorized_read_only_plan_status_and_readback",
        "commands": "rest_openapi_class_specific_separately_closed",
        "events": "committed_hints_require_fresh_authorized_read",
        "manifests": "declarative_evidence_never_command_authority",
        "access_ai": "closed",
    }

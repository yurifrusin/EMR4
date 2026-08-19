from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_provider_free_default_off_check_in_environment_manifest_secret_posture_architecture import (
    CONTRACT_PATH,
    CONTRACT_SCHEMA_PATH,
    EXPECTED_ADMISSION_ARCHITECTURE_SOURCE,
    EXPECTED_CONTRACT_DIGEST,
    EXPECTED_EVALUATOR_STEPS,
    EXPECTED_MANIFEST_FIELDS,
    EXPECTED_MANIFEST_SCHEMA_DIGEST,
    EXPECTED_READINESS_SOURCE,
    EXPECTED_SLOT_IDS,
    EXPECTED_SOURCE_HEAD,
    EXPECTED_SOURCES,
    EXPECTED_SUCCESSOR_RESOLUTION_SOURCE,
    EXPECTED_UNMOUNTED_KERNEL_SOURCE,
    FORBIDDEN_SECRET_FIELDS,
    MANIFEST_SCHEMA_PATH,
    _canonical_json_digest,
    build_report,
    build_synthetic_manifest,
    evaluate_manifest,
    hostile_contract_mutations,
    hostile_manifest_mutations,
    load_contract,
    load_contract_schema,
    load_manifest_schema,
    manifest_errors,
    source_errors,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture.md"
THREAT = ROOT / "docs/security/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture-threat-model-delta.md"
SCRIPT = ROOT / "scripts/raisa_provider_free_default_off_check_in_environment_manifest_secret_posture_architecture.py"
EVIDENCE = CONTRACT_PATH.parent / "provider-free-architecture-evidence.json"
REPORT = CONTRACT_PATH.parent / "architecture-report.md"


def test_contract_schema_semantics_sources_and_exact_report_pass() -> None:
    packet = load_contract()
    Draft202012Validator.check_schema(load_contract_schema())
    Draft202012Validator(load_contract_schema()).validate(packet)
    assert validate_contract(packet, verify_source_files=True) == []
    assert build_report(packet) == {
        "schema_version": "emr4.check-in-environment-manifest-secret-posture-architecture-report.v1",
        "status": "passed",
        "reasons": [],
        "source_head": EXPECTED_SOURCE_HEAD,
        "source_binding_count": 16,
        "manifest_schema_sha256": EXPECTED_MANIFEST_SCHEMA_DIGEST,
        "secret_slot_count": 3,
        "canonical_manifest_instance_count": 0,
        "current_secret_reference_count": 0,
        "current_rotation_evidence_count": 0,
        "contract_hostile_mutation_count": 268,
        "contract_hostile_mutation_escape_count": 0,
        "manifest_hostile_mutation_count": 69,
        "manifest_hostile_mutation_escape_count": 0,
        "missing_operational_evidence_outcome": {
            "outcome": "denied",
            "reason_code": "role_evidence_invalid",
        },
        "bounded_synthetic_shape_outcome": {
            "outcome": "satisfied",
            "reason_code": "evidence_gate_satisfied",
        },
        "ordinary_practice_enabled": False,
        "secret_value_used": False,
        "database_or_role_used": False,
        "product_or_configuration_changed": False,
        "provider_or_network_used": False,
    }


def test_exact_full_git_lineage_contract_digest_and_source_bindings() -> None:
    packet = load_contract()
    assert packet["source_head"] == EXPECTED_SOURCE_HEAD
    assert packet["accepted_successor_resolution_source"] == EXPECTED_SUCCESSOR_RESOLUTION_SOURCE
    assert packet["accepted_readiness_source"] == EXPECTED_READINESS_SOURCE
    assert packet["accepted_admission_architecture_source"] == EXPECTED_ADMISSION_ARCHITECTURE_SOURCE
    assert packet["accepted_unmounted_kernel_source"] == EXPECTED_UNMOUNTED_KERNEL_SOURCE
    assert _canonical_json_digest(packet) == EXPECTED_CONTRACT_DIGEST
    assert {row["path"]: row["sha256"] for row in packet["source_bindings"]} == EXPECTED_SOURCES
    assert source_errors(packet) == []


def test_current_population_is_empty_and_default_denied() -> None:
    posture = load_contract()["current_posture"]
    for field in (
        "ordinary_admission_records_present",
        "environment_manifest_instances_present",
        "selected_practice_bindings_present",
        "ordinary_runtime_role_bindings_present",
        "secret_reference_bindings_present",
        "operational_evidence_artifacts_present",
    ):
        assert posture[field] == 0
    assert posture["feature_default"] is False
    assert posture["synthetic_allowlist_default"] == []
    assert posture["secret_values_supplied"] is False
    assert posture["database_opened"] is False
    assert posture["product_configuration_changed"] is False
    assert posture["ordinary_practice_enabled"] is False
    assert posture["default_result"] == "deny_environment_manifest_absent"
    assert evaluate_manifest(
        None,
        evaluation_time="2026-08-20T00:00:00+10:00",
        operational_evidence_verified=False,
    ) == {"outcome": "denied", "reason_code": "manifest_absent"}


def test_future_manifest_schema_is_closed_and_synthetic_shape_is_non_operational() -> None:
    schema = load_manifest_schema()
    Draft202012Validator.check_schema(schema)
    sample = build_synthetic_manifest()
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(sample)
    assert manifest_errors(sample) == []
    assert list(sample) == EXPECTED_MANIFEST_FIELDS
    assert evaluate_manifest(
        sample,
        evaluation_time="2026-08-20T00:00:00+10:00",
        operational_evidence_verified=False,
    ) == {"outcome": "denied", "reason_code": "role_evidence_invalid"}
    assert load_contract()["evidence_gate_evaluator"]["may_admit_ordinary_practice"] is False


def test_runtime_role_is_exact_non_owner_nobypassrls_expectation_not_claim() -> None:
    role = load_contract()["runtime_role_profile"]
    assert role["logical_role_id"] == "appointment_check_in_ordinary_runtime_v1"
    assert role["non_owner_required"] is True
    assert role["nobypassrls_required"] is True
    assert role["product_relation_ownership_allowed"] is False
    assert role["cross_tenant_denial_attestation_required"] is True
    assert role["exact_environment_attestation_required"] is True
    assert role["role_created"] is False
    assert role["role_attested"] is False
    assert role["database_connected"] is False


def test_three_ordered_distinct_reference_only_slots_forbid_secret_values() -> None:
    packet = load_contract()
    profile = packet["secret_reference_profile"]
    assert [row["slot_id"] for row in profile["ordered_slots"]] == EXPECTED_SLOT_IDS
    assert set(profile["forbidden_field_names"]) == FORBIDDEN_SECRET_FIELDS
    assert all(row["value_allowed"] is False for row in profile["ordered_slots"])
    assert profile["reference_only"] is True
    assert profile["slot_reference_reuse_allowed"] is False
    assert profile["key_identifier_reuse_across_slots_allowed"] is False
    assert profile["cross_environment_reference_reuse_allowed"] is False
    assert profile["repository_secret_value_allowed"] is False
    assert profile["provider_endpoint_allowed"] is False
    sample = build_synthetic_manifest()
    hostile = copy.deepcopy(sample)
    hostile["secret_references"][0]["password"] = "not-allowed"
    assert any("forbidden_secret_field" in reason for reason in manifest_errors(hostile))


def test_rotation_evidence_is_exact_fresh_independent_and_cross_bound() -> None:
    profile = load_contract()["rotation_evidence_profile"]
    assert profile["ordered_slot_ids"] == EXPECTED_SLOT_IDS
    assert profile["required_for_each_slot"] is True
    assert profile["artifact_digest_is_evidence_digest_not_secret_material_digest"] is True
    assert profile["full_git_object_required"] is True
    assert profile["independent_verifier_required"] is True
    assert profile["self_verified_evidence_allowed"] is False
    assert profile["fresh_until_must_follow_observed_at"] is True
    assert profile["evaluation_time_must_precede_fresh_until"] is True
    assert profile["old_key_evidence_reuse_allowed"] is False
    sample = build_synthetic_manifest()
    hostile = copy.deepcopy(sample)
    hostile["rotation_evidence"][0]["environment_identifier"] = "env:wrong-environment"
    assert "rotation_environment_mismatch:database_connection_credential" in manifest_errors(hostile)


def test_break_glass_is_deny_only_and_never_increases_authority() -> None:
    profile = load_contract()["break_glass_profile"]
    assert profile["mode"] == "deny_only"
    assert profile["states"] == ["inactive", "engaged_deny", "retired"]
    assert profile["only_state_allowing_evidence_evaluation_to_continue"] == "inactive"
    for field in (
        "may_supply_secret",
        "may_skip_rotation",
        "may_attest_role",
        "may_activate_practice",
        "may_clear_global_kill_switch",
        "may_grant_command_authority",
        "automatic_clear_allowed",
        "last_known_good_fallback",
    ):
        assert profile[field] is False
    for state in ("engaged_deny", "retired"):
        sample = build_synthetic_manifest()
        sample["break_glass"]["state"] = state
        assert evaluate_manifest(
            sample,
            evaluation_time="2026-08-20T00:00:00+10:00",
            operational_evidence_verified=True,
        ) == {"outcome": "denied", "reason_code": "break_glass_not_inactive"}


def test_evaluator_order_has_no_secret_database_product_or_admission_capability() -> None:
    evaluator = load_contract()["evidence_gate_evaluator"]
    assert evaluator["ordered_steps"] == EXPECTED_EVALUATOR_STEPS
    assert evaluator["canonical_current_outcome"] == "denied"
    assert evaluator["canonical_current_reason_code"] == "manifest_absent"
    for field in (
        "may_admit_ordinary_practice",
        "may_execute_check_in",
        "may_connect_database",
        "may_resolve_secret",
        "may_create_or_change_role",
        "may_mutate_product_configuration",
    ):
        assert evaluator[field] is False


def test_seven_character_object_duplicate_reference_stale_and_wrong_environment_deny() -> None:
    cases: list[dict[str, Any]] = []
    abbreviated = build_synthetic_manifest()
    abbreviated["authority_git_object"] = EXPECTED_SOURCE_HEAD[:7]
    cases.append(abbreviated)
    duplicate = build_synthetic_manifest()
    duplicate["secret_references"][1]["secret_reference"] = duplicate["secret_references"][0]["secret_reference"]
    cases.append(duplicate)
    wrong_environment = build_synthetic_manifest()
    wrong_environment["rotation_evidence"][1]["environment_identifier"] = "env:wrong-environment"
    cases.append(wrong_environment)
    for case in cases:
        assert evaluate_manifest(
            case,
            evaluation_time="2026-08-20T00:00:00+10:00",
            operational_evidence_verified=True,
        )["outcome"] == "denied"
    stale = build_synthetic_manifest()
    assert evaluate_manifest(
        stale,
        evaluation_time="2026-12-02T00:00:00+10:00",
        operational_evidence_verified=True,
    ) == {"outcome": "denied", "reason_code": "manifest_stale"}


def test_all_hostile_contract_and_manifest_mutations_fail_closed() -> None:
    contract_mutants = hostile_contract_mutations(load_contract())
    assert len(contract_mutants) == 268
    assert [name for name, mutant in contract_mutants if not validate_contract(mutant)] == []
    manifest_mutants = hostile_manifest_mutations()
    assert len(manifest_mutants) == 69
    escapes = []
    for name, mutant in manifest_mutants:
        if evaluate_manifest(
            mutant,
            evaluation_time="2026-08-20T00:00:00+10:00",
            operational_evidence_verified=True,
        ) == {"outcome": "satisfied", "reason_code": "evidence_gate_satisfied"}:
            escapes.append(name)
    assert escapes == []


def test_every_declared_schema_object_is_closed() -> None:
    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                assert node.get("additionalProperties") is False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8")))
    visit(json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8")))


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
        "datetime",
        "hashlib",
        "json",
        "jsonschema",
        "pathlib",
        "typing",
    }
    assert imports.isdisjoint(
        {"app", "sqlalchemy", "psycopg", "requests", "httpx", "google", "socket", "subprocess"}
    )


def test_clockwork_is_live_single_owner_but_broker_has_no_secret_or_product_authority() -> None:
    clockwork = load_contract()["clockwork_boundary"]
    assert clockwork["governance_clockwork_status"] == "accepted_live_single_owner"
    assert clockwork["closeout_projection_owner"] == "clockwork"
    assert clockwork["full_git_objects_are_machine_resolved"] is True
    assert clockwork["manual_git_abbreviation_accepted"] is False
    assert clockwork["deepseek_native_harness_occupied_for_this_tranche"] is False
    assert clockwork["deepseek_broker_has_product_or_secret_authority"] is False
    assert clockwork["workflow_receipt_is_operational_or_product_authority"] is False


def test_every_closed_boundary_is_false_and_successor_is_not_authorized_now() -> None:
    packet = load_contract()
    assert all(value is False for value in packet["closed_boundaries"].values())
    successor = packet["successor"]
    assert successor["operation_id"] == "raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal"
    assert successor["authorized_now"] is False
    assert successor["ordinary_enablement_authorized"] is False
    assert successor["production_or_live_secret_authorized"] is False


def test_plan_design_and_threat_model_freeze_the_exact_boundary() -> None:
    text = " ".join(
        " ".join(path.read_text(encoding="utf-8").lower().split())
        for path in (PLAN, DESIGN, THREAT)
    )
    for phrase in (
        "provider-free",
        "default denial",
        "secret-ref:",
        "nobypassrls",
        "40-character",
        "rotation evidence",
        "deny-only",
        "break glass",
        "authored-synthetic",
        "deepseek",
        "clockwork",
        "protected-ref",
    ):
        assert phrase in text


def test_derived_evidence_matches_single_typed_reading_and_artifacts_exist() -> None:
    assert json.loads(EVIDENCE.read_text(encoding="utf-8")) == build_report()
    for path in (
        CONTRACT_PATH,
        CONTRACT_SCHEMA_PATH,
        MANIFEST_SCHEMA_PATH,
        PLAN,
        DESIGN,
        THREAT,
        SCRIPT,
        EVIDENCE,
        REPORT,
    ):
        assert path.is_file()

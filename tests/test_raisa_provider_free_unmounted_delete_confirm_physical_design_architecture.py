from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_unmounted_delete_confirm_physical_design_architecture
    as design,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-delete-confirm-physical-design-"
    "architecture-plan.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-delete-confirm-physical-"
    "design-architecture-threat-model-delta.md"
)


@pytest.fixture(scope="module")
def contract() -> dict:
    return json.loads(design.CONTRACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(design.SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def built_evidence() -> dict:
    return design.build_evidence()


def _walk_objects(node):
    """Yield every dict in a JSON-like structure."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_objects(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_objects(value)


def test_contract_is_closed_unmounted_and_not_implementation_authority(contract, schema):
    design.validate_schema(contract, schema)
    design.validate_contract_semantics(contract)
    assert contract["implementation_authorized"] is False
    assert contract["api_boundary"]["public_response_schema_edit_authorized"] is False
    assert contract["canonical_response"]["current_full_response_not_accepted"] is True
    assert contract["canonical_response"]["compatibility_or_version_transition"] == (
        "later_explicit_gate"
    )
    assert set(contract["forbidden"].values()) == {False}
    assert len(contract["forbidden"]) == 14


def test_schema_closes_every_object_with_additional_properties_false(schema):
    for obj in _walk_objects(schema):
        if obj.get("type") == "object":
            assert obj.get("additionalProperties") is False, obj.get("$id") or obj


def test_all_twenty_exact_source_hashes_pass(contract):
    observed = design.verify_source_bindings(contract)
    assert observed == design.EXPECTED_SOURCE_BINDINGS
    assert len(observed) == 20
    assert len(contract["source_bindings"]) == 20


def test_product_authority_fence_is_users_database_owned_generation(contract):
    fence = contract["product_authority_fence"]
    assert fence == design.EXPECTED_PRODUCT_AUTHORITY_FENCE
    assert fence["table"] == "users"
    assert fence["generation_column"] == "authority_generation"
    assert fence["postgresql_type"] == "BIGINT"
    assert fence["domain_minimum"] == 1
    assert fence["domain_maximum"] == 9223372036854775807
    assert fence["generation_owner"] == "postgresql"
    assert fence["submitted_generation_policy"] == "ignored_by_database"
    assert fence["synthetic_application_auth_relations_ineligible"] is True


def test_capability_relation_is_closed_normalized_and_grant_is_row_presence(contract):
    grants = contract["user_capability_grants"]
    assert grants == design.EXPECTED_USER_CAPABILITY_GRANTS
    assert grants["relation"] == "user_capability_grants"
    assert grants["primary_key"] == ["practice_id", "user_id", "capability_code"]
    assert grants["composite_foreign_key"] == ["practice_id", "user_id"]
    assert grants["admitted_capabilities"] == [
        "appointment.cancel.confirm",
        "appointment.read",
    ]
    assert grants["grant_semantics"] == "row_presence_is_grant_absence_is_denial"
    assert grants["wildcard_representable"] is False
    assert grants["automatic_grant_to_existing_users"] is False
    assert grants["cancel_does_not_imply_read"] is True


def test_authority_check_locks_fence_and_requires_signed_generation(contract):
    check = contract["authority_check"]
    assert check == design.EXPECTED_AUTHORITY_CHECK
    assert check["fence_lock_resource"] == "users"
    assert check["fence_lock_strength"] == "FOR SHARE"
    assert check["admitted_roles"] == [
        "Receptionist",
        "GP",
        "Nurse",
        "Admin",
        "PracticeOwner",
    ]
    assert "signed_authority_generation_equals_locked_current_generation" in check[
        "required_conditions"
    ]
    assert "exact_grant_appointment_cancel_confirm_exists" in check["required_conditions"]
    assert check["check_count"] == 2


def test_authority_migration_provisions_nothing_and_rollback_is_fail_closed(contract):
    migration = contract["authority_migration"]
    assert migration == design.EXPECTED_AUTHORITY_MIGRATION
    assert len(migration["phases"]) == 10
    assert migration["phases"][0] == "add_users_authority_generation_nullable_without_table_rewriting_default"
    assert migration["phases"][-1] == "retain_generation_server_default_for_new_users"
    assert migration["capability_rows_after_migration"] == 0
    assert migration["automatic_capability_grant"] is False
    rollback = contract["rollback_contract"]
    assert rollback == design.EXPECTED_ROLLBACK_CONTRACT
    assert rollback["schema_only_before_first_use"] is True
    assert rollback["after_first_use"] == "forward_only"
    assert rollback["automatic_downgrade_after_first_use"] == "fail_closed"


def test_appointment_truth_reuses_database_owned_positive_state_version(contract):
    truth = contract["appointment_truth"]
    assert truth == design.EXPECTED_APPOINTMENT_TRUTH
    assert truth["table"] == "appointments"
    assert truth["state_version_column"] == "appointment_state_version"
    assert truth["postgresql_type"] == "BIGINT"
    assert truth["minimum"] == truth["insert_value"] == 1
    assert truth["state_version_owner"] == "postgresql_database_owned_positive"
    assert truth["new_version_identity_added"] is False
    assert truth["new_timestamp_identity_added"] is False
    assert truth["status"] == "Cancelled"
    assert truth["mandatory_structured_reason"] is True


def test_status_reason_codes_are_exact_and_legacy_is_rejected(contract):
    reasons = contract["status_reason_codes"]
    assert reasons == design.EXPECTED_STATUS_REASON_CODES
    assert reasons["accepted_codes"] == [
        "PATIENT_CANCELLED",
        "PATIENT_RESCHEDULED",
        "PATIENT_UNWELL",
        "PATIENT_TRANSPORT",
        "PRACTITIONER_UNAVAILABLE",
        "CLINIC_OPERATIONAL",
        "CLINIC_RESCHEDULED",
        "ADMIN_ERROR",
        "DUPLICATE_BOOKING",
        "OTHER",
    ]
    assert "LEGACY_UNCLASSIFIED" in reasons["rejected_codes"]
    assert reasons["cancellation_reason_max_length"] == 500
    assert reasons["confirmed_warnings"] == "human_acknowledgement_set_not_reason"


def test_private_receipt_is_family_qualified_v1_with_one_additive_generation(contract):
    receipt = contract["private_completed_receipt"]
    assert receipt == design.EXPECTED_PRIVATE_COMPLETED_RECEIPT
    assert receipt["contract_version"] == 1
    assert receipt["family_qualified"] is True
    assert receipt["single_additive_field"]["name"] == "authority_generation"
    assert receipt["existing_reused_fields"] == [
        "completed_receipt_version",
        "session_binding_digest",
        "pre_state_version",
        "post_state_version",
        "response_body_canonical_bytes",
    ]
    assert receipt["legacy_rows"] == "remain_null_not_inferred_or_backfilled"
    assert receipt["legacy_replay_outcome"] == "legacy_receipt_not_replayable"


def test_session_binding_is_opaque_domain_separated_hmac(contract):
    session = contract["private_completed_receipt"]["session_binding"]
    assert session["algorithm"] == "HMAC-SHA-256"
    assert session["stored_form"] == "32_raw_digest_bytes"
    assert session["domain_separator"] == "appointment-delete-session:v1"
    assert session["message_fields"] == [
        "practice_id",
        "actor_user_id",
        "authenticated_session_id",
    ]
    assert session["raw_session_stored"] is False
    assert session["secret_stored"] is False


def test_canonical_response_is_exactly_six_fields_in_fixed_order(contract):
    response = contract["canonical_response"]
    assert response == design.EXPECTED_CANONICAL_RESPONSE
    assert response["fields_in_order"] == [
        "appointment_id",
        "status",
        "status_reason_code",
        "cancellation_reason",
        "waiting_area_id",
        "warning_codes",
    ]
    assert response["status_constant"] == "Cancelled"
    assert response["jsonb_is_delivery_authority"] is False
    assert response["digest"] == "lowercase_hex_sha256_of_exact_stored_bytes"
    assert "without_reserialization" in response["initial_delivery"]
    assert "without_reserialization" in response["replay_delivery"]
    assert response["current_full_response_not_accepted"] is True


def test_attributable_audit_is_versioned_and_separates_warnings_from_evidence(contract):
    audit = contract["attributable_audit"]
    assert audit == design.EXPECTED_ATTRIBUTABLE_AUDIT
    assert audit["audit_contract_version"] == 1
    assert len(audit["additive_fields"]) == 7
    assert audit["confirmed_warnings"] == "stores_only_exact_human_warning_acknowledgements"
    assert audit["audit_evidence_codes"] == (
        "stores_only_bounded_internal_evidence_codes_as_json_array"
    )
    assert audit["legacy_merged_array_not_reinterpreted"] is True
    assert audit["raw_authenticated_session_id_in_audit"] is False
    assert "post_equals_pre_plus_one" in audit["v1_required"]
    assert "waiting_area_after_id_null" in audit["v1_required"]


def test_transaction_is_read_committed_single_with_2000ms_cumulative_budget(contract):
    transaction = contract["transaction_contract"]
    assert transaction == design.EXPECTED_TRANSACTION_CONTRACT
    assert transaction["owner"] == "backend_delete_confirm_kernel"
    assert transaction["isolation"] == "READ COMMITTED"
    assert transaction["single_transaction"] is True
    assert transaction["cumulative_lock_wait_budget_ms"] == 2000
    assert "never_resets" in transaction["budget_policy"]
    assert transaction["nowait"] is False
    assert transaction["skip_locked"] is False
    assert transaction["advisory_locks"] is False
    assert transaction["hidden_effect_retries"] is False


def test_lock_order_and_strength_are_exact(contract):
    transaction = contract["transaction_contract"]
    assert transaction["locks"] == design.EXPECTED_TRANSACTION_CONTRACT["locks"]
    assert [item["resource"] for item in transaction["locks"]] == [
        "users_authority_fence",
        "appointment",
        "idempotency_record",
    ]
    assert [item["strength"] for item in transaction["locks"]] == [
        "FOR SHARE",
        "FOR UPDATE",
        "FOR UPDATE",
    ]
    assert [item["position"] for item in transaction["locks"]] == [1, 2, 3]


def test_authority_checks_precede_disclosure_replay_and_effect(contract):
    trace = contract["transaction_contract"]["decision_trace"]
    assert trace == design.EXPECTED_TRANSACTION_CONTRACT["decision_trace"]
    assert len(trace) == 15
    first_authority = trace.index(
        "first_complete_current_authority_and_signed_generation_check"
    )
    idempotency_lock = trace.index(
        "select_exact_idempotency_row_for_update_or_insert_target_bound_conflict_do_nothing_returning_then_lock_winning_row_without_releasing_appointment_lock"
    )
    second_authority = trace.index(
        "repeat_complete_current_authority_check_while_every_lock_held"
    )
    classification = trace.index(
        "classify_exact_actor_role_generation_session_operation_route_target_key_and_request_bindings"
    )
    replay = trace.index(
        "replay_only_complete_integrity_valid_family_qualified_v1_receipt"
    )
    stage = trace.index(
        "stage_one_appointment_soft_cancel_one_versioned_delete_audit_and_one_complete_private_receipt"
    )
    assert first_authority < idempotency_lock < second_authority
    assert second_authority < classification < replay < stage


def test_replay_requires_generation_session_byte_integrity_and_current_authority(contract):
    required = set(
        contract["transaction_contract"]["same_digest_replay_requires"]
    )
    assert {
        "current_authority",
        "authority_generation_match",
        "session_digest_match",
        "stored_byte_digest_valid",
        "completed_receipt_version_one",
        "request_digest_match",
        "route_match",
    } <= required
    assert "authority_revoked" in contract["transaction_contract"][
        "non_disclosing_outcomes"
    ]
    assert "legacy_receipt_not_replayable" in contract["transaction_contract"][
        "non_disclosing_outcomes"
    ]


def test_fresh_readback_is_reconciliation_only_and_never_proves_commit(contract):
    readback = contract["fresh_readback"]
    assert readback == design.EXPECTED_FRESH_READBACK
    assert readback["begins_after_commit_only"] is True
    assert readback["new_transaction"] is True
    assert readback["never_proves_commit"] is True
    assert "exact_appointment_read_grant" in readback["requires"]
    assert readback["evidence_role"] == "reconciliation_only"
    assert readback["command_response_contains_no_display_data"] is True
    assert "patient" in readback["excluded_display_data"]


def test_non_authority_surfaces_are_inert_and_cannot_grant(contract):
    surfaces = contract["non_authority_surfaces"]
    assert surfaces == design.EXPECTED_NON_AUTHORITY_SURFACES
    for key in ("raw_compatibility_delete", "status_family_cancellation_path"):
        assert "no_authority" in surfaces[key]
    assert surfaces["model_output"] == "inert_proposal_no_command_authority"
    assert surfaces["context_fabric"] == "inert_proposal_no_command_authority"
    assert surfaces["channel_output"] == "inert_proposal_no_command_authority"
    assert surfaces["events"] == "non_authoritative_acceleration_hints"
    assert surfaces["graphql"] == "read_only"
    assert surfaces["wildcard"] == "not_representable"


def test_worker_allocation_keeps_deepseek_mechanical_and_gemini_veto_only(contract):
    allocation = contract["worker_allocation"]
    assert allocation == design.EXPECTED_WORKER_ALLOCATION
    assert allocation["deepseek_role"] == "bounded_mechanical_implementation_only"
    assert allocation["deepseek_authority"]["acceptance"] is False
    assert allocation["deepseek_authority"]["integration"] is False
    assert allocation["deepseek_authority"]["protected_ref"] is False
    assert allocation["gemini_verifier"] == "gemini_3_6_flash_high"
    assert allocation["gemini_role"] == "fresh_independent_veto_exact_candidate"
    assert allocation["gemini_authority"]["acceptance"] is False
    assert "not_yet_admitted" in allocation["gemini_3_7_flash_high"]


def test_all_hostile_mutations_fail_closed(built_evidence):
    hostile = built_evidence["hostile_mutations"]
    assert hostile["attempted"] >= 60
    assert hostile["attempted"] == 166
    assert hostile["rejected"] == hostile["attempted"]


def test_every_hostile_family_named_by_the_plan_is_represented():
    names = {name for name, _ in design.hostile_mutations()}
    for family in design.HOSTILE_FAMILY_NAMES:
        assert any(family in name for name in names), family


def test_committed_evidence_equals_fresh_builder_output(built_evidence):
    committed = json.loads(design.EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert committed == built_evidence
    assert committed["architecture_facts"]["authority_check_count"] == 2
    assert committed["architecture_facts"]["canonical_field_count"] == 6
    assert committed["architecture_facts"]["cumulative_lock_wait_budget_ms"] == 2000
    assert committed["architecture_facts"]["readback_never_proves_commit"] is True
    assert committed["implementation_authorized"] is False


def test_verify_evidence_admits_the_frozen_evidence(built_evidence):
    admitted = design.verify_evidence()
    assert admitted == built_evidence


def test_validator_imports_no_application_database_or_provider_modules():
    source = Path(design.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(name == "app" or name.startswith("app.") for name in imported)
    assert not any(
        fragment in name
        for name in imported
        for fragment in ("sqlalchemy", "psycopg", "alembic", "google", "vertex", "requests", "httpx")
    )


def test_validator_has_no_executable_runtime_or_mutation_path():
    source = Path(design.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_fragments = (
        "write_text",
        "write_bytes",
        "subprocess",
        "Popen",
        "os.system",
        "os.remove",
        "os.rename",
        "shutil",
        "socket",
        "sqlalchemy",
        "psycopg",
        "alembic",
        "create_engine",
        "execute",
        "exec",
        "eval",
        "importlib",
        "requests",
        "httpx",
        "boto3",
        "paramiko",
        "getpass",
    )
    identifiers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
        elif isinstance(node, ast.Import):
            identifiers.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            identifiers.add(node.module)
            identifiers.update(alias.name for alias in node.names)
    for identifier in identifiers:
        for fragment in forbidden_fragments:
            assert fragment not in identifier, (fragment, identifier)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            assert name not in {"open", "exec", "eval"}, name


def test_plan_and_threat_model_freeze_unmounted_next_work():
    plan = PLAN.read_text(encoding="utf-8")
    compact_plan = " ".join(plan.split())
    threat = THREAT.read_text(encoding="utf-8")
    compact_threat = " ".join(threat.split())
    for phrase in (
        "material authority / transaction architecture / Extra High",
        "one PostgreSQL `READ COMMITTED`",
        "`FOR SHARE`",
        "`FOR UPDATE`",
        "2000 ms",
        "confirmAppointmentDeleteProposal",
        "appointment.cancel.confirm",
        "appointment.read",
        "LEGACY_UNCLASSIFIED",
        "legacy_receipt_not_replayable",
        "implementation_authorized",
        "grant no capability and mount no consumer",
        "provider-free unmounted delete-confirm physical schema-and-transaction scaffold",
    ):
        assert phrase in compact_plan, phrase
    for phrase in (
        "synthetic relations remain ineligible",
        "Capability table is created empty; no automatic or role-derived grant is permitted.",
        "Only a family-qualified complete v1 receipt is replayable",
        "Canonical bytes are delivery authority",
        "Enforce one cumulative 2000 ms deadline and apply only its remaining positive budget.",
        "separately authorised fresh readback is reconciliation only",
        "`implementation_authorized` remains false",
    ):
        assert phrase in compact_threat, phrase

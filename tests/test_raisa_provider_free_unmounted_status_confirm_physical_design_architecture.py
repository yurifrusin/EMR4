from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_unmounted_status_confirm_physical_design_architecture
    as design,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-status-confirm-physical-design-"
    "architecture-plan.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-status-confirm-physical-"
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


def test_contract_is_closed_unmounted_and_not_implementation_authority(contract, schema):
    design.validate_schema(contract, schema)
    design.validate_contract_semantics(contract)
    assert contract["implementation_authorized"] is False
    assert set(contract["forbidden"].values()) == {False}


def test_all_eleven_exact_source_hashes_pass(contract):
    observed = design.verify_source_bindings(contract)
    assert observed == design.EXPECTED_SOURCE_BINDINGS
    assert len(observed) == 11


def test_state_version_is_positive_bigint_and_database_owned(contract):
    version = contract["appointment_state_version"]
    assert version == design.EXPECTED_STATE_VERSION
    assert version["postgresql_type"] == "BIGINT"
    assert version["minimum"] == version["insert_value"] == 1
    assert version["increment_owner"] == "postgresql_before_update_trigger"
    assert version["timestamp_substitution"] is False
    assert version["trigger_is_watcher_or_event"] is False


def test_migration_uses_cutover_baseline_and_forward_only_post_adoption(contract):
    migration = contract["migration_contract"]
    assert migration == design.EXPECTED_MIGRATION
    assert migration["phases"][0] == "add_nullable_bigint_without_default"
    assert migration["phases"][-1] == "expose_version_only_after_all_prior_phases"
    assert migration["historical_backfill_claim"].startswith("cutover_baseline")
    assert migration["automatic_downgrade_after_first_v1_receipt"] is False


def test_private_receipt_is_versioned_and_never_fabricates_legacy_replay(contract):
    receipt = contract["private_completed_receipt"]
    assert receipt["contract_version"] == 1
    assert receipt["additive_fields"] == design.EXPECTED_ADDITIVE_FIELDS
    assert receipt["legacy_backfill"] == "none"
    assert receipt["legacy_replay_outcome"] == "legacy_receipt_not_replayable"
    assert receipt["completed_v1_constraints"] == design.EXPECTED_RECEIPT_CONSTRAINTS


def test_session_binding_is_opaque_domain_separated_hmac(contract):
    session = contract["private_completed_receipt"]["session_binding"]
    assert session["algorithm"] == "HMAC-SHA-256"
    assert session["stored_form"] == "32_raw_digest_bytes"
    assert session["domain_separator"] == "appointment-status-session:v1"
    assert session["message_fields"] == [
        "practice_id",
        "actor_user_id",
        "authenticated_session_id",
    ]
    assert session["raw_session_stored"] is False
    assert session["secret_stored"] is False


def test_stored_canonical_bytes_are_the_only_delivery_authority(contract):
    response = contract["canonical_response"]
    assert response == design.EXPECTED_CANONICAL_RESPONSE
    assert response["jsonb_is_delivery_authority"] is False
    assert response["fields_in_order"] == [
        "appointment_id",
        "status",
        "status_reason_code",
        "waiting_area_id",
        "warning_codes",
    ]
    assert "without_reserialization" in response["initial_delivery"]
    assert "without_reserialization" in response["replay_delivery"]
    assert response["integrity_failure"] == "release_no_body_and_fail_closed"


def test_lock_order_and_strength_are_exact(contract):
    transaction = contract["transaction_contract"]
    assert transaction["locks"] == design.EXPECTED_LOCKS
    assert [item["resource"] for item in transaction["locks"]] == [
        "practice",
        "appointment",
        "idempotency_record",
    ]
    assert [item["strength"] for item in transaction["locks"]] == [
        "FOR SHARE",
        "FOR UPDATE",
        "FOR UPDATE",
    ]


def test_authority_and_target_precede_idempotency_disclosure(contract):
    trace = contract["transaction_contract"]["decision_trace"]
    assert trace == design.EXPECTED_TRACE
    target_stop = trace.index(
        "lock_practice_scoped_appointment_or_stop_before_idempotency_access"
    )
    first_authority = trace.index("check_current_authority_before_idempotency_insert")
    idempotency_lock = trace.index(
        "lock_existing_idempotency_or_insert_target_bound_in_progress_row"
    )
    second_authority = trace.index(
        "recheck_current_authority_while_all_locks_held"
    )
    classification = trace.index(
        "classify_exact_operation_route_target_actor_role_request_and_session_bindings"
    )
    assert target_stop < first_authority < idempotency_lock < second_authority
    assert second_authority < classification


def test_lock_wait_and_failure_policy_have_no_hidden_retry(contract):
    wait = contract["transaction_contract"]["lock_wait"]
    assert wait == {
        "policy": "positive_bounded_blocking",
        "nowait": False,
        "skip_locked": False,
        "same_budget_for_all_locks": True,
        "hidden_effect_retry": False,
    }
    failure = contract["failure_policy"]
    assert failure["server_effect_retry"] is False
    assert set(failure["atomic_write_set"]) == {
        "appointment_mutation",
        "attributable_audit",
        "completed_v1_receipt",
    }


def test_replay_requires_current_authority_session_and_byte_integrity(contract):
    required = set(
        contract["transaction_contract"]["same_digest_replay_requires"]
    )
    assert {
        "current_authority",
        "session_binding_digest_match",
        "stored_byte_digest_valid",
        "completed_receipt_version_one",
        "request_digest_match",
    } <= required
    assert "authority_revoked" in contract["transaction_contract"][
        "non_disclosing_outcomes"
    ]


def test_api_spine_boundary_keeps_public_graphql_and_events_closed(contract):
    boundary = contract["api_boundary"]
    assert boundary == design.EXPECTED_API_BOUNDARY
    assert boundary["operation_id"] == "confirmAppointmentStatusProposal"
    assert boundary["route_family"] == "status-confirm"
    assert boundary["public_response_schema_changed"] is False
    assert boundary["private_receipt_fields_publicly_mapped"] is False
    assert boundary["graphql_mutation_authority"] is False
    assert boundary["event_command_authority"] is False


def test_all_hostile_mutations_fail_closed(built_evidence):
    hostile = built_evidence["hostile_mutations"]
    assert hostile["attempted"] >= 50
    assert hostile["attempted"] == 91
    assert hostile["rejected"] == hostile["attempted"]


def test_committed_evidence_equals_fresh_builder_output(built_evidence):
    committed = json.loads(design.EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert committed == built_evidence
    assert committed["architecture_facts"]["authority_check_count"] == 2
    assert committed["architecture_facts"]["legacy_receipts_replayable"] is False
    assert committed["implementation_authorized"] is False


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
        for fragment in ("sqlalchemy", "psycopg", "google", "vertex")
    )


def test_plan_and_threat_model_freeze_unmounted_next_work():
    plan = PLAN.read_text(encoding="utf-8")
    compact_plan = " ".join(plan.split())
    threat = THREAT.read_text(encoding="utf-8")
    compact_threat = " ".join(threat.split())
    for phrase in (
        "material architecture / Extra High",
        "PostgreSQL, not route code, owns increments",
        "Existing rows remain",
        "legacy_receipt_not_replayable",
        "one PostgreSQL `READ COMMITTED`",
        "`FOR SHARE`",
        "`FOR UPDATE`",
        "implementation_authorized` remains false",
        "provider-free unmounted status-confirm physical schema-and-transaction scaffold",
    ):
        assert phrase in compact_plan
    assert "synchronous row invariant" in compact_threat
    assert "single atomic committed truth" in compact_threat
    assert (
        "No application/model/migration/service/route edit or import"
        in compact_threat
    )

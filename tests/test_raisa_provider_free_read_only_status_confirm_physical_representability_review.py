from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_read_only_status_confirm_physical_representability_review
    as review,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = (
    ROOT
    / "docs/raisa-provider-free-read-only-status-confirm-physical-"
    "representability-review-plan.md"
)
THREAT_PATH = (
    ROOT
    / "docs/security/raisa-provider-free-read-only-status-confirm-physical-"
    "representability-review-threat-model-delta.md"
)
INCIDENT_PATH = (
    ROOT
    / "orchestration/agent_inbox/codex/raisa-status-confirm-physical-"
    "representability-protected-metadata-scope-incident.json"
)


@pytest.fixture(scope="module")
def contract() -> dict:
    return json.loads(review.CONTRACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(review.SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def built_evidence() -> dict:
    return review.build_evidence()


def test_contract_is_closed_and_implementation_is_not_admitted(contract, schema):
    review.validate_schema(contract, schema)
    review.validate_contract_semantics(contract)
    assert contract["overall_verdict"] == "implementation_not_admitted"
    assert set(contract["forbidden"].values()) == {False}


def test_all_eleven_exact_source_hashes_pass(contract):
    observed = review.verify_source_bindings(contract)
    assert observed == review.EXPECTED_SOURCE_BINDINGS
    assert len(observed) == 11


def test_only_the_six_frozen_physical_api_sources_are_cited(contract):
    cited = {
        observation["path"]
        for domain in contract["domains"]
        for observation in domain["current_observations"]
    }
    assert cited <= review.PHYSICAL_SOURCE_PATHS
    assert {
        "app/models/appointments.py",
        "app/services/appointment_idempotency.py",
        "docs/api-spine/openapi/appointment-commands.yaml",
    } <= cited


def test_all_three_domains_require_additive_change(contract):
    assert [domain["id"] for domain in contract["domains"]] == (
        review.EXPECTED_DOMAIN_IDS
    )
    assert {domain["verdict"] for domain in contract["domains"]} == {
        "representable_with_additive_change"
    }


def test_state_version_is_absent_and_timestamp_substitution_is_rejected(
    built_evidence,
):
    observations = built_evidence["physical_observations"]
    assert observations["appointment_state_version_absent"] is True
    assert observations["appointment_created_at_not_used_as_version"] is True
    domain = next(
        item
        for item in json.loads(review.CONTRACT_PATH.read_text(encoding="utf-8"))[
            "domains"
        ]
        if item["id"] == "locked_state_version"
    )
    assert "created_at" in domain["current_observations"][0]["fact"]
    assert "not an admissible substitute" in domain["current_observations"][0][
        "fact"
    ]


def test_private_receipt_has_thirteen_primitives_and_four_additive_gaps(
    built_evidence,
):
    observations = built_evidence["physical_observations"]
    assert observations["receipt_existing_field_count"] == 13
    assert observations["receipt_additive_gap_count"] == 4
    assert observations["response_json_and_canonical_hash_stored"] is True
    assert observations["audit_correlation_primitives_present"] is True


def test_public_envelope_stays_separate_from_private_receipt(contract):
    receipt = next(item for item in contract["domains"] if item["id"] == "private_completed_receipt")
    joined = " ".join(
        [item["fact"] for item in receipt["current_observations"]]
        + receipt["additive_requirements"]
        + receipt["deliberately_unselected"]
    ).lower()
    assert "public result envelope is closed" in joined
    assert "opaque session-binding digest" in joined
    assert "stored canonical public response bytes" in joined
    assert "pre-state version" in joined
    assert "post-state version" in joined


def test_existing_lock_is_idempotency_only_and_in_the_wrong_outer_order(
    built_evidence,
):
    observations = built_evidence["physical_observations"]
    assert observations["idempotency_insert_precedes_only_row_lock"] is True
    assert observations["idempotency_lock_precedes_conflict_and_replay"] is True
    lock_domain = next(
        item
        for item in json.loads(review.CONTRACT_PATH.read_text(encoding="utf-8"))[
            "domains"
        ]
        if item["id"] == "ordered_lock_boundary"
    )
    requirements = set(lock_domain["additive_requirements"])
    assert "practice lock before appointment lock" in requirements
    assert "idempotency lock after appointment lock" in requirements
    assert "current authority recheck before conflict/replay classification" in requirements


def test_migration_primitives_do_not_select_a_future_design(contract):
    assert review.verify_physical_observations()[
        "additive_migration_primitive_present"
    ] is True
    joined = " ".join(
        choice
        for domain in contract["domains"]
        for choice in domain["deliberately_unselected"]
    ).lower()
    for phrase in (
        "physical column type",
        "backfill",
        "migration revision",
        "constraint form",
        "practice mapping/query expression",
        "isolation level",
    ):
        assert phrase in joined


def test_committed_evidence_equals_fresh_builder_output(built_evidence):
    committed = json.loads(review.EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert committed == built_evidence
    assert set(committed["domain_verdicts"].values()) == {
        "representable_with_additive_change"
    }


def test_all_hostile_mutations_fail_closed(built_evidence):
    hostile = built_evidence["hostile_mutations"]
    assert hostile["attempted"] >= 30
    assert hostile["rejected"] == hostile["attempted"]


def test_review_script_does_not_import_application_or_database_modules():
    source = Path(review.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(name == "app" or name.startswith("app.") for name in imported)
    assert not any("sqlalchemy" in name or "psycopg" in name for name in imported)


def test_aer_0292_is_sanitized_and_precedes_the_review_plan():
    incident = json.loads(INCIDENT_PATH.read_text(encoding="utf-8"))
    assert incident["incident_id"] == "AER-0292"
    assert incident["status"] == "corrected"
    assert incident["effects"]["protected_content_opened"] is False
    assert incident["effects"]["repository_file_mutated_by_query"] is False
    assert "exact already-known non-protected paths" in incident["correction"]


def test_plan_and_threat_model_keep_the_next_architecture_unmounted():
    plan = PLAN_PATH.read_text(encoding="utf-8")
    threat = THREAT_PATH.read_text(encoding="utf-8")
    assert "Only these exact non-protected artifacts" in plan
    assert "overall verdict is `implementation_not_admitted`" in plan
    assert "at least thirty hostile changes" in plan
    assert "provider-free unmounted status-confirm physical design" in plan
    assert "cannot edit or execute application or database" in plan
    assert "selects no implementation" in threat
    assert "No application or migration edit/import" in threat

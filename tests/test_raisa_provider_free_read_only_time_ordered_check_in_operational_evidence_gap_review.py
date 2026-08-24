from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from scripts import (
    raisa_provider_free_read_only_time_ordered_check_in_operational_evidence_gap_review as review,
)


ROOT = Path(__file__).resolve().parents[1]


def test_contract_and_evidence_schemas_are_closed_and_valid() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    contract_schema = review.load_json(ROOT, f"{review.BASE}/contract.schema.json")
    evidence_schema = review.load_json(ROOT, f"{review.BASE}/evidence.schema.json")
    Draft202012Validator.check_schema(contract_schema)
    Draft202012Validator.check_schema(evidence_schema)
    assert list(Draft202012Validator(contract_schema).iter_errors(contract)) == []
    evidence = review.run_review(ROOT, release=False)
    assert list(Draft202012Validator(evidence_schema).iter_errors(evidence)) == []


def test_all_bindings_are_full_ancestral_and_byte_exact() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    objects = [contract["planning_source"]] + [
        item["git_object"] for item in contract["accepted_sources"]
    ]
    assert all(re.fullmatch(r"[0-9a-f]{40}", value) for value in objects)
    assert all(review.git_object_is_ancestor(ROOT, value) for value in objects)
    assert all(
        review.canonical_sha256(ROOT, item["path"]) == item["sha256"]
        for item in contract["accepted_sources"]
    )


def test_temporal_claim_ceiling_and_coverage_are_not_promoted() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["temporal_reading"] == {
        "scenario_count": 30,
        "cross_family_pair_count": 74,
        "claim_ceiling": "minimum_pairwise_authored_synthetic_in_memory_adapter_composition_and_precedence_only",
        "unmasked_witness_count": 16,
        "physical_capability_claimed": False,
    }


def test_existing_physical_evidence_is_not_scheduled_for_repetition() -> None:
    gap = review.run_review(ROOT, release=False)["gap_classification"]
    assert gap["unknown_response_rehearsal_repeated"] is False
    assert gap["runtime_role_tenant_rehearsal_repeated"] is False
    assert gap["ordinary_admission_prerequisite_reopened"] is False
    assert gap["unbacked_temporal_transition_count"] == 2


def test_only_post_proposal_authority_and_area_revalidation_remain() -> None:
    gap = review.run_review(ROOT, release=False)["gap_classification"]
    assert gap["recommendation"] == review.RECOMMENDATIONS[1]
    assert gap["next_operation"] == review.NEXT_OPERATION
    assert gap["next_scope"] == [
        "receptionist_role_revoked_after_proposal_before_confirmation",
        "assigned_waiting_area_deactivated_after_proposal_before_confirmation",
    ]


def test_admission_boundary_remains_11_0_1_and_external() -> None:
    assert review.run_review(ROOT, release=False)["admission_boundary"] == {
        "readiness": {
            "satisfied": 11,
            "blocking_gap": 0,
            "operational_evidence_gap": 1,
        },
        "repository_prerequisites_remaining": 0,
        "external_facts_absent": 6,
        "ordinary_admission_releases": 0,
        "verdict": "not_ready_for_ordinary_practice_admission",
    }


def test_hostile_mutations_reject_short_ids_and_vocabulary_drift() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    short = copy.deepcopy(contract)
    short["accepted_sources"][0]["git_object"] = "203f297"
    with pytest.raises(review.ContractError):
        review.validate_contract(short, ROOT, check_git=False)
    drift = copy.deepcopy(contract)
    drift["recommendation_vocabulary"][1] = "something_descriptive"
    with pytest.raises(review.ContractError):
        review.validate_contract(drift, ROOT, check_git=False)
    assert review.hostile_mutations(contract, ROOT) >= 40


def test_release_is_idempotent_and_schema_valid() -> None:
    evidence = review.run_review(ROOT, release=False)
    expected = json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    assert (ROOT / review.EVIDENCE_PATH).read_text(encoding="utf-8") == expected
    assert (ROOT / review.REPORT_PATH).read_text(encoding="utf-8") == review.render_report(evidence)


def test_reviewer_has_no_runtime_network_or_historical_data_capability() -> None:
    source = (
        ROOT
        / "scripts/raisa_provider_free_read_only_time_ordered_check_in_operational_evidence_gap_review.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "from app",
        "import app",
        "import docker",
        "import psycopg",
        "import sqlalchemy",
        "import requests",
        "import httpx",
        "import socket",
        "historical_diary",
        "snapshot_trove",
    )
    assert all(value not in source for value in forbidden)


def test_plan_and_threat_keep_execution_and_protected_surfaces_closed() -> None:
    plan = (
        ROOT
        / "docs/raisa-provider-free-read-only-authored-synthetic-time-ordered-canonical-check-in-context-operational-evidence-gap-review-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        ROOT
        / "docs/security/raisa-provider-free-read-only-authored-synthetic-time-ordered-canonical-check-in-context-operational-evidence-gap-review-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    assert "40-character" in plan and "40-character" in threat
    assert "docs/branding/" in plan
    for text in (plan, threat):
        assert "ordinary" in text.lower()
        assert "protected-ref" in text

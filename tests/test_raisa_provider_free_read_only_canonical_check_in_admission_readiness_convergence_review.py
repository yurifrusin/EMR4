from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from scripts import (
    raisa_provider_free_read_only_canonical_check_in_admission_readiness_convergence_review as review,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_NAME = review.__name__


def test_contract_matches_schema_and_exact_shape() -> None:
    contract = json.loads((ROOT / review.CONTRACT_PATH).read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / review.BASE / "contract.schema.json").read_text(encoding="utf-8")
    )
    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=str)
    assert errors == []
    assert len(contract["inputs"]) == 20
    assert len(contract["dimensions"]) == 12
    assert len(contract["accepted_git_objects"]) == 11


def test_every_git_binding_is_full_and_ancestral() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    bindings = {
        "planning_source": contract["planning_source"],
        **contract["accepted_git_objects"],
    }
    assert all(re.fullmatch(r"[0-9a-f]{40}", value) for value in bindings.values())
    assert all(
        review.git_object_is_ancestor(ROOT, value) for value in bindings.values()
    )


def test_review_produces_the_frozen_10_0_2_not_ready_verdict() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["result"] == review.RESULT
    assert evidence["dimension_counts"] == {
        "satisfied": 10,
        "blocking_gap": 0,
        "operational_evidence_gap": 2,
    }
    assert evidence["blocking_gaps"] == []
    assert evidence["operational_evidence_gaps"] == list(review.REQUIRED_OPEN_GAPS)
    assert evidence["verdict"] == "not_ready_for_ordinary_practice_admission"


def test_dimension_order_and_closed_vocabulary_are_exact() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert [item["order"] for item in evidence["dimensions"]] == list(range(1, 13))
    assert [item["id"] for item in evidence["dimensions"]] == [
        item[1] for item in review.DIMENSIONS
    ]
    assert {item["classification"] for item in evidence["dimensions"]} <= set(
        review.CLASSIFICATIONS
    )
    assert [item["classification"] for item in evidence["dimensions"]] == [
        item[2] for item in review.DIMENSIONS
    ]


def test_four_original_gaps_advance_only_on_exact_descendant_basis() -> None:
    evidence = review.run_review(ROOT, release=False)
    indexed = {item["order"]: item for item in evidence["dimensions"]}
    assert indexed[2]["basis"] == "accepted_admission_kernel"
    assert indexed[5]["basis"] == "accepted_disposable_postgresql_attestation"
    assert indexed[9]["basis"] == "accepted_default_off_runbook"
    assert indexed[10]["basis"] == "accepted_non_phi_manifest_and_unmounted_adapter"
    assert all(
        indexed[order]["classification"] == "satisfied" for order in (2, 5, 9, 10)
    )


def test_unknown_commit_gap_cannot_be_closed_by_static_lifecycle_repair() -> None:
    failure = review.load_json(ROOT, review.ATTEMPT_FAILURE)
    envelope = review.load_json(ROOT, review.ATTEMPT_ENVELOPE)
    repair = review.load_json(ROOT, review.REPAIR)
    assert (failure["stage"], failure["code"]) == (
        "environment",
        "server_not_running_after_readiness",
    )
    assert "setup_and_catalogue" not in failure["lifecycle"]
    assert envelope["transaction_attestation_sha256"] is None
    assert repair["deterministic_verification"]["database_invocations"] == 0
    evidence = review.run_review(ROOT, release=False)
    assert evidence["dimensions"][6]["classification"] == "operational_evidence_gap"


def test_environment_architecture_cannot_impersonate_operational_posture() -> None:
    architecture = review.load_json(ROOT, review.ENVIRONMENT)
    assert architecture["canonical_manifest_instance_count"] == 0
    assert architecture["current_secret_reference_count"] == 0
    assert architecture["current_rotation_evidence_count"] == 0
    assert architecture["database_or_role_used"] is False
    assert architecture["provider_or_network_used"] is False
    evidence = review.run_review(ROOT, release=False)
    assert evidence["dimensions"][10]["classification"] == "operational_evidence_gap"


def test_hostile_contract_mutations_reject_abbreviations_and_vocabulary_drift() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    abbreviated = copy.deepcopy(contract)
    abbreviated["accepted_git_objects"]["original_readiness_review"] = "27101fa"
    with pytest.raises(review.ContractError):
        review.validate_contract(abbreviated, ROOT, check_git=False)

    drifted = copy.deepcopy(contract)
    drifted["dimensions"][6]["expected_classification"] = "blocked"
    with pytest.raises(review.ContractError):
        review.validate_contract(drifted, ROOT, check_git=False)

    assert review.hostile_mutations(contract, ROOT) == 125


def test_release_is_idempotent_and_matches_checked_in_outputs(tmp_path: Path) -> None:
    evidence = review.run_review(ROOT, release=False)
    expected_json = (
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    )
    expected_report = review.render_report(evidence)
    assert (ROOT / review.EVIDENCE_PATH).read_text(encoding="utf-8") == expected_json
    assert (ROOT / review.REPORT_PATH).read_text(encoding="utf-8") == expected_report
    assert tmp_path.exists()


def test_reviewer_source_has_no_application_or_runtime_import() -> None:
    source = (ROOT / f"{MODULE_NAME.replace('.', '/')}.py").read_text(encoding="utf-8")
    forbidden = (
        "from app",
        "import app",
        "import docker",
        "import psycopg",
        "import sqlalchemy",
        "import requests",
        "import httpx",
        "import socket",
    )
    assert all(needle not in source for needle in forbidden)


def test_plan_and_threat_delta_retain_closed_authority() -> None:
    plan = (
        ROOT
        / "docs/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-"
        "admission-readiness-convergence-review-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        ROOT
        / "docs/security/raisa-provider-free-read-only-canonical-check-in-ordinary-"
        "practice-admission-readiness-convergence-review-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for text in (plan, threat):
        assert "Date: 2026-08-23" in text
        assert "+10:00 (Australia/Brisbane)" in text
        assert "not_ready_for_ordinary_practice_admission" in text
        assert "2e34bdad732fdab32fbf778280b3d3c70d66d602" in plan
    assert "No seven-character abbreviation is an admitted binding." in plan
    assert (
        "ten `satisfied`, zero `blocking_gap`, two `operational_evidence_gap`" in plan
    )

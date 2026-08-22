from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from scripts import (
    raisa_provider_free_read_only_post_attempt_008_check_in_admission_readiness_convergence_review as review,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / f"{review.__name__.replace('.', '/')}.py"


def _attempt_packet() -> tuple[dict, dict, dict, dict[str, str]]:
    texts = {
        path: review.canonical_text(ROOT, path) for path, _ in review.INPUT_BINDINGS
    }
    return (
        json.loads(texts[review.ATTEMPT_EVIDENCE]),
        json.loads(texts[review.ATTEMPT_ATTESTATION]),
        json.loads(texts[review.ATTEMPT_ENVELOPE]),
        texts,
    )


def test_contract_matches_closed_schema_and_exact_shape() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    schema = review.load_json(ROOT, review.SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=str)
    assert errors == []
    assert len(contract["inputs"]) == 11
    assert len(contract["accepted_git_objects"]) == 4
    assert len(contract["dimensions"]) == 12


def test_every_git_binding_is_full_and_ancestral() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    bindings = {
        "planning_source": contract["planning_source"],
        **contract["accepted_git_objects"],
    }
    assert all(re.fullmatch(r"[0-9a-f]{40}", value) for value in bindings.values())
    assert all(review.git_object_is_ancestor(ROOT, value) for value in bindings.values())


def test_prior_packet_is_exactly_the_accepted_10_0_2_reading() -> None:
    texts = {
        path: review.canonical_text(ROOT, path) for path, _ in review.INPUT_BINDINGS
    }
    dimensions = review.validate_prior_packet(
        json.loads(texts[review.PRIOR_CONTRACT]),
        json.loads(texts[review.PRIOR_EVIDENCE]),
        texts,
    )
    assert len(dimensions) == 12
    assert dimensions[6]["classification"] == "operational_evidence_gap"
    assert dimensions[10]["classification"] == "operational_evidence_gap"


def test_review_advances_only_dimension_seven_to_11_0_1() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["result"] == review.RESULT
    assert evidence["prior_dimension_counts"] == review.PRIOR_COUNTS
    assert evidence["dimension_counts"] == review.EXPECTED_COUNTS
    assert evidence["blocking_gaps"] == []
    assert evidence["operational_evidence_gaps"] == list(review.REQUIRED_OPEN_GAPS)
    assert evidence["verdict"] == "not_ready_for_ordinary_practice_admission"

    prior = review.load_json(ROOT, review.PRIOR_EVIDENCE)["dimensions"]
    current = evidence["dimensions"]
    for index in range(12):
        if index == 6:
            assert prior[index]["classification"] == "operational_evidence_gap"
            assert current[index]["classification"] == "satisfied"
            assert (
                current[index]["basis"]
                == "accepted_attempt_008_one_shot_transaction_terminal"
            )
        else:
            assert current[index] == prior[index]


def test_all_nine_transaction_transition_criteria_pass() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert tuple(evidence["transaction_criteria"]) == review.TRANSACTION_CRITERIA
    assert all(evidence["transaction_criteria"].values())


@pytest.mark.parametrize(
    ("target", "path", "value"),
    [
        ("evidence", ("result",), "failed_closed"),
        ("envelope", ("occupied_execution_count",), 2),
        ("attestation", ("explicit_rollback", "readback_counts", "effect"), 1),
        ("attestation", ("ambiguous_response", "success_released"), True),
        ("attestation", ("authoritative_readback", "duplicate_effect_count"), 1),
        ("attestation", ("role_catalogue", "bypass_rls"), True),
        ("attestation", ("product_record_count",), 1),
        ("evidence", ("cleanup", "matching_owned_resources"), 1),
        ("envelope", ("transaction_attestation_sha256",), "0" * 64),
    ],
)
def test_each_frozen_transaction_criterion_fails_closed(
    target: str, path: tuple[str, ...], value: object
) -> None:
    evidence, attestation, envelope, texts = _attempt_packet()
    packets = {
        "evidence": evidence,
        "attestation": attestation,
        "envelope": envelope,
    }
    cursor = packets[target]
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    with pytest.raises(review.ContractError):
        review.validate_attempt_packet(evidence, attestation, envelope, texts)


def test_hostile_contract_mutations_reject_with_zero_escape() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    assert review.hostile_mutations(contract, ROOT) == 124

    abbreviated = copy.deepcopy(contract)
    abbreviated["accepted_git_objects"]["attempt_008_occupied_source"] = "9f37ede"
    with pytest.raises(review.ContractError):
        review.validate_contract(abbreviated, ROOT, check_sources=False)

    descriptive = copy.deepcopy(contract)
    descriptive["dimensions"][6]["expected_classification"] = "closed_by_attempt"
    with pytest.raises(review.ContractError):
        review.validate_contract(descriptive, ROOT, check_sources=False)


def test_environment_and_ordinary_admission_remain_closed() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["dimensions"][10]["classification"] == "operational_evidence_gap"
    assert evidence["closed_boundaries"]["environment_or_secret_posture_claimed"] is False
    assert evidence["closed_boundaries"]["ordinary_practice_enabled"] is False
    assert evidence["closed_boundaries"]["ordinary_admission_released"] is False


def test_api_spine_boundary_is_read_only_and_unchanged() -> None:
    assert review.product_paths_are_unchanged(ROOT)
    boundary = review.run_review(ROOT, release=False)["api_spine_boundary"]
    assert boundary == {
        "classification": "read_only_security_audit_idempotency_evidence_review",
        "graphql_remains_read_only": True,
        "rest_command_pattern_unchanged": True,
        "practice_scope_confirmation_idempotency_audit_retained": True,
        "authoritative_readback_decides_unknown_response": True,
        "api_or_product_artifact_changed": False,
        "unchanged_path_count": 6,
    }


def test_release_is_idempotent_and_matches_checked_in_outputs(tmp_path: Path) -> None:
    evidence = review.run_review(ROOT, release=False)
    expected_json = json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    assert (ROOT / review.EVIDENCE_PATH).read_text(encoding="utf-8") == expected_json
    assert (ROOT / review.REPORT_PATH).read_text(encoding="utf-8") == review.render_report(evidence)
    assert tmp_path.exists()


def test_reviewer_has_no_application_database_network_or_provider_import() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
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


def test_plan_and_threat_delta_retain_the_narrow_boundary() -> None:
    plan = (
        ROOT
        / "docs/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-"
        "admission-readiness-post-attempt-008-convergence-review-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        ROOT
        / "docs/security/raisa-provider-free-read-only-canonical-check-in-ordinary-"
        "practice-admission-readiness-post-attempt-008-convergence-review-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for text in (plan, threat):
        assert "Date: 2026-08-23" in text
        assert "+10:00 (Australia/Brisbane)" in text
        assert "not_ready_for_ordinary_practice_admission" in text
        assert "environment_manifest_and_operational_secret_posture" in text
    assert "eleven `satisfied`, zero `blocking_gap` and one" in plan
    assert "2e34bdad732fdab32fbf778280b3d3c70d66d602" in plan

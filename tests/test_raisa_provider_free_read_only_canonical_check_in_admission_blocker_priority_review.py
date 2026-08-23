from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from scripts import (
    raisa_provider_free_read_only_canonical_check_in_admission_blocker_priority_review as review,
)


ROOT = Path(__file__).resolve().parents[1]


def test_contract_and_evidence_schemas_are_closed_and_valid() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    contract_schema = review.load_json(ROOT, f"{review.BASE}/contract.schema.json")
    Draft202012Validator.check_schema(contract_schema)
    assert list(Draft202012Validator(contract_schema).iter_errors(contract)) == []
    evidence_schema = review.load_json(ROOT, f"{review.BASE}/evidence.schema.json")
    Draft202012Validator.check_schema(evidence_schema)


def test_every_git_binding_is_full_and_ancestral() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    bindings = [contract["planning_source"]] + [
        item["git_object"] for item in contract["accepted_sources"]
    ]
    assert all(re.fullmatch(r"[0-9a-f]{40}", value) for value in bindings)
    assert all(review.git_object_is_ancestor(ROOT, value) for value in bindings)


def test_review_reconciles_6_3_3_to_11_0_1_without_reopening_repository_work() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["readiness_reconciliation"]["original"] == {
        "satisfied": 6,
        "blocking_gap": 3,
        "operational_evidence_gap": 3,
    }
    assert evidence["readiness_reconciliation"]["current"] == {
        "satisfied": 11,
        "blocking_gap": 0,
        "operational_evidence_gap": 1,
    }
    assert evidence["readiness_reconciliation"]["repository_prerequisites_remaining"] == 0
    assert evidence["readiness_reconciliation"]["ordinary_admission_releases"] == 0


def test_external_facts_and_human_choices_remain_exactly_absent() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert tuple(item["id"] for item in evidence["external_facts"]) == review.EXTERNAL_FACT_IDS
    assert all(item["status"] == "absent" for item in evidence["external_facts"])
    assert tuple(item["id"] for item in evidence["human_choices"]) == review.HUMAN_CHOICE_IDS
    assert all(item["status"] == "unselected" for item in evidence["human_choices"])


def test_dependency_order_preserves_independent_readback_and_final_activation() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert tuple(item["id"] for item in evidence["ranked_groups"]) == review.RANKS
    assert evidence["ranked_groups"][3]["depends_on"] == [review.RANKS[2]]
    assert evidence["ranked_groups"][4]["depends_on"] == [review.RANKS[3]]
    assert evidence["ranked_groups"][4]["kind"] == "separate_lasting_impact_confirmation"


def test_successor_is_only_a_non_actuating_root_decision_brief() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["next_operation"] == {
        "operation_id": review.NEXT_OPERATION,
        "kind": "provider_free_read_only_decision_brief",
        "asks_only_root_decision": True,
        "creates_control_layer": False,
        "user_attention_required_after_closeout": True,
    }


def test_hostile_contract_mutations_reject_short_ids_and_dependency_drift() -> None:
    contract = review.load_json(ROOT, review.CONTRACT_PATH)
    abbreviated = copy.deepcopy(contract)
    abbreviated["accepted_sources"][0]["git_object"] = "27101fa"
    with pytest.raises(review.ContractError):
        review.validate_contract(abbreviated, ROOT, check_git=False)
    inverted = copy.deepcopy(contract)
    inverted["ranked_groups"].reverse()
    with pytest.raises(review.ContractError):
        review.validate_contract(inverted, ROOT, check_git=False)
    assert review.hostile_mutations(contract, ROOT) >= 30


def test_release_is_idempotent_and_schema_valid() -> None:
    evidence = review.run_review(ROOT, release=False)
    expected = json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    assert (ROOT / review.EVIDENCE_PATH).read_text(encoding="utf-8") == expected
    schema = review.load_json(ROOT, f"{review.BASE}/evidence.schema.json")
    assert list(Draft202012Validator(schema).iter_errors(evidence)) == []
    assert (ROOT / review.REPORT_PATH).read_text(encoding="utf-8") == review.render_report(evidence)


def test_reviewer_has_no_runtime_or_network_capability_import() -> None:
    source = (ROOT / "scripts/raisa_provider_free_read_only_canonical_check_in_admission_blocker_priority_review.py").read_text(encoding="utf-8")
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
    assert all(value not in source for value in forbidden)


def test_plan_and_threat_preserve_closed_authority() -> None:
    plan = (ROOT / "docs/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-admission-blocker-priority-review-plan.md").read_text(encoding="utf-8")
    threat = (ROOT / "docs/security/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-admission-blocker-priority-review-threat-model-delta.md").read_text(encoding="utf-8")
    for text in (plan, threat):
        assert "Date: 2026-08-23" in text
        assert "ordinary activation" in text.lower()
        assert "40-character" in text
    assert "Timestamp:" in plan and "+10:00 (Australia/Brisbane)" in plan
    assert "docs/branding/" in plan
    assert "2e34bdad732fdab32fbf778280b3d3c70d66d602" not in threat

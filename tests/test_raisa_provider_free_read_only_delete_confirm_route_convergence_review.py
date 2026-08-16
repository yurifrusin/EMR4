import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_read_only_delete_confirm_route_convergence_review import (
    CONTRACT_PATH,
    CONTRACT_SCHEMA_PATH,
    DIMENSION_IDS,
    EVIDENCE_SCHEMA_PATH,
    ROOT,
    ReviewError,
    evaluate,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_exact_read_only_route_review_passes() -> None:
    evidence = evaluate()

    assert evidence["verdict"] == "unmounted_adapter_and_response_transition_required"
    assert evidence["dimension_counts"] == {
        "satisfied": 3,
        "partial_gap": 1,
        "blocking_gap": 6,
    }
    assert len(evidence["source_bindings"]) == 18
    assert all(evidence["checks"].values())
    assert all(value is False for value in evidence["runtime_boundaries"].values())
    Draft202012Validator(_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)


def test_review_contract_preserves_exact_dimension_order_and_response_blocker() -> None:
    contract = _json(CONTRACT_PATH)

    assert tuple(item["id"] for item in contract["dimensions"]) == DIMENSION_IDS
    response = next(
        item
        for item in contract["dimensions"]
        if item["id"] == "response_contract_compatibility"
    )
    assert response["classification"] == "blocking_gap"
    assert "six-field" in response["observation"]
    assert "byte-exact replay" in response["prerequisite"]


def test_reviewer_imports_no_application_runtime() -> None:
    source = (
        ROOT
        / "scripts/raisa_provider_free_read_only_delete_confirm_route_convergence_review.py"
    ).read_text(encoding="utf-8")
    assert "from app" not in source
    assert "import app" not in source
    assert "TestClient" not in source
    assert "sqlalchemy" not in source.lower()


@pytest.mark.parametrize(
    ("mutation", "expected_fragment"),
    [
        ("short_source", "does not match"),
        ("extra_top_level", "Additional properties"),
        ("missing_source", "is too short"),
        ("duplicate_source", "has non-unique elements"),
        ("missing_dimension", "is too short"),
        ("extra_dimension", "is too long"),
        ("unknown_dimension", "is not one of"),
        ("unknown_classification", "is not one of"),
        ("unknown_verdict", "is not one of"),
        ("missing_prerequisite_key", "is a required property"),
    ],
)
def test_closed_contract_rejects_named_structural_threats(
    mutation: str, expected_fragment: str
) -> None:
    value = copy.deepcopy(_json(CONTRACT_PATH))
    if mutation == "short_source":
        value["source_head"] = "abc"
    elif mutation == "extra_top_level":
        value["unexpected"] = True
    elif mutation == "missing_source":
        value["sources"].pop()
    elif mutation == "duplicate_source":
        value["sources"][-1] = copy.deepcopy(value["sources"][0])
    elif mutation == "missing_dimension":
        value["dimensions"].pop()
    elif mutation == "extra_dimension":
        value["dimensions"].append(copy.deepcopy(value["dimensions"][0]))
    elif mutation == "unknown_dimension":
        value["dimensions"][0]["id"] = "other"
    elif mutation == "unknown_classification":
        value["dimensions"][0]["classification"] = "ready"
    elif mutation == "unknown_verdict":
        value["verdict"] = "route_ready"
    elif mutation == "missing_prerequisite_key":
        value["dimensions"][0].pop("prerequisite")

    errors = list(Draft202012Validator(_json(CONTRACT_SCHEMA_PATH)).iter_errors(value))
    assert errors
    assert any(expected_fragment in error.message for error in errors)


def test_source_hash_change_fails_closed(tmp_path: Path) -> None:
    contract = _json(CONTRACT_PATH)
    contract["sources"][0]["sha256"] = "0" * 64
    altered = tmp_path / "contract.json"
    altered.write_text(json.dumps(contract), encoding="utf-8")

    with pytest.raises(ReviewError, match="bound source hash mismatch"):
        evaluate(contract_path=altered)


def test_verdict_cannot_ignore_a_blocker(tmp_path: Path) -> None:
    contract = _json(CONTRACT_PATH)
    contract["verdict"] = "ready_for_bounded_unmounted_route_candidate"
    altered = tmp_path / "contract.json"
    altered.write_text(json.dumps(contract), encoding="utf-8")

    with pytest.raises(ReviewError, match="verdict does not follow"):
        evaluate(contract_path=altered)

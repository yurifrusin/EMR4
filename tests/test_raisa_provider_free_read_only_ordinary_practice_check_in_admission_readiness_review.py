from __future__ import annotations

import ast
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    raisa_provider_free_read_only_ordinary_practice_check_in_admission_readiness_review
    as review,
)


ROOT = Path(__file__).resolve().parents[1]


def test_contract_matches_schema_and_frozen_validation() -> None:
    contract = review.load_contract(ROOT)
    schema = json.loads(
        (
            ROOT
            / review.BASE
            / "admission-readiness-review-contract.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema).validate(contract)
    review.validate_contract(contract, ROOT)


def test_review_proves_exact_not_ready_matrix_without_writing() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["result"] == review.RESULT
    assert evidence["verdict"] == "not_ready_for_ordinary_practice_admission"
    assert evidence["dimension_counts"] == {
        "satisfied": 6,
        "blocking_gap": 3,
        "operational_evidence_gap": 3,
    }
    assert [item["id"] for item in evidence["dimensions"]] == [
        item[1] for item in review.DIMENSIONS
    ]
    assert evidence["next_tranche"] == review.NEXT_TRANCHE


def test_expected_blocking_and_operational_gaps_are_exact() -> None:
    evidence = review.run_review(ROOT, release=False)
    assert evidence["blocking_gaps"] == [
        "ordinary_practice_admission_control",
        "ordinary_rollout_kill_switch_and_rollback_runbook",
        "non_phi_observability_and_alerting",
    ]
    assert evidence["operational_evidence_gaps"] == [
        "tenant_isolation_and_runtime_database_role",
        "atomic_effect_rollback_and_unknown_commit_recovery",
        "environment_manifest_and_operational_secret_posture",
    ]


def test_hostile_mutation_suite_exceeds_minimum() -> None:
    contract = review.load_contract(ROOT)
    assert review.hostile_mutations(contract, ROOT) >= 120


def test_hash_mode_normalizes_crlf_and_rejects_bare_cr(tmp_path: Path) -> None:
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    bare = tmp_path / "bare.txt"
    lf.write_bytes(b"one\ntwo\n")
    crlf.write_bytes(b"one\r\ntwo\r\n")
    bare.write_bytes(b"one\rtwo\n")
    assert review.canonical_sha256(lf) == review.canonical_sha256(crlf)
    with pytest.raises(review.ContractError, match="bare CR"):
        review.canonical_sha256(bare)


def test_reviewer_imports_no_app_and_has_no_runtime_clients() -> None:
    source = (
        ROOT
        / "scripts/raisa_provider_free_read_only_ordinary_practice_check_in_"
        "admission_readiness_review.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    assert not any(name == "app" or name.startswith("app.") for name in imports)
    assert "sqlalchemy" not in imports
    assert "requests" not in imports
    assert "httpx" not in imports
    assert "subprocess" not in imports


def test_released_outputs_are_exact_renderer_products() -> None:
    evidence = review.run_review(ROOT, release=False)
    released = json.loads((ROOT / review.EVIDENCE_PATH).read_text(encoding="utf-8"))
    report = (ROOT / review.REPORT_PATH).read_text(encoding="utf-8")
    assert released == evidence
    assert report == review.render_report(evidence)
    assert all(value is False for value in released["closed_boundaries"].values())

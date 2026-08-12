import ast
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_read_only_status_confirm_runtime_gap_admission_review as review,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review-plan.md"
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-read-only-status-confirm-runtime-gap-"
    "admission-review-threat-model-delta.md"
)
SCRIPT = (
    ROOT
    / "scripts/raisa_provider_free_read_only_status_confirm_runtime_gap_admission_review.py"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_is_closed_and_schema_valid() -> None:
    contract = _load(review.CONTRACT_PATH)
    schema = _load(review.SCHEMA_PATH)
    Draft202012Validator(schema).validate(contract)
    allowlist = review.validate_contract(contract, schema)
    assert len(allowlist) == 11
    assert contract["implementation_authorized"] is False


def test_generated_evidence_matches_exact_builder() -> None:
    assert _load(review.EVIDENCE_PATH) == review.build_evidence()


def test_verdict_is_not_admitted_with_exact_gap_counts() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert evidence["verdict"] == "not_admitted"
    assert evidence["dimension_counts"] == {
        "satisfied": 0,
        "partial_gap": 2,
        "blocking_gap": 7,
    }
    assert evidence["implementation_authorized"] is False


def test_all_exact_source_hashes_match() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert len(evidence["source_hashes"]) == 11
    for relative, expected in evidence["source_hashes"].items():
        assert review._sha256(ROOT / relative) == expected


def test_all_dimensions_have_resolved_allowlisted_citations() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    allowlist = set(evidence["source_hashes"])
    assert tuple(item["id"] for item in evidence["dimensions"]) == review.EXPECTED_DIMENSIONS
    for dimension in evidence["dimensions"]:
        assert dimension["citations"]
        for citation in dimension["citations"]:
            assert citation["path"] in allowlist
            assert citation["line_start"] >= 1
            assert citation["line_end"] >= citation["line_start"]


def test_structural_assertions_all_pass() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert len(evidence["structural_assertions"]) == 15
    assert all(item["passed"] is True for item in evidence["structural_assertions"])


def test_all_thirty_seven_hostile_mutations_fail_closed() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert evidence["hostile_mutations"] == {"attempted": 37, "rejected": 37}


def test_terminal_guard_is_read_only_and_not_counted_as_execution() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert evidence["terminal_guard_executed"] is False
    terminal = next(
        item for item in evidence["dimensions"] if item["id"] == "terminal_transition_policy"
    )
    assert terminal["classification"] == "blocking_gap"
    assert any(item["path"].startswith("review/") for item in terminal["citations"])


def test_script_imports_no_application_or_database_runtime() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any(name == "app" or name.startswith("app.") for name in imported)
    assert not any(name.startswith("sqlalchemy") for name in imported)


def test_plan_and_threat_model_preserve_exact_file_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for phrase in (
        "exact files may be read or content-searched",
        "No repository, `tests/`, `docs/`, `review/` or application-directory search",
        "not edit or execute an application route or database",
        "at least 30 hostile mutations fail closed",
        "`docs/branding/`",
    ):
        assert phrase in text
    assert "implementation_authorized: false" in threat
    assert "AER-0291" in threat


def test_next_candidate_remains_unmounted_and_non_executing() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert (
        evidence["next_candidate"]
        == "provider_free_unmounted_status_confirm_runtime_convergence_architecture"
    )
    assert set(evidence["forbidden"].values()) == {False}

import ast
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_read_only_status_confirm_route_mounting_admission_review
    as review,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-read-only-status-confirm-route-mounting-"
    "admission-review-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-read-only-status-confirm-route-mounting-"
    "admission-review-threat-model-delta.md"
)
SCRIPT = ROOT / (
    "scripts/raisa_provider_free_read_only_status_confirm_route_mounting_"
    "admission_review.py"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_is_closed_and_schema_valid() -> None:
    contract = _load(review.CONTRACT_PATH)
    schema = _load(review.SCHEMA_PATH)
    Draft202012Validator(schema).validate(contract)
    allowlist = review.validate_contract(contract, schema)
    assert len(allowlist) == 10
    assert contract["implementation_authorized"] is False


def test_generated_evidence_matches_exact_builder() -> None:
    assert _load(review.EVIDENCE_PATH) == review.build_evidence()


def test_verdict_distinguishes_mounting_from_admission() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert (
        evidence["verdict"]
        == "mounted_legacy_route_not_admitted_for_physical_convergence"
    )
    assert evidence["dimension_counts"] == {
        "satisfied": 2,
        "partial_gap": 1,
        "blocking_gap": 7,
    }
    literal = next(
        item for item in evidence["dimensions"] if item["id"] == "literal_route_mounting"
    )
    assert literal["classification"] == "satisfied"
    assert evidence["implementation_authorized"] is False


def test_all_exact_source_hashes_match() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert len(evidence["source_hashes"]) == 10
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


def test_all_structural_assertions_pass() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert len(evidence["structural_assertions"]) == 25
    assert all(item["passed"] is True for item in evidence["structural_assertions"])


def test_all_forty_five_hostile_mutations_fail_closed() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert evidence["hostile_mutations"] == {"attempted": 45, "rejected": 45}


def test_physical_foundation_is_consumed_not_reopened() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    physical = next(
        item
        for item in evidence["dimensions"]
        if item["id"] == "proved_physical_foundation"
    )
    assert physical["classification"] == "satisfied"
    assert physical["admission_blocker"] is False


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
        "Only the exact files and hashes",
        "No repository, `tests/`, `docs/`, `review/` or",
        "must not edit or execute an application route or database",
        "At least 40 hostile mutations fail closed",
        "`docs/branding/`",
    ):
        assert phrase in text
    assert "implementation_authorized: false" in threat
    assert "AER-0292" in threat


def test_next_candidate_remains_unmounted_and_non_executing() -> None:
    evidence = _load(review.EVIDENCE_PATH)
    assert (
        evidence["next_candidate"]
        == "provider_free_unmounted_status_confirm_route_convergence_composition_rehearsal"
    )
    assert set(evidence["forbidden"].values()) == {False}

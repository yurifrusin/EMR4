"""Focused provider-free review tests for the delete-confirm route-mounting
readiness review script.

These tests exercise the deterministic review script only.  They never import
``app``, never mount or call a route, and never open a database, Docker, SQL,
provider or network surface.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review as review  # noqa: E402


EXPECTED_IDS = [
    "literal_mounting",
    "canonical_identity_and_alias",
    "proposal_version_binding_carriage",
    "server_authority_and_session_ingress",
    "physical_seam_composition",
    "locked_current_truth_readmission",
    "atomic_effect_audit_private_receipt",
    "public_response_schema",
    "canonical_public_byte_delivery",
    "closed_outcome_http_mapping",
    "raw_delete_isolation",
    "accepted_postgresql_foundation",
]

EXPECTED_CLASSIFICATIONS = [
    "satisfied",
    "route_transition_gap",
    "route_transition_gap",
    "route_transition_gap",
    "satisfied",
    "satisfied",
    "satisfied",
    "route_transition_gap",
    "route_transition_gap",
    "satisfied",
    "satisfied",
    "satisfied",
]

EXPECTED_TRANSITION_GAPS = [
    "canonical_identity_and_alias",
    "proposal_version_binding_carriage",
    "server_authority_and_session_ingress",
    "public_response_schema",
    "canonical_public_byte_delivery",
]

_CACHED_RESULT = None


def _result() -> dict:
    global _CACHED_RESULT
    if _CACHED_RESULT is None:
        _CACHED_RESULT = review.run_review(repo_root=ROOT, write_outputs=False)
    return _CACHED_RESULT


def test_review_verdict_and_matrix():
    result = _result()
    assert result["verdict"] == "ready_for_bounded_route_convergence_candidate"
    assert result["dimension_counts"] == {
        "satisfied": 7,
        "route_transition_gap": 5,
        "blocking_gap": 0,
    }


def test_dimension_order_and_classifications():
    result = _result()
    dims = result["dimensions"]
    assert [d["id"] for d in dims] == EXPECTED_IDS
    assert [d["classification"] for d in dims] == EXPECTED_CLASSIFICATIONS
    assert [d["order"] for d in dims] == list(range(1, 13))


def test_transition_gaps_are_exactly_five():
    result = _result()
    assert result["transition_gaps"] == EXPECTED_TRANSITION_GAPS
    gaps = [d["id"] for d in result["dimensions"] if d["classification"] == "route_transition_gap"]
    assert gaps == EXPECTED_TRANSITION_GAPS


def test_private_public_byte_separation():
    result = _result()
    assert result["private_public_byte_separation"] is True
    markers = result["private_public_byte_separation_markers"]
    assert "public_body_is_public_bytes" in markers
    assert "private_stored_bytes_carried_separately" in markers
    assert "public_bytes_derived_from_public_projection" in markers


def test_hostile_mutations_at_least_72():
    result = _result()
    assert result["hostile_mutations_rejected"] >= 72
    assert result["hostile_mutations_rejected"] >= review.EXPECTED_ACCEPTANCE["minimum_hostile_mutations"]


def test_all_23_bindings_match():
    contract = review.load_contract(ROOT)
    # validate_contract raises ContractValidationError on any mismatch.
    review.validate_contract(contract, ROOT)
    assert len(contract["inputs"]) == 23


def test_script_has_no_app_import():
    source = Path(review.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("app"), f"app import found: {alias.name}"
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith("app"), f"app import from found: {module}"
    assert "import app" not in source
    assert "from app " not in source


def test_hash_function_rejects_bare_cr():
    with pytest.raises(ValueError):
        review._canonical_lf_hash_bytes(b"line\rvalue")
    with pytest.raises(ValueError):
        review._canonical_lf_hash_bytes(b"line\rvalue\r")


def test_hash_function_canonicalizes_crlf():
    assert review._canonical_lf_hash_bytes(b"a\r\nb") == review._canonical_lf_hash_bytes(b"a\nb")
    assert review._canonical_lf_hash_bytes(b"a\r\nb\r\n") == review._canonical_lf_hash_bytes(b"a\nb\n")


def test_fail_closed_when_evidence_missing():
    with pytest.raises(review.EvidenceError):
        review._prove_literal_mounting({})


def test_evidence_citations_nonempty():
    result = _result()
    for dim in result["dimensions"]:
        # The released JSON intentionally omits citations; verify internally by
        # running the evidence checks once and asserting citations are recorded.
        pass
    texts = review.load_source_texts(review.load_contract(ROOT), ROOT)
    checks = review.run_evidence_checks(texts)
    for check in checks:
        assert check["citations"], f"dimension {check['id']} has no source citations"
        assert check["markers"], f"dimension {check['id']} has no evidence markers"


def test_released_evidence_json_conforms():
    review.run_review(repo_root=ROOT, write_outputs=True)
    evidence_path = ROOT / review.EVIDENCE_RELATIVE_PATH
    assert evidence_path.exists()
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    allowed = {
        "schema_version",
        "result",
        "source_head",
        "source_bindings",
        "dimension_counts",
        "dimensions",
        "transition_gaps",
        "satisfied_dimensions",
        "private_public_byte_separation",
        "private_public_byte_separation_markers",
        "hostile_mutations_rejected",
        "verdict",
        "closed_boundaries",
    }
    assert set(payload) == allowed
    assert payload["verdict"] == "ready_for_bounded_route_convergence_candidate"
    assert payload["hostile_mutations_rejected"] >= 72
    assert payload["closed_boundaries"]["app_imported"] is False
    assert payload["closed_boundaries"]["route_called"] is False
    # released JSON must contain only paths, hashes, ids, classifications,
    # marker names/counts, verdict and closed-boundary booleans.
    for dim in payload["dimensions"]:
        assert set(dim) == {"order", "id", "classification", "citations", "markers"}
        assert isinstance(dim["citations"], list) and dim["citations"]
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in payload["source_bindings"].items())


def test_report_contains_date_and_timestamp_in_order():
    report = review.render_report(_result())
    lines = report.splitlines()
    date_line = "Date: 2026-08-17"
    timestamp_line = "Timestamp: 2026-08-17T00:46:11.8521710+10:00 (Australia/Brisbane)"
    assert date_line in lines
    assert timestamp_line in lines
    date_idx = lines.index(date_line)
    timestamp_idx = lines.index(timestamp_line)
    # The timestamp must appear immediately after the date, near the top of the
    # report, matching AGENTS.md section 10 item 8.
    assert timestamp_idx == date_idx + 1
    assert date_idx < 5

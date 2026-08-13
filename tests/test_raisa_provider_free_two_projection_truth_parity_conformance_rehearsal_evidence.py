from __future__ import annotations

import json
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from scripts.raisa_provider_free_two_projection_truth_parity_conformance_rehearsal import (
    RENDERERS,
    SCENARIOS,
    compare_paired_traces,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "orchestration/continuity/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal"
EVIDENCE = EVIDENCE_DIR / "two-projection-truth-parity-evidence.json"
EVIDENCE_SCHEMA = EVIDENCE_DIR / "two-projection-truth-parity-evidence.schema.json"
TRACE_SCHEMA = EVIDENCE_DIR / "projection-truth-trace.schema.json"
CANDIDATE_SOURCE = "18aa4b613d735a68a7f6f2e55d34e498176c9935"
TRANCHE_BASELINE = "fbb2fd1822f73b2469fc774eb001af31dfdfa85b"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_is_schema_valid_and_bound_to_exact_source() -> None:
    evidence = _json(EVIDENCE)
    envelope_schema = _json(EVIDENCE_SCHEMA)
    trace_schema = _json(TRACE_SCHEMA)
    registry = Registry().with_resource(
        trace_schema["$id"],
        Resource.from_contents(trace_schema),
    )
    Draft202012Validator(envelope_schema, registry=registry).validate(evidence)
    assert evidence["candidate_source"] == CANDIDATE_SOURCE
    assert evidence["trace_count"] == 12
    assert evidence["comparison_count"] == 6


def test_evidence_contains_exact_complete_pair_matrix() -> None:
    evidence = _json(EVIDENCE)
    coordinates = {(trace["renderer"], trace["scenario"]) for trace in evidence["traces"]}
    assert coordinates == {(renderer, scenario) for renderer in RENDERERS for scenario in SCENARIOS}
    assert compare_paired_traces(evidence["traces"]) == evidence["comparisons"]
    assert all(item["kernel_fields_equal"] for item in evidence["comparisons"])
    assert all(item["raw_compatibility_requests"] == 0 for item in evidence["comparisons"])


def test_commits_and_noncommits_have_exact_current_truth() -> None:
    evidence = _json(EVIDENCE)
    for trace in evidence["traces"]:
        expected_status = {
            "safe": "Arrived",
            "committed": "Completed",
        }.get(trace["scenario"], "Booked")
        assert trace["fresh_read_result"]["current_status"] == expected_status
        assert trace["displayed_terminal_state"]["status"] == expected_status


def test_renderer_local_grammar_differs_without_kernel_difference() -> None:
    evidence = _json(EVIDENCE)
    for scenario in SCENARIOS:
        pair = {trace["renderer"]: trace for trace in evidence["traces"] if trace["scenario"] == scenario}
        assert pair["conventional_grid"]["renderer_local"] != pair["reception_one"]["renderer_local"]


def test_candidate_source_changes_no_product_or_api_file() -> None:
    changed = subprocess.run(
        ["git", "diff", "--name-only", TRANCHE_BASELINE, CANDIDATE_SOURCE],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert changed
    forbidden_prefixes = ("app/", "docs/diary/", "docs/api-spine/", "alembic/")
    assert [path for path in changed if path.startswith(forbidden_prefixes)] == []


def test_authority_counts_and_claim_limit_remain_zero_and_narrow() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["authority_counts"] == {
        "provider_calls": 0,
        "patient_or_product_records": 0,
        "database_or_source_reads": 0,
        "database_writes": 0,
        "deployments": 0,
        "releases": 0,
        "protected_ref_movements": 0,
    }
    claim = evidence["claim_limit"].lower()
    assert "route-intercepted" in claim
    assert "no live backend" in claim
    assert "broader feature-parity" in claim

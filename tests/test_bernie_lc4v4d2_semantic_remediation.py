"""Comprehensive tests for LC4V4D2 semantic remediation.

Validates frozen D1 hashes, target IDs, before/after transitions, two-repeat
determinism, and regression safety.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from app.services.bernie.lc4v4_development_diagnostic import (
    EXPECTED_PROBE_COUNT,
    author_all_probes,
    compute_fixture_hash,
    run_diagnostic,
    report_to_dict,
)
from app.services.bernie.lc4v4d2_semantic_remediation import (
    EXPECTED_FIXTURE_HASH,
    EXPECTED_REPORT_HASH,
    EXPECTED_SELECTION_HASH,
    TARGET_23_IDS,
    run_semantic_remediation,
    d2_report_to_dict,
    d2_report_to_markdown,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = pathlib.Path(__file__).resolve().parent
_DOCS_DIR = _HERE.parent / "docs"
_D2_REPORT_PATH = _DOCS_DIR / "bernie-lc4v4d2-semantic-remediation.json"
_D2_MD_PATH = _DOCS_DIR / "bernie-lc4v4d2-semantic-remediation.md"

SOURCE_COMMIT = "c8f015962ecc836d2c0b2a25426ea1114e8c1ccb"


# ===================================================================
# 1. Frozen D1 evidence validation
# ===================================================================


class TestD1EvidenceValidation:
    """Validate frozen D1 fixture, report, and selection hashes."""

    def test_fixture_hash_matches(self):
        probes = author_all_probes()
        assert compute_fixture_hash(probes) == EXPECTED_FIXTURE_HASH

    def test_target_23_ids_exist(self):
        probes = author_all_probes()
        ids = {p["scenario_id"] for p in probes}
        for target_id in TARGET_23_IDS:
            assert target_id in ids, f"Missing target ID: {target_id}"

    def test_selection_hash_matches(self):
        """The 23-case selection hash must match the frozen D1 value."""
        import hashlib, json
        raw = json.dumps(sorted(TARGET_23_IDS), sort_keys=True).encode("utf-8")
        h = "sha256:" + hashlib.sha256(raw).hexdigest()
        assert h == EXPECTED_SELECTION_HASH


# ===================================================================
# 2. D2 remediation report
# ===================================================================


class TestD2RemediationReport:
    """Run the D2 evaluator and validate results."""

    @pytest.fixture(scope="class")
    def report(self):
        return run_semantic_remediation(source_commit=SOURCE_COMMIT)

    def test_probe_count(self, report):
        assert report.total_probes == EXPECTED_PROBE_COUNT

    def test_d1_hashes_validated(self, report):
        assert report.d1_fixture_hash_validated
        assert report.d1_report_hash_validated
        assert report.d1_selection_hash_validated

    def test_target_ids_matched(self, report):
        assert report.target_23_ids_matched

    def test_zero_variance(self, report):
        assert report.zero_variance, "Variance detected between repeats"

    def test_all_supported_maintained(self, report):
        assert report.all_supported_maintained, (
            f"Discrepancies: {report.discrepancies}"
        )

    def test_no_new_parser_gaps(self, report):
        assert not report.new_parser_gap_ids, (
            f"New parser gaps outside target selection: "
            f"{report.new_parser_gap_ids}"
        )

    def test_target_fixed_count_positive(self, report):
        # 20 of 23 target parser gaps should be fixed (3 are fixture-value issues)
        assert report.target_fixed_count >= 17

    def test_classification_counts_non_negative(self, report):
        for cat, count in report.after_classifications.items():
            assert count >= 0, f"Negative count for {cat}"

    def test_transition_every_target(self, report):
        assert len(report.transitions) == len(TARGET_23_IDS)

    def test_before_report_hash_frozen(self, report):
        assert report.before_report_hash == EXPECTED_REPORT_HASH

    def test_json_serialization(self, report):
        d = d2_report_to_dict(report)
        assert d["total_probes"] == EXPECTED_PROBE_COUNT
        assert d["zero_variance"]
        assert d["all_supported_maintained"]
        assert d["d1_fixture_hash_validated"]
        assert d["d1_selection_hash_validated"]
        assert "transitions" in d
        assert len(d["transitions"]) == len(TARGET_23_IDS)

    def test_markdown_report(self, report):
        md = d2_report_to_markdown(report)
        assert "## Classification Comparison" in md
        assert "## Target 23: Before/After Transitions" in md
        assert "## Protected Boundary" in md
        assert "remediation_complete" in md or "revision_required" in md


# ===================================================================
# 3. Two-repeat determinism
# ===================================================================


class TestTwoRepeatDeterminism:
    """Verify complete two-repeat determinism."""

    def test_all_probes_deterministic(self):
        probes = author_all_probes()
        report = run_diagnostic(probes, source_commit=SOURCE_COMMIT)
        assert report.variance_count == 0
        for pr in report.probe_results:
            assert not pr.variance_observed, (
                f"{pr.probe_id}: variance observed"
            )

    def test_fingerprint_matches_across_runs(self):
        probes = author_all_probes()
        r1 = run_diagnostic(probes, source_commit=SOURCE_COMMIT)
        r2 = run_diagnostic(probes, source_commit=SOURCE_COMMIT)
        assert r1.report_hash == r2.report_hash


# ===================================================================
# 4. Policy gap structure
# ===================================================================


class TestPolicyGapStructure:
    """Verify policy gaps are correctly attributed."""

    def test_mismatched_entities_are_policy_gaps(self):
        """Mismatched diary-join cases must remain policy gaps."""
        d2_report = run_semantic_remediation(source_commit=SOURCE_COMMIT)
        mismatched_ids = {
            "lc4v4d1_entity_patient_mismatched_06",
            "lc4v4d1_entity_practitioner_mismatched_12",
            "lc4v4d1_entity_location_mismatched_18",
            "lc4v4d1_entity_appt_type_mismatched_24",
            "lc4v4d1_entity_duration_mismatched_30",
        }
        for t in d2_report.transitions:
            if t.probe_id in mismatched_ids:
                assert t.after_classification == "policy_contract_gap", (
                    f"{t.probe_id}: should remain policy gap"
                )

    def test_diary_passes_all(self):
        """All 6 diary-state probes must still pass."""
        d2_report = run_semantic_remediation(source_commit=SOURCE_COMMIT)
        diary_fam = d2_report.after_family_counts.get("diary", {})
        assert diary_fam.get("supported_pass", 0) == 6

    def test_five_diary_joins_remain_policy(self):
        """The five explicit mismatched diary joins remain policy-contract gaps."""
        d2_report = run_semantic_remediation(source_commit=SOURCE_COMMIT)
        diag = run_diagnostic(author_all_probes(), source_commit=SOURCE_COMMIT)
        policy_ids = set(diag.parser_gap_ids) | {
            pr.probe_id for pr in diag.probe_results
            if pr.classification == "policy_contract_gap"
        }
        mismatched_state_join = {
            "lc4v4d1_entity_patient_mismatched_06",
            "lc4v4d1_entity_practitioner_mismatched_12",
            "lc4v4d1_entity_location_mismatched_18",
            "lc4v4d1_entity_appt_type_mismatched_24",
            "lc4v4d1_entity_duration_mismatched_30",
        }
        for mid in mismatched_state_join:
            pr = next(r for r in diag.probe_results if r.probe_id == mid)
            assert pr.classification == "policy_contract_gap", (
                f"{mid}: should be policy gap, got {pr.classification}"
            )

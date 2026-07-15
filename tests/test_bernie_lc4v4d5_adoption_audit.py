"""LC4V4D5 — Focused adoption audit tests.

Covers population validation, legacy equivalence, D4 preservation,
classification counts, five-difference/blocker selections, variance,
forbidden observations, authoring-invalid quarantine, fail-closed gates,
and deterministic tamper resistance.
"""

from __future__ import annotations

import json
import hashlib
import pathlib
from typing import Any

import pytest

from app.services.bernie.lc4v4_development_diagnostic import (
    author_all_probes,
    compute_fixture_hash,
    validate_probe_population,
)
from app.services.bernie.lc4v4d3_policy_evidence import (
    D3_TARGET_IDS,
    EXPECTED_20_CASE_HASH,
)
from app.services.bernie.lc4v4d4_composed_evidence import (
    EXPECTED_LEGACY_60_HASH,
)
from app.services.bernie.lc4v4d5_adoption_audit import (
    SCHEMA_VERSION,
    FIVE_DIFFERENCE_IDS,
    FOUR_BLOCKER_IDS,
    AUTHORING_INVALID_IDS,
    EXPECTED_ALL_60_POPULATION_HASH,
    EXPECTED_FIVE_DIFFERENCE_SELECTION_HASH,
    EXPECTED_D4_REPORT_HASH,
    EXPECTED_LEGACY_60_BASELINE_HASH,
    run_d5_audit,
    generate_report_json,
    generate_report_markdown,
)


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
D5_JSON_REPORT = ROOT / "docs" / "bernie-lc4v4d5-option-a-adoption-audit.json"
D5_MARKDOWN_REPORT = ROOT / "docs" / "bernie-lc4v4d5-option-a-adoption-audit.md"
SOURCE_COMMIT = "1ac0c71b929cff610f78d2ed8a803b057627d31e"


def _hash(payload: Any) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


# ===================================================================
# 1. Population and fixture tests
# ===================================================================


class TestPopulation:
    """The 60-probe population is valid and matches frozen hashes."""

    def test_exact_60_probes(self) -> None:
        probes = author_all_probes()
        assert len(probes) == 60

    def test_population_validation_passes(self) -> None:
        probes = author_all_probes()
        errors = validate_probe_population(probes)
        assert not errors

    def test_fixture_hash_exact(self) -> None:
        probes = author_all_probes()
        actual = compute_fixture_hash(probes)
        from app.services.bernie.lc4v4d5_adoption_audit import EXPECTED_D1_FIXTURE_HASH
        assert actual == EXPECTED_D1_FIXTURE_HASH, (
            f"Fixture hash mismatch: {actual}"
        )

    def test_all_60_population_hash_exact(self) -> None:
        probes = author_all_probes()
        import json, hashlib
        all_ids = sorted(p["scenario_id"] for p in probes)
        raw = json.dumps(all_ids, sort_keys=True).encode("utf-8")
        actual = "sha256:" + hashlib.sha256(raw).hexdigest()
        assert actual == EXPECTED_ALL_60_POPULATION_HASH, (
            f"Population selection hash mismatch: {actual}"
        )


# ===================================================================
# 2. D5 evidence report tests
# ===================================================================


class TestD5EvidenceReport:
    """D5 evidence report generation and gates."""

    def test_d5_evidence_runs(self) -> None:
        report = run_d5_audit("test-source")
        assert report["total_probes"] == 60
        assert report["schema_version"] == SCHEMA_VERSION
        assert report["all_60_population_hash"] == EXPECTED_ALL_60_POPULATION_HASH

    def test_d5_all_gates_pass(self) -> None:
        report = run_d5_audit("test-source")
        assert report["decision"] == "option_a_adoption_audit_valid_with_4_blockers", (
            f"Decision was {report['decision']!r}. "
            f"Failing gates: {[name for name, val in report['gates'].items() if not val]}"
        )
        assert all(report["gates"].values())

    def test_d5_gate_count(self) -> None:
        report = run_d5_audit("test-source")
        assert len(report["gates"]) == 24

    def test_d5_classification_counts_exact(self) -> None:
        report = run_d5_audit("test-source")
        counts = report["classification_counts"]
        assert counts["legacy_equivalent"] == 35
        assert counts["accepted_d4_versioned_change"] == 20
        assert counts["expected_versioned_relation"] == 1
        assert counts["adoption_blocker_missing_mutation_deltas"] == 3
        assert counts[
            "adoption_blocker_target_field_conflict_and_missing_mutation_deltas"
        ] == 1
        assert counts.get("unexpected_difference", 0) == 0
        assert counts.get("option_a_failed", 0) == 0

    def test_d5_five_difference_ids_exact(self) -> None:
        report = run_d5_audit("test-source")
        actual = set(report["five_difference_ids"])
        assert actual == FIVE_DIFFERENCE_IDS

    def test_d5_four_blocker_ids_exact(self) -> None:
        report = run_d5_audit("test-source")
        actual = set(report["four_blocker_ids"])
        assert actual == FOUR_BLOCKER_IDS

    def test_d5_authoring_invalid_ids_exact(self) -> None:
        report = run_d5_audit("test-source")
        actual = set(report["authoring_invalid_ids"])
        assert actual == AUTHORING_INVALID_IDS

    def test_d5_legacy_baseline_hash_exact(self) -> None:
        report = run_d5_audit("test-source")
        assert report["legacy_60_baseline_hash"] == EXPECTED_LEGACY_60_BASELINE_HASH

    def test_d5_zero_forbidden_observations(self) -> None:
        report = run_d5_audit("test-source")
        for case in report["cases"]:
            assert not case["forbidden_observations"], (
                f"Case {case['probe_id']} has forbidden observations: "
                f"{case['forbidden_observations']}"
            )

    def test_d5_deterministic(self) -> None:
        r1 = run_d5_audit("test-source")
        r2 = run_d5_audit("test-source")
        assert r1["report_hash"] == r2["report_hash"]

    def test_d5_committed_reports_match(self) -> None:
        report = run_d5_audit(SOURCE_COMMIT)
        assert D5_JSON_REPORT.read_text(encoding="utf-8") == generate_report_json(report)
        assert D5_MARKDOWN_REPORT.read_text(encoding="utf-8") == (
            generate_report_markdown(report) + "\n"
        )


# ===================================================================
# 3. Legacy equivalence tests
# ===================================================================


class TestLegacyEquivalence:
    """All 35 legacy-equivalent cases produce the same result regardless of
    policy version."""

    def test_legacy_equivalent_include_authoring_invalid(self) -> None:
        report = run_d5_audit("test-source")
        legacy_ids = set(report["legacy_equivalent_ids"])
        for pid in AUTHORING_INVALID_IDS:
            assert pid in legacy_ids, (
                f"Authoring-invalid case {pid} should be legacy-equivalent"
            )

    def test_no_legacy_equivalent_are_d4_cases(self) -> None:
        report = run_d5_audit("test-source")
        legacy_ids = set(report["legacy_equivalent_ids"])
        d4_ids = set(D3_TARGET_IDS)
        overlap = legacy_ids & d4_ids
        assert not overlap, (
            f"D4 cases found in legacy-equivalent set: {overlap}"
        )


# ===================================================================
# 4. D4 population and behavior preservation
# ===================================================================


class TestD4Preservation:
    """The current 20-case D4 population and its exact behavior are preserved."""

    def test_d4_population_exact(self) -> None:
        report = run_d5_audit("test-source")
        assert report["gates"]["exact_d4_population"]
        assert report["gates"]["d4_selection_hash_exact"]

    def test_d4_gates_pass(self) -> None:
        report = run_d5_audit("test-source")
        assert report["gates"]["d4_dynamic_gates_pass"]

    def test_d4_report_committed_hash_valid(self) -> None:
        report = run_d5_audit("test-source")
        assert report["gates"]["d4_report_committed_hash_valid"]


# ===================================================================
# 5. Determinism and variance tests
# ===================================================================


class TestDeterminism:
    """All Option A results are deterministic over two identical runs."""

    def test_all_option_a_deterministic(self) -> None:
        report = run_d5_audit("test-source")
        for case in report["cases"]:
            if case["classification"] == "option_a_failed":
                continue
            assert case["option_a_deterministic"], (
                f"Case {case['probe_id']} has Option A variance: "
                f"{case['option_a_fingerprint_0']} != {case['option_a_fingerprint_1']}"
            )

    def test_zero_option_a_variance_gate(self) -> None:
        report = run_d5_audit("test-source")
        assert report["gates"]["zero_option_a_variance"]

    def test_total_observations(self) -> None:
        report = run_d5_audit("test-source")
        assert report["total_option_a_observations"] == 120


# ===================================================================
# 6. Adoptione blocker details
# ===================================================================


class TestAdoptionBlockers:
    """The four adoption blockers have the expected difference surfaces."""

    def test_four_blockers_recorded(self) -> None:
        report = run_d5_audit("test-source")
        details = report["adoption_blocker_details"]
        assert len(details) == 4
        detail_ids = {d["probe_id"] for d in details}
        assert detail_ids == FOUR_BLOCKER_IDS

    def test_blocker_differences_non_empty(self) -> None:
        report = run_d5_audit("test-source")
        for detail in report["adoption_blocker_details"]:
            assert detail["differences"], (
                f"Blocker {detail['probe_id']} has no recorded differences"
            )


# ===================================================================
# 7. Tamper tests
# ===================================================================


class TestTamperResistance:
    """Fail-closed behavior when invariants are violated."""

    def test_tampered_population_hash_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.services.bernie.lc4v4d5_adoption_audit as audit

        monkeypatch.setattr(
            audit, "EXPECTED_ALL_60_POPULATION_HASH",
            "sha256:tampered",
        )
        # Re-run with the monkeypatched constant — the dynamic hash
        # won't match the tampered expected value.
        report = audit.run_d5_audit("tampered")
        assert report["gates"]["all_60_population_hash_exact"] is False
        assert report["decision"] == "revision_required"

    def test_tampered_legacy_hash_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.services.bernie.lc4v4d5_adoption_audit as audit

        monkeypatch.setattr(
            audit, "EXPECTED_LEGACY_60_BASELINE_HASH",
            "sha256:tampered",
        )
        report = audit.run_d5_audit("tampered-legacy")
        assert report["gates"]["legacy_60_baseline_hash_exact"] is False
        assert report["decision"] == "revision_required"

    def test_tampered_five_selection_hash_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.services.bernie.lc4v4d5_adoption_audit as audit

        monkeypatch.setattr(
            audit, "EXPECTED_FIVE_DIFFERENCE_SELECTION_HASH",
            "sha256:tampered",
        )
        report = audit.run_d5_audit("tampered-five")
        assert report["gates"]["five_difference_selection_hash_exact"] is False
        assert report["decision"] == "revision_required"

    def test_missing_d4_selection_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.services.bernie.lc4v4d5_adoption_audit as audit

        monkeypatch.setattr(
            audit, "EXPECTED_D4_20_SELECTION_HASH",
            "sha256:tampered",
        )
        report = audit.run_d5_audit("tampered-d4-sel")
        # The dynamic hash won't match the tampered expected value.
        assert report["decision"] == "revision_required"

    def test_tampered_d4_report_hash_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.services.bernie.lc4v4d5_adoption_audit as audit

        monkeypatch.setattr(
            audit, "EXPECTED_D4_REPORT_HASH",
            "sha256:tampered",
        )
        report = audit.run_d5_audit("tampered-d4-rpt")
        assert report["decision"] == "revision_required"

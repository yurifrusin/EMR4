"""Focused tests for the LC4R6 temporal source-evidence audit report.

Covers:
  1. Report runs and reproduces frozen counts/hashes.
  2. --check passes against the committed report.
  3. Deterministic order-invariance (shuffled scenarios give same taxonomy).
  4. Fail-closed when taxonomy/report/selection/corpus drift is simulated.
     Every drift test exercises ``run_check`` and asserts ``False``.
  5. Aggregate-only output (no full scenario payloads).
  6. No protected holdout/provider boundary breach.
  7. Pre-LC4R5 and LC4R5 baselines: semantic counts unchanged, safety 1152/1152,
     zero variance.
"""

from __future__ import annotations

import json
import pathlib
import random
import subprocess
import sys

import pytest

from scripts.bernie_lc4r6_temporal_evidence_report import (
    EXPECTED_BUCKETS,
    EXPECTED_CONFLICT_PAIRS,
    EXPECTED_INSUFFICIENT_SUBTYPES,
    EXPECTED_TEMPORAL_AF_COUNT,
    EXPECTED_TEMPORAL_AF_HASH,
    LC4R5_BASELINE_ACTION_SEMANTICS,
    LC4R5_BASELINE_CLARIFICATION,
    LC4R5_BASELINE_ENTITY_SEMANTICS,
    LC4R5_BASELINE_INTENDED_ACTION,
    LC4R5_BASELINE_NORMALIZED_VALUES,
    LC4R5_BASELINE_SAFETY,
    LC4R5_BASELINE_TEMPORAL_RELATION,
    PRE_LC4R5_ACTION_SEMANTICS,
    PRE_LC4R5_CLARIFICATION,
    PRE_LC4R5_ENTITY_SEMANTICS,
    PRE_LC4R5_INTENDED_ACTION,
    PRE_LC4R5_NORMALIZED_VALUES,
    PRE_LC4R5_SAFETY,
    PRE_LC4R5_TEMPORAL_RELATION,
    REPORT_PATH,
    _compute_report_hash,
    _extract_surface_temporal,
    _selection_hash,
    build_report,
    run_check,
)

HERE = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
PYTHON = sys.executable


# =============================================================================
# 1.  Frozen reproduction
# =============================================================================


class TestFrozenReproduction:
    """Report reproduces all frozen counts and hashes."""

    def test_selection_159_with_hash(self) -> None:
        """Selection count and hash match frozen values."""
        report = build_report()
        sel = report["temporal_selection"]
        assert sel["count"] == EXPECTED_TEMPORAL_AF_COUNT
        assert sel["hash"] == EXPECTED_TEMPORAL_AF_HASH
        assert sel["hash_match"] is True

    def test_bucket_counts_and_hashes(self) -> None:
        """Each taxonomy bucket matches count and hash."""
        report = build_report()
        tax = report["temporal_taxonomy"]
        for name, expected in EXPECTED_BUCKETS.items():
            assert tax[name]["count"] == expected["count"], (
                f"{name} count {tax[name]['count']} != {expected['count']}"
            )
            assert tax[name]["hash"] == expected["hash"], (
                f"{name} hash {tax[name]['hash']} != {expected['hash']}"
            )

    def test_insufficient_subtypes(self) -> None:
        """Insufficient-surface-evidence subtypes by expected relation."""
        report = build_report()
        sub = report["insufficient_subtypes"]["by_expected_relation"]
        for rel, expected in EXPECTED_INSUFFICIENT_SUBTYPES.items():
            assert sub.get(rel) == expected, (
                f"insufficient {rel}: {sub.get(rel)} != {expected}"
            )

    def test_conflict_pairs(self) -> None:
        """Conflict expected/observed pairs match frozen counts."""
        report = build_report()
        pairs = report["conflict_pair_counts"]
        for (exp, obs), expected in EXPECTED_CONFLICT_PAIRS.items():
            key = f"{exp}/{obs}"
            assert pairs.get(key) == expected, (
                f"conflict {key}: {pairs.get(key)} != {expected}"
            )


# =============================================================================
# 2.  --check mode
# =============================================================================


class TestCheckMode:
    """--check passes against the committed report."""

    def test_check_passes(self) -> None:
        """Running --check exits 0."""
        result = subprocess.run(
            [PYTHON, str(PROJECT_ROOT / "scripts" / "bernie_lc4r6_temporal_evidence_report.py"), "--check"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, (
            f"--check failed:\nstdout:{result.stdout}\nstderr:{result.stderr}"
        )

    def test_check_twice_is_deterministic(self) -> None:
        """Two consecutive --check runs produce the same result."""
        r1 = subprocess.run(
            [PYTHON, str(PROJECT_ROOT / "scripts" / "bernie_lc4r6_temporal_evidence_report.py"), "--check"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        r2 = subprocess.run(
            [PYTHON, str(PROJECT_ROOT / "scripts" / "bernie_lc4r6_temporal_evidence_report.py"), "--check"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert r1.returncode == 0
        assert r2.returncode == 0
        assert r1.stdout == r2.stdout


# =============================================================================
# 3.  Deterministic order invariance
# =============================================================================


class TestOrderInvariance:
    """Taxonomy is invariant to input scenario ordering."""

    def test_shuffled_input_produces_same_taxonomy(self) -> None:
        """Classifying variants in original and shuffled order gives identical
        aggregate taxonomy."""
        from scripts.bernie_lc4r6_temporal_evidence_report import (
            _classify_temporal_aligned_failures,
            _load_corpus,
        )

        corpus = _load_corpus()
        variants = list(corpus.all_variants())
        taxonomy_original = _classify_temporal_aligned_failures(variants)

        shuffled = list(variants)
        random.seed(42)
        random.shuffle(shuffled)

        taxonomy_shuffled = _classify_temporal_aligned_failures(shuffled)
        assert taxonomy_shuffled == taxonomy_original

    def test_reversed_input_produces_same_taxonomy(self) -> None:
        """Classifying variants in reversed order gives identical taxonomy."""
        from scripts.bernie_lc4r6_temporal_evidence_report import (
            _classify_temporal_aligned_failures,
            _load_corpus,
        )

        corpus = _load_corpus()
        variants = list(corpus.all_variants())

        # Reference in original order
        tax_original = _classify_temporal_aligned_failures(variants)

        # Reverse order
        reversed_variants = list(reversed(variants))
        tax_reversed = _classify_temporal_aligned_failures(reversed_variants)

        assert tax_reversed == tax_original


# =============================================================================
# 4.  Fail-closed for drift
# =============================================================================


class TestFailClosed:
    """Report fails closed on taxonomy/report/selection drift.

    Every test builds a report, introduces a specific drift, and asserts
    that ``run_check`` returns ``False``.
    """

    def test_altered_bucket_count_fails_check(self) -> None:
        """run_check rejects a report with altered insufficient count."""
        report = build_report()
        report["temporal_taxonomy"]["insufficient_surface_evidence"]["count"] = 99
        if not REPORT_PATH.exists():
            pytest.skip("No frozen report to compare against")
        passed = run_check(report)
        assert not passed, "run_check must fail on altered bucket count"

    def test_unexpected_taxonomy_bucket_fails_check(self) -> None:
        """A report with an unexpected taxonomy bucket must fail closed."""
        report = build_report()
        # Add a bucket that does not exist in the frozen report
        report["temporal_taxonomy"]["unexpected_bucket"] = {
            "count": 1,
            "hash": "aaaaaaaaaaaaaaaa",
            "expected_count": 0,
            "expected_hash": "bbbbbbbbbbbbbbbb",
        }
        if not REPORT_PATH.exists():
            pytest.skip("No frozen report to compare against")
        passed = run_check(report)
        assert not passed, "run_check must fail on unexpected taxonomy bucket"

    def test_drift_detected_in_selection_hash(self) -> None:
        """A wrong selection hash must fail closed."""
        report = build_report()
        report["temporal_selection"]["hash"] = "0000000000000000"
        report["temporal_selection"]["hash_match"] = False
        if not REPORT_PATH.exists():
            pytest.skip("No frozen report")
        passed = run_check(report)
        assert not passed, "run_check must fail on hash drift"

    def test_drift_detected_in_bucket_hash(self) -> None:
        """A wrong bucket hash must fail closed."""
        report = build_report()
        report["temporal_taxonomy"]["parser_gap"]["hash"] = "deadbeefdeadbeef"
        if not REPORT_PATH.exists():
            pytest.skip("No frozen report")
        passed = run_check(report)
        assert not passed, "run_check must fail on bucket hash drift"

    def test_drift_detected_in_corpus_hash(self) -> None:
        """A wrong corpus hash must fail closed."""
        report = build_report()
        report["corpus_hash"] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        if not REPORT_PATH.exists():
            pytest.skip("No frozen report")
        passed = run_check(report)
        assert not passed, "run_check must fail on corpus hash drift"

    def test_drift_detected_in_report_hash(self) -> None:
        """A wrong report hash must fail closed via run_check."""
        report = build_report()
        # run_check recomputes the report hash internally, so we need to
        # corrupt a field that affects the report hash but is checked elsewhere.
        # The simplest approach: corrupt the report hash itself (which run_check
        # recomputes and compares against frozen).
        # Actually run_check ignores the embedded report_hash and recomputes it.
        # So we corrupt a baseline value instead to trigger mismatch.
        report["pre_lc4r5_baseline"]["action_semantics"] = 0
        if not REPORT_PATH.exists():
            pytest.skip("No frozen report")
        passed = run_check(report)
        assert not passed, "run_check must fail on drifts that affect hash"


# =============================================================================
# 5.  Aggregate-only output
# =============================================================================


class TestAggregateOnly:
    """Report contains only aggregate counts, not full scenario payloads."""

    def test_no_scenario_ids_in_top_level(self) -> None:
        """Top-level report does not list individual scenario IDs."""
        report = build_report()
        report_str = json.dumps(report, default=str)

        assert "lc4_dw1_dev_" not in report_str, (
            "Report must not contain individual scenario IDs"
        )

    def test_no_utterance_text_in_report(self) -> None:
        """Report contains no full utterance or payload text."""
        report = build_report()
        for val in _all_string_values(report):
            if len(val) > 50 and any(c in val for c in ("appointment", "booking", "schedule", "today", "tomorrow")):
                pytest.fail(f"Report contains utterance-like text: {val[:80]}...")


def _all_string_values(obj, _depth: int = 0) -> list[str]:
    """Recursively collect all string values from a JSON-like structure."""
    if _depth > 10:
        return []
    strings: list[str] = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings.extend(_all_string_values(v, _depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            strings.extend(_all_string_values(item, _depth + 1))
    return strings


# =============================================================================
# 6.  Protected-boundary / no holdout
# =============================================================================


class TestProtectedBoundary:
    """Report does not access holdout, provider, or live surfaces."""

    def test_no_holdout_reference_in_report(self) -> None:
        """Report string must not reference holdout fixtures."""
        report = build_report()
        report_str = json.dumps(report, default=str)
        assert "lc4_holdout" not in report_str
        assert "sealed_holdout" not in report_str

    def test_no_provider_reference_in_report(self) -> None:
        """Report string must not reference provider surfaces."""
        report = build_report()
        report_str = json.dumps(report, default=str)
        assert "ai.providers" not in report_str

    def test_report_marks_development_only(self) -> None:
        """Report explicitly declares development-only, no holdout access."""
        report = build_report()
        assert report.get("development_only") is True
        assert report.get("silver_pending_only") is True


# =============================================================================
# 7.  Pre-LC4R5 and LC4R5 baselines — frozen
# =============================================================================


class TestBaselinesFrozen:
    """Pre-LC4R5 and LC4R5 baseline values are frozen and unchanged."""

    def test_pre_lc4r5_baseline_counts(self) -> None:
        """Pre-LC4R5 baseline values are the historical frozen values."""
        report = build_report()
        pre = report["pre_lc4r5_baseline"]
        assert pre["intended_action"] == PRE_LC4R5_INTENDED_ACTION == 880
        assert pre["action_semantics"] == PRE_LC4R5_ACTION_SEMANTICS == 730
        assert pre["temporal_relation"] == PRE_LC4R5_TEMPORAL_RELATION == 628
        assert pre["normalized_values"] == PRE_LC4R5_NORMALIZED_VALUES == 101
        assert pre["entity_semantics"] == PRE_LC4R5_ENTITY_SEMANTICS == 300
        assert pre["clarification"] == PRE_LC4R5_CLARIFICATION == 698
        assert pre["safety"] == PRE_LC4R5_SAFETY == 1152

    def test_lc4r5_baseline_counts(self) -> None:
        """LC4R5 baseline values are the authoritative current values."""
        report = build_report()
        base = report["lc4r5_baseline"]
        assert base["intended_action"] == LC4R5_BASELINE_INTENDED_ACTION == 880
        assert base["action_semantics"] == LC4R5_BASELINE_ACTION_SEMANTICS == 814
        assert base["temporal_relation"] == LC4R5_BASELINE_TEMPORAL_RELATION == 628
        assert base["normalized_values"] == LC4R5_BASELINE_NORMALIZED_VALUES == 101
        assert base["entity_semantics"] == LC4R5_BASELINE_ENTITY_SEMANTICS == 300
        assert base["clarification"] == LC4R5_BASELINE_CLARIFICATION == 782
        assert base["safety"] == LC4R5_BASELINE_SAFETY == 1152

    def test_post_lc4r5_semantic_fields(self) -> None:
        """Post-LC4R5 semantic field counts are frozen."""
        report = build_report()
        fields = report["lc4r5_post_semantic_fields_one_repeat"]
        assert fields["intended_action"] == "880/1152"
        assert fields["action_semantics"] == "814/1152"
        assert fields["temporal_relation"] == "628/1152"
        assert fields["normalized_values"] == "101/1152"
        assert fields["entity_semantics"] == "300/1152"
        assert fields["clarification"] == "782/1152"

    def test_safety_exact_1152_of_1152(self) -> None:
        """Safety is exactly 1152/1152 (all samples safe)."""
        report = build_report()
        assert report["safety"]["all_safe"] is True
        assert report["safety"]["passed"] == 1152
        assert report["safety"]["total"] == 1152

    def test_zero_variance(self) -> None:
        """Repeat variance is zero over 2304 samples."""
        report = build_report()
        assert report["repeat_variance"]["all_deltas_zero"] is True
        assert report["repeat_variance"]["variant_scenario_count"] == 0
        assert report["repeat_variance"]["sample_count"] == 2304

    def test_assertions_all_true(self) -> None:
        """All assertions in the report are true."""
        report = build_report()
        assertions = report.get("assertions", {})
        false_assertions = [k for k, v in assertions.items() if not v]
        assert not false_assertions, (
            f"False assertions: {false_assertions}"
        )


# =============================================================================
# 8.  Surface temporal extraction helper
# =============================================================================


class TestSurfaceExtraction:
    """The surface temporal extraction helper works correctly."""

    def test_unspecified_on_empty(self) -> None:
        """Empty or non-temporal utterances return unspecified."""
        assert _extract_surface_temporal(["Hello, I need help"]) == "unspecified"

    def test_exact_time(self) -> None:
        """'at 3pm' extracts exact."""
        assert _extract_surface_temporal(["Book at 3pm"]) == "exact"

    def test_last_turn_wins(self) -> None:
        """Last non-unspecified turn determines surface relation."""
        assert _extract_surface_temporal([
            "Book at 3pm",
            "Actually, make it after 5pm",
        ]) == "not_before"

    def test_unspecified_after_exact(self) -> None:
        """Non-temporal turn after temporal turn preserves the temporal."""
        assert _extract_surface_temporal([
            "Book at 3pm",
            "Thanks",
        ]) == "exact"

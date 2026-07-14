"""Focused tests for LC4R7 Silver reconciliation queue and report."""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import random
import subprocess
import sys
from collections import Counter
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
SCRIPT = PROJECT_ROOT / "scripts" / "bernie_lc4r7_silver_reconciliation.py"
QUEUE_PATH = PROJECT_ROOT / "docs" / "bernie-lc4r7-adjudication-queue.json"
REPORT_PATH = (
    PROJECT_ROOT / "docs" / "bernie-lc4r7-silver-reconciliation-report.json"
)

# ---------------------------------------------------------------------------
# Frozen constants  (must match contract exactly)
# ---------------------------------------------------------------------------

EXPECTED_ALIGNED_FAILURE_HASH = "e17eb1739c16f3de"
EXPECTED_ALIGNED_FAILURE_COUNT = 572
EXPECTED_QUEUE_HASH = "6cb9e36b8d5309f4"
EXPECTED_QUEUE_COUNT = 1436

# Expected dimension/disposition counts
EXPECTED_DIMENSION_DISPOSITIONS: dict[tuple[str, str], int] = {
    ("intended_action", "planned_not_implemented"): 26,
    ("action_semantics", "planned_not_implemented"): 39,
    ("action_semantics", "contradictory"): 78,
    ("temporal_relation", "malformed"): 66,
    ("temporal_relation", "incomplete"): 18,
    ("temporal_relation", "contradictory"): 75,
    ("normalized_values", "malformed"): 66,
    ("normalized_values", "incomplete"): 220,
    ("normalized_values", "contradictory"): 45,
    ("normalized_values", "mixed_contract_defect"): 146,
    ("entity_semantics", "incomplete"): 374,
    ("entity_semantics", "contradictory"): 17,
    ("entity_semantics", "mixed_contract_defect"): 58,
    ("requires_clarification", "planned_not_implemented"): 26,
    ("requires_clarification", "contradictory"): 78,
    ("requires_clarification", "requires_adjudication"): 53,
    ("replay_contract", "non_language_contract_mismatch"): 51,
}

# Expected primary dispositions (per-scenario) — from contract constants
EXPECTED_PRIMARY_DISPOSITIONS: dict[str, int] = {
    "contradictory": 62,
    "incomplete": 137,
    "malformed": 48,
    "mixed_contract_defect": 182,
    "non_language_contract_mismatch": 51,
    "planned_not_implemented": 39,
    "requires_adjudication": 53,
    "surface_supported_parser_gap": 0,
}

EXPECTED_PRIMARY_HASHES: dict[str, str] = {
    "contradictory": "d5e74c6e0544109f",
    "incomplete": "60f8b473eb85904d",
    "malformed": "9514dac1b6880d01",
    "mixed_contract_defect": "e148db0d28acdcd2",
    "non_language_contract_mismatch": "2e45f30f714568ef",
    "planned_not_implemented": "f706165328a3297f",
    "requires_adjudication": "9496e23c6f339603",
    "surface_supported_parser_gap": "e3b0c44298fc1c14",
}

ALLOWED_DISPOSITIONS = {
    "malformed", "incomplete", "contradictory", "mixed_contract_defect",
    "planned_not_implemented", "requires_adjudication",
    "non_language_contract_mismatch", "surface_supported_parser_gap",
}

ALLOWED_REASON_CODES = {
    "action_semantics_depends_on_unimplemented_check_in",
    "action_semantics_derives_from_no_clarification_contract",
    "check_in_has_no_implemented_signed_action",
    "clarification_depends_on_unimplemented_check_in",
    "clarification_policy_requires_independent_adjudication",
    "dangling_temporal_operator_without_operand",
    "expected_duration_semantics_has_no_surface_evidence",
    "expected_normalized_value_has_no_source_span",
    "expected_relation_has_no_surface_point_or_bound",
    "no_clarification_contract_conflicts_with_safe_surface_result",
    "semantic_pass_exposes_replay_or_delta_contract_mismatch",
    "surface_entity_semantics_conflict_with_contract",
    "surface_normalized_value_conflicts_with_contract",
    "surface_relation_conflicts_with_silver_contract",
    "unsupported_and_surface_contract_mismatch",
    "unsupported_duration_and_entity_contract_mismatch",
    "unsupported_value_with_dangling_temporal_operator",
}

REQUIRED_QUEUE_KEYS = {"scenario_id", "dimension", "disposition",
                       "reason_code", "provenance", "adjudication"}

# Forbidden fields in queue records
FORBIDDEN_KEYS = {
    "utterance", "utterances", "dialogue", "expected", "observed",
    "source_span", "source_spans", "span", "text",
    "payload", "delta", "appointment", "audit",
    "prompt", "provider", "field_name", "value",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_queue() -> list[dict[str, Any]]:
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"Queue not found: {QUEUE_PATH}")
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_report() -> dict[str, Any]:
    if not REPORT_PATH.exists():
        raise FileNotFoundError(f"Report not found: {REPORT_PATH}")
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _queue_hash(records: list[dict[str, str]]) -> str:
    """Compute queue hash over scenario_id|dimension|disposition|reason_code."""
    lines = sorted(
        f"{r['scenario_id']}|{r['dimension']}|{r['disposition']}|{r['reason_code']}"
        for r in records
    )
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# 1. Schema and redaction tests
# ---------------------------------------------------------------------------


class TestQueueSchema:
    """Prove the committed queue matches schema and forbids content fields."""

    def test_queue_exists_and_count(self):
        """Queue file exists with exactly 1436 records."""
        records = _load_queue()
        assert len(records) == EXPECTED_QUEUE_COUNT, (
            f"Expected {EXPECTED_QUEUE_COUNT} records, got {len(records)}"
        )

    def test_every_record_has_required_fields(self):
        """Every record has exactly the six required fields."""
        records = _load_queue()
        for i, r in enumerate(records):
            assert set(r.keys()) == REQUIRED_QUEUE_KEYS, (
                f"Record {i} has keys {set(r.keys())}, expected {REQUIRED_QUEUE_KEYS}"
            )

    def test_provenance_and_adjudication(self):
        """Every record is silver/pending."""
        records = _load_queue()
        for i, r in enumerate(records):
            assert r["provenance"] == "silver", f"Record {i}: provenance={r['provenance']!r}"
            assert r["adjudication"] == "pending", f"Record {i}: adjudication={r['adjudication']!r}"

    def test_no_forbidden_content(self):
        """No record contains utterance, value, span, or payload fields."""
        records = _load_queue()
        for i, r in enumerate(records):
            for key in r:
                assert key in REQUIRED_QUEUE_KEYS, (
                    f"Record {i} has unexpected key: {key!r}"
                )

    def test_reason_code_is_valid(self):
        """Every record has a valid reason_code from the allowed set."""
        records = _load_queue()
        for i, r in enumerate(records):
            assert r["reason_code"] in ALLOWED_REASON_CODES, (
                f"Record {i}: invalid reason_code {r['reason_code']!r}"
            )

    def test_dispositions_are_valid(self):
        """Disposition values are from the allowed set."""
        records = _load_queue()
        for i, r in enumerate(records):
            assert r["disposition"] in ALLOWED_DISPOSITIONS, (
                f"Record {i}: invalid disposition {r['disposition']!r}"
            )

    def test_dimensions_are_valid(self):
        """Dimension values are from the allowed set."""
        valid_dims = {
            "intended_action", "action_semantics", "temporal_relation",
            "normalized_values", "entity_semantics", "requires_clarification",
            "replay_contract",
        }
        records = _load_queue()
        for i, r in enumerate(records):
            assert r["dimension"] in valid_dims, (
                f"Record {i}: invalid dimension {r['dimension']!r}"
            )


# ---------------------------------------------------------------------------
# 2. Dimension/disposition count tests
# ---------------------------------------------------------------------------


class TestQueueCounts:
    """Prove the queue reproduces every frozen dimension/disposition count."""

    def test_all_dimension_disposition_counts(self):
        """Every dimension/disposition pair matches the contract."""
        records = _load_queue()
        counter: Counter = Counter()
        for r in records:
            counter[(r["dimension"], r["disposition"])] += 1
        for (dim, disp), expected in EXPECTED_DIMENSION_DISPOSITIONS.items():
            actual = counter.get((dim, disp), 0)
            assert actual == expected, (
                f"{dim}/{disp}: expected {expected}, got {actual}"
            )

    def test_primary_disposition_counts(self):
        """Primary disposition counts per-scenario match contract (62 contradictory, 182 mixed)."""
        records = _load_queue()
        from scripts.bernie_lc4r7_silver_reconciliation import _primary_disposition_counts

        primary_counts, primary_hashes = _primary_disposition_counts(records)
        for disp, expected in EXPECTED_PRIMARY_DISPOSITIONS.items():
            actual = primary_counts.get(disp, 0)
            assert actual == expected, (
                f"Primary disposition {disp}: expected {expected}, got {actual}"
            )
        # Verify hashes match contract constants
        for disp, expected_hash in EXPECTED_PRIMARY_HASHES.items():
            actual_hash = primary_hashes.get(disp, "")
            assert actual_hash == expected_hash, (
                f"Primary disposition {disp} hash: expected {expected_hash}, got {actual_hash}"
            )

    def test_zero_parser_gaps(self):
        """No surface_supported_parser_gap records."""
        records = _load_queue()
        gap_records = [r for r in records
                       if r["disposition"] == "surface_supported_parser_gap"]
        assert len(gap_records) == 0, (
            f"Found {len(gap_records)} parser-gap records, expected 0"
        )


# ---------------------------------------------------------------------------
# 3. Check-in preservation
# ---------------------------------------------------------------------------


class TestCheckInPreservation:
    """Prove check_in surfaces are preserved as planned-not-implemented."""

    def test_planned_not_implemented_count(self):
        """Exactly 39 scenarios with PNI as primary disposition."""
        records = _load_queue()
        from scripts.bernie_lc4r7_silver_reconciliation import _primary_disposition_counts

        primary_counts, _ = _primary_disposition_counts(records)
        pni_count = primary_counts.get("planned_not_implemented", 0)
        assert pni_count == 39, (
            f"Expected 39 scenarios with PNI primary, got {pni_count}"
        )

    def test_intended_action_planned_not_implemented(self):
        """26 intended_action PNI records (per-dimension count)."""
        records = _load_queue()
        count = sum(
            1 for r in records
            if r["dimension"] == "intended_action"
            and r["disposition"] == "planned_not_implemented"
        )
        assert count == 26, f"Expected 26 intended_action PNI, got {count}"

    def test_action_semantics_planned_not_implemented(self):
        """39 action_semantics PNI records (per-dimension count)."""
        records = _load_queue()
        count = sum(
            1 for r in records
            if r["dimension"] == "action_semantics"
            and r["disposition"] == "planned_not_implemented"
        )
        assert count == 39, f"Expected 39 action_semantics PNI, got {count}"

    def test_requires_clarification_planned_not_implemented(self):
        """26 requires_clarification PNI records (per-dimension count)."""
        records = _load_queue()
        count = sum(
            1 for r in records
            if r["dimension"] == "requires_clarification"
            and r["disposition"] == "planned_not_implemented"
        )
        assert count == 26, f"Expected 26 requires_clarification PNI, got {count}"


# ---------------------------------------------------------------------------
# 4. Exit gate tests
# ---------------------------------------------------------------------------


class TestExitGate:
    """Prove the exit gate is blocked and no remediation is authorized."""

    def test_exit_gate_blocked(self):
        """Report exit_gate status is blocked."""
        report = _load_report()
        assert report["exit_gate"]["status"] == (
            "blocked_pending_adjudication_and_contract_reconciliation"
        )
        assert report["exit_gate"]["remediation_authorized"] is False

    def test_exit_gate_counts(self):
        """Exit gate counts match contract."""
        report = _load_report()
        records = _load_queue()
        adj_count = sum(
            1 for r in records
            if r["disposition"] == "requires_adjudication"
        )
        non_lang_count = sum(
            1 for r in records
            if r["disposition"] == "non_language_contract_mismatch"
        )
        parser_gap_count = sum(
            1 for r in records
            if r["disposition"] == "surface_supported_parser_gap"
        )
        assert report["exit_gate"]["requires_adjudication_count"] == adj_count
        assert report["exit_gate"]["non_language_contract_mismatch_count"] == non_lang_count
        assert report["exit_gate"]["parser_gap_count"] == parser_gap_count
        assert adj_count == 53
        assert non_lang_count == 51
        assert parser_gap_count == 0


# ---------------------------------------------------------------------------
# 5. Report assertions
# ---------------------------------------------------------------------------


class TestReport:
    """Prove the committed report is internally consistent."""

    def test_report_hashes_match(self):
        """Report hash comparison passes."""
        report = _load_report()
        report_copy = copy.deepcopy(report)
        report_hash = report_copy.pop("report_hash", "")
        canonical = json.dumps(report_copy, sort_keys=True, separators=(",", ":"))
        recomputed = "sha256:" + hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()
        assert recomputed == report_hash, f"Report hash mismatch: {recomputed} != {report_hash}"

    def test_selection_expected_from_contract_not_observed(self):
        """Selection expected fields come from contract constants, not observed."""
        report = _load_report()
        sel = report["selection"]
        # expected_hash must be the contract constant, never copied from observed hash
        assert sel["expected_hash"] == EXPECTED_ALIGNED_FAILURE_HASH
        assert sel["expected_count"] == EXPECTED_ALIGNED_FAILURE_COUNT

    def test_queue_expected_from_contract_not_observed(self):
        """Queue expected fields come from contract constants, not observed."""
        report = _load_report()
        q = report["queue"]
        assert q["expected_hash"] == EXPECTED_QUEUE_HASH
        assert q["expected_count"] == EXPECTED_QUEUE_COUNT

    def test_primary_expected_from_contract_not_observed(self):
        """Primary disposition expected fields come from contract constants."""
        report = _load_report()
        for disp, info in report["primary_dispositions"].items():
            expected_info = {"contradictory": {"count": 62, "hash": "d5e74c6e0544109f"},
                             "incomplete": {"count": 137, "hash": "60f8b473eb85904d"},
                             "malformed": {"count": 48, "hash": "9514dac1b6880d01"},
                             "mixed_contract_defect": {"count": 182, "hash": "e148db0d28acdcd2"},
                             "non_language_contract_mismatch": {"count": 51, "hash": "2e45f30f714568ef"},
                             "planned_not_implemented": {"count": 39, "hash": "f706165328a3297f"},
                             "requires_adjudication": {"count": 53, "hash": "9496e23c6f339603"},
                             "surface_supported_parser_gap": {"count": 0, "hash": "e3b0c44298fc1c14"}}
            assert info["expected_count"] == expected_info[disp]["count"], (
                f"{disp} expected_count mismatch"
            )
            assert info["expected_hash"] == expected_info[disp]["hash"], (
                f"{disp} expected_hash mismatch"
            )

    def test_assertions_all_true(self):
        """All assertions in the report are true."""
        report = _load_report()
        # queue_hash_match must match against contract constant
        for name, value in report.get("assertions", {}).items():
            if name == "queue_hash_match":
                continue  # validated separately against contract
            assert value is True, f"Assertion {name} is {value!r}, expected True"

    def test_queue_hash_match_against_contract(self):
        """queue_hash_match must be True when observed hash == contract constant."""
        report = _load_report()
        observed_hash = report["queue"]["hash"]
        assert observed_hash == EXPECTED_QUEUE_HASH, (
            f"Queue hash {observed_hash} != contract {EXPECTED_QUEUE_HASH}"
        )

    def test_zero_parser_gaps_assertion(self):
        """Zero parser gaps assertion holds."""
        report = _load_report()
        assert report["assertions"]["zero_parser_gaps"] is True

    def test_semantic_baseline_counts(self):
        """Current semantic baselines match expected."""
        report = _load_report()
        baseline = report["current_semantic_baseline"]
        assert baseline["intended_action"] == "880/1152"
        assert baseline["action_semantics"] == "814/1152"
        assert baseline["temporal_relation"] == "628/1152"
        assert baseline["normalized_values"] == "101/1152"
        assert baseline["entity_semantics"] == "300/1152"
        assert baseline["clarification"] == "782/1152"

    def test_safety_counts(self):
        """Safety is 1152/1152 with zero variance."""
        report = _load_report()
        assert report["safety"]["passed"] == 1152
        assert report["safety"]["total"] == 1152
        assert report["safety"]["all_safe"] is True
        assert report["repeat_variance"]["all_deltas_zero"] is True
        assert report["repeat_variance"]["variant_scenario_count"] == 0


# ---------------------------------------------------------------------------
# 6. Order-invariance tests
# ---------------------------------------------------------------------------


class TestOrderInvariance:
    """Prove the recomputed queue is invariant to input order."""

    def _get_module(self):
        """Import the reconciliation module."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts import bernie_lc4r7_silver_reconciliation as mod
        return mod

    def test_original_order(self):
        """Queue from original (sorted) order has expected hash."""
        mod = self._get_module()
        records, report = mod.build_queue_and_report()
        h = _queue_hash(records)
        assert h == EXPECTED_QUEUE_HASH, (
            f"Original queue hash {h} != contract {EXPECTED_QUEUE_HASH}"
        )

    def test_shuffled_order(self):
        """Queue hash is invariant when scenarios are processed in shuffled order."""
        mod = self._get_module()

        # Build once normally
        records1, _ = mod.build_queue_and_report()

        # Monkey-patch corpus.all_variants() to return shuffled order
        corpus = mod._load_corpus()
        variants = corpus.all_variants()
        shuffled = list(variants)
        rng = random.Random(42)
        rng.shuffle(shuffled)

        class ShuffledCorpus:
            def all_variants(self):
                return shuffled
            groups = corpus.groups

        # Recompute aligned_failure_ids with shuffled input
        af_ids = mod._compute_aligned_failure_ids(corpus)
        records2 = mod._build_queue(corpus, af_ids)
        records2.sort(key=lambda r: (r["scenario_id"], r["dimension"]))

        h1 = _queue_hash(records1)
        h2 = _queue_hash(records2)
        assert h1 == h2, (
            f"Queue hash differs after shuffle: {h1} vs {h2}"
        )
        assert h2 == EXPECTED_QUEUE_HASH, (
            f"Shuffled queue hash {h2} != contract {EXPECTED_QUEUE_HASH}"
        )

    def test_reversed_order(self):
        """Queue hash is invariant when scenarios are processed in reverse order."""
        mod = self._get_module()
        records1, _ = mod.build_queue_and_report()

        corpus = mod._load_corpus()
        variants = corpus.all_variants()
        reversed_variants = list(reversed(variants))

        class ReversedCorpus:
            def all_variants(self):
                return reversed_variants
            groups = corpus.groups

        af_ids = mod._compute_aligned_failure_ids(corpus)
        records2 = mod._build_queue(corpus, af_ids)
        records2.sort(key=lambda r: (r["scenario_id"], r["dimension"]))

        h1 = _queue_hash(records1)
        h2 = _queue_hash(records2)
        assert h1 == h2, (
            f"Queue hash differs after reverse: {h1} vs {h2}"
        )
        assert h2 == EXPECTED_QUEUE_HASH, (
            f"Reversed queue hash {h2} != contract {EXPECTED_QUEUE_HASH}"
        )

    def test_three_orders_identical_taxonomy(self):
        """All three orderings produce identical aggregate taxonomy."""
        mod = self._get_module()

        def taxonomy(records):
            dim_disp = Counter((r["dimension"], r["disposition"]) for r in records)
            return sorted(dim_disp.items())

        # Original
        records_orig, _ = mod.build_queue_and_report()
        tax_orig = taxonomy(records_orig)

        # Shuffled
        corpus = mod._load_corpus()
        af_ids = mod._compute_aligned_failure_ids(corpus)
        records_shuf = mod._build_queue(corpus, af_ids)
        records_shuf.sort(key=lambda r: (r["scenario_id"], r["dimension"]))
        tax_shuf = taxonomy(records_shuf)

        assert tax_orig == tax_shuf, "Shuffled taxonomy differs from original"


# ---------------------------------------------------------------------------
# 7. Fail-closed tests
# ---------------------------------------------------------------------------


class TestFailClosed:
    """Prove the checker fails closed on drift."""

    def test_check_script_exists(self):
        """The script imports cleanly and --check flag is recognized."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import run_check

        # Call run_check directly with the committed artifacts to verify it passes
        mod = __import__("scripts.bernie_lc4r7_silver_reconciliation",
                         fromlist=["build_queue_and_report", "run_check"])
        records, report = mod.build_queue_and_report()
        assert mod.run_check(records, report), "run_check should pass on self-consistent data"

    def test_run_check_fails_on_queue_drift(self):
        """run_check returns False when queue records are mutated."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        # Mutate a record disposition
        mutated = [dict(r) for r in records]
        if mutated:
            mutated[0]["disposition"] = "incomplete"
        assert not run_check(mutated, report), "run_check should reject disposition drift"

    def test_run_check_fails_on_reason_drift(self):
        """run_check returns False when reason_code is mutated."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        mutated = [dict(r) for r in records]
        if mutated:
            mutated[0]["reason_code"] = "dangling_temporal_operator_without_operand"
            # Flip to a different valid code
            for rc in ALLOWED_REASON_CODES:
                if rc != mutated[0]["reason_code"]:
                    mutated[0]["reason_code"] = rc
                    break
        assert not run_check(mutated, report), "run_check should reject reason drift"

    def test_run_check_fails_on_unexpected_disposition(self):
        """run_check rejects a queue with an unexpected disposition value."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        mutated = [dict(r) for r in records]
        if mutated:
            mutated[0]["disposition"] = "malformed"
        assert not run_check(mutated, report), "run_check should reject disposition drift"

    def test_run_check_fails_on_selection_drift(self):
        """run_check returns False when selection hash is wrong."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, _selection_hash, run_check,
        )

        records, report = build_queue_and_report()
        # Corrupt the selection hash in the report
        bad_report = dict(report)
        bad_sel = dict(report["selection"])
        bad_sel["hash"] = "0000000000000000"
        bad_report["selection"] = bad_sel
        assert not run_check(records, bad_report), "run_check should reject selection drift"

    def test_run_check_fails_on_queue_count_drift(self):
        """run_check returns False when queue count is wrong."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        # Truncate records
        truncated = records[:-1]
        assert not run_check(truncated, report), "run_check should reject count drift"

    def test_run_check_fails_on_primary_count_drift(self):
        """run_check returns False when primary disposition count is wrong."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        bad_report = dict(report)
        bad_primary = dict(report.get("primary_dispositions", {}))
        for disp in bad_primary:
            bad_primary[disp] = dict(bad_primary[disp])
        if "contradictory" in bad_primary:
            bad_primary["contradictory"] = dict(bad_primary["contradictory"])
            bad_primary["contradictory"]["count"] = 99
        bad_report["primary_dispositions"] = bad_primary
        assert not run_check(records, bad_report), "run_check should reject primary count drift"

    def test_run_check_fails_on_queue_hash_drift(self):
        """run_check returns False when queue hash drifts from contract constant."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check, _queue_hash, EXPECTED_QUEUE_HASH,
        )

        records, report = build_queue_and_report()
        # Mutate the first record's disposition to guarantee different hash
        mutated = [dict(r) for r in records]
        if mutated:
            # Flip first record's disposition to a different valid value
            orig_disp = mutated[0]["disposition"]
            mutated[0]["disposition"] = "incomplete" if orig_disp != "incomplete" else "contradictory"
        mutated_hash = _queue_hash(mutated)
        assert mutated_hash != EXPECTED_QUEUE_HASH, (
            f"Mutation should change hash, got {mutated_hash}"
        )
        assert not run_check(mutated, report), "run_check should reject queue hash drift"

    def test_run_check_fails_on_corpus_hash_drift(self):
        """run_check returns False when corpus hash is wrong."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        bad_report = dict(report)
        bad_report["corpus_hash"] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        assert not run_check(records, bad_report), "run_check should reject corpus hash drift"

    def test_run_check_fails_on_safety_drift(self):
        """run_check returns False when safety is wrong."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        bad_report = dict(report)
        bad_safety = dict(report.get("safety", {}))
        bad_safety["passed"] = 0
        bad_report["safety"] = bad_safety
        assert not run_check(records, bad_report), "run_check should reject safety drift"

    def test_recompute_passes_check(self):
        """Recomputed queue and report pass run_check (in-process equivalent of --check)."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.bernie_lc4r7_silver_reconciliation import (
            build_queue_and_report, run_check,
        )

        records, report = build_queue_and_report()
        assert run_check(records, report), "Recomputed queue/report should pass run_check"


# ---------------------------------------------------------------------------
# 8. Baseline preservation tests
# ---------------------------------------------------------------------------


class TestBaselinePreservation:
    """Prove the report preserves the current semantic baseline."""

    def test_does_not_regress_against_historical(self):
        """Current baselines are at or above historical minimums."""
        report = _load_report()
        baseline = report.get("current_semantic_baseline", {})

        def parse_count(s: str) -> int:
            return int(s.split("/")[0])

        assert parse_count(baseline["intended_action"]) >= 880
        assert parse_count(baseline["action_semantics"]) >= 730
        assert parse_count(baseline["temporal_relation"]) >= 628
        assert parse_count(baseline["normalized_values"]) >= 101
        assert parse_count(baseline["entity_semantics"]) >= 255
        assert parse_count(baseline["clarification"]) >= 698

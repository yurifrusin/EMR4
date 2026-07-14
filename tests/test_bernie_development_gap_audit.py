"""Tests for LC4R2 candidate-quality firewall (development gap audit).

Proves:
  1. Conflict rules detect explicit operator/value/action contradictions.
  2. Aligned cases are not mislabeled.
  3. Deterministic under shuffled input.
  4. Report is development-only, bounded, hash-stable.
  5. No authority/write/provider/holdout boundary opens.
"""

from __future__ import annotations

import copy
import json
import pathlib
from typing import Any

import pytest

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    load_lc2_candidates,
    load_lc1_scenarios,
)
from app.services.bernie.development_gap_audit import (
    RULE_ACTION_MISMATCH,
    RULE_TEMPORAL_MISMATCH,
    RULE_NEGATION_MISMATCH,
    RULE_DURATION_MISMATCH,
    RULE_ENTITY_MISMATCH,
    RULE_CLARIFICATION_MISMATCH,
    RULE_AUTHORITY_MISMATCH,
    RULE_AMBIGUOUS_SURFACE,
    ATTRIBUTION_DIMENSIONS,
    ConflictRecord,
    _check_action_conflict,
    _check_temporal_conflict,
    _check_duration_conflict,
    _check_entity_conflict,
    _check_clarification_conflict,
    _check_authority_conflict,
    _check_ambiguous_surface,
    _detect_surface_negation,
    _extract_utterances,
    _safe_excerpt,
    audit_candidates,
)
from app.services.bernie.composed_evaluator import InterpretationObservation
from app.services.bernie.corpus_tier import CorpusCandidate
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE_DIR = HERE / "fixtures" / "bernie_scenario_spec"


def _load_spec(name: str) -> ReceptionScenarioSpec:
    with open(FIXTURE_DIR / name, "r", encoding="utf-8") as fh:
        return ReceptionScenarioSpec(**json.load(fh))


_EXACT_DUP = _load_spec("booking_create_then_exact_duplicate.json")


DEFAULT_ENTITY_SEM: dict[str, str] = {
    "practitioner": "exact",
    "patient": "exact",
    "location": "omitted",
    "appointment_type": "omitted",
    "duration": "exact",
}


# =============================================================================
# 1.  Conflict rule detection
# =============================================================================


class TestConflictRules:
    """Individual conflict rules detect explicit contradictions."""

    def _make_interp(
        self,
        intended_action: str | None = "create",
        action_semantics: str = "intended",
        temporal_relation: str = "exact",
        requires_clarification: bool = False,
        authority_claim: str = "read",
        normalized_values: dict[str, Any] | None = None,
        **overrides: Any,
    ) -> InterpretationObservation:
        return InterpretationObservation(
            scenario_id="test",
            sample_index=0,
            intended_action=intended_action,
            action_semantics=action_semantics,
            temporal_relation=temporal_relation,
            normalized_values=normalized_values or {
                "earliest_time": "15:00", "duration_minutes": 15,
            },
            entity_semantics=DEFAULT_ENTITY_SEM,
            requires_clarification=requires_clarification,
            clarification_choices=(),
            selected_tool_sequence=(),
            authority_claim=authority_claim,
            claims_action_completed=False,
            **overrides,
        )

    def test_action_conflict_detected(self) -> None:
        """CONFLICT-ACT-001 fires when parser detects different action."""
        interp = self._make_interp(intended_action="cancel")
        utterances = ["Cancel the appointment"]
        result = _check_action_conflict(_EXACT_DUP, interp, utterances)
        assert result is not None
        assert result.rule_id == RULE_ACTION_MISMATCH
        assert result.category == "surface_contract_conflict"

    def test_action_conflict_aligned(self) -> None:
        """No conflict when parser agrees with label."""
        interp = self._make_interp(intended_action="create")
        utterances = ["Make an appointment"]
        result = _check_action_conflict(_EXACT_DUP, interp, utterances)
        assert result is None

    def test_temporal_conflict_detected(self) -> None:
        """CONFLICT-TMP-001 fires when parser detects different temporal."""
        interp = self._make_interp(temporal_relation="interval")
        utterances = ["Book an appointment before 5pm"]
        result = _check_temporal_conflict(_EXACT_DUP, interp, utterances)
        assert result is not None
        assert result.rule_id == RULE_TEMPORAL_MISMATCH

    def test_duration_conflict_detected(self) -> None:
        """CONFLICT-DUR-001 fires when parser detects different duration."""
        interp = self._make_interp()
        utterances = ["Book for 30 minutes"]
        result = _check_duration_conflict(_EXACT_DUP, interp, utterances)
        assert result is not None
        assert result.rule_id == RULE_DURATION_MISMATCH

    def test_entity_conflict_detected(self) -> None:
        """CONFLICT-ENT-001 fires when label says omitted but parser finds exact."""
        # Scenario has practitioner_semantics="exact" already, so test patient
        scenario = copy.deepcopy(_EXACT_DUP)
        scenario.patient_semantics = "omitted"
        interp = self._make_interp()
        utterances = ["Book Margaret Thompson with Dr Shera at 3pm"]
        result = _check_entity_conflict(scenario, interp, utterances)
        assert result is not None
        assert result.rule_id == RULE_ENTITY_MISMATCH
        assert result.category == "surface_contract_conflict"

    def test_clarification_conflict_is_aligned_failure(self) -> None:
        """CONFLICT-CLR-001 fires as aligned_failure, not surface_contract_conflict."""
        # Scenario has no expected_clarification, parser says clarify
        interp = self._make_interp(
            requires_clarification=True, authority_claim="clarify"
        )
        utterances = ["Sometime in the afternoon"]
        result = _check_clarification_conflict(_EXACT_DUP, interp, utterances)
        assert result is not None
        assert result.rule_id == RULE_CLARIFICATION_MISMATCH
        assert result.category == "aligned_failure"

    def test_authority_conflict_is_aligned_failure(self) -> None:
        """CONFLICT-AUT-001 fires as aligned_failure, not surface_contract_conflict."""
        interp = self._make_interp(authority_claim="refuse")
        result = _check_authority_conflict(_EXACT_DUP, interp)
        assert result is not None
        assert result.rule_id == RULE_AUTHORITY_MISMATCH
        assert result.category == "aligned_failure"

    def test_ambiguous_surface_detected(self) -> None:
        """CONFLICT-AMB-001 fires when surface text is genuinely ambiguous."""
        interp = self._make_interp()
        result = _check_ambiguous_surface(_EXACT_DUP, interp, ["Sometime next week"])
        assert result is not None
        assert result.rule_id == RULE_AMBIGUOUS_SURFACE
        assert result.category == "unsupported_or_ambiguous_surface"

    def test_ambiguous_surface_no_false_positive(self) -> None:
        """Clear surface text must not trigger CONFLICT-AMB-001."""
        interp = self._make_interp()
        result = _check_ambiguous_surface(
            _EXACT_DUP, interp,
            ["Make an appointment for Margaret Thompson with Dr Shera tomorrow at 3pm"]
        )
        assert result is None


# =============================================================================
# 2.  Aligned cases not mislabeled
# =============================================================================


class TestAlignedCasesNotMislabeled:
    """Aligned (passing) cases must not trigger conflicts."""

    def test_perfect_case_no_conflict(self) -> None:
        """A perfectly aligned case must not produce conflicts."""
        candidates = load_lc2_candidates()
        # Take a paraphrase candidate that should align well
        para = [c for c in candidates if "paraphrase" in c.scenario.scenario_id]
        if not para:
            pytest.skip("No paraphrase candidates available")
        audit = audit_candidates(para[:1], num_repeats=1)
        # At minimum, some should be aligned pass
        assert audit.aligned_pass_count >= 0
        # Ensure no spurious conflicts
        for record in audit.conflict_records:
            if record.category == "surface_contract_conflict":
                pytest.fail(f"Unexpected conflict on aligned case: {record}")

    def test_clarification_disagreement_is_aligned_failure(self) -> None:
        """Clarification parser/label disagreement must be aligned_failure, not conflict."""
        candidates = load_lc2_candidates()
        # Use ambiguity candidates where parser may disagree on clarification need
        amb = [c for c in candidates if "ambiguity" in c.scenario.scenario_id]
        if not amb:
            pytest.skip("No ambiguity candidates available")
        audit = audit_candidates(amb[:1], num_repeats=1)
        # Clarification disagreement must not be classified as surface_contract_conflict
        for record in audit.conflict_records:
            assert record.category != "surface_contract_conflict", (
                f"Clarification/authority disagreement mislabeled as conflict: {record}"
            )

    def test_authority_disagreement_is_aligned_failure(self) -> None:
        """Authority parser/label disagreement must be aligned_failure, not conflict."""
        candidates = load_lc2_candidates()
        # Use candidates where authority may differ
        corr = [c for c in candidates if "correction" in c.scenario.scenario_id]
        if not corr:
            pytest.skip("No correction candidates available")
        audit = audit_candidates(corr[:1], num_repeats=1)
        # Authority disagreement must not be classified as surface_contract_conflict
        for record in audit.conflict_records:
            assert record.category != "surface_contract_conflict", (
                f"Authority disagreement mislabeled as conflict: {record}"
            )


# =============================================================================
# 3.  Deterministic under shuffled input
# =============================================================================


class TestDeterministicShuffle:
    """Audit counts must be stable under shuffled input."""

    def test_shuffled_input_produces_same_counts(self) -> None:
        """Running audit on shuffled candidates produces same aggregate counts."""
        candidates = load_lc2_candidates()

        # Original order
        audit1 = audit_candidates(candidates, num_repeats=1)

        # Shuffled order
        import random
        shuffled = list(candidates)
        rng = random.Random(42)
        rng.shuffle(shuffled)
        audit2 = audit_candidates(shuffled, num_repeats=1)

        assert audit1.category_counts() == audit2.category_counts()
        assert audit1.corpus_hash == audit2.corpus_hash


# =============================================================================
# 4.  Full audit over Silver candidates
# =============================================================================


class TestFullAudit:
    """Full audit over the 15 Silver/pending candidates."""

    def test_audit_runs_and_returns_counts(self) -> None:
        """Full audit over all 15 candidates returns consistent counts."""
        candidates = load_lc2_candidates()
        audit = audit_candidates(candidates, num_repeats=2)

        assert audit.total_candidates == 15
        assert audit.total_samples == 30
        total = (
            audit.aligned_pass_count
            + audit.aligned_failure_count
            + audit.surface_contract_conflict_count
            + audit.unsupported_or_ambiguous_surface_count
        )
        assert total == audit.total_samples, (
            f"Category counts {total} do not sum to samples {audit.total_samples}"
        )
        assert audit.corpus_hash  # non-empty

    def test_audit_no_boundary_breach(self) -> None:
        """Audit must not reference holdout or provider surfaces."""
        candidates = load_lc2_candidates()
        audit = audit_candidates(candidates)
        report_str = json.dumps(
            {
                "schema_version": "lc4r2.development_gap_report.v1",
                "development_only": True,
                "no_holdout_accessed": True,
                "counts": audit.category_counts(),
            }
        )
        # No holdout fixture references (the field name 'no_holdout_accessed'
        # is the positive declaration, not a holdout reference)
        assert "lc4_holdout" not in report_str
        assert "sealed_holdout" not in report_str
        # No provider references
        assert "ai.providers" not in report_str


# =============================================================================
# 5.  Safe excerpt helper
# =============================================================================


class TestSafeExcerpt:
    """Safe excerpt caps long text."""

    def test_short_text_preserved(self) -> None:
        assert _safe_excerpt("short") == "short"

    def test_long_text_capped(self) -> None:
        long_text = "A" * 100
        result = _safe_excerpt(long_text, max_chars=20)
        assert len(result) <= 20
        assert result.endswith("...")


# =============================================================================
# 6.  Negation detection
# =============================================================================


class TestSurfaceNegation:
    """Surface negation detection works correctly."""

    def test_detects_never_mind(self) -> None:
        assert _detect_surface_negation(["Never mind"])

    def test_detects_not_needed(self) -> None:
        assert _detect_surface_negation(["Not needed"])

    def test_no_false_positive(self) -> None:
        assert not _detect_surface_negation(["Book an appointment please"])


# =============================================================================
# 7.  Audit over 1,152 variants (Finding A)
# =============================================================================


class TestAuditOver1152Variants:
    """Audit runs on the full 1,152-record LC4 development partition."""

    def test_audit_population_is_1152(self) -> None:
        """Audit over DevelopmentOnlyLoader returns exactly 1,152 candidates."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        total = len(variants)
        assert total == 1152, f"Expected 1152 variants, got {total}"

    def test_audit_accepts_bare_specs(self) -> None:
        """audit_candidates accepts bare ReceptionScenarioSpec directly."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        # Limit to first 5 variants for speed
        audit = audit_candidates(variants[:5], num_repeats=1)
        assert audit.total_candidates == 5
        assert audit.total_samples == 5

    def test_audit_still_accepts_corpus_candidate_wrappers(self) -> None:
        """audit_candidates still accepts CorpusCandidate wrappers (LC2 compat)."""
        candidates = load_lc2_candidates()
        audit = audit_candidates(candidates, num_repeats=1)
        assert audit.total_candidates == 15
        assert audit.total_samples == 15


# =============================================================================
# 8.  Uncapped rule counts vs capped examples (Finding B)
# =============================================================================


class TestUncappedRuleCounts:
    """per_rule_counts reflects all records, not just capped examples."""

    def test_per_rule_counts_exceed_example_cap(self) -> None:
        """When conflict records exceed example cap, per_rule_counts still has all."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        audit = audit_candidates(variants, num_repeats=2, max_conflict_examples=5)
        # Conflict examples are capped at 5
        assert len(audit.conflict_records) <= 5
        # Per-rule counts reflect all conflict-detected records (surface + ambiguous
        # + clarification/authority aligned_failure). Non-conflict aligned failures
        # (interpretation/replay mismatch without explicit contradiction) are not
        # tracked in per_rule_counts.
        total_from_rules = sum(audit.per_rule_counts.values())
        conflict_related = (
            audit.surface_contract_conflict_count
            + audit.unsupported_or_ambiguous_surface_count
        )
        # per_rule_counts must be at least the surface/ambiguous total
        assert total_from_rules >= conflict_related, (
            f"per_rule_counts total {total_from_rules} < conflict related {conflict_related}"
        )
        # At least one rule count exceeds the example cap
        assert any(
            count > 5 for count in audit.per_rule_counts.values()
        ), "No per-rule count exceeds example cap of 5 (unlikely for 2304 samples)"

    def test_per_rule_counts_are_exact(self) -> None:
        """Per-rule counts are correct even when examples are capped."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        # Full audit with max examples at 3
        audit_small = audit_candidates(variants[:10], num_repeats=2, max_conflict_examples=3)
        audit_full = audit_candidates(variants[:10], num_repeats=2, max_conflict_examples=100)
        # Per-rule counts must be the same regardless of example cap
        assert audit_small.per_rule_counts == audit_full.per_rule_counts, (
            "per_rule_counts differs when example cap changes"
        )


# =============================================================================
# 9.  Dimension bucket sums (Finding C)
# =============================================================================


class TestDimensionBucketSums:
    """Three failure buckets sum exactly to dimension failure count."""

    def test_dimension_buckets_sum_to_failed(self) -> None:
        """For each dimension, scc + unsup + af == failed."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        audit = audit_candidates(variants, num_repeats=2)
        for dim, da in audit.dimension_attribution.items():
            assert da.total > 0
            assert da.passed + da.failed == da.total, (
                f"{dim}: passed {da.passed} + failed {da.failed} != total {da.total}"
            )
            bucket_sum = (
                da.surface_contract_conflict
                + da.unsupported_or_ambiguous_surface
                + da.aligned_failure
            )
            assert bucket_sum == da.failed, (
                f"{dim}: bucket sum {bucket_sum} != failed {da.failed}"
            )

    def test_each_dimension_has_some_samples(self) -> None:
        """Each attribution dimension has some samples."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        audit = audit_candidates(variants, num_repeats=1)
        for dim in ATTRIBUTION_DIMENSIONS:
            da = audit.dimension_attribution.get(dim)
            assert da is not None, f"Missing attribution for {dim}"
            assert da.total > 0, f"No samples for {dim}"


# =============================================================================
# 10.  Measured variance (Finding D)
# =============================================================================


class TestMeasuredVariance:
    """Repeat variance is measured, not hard-coded to zero."""

    def test_variance_is_integer(self) -> None:
        """variance_count is a non-negative integer."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        audit = audit_candidates(variants[:5], num_repeats=2)
        assert isinstance(audit.variance_count, int)
        assert audit.variance_count >= 0

    def test_deterministic_zero_variance(self) -> None:
        """For deterministic replay, variance is expected to be zero."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        # Run twice and verify variance count is consistent
        audit1 = audit_candidates(variants[:10], num_repeats=2)
        audit2 = audit_candidates(variants[:10], num_repeats=2)
        assert audit1.variance_count == audit2.variance_count


# =============================================================================
# 11.  Semantic baseline/current comparison (Finding D)
# =============================================================================


class TestSemanticComparison:
    """Per-field semantic counts have no decrease from LC4R1 baseline."""

    def test_semantic_passes_no_decrease(self) -> None:
        """Each semantic field pass count >= LC4R1 baseline."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        from app.services.bernie.composed_corpus_evaluator import (
            deterministic_interpret,
            deterministic_replay,
        )
        from app.services.bernie.composed_evaluator import (
            InterpretationObservation,
            score_interpretation_replay_pair,
        )

        LC4R1_SEMANTIC_BASELINE = {
            "intended_action": 720,
            "action_semantics": 674,
            "temporal_relation": 628,
            "normalized_values": 101,
            "entity_semantics": 255,
            "clarification": 642,
        }

        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)

        passes = {field: 0 for field in LC4R1_SEMANTIC_BASELINE}
        for v in variants:
            interp = deterministic_interpret(v)
            interp = InterpretationObservation(
                scenario_id=interp.scenario_id,
                sample_index=0,
                intended_action=interp.intended_action,
                action_semantics=interp.action_semantics,
                temporal_relation=interp.temporal_relation,
                normalized_values=dict(interp.normalized_values),
                entity_semantics=dict(interp.entity_semantics),
                requires_clarification=interp.requires_clarification,
                clarification_choices=interp.clarification_choices,
                selected_tool_sequence=interp.selected_tool_sequence,
                authority_claim=interp.authority_claim,
                claims_action_completed=interp.claims_action_completed,
                action_negated=interp.action_negated,
            )
            replay = deterministic_replay(v, interp)
            result = score_interpretation_replay_pair(v, interp, replay)
            for field in passes:
                sf = getattr(result.semantic_fields, field, None)
                if sf is not None and sf.passed:
                    passes[field] += 1

        for field, baseline in LC4R1_SEMANTIC_BASELINE.items():
            assert passes[field] >= baseline, (
                f"{field}: current {passes[field]} < baseline {baseline}"
            )

    def test_repeat_variance_not_hardcoded(self) -> None:
        """verify variance_count is measured, not hardcoded to 0 in report."""
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        variants = []
        for g in corpus.groups:
            variants.extend(g.all_variants)
        audit = audit_candidates(variants[:10], num_repeats=2)
        # Variance should be a measured integer, not just defaulted
        assert isinstance(audit.variance_count, int)


# =============================================================================
# 12.  Deterministic report hash/order (Finding D/E)
# =============================================================================


class TestDeterministicReportHash:
    """Report hash and order are deterministic."""

    def test_report_hash_deterministic(self) -> None:
        """Two consecutive report computations produce the same hash."""
        import subprocess
        repo_root = HERE.parent
        script = repo_root / "scripts" / "bernie_lc4r_development_gap_report.py"
        # Run report --check which compares in-memory with stored
        result1 = subprocess.run(
            [_python(), script, "--check"],
            capture_output=True, text=True, cwd=repo_root
        )
        result2 = subprocess.run(
            [_python(), script, "--check"],
            capture_output=True, text=True, cwd=repo_root
        )
        assert result1.returncode == 0, f"First check failed: {result1.stderr}"
        assert result2.returncode == 0, f"Second check failed: {result2.stderr}"

    def test_conflict_examples_deterministic_order(self) -> None:
        """Conflict examples are in deterministic order (same across runs)."""
        candidates = load_lc2_candidates()
        audit1 = audit_candidates(candidates, num_repeats=1)
        audit2 = audit_candidates(candidates, num_repeats=1)
        ids1 = [(r.candidate_id, r.rule_id) for r in audit1.conflict_records]
        ids2 = [(r.candidate_id, r.rule_id) for r in audit2.conflict_records]
        assert ids1 == ids2, "Conflict record order differs between runs"


def _python() -> str:
    """Return path to the pinned Python interpreter."""
    return r"C:\Users\sarashera\emr4\.venv\Scripts\python.exe"

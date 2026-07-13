"""LC2 Corpus Factory — unit tests for provenance tiers, promotion, quarantine,
registry, and the CorpusCandidate wrapper.

All tests are pure-Python / domain-layer only.  No provider, route, database,
HTTP, or external-service dependency is required.  Tests prove every
correction specified in the LC2 DW1 hardening packet.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.services.bernie.corpus_tier import (
    AdjudicationRecord,
    AdjudicationState,
    AuthorityGrant,
    CandidateRegistry,
    CorpusCandidate,
    GeneratorIdentity,
    JudgeIdentity,
    PromotionEvent,
    PromotionOutcome,
    ProvenanceTier,
    QuarantineReason,
    ScenarioFamily,
    promote_candidate,
    _compute_derivation_id,
    _validate_derivation_id,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

FIXTURE_DIR = Path("tests/fixtures/bernie_corpus_tier")


# ═══════════════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════════════


def load_candidate(name: str) -> CorpusCandidate:
    path = FIXTURE_DIR / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return CorpusCandidate.model_validate(data)


def load_candidate_raw(name: str) -> dict:
    path = FIXTURE_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def _adapt_scenario(
    spec: ReceptionScenarioSpec,
    *,
    provenance: str | None = None,
    adjudication: str | None = None,
    family: str | None = None,
    scenario_id: str | None = None,
) -> ReceptionScenarioSpec:
    """Create a copy of a scenario spec with overridden metadata fields.

    Used to build a scenario whose metadata matches a wrapper tier.
    """
    data = spec.model_dump()
    if provenance is not None:
        data["provenance"] = provenance
    if adjudication is not None:
        data["adjudication"] = adjudication
    if family is not None:
        data["family"] = family
    if scenario_id is not None:
        data["scenario_id"] = scenario_id
    return ReceptionScenarioSpec.model_validate(data)


def make_adjudication(
    *,
    decision: str = "accepted",
    model_id: str = "judge-model",
    instance_id: str = "judge-lane",
    timestamp: datetime | None = None,
    semantic_scope: str = "action,entity,temporal",
    evidence_scope: str = "source_spans,dialogue_turns",
    evidence_ref: str = "ev-001",
) -> AdjudicationRecord:
    """Convenience to build a deterministic adjudication record."""
    if timestamp is None:
        timestamp = datetime(2026, 7, 14, 12, 0, 0, tzinfo=timezone.utc)
    return AdjudicationRecord(
        decision=decision,  # type: ignore[arg-type]
        judge=JudgeIdentity(model_id=model_id, instance_id=instance_id),
        timestamp=timestamp,
        checked_semantic_scope=semantic_scope,
        checked_evidence_scope=evidence_scope,
        evidence_ref=evidence_ref,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  Module import and enumeration tests
# ═══════════════════════════════════════════════════════════════════════════


def test_module_imports_cleanly():
    """Corpus tier module imports cleanly."""
    from app.services.bernie.corpus_tier import (
        AdjudicationState,
        CorpusCandidate,
        ProvenanceTier,
        ScenarioFamily,
        promote_candidate,
    )

    assert ProvenanceTier.GOLD.value == "gold"
    assert AdjudicationState.ADJUDICATED.value == "adjudicated"


def test_scenario_family_expanded():
    """ScenarioFamily covers the canonical LC1 action/family surface."""
    families = list(ScenarioFamily)
    expected = [
        ScenarioFamily.BOOKING_CREATE,
        ScenarioFamily.BOOKING_MOVE,
        ScenarioFamily.BOOKING_RESIZE,
        ScenarioFamily.BOOKING_CANCEL,
        ScenarioFamily.STATUS_CHANGE,
        ScenarioFamily.EXPLAIN_SCHEDULE,
        ScenarioFamily.CLARIFY_TEMPORAL,
        ScenarioFamily.ADVERSARIAL,
    ]
    assert families == expected


def test_quarantine_reason_no_duplicates():
    """generator_equals_judge removed (duplicate of self_certification)."""
    reasons = {r.value for r in QuarantineReason}
    assert "generator_equals_judge" not in reasons
    assert "self_certification" in reasons
    assert "adjudication_rejected" in reasons
    assert "adjudication_disputed" in reasons
    assert "derivation_mismatch" in reasons
    assert "generator_authority_grant" in reasons


# ═══════════════════════════════════════════════════════════════════════════
#  Identity tests — req #1 (model-level independence)
# ═══════════════════════════════════════════════════════════════════════════


class TestIdentity:
    """Req #1: identity independence is model-level, not instance-level."""

    def test_generator_identity_immutable(self):
        gen = GeneratorIdentity(model_id="test-model", instance_id="lane-1")
        with pytest.raises(Exception):
            gen.model_id = "other"  # type: ignore[misc]

    def test_judge_identity_immutable(self):
        judge = JudgeIdentity(model_id="judge-model")
        with pytest.raises(Exception):
            judge.model_id = "other"  # type: ignore[misc]

    def test_model_key_ignores_instance(self):
        """model_key() returns only model_id; same model, different instances match."""
        gen1 = GeneratorIdentity(model_id="deepseek", instance_id="dw2")
        gen2 = GeneratorIdentity(model_id="deepseek", instance_id="dw3")
        assert gen1.model_key() == gen2.model_key()

    def test_stable_key_includes_instance_for_traceability(self):
        """stable_key() preserves instance identity for traceability."""
        gen1 = GeneratorIdentity(model_id="deepseek", instance_id="dw2")
        gen2 = GeneratorIdentity(model_id="deepseek", instance_id="dw3")
        assert gen1.stable_key() != gen2.stable_key()

    def test_same_model_different_instance_rejected(self):
        """Req #1: second instance of same provider model CANNOT certify."""
        gen = GeneratorIdentity(model_id="deepseek-flash", instance_id="dw2")
        judge = JudgeIdentity(model_id="deepseek-flash", instance_id="dw3")
        candidate = load_candidate("valid_silver_candidate.json")
        # Replace generator
        d = json.loads(candidate.model_dump_json())
        d["generator_identity"] = {"model_id": "deepseek-flash", "instance_id": "dw2"}
        d["source_scenario_id"] = "booking_create_then_exact_duplicate"
        modified = CorpusCandidate.model_validate(d)
        ad = make_adjudication(model_id="deepseek-flash", instance_id="dw3")
        result = promote_candidate(modified, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.SELF_CERTIFICATION

    def test_different_model_accepted(self):
        """Different model_id passes the self-certification gate."""
        gen = GeneratorIdentity(model_id="model-a", instance_id="lane-1")
        judge = JudgeIdentity(model_id="model-b", instance_id="lane-1")
        assert gen.model_key() != judge.model_key()
        candidate = load_candidate("valid_silver_candidate.json")
        d = json.loads(candidate.model_dump_json())
        d["generator_identity"] = {"model_id": "model-a", "instance_id": "lane-1"}
        d["source_scenario_id"] = "booking_create_then_exact_duplicate"
        modified = CorpusCandidate.model_validate(d)
        ad = make_adjudication(model_id="model-b", instance_id="lane-1")
        result = promote_candidate(modified, adjudication=ad)
        assert not isinstance(result, PromotionOutcome.Quarantined) or (
            result.quarantine.reason != QuarantineReason.SELF_CERTIFICATION
        )

    def test_rejects_extra_keys(self):
        with pytest.raises(ValueError):
            GeneratorIdentity(model_id="m", unknown_extra="x")  # type: ignore[call-arg]


# ═══════════════════════════════════════════════════════════════════════════
#  CorpusCandidate wrapper tests — req #4, #5, #7
# ═══════════════════════════════════════════════════════════════════════════


class TestCorpusCandidateWrapper:
    """Req #4 (metadata fail-closed), #5 (source_scenario_id rules), #7 (authority grant)."""

    def test_gold_seed_loads(self):
        candidate = load_candidate("valid_gold_seed.json")
        assert candidate.provenance == ProvenanceTier.GOLD
        assert candidate.adjudication == AdjudicationState.ADJUDICATED
        assert candidate.generator_identity is None
        assert candidate.generation_timestamp is None
        assert candidate.source_scenario_id is None

    def test_silver_candidate_loads(self):
        candidate = load_candidate("valid_silver_candidate.json")
        assert candidate.provenance == ProvenanceTier.SILVER
        assert candidate.adjudication == AdjudicationState.PENDING
        assert candidate.generator_identity is not None
        assert candidate.generation_timestamp is not None
        assert candidate.source_scenario_id == "booking_create_then_exact_duplicate"
        assert candidate.derivation_id is not None
        assert candidate.derivation_id.startswith("sha256:")
        assert len(candidate.derivation_id) == 71

    def test_wraps_reception_scenario_spec_without_mutation(self):
        candidate = load_candidate("valid_silver_candidate.json")
        assert isinstance(candidate.scenario, ReceptionScenarioSpec)
        assert candidate.scenario.spec_version == "lc1.v1"
        assert candidate.scenario.intended_action == "create"

    def test_stable_key_is_deterministic(self):
        c1 = load_candidate("valid_silver_candidate.json")
        c2 = load_candidate("valid_silver_candidate.json")
        assert c1.stable_key() == c2.stable_key()

    def test_bronze_candidate_construction(self):
        """Bronze candidate can be constructed with matched scenario metadata."""
        gen = GeneratorIdentity(model_id="bronze-gen", instance_id="test")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        scenario = _adapt_scenario(
            gold_spec, provenance="bronze", adjudication="pending"
        )
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=gold_spec.scenario_id,
            scenario=scenario,
        )
        assert bronze.provenance == ProvenanceTier.BRONZE
        assert isinstance(bronze.scenario, ReceptionScenarioSpec)
        assert bronze.scenario.provenance == "bronze"

    def test_rejects_extra_keys(self):
        data = load_candidate_raw("valid_silver_candidate.json")
        data["unknown_key"] = "should_fail"
        with pytest.raises(ValueError):
            CorpusCandidate.model_validate(data)

    # ── Req #5: source-scenario-id rules ──────────────────────────────────

    def test_gold_must_not_have_generator(self):
        data = load_candidate_raw("valid_gold_seed.json")
        data["generator_identity"] = {"model_id": "test"}
        with pytest.raises(ValueError, match="generator_identity"):
            CorpusCandidate.model_validate(data)

    def test_gold_must_not_have_source_scenario_id(self):
        data = load_candidate_raw("valid_gold_seed.json")
        data["source_scenario_id"] = "some_source"
        with pytest.raises(ValueError, match="source_scenario_id"):
            CorpusCandidate.model_validate(data)

    def test_silver_must_have_generator_identity(self):
        data = load_candidate_raw("valid_silver_candidate.json")
        data["generator_identity"] = None
        with pytest.raises(ValueError, match="generator_identity"):
            CorpusCandidate.model_validate(data)

    def test_silver_must_have_source_scenario_id(self):
        data = load_candidate_raw("valid_silver_candidate.json")
        data["source_scenario_id"] = None
        with pytest.raises(ValueError, match="source_scenario_id"):
            CorpusCandidate.model_validate(data)

    def test_bronze_allowed_without_source_scenario_id(self):
        """Req #5: Bronze external/discovery candidates may lack a Gold source."""
        gen = GeneratorIdentity(model_id="bronze-gen", instance_id="test")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        scenario = _adapt_scenario(
            gold_spec, provenance="bronze", adjudication="pending"
        )
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=None,
            scenario=scenario,
        )
        assert bronze.source_scenario_id is None
        assert bronze.provenance == ProvenanceTier.BRONZE

    def test_bronze_can_have_source_scenario_id(self):
        """Bronze derived from a Gold source may carry the source ID."""
        gen = GeneratorIdentity(model_id="bronze-gen", instance_id="test")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        scenario = _adapt_scenario(
            gold_spec, provenance="bronze", adjudication="pending"
        )
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=gold_spec.scenario_id,
            scenario=scenario,
        )
        assert bronze.source_scenario_id is not None

    # ── Req #4: metadata agreement fail-closed ────────────────────────────

    def test_metadata_mismatch_provenance_rejected(self):
        """Wrapper provenance must match embedded scenario provenance."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario = load_candidate("valid_gold_seed.json").scenario
        # Wrap gold scenario with silver wrapper
        with pytest.raises(ValueError, match="provenance"):
            CorpusCandidate(
                provenance=ProvenanceTier.SILVER,
                adjudication=AdjudicationState.PENDING,
                family=ScenarioFamily.BOOKING_CREATE,
                generator_identity=gen,
                generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
                source_scenario_id=scenario.scenario_id,
                scenario=scenario,
            )

    def test_metadata_mismatch_adjudication_rejected(self):
        """Wrapper adjudication must match embedded scenario adjudication."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario = load_candidate("valid_silver_candidate.json").scenario
        # The silver scenario's adjudication is "pending"
        with pytest.raises(ValueError, match="adjudication"):
            CorpusCandidate(
                provenance=ProvenanceTier.SILVER,
                adjudication=AdjudicationState.ADJUDICATED,  # mismatch
                family=ScenarioFamily.BOOKING_CREATE,
                generator_identity=gen,
                generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
                source_scenario_id="test",
                scenario=scenario,
            )

    def test_metadata_mismatch_family_rejected(self):
        """Wrapper family must match embedded scenario family."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario = load_candidate("valid_gold_seed.json").scenario
        # scenario.family is "booking_create"
        with pytest.raises(ValueError, match="family"):
            CorpusCandidate(
                provenance=ProvenanceTier.GOLD,
                adjudication=AdjudicationState.ADJUDICATED,
                family=ScenarioFamily.CLARIFY_TEMPORAL,  # mismatch
                scenario=scenario,
            )

    def test_silver_wrapper_around_gold_scenario_rejected(self):
        """Req #4: Silver/pending wrapper around Gold/adjudicated scenario is rejected."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario = load_candidate("valid_gold_seed.json").scenario
        with pytest.raises(ValueError, match="provenance"):
            CorpusCandidate(
                provenance=ProvenanceTier.SILVER,
                adjudication=AdjudicationState.PENDING,
                family=ScenarioFamily.BOOKING_CREATE,
                generator_identity=gen,
                generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
                source_scenario_id=scenario.scenario_id,
                scenario=scenario,
            )

    # ── Req #7: authority grant validation ────────────────────────────────

    def test_generated_candidate_rejects_non_empty_authority_grant(self):
        """Generated candidates must have empty authority grant."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario = load_candidate("valid_silver_candidate.json").scenario
        with pytest.raises(ValueError, match="authority"):
            CorpusCandidate(
                provenance=ProvenanceTier.SILVER,
                adjudication=AdjudicationState.PENDING,
                family=ScenarioFamily.BOOKING_CREATE,
                generator_identity=gen,
                generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
                source_scenario_id="test",
                authority_grant=AuthorityGrant(diary_write=True),
                scenario=scenario,
            )

    def test_gold_candidate_may_carry_authority_grant(self):
        """Gold (Sol-authored) may carry a non-empty authority grant."""
        scenario = load_candidate("valid_gold_seed.json").scenario
        # Gold candidates are not checked for authority grant in validator
        candidate = CorpusCandidate(
            provenance=ProvenanceTier.GOLD,
            adjudication=AdjudicationState.ADJUDICATED,
            family=ScenarioFamily.BOOKING_CREATE,
            authority_grant=AuthorityGrant(provider_write=True),
            scenario=scenario,
        )
        assert candidate.authority_grant.provider_write is True


# ═══════════════════════════════════════════════════════════════════════════
#  Promotion tests — req #2, #3, #6
# ═══════════════════════════════════════════════════════════════════════════


class TestPromotion:
    """Req #2 (adjudication record), #3 (return candidate), #6 (derivation)."""

    # ── Bronze -> Silver ──────────────────────────────────────────────────

    def test_bronze_to_silver_with_accepted_adjudication(self):
        """Req #2: Bronze -> Silver requires accepted independent record."""
        gen = GeneratorIdentity(model_id="generator", instance_id="test")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        scenario = _adapt_scenario(
            gold_spec, provenance="bronze", adjudication="pending"
        )
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=gold_spec.scenario_id,
            scenario=scenario,
        )
        ad = make_adjudication(model_id="judge-model", instance_id="judge-lane")
        result = promote_candidate(bronze, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Promoted)

    # ── Silver -> Gold ────────────────────────────────────────────────────

    def test_silver_to_gold_with_independent_judge(self):
        """Req #2: Silver -> Gold with independent accepted adjudication."""
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(model_id="independent-judge", instance_id="lane-1")
        assert candidate.generator_identity.model_key() != ad.judge.model_key()
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Promoted)

    def test_silver_to_gold_requires_adjudication_record(self):
        """Req #2: Silver promotion fails without adjudication record."""
        candidate = load_candidate("valid_silver_candidate.json")
        result = promote_candidate(candidate, adjudication=None)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.MISSING_PROVENANCE

    # ── Gold cannot be promoted ───────────────────────────────────────────

    def test_gold_cannot_be_promoted(self):
        candidate = load_candidate("valid_gold_seed.json")
        ad = make_adjudication(model_id="judge-model")
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Rejected)
        assert "cannot be promoted" in result.reason

    # ── Promotion with explicit target ────────────────────────────────────

    def test_promote_with_explicit_target(self):
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(model_id="independent-judge")
        result = promote_candidate(candidate, adjudication=ad, target_tier=ProvenanceTier.GOLD)
        assert isinstance(result, PromotionOutcome.Promoted)

    def test_invalid_explicit_target_is_quarantined(self):
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(model_id="independent-judge")
        result = promote_candidate(
            candidate, adjudication=ad, target_tier=ProvenanceTier.BRONZE
        )
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.INVALID_TIER_TRANSITION

    # ── Req #3: promotion returns candidate ───────────────────────────────

    def test_promotion_returns_changed_candidate(self):
        """Req #3: Successful promotion returns the resulting immutable candidate."""
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(model_id="independent-judge", instance_id="lane-1")
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Promoted)
        promoted = result.candidate
        assert isinstance(promoted, CorpusCandidate)
        assert promoted.provenance == ProvenanceTier.GOLD
        assert promoted.adjudication == AdjudicationState.ADJUDICATED
        # Candidate is different object from original
        assert promoted is not candidate
        # Judge identity from adjudication is attached
        assert promoted.judge_identity is not None
        assert promoted.judge_identity.model_id == "independent-judge"
        # Adjudication record is attached
        assert promoted.adjudication_record is not None
        assert promoted.adjudication_record.decision == "accepted"
        # Promotion history is appended
        assert len(promoted.promotion_history) == len(candidate.promotion_history) + 1
        assert promoted.promotion_history[-1].from_tier == ProvenanceTier.SILVER
        assert promoted.promotion_history[-1].to_tier == ProvenanceTier.GOLD

    def test_promotion_timestamp_comes_from_adjudication(self):
        """Req #3: Promotion-event time must come from adjudication record, not datetime.now()."""
        fixed_ts = datetime(2025, 1, 15, 8, 30, 0, tzinfo=timezone.utc)
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(
            model_id="independent-judge",
            timestamp=fixed_ts,
        )
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Promoted)
        promoted = result.candidate
        event = promoted.promotion_history[-1]
        assert event.timestamp == fixed_ts
        assert event.timestamp != datetime.now(timezone.utc)  # not from now()

    # ── Req #2: rejected/disputed adjudication quarantines ────────────────

    def test_adjudication_rejected_quarantines(self):
        """Req #2: Rejected adjudication records cause quarantine."""
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(decision="rejected", model_id="independent-judge")
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.ADJUDICATION_REJECTED

    def test_adjudication_disputed_quarantines(self):
        """Req #2: Disputed adjudication records cause quarantine."""
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(decision="disputed", model_id="independent-judge")
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.ADJUDICATION_DISPUTED

    def test_bare_judge_identity_never_promotes(self):
        """Req #2: Bare JudgeIdentity (without adjudication record) never promotes."""
        candidate = load_candidate("valid_silver_candidate.json")
        result = promote_candidate(candidate, adjudication=None)
        assert isinstance(result, PromotionOutcome.Quarantined)

    # ── Promotion event record ────────────────────────────────────────────

    def test_promotion_event_recorded(self):
        candidate = load_candidate("valid_silver_candidate.json")
        ad = make_adjudication(model_id="independent-judge")
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Promoted)
        promoted = result.candidate
        event = promoted.promotion_history[-1]
        assert event.from_tier == ProvenanceTier.SILVER
        assert event.to_tier == ProvenanceTier.GOLD
        assert event.judge is not None
        assert event.judge.model_id == "independent-judge"


# ═══════════════════════════════════════════════════════════════════════════
#  Self-certification guard tests — req #1
# ═══════════════════════════════════════════════════════════════════════════


class TestSelfCertification:
    """Req #1: model-level independence check."""

    def test_self_certification_is_quarantined(self):
        """Same model_id (same or different instance) is caught."""
        candidate = load_candidate("self_certified_reject.json")
        ad = make_adjudication(model_id="same-model", instance_id="different-instance")
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.SELF_CERTIFICATION

    def test_same_model_different_instance(self):
        """Req #1: same model_id, different instance_id is still self-certification."""
        gen = GeneratorIdentity(model_id="model-a", instance_id="lane-1")
        judge = JudgeIdentity(model_id="model-a", instance_id="lane-2")
        assert gen.model_key() == judge.model_key()
        candidate = load_candidate("valid_silver_candidate.json")
        d = json.loads(candidate.model_dump_json())
        d["generator_identity"] = {"model_id": "model-a", "instance_id": "lane-1"}
        modified = CorpusCandidate.model_validate(d)
        ad = make_adjudication(model_id="model-a", instance_id="lane-2")
        result = promote_candidate(modified, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.SELF_CERTIFICATION

    def test_different_models_pass_self_cert_check(self):
        """Different model_ids are accepted even with same instance_id."""
        candidate = load_candidate("valid_silver_candidate.json")
        d = json.loads(candidate.model_dump_json())
        d["generator_identity"] = {"model_id": "model-a", "instance_id": "lane-1"}
        modified = CorpusCandidate.model_validate(d)
        ad = make_adjudication(model_id="model-b", instance_id="lane-1")
        result = promote_candidate(modified, adjudication=ad)
        assert not isinstance(result, PromotionOutcome.Quarantined) or (
            result.quarantine.reason != QuarantineReason.SELF_CERTIFICATION
        )


# ═══════════════════════════════════════════════════════════════════════════
#  Quarantine trigger tests — req #2, #7
# ═══════════════════════════════════════════════════════════════════════════


class TestQuarantine:
    """Quarantine triggers for schema, authority, evidence, provenance, transitions."""

    def _make_adjudication(self, model_id: str = "judge-model") -> AdjudicationRecord:
        return make_adjudication(model_id=model_id)

    def test_quarantine_schema_invalid(self):
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        scenario["dialogue_turns"] = []
        invalid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id="test-source",
            scenario=invalid_scenario,
        )
        result = promote_candidate(candidate, adjudication=self._make_adjudication())
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.SCHEMA_INVALID

    def test_quarantine_authority_breach(self):
        """Req #7: Explicit authority grant breach is quarantined."""
        # Must construct via model_construct to bypass the construction-time
        # authority-grant validator (which would reject this candidate).
        raw = load_candidate_raw("quarantine_authority_breach.json")
        # Recursively construct nested models to avoid dict/object mismatch
        raw["authority_grant"] = AuthorityGrant.model_construct(**raw["authority_grant"])
        if raw.get("generator_identity"):
            raw["generator_identity"] = GeneratorIdentity.model_construct(
                **raw["generator_identity"]
            )
        raw["scenario"] = ReceptionScenarioSpec.model_construct(**raw["scenario"])
        candidate = CorpusCandidate.model_construct(**raw)
        # authority_grant should have diary_write=True
        assert candidate.authority_grant.diary_write is True
        result = promote_candidate(candidate, adjudication=self._make_adjudication())
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.GENERATOR_AUTHORITY_GRANT

    def test_authority_breach_description_not_scanned(self):
        """Req #7: Description/outcome prose mentioning authority is NOT a breach.

        The breach is detected via the explicit authority_grant field, not
        substring scanning of scenario prose.
        """
        # Construct a candidate where description mentions "write_authority"
        # but authority_grant is empty — should NOT be quarantined for authority breach.
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        scenario["description"] = "This mentions write_authority as evidence context."
        scenario["expected_outcome_kind"] = "confirmation_required"
        safe_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id="test-source",
            scenario=safe_scenario,
        )
        # Should fail on adjudication requirement, NOT on authority breach
        result = promote_candidate(candidate, adjudication=None)
        # The result may be quarantined for missing adjudication, NOT authority breach
        if isinstance(result, PromotionOutcome.Quarantined):
            assert result.quarantine.reason != QuarantineReason.GENERATOR_AUTHORITY_GRANT

    def test_forbidden_tool_calls_not_treated_as_authority(self):
        """Req #7: forbidden_tool_calls is NOT treated as granted authority."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        scenario["forbidden_tool_calls"] = ["mutate_diary_direct", "override_confirmation"]
        safe_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id="test-source",
            scenario=safe_scenario,
        )
        # Should fail on adjudication requirement, NOT on authority breach
        result = promote_candidate(candidate, adjudication=None)
        if isinstance(result, PromotionOutcome.Quarantined):
            assert result.quarantine.reason != QuarantineReason.GENERATOR_AUTHORITY_GRANT

    def test_quarantine_evidence_mismatch(self):
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        scenario["source_spans"]["earliest_time"] = [
            {"turn_index": 0, "start": 0, "end": 4, "text": "NOPE"}
        ]
        valid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id="test-source",
            scenario=valid_scenario,
        )
        result = promote_candidate(candidate, adjudication=self._make_adjudication())
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason in (
            QuarantineReason.SCHEMA_INVALID,
            QuarantineReason.EVIDENCE_MISMATCH,
        )

    def test_quarantine_missing_provenance_silver(self):
        """Silver without source_scenario_id is quarantined."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario = load_candidate("valid_gold_seed.json").scenario
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=None,
            scenario=scenario,
        )
        result = promote_candidate(candidate, adjudication=self._make_adjudication())
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.MISSING_PROVENANCE

    def test_bronze_missing_generator_quarantined(self):
        """Bronze without generator_identity is quarantined."""
        scenario = load_candidate("valid_gold_seed.json").scenario
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=None,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=None,
            scenario=scenario,
        )
        result = promote_candidate(candidate, adjudication=self._make_adjudication())
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.MISSING_PROVENANCE

    def test_quarantine_invalid_tier_transition(self):
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        scenario = _adapt_scenario(gold_spec, provenance="bronze", adjudication="pending")
        candidate = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=gold_spec.scenario_id,
            scenario=scenario,
        )
        ad = self._make_adjudication()
        result = promote_candidate(candidate, adjudication=ad, target_tier=ProvenanceTier.GOLD)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.INVALID_TIER_TRANSITION


# ═══════════════════════════════════════════════════════════════════════════
#  Derivation ID / stable hash tests — req #6
# ═══════════════════════════════════════════════════════════════════════════


class TestDerivationId:
    """Req #6: full sha256:<64hex> derivation, no timestamp/instance dependency."""

    def test_derivation_id_is_deterministic(self):
        c1 = load_candidate("valid_silver_candidate.json")
        c2 = load_candidate("valid_silver_candidate.json")
        assert c1.derivation_id == c2.derivation_id

    def test_derivation_id_full_hash_format(self):
        """Derivation ID is sha256:<64 lowercase hex>."""
        candidate = load_candidate("valid_silver_candidate.json")
        assert candidate.derivation_id.startswith("sha256:")
        hex_part = candidate.derivation_id[7:]
        assert len(hex_part) == 64
        assert all(c in "0123456789abcdef" for c in hex_part)
        assert len(candidate.derivation_id) == 71

    def test_derivation_id_independent_of_timestamp(self):
        """Req #6: Timestamp must not change the derivation."""
        id1 = _compute_derivation_id("src-1", "model-a", seed="seed-x")
        id2 = _compute_derivation_id("src-1", "model-a", seed="seed-x")
        assert id1 == id2

    def test_derivation_id_independent_of_instance(self):
        """Req #6: Lane instance must not change the derivation."""
        id1 = _compute_derivation_id("src-1", "model-a", seed="seed-x")
        id2 = _compute_derivation_id("src-1", "model-a", seed="seed-x")
        assert id1 == id2

    def test_derivation_id_changes_with_seed(self):
        id1 = _compute_derivation_id("src-1", "model-a", seed="seed-a")
        id2 = _compute_derivation_id("src-1", "model-a", seed="seed-b")
        assert id1 != id2

    def test_derivation_id_changes_with_model(self):
        id1 = _compute_derivation_id("src-1", "model-a", seed="seed-x")
        id2 = _compute_derivation_id("src-1", "model-b", seed="seed-x")
        assert id1 != id2

    def test_derivation_id_changes_with_source(self):
        id1 = _compute_derivation_id("src-1", "model-a", seed="seed-x")
        id2 = _compute_derivation_id("src-2", "model-a", seed="seed-x")
        assert id1 != id2

    def test_rejects_mismatched_derivation_id(self):
        """Req #6: Recompute and reject a supplied mismatched derivation ID."""
        with pytest.raises(ValueError, match="does not match"):
            _validate_derivation_id(
                "src-1", "model-a", "seed-x",
                supplied="sha256:" + "a" * 64,
            )

    def test_rejects_invalid_format(self):
        """Derivation ID must be sha256:<64hex>."""
        with pytest.raises(ValueError, match="derivation_id must be"):
            _validate_derivation_id(
                "src-1", "model-a", "seed-x",
                supplied="invalid-hash",
            )

    def test_short_hash_rejected_at_construction(self):
        """Old 32-char hex derivation IDs are rejected at construction."""
        data = load_candidate_raw("valid_silver_candidate.json")
        data["derivation_id"] = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
        with pytest.raises(ValueError, match="derivation_id must be"):
            CorpusCandidate.model_validate(data)

    def test_promotion_rejects_mismatched_derivation_id(self):
        """Promotion quarantines on derivation ID mismatch."""
        gen = GeneratorIdentity(model_id="model-a", instance_id="x")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        scenario = _adapt_scenario(gold_spec, provenance="silver", adjudication="pending")
        candidate = CorpusCandidate(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id="src-1",
            derivation_id="sha256:" + "a" * 64,  # wrong hash
            derivation_seed="seed-x",
            scenario=scenario,
        )
        ad = make_adjudication(model_id="independent-judge")
        result = promote_candidate(candidate, adjudication=ad)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.DERIVATION_MISMATCH


# ═══════════════════════════════════════════════════════════════════════════
#  Candidate registry tests — req #10
# ═══════════════════════════════════════════════════════════════════════════


class TestCandidateRegistry:
    """Req #10: Registry schema validation with 4th entry."""

    REGISTRY_PATH = FIXTURE_DIR / "registry_evaluation_candidates.json"

    def test_registry_loads(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        assert len(registry.entries) >= 4

    def test_four_required_candidates_present(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        names = {e.name for e in registry.entries}
        assert "Schema-Guided Dialogue / SGD-X" in names
        assert "SMCalFlow" in names
        assert "MultiWOZ research data" in names
        assert "Healthcare Appointment Booking Calls Dataset" in names

    def test_healthcare_entry_metadata(self):
        """Req #10: 4th entry is healthcare dataset with correct metadata."""
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        healthcare = [
            e for e in registry.entries if "Healthcare Appointment" in e.name
        ][0]
        assert healthcare.decision == "requires_licence_review"
        assert healthcare.official_url.startswith(
            "https://www.kaggle.com/datasets/ammarshafiq/"
        )
        labels = {l.label for l in healthcare.capability_labels}
        assert "healthcare_appointment_booking" in labels
        assert "privacy_sensitive" in labels

    def test_all_entries_have_official_urls(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        for entry in registry.entries:
            assert entry.official_url.startswith("http"), f"{entry.name} missing URL"

    def test_all_entries_have_declared_licence(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        for entry in registry.entries:
            assert len(entry.declared_licence) > 0, f"{entry.name} missing licence"

    def test_all_entries_have_conservative_decision(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        for entry in registry.entries:
            assert entry.decision in (
                "candidate_only",
                "requires_licence_review",
            ), f"{entry.name} has non-conservative decision"

    def test_no_entry_claims_eligibility(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        for entry in registry.entries:
            assert entry.decision != "eligible", f"{entry.name} claims eligibility"

    def test_all_entries_have_licence_notes(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        for entry in registry.entries:
            assert entry.licence_notes is not None, f"{entry.name} missing licence_notes"
            assert "No licence is accepted" in entry.licence_notes

    def test_rejects_content_payload(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        data["entries"][0]["dialogue_payload"] = {"utterance": "test"}
        with pytest.raises(ValueError):
            CandidateRegistry.model_validate(data)


# ═══════════════════════════════════════════════════════════════════════════
#  Strict extra-key rejection tests
# ═══════════════════════════════════════════════════════════════════════════


class TestExtraKeyRejection:
    def test_candidate_rejects_extra_field(self):
        data = load_candidate_raw("valid_silver_candidate.json")
        data["illegal_field"] = "should_fail"
        with pytest.raises(ValueError):
            CorpusCandidate.model_validate(data)

    def test_registry_entry_rejects_extra_field(self):
        from app.services.bernie.corpus_tier import RegistryEntry

        with pytest.raises(ValueError):
            RegistryEntry(
                name="test",
                official_url="https://example.com",
                declared_licence="MIT",
                decision="candidate_only",
                dataset_content="should_fail",  # type: ignore[call-arg]
            )

    def test_adjudication_record_rejects_extra_field(self):
        with pytest.raises(ValueError):
            AdjudicationRecord(
                decision="accepted",
                judge=JudgeIdentity(model_id="j"),
                timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
                checked_semantic_scope="action",
                checked_evidence_scope="spans",
                evidence_ref="ev-001",
                unknown_field="x",  # type: ignore[call-arg]
            )


# ═══════════════════════════════════════════════════════════════════════════
#  Source-coordinate validation tests
# ═══════════════════════════════════════════════════════════════════════════


class TestSourceCoordinateValidation:
    def test_valid_source_spans_pass(self):
        candidate = load_candidate("valid_gold_seed.json")
        assert len(candidate.scenario.source_spans) > 0

    def test_evidence_mismatch_detected(self):
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        scenario["source_spans"]["patient"] = [
            {"turn_index": 0, "start": 0, "end": 5, "text": "WRONG"}
        ]
        invalid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id="test-source",
            scenario=invalid_scenario,
        )
        result = promote_candidate(candidate, adjudication=make_adjudication())
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason in (
            QuarantineReason.SCHEMA_INVALID,
            QuarantineReason.EVIDENCE_MISMATCH,
        )

    def test_evidence_mismatch_missing_turn(self):
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        scenario["source_spans"]["patient"] = [
            {"turn_index": 99, "start": 0, "end": 1, "text": "X"}
        ]
        invalid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id="test-source",
            scenario=invalid_scenario,
        )
        result = promote_candidate(candidate, adjudication=make_adjudication())
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason in (
            QuarantineReason.SCHEMA_INVALID,
            QuarantineReason.EVIDENCE_MISMATCH,
        )


# ═══════════════════════════════════════════════════════════════════════════
#  Registry content rejection tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistryContentRejection:
    def test_registry_rejects_embedded_dialogue(self):
        from app.services.bernie.corpus_tier import RegistryEntry

        with pytest.raises(ValueError):
            RegistryEntry(
                name="bad",
                official_url="https://example.com",
                declared_licence="MIT",
                decision="candidate_only",
                dialogues=["hello"],  # type: ignore[call-arg]
            )

    def test_registry_rejects_dataset_content(self):
        from app.services.bernie.corpus_tier import RegistryEntry

        with pytest.raises(ValueError):
            RegistryEntry(
                name="bad",
                official_url="https://example.com",
                declared_licence="MIT",
                decision="candidate_only",
                content_bytes="base64data",  # type: ignore[call-arg]
            )

    def test_registry_decision_must_be_conservative(self):
        from app.services.bernie.corpus_tier import RegistryEntry

        with pytest.raises(ValueError):
            RegistryEntry(
                name="bad",
                official_url="https://example.com",
                declared_licence="MIT",
                decision="eligible",  # type: ignore[arg-type]
            )


# ═══════════════════════════════════════════════════════════════════════════
#  Registry fixture content verification
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistryFixture:
    """All four registry entries are verified."""

    def test_sgd_x_entry(self):
        data = json.loads(
            (FIXTURE_DIR / "registry_evaluation_candidates.json").read_text(
                encoding="utf-8"
            )
        )
        registry = CandidateRegistry.model_validate(data)
        sgd = [e for e in registry.entries if "Schema-Guided" in e.name][0]
        assert sgd.official_url == (
            "https://github.com/google-research-datasets/"
            "dstc8-schema-guided-dialogue"
        )
        assert "CC BY-SA 4.0" in sgd.declared_licence
        labels = {l.label for l in sgd.capability_labels}
        assert "multi-domain_turns" in labels
        assert "intent_slot_annotations" in labels
        assert sgd.decision == "candidate_only"

    def test_smcalflow_entry(self):
        data = json.loads(
            (FIXTURE_DIR / "registry_evaluation_candidates.json").read_text(
                encoding="utf-8"
            )
        )
        registry = CandidateRegistry.model_validate(data)
        smc = [e for e in registry.entries if "SMCalFlow" in e.name][0]
        assert smc.official_url == (
            "https://microsoft.github.io/"
            "task_oriented_dialogue_as_dataflow_synthesis/"
        )
        assert "CC BY-SA 4.0" in smc.declared_licence
        labels = {l.label for l in smc.capability_labels}
        assert "multi_turn_calendar" in labels
        assert "executable_task_structure" in labels
        assert smc.decision == "candidate_only"

    def test_multiwoz_entry(self):
        data = json.loads(
            (FIXTURE_DIR / "registry_evaluation_candidates.json").read_text(
                encoding="utf-8"
            )
        )
        registry = CandidateRegistry.model_validate(data)
        mw = [e for e in registry.entries if "MultiWOZ" in e.name][0]
        assert mw.official_url == (
            "https://www.repository.cam.ac.uk/"
            "items/322039b6-ab19-4798-9a80-faee9e62daab"
        )
        assert "CC BY 4.0" in mw.declared_licence
        labels = {l.label for l in mw.capability_labels}
        assert "human_human_multi_domain" in labels
        assert "booking_related_domains" in labels
        assert mw.decision == "candidate_only"

    def test_healthcare_entry(self):
        data = json.loads(
            (FIXTURE_DIR / "registry_evaluation_candidates.json").read_text(
                encoding="utf-8"
            )
        )
        registry = CandidateRegistry.model_validate(data)
        hc = [e for e in registry.entries if "Healthcare Appointment" in e.name][0]
        assert hc.official_url == (
            "https://www.kaggle.com/datasets/"
            "ammarshafiq/healthcare-appointment-booking-calls-dataset"
        )
        assert hc.decision == "requires_licence_review"
        labels = {l.label for l in hc.capability_labels}
        assert "healthcare_appointment_booking" in labels
        assert "privacy_sensitive" in labels
        # Must not claim eligibility
        assert hc.access_notes is not None
        assert "NOT downloaded or accepted" in hc.access_notes


# ═══════════════════════════════════════════════════════════════════════════
#  Full promotion path coverage
# ═══════════════════════════════════════════════════════════════════════════


class TestFullPromotionPaths:
    """Every promotion path is tested end-to-end."""

    def test_gold_to_silver_via_bronze(self):
        """Gold -> (generation) -> Bronze -> Silver -> Gold path."""
        gen = GeneratorIdentity(model_id="generator", instance_id="test")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        # Bronze with matching scenario metadata
        bronze_scenario = _adapt_scenario(
            gold_spec, provenance="bronze", adjudication="pending"
        )
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=gold_spec.scenario_id,
            scenario=bronze_scenario,
        )
        # Bronze -> Silver
        ad1 = make_adjudication(model_id="judge-1", instance_id="lane-1",
                                 timestamp=datetime(2026, 7, 14, 12, 0, 0, tzinfo=timezone.utc))
        result1 = promote_candidate(bronze, adjudication=ad1)
        assert isinstance(result1, PromotionOutcome.Promoted)
        silver = result1.candidate
        assert silver.provenance == ProvenanceTier.SILVER
        # Silver -> Gold
        ad2 = make_adjudication(model_id="judge-2", instance_id="lane-1",
                                 timestamp=datetime(2026, 7, 14, 14, 0, 0, tzinfo=timezone.utc))
        result2 = promote_candidate(silver, adjudication=ad2)
        assert isinstance(result2, PromotionOutcome.Promoted)
        gold = result2.candidate
        assert gold.provenance == ProvenanceTier.GOLD
        assert gold.adjudication == AdjudicationState.ADJUDICATED
        # Check promotion history preserved
        assert len(gold.promotion_history) == 2
        assert gold.promotion_history[0].to_tier == ProvenanceTier.SILVER
        assert gold.promotion_history[1].to_tier == ProvenanceTier.GOLD

    def test_model_cannot_become_gold_directly(self):
        gen = GeneratorIdentity(model_id="generator", instance_id="test")
        gold_spec = load_candidate("valid_gold_seed.json").scenario
        scenario = _adapt_scenario(gold_spec, provenance="bronze", adjudication="pending")
        candidate = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc),
            source_scenario_id=gold_spec.scenario_id,
            scenario=scenario,
        )
        ad = make_adjudication(model_id="independent-judge")
        result = promote_candidate(candidate, adjudication=ad, target_tier=ProvenanceTier.GOLD)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.INVALID_TIER_TRANSITION


# ═══════════════════════════════════════════════════════════════════════════
#  Gold fixture validation
# ═══════════════════════════════════════════════════════════════════════════


class TestGoldFixtureValidation:
    """All three existing Gold fixtures validate as read-only evidence."""

    GOLD_PATHS = [
        Path("tests/fixtures/bernie_scenario_spec/booking_create_then_exact_duplicate.json"),
        Path("tests/fixtures/bernie_scenario_spec/booking_overlap_not_exact_duplicate.json"),
        Path("tests/fixtures/bernie_scenario_spec/interpret_clarify_temporal_bounds.json"),
    ]

    def test_all_gold_fixtures_load_as_scenario_spec(self):
        for path in self.GOLD_PATHS:
            assert path.exists(), f"Gold fixture not found: {path}"
            data = json.loads(path.read_text(encoding="utf-8"))
            spec = ReceptionScenarioSpec.model_validate(data)
            assert spec.provenance == "gold"
            assert spec.adjudication == "adjudicated"

    def test_all_gold_scenarios_can_be_embedded(self):
        for path in self.GOLD_PATHS:
            data = json.loads(path.read_text(encoding="utf-8"))
            spec = ReceptionScenarioSpec.model_validate(data)
            # Use the family from the scenario data to match
            family_str = data["family"]
            family = ScenarioFamily(family_str)
            candidate = CorpusCandidate(
                provenance=ProvenanceTier.GOLD,
                adjudication=AdjudicationState.ADJUDICATED,
                family=family,
                scenario=spec,
            )
            assert candidate.scenario.scenario_id == data["scenario_id"]

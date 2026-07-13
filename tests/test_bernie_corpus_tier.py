"""LC2 Corpus Factory — unit tests for provenance tiers, promotion, quarantine,
registry, and the CorpusCandidate wrapper.

All tests are pure-Python / domain-layer only.  No provider, route, database,
HTTP, or external-service dependency is required.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.services.bernie.corpus_tier import (
    AdjudicationState,
    CandidateRegistry,
    CorpusCandidate,
    GeneratorIdentity,
    JudgeIdentity,
    PromotionEvent,
    PromotionOutcome,
    ProvenanceTier,
    QuarantineDetail,
    QuarantineReason,
    ScenarioFamily,
    promote_candidate,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

FIXTURE_DIR = Path("tests/fixtures/bernie_corpus_tier")


# ═══════════════════════════════════════════════════════════════════════════
#  Helper to load a fixture as a CorpusCandidate
# ═══════════════════════════════════════════════════════════════════════════


def load_candidate(name: str) -> CorpusCandidate:
    path = FIXTURE_DIR / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return CorpusCandidate.model_validate(data)


def load_candidate_raw(name: str) -> dict:
    path = FIXTURE_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════════════════
#  Module import and enumeration tests
# ═══════════════════════════════════════════════════════════════════════════


def test_module_imports_cleanly():
    """Verification Plan item 6: corpus tier module imports cleanly."""
    from app.services.bernie.corpus_tier import (
        AdjudicationState,
        CorpusCandidate,
        ProvenanceTier,
        ScenarioFamily,
        promote_candidate,
    )

    assert ProvenanceTier.GOLD.value == "gold"
    assert AdjudicationState.ADJUDICATED.value == "adjudicated"
    assert list(ScenarioFamily) == [
        ScenarioFamily.BOOKING_CREATE,
        ScenarioFamily.CLARIFY_TEMPORAL,
    ]


def test_quarantine_reason_values():
    """All quarantine reasons are defined."""
    reasons = list(QuarantineReason)
    expected = {
        "self_certification",
        "schema_invalid",
        "authority_breach",
        "evidence_mismatch",
        "missing_provenance",
        "unsafe_instruction",
        "invalid_tier_transition",
        "generator_equals_judge",
        "missing_source_gold",
    }
    assert {r.value for r in reasons} == expected


# ═══════════════════════════════════════════════════════════════════════════
#  Generator / Judge identity tests
# ═══════════════════════════════════════════════════════════════════════════


class TestIdentity:
    def test_generator_identity_immutable(self):
        gen = GeneratorIdentity(model_id="test-model", instance_id="lane-1")
        with pytest.raises(Exception):
            gen.model_id = "other"  # type: ignore[misc]

    def test_judge_identity_immutable(self):
        judge = JudgeIdentity(model_id="judge-model")
        with pytest.raises(Exception):
            judge.model_id = "other"  # type: ignore[misc]

    def test_stable_key_comparison(self):
        gen1 = GeneratorIdentity(model_id="deepseek", instance_id="dw2")
        gen2 = GeneratorIdentity(model_id="deepseek", instance_id="dw2")
        assert gen1.stable_key() == gen2.stable_key()

    def test_stable_key_differs_when_instance_differs(self):
        gen1 = GeneratorIdentity(model_id="deepseek", instance_id="dw2")
        gen2 = GeneratorIdentity(model_id="deepseek", instance_id="dw3")
        assert gen1.stable_key() != gen2.stable_key()

    def test_generator_vs_judge_key_matches_rejected(self):
        gen = GeneratorIdentity(model_id="same", instance_id="x")
        judge = JudgeIdentity(model_id="same", instance_id="x")
        assert gen.stable_key() == judge.stable_key()

    def test_rejects_extra_keys(self):
        with pytest.raises(ValueError):
            GeneratorIdentity(model_id="m", unknown_extra="x")  # type: ignore[call-arg]


# ═══════════════════════════════════════════════════════════════════════════
#  CorpusCandidate wrapper tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCorpusCandidateWrapper:
    def test_gold_seed_loads(self):
        """Verify a valid Gold seed loads from fixture."""
        candidate = load_candidate("valid_gold_seed.json")
        assert candidate.provenance == ProvenanceTier.GOLD
        assert candidate.adjudication == AdjudicationState.ADJUDICATED
        assert candidate.generator_identity is None
        assert candidate.generation_timestamp is None
        assert candidate.source_scenario_id is None

    def test_silver_candidate_loads(self):
        """Verify a valid Silver candidate loads from fixture."""
        candidate = load_candidate("valid_silver_candidate.json")
        assert candidate.provenance == ProvenanceTier.SILVER
        assert candidate.adjudication == AdjudicationState.PENDING
        assert candidate.generator_identity is not None
        assert candidate.generation_timestamp is not None
        assert candidate.source_scenario_id == "booking_create_then_exact_duplicate"
        assert candidate.derivation_id is not None

    def test_wraps_reception_scenario_spec_without_mutation(self):
        """CorpusCandidate wraps ReceptionScenarioSpec without changing it."""
        candidate = load_candidate("valid_silver_candidate.json")
        assert isinstance(candidate.scenario, ReceptionScenarioSpec)
        # Verify the scenario still has its original schema fields
        assert candidate.scenario.spec_version == "lc1.v1"
        assert candidate.scenario.intended_action == "create"

    def test_stable_key_is_deterministic(self):
        c1 = load_candidate("valid_silver_candidate.json")
        c2 = load_candidate("valid_silver_candidate.json")
        assert c1.stable_key() == c2.stable_key()

    def test_derive_produces_new_candidate_with_overrides(self):
        candidate = load_candidate("valid_silver_candidate.json")
        derived = candidate.derive(provenance="bronze")
        assert derived.provenance == ProvenanceTier.BRONZE
        assert derived.scenario is candidate.scenario  # same object

    def test_rejects_extra_keys(self):
        data = load_candidate_raw("valid_silver_candidate.json")
        data["unknown_key"] = "should_fail"
        with pytest.raises(ValueError):
            CorpusCandidate.model_validate(data)

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

    def test_silver_must_have_generation_timestamp(self):
        data = load_candidate_raw("valid_silver_candidate.json")
        data["generation_timestamp"] = None
        with pytest.raises(ValueError, match="generation_timestamp"):
            CorpusCandidate.model_validate(data)

    def test_silver_must_have_source_scenario_id(self):
        data = load_candidate_raw("valid_silver_candidate.json")
        data["source_scenario_id"] = None
        with pytest.raises(ValueError, match="source_scenario_id"):
            CorpusCandidate.model_validate(data)


# ═══════════════════════════════════════════════════════════════════════════
#  Promotion tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPromotion:
    """Verification Plan items 7-9: promotion rules, self-cert, quarantine."""

    def _make_judge(self, model_id: str = "judge-model") -> JudgeIdentity:
        return JudgeIdentity(model_id=model_id, instance_id="judge-lane")

    # ── Gold → Silver ────────────────────────────────────────────────────

    def test_gold_seeds_silver_promotion(self):
        """Gold scenario can seed Silver generation (promote Bronze -> Silver)."""
        # Create a Bronze candidate with Gold source reference
        gen = GeneratorIdentity(model_id="generator", instance_id="test")
        scenario = load_candidate("valid_gold_seed.json").scenario
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=scenario.scenario_id,
            scenario=scenario,
        )
        result = promote_candidate(bronze, judge=self._make_judge())
        assert isinstance(result, PromotionOutcome.Promoted)
        assert result.new_tier == ProvenanceTier.SILVER

    # ── Silver → Gold ────────────────────────────────────────────────────

    def test_silver_to_gold_with_independent_judge(self):
        """Silver candidate promoted to Gold with an independent judge."""
        candidate = load_candidate("valid_silver_candidate.json")
        judge = self._make_judge()
        # Ensure judge differs from generator
        assert candidate.generator_identity.stable_key() != judge.stable_key()
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Promoted)
        assert result.new_tier == ProvenanceTier.GOLD
        assert result.new_adjudication == AdjudicationState.ADJUDICATED

    def test_silver_to_gold_requires_judge(self):
        """Silver promotion to Gold fails without a judge."""
        candidate = load_candidate("valid_silver_candidate.json")
        result = promote_candidate(candidate, judge=None)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.MISSING_PROVENANCE

    # ── Bronze → Silver ──────────────────────────────────────────────────

    def test_bronze_to_silver_with_judge(self):
        gen = GeneratorIdentity(model_id="bronze-gen", instance_id="test")
        scenario = load_candidate("valid_gold_seed.json").scenario
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=scenario.scenario_id,
            scenario=scenario,
        )
        judge = self._make_judge()
        assert gen.stable_key() != judge.stable_key()
        result = promote_candidate(bronze, judge=judge)
        assert isinstance(result, PromotionOutcome.Promoted)
        assert result.new_tier == ProvenanceTier.SILVER

    # ── Gold cannot be promoted further ───────────────────────────────────

    def test_gold_cannot_be_promoted(self):
        candidate = load_candidate("valid_gold_seed.json")
        result = promote_candidate(candidate)
        assert isinstance(result, PromotionOutcome.Rejected)
        assert "cannot be promoted" in result.reason

    # ── Promotion with explicit target tier ──────────────────────────────

    def test_promote_with_explicit_target(self):
        candidate = load_candidate("valid_silver_candidate.json")
        judge = self._make_judge()
        result = promote_candidate(candidate, judge=judge, target_tier=ProvenanceTier.GOLD)
        assert isinstance(result, PromotionOutcome.Promoted)
        assert result.new_tier == ProvenanceTier.GOLD

    def test_invalid_explicit_target_is_quarantined(self):
        """Promoting Silver to Bronze (regressive) is quarantined."""
        candidate = load_candidate("valid_silver_candidate.json")
        result = promote_candidate(
            candidate, judge=self._make_judge(), target_tier=ProvenanceTier.BRONZE
        )
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.INVALID_TIER_TRANSITION

    # ── Promotion event record ───────────────────────────────────────────

    def test_promotion_event_recorded(self):
        candidate = load_candidate("valid_silver_candidate.json")
        judge = self._make_judge()
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Promoted)
        assert result.event.from_tier == ProvenanceTier.SILVER
        assert result.event.to_tier == ProvenanceTier.GOLD
        assert result.event.judge is not None
        assert result.event.judge.stable_key() == judge.stable_key()


# ═══════════════════════════════════════════════════════════════════════════
#  Self-certification guard tests
# ═══════════════════════════════════════════════════════════════════════════


class TestSelfCertification:
    """Verification Plan item 8: self-certification guard."""

    def test_self_certification_is_quarantined(self):
        """Generator == judge results in quarantine."""
        candidate = load_candidate("self_certified_reject.json")
        judge = JudgeIdentity(model_id="same-model", instance_id="same-instance")
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.SELF_CERTIFICATION

    def test_self_certification_by_stable_key(self):
        """Same stable key even with different object is caught."""
        gen = GeneratorIdentity(model_id="model-a", instance_id="lane-1")
        judge = JudgeIdentity(model_id="model-a", instance_id="lane-1")
        assert gen.stable_key() == judge.stable_key()
        candidate = load_candidate("valid_silver_candidate.json")
        # Replace generator identity using JSON-safe serialization
        candidate_dict = json.loads(
            candidate.model_dump_json()
        )
        candidate_dict["generator_identity"] = {
            "model_id": "model-a",
            "instance_id": "lane-1",
        }
        modified = CorpusCandidate.model_validate(candidate_dict)
        result = promote_candidate(modified, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.SELF_CERTIFICATION

    def test_different_models_pass_self_cert_check(self):
        """Different model_ids are accepted."""
        gen = GeneratorIdentity(model_id="model-a", instance_id="lane-1")
        judge = JudgeIdentity(model_id="model-b", instance_id="lane-1")
        assert gen.stable_key() != judge.stable_key()
        candidate = load_candidate("valid_silver_candidate.json")
        result = promote_candidate(candidate, judge=judge)
        # Should pass self-cert check (may fail elsewhere, but not on self-cert)
        assert not isinstance(result, PromotionOutcome.Quarantined) or (
            result.quarantine.reason != QuarantineReason.SELF_CERTIFICATION
        )


# ═══════════════════════════════════════════════════════════════════════════
#  Quarantine trigger tests
# ═══════════════════════════════════════════════════════════════════════════


class TestQuarantine:
    """Verification Plan item 9: quarantine triggers."""

    def test_quarantine_schema_invalid(self):
        """Schema-invalid scenario is quarantined."""
        # Construct a candidate with an invalid embedded scenario
        # (bypassing model validation)
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        judge = JudgeIdentity(model_id="judge", instance_id="x")
        # Create a scenario with empty dialogue_turns which is invalid
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        scenario["dialogue_turns"] = []
        # Build with model_construct to bypass validation
        invalid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(  # type: ignore[call-arg]
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id="test-source",
            scenario=invalid_scenario,
        )
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.SCHEMA_INVALID

    def test_quarantine_authority_breach(self):
        """Authority breach (write_authority claimed) is quarantined."""
        candidate = load_candidate("quarantine_authority_breach.json")
        judge = self._make_judge()
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.AUTHORITY_BREACH

    def _make_judge(self, model_id: str = "judge-model") -> JudgeIdentity:
        return JudgeIdentity(model_id=model_id, instance_id="judge-lane")

    def test_quarantine_evidence_mismatch(self):
        """Evidence mismatch (bad source span) is quarantined.

        Note: the mismatch is caught by schema validation first
        (ReceptionScenarioSpec model_validator checks span/text matches),
        so the quarantine reason is SCHEMA_INVALID.
        """
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        judge = self._make_judge()
        # Create a scenario where source spans don't match
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        # Alter a span to create mismatch
        scenario["source_spans"]["earliest_time"] = [
            {"turn_index": 0, "start": 0, "end": 4, "text": "NOPE"}
        ]
        # Reconstruct using model_construct to bypass scenario validation
        valid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id="test-source",
            scenario=valid_scenario,
        )
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        # Schema validation catches the mismatch first
        assert result.quarantine.reason in (
            QuarantineReason.SCHEMA_INVALID,
            QuarantineReason.EVIDENCE_MISMATCH,
        )

    def test_quarantine_missing_provenance(self):
        """Missing provenance fields trigger quarantine."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        judge = self._make_judge()
        scenario = load_candidate("valid_gold_seed.json").scenario
        # Create candidate without source_scenario_id (via construct)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=None,
            scenario=scenario,
        )
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.MISSING_PROVENANCE

    def test_quarantine_missing_source_gold(self):
        """Silver candidate without source is quarantined via missing_provenance."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        judge = self._make_judge()
        scenario = load_candidate("valid_gold_seed.json").scenario
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=None,
            scenario=scenario,
        )
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.MISSING_PROVENANCE

    def test_quarantine_invalid_tier_transition(self):
        """Bronze → Gold (skipping Silver) is quarantined."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        judge = self._make_judge()
        scenario = load_candidate("valid_gold_seed.json").scenario
        candidate = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=scenario.scenario_id,
            scenario=scenario,
        )
        result = promote_candidate(candidate, judge=judge, target_tier=ProvenanceTier.GOLD)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason == QuarantineReason.INVALID_TIER_TRANSITION


# ═══════════════════════════════════════════════════════════════════════════
#  Candidate registry tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCandidateRegistry:
    """Verification Plan item 10: registry schema validation."""

    REGISTRY_PATH = FIXTURE_DIR / "registry_evaluation_candidates.json"

    def test_registry_loads(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        assert len(registry.entries) >= 3

    def test_three_required_candidates_present(self):
        data = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        registry = CandidateRegistry.model_validate(data)
        names = {e.name for e in registry.entries}
        assert "Schema-Guided Dialogue / SGD-X" in names
        assert "SMCalFlow" in names
        assert "MultiWOZ research data" in names

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

    def test_generator_identity_rejects_extra_field(self):
        with pytest.raises(ValueError):
            GeneratorIdentity(
                model_id="test", unknown_field="x"  # type: ignore[call-arg]
            )

    def test_judge_identity_rejects_extra_field(self):
        with pytest.raises(ValueError):
            JudgeIdentity(
                model_id="test", unknown_field="x"  # type: ignore[call-arg]
            )


# ═══════════════════════════════════════════════════════════════════════════
#  Source-coordinate validation tests
# ═══════════════════════════════════════════════════════════════════════════


class TestSourceCoordinateValidation:
    def test_valid_source_spans_pass(self):
        """Valid source spans in the embedded scenario pass validation."""
        candidate = load_candidate("valid_gold_seed.json")
        # No error when accessing source spans
        assert len(candidate.scenario.source_spans) > 0

    def test_evidence_mismatch_detected(self):
        """Source spans that don't match utterance text are caught.

        Schema validation catches the mismatch first (ReceptionScenarioSpec's
        own model_validator checks span/text alignment).
        """
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        judge = JudgeIdentity(model_id="judge", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        # Break a span
        scenario["source_spans"]["patient"] = [
            {"turn_index": 0, "start": 0, "end": 5, "text": "WRONG"}
        ]
        invalid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id="test-source",
            scenario=invalid_scenario,
        )
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason in (
            QuarantineReason.SCHEMA_INVALID,
            QuarantineReason.EVIDENCE_MISMATCH,
        )

    def test_evidence_mismatch_missing_turn(self):
        """Span referencing a missing turn is caught.

        Schema validation catches the mismatch first.
        """
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        judge = JudgeIdentity(model_id="judge", instance_id="x")
        scenario_dict = load_candidate("valid_gold_seed.json").model_dump()
        scenario = scenario_dict["scenario"]
        # Reference turn index beyond available turns
        scenario["source_spans"]["patient"] = [
            {"turn_index": 99, "start": 0, "end": 1, "text": "X"}
        ]
        invalid_scenario = ReceptionScenarioSpec.model_construct(**scenario)
        candidate = CorpusCandidate.model_construct(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id="test-source",
            scenario=invalid_scenario,
        )
        result = promote_candidate(candidate, judge=judge)
        assert isinstance(result, PromotionOutcome.Quarantined)
        assert result.quarantine.reason in (
            QuarantineReason.SCHEMA_INVALID,
            QuarantineReason.EVIDENCE_MISMATCH,
        )


# ═══════════════════════════════════════════════════════════════════════════
#  Derivation ID / stable hash tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDerivationId:
    def test_derivation_id_is_deterministic(self):
        c1 = load_candidate("valid_silver_candidate.json")
        c2 = load_candidate("valid_silver_candidate.json")
        assert c1.derivation_id == c2.derivation_id

    def test_derivation_id_changes_with_seed(self):
        from app.services.bernie.corpus_tier import _compute_derivation_id

        gen = GeneratorIdentity(model_id="test", instance_id="x")
        ts = datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc)
        id1 = _compute_derivation_id("src-1", gen.stable_key(), ts, seed="seed-a")
        id2 = _compute_derivation_id("src-1", gen.stable_key(), ts, seed="seed-b")
        assert id1 != id2

    def test_derivation_id_auto_computed(self):
        """Silver candidate without derivation_id gets one auto-computed."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        scenario = load_candidate("valid_gold_seed.json").scenario
        candidate = CorpusCandidate(  # type: ignore[call-arg]
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=scenario.scenario_id,
            derivation_id=None,
            scenario=scenario,
        )
        assert candidate.derivation_id is not None
        assert len(candidate.derivation_id) == 32  # SHA-256 hex[:32]

    def test_derivation_id_length(self):
        """Derivation ID is a 32-char hex string."""
        gen = GeneratorIdentity(model_id="test", instance_id="x")
        ts = datetime(2026, 7, 14, 10, 0, 0, tzinfo=timezone.utc)
        from app.services.bernie.corpus_tier import _compute_derivation_id

        did = _compute_derivation_id("src-1", gen.stable_key(), ts)
        assert len(did) == 32
        assert all(c in "0123456789abcdef" for c in did)


# ═══════════════════════════════════════════════════════════════════════════
#  Registry content rejection tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistryContentRejection:
    def test_registry_rejects_embedded_dialogue(self):
        """Registry entry cannot contain dialogue payload."""
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
        """Registry entry cannot contain downloaded dataset content."""
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
#  Fixture-level validation tests (conservative registry entries)
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistryFixture:
    """The three conservative registry entries are verified."""

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


# ═══════════════════════════════════════════════════════════════════════════
#  Full promotion path coverage
# ═══════════════════════════════════════════════════════════════════════════


class TestFullPromotionPaths:
    """Every promotion path is tested."""

    def test_gold_to_silver_via_bronze(self):
        """Gold -> (generation) -> Bronze -> Silver path."""
        gen = GeneratorIdentity(model_id="generator", instance_id="test")
        judge = JudgeIdentity(model_id="judge", instance_id="test")
        scenario = load_candidate("valid_gold_seed.json").scenario
        bronze = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=scenario.scenario_id,
            scenario=scenario,
        )
        result = promote_candidate(bronze, judge=judge)
        assert isinstance(result, PromotionOutcome.Promoted)
        assert result.new_tier == ProvenanceTier.SILVER
        # Silver to Gold
        silver = CorpusCandidate(
            provenance=ProvenanceTier.SILVER,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            judge_identity=None,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=scenario.scenario_id,
            scenario=scenario,
        )
        result2 = promote_candidate(silver, judge=judge)
        assert isinstance(result2, PromotionOutcome.Promoted)
        assert result2.new_tier == ProvenanceTier.GOLD

    def test_model_cannot_become_gold_directly(self):
        """Model-generated candidates cannot become Gold directly (must go through Silver -> Gold)."""
        gen = GeneratorIdentity(model_id="generator", instance_id="test")
        judge = JudgeIdentity(model_id="judge", instance_id="test")
        scenario = load_candidate("valid_gold_seed.json").scenario
        # Bronze -> Gold attempt (skipping Silver)
        candidate = CorpusCandidate(
            provenance=ProvenanceTier.BRONZE,
            adjudication=AdjudicationState.PENDING,
            family=ScenarioFamily.BOOKING_CREATE,
            generator_identity=gen,
            generation_timestamp=datetime.now(timezone.utc),
            source_scenario_id=scenario.scenario_id,
            scenario=scenario,
        )
        result = promote_candidate(candidate, judge=judge, target_tier=ProvenanceTier.GOLD)
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
        """All three Gold fixtures can be embedded in a CorpusCandidate."""
        for path in self.GOLD_PATHS:
            data = json.loads(path.read_text(encoding="utf-8"))
            spec = ReceptionScenarioSpec.model_validate(data)
            candidate = CorpusCandidate(
                provenance=ProvenanceTier.GOLD,
                adjudication=AdjudicationState.ADJUDICATED,
                family=ScenarioFamily.BOOKING_CREATE,
                scenario=spec,
            )
            assert candidate.scenario.scenario_id == data["scenario_id"]

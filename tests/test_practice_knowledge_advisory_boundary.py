"""Adversarial tests for the practice-knowledge advisory boundary.

These tests prove that:
1. to_advisory_frame produces only a BernieAdvisoryWarningFrame (status=advisory).
2. A PracticeKnowledgeResult cannot construct or alter a ConfirmAffordanceDecision.
3. A PracticeKnowledgeResult cannot construct or alter a BernieReceptionPolicyDecision.
4. evaluate_confirm_affordance signature takes no knowledge input.
5. Import boundary: diary confirm_gate.py and policy.py do not import
   app.services.practice_knowledge.
6. Retrieved facts cannot create no-slot truth, roster truth, confirm authority,
   freshness/audit evidence, or write payloads.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from app.services.diary.confirm_gate import (
    ConfirmAffordanceDecision,
    ConfirmAffordanceGate,
    evaluate_confirm_affordance,
)
from app.services.diary.frames import BernieAdvisoryWarningFrame
from app.services.practice_knowledge.boundary import to_advisory_frame
from app.services.practice_knowledge.envelopes import PracticeKnowledgeResult
from app.services.practice_knowledge.examples import DEV_CLINIC_FACTS
from app.services.practice_knowledge.retriever import InMemoryPracticeKnowledgeRetriever
from app.services.practice_knowledge.envelopes import PracticeKnowledgeQuery
from app.services.practice_knowledge.facts import PracticeFactKind


REFERENCE_DATE = date(2026, 7, 3)


@pytest.fixture()
def retriever() -> InMemoryPracticeKnowledgeRetriever:
    return InMemoryPracticeKnowledgeRetriever(DEV_CLINIC_FACTS)


@pytest.fixture()
def sample_result(retriever) -> PracticeKnowledgeResult:
    q = PracticeKnowledgeQuery(query_text="Dr Shera Friday opening hours")
    return retriever.retrieve(q)


class TestToAdvisoryFrameProducesAdvisoryOnly:
    def test_frame_type_is_advisory_warning(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.frame_type == "advisory_warning"

    def test_frame_status_is_advisory(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.status == "advisory"

    def test_frame_is_bernie_advisory_warning_frame(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert isinstance(frame, BernieAdvisoryWarningFrame)

    def test_frame_payload_carries_advisory_only_true(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.payload["advisory_only"] is True

    def test_frame_payload_carries_cannot_affect_slots_true(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.payload["cannot_affect_slots"] is True

    def test_frame_payload_carries_cannot_affect_policy_true(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.payload["cannot_affect_policy"] is True

    def test_frame_payload_carries_cannot_affect_confirm_true(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.payload["cannot_affect_confirm"] is True

    def test_frame_payload_carries_fact_snapshots(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert "fact_snapshots" in frame.payload
        assert isinstance(frame.payload["fact_snapshots"], list)

    def test_frame_snapshots_have_no_write_payloads(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        for snap in frame.payload["fact_snapshots"]:
            assert "confirm_grade_allowed" not in snap
            assert "slot_id" not in snap
            assert "appointment_id" not in snap
            assert "write" not in snap
            assert "mutation" not in snap

    def test_reason_code_defaults_to_practice_knowledge_advisory(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.reason_code == "practice_knowledge_advisory"

    def test_custom_reason_code_accepted(self, sample_result):
        frame = to_advisory_frame(
            sample_result, reference_date=REFERENCE_DATE, reason_code="friday_roster_advisory"
        )
        assert frame.reason_code == "friday_roster_advisory"


class TestBoundaryAssertsInvariants:
    def test_boundary_rejects_corrupted_result_advisory_only(self):
        result = PracticeKnowledgeResult()
        object.__setattr__(result, "advisory_only", False)
        with pytest.raises(AssertionError, match="advisory_only"):
            to_advisory_frame(result, reference_date=REFERENCE_DATE)

    def test_boundary_rejects_corrupted_result_cannot_affect_slots(self):
        result = PracticeKnowledgeResult()
        object.__setattr__(result, "cannot_affect_slots", False)
        with pytest.raises(AssertionError, match="cannot_affect_slots"):
            to_advisory_frame(result, reference_date=REFERENCE_DATE)

    def test_boundary_rejects_corrupted_result_cannot_affect_policy(self):
        result = PracticeKnowledgeResult()
        object.__setattr__(result, "cannot_affect_policy", False)
        with pytest.raises(AssertionError, match="cannot_affect_policy"):
            to_advisory_frame(result, reference_date=REFERENCE_DATE)

    def test_boundary_rejects_corrupted_result_cannot_affect_confirm(self):
        result = PracticeKnowledgeResult()
        object.__setattr__(result, "cannot_affect_confirm", False)
        with pytest.raises(AssertionError, match="cannot_affect_confirm"):
            to_advisory_frame(result, reference_date=REFERENCE_DATE)


class TestCannotConstructConfirmAffordanceDecision:
    def test_knowledge_result_has_no_confirm_grade_allowed_field(self, sample_result):
        assert not hasattr(sample_result, "confirm_grade_allowed")

    def test_knowledge_result_has_no_gate_field(self, sample_result):
        assert not hasattr(sample_result, "gate")

    def test_advisory_frame_is_not_confirm_affordance_decision(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert not isinstance(frame, ConfirmAffordanceDecision)

    def test_advisory_frame_payload_has_no_confirm_grade_allowed(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert "confirm_grade_allowed" not in frame.payload


class TestCannotAlterConfirmAffordanceGate:
    """Prove retrieval results cannot influence evaluate_confirm_affordance."""

    def test_evaluate_confirm_affordance_signature_has_no_knowledge_param(self):
        sig = inspect.signature(evaluate_confirm_affordance)
        param_names = set(sig.parameters)
        assert "knowledge" not in param_names
        assert "practice_knowledge" not in param_names
        assert "retrieval" not in param_names
        assert "facts" not in param_names

    def test_knowledge_result_cannot_be_passed_to_confirm_gate(self, sample_result):
        from app.services.diary.policy import BernieReceptionPolicyDecision
        policy = BernieReceptionPolicyDecision(
            availability="not_evaluated",
            can_search_slots=False,
            must_ask_clarification=False,
            can_offer_candidates=False,
            can_prepare_proposal=False,
            must_block_confirmation=False,
            advisory_warnings_only=True,
            roster_unavailable=False,
            search_ran_no_candidates=False,
        )
        # evaluate_confirm_affordance must not accept a knowledge kwarg
        with pytest.raises(TypeError):
            evaluate_confirm_affordance(policy, knowledge=sample_result, has_staged_proposal=False)


class TestCannotCreateNoSlotTruth:
    def test_knowledge_result_has_no_slot_candidates_field(self, sample_result):
        assert not hasattr(sample_result, "candidate_count")
        assert not hasattr(sample_result, "slot_candidates")

    def test_advisory_frame_payload_has_no_slot_fields(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert "candidate_count" not in frame.payload
        assert "slot_candidates" not in frame.payload
        assert "search_ran_no_candidates" not in frame.payload
        assert "roster_unavailable" not in frame.payload

    def test_knowledge_items_have_no_appointment_ids(self, sample_result):
        for item in sample_result.items:
            snap = {
                "fact_id": item.fact.fact_id,
                "kind": item.fact.kind.value,
                "subject": item.fact.subject,
                "body": item.fact.body,
            }
            assert "appointment_id" not in snap
            assert "slot_id" not in snap
            assert "booking_id" not in snap


class TestCannotCreateRosterTruth:
    """Facts may describe roster policy, but cannot act as authoritative roster decisions."""

    def test_knowledge_result_advisory_only_true(self, sample_result):
        assert sample_result.advisory_only is True

    def test_knowledge_items_authority_tier_is_advisory(self, retriever):
        q = PracticeKnowledgeQuery(query_text="Dr Shera Friday", kinds=[PracticeFactKind.roster])
        result = retriever.retrieve(q)
        for item in result.items:
            assert item.fact.authority_tier == "advisory"

    def test_roster_fact_does_not_create_bernie_roster_schedule_frame(self, retriever):
        from app.services.diary.frames import BernieRosterScheduleFrame
        q = PracticeKnowledgeQuery(query_text="Dr Shera Friday", kinds=[PracticeFactKind.roster])
        result = retriever.retrieve(q)
        frame = to_advisory_frame(result, reference_date=REFERENCE_DATE)
        assert not isinstance(frame, BernieRosterScheduleFrame)
        assert frame.frame_type == "advisory_warning"
        assert frame.status == "advisory"


class TestCannotCreateFreshnessOrAuditEvidence:
    def test_knowledge_result_has_no_staleness_verdict(self, sample_result):
        assert not hasattr(sample_result, "staleness_verdict")
        assert not hasattr(sample_result, "fresh_for_turn_ref")

    def test_advisory_frame_fresh_for_turn_ref_is_none(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert frame.fresh_for_turn_ref is None

    def test_advisory_frame_payload_has_no_audit_fields(self, sample_result):
        frame = to_advisory_frame(sample_result, reference_date=REFERENCE_DATE)
        assert "audit_log_id" not in frame.payload
        assert "confirmed_by" not in frame.payload
        assert "staleness_verdict" not in frame.payload


class TestImportBoundary:
    """practice_knowledge must not be imported by diary policy, confirm_gate, or temporal."""

    FORBIDDEN_IMPORTERS = [
        "app/services/diary/confirm_gate.py",
        "app/services/diary/policy.py",
        "app/services/diary/temporal.py",
        "app/services/diary/envelopes.py",
    ]

    @pytest.mark.parametrize("rel_path", FORBIDDEN_IMPORTERS)
    def test_diary_file_does_not_import_practice_knowledge(self, rel_path):
        repo_root = Path(__file__).parent.parent
        source_path = repo_root / rel_path
        if not source_path.exists():
            pytest.skip(f"{rel_path} not found")
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert "practice_knowledge" not in node.module, (
                        f"{rel_path} imports from practice_knowledge: {node.module}"
                    )
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert "practice_knowledge" not in alias.name, (
                            f"{rel_path} imports practice_knowledge: {alias.name}"
                        )

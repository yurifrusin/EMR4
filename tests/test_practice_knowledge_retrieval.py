"""Tests for PracticeKnowledgeQuery, PracticeKnowledgeResult envelopes, and
InMemoryPracticeKnowledgeRetriever.

Known-answer assertions prove deterministic retrieval over the dev-clinic fact set.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.services.practice_knowledge.envelopes import (
    PracticeKnowledgeQuery,
    PracticeKnowledgeResult,
)
from app.services.practice_knowledge.examples import DEV_CLINIC_FACTS
from app.services.practice_knowledge.facts import PracticeFactKind
from app.services.practice_knowledge.retriever import (
    InMemoryPracticeKnowledgeRetriever,
    PracticeKnowledgeRetriever,
)


@pytest.fixture()
def retriever() -> InMemoryPracticeKnowledgeRetriever:
    return InMemoryPracticeKnowledgeRetriever(DEV_CLINIC_FACTS)


def _query(text: str, **kwargs) -> PracticeKnowledgeQuery:
    return PracticeKnowledgeQuery(query_text=text, **kwargs)


class TestPracticeKnowledgeQuery:
    def test_advisory_only_is_always_true(self):
        q = _query("opening hours")
        assert q.advisory_only is True

    def test_contains_phi_is_always_false(self):
        q = _query("opening hours")
        assert q.contains_phi is False

    def test_cannot_set_advisory_only_false(self):
        with pytest.raises((ValidationError, TypeError)):
            PracticeKnowledgeQuery(query_text="test", advisory_only=False)

    def test_cannot_set_contains_phi_true(self):
        with pytest.raises((ValidationError, TypeError)):
            PracticeKnowledgeQuery(query_text="test", contains_phi=True)

    def test_kinds_filter_accepted(self):
        q = _query("roster", kinds=[PracticeFactKind.roster])
        assert q.kinds == [PracticeFactKind.roster]

    def test_max_results_defaults_to_five(self):
        q = _query("test")
        assert q.max_results == 5


class TestPracticeKnowledgeResult:
    def test_structural_invariants_always_true(self):
        result = PracticeKnowledgeResult()
        assert result.advisory_only is True
        assert result.cannot_affect_slots is True
        assert result.cannot_affect_policy is True
        assert result.cannot_affect_confirm is True

    def test_schema_version_is_fixed(self):
        result = PracticeKnowledgeResult()
        assert result.schema_version == "practice.knowledge.result.v1"

    def test_cannot_set_advisory_only_false(self):
        with pytest.raises((ValidationError, TypeError)):
            PracticeKnowledgeResult(advisory_only=False)

    def test_cannot_set_cannot_affect_slots_false(self):
        with pytest.raises((ValidationError, TypeError)):
            PracticeKnowledgeResult(cannot_affect_slots=False)

    def test_cannot_set_cannot_affect_policy_false(self):
        with pytest.raises((ValidationError, TypeError)):
            PracticeKnowledgeResult(cannot_affect_policy=False)

    def test_cannot_set_cannot_affect_confirm_false(self):
        with pytest.raises((ValidationError, TypeError)):
            PracticeKnowledgeResult(cannot_affect_confirm=False)


class TestInMemoryRetrieverProtocolConformance:
    def test_retriever_satisfies_protocol(self, retriever):
        assert isinstance(retriever, PracticeKnowledgeRetriever)


class TestInMemoryRetrieverKnownAnswers:
    def test_friday_query_returns_roster_fact(self, retriever):
        q = _query("Dr Shera Friday")
        result = retriever.retrieve(q)
        fact_ids = [item.fact.fact_id for item in result.items]
        assert "roster-001" in fact_ids

    def test_opening_hours_query_returns_hours_fact(self, retriever):
        q = _query("opening hours")
        result = retriever.retrieve(q)
        fact_ids = [item.fact.fact_id for item in result.items]
        assert "opening-001" in fact_ids

    def test_phone_query_returns_contact_fact(self, retriever):
        q = _query("phone number contact")
        result = retriever.retrieve(q)
        fact_ids = [item.fact.fact_id for item in result.items]
        assert "contact-001" in fact_ids

    def test_new_patient_query_returns_policy_fact(self, retriever):
        q = _query("new patient duration")
        result = retriever.retrieve(q)
        fact_ids = [item.fact.fact_id for item in result.items]
        assert "policy-001" in fact_ids

    def test_urgent_query_returns_reception_guidance(self, retriever):
        q = _query("urgent same day")
        result = retriever.retrieve(q)
        fact_ids = [item.fact.fact_id for item in result.items]
        assert "reception-001" in fact_ids

    def test_prescription_query_returns_rx_guidance(self, retriever):
        q = _query("repeat prescription")
        result = retriever.retrieve(q)
        fact_ids = [item.fact.fact_id for item in result.items]
        assert "reception-002" in fact_ids


class TestDeterminism:
    def test_same_query_returns_same_order(self, retriever):
        q = _query("Dr Shera Friday")
        result_a = retriever.retrieve(q)
        result_b = retriever.retrieve(q)
        assert [item.fact.fact_id for item in result_a.items] == [
            item.fact.fact_id for item in result_b.items
        ]

    def test_same_query_returns_same_ranks(self, retriever):
        q = _query("opening hours")
        result_a = retriever.retrieve(q)
        result_b = retriever.retrieve(q)
        assert [item.rank for item in result_a.items] == [item.rank for item in result_b.items]


class TestKindFilter:
    def test_kind_filter_restricts_to_roster(self, retriever):
        q = _query("Shera Friday", kinds=[PracticeFactKind.roster])
        result = retriever.retrieve(q)
        assert all(item.fact.kind == PracticeFactKind.roster for item in result.items)

    def test_kind_filter_restricts_to_contact(self, retriever):
        q = _query("phone hours", kinds=[PracticeFactKind.contact])
        result = retriever.retrieve(q)
        assert all(item.fact.kind == PracticeFactKind.contact for item in result.items)

    def test_kind_filter_returns_empty_for_no_match(self, retriever):
        # No facts have kind roster with keyword "prescription"
        q = _query("prescription telehealth", kinds=[PracticeFactKind.roster])
        result = retriever.retrieve(q)
        assert result.items == []


class TestMaxResults:
    def test_max_results_caps_output(self, retriever):
        q = _query("appointment", max_results=2)
        result = retriever.retrieve(q)
        assert len(result.items) <= 2

    def test_ranks_are_sequential_from_one(self, retriever):
        q = _query("clinic", max_results=3)
        result = retriever.retrieve(q)
        ranks = [item.rank for item in result.items]
        assert ranks == list(range(1, len(ranks) + 1))


class TestResultInvariants:
    def test_result_advisory_only_always_true(self, retriever):
        q = _query("any query")
        result = retriever.retrieve(q)
        assert result.advisory_only is True

    def test_result_cannot_affect_slots_always_true(self, retriever):
        q = _query("any query")
        result = retriever.retrieve(q)
        assert result.cannot_affect_slots is True

    def test_result_cannot_affect_policy_always_true(self, retriever):
        q = _query("any query")
        result = retriever.retrieve(q)
        assert result.cannot_affect_policy is True

    def test_result_cannot_affect_confirm_always_true(self, retriever):
        q = _query("any query")
        result = retriever.retrieve(q)
        assert result.cannot_affect_confirm is True

    def test_items_carry_provenance(self, retriever):
        q = _query("Dr Shera Friday")
        result = retriever.retrieve(q)
        for item in result.items:
            assert item.provenance is not None
            assert item.provenance.author != ""

    def test_staff_copy_is_nonempty_when_results_exist(self, retriever):
        q = _query("Dr Shera Friday")
        result = retriever.retrieve(q)
        if result.items:
            assert result.staff_copy != ""

    def test_empty_result_staff_copy_is_empty_string(self, retriever):
        # Query that matches nothing
        q = _query("xyzzy nonexistent zork", kinds=[PracticeFactKind.roster])
        result = retriever.retrieve(q)
        assert result.items == []
        assert result.staff_copy == ""

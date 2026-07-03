"""Tests for PracticeFact and PracticeFactProvenance models."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.services.practice_knowledge.facts import (
    PracticeFact,
    PracticeFactKind,
    PracticeFactProvenance,
    PracticeFactSourceKind,
    ReviewStatus,
)


def _provenance(**kwargs) -> PracticeFactProvenance:
    defaults = dict(
        source_kind=PracticeFactSourceKind.staff_authored,
        source_ref="test-ref",
        author="test@clinic.local",
        captured_at=datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc),
        effective_from=date(2026, 7, 1),
        review_status=ReviewStatus.current,
    )
    defaults.update(kwargs)
    return PracticeFactProvenance(**defaults)


def _fact(**kwargs) -> PracticeFact:
    defaults = dict(
        fact_id="fact-001",
        kind=PracticeFactKind.roster,
        subject="Dr Shera Friday availability",
        body="Dr Shera does not work Fridays.",
        provenance=_provenance(),
    )
    defaults.update(kwargs)
    return PracticeFact(**defaults)


class TestPracticeFactProvenance:
    def test_round_trips_all_fields(self):
        prov = _provenance(
            effective_to=date(2027, 1, 1),
            last_reviewed=date(2026, 7, 1),
            review_status=ReviewStatus.needs_review,
        )
        assert prov.source_kind == PracticeFactSourceKind.staff_authored
        assert prov.effective_to == date(2027, 1, 1)
        assert prov.review_status == ReviewStatus.needs_review

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PracticeFactProvenance(
                source_kind="staff_authored",
                source_ref="x",
                author="a",
                captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                unknown_field="bad",
            )

    def test_all_source_kinds_valid(self):
        for sk in PracticeFactSourceKind:
            prov = _provenance(source_kind=sk)
            assert prov.source_kind == sk

    def test_all_review_statuses_valid(self):
        for rs in ReviewStatus:
            prov = _provenance(review_status=rs)
            assert prov.review_status == rs


class TestPracticeFact:
    def test_round_trips(self):
        fact = _fact()
        assert fact.authority_tier == "advisory"
        assert fact.contains_phi is False
        assert fact.kind == PracticeFactKind.roster

    def test_all_kinds_accepted(self):
        for kind in PracticeFactKind:
            fact = _fact(kind=kind)
            assert fact.kind == kind

    def test_authority_tier_is_always_advisory(self):
        fact = _fact()
        assert fact.authority_tier == "advisory"

    def test_contains_phi_is_always_false(self):
        fact = _fact()
        assert fact.contains_phi is False

    def test_cannot_set_contains_phi_true(self):
        with pytest.raises(ValidationError):
            PracticeFact(
                fact_id="fact-phi",
                kind=PracticeFactKind.roster,
                subject="subject",
                body="body",
                provenance=_provenance(),
                contains_phi=True,
            )

    def test_cannot_set_authority_tier_non_advisory(self):
        with pytest.raises(ValidationError):
            PracticeFact(
                fact_id="fact-x",
                kind=PracticeFactKind.policy,
                subject="s",
                body="b",
                provenance=_provenance(),
                authority_tier="authoritative",
            )

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PracticeFact(
                fact_id="fact-extra",
                kind=PracticeFactKind.contact,
                subject="s",
                body="b",
                provenance=_provenance(),
                slot_authority=True,
            )

    def test_tags_default_empty(self):
        fact = _fact()
        assert fact.tags == []

    def test_tags_accepted(self):
        fact = _fact(tags=["friday", "roster"])
        assert fact.tags == ["friday", "roster"]

    def test_fact_id_required_nonempty(self):
        with pytest.raises(ValidationError):
            _fact(fact_id="")

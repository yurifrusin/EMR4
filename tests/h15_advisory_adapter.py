"""Test-only adapter from H15 synthetic candidates to advisory practice knowledge."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.practice_knowledge.envelopes import (
    PracticeKnowledgeResult,
    PracticeKnowledgeResultItem,
)
from app.services.practice_knowledge.facts import (
    PracticeFact,
    PracticeFactKind,
    PracticeFactProvenance,
    PracticeFactSourceKind,
    ReviewStatus,
)


def candidates_to_practice_knowledge_result(payload: dict[str, Any]) -> PracticeKnowledgeResult:
    """Convert authored H15 read-only candidates into advisory-only facts.

    This helper is intentionally test-only. It does not read raw diary files,
    ignored local outputs, provider results, or runtime memory.
    """
    items: list[PracticeKnowledgeResultItem] = []
    for index, candidate in enumerate(payload["candidates"], start=1):
        fact = PracticeFact(
            fact_id=f"h15-{candidate['synthetic_event_id']}",
            kind=PracticeFactKind.reception_guidance,
            subject="Historical diary read-only schedule explanation candidate",
            body="Synthetic read-only schedule explanation candidate; advisory only.",
            tags=[
                "h15_synthetic",
                "read_only",
                candidate["action_name"],
                candidate["confidence_label"],
            ],
            provenance=PracticeFactProvenance(
                source_kind=PracticeFactSourceKind.imported_doc,
                source_ref="h15-synthetic-candidates",
                author="ariadne",
                captured_at=datetime(2026, 7, 6, 8, 0, tzinfo=timezone.utc),
                review_status=ReviewStatus.current,
            ),
            contains_phi=False,
        )
        items.append(
            PracticeKnowledgeResultItem(
                fact=fact,
                match_basis="synthetic_candidate_id",
                rank=index,
                score=0.1,
                provenance=fact.provenance,
            )
        )

    return PracticeKnowledgeResult(
        items=items,
        retrieval_basis="h15_authored_synthetic_test_adapter",
        staff_copy="Synthetic read-only historical diary candidates are advisory only.",
    )

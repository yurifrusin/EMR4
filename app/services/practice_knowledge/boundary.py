"""Advisory boundary between practice-knowledge retrieval and Bernie frames.

to_advisory_frame is the ONLY supported exit point for retrieval results into
the Bernie domain. It produces a BernieAdvisoryWarningFrame (status=advisory),
which confirm_gate and policy never consume.

This module is a one-way gate:
- practice_knowledge may import from diary.frames (to emit advisory frames).
- diary policy, confirm_gate, temporal, slot_search must never import from
  practice_knowledge (enforced by import-boundary tests).
"""

from __future__ import annotations

from datetime import date

from app.services.diary.frames import BernieAdvisoryWarningFrame
from app.services.practice_knowledge.envelopes import PracticeKnowledgeResult


def to_advisory_frame(
    result: PracticeKnowledgeResult,
    *,
    reference_date: date,
    reason_code: str = "practice_knowledge_advisory",
) -> BernieAdvisoryWarningFrame:
    """Convert a PracticeKnowledgeResult into a BernieAdvisoryWarningFrame.

    The frame status is always 'advisory'. confirm_gate and policy.py read
    guardrail/slot/roster frames; they never read advisory_warning frames,
    so this result cannot affect confirm-affordance or hard blocks.

    Asserts the structural advisory-only invariants on the result before
    producing the frame so any retriever that corrupts these flags is caught
    at the boundary.
    """
    assert result.advisory_only is True, "PracticeKnowledgeResult.advisory_only must be True"
    assert result.cannot_affect_slots is True, "PracticeKnowledgeResult.cannot_affect_slots must be True"
    assert result.cannot_affect_policy is True, "PracticeKnowledgeResult.cannot_affect_policy must be True"
    assert result.cannot_affect_confirm is True, "PracticeKnowledgeResult.cannot_affect_confirm must be True"

    fact_snapshots = [
        {
            "fact_id": item.fact.fact_id,
            "kind": item.fact.kind.value,
            "subject": item.fact.subject,
            "body": item.fact.body,
            "match_basis": item.match_basis,
            "rank": item.rank,
            "provenance": {
                "source_kind": item.provenance.source_kind.value,
                "source_ref": item.provenance.source_ref,
                "author": item.provenance.author,
                "review_status": item.provenance.review_status.value,
            },
        }
        for item in result.items
    ]

    return BernieAdvisoryWarningFrame(
        status="advisory",
        source="server_resolver",
        basis="practice_knowledge_retrieval",
        reference_date=reference_date,
        reason_code=reason_code,
        payload={
            "schema_version": result.schema_version,
            "retrieval_basis": result.retrieval_basis,
            "staff_copy": result.staff_copy,
            "fact_snapshots": fact_snapshots,
            "advisory_only": True,
            "cannot_affect_slots": True,
            "cannot_affect_policy": True,
            "cannot_affect_confirm": True,
        },
    )


__all__ = ["to_advisory_frame"]

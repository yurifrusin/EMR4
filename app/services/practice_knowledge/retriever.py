"""Practice-knowledge retriever Protocol and deterministic in-memory implementation.

The Protocol seam allows a future GraphRAGRetriever to replace InMemoryPracticeKnowledgeRetriever
without touching call sites. The in-memory implementation uses deterministic
kind/subject/keyword filtering with a stable sort - no wall-clock, no network, no LLM.

Rank priority (lower = higher priority):
  1. Subject exact match
  2. Kind filter match
  3. Keyword hit in body or subject
  4. fact_id lexicographic (stable tiebreaker)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.services.practice_knowledge.envelopes import (
    PracticeKnowledgeQuery,
    PracticeKnowledgeResult,
    PracticeKnowledgeResultItem,
)
from app.services.practice_knowledge.facts import PracticeFact


@runtime_checkable
class PracticeKnowledgeRetriever(Protocol):
    """Retrieve advisory practice-knowledge facts for a query.

    Implementations must return a PracticeKnowledgeResult whose advisory_only
    and cannot_affect_* invariants are always True. A future GraphRAGRetriever
    implementing this Protocol can drop in without changing call sites.
    """

    def retrieve(self, query: PracticeKnowledgeQuery) -> PracticeKnowledgeResult:
        ...


class InMemoryPracticeKnowledgeRetriever:
    """Deterministic retriever over a typed in-memory fact list.

    Filtering: kind filter (if specified), then keyword match against fact
    subject + body. Ranking: subject-exact > kind-match > keyword-hit > fact_id.
    Capped at query.max_results. No randomness, no network, no LLM.
    """

    def __init__(self, facts: list[PracticeFact]) -> None:
        self._facts = list(facts)

    def retrieve(self, query: PracticeKnowledgeQuery) -> PracticeKnowledgeResult:
        candidates = self._filter(query)
        ranked = self._rank(candidates, query)
        capped = ranked[: query.max_results]
        items = [
            PracticeKnowledgeResultItem(
                fact=fact,
                match_basis=basis,
                rank=idx + 1,
                score=max(0.0, 1.0 - idx * 0.1),
                provenance=fact.provenance,
            )
            for idx, (fact, basis) in enumerate(capped)
        ]
        return PracticeKnowledgeResult(
            items=items,
            retrieval_basis="deterministic_in_memory",
            staff_copy=self._build_staff_copy(items),
        )

    def _filter(self, query: PracticeKnowledgeQuery) -> list[PracticeFact]:
        results = []
        keywords = [w.lower() for w in query.query_text.split() if len(w) > 2]
        for fact in self._facts:
            if query.kinds and fact.kind not in query.kinds:
                continue
            searchable = (fact.subject + " " + fact.body).lower()
            if not keywords or any(kw in searchable for kw in keywords):
                results.append(fact)
        return results

    def _rank(
        self, facts: list[PracticeFact], query: PracticeKnowledgeQuery
    ) -> list[tuple[PracticeFact, str]]:
        keywords = [w.lower() for w in query.query_text.split() if len(w) > 2]
        hints_lower = [h.lower() for h in query.subject_hints]

        def sort_key(fact: PracticeFact) -> tuple[int, int, int, str]:
            subject_lower = fact.subject.lower()
            body_lower = fact.body.lower()
            subject_exact = 0 if (hints_lower and any(h in subject_lower for h in hints_lower)) else 1
            kind_match = 0 if (query.kinds and fact.kind in query.kinds) else 1
            keyword_hit = 0 if (keywords and any(kw in subject_lower or kw in body_lower for kw in keywords)) else 1
            return (subject_exact, kind_match, keyword_hit, fact.fact_id)

        def match_basis(fact: PracticeFact) -> str:
            subject_lower = fact.subject.lower()
            body_lower = fact.body.lower()
            if hints_lower and any(h in subject_lower for h in hints_lower):
                return "subject_exact"
            if keywords and any(kw in subject_lower for kw in keywords):
                return "subject_keyword"
            if keywords and any(kw in body_lower for kw in keywords):
                return "body_keyword"
            if query.kinds and fact.kind in query.kinds:
                return "kind_match"
            return "kind_filter_pass"

        sorted_facts = sorted(facts, key=sort_key)
        return [(f, match_basis(f)) for f in sorted_facts]

    @staticmethod
    def _build_staff_copy(items: list[PracticeKnowledgeResultItem]) -> str:
        if not items:
            return ""
        lines = [f"[{item.fact.kind.value}] {item.fact.subject}: {item.fact.body}" for item in items]
        return "\n".join(lines)


__all__ = [
    "InMemoryPracticeKnowledgeRetriever",
    "PracticeKnowledgeRetriever",
]

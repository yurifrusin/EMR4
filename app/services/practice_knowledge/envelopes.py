"""Practice-knowledge query and result envelopes.

All envelopes carry structural advisory-only invariants as Literal True fields
so any attempt to use them for slot availability, policy hard blocks, or
confirm-affordance decisions will fail to type-check or assert at runtime.

Pure contract code: no DB, no network, no wall-clock.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.practice_knowledge.facts import PracticeFact, PracticeFactKind, PracticeFactProvenance


class PracticeKnowledgeQuery(BaseModel):
    """A query into the practice-knowledge substrate.

    advisory_only and contains_phi are structural invariants validated on
    construction - a query that attempts to set them otherwise is rejected.
    """

    model_config = ConfigDict(extra="forbid")

    query_text: str = Field(..., min_length=1)
    kinds: Optional[list[PracticeFactKind]] = None
    subject_hints: list[str] = Field(default_factory=list)
    max_results: int = Field(default=5, ge=1, le=20)
    requires_provenance: bool = True
    advisory_only: Literal[True] = True
    contains_phi: Literal[False] = False

    @model_validator(mode="after")
    def _enforce_invariants(self) -> "PracticeKnowledgeQuery":
        if self.advisory_only is not True:
            raise ValueError("PracticeKnowledgeQuery.advisory_only must always be True")
        if self.contains_phi is not False:
            raise ValueError("PracticeKnowledgeQuery.contains_phi must always be False")
        return self


class PracticeKnowledgeResultItem(BaseModel):
    """A single matched fact within a retrieval result."""

    model_config = ConfigDict(extra="forbid")

    fact: PracticeFact
    match_basis: str
    rank: int = Field(..., ge=1)
    score: float = Field(..., ge=0.0, le=1.0)
    provenance: PracticeFactProvenance


class PracticeKnowledgeResult(BaseModel):
    """Advisory-only retrieval result envelope.

    The three cannot_affect_* Literal True fields are structural declarations:
    any downstream code path that attempts to route these results into slot
    availability, policy decisions, or confirm-affordance gates will fail at
    the type boundary. They are also asserted at runtime in boundary.py.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["practice.knowledge.result.v1"] = "practice.knowledge.result.v1"
    advisory_only: Literal[True] = True
    cannot_affect_slots: Literal[True] = True
    cannot_affect_policy: Literal[True] = True
    cannot_affect_confirm: Literal[True] = True
    items: list[PracticeKnowledgeResultItem] = Field(default_factory=list)
    retrieval_basis: str = "deterministic_in_memory"
    staff_copy: str = ""


__all__ = [
    "PracticeKnowledgeQuery",
    "PracticeKnowledgeResult",
    "PracticeKnowledgeResultItem",
]

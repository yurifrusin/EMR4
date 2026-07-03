"""Typed practice-knowledge fact models.

Pure domain contract: no DB, no network, no wall-clock. Each PracticeFact
carries full provenance so consumers can cite source, author, and effective
dates without making LLM guesses.

Authority tier is fixed to 'advisory' - practice-knowledge facts are NEVER
authoritative for slot availability, reception policy hard blocks, or the
confirm-affordance gate.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PracticeFactKind(str, Enum):
    roster = "roster"
    policy = "policy"
    contact = "contact"
    opening_hours = "opening_hours"
    reception_guidance = "reception_guidance"


class PracticeFactSourceKind(str, Enum):
    staff_authored = "staff_authored"
    config = "config"
    imported_doc = "imported_doc"


class ReviewStatus(str, Enum):
    current = "current"
    needs_review = "needs_review"
    superseded = "superseded"


class PracticeFactProvenance(BaseModel):
    """Source, authorship, and validity metadata for a single fact."""

    model_config = ConfigDict(extra="forbid")

    source_kind: PracticeFactSourceKind
    source_ref: str
    author: str
    captured_at: datetime
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    last_reviewed: Optional[date] = None
    review_status: ReviewStatus = ReviewStatus.current


class PracticeFact(BaseModel):
    """A single typed, provenance-bearing practice-knowledge fact.

    authority_tier is always 'advisory' - structural enforcement of the
    advisory-only invariant. contains_phi must always be False; PHI belongs
    in the clinical record, not the practice-knowledge substrate.
    """

    model_config = ConfigDict(extra="forbid")

    fact_id: str = Field(..., min_length=1)
    kind: PracticeFactKind
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    authority_tier: Literal["advisory"] = "advisory"
    provenance: PracticeFactProvenance
    contains_phi: Literal[False] = False

    @model_validator(mode="after")
    def _enforce_no_phi(self) -> "PracticeFact":
        if self.contains_phi is not False:
            raise ValueError("PracticeFact.contains_phi must always be False")
        return self


__all__ = [
    "PracticeFact",
    "PracticeFactKind",
    "PracticeFactProvenance",
    "PracticeFactSourceKind",
    "ReviewStatus",
]

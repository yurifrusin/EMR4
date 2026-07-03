"""Practice-knowledge substrate: typed advisory facts, deterministic retrieval,
and a boundary adapter that emits only BernieAdvisoryWarningFrames.

Import boundary rule: this package may import from app.services.diary.frames
(to emit advisory frames). The diary policy, confirm_gate, temporal, slot_search,
envelopes, and write paths must NEVER import from this package.
"""

from app.services.practice_knowledge.boundary import to_advisory_frame
from app.services.practice_knowledge.envelopes import (
    PracticeKnowledgeQuery,
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
from app.services.practice_knowledge.retriever import (
    InMemoryPracticeKnowledgeRetriever,
    PracticeKnowledgeRetriever,
)

__all__ = [
    "InMemoryPracticeKnowledgeRetriever",
    "PracticeFact",
    "PracticeFactKind",
    "PracticeFactProvenance",
    "PracticeFactSourceKind",
    "PracticeKnowledgeQuery",
    "PracticeKnowledgeResult",
    "PracticeKnowledgeResultItem",
    "PracticeKnowledgeRetriever",
    "ReviewStatus",
    "to_advisory_frame",
]

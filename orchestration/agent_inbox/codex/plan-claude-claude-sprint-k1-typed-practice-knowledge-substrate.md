# plan-claude-claude-sprint-k1-typed-practice-knowledge-substrate

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-k1-typed-practice-knowledge-substrate` |
| Status | integrated |
| Created | 2026-07-03 21:08 +1000 |
| Source HEAD | `416fcc5` |

## Plan Summary

Design a bounded, pure-contract typed practice-knowledge substrate (roster/policy/contact/opening-hours/reception-guidance facts) with provenance, a deterministic in-memory retriever behind a Protocol seam for future GraphRAG, and a retrieval-result envelope that can only ever surface as a Bernie advisory frame - never touching slot availability, reception policy hard blocks, or the confirm-affordance gate. Plan-only; no production code this turn.

## My Understanding

Sprint K1 wants the first slice of a practice-knowledge substrate so Bernie can EXPLAIN reception facts (for example: Dr Shera does not work Fridays; new-patient long appointments are 30 min; clinic phone and opening hours; reception guidance) using typed, provenance-bearing facts rather than free text or LLM guesses. Bernie is the verification target because the practice-facts domain is small enough to assert the correct answer in tests. The hard constraint carried from Sprints N1-N3 is that deterministic diary state stays authoritative: retrieval is ADVISORY-ONLY. It must not become a slot-availability source, must not relax or create reception-policy hard blocks, and must not influence the backend-owned confirm-affordance gate (evaluate_confirm_affordance in app/services/diary/confirm_gate.py reads only policy + staleness + has_staged_proposal). The existing diary domain already models this separation cleanly: advisory content flows through BernieAdvisoryWarningFrame (frame_type advisory_warning, status advisory) in app/services/diary/frames.py, which confirm_gate and policy never consume. K1 reuses that seam. GraphRAG is explicitly future: build a typed store plus a deterministic retriever behind a Protocol so a vector/graph adapter can drop in later, but do NOT stand up any vector/graph/embedding store now. No PHI-bearing persisted chat/session tables, no route/turn wiring, no auto-mode.

## Intended Surface / Boundary

Backend domain contracts only, in a NEW bounded package app/services/practice_knowledge/ (kept separate from app/services/diary and app/services/bernie so it is independently reusable and clearly not part of diary write authority). Dependency direction is strictly one-way: the practice_knowledge boundary module imports BernieAdvisoryWarningFrame from app/services/diary/frames to emit advisory frames; nothing in diary policy, confirm_gate, temporal, or slot-search imports practice_knowledge. NO user-facing surface changes at all: the Diary grid, booking-slot cards, waiting-room panel, appointment status colours, and the confirm affordance / confirm button must not change in this sprint. No FastAPI routes, no schema wiring, no migrations, and no seeding of production data - dev/example facts live only in an in-package typed fixture used by tests.

## Out Of Scope

No implementation before the plan gate. No vector DB, embeddings, graph store, or GraphRAG deployment. No Scribe/Consultant clinical-corpus ingestion (that stays the separate app/services/ai/knowledge_base.py adapter lane). No route/turn/UI wiring of retrieval results into Bernie responses (contract-first, like N2). No changes to confirm_gate, policy, temporal, slot search, envelopes, or frames semantics - only a one-way import of the existing advisory frame type. No persisted sessions or PHI-bearing tables. No autonomous actions, no slot-availability authority from retrieval, no confirm-grade or hard-block decisions from retrieval. No auto-mode. No broad API review. No migration or alembic changes.

## Files I Expect To Edit

Plan-only this turn (no code edits). For the approved implementation the expected footprint is all-new files: app/services/practice_knowledge/__init__.py (curated exports); facts.py (PracticeFactKind enum limited to roster/policy/contact/opening_hours/reception_guidance; PracticeFact model; PracticeFactProvenance sub-model with source_kind, source_ref, author, captured_at, effective_from/to, last_reviewed, review_status; extra=forbid; contains_phi flag defaulting False and validated False); envelopes.py (PracticeKnowledgeQuery with advisory_only Literal True and contains_phi validated False; PracticeKnowledgeResultItem with matched fact snapshot, match_basis, and provenance; PracticeKnowledgeResult envelope with schema_version literal, advisory_only Literal True, and declarative non-authority invariants cannot_affect_slots / cannot_affect_policy / cannot_affect_confirm as Literal True); retriever.py (PracticeKnowledgeRetriever Protocol plus deterministic InMemoryPracticeKnowledgeRetriever doing kind/subject/keyword filtering and stable ranking, no wall-clock/network/LLM); boundary.py (to_advisory_frame(result) -> BernieAdvisoryWarningFrame, plus assertions of the advisory-only invariants); examples.py (typed dev-clinic example facts for tests/demo only). New tests: tests/test_practice_knowledge_facts.py, tests/test_practice_knowledge_retrieval.py, tests/test_practice_knowledge_advisory_boundary.py. Optionally a short design note docs/practice-knowledge-substrate.md describing the GraphRAG migration path. No edits to app/services/diary/*, app/services/bernie/*, routers, schemas, or migrations.

## Implementation Steps

1. facts.py: define PracticeFactKind (roster/policy/contact/opening_hours/reception_guidance only), PracticeFactProvenance (source_kind of staff_authored|config|imported_doc, source_ref, author, captured_at, effective_from/to, last_reviewed, review_status), and PracticeFact (fact_id, kind, subject key, body/value, tags, authority_tier advisory, provenance, contains_phi False validated). All pure pydantic with extra=forbid.
2. envelopes.py: PracticeKnowledgeQuery (query_text, kinds filter, subject hints, max_results, requires_provenance, advisory_only Literal True, contains_phi validated False); PracticeKnowledgeResultItem (fact snapshot, match_basis deterministic string, rank/score, provenance echoed); PracticeKnowledgeResult (schema_version practice.knowledge.result.v1, advisory_only Literal True, cannot_affect_slots/policy/confirm Literal True, items, retrieval_basis, neutral staff copy).
3. retriever.py: PracticeKnowledgeRetriever Protocol with retrieve(query) -> PracticeKnowledgeResult; InMemoryPracticeKnowledgeRetriever over a typed fact list using deterministic kind/subject/keyword matching plus stable sort (subject-exact, then kind-match, then keyword-hit, then fact_id) capped at max_results; document that a future GraphRAGRetriever implements the same Protocol.
4. boundary.py: to_advisory_frame(result) builds a BernieAdvisoryWarningFrame (existing advisory source such as server_resolver, status advisory) carrying fact snapshots and provenance in payload and nothing that policy or confirm_gate read; assert the result advisory_only and non-authority flags are True.
5. examples.py: a handful of typed dev-clinic facts (Dr Shera Friday-off as a policy/roster note, new-patient duration guidance, clinic phone/opening hours, a reception-guidance line) used only by tests.
6. Tests: (a) facts/provenance validation including PHI rejection; (b) deterministic retrieval - same query yields the same ranked facts, kind/subject filtering correct, known-answer assertions on the small example set; (c) advisory-boundary tests - to_advisory_frame yields only an advisory frame; a PracticeKnowledgeResult cannot construct or alter a ConfirmAffordanceDecision or BernieReceptionPolicyDecision, and evaluate_confirm_affordance/policy signatures take no knowledge input; an import-boundary test asserting confirm_gate.py and policy.py do not import practice_knowledge.
7. Optional design note documenting the GraphRAG migration seam.
8. Verification: run new plus existing bernie/diary domain tests, python -m compileall app, git diff --check.

## Visual / Behavioural Acceptance Checks

No visual/UI change is expected or allowed this sprint - the Diary grid, booking-slot cards, waiting-room panel, status colours, and the confirm button / confirm affordance must render and behave exactly as before (verified by the absence of any docs/, app/routers, or schema diff). Behavioural checks are backend-only: (1) InMemoryPracticeKnowledgeRetriever returns deterministic, provenance-bearing facts for known queries over the example set (known-answer assertions). (2) PracticeKnowledgeResult always carries advisory_only True and cannot_affect_slots/policy/confirm True; a query with contains_phi True is rejected. (3) to_advisory_frame produces only a BernieAdvisoryWarningFrame; there is no code path from a retrieval result into evaluate_confirm_affordance, reception policy hard blocks, or slot availability. (4) An import-boundary test confirms diary confirm_gate, policy, temporal, and slot-search do not depend on practice_knowledge. (5) pytest for new plus existing bernie/diary domain tests all green; python -m compileall app clean; git diff --check clean.

## Risks / Ambiguities

1. Package placement: app/services/practice_knowledge/ versus folding into app/services/diary/knowledge/. I recommend a separate top-level package for clean advisory separation and future Scribe/Consultant reuse, but will defer to Codex if diary-local is preferred.
2. Advisory frame source enum: BernieFrameSource is a fixed Literal; a knowledge advisory may want a practice_knowledge source value, but adding one edits frames.py (a diary contract). I will reuse an existing source (server_resolver) instead and flag the naming question for a later sprint rather than widen scope now.
3. Scope temptation: wiring retrieval into the Bernie turn/route so staff actually see explanations is deferred; K1 stops at contracts, retriever, boundary, and tests (like N2 stopped at contract-first).
4. Overlap with app/services/ai/knowledge_base.py (licensed clinical evidence for Scribe/Consultant) versus this internal reception-operations substrate - keep the two distinct lanes.
5. The GraphRAG seam is a Protocol only; no store is built, so retrieval is deterministic substring/kind matching - adequate for the known-answer Bernie domain but explicitly not semantic, and documented as such.
6. The core safety property is that advisory-only is enforced structurally (Literal flags, one-way imports, and a boundary function that returns only an advisory frame) rather than by convention - this is the main thing for Codex to scrutinise.

## Codex Plan Review

- Review result: Accepted by Ariadne. Use a separate
  `app/services/practice_knowledge/` package for the advisory substrate, with a
  deterministic in-memory retriever behind a protocol seam and no route/UI
  wiring in K1.
- Required changes before implementation: keep retrieval structurally
  advisory-only; do not import practice knowledge from diary policy,
  confirm_gate, temporal, slot search, envelopes, or write paths. Add
  adversarial tests proving retrieved facts cannot create no-slot truth,
  roster truth, confirm authority, freshness/audit evidence, or write payloads.
  Prefer adding a dedicated `practice_knowledge` frame source only if typed
  tests prove it is restricted to advisory frames.
- Approved to proceed: yes, release with `complete sprint task`.

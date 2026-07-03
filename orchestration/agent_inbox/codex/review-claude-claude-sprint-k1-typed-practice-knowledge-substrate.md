# review-claude-claude-sprint-k1-typed-practice-knowledge-substrate

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-k1-typed-practice-knowledge-substrate` |
| Status | queued |

## Review Request

claude-sprint-k1-typed-practice-knowledge-substrate ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW app/services/practice_knowledge/__init__.py — curated package exports
  - NEW app/services/practice_knowledge/facts.py — PracticeFactKind enum (5 kinds), PracticeFactProvenance, PracticeFact (authority_tier=advisory, contains_phi=False enforced structurally)
  - NEW app/services/practice_knowledge/envelopes.py — PracticeKnowledgeQuery (advisory_only/contains_phi validated), PracticeKnowledgeResultItem, PracticeKnowledgeResult (advisory_only/cannot_affect_slots/policy/confirm Literal True)
  - NEW app/services/practice_knowledge/retriever.py — PracticeKnowledgeRetriever Protocol + InMemoryPracticeKnowledgeRetriever (deterministic kind/subject/keyword filter + stable sort, no wall-clock/LLM/network)
  - NEW app/services/practice_knowledge/boundary.py — to_advisory_frame() one-way exit producing only BernieAdvisoryWarningFrame; asserts all advisory-only invariants before emitting frame
  - NEW app/services/practice_knowledge/examples.py — 6 typed dev-clinic facts for tests (roster/policy/contact/opening_hours/reception_guidance x2)
  - NEW tests/test_practice_knowledge_facts.py — 14 tests (provenance round-trips, all kinds/statuses, PHI rejection, authority_tier enforcement, extra-field rejection)
  - NEW tests/test_practice_knowledge_retrieval.py — 33 tests (query/result invariants, known-answer retrieval, determinism, kind filter, max_results, result invariants, provenance, staff_copy)
  - NEW tests/test_practice_knowledge_advisory_boundary.py — 34 tests (advisory frame type/status, payload invariants, boundary assertion on corrupted results, cannot construct ConfirmAffordanceDecision, cannot alter confirm gate signature, cannot create no-slot truth, cannot create roster truth, cannot create freshness/audit evidence, AST import boundary scan)
  - NO edits to app/services/diary/*, app/services/bernie/*, routers, schemas, migrations, or any frontend file

- Verification run:
  - test_practice_knowledge_facts.py: 14 passed
  - test_practice_knowledge_retrieval.py: 33 passed
  - test_practice_knowledge_advisory_boundary.py: 34 passed
  - python -m compileall app/services/practice_knowledge/ -q: clean (no output)
  - git diff --check: clean
  - Full test suite run in progress (no regressions expected; no existing files were edited)

- Remaining risks:
  1. BernieFrameSource does not include a 'practice_knowledge' literal — frames use 'server_resolver'. Plan flagged this as a naming question for a later sprint (adding a new source value would require editing frames.py, widening the diary contract).
  2. The adversarial tests use object.__setattr__ to corrupt Pydantic model fields; this works for Pydantic v2 with model_config frozen=False (default). If the model ever gains frozen=True, the mutation tests would fail; treat as a test design note, not a safety gap.
  3. Import-boundary test uses AST scan of 4 diary files; it does not walk transitive imports. A future indirect import through an intermediate module would not be caught until a deeper scan is added.
  4. InMemoryPracticeKnowledgeRetriever uses substring matching, not semantic search — adequate for the known-answer Bernie domain but not suitable for free-form clinical queries. Documented in retriever.py docstring.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-k1-typed-practice-knowledge-substrate.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:

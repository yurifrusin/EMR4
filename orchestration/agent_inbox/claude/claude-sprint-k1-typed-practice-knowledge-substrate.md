# claude-sprint-k1-typed-practice-knowledge-substrate

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 944883f |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-k1-typed-practice-knowledge-substrate --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-k1-typed-practice-knowledge-substrate --commit-message "Sprint K1 typed practice knowledge substrate" --message "claude-sprint-k1-typed-practice-knowledge-substrate ready for Codex review"` |

## Mission

Plan Sprint K1 backend/domain work for a typed practice knowledge substrate and advisory-only retrieval boundary. Bernie is the first verification target because the practice-facts domain is small enough to know the right answer; Scribe/Consultant GraphRAG-like retrieval remains future.

## Scope

### In Scope

Plan only first. app/services/diary or a new bounded practice knowledge package, typed practice facts for roster/policy/contact/opening-hours/reception guidance, provenance/source fields, retrieval result envelopes, advisory-only boundary tests, and a migration path toward future GraphRAG without building a vector/graph store yet unless the plan strongly justifies it.

### Out of Scope

No implementation before plan gate, no autonomous actions, no slot availability authority from retrieval, no confirm-grade decisions from retrieval, no PHI-bearing persisted chat/session tables, no production GraphRAG deployment, no Scribe/Consultant corpus ingestion, no broad API review.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Plan packet first. Later implementation should run focused backend domain tests proving retrieval facts are advisory-only and cannot affect slot availability, reception policy hard blocks, or confirm affordance; compileall; git diff --check.

## Merge Criteria

A concrete plan for typed practice facts/retrieval envelopes that can support Bernie reception explanations while keeping deterministic diary state authoritative and retrieval advisory-only.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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

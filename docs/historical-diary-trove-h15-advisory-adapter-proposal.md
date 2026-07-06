# Historical Diary Trove H15 Advisory Adapter Proposal

Date: 2026-07-06
Sprint: H32 advisory-only adapter proposal
Status: test-only adapter; no runtime wiring

## Purpose

H32 proves the safest next boundary: H15 read-only candidates can be represented
as advisory-only practice-knowledge results in tests, then passed through the
existing `to_advisory_frame` boundary.

This is not RAG, GraphRAG, Access AI provider integration, Bernie runtime
memory, route wiring, UI wiring, or database persistence.

## Boundary

Allowed in H32:

- test-only adapter in `tests/h15_advisory_adapter.py`;
- hand-authored synthetic fixture input only;
- `PracticeKnowledgeResult` with advisory-only invariants;
- `BernieAdvisoryWarningFrame` output through the existing boundary.

Still blocked:

- raw diary files;
- ignored local generated JSON;
- broad full-trove processing;
- provider calls;
- Access AI runtime invocation;
- RAG or GraphRAG;
- session memory;
- slot/search/roster/policy/confirm/write authority.

## Result

The adapter emits only advisory facts with `contains_phi=false` and
`authority_tier=advisory`. The resulting Bernie frame has:

- `status=advisory`;
- `cannot_affect_slots=true`;
- `cannot_affect_policy=true`;
- `cannot_affect_confirm=true`;
- no slot candidates;
- no confirm-grade fields;
- no write payload.

## Next Step

The next safe implementation step is route-level read-only explanation testing
that proves these advisory frames can be displayed or reasoned about without
provider calls, memory persistence, database writes, or confirmation authority.

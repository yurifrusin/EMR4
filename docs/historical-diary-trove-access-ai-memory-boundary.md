# Historical Diary Trove Access AI and Memory Boundary

Date: 2026-07-06
Sprint: H31 Access-AI/read-only memory boundary review
Status: boundary review only; no RAG, GraphRAG, runtime memory, provider, route,
UI, or database integration added

## Current Position

The H15/H29/H30 artifacts may inform deterministic read-only explanation tests,
but they are not runtime memory.

Allowed now:

- hand-authored synthetic fixtures under `tests/fixtures/h15_semantic_candidates/`;
- deterministic replay tests that prove those fixtures route as read-only
  `explain_schedule`;
- source-safe docs that describe aggregate counts and candidate-shape outcomes.

Still blocked:

- broad full-trove mining;
- provider-visible prompts over raw, extracted, or generated local payloads;
- RAG or GraphRAG over historical diary outputs;
- Bernie prompt memory or session memory sourced from historical diary outputs;
- route/UI/database integration;
- any write, confirmation, slot-search, roster, policy, freshness, or audit
  authority derived from historical diary candidates.

## Access AI Boundary

Any future historical-diary knowledge route must sit behind Access AI and must
preserve these constraints:

- `contains_phi` must remain `false` for any approved historical-diary query.
- Retrieved text storage must remain `transient_only`.
- Audit metadata may contain only source-safe IDs and counts, not raw text,
  filenames, exact source timestamps, patient labels, staff labels, or generated
  local payload content.
- Provider calls are prohibited for raw diary files, extracted text, ignored
  local JSON, or local candidate payloads unless a separate reviewed gate exists.
- Access AI authorization is necessary but not sufficient; H15/H22/H23/H28
  historical-diary gates still apply.

## Advisory Boundary

If historical-diary candidates ever become practice-knowledge-like facts, they
must exit through the same advisory-only shape as existing practice knowledge:

- advisory frame only;
- cannot affect slots;
- cannot affect policy;
- cannot affect confirmation;
- cannot create roster truth;
- cannot create no-slot truth;
- cannot create freshness, signed evidence, or audit evidence;
- cannot create write payloads.

The deterministic diary backend remains authoritative for availability,
collisions, signed evidence, route permissions, confirmation envelopes, and
mutations.

## Next Safe Work

The next safe implementation work is not RAG/GraphRAG. Prefer either:

1. route-level read-only explanation tests that consume the synthetic H15
   candidate fixture and prove no DB/provider/write changes; or
2. a small adapter proposal that maps synthetic historical candidates into an
   advisory-only frame, with static import-boundary tests first.

Do not connect historical diary candidates to runtime Bernie memory or Access AI
providers until that separate boundary is implemented and reviewed.

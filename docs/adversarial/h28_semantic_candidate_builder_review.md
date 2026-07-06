# H28 Semantic Candidate Builder Adversarial Review

Date: 2026-07-06
Scope: H27 candidate builder and bounded local H15 prototype result
Privacy posture: source-safe review only. No raw diary files, ignored generated
JSON, extracted text, filenames, exact source timestamps, patient labels, staff
labels, provider calls, route/UI changes, database writes, RAG, GraphRAG, or
memory integration reviewed or committed.

## Verdict

H27 proved the approved H15 pipeline can run safely, but its first candidate
mapping was too assertive: `status_change` is a mutating diary action and should
not be inferred from neutral structural aggregate evidence, even with
`low` confidence and `unknown` status categories.

H28 fixes this by making the builder emit only read-only `explain_schedule`
candidates. This keeps the prototype useful for deterministic grammar/fixture
shape without implying appointment truth or write-intent.

## Risk Found

Neutral aggregates can show stable grid shape, time-token density, and count
movement. They cannot by themselves prove:

- appointment status changes;
- booking creation;
- cancellation;
- movement/resizing;
- patient arrival;
- waiting-room movement;
- any mutating backend action.

Mapping every snapshot to `status_change` would create a subtle semantic bridge
from layout structure into mutating diary action vocabulary.

## Mitigation

The candidate builder now emits:

```text
action_name = explain_schedule
transition_label = candidate_explain_schedule
confidence_label = low
status_categories = unknown
```

This is still not an appointment fact. It is a read-only grammar candidate that
can be useful for later deterministic explanation fixtures.

## Required Before Promotion

Before any generated candidate shape becomes a committed semantic fixture:

- keep generated local candidate JSON ignored;
- hand-author any committed fixture from the reviewed shape rather than copying
  local derived payloads wholesale;
- keep mutating verbs out unless a future reviewed semantic method can justify
  them without raw text, identifiers, or provider interpretation;
- keep backend write authority in the existing confirmation envelope only;
- run H15 gate validation, semantic fixture validation, leakage lint, and the
  focused H-series/replay tests.

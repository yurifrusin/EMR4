# Historical Diary Trove H15 Bounded Semantic Prototype

Date: 2026-07-06
Sprint: H27 bounded semantic prototype
Approval: `docs/historical-diary-trove-h15-approved-gate.json`
Privacy posture: local-only raw processing; committed summary only. Raw diary
files, ignored aggregate JSON, generated candidate JSON, extracted document
text, filenames, exact source timestamps, patient labels, staff labels,
provider-visible prompts, route/UI changes, database writes, RAG, GraphRAG, and
memory integration remain out of scope.

## Local Run

The approved prototype used one local root, one dense day, and a maximum of 80
samples, without `-AllowLargeRun`:

```text
.\scripts\historical_diary_structure_classifier.ps1
-Root @('local_data\historical-diary-trove\raw\pilot_01')
-Output local_data\historical-diary-trove\inventory\semantic_h15_prototype_neutral_aggregate.json
-SampleSize 80
-MaxSampleSize 80
-DenseDays 1
-IncludeOrderedSnapshots
```

The generated semantic candidate payload was written to ignored local storage:

```text
local_data\historical-diary-trove\inventory\semantic_h15_candidate_fixtures.json
```

No generated local payload is committed.

## Source-Safe Result

- Root label: `pilot_01`.
- Requested sample size: 80.
- Opened count: 80.
- Error count: 0.
- Structure class distribution: 80 `strong_diary_grid`.
- Time-token count range: 78 to 79.
- Date-token count range: 13 to 15.
- Candidate fixture count: 80.
- Candidate action names: `status_change`.
- Candidate confidence labels: `low`.
- Candidate status categories: `unknown`.

Interpretation: the prototype proves the approved H15 pipeline can transform
validator-safe neutral aggregates into validator-safe semantic candidate
fixtures. It does not prove appointment status, patient attendance, booking
creation, cancellation, movement, or clinical meaning.

## Validation

The neutral aggregate passed the H5 output-safety validator:

```text
.venv\Scripts\python.exe scripts\historical_diary_output_safety.py local_data\historical-diary-trove\inventory\semantic_h15_prototype_neutral_aggregate.json
```

The candidate payload passed the semantic fixture validator through
`scripts\historical_diary_semantic_candidate_builder.py`.

The generated local payloads remain ignored under `local_data`.

## Next Boundary

The next safe sprint should decide whether to:

1. keep the candidate payload ignored and add a synthetic committed fixture
   family that mirrors this shape without local-derived counts; or
2. run an adversarial review of the candidate-builder semantics before any
   committed semantic fixture promotion.

Do not run a broad full-trove pass or connect the candidates to Bernie memory,
RAG, GraphRAG, routes, UI, or writes without a separate reviewed gate.

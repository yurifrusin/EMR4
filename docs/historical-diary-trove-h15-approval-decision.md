# Historical Diary Trove H15 Approval Decision

Date: 2026-07-06
Decision: approved for bounded semantic fixture promotion
Reviewer: Yuri
Expiry: 2027-01-01

## Approved Payload

```text
docs/historical-diary-trove-h15-approved-gate.json
```

The earlier draft remains as an audit artifact:

```text
docs/historical-diary-trove-h15-approval-payload-draft.json
```

## Scope

This approval permits only the drafted H15 scope:

- local raw processing only;
- no raw or extracted diary content sent to external providers;
- no committed raw text, redacted text, filenames, exact source timestamps,
  patient labels, staff labels, or identifying labels;
- one tiny local-only prototype slice;
- at most one root and one dense day;
- at most 80 samples;
- `action_grammar_candidates` fixture family only;
- relative day indexes;
- synthetic resource IDs;
- bucket flags and coarse confidence labels;
- no memory, RAG, GraphRAG, provider prompts, route wiring, UI changes,
  autonomous writes, or full-trove pass.

## Next Sprint Boundary

The next sprint may run or design the tiny local-only semantic prototype within
this scope. It must still fail closed if the H15 gate validator, semantic
fixture validator, leakage lint, or output-safety checks fail.

This approval does not authorize broad full-trove mining.

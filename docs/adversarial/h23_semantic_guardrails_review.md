# H23 Semantic Guardrails Adversarial Review

Date: 2026-07-06
Scope: `scripts/historical_diary_output_safety.py`,
`scripts/historical_diary_leakage_lint.py`, synthetic tests, and the Python
Security workflow hook.
Privacy posture: source-safe review only; no raw diary files, ignored
inventory JSON, extracted text, filenames, exact source timestamps, patient
labels, staff labels, provider calls, or semantic fixtures reviewed.

## Verdict

The H23 guardrails are useful and should remain in the sprint path before any
H15 approval. They add two missing tripwires:

- semantic-mode payload validation beside the neutral H5 validator;
- source/doc/test leakage lint for H-series semantic drift.

H15 remains closed. These guardrails do not approve semantic fixture promotion
and do not make full-trove processing safe by themselves.

## Issues Reviewed

### Action Grammar Drift

Risk: the semantic validator could silently allow an action name that is not in
the R29 grammar, or miss a new grammar verb later.

Mitigation added in review:

```text
tests/test_historical_diary_output_safety.py::test_semantic_action_allowlist_tracks_diary_action_grammar
```

This ties the semantic validator allowlist to `DiaryActionVerb`.

### Expiry As Free Text

Risk: H22 required approval expiry/review interval, but the first validator pass
accepted any non-empty value.

Mitigation added in review: `approval_expires_on` must now match `YYYY-MM-DD`,
with a synthetic rejection test.

### Policy-Doc Exemption

Risk: the leakage lint intentionally exempts policy/adversarial historical docs
and negative-test files, because those files need to quote forbidden examples.
This means lint is a tripwire, not a substitute for human review of the H15
approval packet.

Accepted boundary: production-ish fixtures/tests and non-policy docs are linted;
policy/adversarial docs remain review artifacts and must be read by Ariadne or
Yuri when approval scope changes.

### H15 Gate Status

The committed H15 template remains `blocked`. No semantic output payload, draft
approval JSON, raw slice, GraphRAG memory, RAG corpus, route wiring, provider
call, or Bernie prompt use was added.

## Required Before H15 Approval

- A concrete reviewed approval payload with bounded scope.
- Passing H15 gate validation on that payload.
- Passing semantic fixture output validation on any candidate output.
- Passing leakage lint over relevant repo paths.
- Human review of policy/adversarial docs because the lint intentionally allows
  those files to discuss forbidden patterns.
- Separate approval before any full-trove mining or memory integration.

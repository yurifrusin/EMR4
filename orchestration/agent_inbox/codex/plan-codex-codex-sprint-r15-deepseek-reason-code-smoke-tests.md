# plan-codex-codex-sprint-r15-deepseek-reason-code-smoke-tests

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r15-deepseek-reason-code-smoke-tests` |
| Source Task | `codex-sprint-r15-deepseek-reason-code-smoke-tests` |
| Status | integrated |
| Created | 2026-07-05 20:25 +1000 |
| Source HEAD | `57d834d` |

## Plan Summary

Sprint R15 reason-code smoke tests

## My Understanding

Sprint R15 implements: (1) hide PATIENT_UNWELL from selectable dropdown, (2) contextual option filtering for cancel/delete vs retrospective status flows, (3) preserve backend compatibility. Existing tests already verify LEGACY_UNCLASSIFIED exclusion, empty default, privacy warning. Sprint R15 smoke tests must add PATIENT_UNWELL and contextual filtering coverage without duplication.

## Intended Surface / Boundary

review/test_diary_smoke.py only. Touch no production code. Adjacent surfaces that must not change: diary grid, booking modal layout, flow panel, audit history, Bernie panel, slot previews, drag/resize, all status proposal/confirm flows, Bernie tool-intent/reception-policy tests.

## Out Of Scope

No backend, schema, migration, diary.js/html/css production edits. No changes to checks_diary.json or harness.py. No production code lanes.

## Files I Expect To Edit

review/test_diary_smoke.py

## Implementation Steps

1. Read existing reason-code tests and taxonomy docs 2. Write test_reason_code_patient_unwell_hidden_from_dropdown 3. Write test_reason_code_contextual_filtering 4. Run focused pytest -k reason_code 5. Run full smoke suite to confirm no regressions 6. Submit

## Visual / Behavioural Acceptance Checks

PATIENT_UNWELL absent from dropdown. LEGACY_UNCLASSIFIED remains hidden. Cancel-flow options differ from status-housekeeping options. Empty default preserved. Privacy warning and maxlength enforced. All existing smoke tests pass.

## Risks / Ambiguities

Contextual filtering meaning ambiguous (cancel vs edit modal or first-party vs backend). DOM structure may change if separate selects per flow. Unrelated Bernie/audit failures could mask reason-code regressions.

## Codex Plan Review

- Review result: Accepted after clarifying future-vs-retrospective semantics.
- Required changes before implementation: Use deterministic date setup so tests do not depend on the current clock.
- Approved to proceed: yes

# plan-codex-codex-sprint-r11-deepseek-reason-code-adversarial-tests

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r11-reason-code-adversarial-tests` |
| Source Task | `codex-sprint-r11-deepseek-reason-code-adversarial-tests` |
| Status | superseded |
| Created | 2026-07-05 18:43 +1000 |
| Source HEAD | `01cf500` |

## Plan Summary

Reason-code adversarial route tests

## My Understanding

Design focused pytest coverage for the optional R11 status_reason_code substrate using the R10 uppercase taxonomy. Tests may be authored before backend implementation but final integrated tests must pass after Ariadne merges backend and tests; do not leave strict xfails in the final integration.

## Intended Surface / Boundary

Focused appointment status/delete/audit pytest coverage, preferably a new tests/test_reason_code_adversarial.py or a tightly bounded adjacent test module.

## Out Of Scope

Production code, UI assets, migrations, database enum/reference table/check constraint, Bernie/session routes, changing temporal slot-write policy.

## Files I Expect To Edit

tests/test_reason_code_adversarial.py or tests/test_appointment_audit.py

## Implementation Steps

Cover valid codes, invalid-code rejection, null legacy compatibility, raw status/delete, proposal/confirm paths, audit/readback persistence, overlong/empty/special values, and no temporal drift for retrospective status/delete.

## Visual / Behavioural Acceptance Checks

Tests prove accepted uppercase codes persist, invalid codes 422, null compatibility remains, audit/readback expose codes, and status/delete temporal exemptions are unchanged.

## Risks / Ambiguities

Avoid snake_case taxonomy drift from R10 uppercase codes; if tests are written before backend implementation they may fail until integrated with backend patch.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

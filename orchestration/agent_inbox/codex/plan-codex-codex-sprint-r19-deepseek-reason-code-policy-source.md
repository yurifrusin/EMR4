# plan-codex-codex-sprint-r19-deepseek-reason-code-policy-source

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-sprint-r19-deepseek-reason-code-policy-source` |
| Status | integrated |
| Created | 2026-07-05 21:21 +1000 |
| Source HEAD | `6ba0805` |

## Plan Summary

Backend status-specific reason-code policy with frontend-drift detection

## My Understanding

Backend has flat STATUS_REASON_CODES with no status-specific mapping; frontend already has STATUS_SPECIFIC_REASON_CODE_OPTIONS. Add backend source-of-truth policy dict, status-aware validator, and frontend-drift detection test.

## Intended Surface / Boundary

app/schemas/appointments.py, tests/test_reason_code_backend.py

## Out Of Scope

UI changes, diary.js mutation code, migrations, Bernie session schemas

## Files I Expect To Edit

app/schemas/appointments.py, tests/test_reason_code_backend.py

## Implementation Steps

1. Add STATUS_SPECIFIC_REASON_CODE_POLICY dict mapping Cancelled/DNA/NoShow to their allowed codes. 2. Add validate_status_reason_code_for_status(). 3. Update AppointmentStatusUpdate, AppointmentStatusProposalIn, AppointmentStatusCommand, AppointmentDeleteCommand validators. 4. Add frontend-drift detection test parsing diary.js constants. 5. Add valid/invalid combo test coverage.

## Visual / Behavioural Acceptance Checks

Backend rejects Cancelled+DID_NOT_ATTEND (422); accepts Cancelled+PATIENT_CANCELLED; existing tests pass; frontend-drift test catches option mismatches; no mutation-semantics changes.

## Risks / Ambiguities

Grandfathered old records; delete proposal hardcodes Cancelled set; Bernie paths flow through same validators; frontend label drift test only covers STATUS_SPECIFIC_REASON_CODE_OPTIONS

## Codex Plan Review

- Review result: accepted and integrated with Gemini/Ariadne amendment to make `PATIENT_RESCHEDULED`, `PATIENT_UNWELL`, and `CLINIC_RESCHEDULED` valid `Cancelled` options in backend policy and frontend constants.
- Required changes before implementation: preserve null/grandfathering semantics; do not add migrations or requiredness changes in R19.
- Approved to proceed: yes

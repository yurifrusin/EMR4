# plan-antigravity-antigravity-sprint-r16-status-specific-reason-code-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r16-status-specific-reason-code-ux-review` |
| Status | integrated |
| Created | 2026-07-05 20:38 +1000 |
| Source HEAD | `e432c3b` |

## Plan Summary

Sprint R16 status-specific reason-code filtering plan

## My Understanding

Implement status-specific filtering for terminal reason codes (Cancelled, DNA, NoShow) in the first-party Diary UI, replacing date-based filtering. Fully remove PATIENT_UNWELL, and align LEFT_WITHOUT_SEEN as an administrative option under DNA and NoShow.

## Intended Surface / Boundary

Diary booking edit modal: status dropdown (#booking-status), reason-code container (#booking-status-reason-code-container), reason select (#booking-status-reason-code).

## Out Of Scope

No backend schema/migration changes, no modification of audit model or cancellation_reason storage.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.html, docs/receptionist_review_r16.md

## Implementation Steps

1. In docs/diary/diary.js, declare STATUS_SPECIFIC_REASON_CODES mapping. 2. Refactor populateBookingReasonCodeOptions(status) to filter by status rather than context. 3. Update visibility sync to pass the status value. 4. Verify tests pass.

## Visual / Behavioural Acceptance Checks

Selecting Cancelled shows cancellation options. Selecting DNA/NoShow shows non-attendance/walkout options (including LEFT_WITHOUT_SEEN). PATIENT_UNWELL is never present. Smoke tests pass.

## Risks / Ambiguities

Existing smoke tests expect LEFT_WITHOUT_SEEN when DNA is set in the past, but status-specific filtering resolves this correctly.

## Codex Plan Review

- Review result: Accepted and integrated as domain guidance.
- Required changes before implementation: Use status-specific lists and include `LEFT_WITHOUT_SEEN` under `DNA`/`NoShow`.
- Approved to proceed: yes

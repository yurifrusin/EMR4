# plan-antigravity-antigravity-diary-noshow-dna-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-noshow-dna-flow` |
| Status | superseded |
| Created | 2026-06-26 16:23 +1000 |
| Source HEAD | `909df00` |

## Plan Summary

Clear and reviewable diary no-show/DNA user flow with proposal-first confirmation, terminal attendance labels, waiting-room/grid non-confusion, and deterministic review checks.

## My Understanding

NoShow and DNA must undergo proposal-first confirmation when modified in the edit modal, transition to terminal statuses must clear waiting area assignment to avoid active waiting-room/grid confusion, and these states must be verified by deterministic review checks.

## Intended Surface / Boundary

Status mutation, terminal status badges, and Edit Modal flow in docs/diary/diary.js. Nearby surfaces like patient lists, clinical panels, and grid layouts must not change.

## Out Of Scope

Backend routes/models/tests/migrations, side-by-side grid lane/overlap layout work, taskpane/Command Centre, cancellation reason/note capture, cancelled appointment review redesign, recurrence.

## Files I Expect To Edit

docs/diary/diary.js, review/checks_diary.json

## Implementation Steps

1. Add default NoShow/DNA mock appointments in dummy data for testing.
2. Clear waiting area assignment when status transitions to a terminal state (NoShow or DNA).
3. Ensure status proposal checks in the Edit Modal apply to NoShow/DNA changes, prompting confirmation before mutation.
4. Update UI rendering to display clear terminal status badges/labels for NoShow/DNA appointments.
5. Add deterministic smoke checks in review/checks_diary.json to verify terminal status and waiting room clearance.

## Visual / Behavioural Acceptance Checks

Terminal status badges display correctly; Edit Modal status changes to NoShow/DNA prompt proposal confirmation; waiting area is cleared on terminal transition; deterministic review checks pass.

## Risks / Ambiguities

Clearing waiting area might not trigger immediate waiting-room UI update if rendering is decoupled; handled by using the existing standard render refresh path after proposal confirmation.

## Codex Plan Review

- Review result:
- Required changes before implementation: original plan was amended to remove out-of-scope overlap/lane layout work.
- Approved to proceed: yes, but no implementation was integrated. Antigravity CLI later timed out in print mode before submitting code; Ariadne verified the existing diary code and cheap review harness already covered the narrow Sprint 32 frontend expectations, then stood the workstream down.

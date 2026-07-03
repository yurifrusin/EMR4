# plan-antigravity-antigravity-sprint-n4-diary-session-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n4-diary-session-ux-review` |
| Status | accepted |
| Created | 2026-07-03 22:07 +1000 |
| Source HEAD | `a07f0ca` |

## Plan Summary

Plan Sprint N4 Diary/Bernie UI implications for server-owned session/event state: render-from-state tail, stale-state display, one session per staff per diary surface, and confirm evidence echo after persistence lands.

## My Understanding

Align client-side BernieSession with backend BernieSessionRecord (server-owned state machine, event tail rendering, and session/evidence hashes). UI will act as a renderer of server state. Implement stale state warnings if diary navigation changes the active patient/practitioner/date context from the session context, preventing invalid confirmations. Fetch existing session on initial load/refresh (supporting cross-tab synchronization and removing local PHI storage).

## Intended Surface / Boundary

docs/diary/diary.js (class BernieSession and loadBernieLiveReview), docs/diary/diary.html, docs/diary/diary.css, review/test_diary_smoke.py

## Out Of Scope

Production backend implementation, GraphRAG or practice-knowledge UI wiring, visual redesign, database migrations, changes to taskpane / Office.js sidebar.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.html, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Modify BernieSession to load active session from GET /api/v1/appointments/proposals/bernie/active-session on init. 2. Implement backend call for new session POST /api/v1/appointments/proposals/bernie/new-session. 3. Update updateBernieChatTranscriptUI to render bubbles directly from server-supplied events list. 4. Add stale warning banner in diary.html/css. 5. Add check in loadBernieLiveReview to compare active diary view context with session context, displaying stale warning and disabling confirm button on mismatch. 6. Provide 'Jump to Session' and 'New Session' actions on the stale warning. 7. Verify confirm payload echoes session_id, turn_ref, and evidence IDs. 8. Add Playwright smoke tests for active session load, stale context warning, and context recovery.

## Visual / Behavioural Acceptance Checks

1. Verify transcript and state restore on refresh. 2. Verify stale warning banner appears when navigating to different date or practitioner and confirm button is disabled. 3. Verify 'Jump to Session' reverts diary date/practitioner and enables confirm button. 4. Verify 'New Session' clears stale state and transcript. 5. Verify confirm payload includes session_id, turn_ref, and freshness hashes.

## Risks / Ambiguities

1. Race conditions during rapid navigation or state transitions: client should disable inputs during API fetches. 2. Null values for practitioner_id or patient_id during context selection: need robust default handling.

## Codex Plan Review

- Review result: Accepted as the render-from-state/UI tail plan.
- Required changes before implementation: Do not implement the UI lane in the
  first N4 backend foundation slice. Backend-owned session semantics and route
  contracts must exist before Diary assets consume them.
- Approved to proceed: deferred

# plan-antigravity-antigravity-sprint-n5-diary-session-render-tail

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n5-diary-session-render-tail` |
| Status | accepted |
| Created | 2026-07-03 22:26 +1000 |
| Source HEAD | `c185281` |

## Plan Summary

Plan Sprint N5 Diary UI work to consume the minimal Bernie session endpoint

## My Understanding

Consume server-owned Bernie session active-session load, new-session, event append/refetch, stale revision banner, history rendering, and confirm evidence echo without client-side authority.

## Intended Surface / Boundary

The right sidebar panel (#bernie-review-panel, #bernie-chat-transcript, #bernie-review-content) and Playwright review smoke tests.

## Out Of Scope

No backend router/schema changes or table migrations, no GraphRAG, no auto-confirm, no SMS/taskpane edits.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.html, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Add #bernie-stale-banner container in diary.html. 2. Add styles in diary.css. 3. Update BernieSession class in diary.js to fetch active session and POST events with expected_revision. 4. Handle 409 conflict by displaying the stale banner. 5. Bind Refetch/Refresh button to reload session state. 6. Render chat transcript from server events. 7. Echo confirm evidence. 8. Add smoke tests for session conflict and refetch.

## Visual / Behavioural Acceptance Checks

Active session loads automatically; stale revision returns 409 and shows banner; clicking refresh refetches and clears banner; older history is collapsed; confirm echoes backend-supplied signed evidence.

## Risks / Ambiguities

API route path mismatch with concurrent backend worker; client/server synchronization latency on rapid date navigation.

## Codex Plan Review

- Review result: Accepted as the Diary render/refetch tail plan.
- Required changes before implementation: Defer UI implementation until the
  backend endpoint contract lands and is verified.
- Approved to proceed: deferred

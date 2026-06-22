# plan-antigravity-antigravity-diary-checkin-waiting-area-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-checkin-waiting-area-ui` |
| Status | integrated |
| Created | 2026-06-22 15:58 +1000 |
| Source HEAD | `d8f3672` |

## Plan Summary

Streamline waiting-area check-in, live waiting area reassignment, compact expected list, and hide single-area tabs.

## My Understanding

Receptionists need to assign patients to specific waiting areas on check-in. The Waiting Room panel needs inline area selection, live reassignment for arrived patients, denser Expected Today cards, and to hide redundant tabs if there's only one waiting area.

## Intended Surface / Boundary

Waiting Room side panel in docs/diary/ (html, css, js). Visually adjacent surfaces that must NOT change: main diary grid columns, booking modal, and appointment positioning.

## Out Of Scope

No backend migrations, models, or routes. No taskpane, Command Centre, or Bernie changes.

## Files I Expect To Edit

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js

## Implementation Steps

1. Implement getDefaultWaitingArea in diary.js to find inferred default waiting area. 2. Modify renderWaitingAreaTabs to return false if areas.length <= 1. 3. Extend setAppointmentStatus to accept waitingAreaId and include in status patch payload. 4. Render select element inside cards in renderFlowList for Expected Today and Waiting Room. 5. Style select element and compact Expected Today list in diary.css. 6. Bump cache buster in diary.html.

## Visual / Behavioural Acceptance Checks

1. Select area dropdown matches config. 2. Click Check In maps status to Arrived with selected area. 3. Arrived card dropdown changes area dynamically. 4. Expected Today is denser. 5. Single area hides tabs.

## Risks / Ambiguities

1. Mock data discrepancy in smoke test (handled by adding mock area support). 2. Single area check-in doesn't crash (handled by fallback checks).

## Codex Plan Review

- Review result: Implemented by Antigravity and integrated as part of Sprint 15. Note: Antigravity auto-proceeded after plan; protocol alerts were tightened afterward so auto-proceed is explicitly not approval.
- Required changes before implementation: none after diff review; future agents must still wait for explicit approval
- Approved to proceed: yes

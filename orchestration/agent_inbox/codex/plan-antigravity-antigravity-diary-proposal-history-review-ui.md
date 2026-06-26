# plan-antigravity-antigravity-diary-proposal-history-review-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-proposal-history-review-ui` |
| Status | pending_plan_review |
| Created | 2026-06-26 17:17 +1000 |
| Source HEAD | `662e61e` |

## Plan Summary

Plan a lightweight read-only review surface for appointment proposal/audit history at the bottom of the booking modal, collapsing it by default, and degrading gracefully if the endpoint is not implemented.

## My Understanding

Sprint 33 / Programme 2D readiness: Plan a lightweight diary-side read-only review surface for appointment proposal/audit history once the backend contract exists. The UI must be read-only, non-mutating, and collapsed by default to keep the active diary workflow clean and uncluttered. It must degrade gracefully when no history exists or when the server does not support the history endpoint (e.g. 404/501 responses), and it should be simulated in smoke mode (?smoke=true) to enable automated smoke test assertions.

## Intended Surface / Boundary

Affected Surface: The bottom of the booking modal (booking-modal-inner / booking-modal-body) when editing an existing appointment. It will show a collapsible container containing a scrollable, chronologically descending list of history logs (timestamp, actor, action, details). Nearby Surfaces (MUST NOT CHANGE): Booking form inputs/fields, diary grid columns, the waiting room sidebar lists, and the resource administration modal remain untouched.

## Out Of Scope

1. Backend routes, schemas, database models, or Alembic migrations (handled in Workstream S33-A).
2. Taskpane or Command Centre SPA clinical history tabs.
3. Write/update operations (restore, edit logs) from the history panel.
4. AI-provider integration or Gemini prompting logic.
5. Unrelated visual redesign of existing modal elements.

## Files I Expect To Edit

- docs/diary/diary.html: Add HTML structure for the collapsible history section container and list.
- docs/diary/diary.css: Add structural styling, text sizes, scroll limits, and interactive styles for the history toggles.
- docs/diary/diary.js: Add visibility toggling, fetch logic on modal load (handling real API calls & smoke mode mock history), list rendering, and graceful error catching.
- review/checks_diary.json: Add a Playwright smoke assert to confirm that the history section elements render correctly in smoke mode.

## Implementation Steps

1. HTML Structure: Add `#booking-history-section` containing a toggle header (title and chevron) and a scrollable content list at the bottom of `booking-modal`.
2. CSS Rules: Implement styles for `.booking-history-section` (top border, margin), `.booking-history-header` (cursor pointer, colors), `.booking-history-content` (max-height 120px, scroll), and list items.
3. JavaScript Collapsible Handler: Add event listener to the toggle header to expand/collapse the content and rotate the chevron.
4. Modal Lifecycle Integration: Update `openBookingModalForEdit` to show the section, reset it to collapsed, clear prior list contents, and load history. Update `openBookingModalForCreate` to hide the section.
5. Fetch & Render Logic: Call `GET /appointments/{id}/history`. Catch errors (404, 501, network issues) and display a clean degradation fallback message. Render descending list if successful.
6. Smoke Mode Simulation: In `isSmokeMode()`, load a mock list of history events (e.g. proposed, approved, status changed) for the selected mock appointment.
7. Automated Checks: Update `review/checks_diary.json` with a test case checking that the history header or entries are present under `?smoke=true`.

## Visual / Behavioural Acceptance Checks

1. Create Appointment: Open booking modal for a new slot; the history section must be completely hidden.
2. Edit Appointment (Smoke): Open edit modal; history section is visible but collapsed. Clicking the header expands it to show the mock history entries.
3. Graceful Fallback: Open edit modal and simulate API fetch failing; expanding the history shows 'No history available' or 'History not supported' without console errors or UI disruption.
4. Smoke Suite Pass: Running `pytest review/test_diary_smoke.py` passes all assertions (including the new history check) cleanly.

## Risks / Ambiguities

1. Endpoint Name Alignment: The backend contract is currently being developed in Workstream S33-A. We mitigate this by using a standard REST route and implementing robust try/catch blocks that degrade gracefully to a 'Not supported' message if the endpoint returns 404/501.
2. Modal Overflow: Adding content to the modal risks overflow. We mitigate this by setting a strict max-height on the history content list (120px) with vertical scrolling.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

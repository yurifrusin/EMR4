# plan-antigravity-antigravity-diary-proposal-history-review-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-proposal-history-review-ui` |
| Status | integrated |
| Created | 2026-06-26 17:17 +1000 |
| Source HEAD | `662e61e` |

## Plan Summary

Plan a lightweight read-only review surface for appointment proposal/audit history at the bottom of the booking modal, collapsing it by default, hiding it on create, and degrading gracefully if the audit endpoint is not implemented or fails.

## My Understanding

Sprint 33 / Programme 2D readiness: Plan a lightweight diary-side read-only review surface for appointment proposal/audit history once the backend contract exists. The UI must be read-only, non-mutating, collapsed by default, hidden on create, and visible only on edit to keep the active diary workflow clean and uncluttered. It will call `GET /api/v1/appointments/{id}/audit` as the primary endpoint and render the backend audit event shape directly. It must degrade gracefully when no audit logs exist or when the server does not support the audit endpoint (e.g. 404/501 responses), and it should be simulated in smoke mode (`?smoke=true`) to enable automated smoke test assertions.

## Intended Surface / Boundary

Affected Surface: The bottom of the booking modal (booking-modal-inner / booking-modal-body) when editing an existing appointment. It will show a collapsible container containing a scrollable, chronologically descending list of audit events. Nearby Surfaces (MUST NOT CHANGE): Booking form inputs/fields, diary grid columns, the waiting room sidebar lists, and the resource administration modal remain untouched.

## Out Of Scope

1. Backend routes, schemas, database models, or Alembic migrations (handled in Workstream S33-A).
2. Taskpane or Command Centre SPA clinical history tabs.
3. Write/update operations (restore, edit logs) from the history/audit panel.
4. AI-provider integration or Gemini prompting logic.
5. Unrelated visual redesign of existing modal elements.

## Files I Expect To Edit

- docs/diary/diary.html: Add HTML structure for the collapsible audit section container and list.
- docs/diary/diary.css: Add structural styling, text sizes, scroll limits, and interactive styles for the audit toggles.
- docs/diary/diary.js: Add visibility toggling, fetch logic on modal load (handling real API calls & smoke mode mock audit data), list rendering, and graceful error catching.
- review/checks_diary.json: Add a Playwright smoke assert to confirm that the audit section elements render correctly in smoke mode.

## Implementation Steps

1. HTML Structure: Add `#booking-audit-section` containing a toggle header (title and chevron) and a scrollable content list at the bottom of `booking-modal`.
2. CSS Rules: Implement styles for `.booking-audit-section` (top border, margin), `.booking-audit-header` (cursor pointer, colors), `.booking-audit-content` (max-height 120px, scroll), and list items.
3. JavaScript Collapsible Handler: Add event listener to the toggle header to expand/collapse the content and rotate the chevron.
4. Modal Lifecycle Integration: Update `openBookingModalForEdit` to show the section, reset it to collapsed, clear prior list contents, and load audit logs. Update `openBookingModalForCreate` to hide the section.
5. Fetch & Render Logic: Call `GET /api/v1/appointments/{id}/audit`. Catch errors (404, 501, network issues) and display a clean degradation fallback message. If successful, render a chronologically descending list using the backend audit event shape (handling fields such as `created_at`, `action`, `status_target`, `cancellation_reason`, `warning_codes`, `confirmed_with_warnings`, and `confirmed_by`/`confirmed_by_user_id`).
6. Smoke Mode Simulation: In `isSmokeMode()`, load a mock list of audit events matching the backend audit event shape for the selected mock appointment.
7. Automated Checks: Update `review/checks_diary.json` with a test case checking that the audit header or entries are present under `?smoke=true`.

## Visual / Behavioural Acceptance Checks

1. Create Appointment: Open booking modal for a new slot; the audit section must be completely hidden.
2. Edit Appointment (Smoke): Open edit modal; audit section is visible but collapsed. Clicking the header expands it to show the mock audit entries.
3. Graceful Fallback: Open edit modal and simulate API fetch failing (404, 501, network error); expanding the audit section shows 'Audit history not available' or 'Audit history not supported' without console errors or UI disruption.
4. Smoke Suite Pass: Running `pytest review/test_diary_smoke.py` passes all assertions (including the new audit check) cleanly.

## Risks / Ambiguities

1. Endpoint Name Alignment: The backend contract is currently being developed in Workstream S33-A. We mitigate this by using `/api/v1/appointments/{id}/audit` and implementing robust try/catch blocks that degrade gracefully to a 'Not supported' message if the endpoint returns 404/501.
2. Modal Overflow: Adding content to the modal risks overflow. We mitigate this by setting a strict max-height on the audit content list (120px) with vertical scrolling.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

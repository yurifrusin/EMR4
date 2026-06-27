# plan-antigravity-antigravity-bernie-selected-appointment-context

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-selected-appointment-context` |
| Status | integrated |
| Created | 2026-06-27 20:24 +1000 |
| Source HEAD | `0697941` |

## Plan Summary

Plan for Bernie selected appointment context

## My Understanding

- Integrate a real diary-selected appointment context source for the Bernie pilot review.
- Instead of requiring users to manually lookup and enter practitioner & patient UUIDs, they can select a fully linked appointment in the diary grid.
- If a valid linked appointment is selected (i.e. has a practitioner ID and a linked/confirmed patient ID), the Bernie pilot context panel will show a "Use selected appointment: [Patient Name]" button.
- Clicking the button sets the practitioner and patient IDs in memory and submits the context form (prepares supervised review).
- If the selected appointment is provisional (unconfirmed patient), has no practitioner context, or if no appointment is selected, we block/explain this with clear, structured messages.
- The existing manual ID fields are retained as fallbacks.
- The context must NOT be stored in localStorage/sessionStorage or query string/URL params.
- Staff instruction input and the checkbox confirmation gate must be preserved.

## Intended Surface / Boundary

- **Inside Boundary**:
  - `docs/diary/diary.js` (logic for selected appointment detection, validation, rendering the "Use selected" affordance, block states, and triggering refresh on selection change).
  - `docs/diary/diary.html` (bump query string versions to `v=119` for script and `v=109` for stylesheet).
  - `docs/diary/diary.css` (styles for the new selected appointment panel, button, and warning/info messages).
  - `review/test_diary_smoke.py` (Playwright tests for appointment context selection, blocked states, and validation).
- **Adjacent Surfaces Unchanged**:
  - No changes to backend API models, routers, schemas, or migrations.
  - No changes to the booking modal layout or behaviour.
  - No changes to wait room, waiting areas, or roster list consumption.

## Out Of Scope

- Backend changes or database writes.
- Search interfaces for patients or practitioners.
- Persisting IDs in cookies, localStorage, sessionStorage, or URL query parameters.
- Changing appointment create/edit flow, reschedule, or cancel behaviour.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.css](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.css)
- [docs/diary/diary.html](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.html)
- [review/test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)

## Implementation Steps

1. **Appointment and Grid Click handlers**:
   - In `docs/diary/diary.js`, modify the click handlers for `.appt` (appointment elements) and `#diary-grid` backdrop so that if selection changes and `isBerniePilotActive` is true, we call `loadBernieLiveReview()` to refresh the sidebar context panel.
2. **Context Form Extension**:
   - In `renderBerniePilotContextForm(blocks)`, look up the currently active appointment via `document.querySelector(".appt-active")`.
   - If present, find the appointment object by ID in `activeAppointments`.
   - Retrieve/resolve the practitioner ID (using `a.practitioner_id || a.practitioner?.id || (a.practitioner?.ahpra_number ? ahpraToPractitionerMap[a.practitioner.ahpra_number]?.id : null)`) and check if the patient is provisional via `isPatientIdentityUnconfirmed(a)`.
   - Create a sub-panel container `div` with class `bernie-pilot-selected-appt-panel`.
   - If the selected appointment is valid (has practitioner context and a linked/confirmed patient):
     - Expose the "Use selected appointment: [Patient Name]" button (testid `bernie-pilot-use-selected`, class `btn-bernie-use-selected`).
     - Wire the click event to populate input fields, save context values using `setBerniePilotContextValues()`, and trigger `loadBernieLiveReview()`.
   - If invalid:
     - Render clear block warnings (e.g. "Selected appointment is provisional (unlinked patient record)" or "Selected appointment has no practitioner context") inside a `div` with class `bernie-pilot-selected-status error` and testid `bernie-pilot-selected-status-error`.
   - If no appointment is selected:
     - Render a message "No appointment selected in the diary." inside a `div` with class `bernie-pilot-selected-status info` and testid `bernie-pilot-selected-status-info`.
3. **Styling in CSS**:
   - Add styling in `docs/diary/diary.css` for `.bernie-pilot-selected-appt-panel`, `.btn-bernie-use-selected`, and status messages (`error`/`info`).
4. **Asset Bumping**:
   - Update `diary.js?v=119` and `diary.css?v=109` in `docs/diary/diary.html`.
5. **Write Playwright Smoke Tests**:
   - Add tests to `review/test_diary_smoke.py` simulating selection of:
     - A linked appointment (e.g., `smoke-appt-1`) -> click the use-selected button -> verify context form disappears and supervised booking endpoint is called with correct practitioner/patient payload.
     - A provisional appointment (e.g., `smoke-appt-6`) -> verify block error message is rendered.
     - No appointment -> verify info message is rendered.

## Visual / Behavioural Acceptance Checks

- Launch EMR4 diary in ordinary pilot mode.
- Context form shows "No appointment selected in the diary." at the bottom of the form.
- Click `smoke-appt-1` (Margaret Thompson). The message updates to a purple button: "Use selected appointment: Margaret Thompson".
- Click "Use selected appointment: Margaret Thompson". The context form resolves, practitioner ID is populated with `smoke-prac-1`, patient ID is populated with `smoke-pat-1`, and the review loading transitions to the instruction input.
- Click `smoke-appt-6` (Nora Patel). The message updates to a red error message: "Selected appointment is provisional (unlinked patient record)."
- Click the empty grid space. The selection clears, and the panel goes back to "No appointment selected in the diary."
- Ensure URL query parameters and local/sessionStorage remain free of `patient_id` or `practitioner_id` keys.

## Risks / Ambiguities

- **Linked Patients in Smoke Mode**: In mock data (`getMockAppointments()`), the appointments don't contain a `patient_id` attribute. To ensure that `isPatientIdentityUnconfirmed` does not treat mock appointments as unconfirmed (due to `!appt.patient_id`), we must map `patient_id` explicitly for non-provisional mock appointments during smoke initialization. In `docs/diary/diary.js`, when `loadDiary()` loads mock appointments, we will map their `patient.id` (or `patient_id`) to the correct matching mock patient ID (e.g. `smoke-pat-1` for Margaret Thompson) if they are not provisional. This ensures that the mock appointments correctly show up as "linked" and are usable in tests.

## Codex Plan Review

- Review result: accepted; implementation released to Antigravity.
- Required changes before implementation: keep selected context in memory only and keep smoke-only context mapping narrow.
- Approved to proceed: yes

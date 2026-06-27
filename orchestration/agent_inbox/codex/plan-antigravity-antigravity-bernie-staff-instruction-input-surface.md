# plan-antigravity-antigravity-bernie-staff-instruction-input-surface

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-staff-instruction-input-surface` |
| Status | pending_plan_review |
| Created | 2026-06-27 19:10 +1000 |
| Source HEAD | `a07c98ee` |

## Plan Summary

Replace temporary structured-context instruction construction with a proper staff-entered, pilot-gated instruction surface that avoids query-string free text

## My Understanding

The product goal is to add a proper staff-entered booking-instruction input surface for the supervised Bernie pilot review flow in docs/diary/diary.html and docs/diary/diary.js. This enables staff to enter a free-text, non-PHI booking instruction without exposing the instruction text in URL query strings or local storage. The instruction text is sent to the backend interpreter (/appointments/proposals/bernie/interpret-booking-instruction) in the POST request body. If the interpreted result requires clarification, the staff must be shown a clarification field, and confirmation must be blocked. If it is successfully interpreted, the parsed command_candidate should be submitted in the request body to /appointments/proposals/bernie/supervised-booking to obtain slot candidates. If the status is candidate_selection_required, staff can select a candidate slot (using click elements or select buttons) which will make a new POST request to /supervised-booking with the selected candidate index in the request body. If confirmation_ready, they can explicitly confirm via the existing checkbox-mediated flow.

## Intended Surface / Boundary

Only the Bernie review sidebar panel (#bernie-review-panel) inside the native HTML/JS diary interface (docs/diary/diary.html and docs/diary/diary.js). We will add a compact booking instruction input form (a textarea or input with an action button) inside #bernie-review-content, a clarification response input form in the clarification_required state, and interactive controls (buttons or links) next to candidates in the candidate_selection_required state to select a candidate. Other surfaces, including the main diary grid, waitlist, taskpane, and Command Centre, must remain completely unchanged.

## Out Of Scope

Backend routes, FastAPI schemas, and database model changes (such as adding instruction columns). Autonomous bookings. Exposing the Bernie pilot panel by default in production. URL query string instruction parsing/passing (no ?instruction=...). Persisting instruction text to localStorage or sessionStorage. Roster management, taskpane features, billing.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)\n- [docs/diary/diary.css](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.css) (only if styling tweaks are required)\n- [review/test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) (to update mock tests to simulate typing the instruction and clicking the button, and testing clarification state blocking).

## Implementation Steps

1. Define State Variables in docs/diary/diary.js: bernieInstructionText, bernieSelectedCandidateIndex, bernieInterpretEnvelope, bernieSupervisedBookingPayload, isBerniePilotActive.\n2. Revise loadBernieLiveReview(): Check context readiness. If ready but bernieInstructionText is empty, render the initial input surface and return without calling the backend. If bernieInstructionText is set, call /appointments/proposals/bernie/interpret-booking-instruction. If result is clarification_required or blocked, render that state (and block confirm). If interpreted, call /appointments/proposals/bernie/supervised-booking with command_candidate in the body.\n3. Render Instruction Input Form: Textarea with id='bernie-instruction-input' and button id='btn-bernie-instruction-submit'. Submit stores text and re-runs loadBernieLiveReview().\n4. Render Clarification Input Form: Displays question, response textarea id='bernie-clarification-input', button id='btn-bernie-clarification-submit'. Submits clarification, blocks confirmation.\n5. Render Candidate Selection Buttons: Add 'Select' button to each candidate slot. Clicking sets index and calls /supervised-booking with index in body.\n6. Dev/Smoke Test Fixture Bypass: Ensure query-params mock states (blocked, candidate_selection_required, confirmation_ready) still bypass live-input and directly load mocks.\n7. Bumps & Verifications: Increment cache-busting version in diary.html. Update Playwright test cases in review/test_diary_smoke.py to type instruction and click submit.

## Visual / Behavioural Acceptance Checks

- Launching the Bernie pilot with valid patient/practitioner context displays an empty text input area with a placeholder and a submit button.\n- Submitting an empty instruction does nothing or is blocked.\n- Typing an instruction and clicking 'Submit to Bernie' makes a body-only POST request to /proposals/bernie/interpret-booking-instruction.\n- When interpretation returns clarification_required, the clarifying question is displayed along with a response textbox, and the confirmation checkbox/button is not rendered.\n- When interpretation returns interpreted, it makes a POST request to /supervised-booking.\n- If candidate slots are returned, clicking a 'Select' button on a candidate sends selected_candidate_index in the body of a POST to /supervised-booking.\n- If confirmation_ready is returned, a 'Confirm Booking' checkbox and button are rendered; confirmation succeeds only when checked.

## Risks / Ambiguities

1. Ensuring Playwright/pytest-based checks are updated to correctly interact with the input elements (typing instruction, clicking submit) rather than expecting immediate API responses upon load.\n2. Clarifying that no free-text parameters are stored in window.location.search or localStorage.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

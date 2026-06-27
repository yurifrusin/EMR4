# plan-antigravity-antigravity-bernie-staff-instruction-input-surface

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-staff-instruction-input-surface` |
| Status | pending_plan_review |
| Created | 2026-06-27 19:10 +1000 |
| Source HEAD | `bf0a14d` |

## Plan Summary

Implement a compact staff instruction input inside the existing Bernie pilot/review panel using a body-only POST to the interpret endpoint. Render empty, clarification, blocked, and interpreted preview states without query-string/localStorage instruction text, automatic interpret call before explicit submit, new candidate-selection UX, or clarification-submission UX.

## My Understanding

The product goal is to add a proper staff-entered booking-instruction input surface for the supervised Bernie pilot review flow in `docs/diary/diary.html` and `docs/diary/diary.js`. 
This implementation is strictly scoped as follows:
1. **Compact Staff Instruction Input**: Render an input area and submit button in the Bernie pilot/review panel when no instruction is active.
2. **Explicit Submit Only**: There must be no automatic interpret call on load/setup; interpretation must only be triggered when staff explicitly click the submit button.
3. **Body-only POST**: The instruction text must be passed solely in the POST body to the `/appointments/proposals/bernie/interpret-booking-instruction` endpoint. No URL query strings (e.g., `?instruction=...`) or `localStorage` persistence can be used.
4. **Preview States**: The UI must render the following states based on the backend interpreter's response status:
   - `empty`: Shows the initial compact instruction input area.
   - `clarification`: Displays the clarifying question text from the backend, blocks confirmation, and does NOT add any clarification-response input form or submission UX in this sprint.
   - `blocked`: Displays the blocking message from the backend.
   - `interpreted`: Calls the `/appointments/proposals/bernie/supervised-booking` endpoint with the parsed `command_candidate` in the body to load candidates.
5. **Preserve Existing Display & Gate**: Retain the existing candidate display list exactly as-is and preserve the confirmation checkbox/button approval gate for `confirmation_ready` status. Do not add any new candidate-selection UX (like clickable candidate select buttons/handlers) in this sprint.

## Intended Surface / Boundary

Only the Bernie review sidebar panel (`#bernie-review-panel` / `#bernie-review-content`) in the native diary UI (`docs/diary/diary.html` and `docs/diary/diary.js`). We will add a compact text input area and an explicit action button (`#btn-bernie-instruction-submit`) inside `#bernie-review-content`. Surrounding surfaces such as the main diary grid, waitlist, taskpane, and Command Centre must remain completely unchanged.

## Out Of Scope

- Backend endpoints, schemas, or database modifications.
- Autonomous booking creation or writes without the approval checkbox/button flow.
- Exposing the Bernie pilot panel by default in production.
- URL query-string parameters (`window.location.search`) or `localStorage`/`sessionStorage` usage for storing the instruction.
- Clarification-submission UX (no inputs, textareas, or submit buttons to answer the clarifying question).
- Candidate-selection UX (no selection buttons or slot modification handlers).
- Broad diary layout adjustments.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js) (Define state, handle explicit submit button click, execute body-only POST to interpret, handle and render empty/clarification/blocked/interpreted states, and preserve existing candidates display/confirm flow)
- [docs/diary/diary.html](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.html) (HTML container layout for the compact staff instruction input inside `#bernie-review-content`)
- [docs/diary/diary.css](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.css) (minimal styling tweaks for the input and button inside the review sidebar panel)
- [review/test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) (update smoke/review tests to type the instruction, click the submit button, and assert the rendering of empty/clarification/blocked/interpreted states)

## Implementation Steps

1. **State Definition in docs/diary/diary.js**: Declare in-memory JS state variables to hold `bernieInstructionText` and `bernieInterpretResult` (do not read/write from query strings or `localStorage`).
2. **Setup the HTML structure**: In `docs/diary/diary.html`, define the placeholder structure for the instruction textarea (`#bernie-instruction-input`) and explicit submit button (`#btn-bernie-instruction-submit`) inside `#bernie-review-content`.
3. **Draft Render Logic**: Rewrite `loadBernieLiveReview()` (or the panel rendering handler) to branch based on the current state:
   - **Initial/Empty State**: Render the compact instruction textarea and submit button.
   - **Clarification State**: Render the clarifying question text from the backend response. Block confirmation. Ensure no response textbox or clarification submit button is rendered.
   - **Blocked State**: Render the blocking explanation text. Block confirmation.
   - **Interpreted State**: Automatically call `/appointments/proposals/bernie/supervised-booking` with the backend-provided `command_candidate` in the POST body. Display the returned candidates using the existing display layout.
4. **Implement Explicit Submit Handler**: Bind a click event listener to `#btn-bernie-instruction-submit` that reads the instruction text, performs a body-only POST request to `/appointments/proposals/bernie/interpret-booking-instruction`, saves the interpreter result, and re-renders the panel.
5. **Preserve Existing Gate**: Render the existing checkbox-mediated confirmation layout only when the status is `confirmation_ready`.
6. **Mock Bypass Logic**: Verify that local dev/preview fixture mock parameters (which skip live endpoints and load pre-baked fixture states) remain functional.
7. **Version & Tests**: Increment the cache-buster asset version of `diary.js` inside `docs/diary/diary.html`. Update Playwright test cases in `review/test_diary_smoke.py` to type the instruction and click submit, and verify the resulting UI states.

## Visual / Behavioural Acceptance Checks

- The Bernie pilot panel initially loads with a compact textarea and a submit button. No backend interpret API calls are made automatically on page load.
- Typing an instruction and clicking "Submit" makes a body-only POST request to `/appointments/proposals/bernie/interpret-booking-instruction` containing the instruction text.
- If the response is `clarification_required`, the clarifying question is displayed, no clarification input form is present, and the confirmation checkbox/button is hidden/disabled.
- If the response is `blocked`, the blocking message is displayed, and the confirmation checkbox/button is hidden/disabled.
- If the response is `interpreted` or `confirmation_ready`, the slots are rendered using the existing candidate list view, and the approval flow behaves as existing.
- The browser address bar URL and local storage never contain the staff-entered instruction text.

## Risks / Ambiguities

- Ensuring Playwright/pytest smoke tests are adapted to perform the explicit click action to trigger mock interpretation rather than expecting candidate slots on load.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

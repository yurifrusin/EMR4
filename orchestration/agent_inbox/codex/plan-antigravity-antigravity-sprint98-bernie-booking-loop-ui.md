# plan-antigravity-antigravity-sprint98-bernie-booking-loop-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint98-bernie-booking-loop-ui` |
| Status | pending_plan_review |
| Created | 2026-07-01 12:21 +1000 |
| Source HEAD | `b3c4f76` |

## Plan Summary

Sprint 98 plan resubmission for Bernie booking loop UI: support state transition back to candidate selection without network request/confirm POST, hide raw internal/snake_case codes for ordinary users while preserving diagnostics for developers under debug mode, handle confirmation failure with calm messaging (especially for Not Found), name version bumps, and add Playwright coverage.

## My Understanding

Provide a 'Choose different time' button when in confirmation_ready state to transition back to the candidate selection list without a network request. Ensure ordinary receptionists do not see raw snake_case/internal codes like "Missing Practitioner Id: " (from missing_practitioner_id block) or raw confirm details unless dev diagnostics are active. Do not try to resolve practitioner name on the frontend. If confirmation fails with Not Found or 404, show calm copy saying the slot is no longer available.

## Intended Surface / Boundary

- Diary/Bernie side panel (docs/diary/diary.js): renderBernieReview, stageBernieCandidateForReview, loadBernieLiveReview, and confirmBtn click listener.
- Diary HTML layout (docs/diary/diary.html): Bump asset cache-busters for CSS and JS.
- Testing (review/test_diary_smoke.py): Route-intercepted tests covering ordinary user copy, developer diagnostics, back transition, and Not Found confirm errors.
- No changes to backend code or database schemas.

## Out Of Scope

No backend modifications, database changes, new API endpoints, or other side panels/taskpanes. No frontend practitioner-name resolver or trying to solve raw missing_practitioner_id in the UI.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)
- [review/test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py)

## Implementation Steps

1. **State Preservation**: Add a global variable `let bernieLatestCandidatePayload = null;` in `docs/diary/diary.js`.
2. **Capture Candidates**: In `renderBernieReview`, if status is `candidate_selection_required`, store `payload` in `bernieLatestCandidatePayload`.
3. **Calm Block Rendering**: In `renderBernieReview`'s block rendering loop:
   - If not in dev/debug mode (i.e. `!isDevOrDebug` where `isDevOrDebug = isBernieDevOrDebug()`), do NOT prepend the formatted code prefix `formatBernieCode(block.code)` to the message. Only show the calm user-friendly text message itself.
   - For `missing_practitioner_id`, render "Please select a practitioner." as the entire message without any prefix or attempting to resolve it in the UI.
4. **Choose Different Time Button**:
   - In `renderBernieReview` under `confirmation_ready` state, add a button with class `btn-bernie-change-time` and test ID `bernie-review-change-time-button` with label "Choose different time".
   - Define exact state transition on click:
     - Clear staged preview/selected candidate: `bernieSelectedCandidateIndex = null; bernieStagedBookingPreview = null; bernieStagedBookingFresh = false;`
     - Render the restored candidate list: `renderBernieReview(bernieLatestCandidatePayload || { status: 'candidate_selection_required', candidate_slots: [] }, bernieInterpretResult);`
     - Reload the diary grid to clear the calendar staged card: `await loadDiary(true);`
     - Do NOT make any confirm POST or supervised-booking fetch requests.
5. **Calm Confirm Error Handling**:
   - In `confirmBtn` click handler, check `!isDevOrDebug`.
   - If confirmation fails (non-2xx response), check the error. If `response.status === 404` or error message contains "Not Found":
     - Set the text of `errorMsg` to the calm copy: "This slot is no longer available. Please choose a different time."
   - For other confirmation errors in ordinary mode, set `errorMsg` to a generic calm message: "We couldn't confirm this booking. Please try again or select another time."
   - If `isDevOrDebug` is true, show the raw detailed message: `Booking could not be confirmed: ${detail}`.
6. **Asset Cache-Busting**:
   - In `docs/diary/diary.html`, bump the stylesheet link from `diary.css?v=121` to `diary.css?v=122`.
   - Bump the script link from `diary.js?v=135` to `diary.js?v=136`.
7. **Write Route-Intercepted Tests**:
   - `test_bernie_ordinary_mode_no_raw_codes`: Launch Bernie in ordinary mode. Intercept supervised-booking response with a `missing_practitioner_id` block. Assert block is rendered as "Please select a practitioner." with no raw/formatted prefix or code, and that the developer diagnostic section is absent.
   - `test_bernie_dev_mode_diagnostics`: Launch Bernie in dev mode (`bernie_dev_review=true`). Intercept supervised-booking with `missing_practitioner_id`. Assert that the block contains the formatted prefix "Missing Practitioner Id: Please select a practitioner." and that the developer diagnostics section is visible and contains block code details.
   - `test_bernie_choose_different_time_restores_candidates`: Search for slots, click on a candidate (transitioning to `confirmation_ready`), assert that the staged preview card appears on the calendar. Click "Choose different time" and assert that the calendar staged preview card is removed and the candidate selection list is restored, without making new POST requests.
   - `test_bernie_generic_confirm_not_found_calm_copy`: Intercept supervised-booking to return `confirmation_ready`. Click confirm button. Intercept confirm-bernie endpoint to return `404 Not Found`. Assert that the error element shows "This slot is no longer available. Please choose a different time." with no raw details.

## Visual / Behavioural Acceptance Checks

- Ordinary users see no raw codes/internal codes or raw details on errors/blocks.
- Developer review mode shows full diagnostics, including raw error details and formatted codes.
- Choosing different time transitions back instantly to the candidate list and removes the proposed slot preview card from the main diary grid, without triggering any backend POST.
- Assets version bumps are correctly applied in HTML.

## Risks / Ambiguities

- None. Using in-memory cached payloads for candidate selection is fully deterministic and avoids unnecessary network calls.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

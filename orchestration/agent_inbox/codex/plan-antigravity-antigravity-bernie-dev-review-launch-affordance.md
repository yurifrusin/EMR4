# plan-antigravity-antigravity-bernie-dev-review-launch-affordance

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-dev-review-launch-affordance` |
| Status | pending_plan_review |
| Created | 2026-06-27 04:32 +1000 |
| Source HEAD | `0172804` |

## Plan Summary

Dev-only

## My Understanding

The goal is to implement a developer-only convenience affordance (a button) in the Diary UI to launch the Bernie supervised review panel. This avoids developers having to manually construct a URL with `bernie_review=live`. 
- The affordance (button) must only be visible when the explicit URL parameter `bernie_dev_review=true` is present.
- By default (flag absent), the button must remain hidden, and no automatic endpoint calls to the supervised booking API should be triggered.
- When clicked, the user action will opt into the existing `bernie_review=live` path by appending/updating query parameters and reloading/navigating the page.
- Staff approval / confirmation functionality remains strictly gated behind checkbox confirmation.

## Intended Surface / Boundary

- **Diary UI Header (`docs/diary/diary.html` & `docs/diary/diary.css`)**: 
  - Add a button with ID `btn-bernie-dev-launch` and `data-testid="bernie-review-dev-launch-button"` in `diary-actions`.
  - The styling must match other header toolbar buttons (like the refresh button).
- **Query Parameter Handling (`docs/diary/diary.js`)**:
  - Parse query string on initialization.
  - If `bernie_dev_review=true` is present, but `bernie_review` is not set or not `"live"`, reveal the button.
  - Clicking the button reloads the page with `bernie_review=live` preserved alongside existing parameters.
- **Boundary**: Nearby elements (date navigations, refresh actions, waiting room sidebar, grid) must not be affected. Default/production page loads must show no visible launch button or change in behavior.

## Out Of Scope

- Backend endpoints, schema definitions, or DB models.
- Live autonomous writes/bookings without staff approval.
- Unrelated styling or functional changes to the diary layout, wait room, or booking modals.
- Taskpane or Command Centre modifications.

## Files I Expect To Edit

- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html): Add button element, bump script/stylesheet version query parameters to bust cache.
- [docs/diary/diary.css](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.css): Add styles for `#btn-bernie-dev-launch`.
- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js): Add logic to show/hide the button and handle the click event to navigate/reload.
- [review/test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py): Add Playwright-based test cases validating dev-only visibility, default hiding, and redirect/load behavior.

## Implementation Steps

1. **HTML Update**: In `docs/diary/diary.html`, insert a `<button>` with ID `btn-bernie-dev-launch`, text `"🤖 Dev Bernie Review"`, class `"hidden"`, and attribute `data-testid="bernie-review-dev-launch-button"`. Bump CSS (`v=102`) and JS (`v=109`) references.
2. **CSS Update**: Add CSS rule for `#btn-bernie-dev-launch` in `docs/diary/diary.css` to format the button, matching spacing and border rules of header actions.
3. **JS Logic Update**: In `docs/diary/diary.js` initialization:
   - Identify if `bernie_dev_review` is `"true"`.
   - If true and `bernie_review` is not `"live"`, remove the `"hidden"` class from `btn-bernie-dev-launch`.
   - Bind click event to `btn-bernie-dev-launch` to reload by constructing `urlParams` with `bernie_review=live` and redirecting.
4. **Test Writing**: Add test cases to `review/test_diary_smoke.py` checking:
   - Hidden by default.
   - Visible when `bernie_dev_review=true` query is set.
   - Successful navigation/reload to `bernie_review=live` upon click.
5. **Verify Suite**: Run pytest suite locally via `.venv\Scripts\pytest review/test_diary_smoke.py` to ensure everything compiles and runs correctly.

## Visual / Behavioural Acceptance Checks

- **Acceptance 1**: Opening `/diary/diary.html` without parameters renders no button.
- **Acceptance 2**: Opening `/diary/diary.html?bernie_dev_review=true` renders the `"🤖 Dev Bernie Review"` button in the toolbar. No supervised booking panel is loaded.
- **Acceptance 3**: Clicking `"🤖 Dev Bernie Review"` successfully redirects the page, loading the supervised review panel sidebar containing blocks/candidates.
- **Acceptance 4**: The confirm button inside the panel remains disabled until the staff checkbox is ticked.

## Risks / Ambiguities

- **Query Param Preservation**: Need to make sure other URL query variables (like `smoke`, `practitioner_id`, `patient_id`, etc.) are preserved cleanly during reload.
- **Asset Caching**: Handled by bumping cache-bust version strings.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

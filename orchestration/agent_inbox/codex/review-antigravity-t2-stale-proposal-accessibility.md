# Review: Antigravity T2.2 - Stale Proposal Accessibility

## 1. Evidence Tier
- **Tier 1 (Authoritative UI Contract)**: Full route-intercepted Playwright test execution within the local offline diary smoke harness.

## 2. State & Assertion Matrix

| Target State | View Model Trigger Attributes | Rendered Copy (Status / Headline / Action / Alerts) | State Marker (CSS Class on Status Badge) | Focus / Live-Region Behavior | Exposed Keyboard Actions | Confirm Allowed? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stale** | `confirmation_state: "stale"`, `freshness_state: "stale"`, `show_stale_warning: true` | `"Stale"` / `"Review this appointment"` / `"This proposal is stale and must be refreshed."` / `"This proposal needs to be refreshed before it can be confirmed."` | `stale` | Badge role `"status"`, `aria-live="polite"`, focused automatically after transition. | Retry button (`bernie-retry-button`), Edit request button (`bernie-edit-button`) returning focus to input textarea. | **No** (confirm button absent, no confirm requests allowed). |
| **Failed** | `confirmation_state: "failed"` | `"Failed"` / `"Review this appointment"` / `"Confirmation failed due to a backend error."` | `failed` | Badge role `"status"`, `aria-live="polite"`, focused automatically after transition. | Retry button (`bernie-retry-button`), Edit request button (`bernie-edit-button`) returning focus to input textarea. | **No** (confirm button absent, no confirm requests allowed). |
| **Confirmation Pending** | `confirmation_state: "pressed"` or `"awaiting_backend"` | `"Confirmation Pending"` / `"Review this appointment"` / `"Awaiting confirmation response from backend..."` | `confirmation_pending` | Badge role `"status"`, `aria-live="polite"`, focused automatically after transition. | None. Recovery buttons are hidden; input field and submit button can be reached but no confirm retry is possible. | **No** (confirm button absent, no confirm requests allowed). |

## 3. Environment & Browser Configuration
- **Browser**: Chromium (headless) via Playwright Sync API
- **Harness**: Served from `docs/` using the local python-based static server and stubbed `office.js` context

## 4. Test Results
All 3 new tests in `review/test_diary_stale_proposal_accessibility.py` and 3 existing tests in `review/test_diary_outcome_accessibility.py` passed:
- `test_outcome_stale_accessibility`: **PASSED**
- `test_outcome_failed_accessibility`: **PASSED**
- `test_outcome_pending_accessibility`: **PASSED**
- `test_outcome_no_slots_accessibility`: **PASSED**
- `test_outcome_roster_unavailable_accessibility`: **PASSED**
- `test_outcome_clarification_accessibility`: **PASSED**

## 5. Product Gaps / Findings
- **Fallback Status Copy**: Because the static mapping `BERNIE_STATUS_COPY` does not define exact overrides for `stale`, `failed`, or `confirmation_pending`, the runtime falls back cleanly to formatting the transition state name using `formatBernieCode(status)`. This works perfectly, yielding `"Stale"`, `"Failed"`, and `"Confirmation Pending"`.
- **Keyboard Recovery Behavior**: In the stale and failed states, retry and edit controls are correctly appended and positioned in tab index sequence, and clicking/pressing Enter on "Edit request" shifts focus back into the input textarea as required. Clicking "Try again" correctly resets the review panel state.
- **Focus Management**: The client code handles focus movement correctly by focusing `[data-testid='bernie-review-status']` with a timeout of 75ms after the async transition, which makes the updated status readable by screen readers via `role="status"` and `aria-live="polite"`.

## 6. Candidate Commit Resolution
Staged and committed a single candidate commit:
- **Commit message**: `review: add focused stale, failed, and pending proposal accessibility tests`
- **File created**: `review/test_diary_stale_proposal_accessibility.py`

## 7. Boundaries & Rules Preserved
- No product HTML, JS, or CSS files were modified in `docs/diary/`.
- No modifications to backend tests, schemas, migrations, or database files.
- The worktree `C:\Users\sarashera\EMR4-worktrees\antigravity-t2-stale-proposal-accessibility` and branch `antigravity/t2-stale-proposal-accessibility` were verified and strictly followed.
- No push or master integration was performed.

STATUS: complete

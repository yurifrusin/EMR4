# codex-sprint-r12-deepseek-reason-code-ui-smoke-tests — Implementation Plan

## Protocol Status

| Item | Value |
|---|---|
| Worker | DeepSeek Flash (Shen) |
| Worktree | deepseek-sprint-r12-reason-code-ui-smoke-tests |
| Branch | codex/sprint-r12-reason-code-ui-smoke-tests |
| Gate | Plan only - NOT implemented yet |
| Python available | No - sandbox does not expose Python; agent_worktrees.py cannot run |
| Plan artifact | Written directly to orchestration/agent_inbox/codex/ per packet fallback |

## 1. My Understanding

Sprint R11 delivered the nullable status_reason_code backend substrate:
- Alembic migration adding nullable status_reason_code columns to appointments and appointment_audit_log
- Shared STATUS_REASON_CODES allow-list (13 codes) + validate_status_reason_code() in app/schemas/appointments.py
- Backend route threading: raw PATCH /status, status proposal/confirm, delete proposal/confirm all accept and persist the code
- Backend test suite: tests/test_reason_code_backend.py (9 tests covering valid-code persistence, invalid-code rejection, null compatibility, audit propagation, delete+free-text coexistence, past-date exemptions)
- Still absent: first-party Diary UI dropdown/warning flow and deterministic UI smoke tests

Sprint R12 needs deterministic UI/API smoke tests that verify the R12 Diary reason-code UI controls without a running backend, live Office, or Gemini - using the same offline Playwright/pytest pattern already ratified in review/test_diary_smoke.py.

## 2. Intended Surface / Boundary

| Surface | Included? |
|---|---|
| Diary delete-confirm/status-change reason-code dropdown (docs/diary/diary.html + diary.js) | Yes - test selectors, values, no-default, blocking behaviour, optional note field |
| Existing review/test_diary_smoke.py + harness.py + checks_diary.json | Yes - extend with reason-code check data and test functions |
| Backend reason-code smoke route (status/delete proposal/confirm payloads) | Yes - lightweight HTTP-level check via Playwright route interception or direct API call |
| Diary flow panel / flow cards (existing flow-card-cancellation-reason selector) | No - already covered by existing smoke checks |
| Diary grid rendering (appointment blocks, lifecycle colours, breaks) | No - existing checks cover this |
| Taskpane UI, Word add-in, GitHub Pages deployment, live Gemini | No - out of scope |
| Backend schema/routes/migration changes | No - R11 delivered these |
| Broad screenshot or visual regression | No - structural assertions only |

## 3. Out of Scope

- Production UI implementation of the reason-code dropdown
- Backend schema changes, new routes, or migration
- Broad screenshot/snapshot review
- Live Office/GitHub Pages/Gemini/Vertex calls
- Flow panel or grid rendering changes

## 4. Files Expected To Edit (after plan approval)

| File | Change |
|---|---|
| review/reason_code_checks.json | New. Data-driven check definitions for reason-code controls (dropdown presence, no-default, option values, note field, privacy warning, confirm blocking) |
| review/test_diary_smoke.py | Add parametrized test functions that run reason_code_checks.json through the existing harness.run_check() pattern. Add focused smoke-mode test for reason-code route interception. |
| review/harness.py | Possibly add new primitives if needed (assert_selected_value, assert_disabled, assert_input_value, assert_element_visible) |
| docs/diary/diary.html + docs/diary/diary.js | Only to add data-testid attributes to the R12 reason-code dropdown/note/confirm controls if the UI implementation sprint hasn't already added them. Minimal, non-behavioural. |
| review/README.md | Document reason-code checks section |
| .github/workflows/ui-review.yml | Include reason_code_checks.json in the CI run |

## 5. Implementation Steps

### Step 1 - Verify reason-code UI controls have stable data-testid attributes
Check the diary implementation sprint rendered the reason-code controls with test-friendly selectors. If not present (e.g. [data-testid=reason-code-dropdown], [data-testid=reason-code-note], [data-testid=btn-reason-code-confirm]), add them - but ONLY the testid attributes, not behavioural logic.

### Step 2 - Create review/reason_code_checks.json
- No-default check: verify dropdown exists and selected value is empty or placeholder
- Option-count check: verify 12+ reason-code options present (excluding LEGACY_UNCLASSIFIED)
- Specific-code check: verify PATIENT_CANCELLED, DID_NOT_ATTEND, OTHER exist as options
- Note-field check: verify text input exists with maxlength <= 150
- Privacy-warning check: verify privacy admonition text is rendered
- Confirm-blocked check: verify confirm button is disabled when dropdown is at placeholder/default

### Step 3 - Add harness primitives (if needed)
- assert_selected_value(page, selector, expected_value) - verifies a select has a specific selected option
- assert_disabled(page, selector, expected_disabled) - verifies a control disabled state
- assert_input_value(page, selector, expected_value) - verifies input/textarea value
- assert_element_visible(page, selector) - returns visible check result

### Step 4 - Add focused smoke test functions in test_diary_smoke.py
- test_reason_code_dropdown_no_default - smoke mode, reason-code dropdown shows placeholder, confirm button disabled
- test_reason_code_supplied_payload - intercept status proposal route, inject status_reason_code, verify request payload carries it
- test_reason_code_note_affordance - smoke mode, note input exists, maxlength wired, privacy warning visible
- test_reason_code_contextual_filtered_options (stretch) - verify future-cancel mode only shows patient/clinic/admin codes, not DNA/LEFT_WITHOUT_SEEN

### Step 5 - Run verification
- pytest review/test_diary_smoke.py -q --tb=short -k reason_code
- Confirm all existing non-reason-code checks still pass (no regression)
- node --check docs/diary/diary.js (if diary.js was touched)
- git diff --check

### Step 6 - Update review/README.md and .github/workflows/ui-review.yml

## 6. Visual / Behavioural Acceptance Checks

| # | Check Name | Type | Expected | How Verified |
|---|---|---|---|---|
| 1 | reason_code_dropdown_present | count | [data-testid=reason-code-dropdown] exists | Playwright page.locator(sel).count() == 1 |
| 2 | reason_code_no_default | selected_value | Dropdown starts at empty or placeholder text | assert_selected_value returns empty/placeholder |
| 3 | reason_code_options_count | count | >= 12 option elements | page.locator('#reason-code-select option').count() >= 12 |
| 4 | reason_code_patient_cancelled_present | text_count | Option PATIENT_CANCELLED exists | page.locator('option[value=PATIENT_CANCELLED]').count() == 1 |
| 5 | reason_code_note_field_present | count | Text input for admin note visible | page.locator('[data-testid=reason-code-note]').count() == 1 |
| 6 | reason_code_note_maxlength | attribute | maxlength attribute <= 150 | getAttribute('maxlength') value |
| 7 | reason_code_privacy_warning_present | text_count | Privacy admonition text rendered | page locator or text match |
| 8 | reason_code_confirm_blocked_without_selection | disabled | Confirm button disabled when no reason selected | page.locator(sel).is_disabled() == true |
| 9 | reason_code_confirm_enabled_after_selection | enabled | Confirm button enabled after selecting a reason | Select an option, then check is_disabled() == false |
| 10 | reason_code_supplied_payload_status | route_intercept | Status proposal payload includes status_reason_code | Route-intercept the fetch, verify JSON body field |
| 11 | reason_code_supplied_payload_delete | route_intercept | Delete proposal payload includes status_reason_code | Route-intercept the fetch, verify JSON body field |
| 12 | reason_code_legacy_absent_in_flow | text_count | Legacy free-text cancellation_reason still renders in flow cards | Existing flow-card-cancellation-reason coverage preserved |

## 7. Risks / Ambiguities

| Risk | Mitigation |
|---|---|
| Reason-code UI may not exist yet - the task says plan then add smoke coverage but the R12 Diary UI dropdown may not have been implemented yet | The plan is forward-looking. If controls don't exist, tests skip with clear pytest skip message pointing to missing data-testid. |
| data-testid attributes may not be stable - UI implementation may not add test hooks | Step 1 checks for data-testid presence and adds them as minimal non-behavioural change. Fall back to DOM structural selectors. |
| Route interception may not work in smoke-mode - smoke mode uses embedded fixtures | Use page.route() to intercept fetch(s) that would hit real backend. Existing harness already uses this for interpret-booking-instruction. |
| Backend tests already exist in test_reason_code_backend.py | These smoke tests are complementary: verify UI sends the right payload, not that backend processes it correctly. No overlap. |
| Multiple reason-code dialogs - separate dialogs for cancel vs status change | Tests must target each dialog independently with its own selectors. Define separate check groups. |
| Contextual filtering may not exist in R12 | Don't test contextual filtering in first pass. Add as stretch goal only after confirming it's implemented. |
| Privacy warning copy may differ from R11 spec | Use data-testid for warning container rather than fragile text matching. |

## 8. Verification Plan

`
pytest review/test_diary_smoke.py -q --tb=short -k reason_code --junitxml=review/reason-code-review.xml
pytest review/test_diary_smoke.py -q --tb=short --junitxml=review/diary-review.xml
node --check docs/diary/diary.js
git diff --check
`

Expected: all reason-code tests pass; all existing diary smoke tests pass; JS syntax clean.

## 9. Merge Criteria

- Reason-code smoke tests are deterministic and pass
- Existing diary smoke tests are not regressed
- Fewer than 5 lines of non-testid change to docs/diary/diary.{html,js}
- No backend schema/route/migration changes
- No live Office/GitHub Pages/Gemini dependencies in test path
- pytest JUnit XML output is stable and actionable

## Codex Plan Review

- Review result: Accepted with amendments. Tests should follow the selectors and flow implemented by the UI lane; avoid skip-based final tests where possible; do not edit production UI except minimal `data-testid` hooks if Ariadne approves during integration.
- Required changes before implementation: See review result amendments.
- Approved to proceed: yes

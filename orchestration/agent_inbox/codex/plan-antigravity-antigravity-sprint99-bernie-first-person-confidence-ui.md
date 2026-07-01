# plan-antigravity-antigravity-sprint99-bernie-first-person-confidence-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint99-bernie-first-person-confidence-ui` |
| Status | pending_plan_review |
| Created | 2026-07-01 17:08:53+10:00 |
| Source HEAD | `0ffeb20` |

## Plan Summary

Establish a calm, receptionist-focused Bernie UI response layer that maps backend booking confidence fields and flags to clear first-person copy states, leverages HTML `<details>` elements for toggleable evidence disclosure, gates/suppresses diary grid previews to avoid loop fights, and implements a comprehensive suite of route-intercepted smoke tests.

## My Understanding

We are tasked with building the frontend UI logic for confidence-aware booking in the Bernie "Command Center" SPA panel. This involves parsing the backend contract (`BernieStaffReviewPayload`, `BerniePatientEvidence`, `BerniePractitionerEvidence`) and dynamically displaying appropriate receptionist copy and controls.

### 1. Confidence Mapping & Decision Bands
We map backend confidence axes (`patient_evidence.confidence` and issue codes under `warnings`/`blocks`) to distinct UI behaviors:
* **High/Medium Confidence (No Warning)**: Displays confirmation-ready state with a collapsed `<details>` panel. Auto-previews the selected slot on the diary grid.
* **Assumed/Inferred Fields (Medium Confidence)**: Displays first-person explanation notices for inferred date or location.
* **Low/Ambiguous Confidence**: Displays expanded details, candidate list/search box, and warns the receptionist to double-check matching fields.
* **Blocked**: Disables the confirm action and displays a list of required/missing fields mapped to friendly first-person requests.

### 2. Copy States (First-Person Assistant Phrasing)
We will define exact copy strings for these scenarios:
* **Assumed Date**: `"I've assumed today for the booking date since you didn't mention a date."`
* **Practitioner Typo**: `"Do you mean Dr. {Resolved Name} (for your entry '{Typo Name}')?"`
* **Patient Ambiguity**: `"I found multiple patients matching '{Search Text}'. Please select the correct patient."`
* **Low Confidence**: `"I'm not sure about some details. Could you please double-check the booking details below?"`
* **Block**: `"I can't proceed with this booking because {Friendly Reason}."` (e.g. `"please select a practitioner"` instead of `"missing_practitioner_id"`).
* **Confirmation-Ready**: `"I've prepared the booking for {Patient Name} with Dr. {Practitioner Name} at {Time} on {Date}. Would you like to confirm?"`

### 3. Details Panel Disclosure Rules
* The patient and practitioner evidence elements will be wrapped in an HTML `<details>` block with `data-testid="bernie-evidence-details"`.
* **Default Collapsed** (no `open` attribute) when `patient_evidence.confidence` is `high` or `medium` and no verification alerts exist.
* **Default Expanded** (`open` attribute set) when `patient_evidence.confidence` is `low` or `ambiguous`, or if `identity_evidence.verification_status` is `"requires_staff_verification"`, or if `warnings` lists a corrected typo or assumed date.

### 4. Auto-Preview Gating and Suppression
* **Gating**: When `status` is `confirmation_ready` or a candidate is staged and `suppressAutoPreview` is `false`, render a dashed/dotted provisional preview card on the diary grid at the target date, column, and time.
* **Suppression**: Local UI state will maintain a `suppressAutoPreview` boolean. When the user clicks `"Choose another time"` or clicks/drags to manually select another slot on the grid, set `suppressAutoPreview = true`. This prevents the automated preview from overriding user decisions. Reset the flag to `false` only on submitting a new natural language instruction.

## Intended Surface / Boundary

* **Affected**: Bernie supervised review panel rendering within `docs/diary/diary.js`, CSS rules for the details disclosure container and preview cards in `docs/diary/diary.css`, and test scenarios in `review/test_diary_smoke.py`.
* **Boundary**: No modification to underlying diary grid selection logic (other than setting the suppression flag), waiting room tab panels, backend DB schemas, or standard booking modals. Nearby surfaces must remain unchanged.

## Out Of Scope

* Modifying database tables or writing backend Python endpoints.
* Bypassing human staff confirmation (this remains a required gate).
* Displaying raw code blocks, debug stacks, or snake_case technical error codes in ordinary mode.

## Files I Expect To Edit

* `docs/diary/diary.js` — Review UI rendering logic, event listeners, copy states, auto-preview trigger, and details element generation.
* `docs/diary/diary.css` — Styling rules for the new `<details>` disclosures, first-person warnings, and dotted/provisional preview cards.
* `docs/diary/diary.html` — Statically declared template nodes or cache-busting version parameters if required.
* `review/test_diary_smoke.py` — Addition of route-intercepted integration tests.

## Implementation Steps

1. **Aesthetics & Styling**: Add CSS classes in `docs/diary/diary.css` for details panels, summaries, highlighted verification warnings, and the dotted-border provisional slot preview.
2. **Details Disclosure**: Integrate HTML `<details>` and `<summary>` in `renderBernieIdentityEvidence` (`docs/diary/diary.js`). Implement the auto-expansion rules based on the confidence fields.
3. **Copy Translation**: Modify `bernieHeadlineCopy`, `bernieStatusCopy`, `bernieReviewActionCopy` (and introduce helper copy mapping) to return clean first-person copy, stripping snake_case text, and mapping internal codes to friendly receptionist alerts.
4. **Auto-Preview & Loop Suppression**: Update `renderBernieReview` to stage the preview card on the grid. Inject the `suppressAutoPreview` state tracking, binding it to the `"Choose another time"` button event listener and grid manual-click/drag events.
5. **Testing Harness**: Add the suite of nine route-intercepted test cases inside `review/test_diary_smoke.py`.

## Visual / Behavioural Acceptance Checks

We will verify implementation using deterministic route-intercepted Playwright tests:
1. **Inferred Today**: Mock warning code `date_inferred_today`. Verify first-person warning notice renders and the provisional slot is rendered on the grid.
2. **No-Reference Date Clarification**: Mock missing date block. Verify first-person date prompt displays.
3. **Practitioner Typo**: Mock `practitioner_typo_resolved`. Verify "Do you mean Dr. {Resolved Name}..." is visible.
4. **Patient Candidate Ambiguity**: Mock `confidence: "ambiguous"` with candidates. Verify first-person list choice prompt and candidate items render.
5. **Details Toggle**: Verify `<details>` is collapsed for high confidence, and open for low/ambiguous confidence. Clicking summaries correctly toggles the open attribute.
6. **Raw Code Exclusion**: Scan flow panel text; assert no snake_case internal fields or raw codes are rendered in ordinary mode.
7. **No Write Before Confirm**: Assert `/confirm-bernie` endpoint is never hit until Confirm is clicked.
8. **Choose Another Time Suppression**: Assert clicking `"Choose another time"` removes the provisional preview card and prevents subsequent auto-previews from refiring.
9. **Asset Version Checks**: Parse HTML files to ensure that scripts and style assets are loaded with cache-busting hash/version query parameters.

## Risks / Ambiguities

* **Cache Busting**: Ensure the browser loads the modified `diary.js`/`diary.css` assets without relying on old cached copies.
* **Contract Sync**: Keep frontend parser resilient: fallback safely to standard labels if optional evidence schema properties (such as `masked_phone` or `provider_number`) are null.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

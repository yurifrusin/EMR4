# plan-antigravity-antigravity-bernie-selected-instruction-affordance

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-selected-instruction-affordance` |
| Status | pending_plan_review |
| Created | 2026-06-28 00:31 +1000 |
| Source HEAD | `472dde6` |

## Plan Summary

Suggested instruction chips when linked context imported

## My Understanding

The goal is to improve the staff-visible Bernie pilot instruction input UI in `docs/diary/` (the Supervised Booking Review panel) when it is launched using context imported from a selected appointment.
When an active, linked appointment context is loaded (i.e. `showSelectedAppt` is true in `renderBernieInstructionInput` or `berniePilotContext.sourceAppointmentId` matches the currently selected active appointment), we want to show safe, bounded suggested instruction affordances (chips/buttons) for common staff booking requests under the textarea.
These affordances should populate the textarea when clicked, but MUST NOT automatically submit the instruction or trigger the provider call (preserving explicit staff submit and confirmation gates).
It must also preserve the stale-selection guard, keep the allowlist gate, have no manual IDs in ordinary mode, preserve the explicit approval checkbox, and we must perform an asset version bump in `docs/diary/diary.js` and `docs/diary/diary.html` (e.g. `?v=...`) if runtime assets change.

## Intended Surface / Boundary

- **Affected Surface**: Inside the `#bernie-review-panel` sidebar panel. Specifically, inside `#bernie-instruction-container` under the `textarea#bernie-instruction-input` element and above the submit button `#btn-bernie-instruction-submit`. We will add a small flex container `#bernie-suggested-instructions` with class `bernie-suggested-instructions` containing suggestion chip buttons (e.g. buttons with class `bernie-suggestion-chip`).
- **Nearby Surfaces (Unchanged)**:
  - The main diary grid, appointment cards/slots, the waiting room section, the patient flow workbench, and the status controls.
  - The dev review tools dropdown/selector and help box.
  - The main patient search and practitioner context inputs.
  - The confirmation review UI itself (once interpreted, the review payload layout and inputs must remain unchanged, except that the instruction input remains editable/submittable at the top).

## Out Of Scope

- Backend changes (routes, schemas, models, Alembic migrations).
- Gemini API or LLM call changes/provider modifications.
- Fully autonomous scheduling (the workflow must remain supervised by a staff member).
- URL or localStorage/sessionStorage persistence for instructions/context.
- Unrelated CSS/JS refactoring.

## Files I Expect To Edit

- [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js) (to add the suggestion chips rendering code inside `renderBernieInstructionInput`, update the asset version metadata if needed).
- [diary.html](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.html) (if any static element or version reference is updated, otherwise just JS/CSS).
- [diary.css](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.css) (to style the suggested instruction chips/container so it looks modern, clean, aligned with the design systems, with hover state and subtle transition).
- [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) (to add a test verifying that when a selected appointment context is active, the suggestion chips are visible, clicking a chip populates the textarea, and does not submit automatically).

## Implementation Steps

1. **Diary CSS Changes**:
   - Add `.bernie-suggested-instructions` styling (e.g. flex container, flex-wrap, gap, margin).
   - Add `.bernie-suggestion-chip` styling (e.g. small modern pill buttons, subtle borders, Outfit/Inter typography, transition on hover/active, modern color palette like HSL tailored gray/blue, pointer cursor).
2. **Diary JS Changes**:
   - Update `renderBernieInstructionInput`:
     - If `showSelectedAppt` is true, define an array of suggestion objects (e.g. `{ label: "Follow-up 1wk", text: "Book follow-up in 1 week" }`, `{ label: "Follow-up 2wk", text: "Book follow-up in 2 weeks" }`, `{ label: "Reschedule next week", text: "Reschedule appointment to next week" }`).
     - Create a container element `div` with id/class `bernie-suggested-instructions`.
     - For each suggestion, create a `button` with class `bernie-suggestion-chip` and custom test-id attributes, set its `textContent` to the label (or text), and add a `click` listener that sets `textarea.value = suggestion.text` and updates `bernieInstructionText = suggestion.text` (optionally).
     - Append the suggestion chips container after the textarea but before the submit button.
   - Bump asset versions if needed.
3. **Smoke Test Verification**:
   - Add a pytest test case in `review/test_diary_smoke.py` that loads the page with active appointment context, verifies suggestions container exists, clicks a chip, asserts the textarea contains the expected instruction text, and verifies that the submit state is not automatically triggered.

## Visual / Behavioural Acceptance Checks

- Open the diary with `?smoke=true&bernie_review=...` and verify:
  - If no appointment is selected, the chips are NOT displayed (context not imported).
  - If a linked appointment is selected, the chips are visible below the instruction input.
  - Clicking a chip populates the input textarea with the appropriate instruction copy.
  - The form is not submitted upon click (it still requires clicking "Submit Instruction for Review").
  - The layout of adjacent elements is unaffected.

## Risks / Ambiguities

- **Risk**: Ensuring the stale-selection guard still invalidates the context or handles updates cleanly if the user changes the active selection after clicking a chip.
  - *Mitigation*: The current `resolveBerniePilotLaunchRequest` checks active selected appointment and blocks with `stale_selected_appointment_context` if it changes, which is preserved.
- **Risk**: Overcrowding the narrow Supervised Booking Review panel with chip buttons.
  - *Mitigation*: Use a wrap layout, small text/padding, and clear labeling, keeping it concise.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

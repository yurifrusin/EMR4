# plan-antigravity-antigravity-sprint104-bernie-chat-state-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint104-bernie-chat-state-ui` |
| Status | pending_plan_review |
| Created | 2026-07-02 15:30 +1000 |
| Source HEAD | `e6031d7` |

## Plan Summary

Transition the Bernie receptionist assistant from a single-turn search tool to a stateful conversational workflow with turn memory, stale-state management, and clear visual boundaries.

## My Understanding

- **Multi-turn Chat & Clarification**: The input text box should act as a messaging prompt. Instead of retaining the submitted prompt indefinitely, it must clear on submission. A scrollable transcript of user prompts and Bernie's responses (clarifications, results, status alerts) should be rendered above the input area.
- **Stale-State Management**: Clicking Today, Prev, Next, changing dates via the date picker, or hitting Refresh makes any current unconfirmed candidate snapshot or staged preview invalid. The UI must clear this state to avoid displaying stale slots on the newly navigated day.
- **No-Slot & Suggestion Handling**: If no slots are found (`candidate_slots: []`), instead of rendering a generic empty list, Bernie must output a direct, receptionist-friendly notification in first-person copy, accompanied by clickable recommendation chips (e.g., "Try Friday instead", "Check next Monday") that populate the box and submit automatically.
- **Provisional Preview Boundary**: Auto-previewed slots are provisional and must be visually distinguishable from selected slots. We will apply a dashed purple border style and add a "PROVISIONAL PREVIEW" badge on the grid card. A toggle switch in the Bernie panel will allow the receptionist to enable/disable auto-previews (`suppressAutoPreview`).

## Intended Surface / Boundary

- **In Scope**:
  - `docs/diary/diary.js`: Logic for session state tracking, transcript formatting, clearing prompt inputs, date/refresh event handlers, no-slot suggestions, and the auto-preview toggle.
  - `docs/diary/diary.html`: Layout elements for the scrollable chat transcript and auto-preview toggle checkbox.
  - `docs/diary/diary.css`: Styles for chat bubbles (user/assistant alignment), suggestion chips, and the `.bernie-staged-booking-card.provisional` card badge.
  - `review/test_diary_smoke.py`: Addition of automated smoke tests verifying the state machine transitions and UI feedback under mocked endpoints.
- **Out of Scope**:
  - Modifying backend scheduling engines or writing appointments to the DB.
  - Redesigning the core diary grid, patient search modals, or other practitioner schedules.
  - Using XState or any other heavy state-management libraries.

## Out Of Scope

- Backend implementation except consuming planned contract fields.
- Broad diary redesign.
- XState/runtime dependency.
- Exposing sensitive identifiers by default.

## Files I Expect To Edit

- `docs/diary/diary.js`
- `docs/diary/diary.html`
- `docs/diary/diary.css`
- `review/test_diary_smoke.py`

## Implementation Steps

1. **Extend `BernieSession` state management**: Add `sessionId` (generated as a random UUID upon initialization/reset) and `turns` (array of `{ actor: "staff" | "bernie", text: string }`) to track conversational history. Update `reset()` and `clearResponse()`.
2. **Implement scrollable Chat Transcript area**: Update `docs/diary/diary.html` to introduce `<div id="bernie-chat-transcript" class="bernie-transcript-container" data-testid="bernie-chat-transcript"></div>` inside `#bernie-review-panel`. Add CSS styles for bubbles.
3. **Multi-turn input submission**: Clear prompt entry text area on submission and update `/appointments/proposals/bernie/interpret-booking-instruction` call payload to include `session_id` and prior `turns`.
4. **Invalidate stale state on date change or manual refresh**: Hook into navigation actions in `Office.onReady()` (`btn-prev-day`, `btn-next-day`, `btn-today`, `btn-now`, `diary-date-picker`, and `btn-refresh`) to clear response and staged proposal.
5. **Suggestion chips for No-Slots responses**: Render direct copy and button chips styled `.bernie-suggestion-chip` when `candidate_slots` is empty. Register click handlers to auto-fill and submit.
6. **Visual boundary for provisional cards & Toggle Switch**: In `renderBernieStagedBookingPreview()`, if `preview.isProvisional` is true, apply class `.provisional` and prepend a badge. Add a checkbox toggle for auto-preview.
7. **Write Smoke Tests**: Add new test cases in `review/test_diary_smoke.py` verifying chat input, stale state clearing, no-slot suggestion clicks, and auto-preview boundary behaviors.

## Visual / Behavioural Acceptance Checks

- **Chat interface validation**: Submit a search -> verify input area goes blank, the text box retains focus, and the prompt text is added to the scrollable transcript container.
- **Stale status cleanup**: Prepare a proposal -> click "Next Day" -> verify the proposal disappears from the grid and the Bernie panel returns to its prompt input state.
- **No-slot recommendations**: Mock an empty slot response with suggestion chips -> verify assistant message renders first-person copy, chips display, and clicking one triggers a new search.
- **Provisional preview boundary**: Auto-stage a best candidate -> verify it displays with a dashed boundary and a "PROVISIONAL PREVIEW" badge on the diary grid. Uncheck the "Auto-preview" box -> verify the provisional card disappears immediately.

## Risks / Ambiguities

- **Scroll management**: Capping transcript container size and forcing scroll-to-bottom.
- **Navigation during multi-turn state**: Navigation will clear transcript to maintain alignment.


## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

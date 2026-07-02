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
- **Stale-State Management**: Clicking Today, Prev, Next, changing dates via the date picker, or hitting Refresh makes any current unconfirmed candidate snapshot or staged preview invalid. The UI must clear or mark candidate/proposal/response state as stale, but MUST preserve the Bernie chat transcript/turn history to keep conversational context intact unless the user explicitly starts a new Bernie session (e.g. by clicking a dedicated "New Session" or clear button).
- **No-Slot & Suggestion Handling**: If no slots are found (`candidate_slots: []`), instead of rendering a generic empty list, Bernie must output a direct, receptionist-friendly notification in first-person copy, accompanied by clickable recommendation chips (e.g., "Try Friday instead", "Check next Monday") that populate the box and submit automatically.
- **Provisional Preview Boundary**: Auto-previewed slots are provisional and must be visually distinguishable from selected slots. We will reuse the existing `.bernie-staged-booking-card.provisional` class (which already has a dashed purple border style). We will not add loud purple visual badges or styling; any text helper/badge will use restrained, grey/neutral design tokens.
- **Auto-Preview Toggle**: A toggle switch in the Bernie panel will control auto-previews, aligning its semantics with the existing ordinary-mode `bernie_auto_preview` setting/URL param rather than using a reversed `suppressAutoPreview` logic.

## Intended Surface / Boundary

- **In Scope**:
  - `docs/diary/diary.js`: Logic for session state tracking (preserving transcript/turn history on navigation/refresh, resetting only on explicit new session), date/refresh event handlers, no-slot suggestions, and the `bernie_auto_preview` positive-logic toggle.
  - `docs/diary/diary.html`: Layout elements for the scrollable chat transcript, explicit "New Session" control, and the positive-logic `bernie_auto_preview` toggle.
  - `docs/diary/diary.css`: Styles for chat bubbles (user/assistant alignment), suggestion chips, and restrained grid preview styles utilizing existing grey/neutral tokens and reusing `.bernie-staged-booking-card.provisional`. No new loud purple styles.
  - `review/test_diary_smoke.py`: Addition of automated smoke tests verifying state machine transitions, preserved history across navigation, positive-logic auto-preview toggle, and UI feedback under mocked endpoints.
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

1. **Extend `BernieSession` state management**: Add `sessionId` (generated as a random UUID upon initialization) and `turns` (array of `{ actor: "staff" | "bernie", text: string }`) to track conversational history. Retain these across navigation and refreshes, only clearing them when the user explicitly triggers a new session (e.g. clicking a "New Session" action in the panel).
2. **Implement scrollable Chat Transcript area**: Update `docs/diary/diary.html` to introduce `<div id="bernie-chat-transcript" class="bernie-transcript-container" data-testid="bernie-chat-transcript"></div>` inside `#bernie-review-panel`, along with an explicit "New Session" button. Add CSS styles for bubbles.
3. **Multi-turn input submission**: Clear prompt entry text area on submission and update `/appointments/proposals/bernie/interpret-booking-instruction` call payload to include `session_id` and prior `turns`.
4. **Invalidate stale state on date change or manual refresh**: Hook into navigation actions in `Office.onReady()` (`btn-prev-day`, `btn-next-day`, `btn-today`, `btn-now`, `diary-date-picker`, and `btn-refresh`) to clear response, candidates, and staged proposal previews. Ensure this does NOT clear the active `sessionId`, `turns`, or chat transcript.
5. **Suggestion chips for No-Slots responses**: Render direct copy and button chips styled `.bernie-suggestion-chip` when `candidate_slots` is empty. Register click handlers to auto-fill and submit.
6. **Visual boundary for provisional cards & Toggle Switch**: In `renderBernieStagedBookingPreview()`, if the preview is provisional, apply the existing `.bernie-staged-booking-card.provisional` class. Implement a checkbox toggle for auto-preview that directly controls the `bernie_auto_preview` positive-logic flag. Avoid introducing new loud purple visual language or badges; use restrained, existing design tokens and neutral classes for any text helpers on the grid card.
7. **Write Smoke Tests**: Add new test cases in `review/test_diary_smoke.py` verifying chat input, preserved history across navigation, stale candidate/staged proposal clearing, no-slot suggestion clicks, and positive-logic auto-preview toggle behaviors.

## Visual / Behavioural Acceptance Checks

- **Chat interface validation**: Submit a search -> verify input area goes blank, the text box retains focus, and the prompt text is added to the scrollable transcript container.
- **Stale status cleanup**: Prepare a proposal -> click "Next Day" -> verify the proposal disappears from the grid, the candidates/response are cleared/marked stale, but the chat transcript and turn history are fully preserved.
- **New session action**: Click the "New Session" button -> verify the chat transcript and turn history are cleared and a new `sessionId` is generated.
- **No-slot recommendations**: Mock an empty slot response with suggestion chips -> verify assistant message renders first-person copy, chips display, and clicking one triggers a new search.
- **Provisional preview boundary**: Auto-stage a best candidate -> verify it displays with the existing dashed boundary (`.bernie-staged-booking-card.provisional`) on the diary grid. Verify any visual labels are in a restrained, neutral style matching the existing design. Uncheck the positive-logic "Auto-preview" toggle -> verify the provisional card disappears immediately, and subsequent interpretations do not auto-preview unless re-enabled.

## Risks / Ambiguities

- **Scroll management**: Capping transcript container size and forcing scroll-to-bottom.
- **Transcript context alignment**: When navigating dates, the transcript is preserved. We should ensure the backend interpret call handles date-relative instructions properly using the current navigated date rather than assuming dates from the first turn.


## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

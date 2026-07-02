# plan-antigravity-antigravity-sprint105-bernie-typed-turn-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint105-bernie-typed-turn-ui` |
| Status | pending_plan_review |
| Created | 2026-07-02 23:34 +1000 |
| Source HEAD | `0e9438b` |

## Plan Summary

Transition the Bernie reception assistant sidebar from unstructured string turn history to a structured event-driven state log. All interactions—from initial staff instruction to candidate selection, previews, suggestions, and final confirmation—will be logged as explicit typed client events and passed to the backend API (`/interpret-booking-instruction`, `/supervised-booking`, `/confirm-bernie`) to prevent stale prose interpretations, enable backend staleness detection, and support robust multi-turn reception flows.

## My Understanding

- **Event-Driven Turns**: Instead of logging history as simple `{ actor: "staff" | "bernie", text: string }` turns, the client-side `turns` array will record a sequence of strongly-typed events, each containing a unique `id` (UUID), `timestamp`, `kind`, and `payload`.
- **Preventing Stale Prose Leakage**:
  - Suggestion chips clicked on "no-slots" results will submit a typed event (`no_slot_suggestion_click`) referencing the original turn rather than rewriting/leaking previous text prompts into the LLM.
  - Composer input will be treated strictly as a transient draft, cleared immediately upon submit.
- **Staleness Protection**:
  - The client will track stable IDs/hashes for the candidate slots returned by the backend.
  - Selecting a candidate, previewing, and confirming will send the selected candidate's stable ID/hash to the backend.
  - Refreshing or navigating dates (Refresh/Today/Prev/Next) will perform state-clearing, invalidating the current staged preview/evidence, and log a `date_navigation_clear` event so the backend blocks old stale confirmations.
- **Visual Compactness**:
  - The UI remains compact, reusing existing classes (e.g. `.bernie-staged-booking-card.provisional` for previews).
  - Clear separation between composer text and chat history.

## Intended Surface / Boundary

- **In Scope**:
  - `docs/diary/diary.js`: `BernieSession` updates for structured turns/events, client-side UUID generation for turns, event creators, updated API request payload builders for all three Bernie endpoints, date navigation event handlers, and no-slot suggestion click event dispatching.
  - `docs/diary/diary.html`: Verification of IDs, keeping DOM elements for transcript, composer, and buttons.
  - `docs/diary/diary.css`: Styles for suggestion chips, bubbles, and visual copy boundaries.
  - `review/test_diary_smoke.py`: Add Playwright test cases to verify the event-driven turn history generation, composer clearing, stale proposal clearing, suggestions, and confirmation payload evidence.
- **Out of Scope**:
  - Any backend routes, DB schema, or interpreter implementation details.
  - Modifying the clinical taskpane.
  - Modifying user identity verification logic.
  - Direct database writes or bypassing the confirmation step.

## Out Of Scope

- Redesigning the entire diary layout or structure.
- Voice recognition, audio listener, or wake-word integration.
- Medicare, HI, PVM, or OPV integration.
- Bypassing staff confirmation.

## Files I Expect To Edit

- `docs/diary/diary.js`
- `docs/diary/diary.css`
- `docs/diary/diary.html`
- `review/test_diary_smoke.py`

## Implementation Steps

1. **Define Event Types and Typescript-like Schema**:
   In `docs/diary/diary.js`, define the schemas for events (`staff_instruction`, `bernie_clarification`, `clarification_reply`, `no_slot_suggestion_click`, `candidate_selection`, `choose_another_time`, `proposal_preview`, `date_navigation_clear`, `confirmation`).
2. **Update `BernieSession` class**:
   - Update `this.turns` to store these event objects instead of plain text turns.
   - Refactor `generateSessionId` or helper to generate UUIDs for each event (`generateEventId()`).
   - Add helper methods to push events to history: `addEvent(kind, payload)`.
3. **Refactor Staff Instruction Submission**:
   - When the staff clicks submit, push a `staff_instruction` event (or `clarification_reply` if responding to a question).
   - Clear composer input immediately and focus the composer.
   - Pass the full `turns` log in the body of `POST /appointments/proposals/bernie/interpret-booking-instruction`.
4. **Refactor Candidate Selection and Preview**:
   - Selecting a candidate slot logs a `candidate_selection` event (and a `proposal_preview` event if auto-previewed or manually previewed).
   - Ensure the backend-returned candidate slot contains a stable ID/hash (e.g. `candidate_id`), which the client maps and sends in `supervised-booking`.
   - Track this `candidate_id` in `bernieSession`.
5. **Refactor Choose Another Time**:
   - Clicking "Choose another time" logs a `choose_another_time` event.
6. **Refactor No-Slot Suggestion Click**:
   - Clicking a suggestion chip creates a `no_slot_suggestion_click` event, appends it to `turns`, and triggers `/interpret-booking-instruction` directly.
7. **Refactor Date Navigation and Refresh**:
   - Hook into date navigation and refresh buttons. Clear local booking proposal, candidates, and preview states.
   - Append `date_navigation_clear` event with old/new reference dates to the session history.
8. **Refactor Confirmation**:
   - Send the confirmation event with the `candidate_id` / `confirm_payload` evidence to `/confirm-bernie`.
9. **Asset Version Strategy**:
   - Increment the asset version of `diary.js`/`diary.css` imports inside `docs/diary/diary.html` (e.g. query string version bump like `diary.js?v=105`) to prevent browser cache issues.
10. **Implement Smoke Tests**:
   - In `review/test_diary_smoke.py`, add mock interceptors for the new event-driven payloads.
   - Assert composer clearing, suggestion click, date navigation stale clearing, and confirmation evidence matching.

## Visual / Behavioural Acceptance Checks

- **Composer Clearing**: Submit instruction -> verify textarea is immediately blank and turns array has `staff_instruction`.
- **Suggestion Click**: Click suggestions chip -> verify request sent to backend contains a `no_slot_suggestion_click` turn, and text area remains blank.
- **Date Navigation Stale Clearing**: Load candidates -> click Next Day -> verify candidates and grid preview disappear, and `date_navigation_clear` event is added.
- **Candidate ID Preservation**: Select candidate -> verify candidate ID/hash is sent to `supervised-booking` and `confirm-bernie`.
- **Confirmation Payload**: Confirm -> verify POST payload to `/confirm-bernie` includes the correct `confirm_payload` from the latest backend review response.
- **Compact UI**: Verify visual styling is unchanged (no loud new components), retaining Sprint 104 receptionist panel ergonomics.

## Risks / Ambiguities

- **Dissent / Risks**:
  - Session history length could grow large if date navigation events are continuously appended. A maximum event history limit (e.g., 20-30 turns) or session-restart nudge could be planned if the backend requires it.
  - Aligning client-side UUIDs with backend expectations: we generate standard UUID v4 strings locally.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no


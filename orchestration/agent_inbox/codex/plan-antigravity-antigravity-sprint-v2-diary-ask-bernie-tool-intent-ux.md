# plan-antigravity-antigravity-sprint-v2-diary-ask-bernie-tool-intent-ux

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-v2-diary-ask-bernie-tool-intent-ux` |
| Status | integrated |
| Created | 2026-07-04 06:16 +1000 |
| Source HEAD | `0297f3a` |

## Plan Summary

Plan the visible Diary/Bernie UX for consuming V1 tool-intent proposal responses, starting with appointment extension, so staff see Bernie as a friendly professional reception copilot while deterministic backend proposal evidence owns actions.

## My Understanding

- **Sprint Goal**: Wire the V1 backend tool-intent route `/api/v1/appointments/proposals/bernie/tool-intent` into the Diary panel's composer/Ask Bernie flow.
- **Trigger Condition**: When an instruction matches `extend` or `lengthen` (case-insensitive), route the request to the tool-intent API.
- **Friendly Professional voice**: Display the `summary` from the `/tool-intent` response directly in the chat bubble of the transcript. Keep the latest turn highlighted and collapse the history.
- **Extension Proposal Review Card**:
  - Render a custom read-only proposal card showing details of the proposed extension: patient, practitioner, date, start time, current duration, and proposed duration.
  - Find the target appointment in the global `activeAppointments` array via `appointment_id` to show the current vs. proposed duration comparison.
- **Strict Invariant**: Do NOT render any "Confirm booking", "Confirm", or other mutating controls on the panel since the backend response doesn't provide confirmation evidence/payload for tool intent. Only the details of the proposal are shown.

## Intended Surface / Boundary

- **Diary Bernie Panel Sidebar** (`#bernie-review-panel`): Visual area where the chat history, request preview, and proposal card are rendered.
- **composer / Ask Bernie composer**: The composer input where instructions are written.
- **Diary Grid**: Nearby surface displaying columns and rows of appointments. Must NOT change (no provisional/staged slots rendering for read-only extensions since they don't modify the diary grid until a standard edit action is fully confirmed).

## Out Of Scope

- Backend route implementation (already done in V1).
- GraphRAG retrieval changes.
- Broad Diary grid redesign.
- Taskpane or Command Centre changes.
- Direct write controls or bypassing staff confirmation.

## Files I Expect To Edit

- `docs/diary/diary.js` (UI logic, route routing, proposal card rendering, reanchor handling)
- `docs/diary/diary.css` (Styles for `.bernie-proposal-card`, `.bernie-proposal-title`, etc.)
- `review/test_diary_smoke.py` (Playwright smoke tests for the tool-intent UI flow)

## Implementation Steps

### docs/diary/diary.js
1. Inside the composer submit button click handler:
   - Perform a regex check on the typed instruction: `const isToolIntent = /\b(extend|lengthen)\b/i.test(text);`.
   - If `isToolIntent` is true, call `POST /api/v1/appointments/proposals/bernie/tool-intent` with `instruction`, `reference_date`, and `context_frames`.
   - Otherwise, fallback to the existing `/appointments/proposals/bernie/interpret-booking-instruction` call.
2. In `loadBernieLiveReview()`:
   - Check if `bernieInterpretResult.intent === "bernie_tool_intent"`.
   - If true, call a new function `renderBernieToolIntentProposal(bernieInterpretResult)` and return early (bypassing `/supervised-booking` call).
3. Implement `renderBernieToolIntentProposal(envelope)`:
   - Clear `#bernie-review-content`.
   - Render the composer input form using `renderBernieInstructionInput()`.
   - Render the request preview using `renderBernieInterpretPreview(contentEl, envelope)`.
   - Render status badge and headline using the envelope's summary.
   - If `envelope.result === "proposal_ready"`:
     - Find the corresponding appointment in `activeAppointments` matching `envelope.proposal.command.appointment_id`.
     - Render a `.bernie-proposal-card` displaying:
       - Patient name
       - Practitioner name
       - Date and local start time
       - Current duration (e.g. 15 mins)
       - Proposed duration (e.g. 30 mins)
       - Propose/Audit evidence: "Staff-confirmed PUT only"
     - Do NOT append any confirmation box or confirmation buttons (since `confirm_payload` is missing/null).
   - If `envelope.result === "clarification_required"`, `"blocked"`, or `"unsupported"`:
     - Render the blocks/warnings detailing what is required (e.g., "Tell me the total appointment duration, for example 30 minutes.").

### docs/diary/diary.css
1. Add `.bernie-proposal-card` style rule:
   - Distinct background-color (e.g. a soft blue `#eff6ff` with a blue border `#bfdbfe` to indicate a read-only proposal, differentiating it from the green slot-confirm card).
   - Font size, padding, border-radius, flex layout.
2. Add `.bernie-proposal-title`, `.bernie-proposal-detail-row`, and `.bernie-proposal-label` classes to style the card contents cleanly.

### review/test_diary_smoke.py
1. Add `test_bernie_tool_intent_proposal_ready(diary_page)` Playwright smoke test:
   - Mocks `/api/v1/appointments/proposals/bernie/tool-intent` to return `proposal_ready` with a nested `proposal` for appointment extension.
   - Types "extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes" and clicks Ask Bernie.
   - Verifies the proposal card is visible, shows "Proposed Duration: 30 mins", and no "Confirm booking" button is rendered.
2. Add `test_bernie_tool_intent_clarification_required(diary_page)` Playwright smoke test:
   - Mocks `/api/v1/appointments/proposals/bernie/tool-intent` to return `clarification_required` with block code `target_duration_required`.
   - Types "extend Margaret Thompson's booking" and clicks Ask Bernie.
   - Verifies the warning block text is displayed and no confirm controls or proposal cards are shown.

## Visual / Behavioural Acceptance Checks

- **Check 1: Composer Routing & Friendly voice**
  - Input: "extend Margaret's booking to 30 minutes"
  - Expected: POST request goes to `/proposals/bernie/tool-intent`. Bernie transcript shows bubble saying "I've prepared a proposal to change this appointment to 30 minutes. Nothing is changed until staff confirm."
- **Check 2: Proposal Card layout**
  - Input: Same as Check 1.
  - Expected: A blue-shaded `.bernie-proposal-card` is rendered under "Request". Details show Patient Name, Practitioner, Time, Current Duration, and Proposed Duration. No "Confirm booking" button is visible anywhere on the panel.
- **Check 3: Missing details error**
  - Input: "extend Margaret's booking" (no duration).
  - Expected: Warning block shows "Tell me the total appointment duration, for example 30 minutes." No proposal card or confirm buttons are visible.

## Risks / Ambiguities

- If the user types "extend" but there is no matching appointment on the active diary page, the backend will return `clarification_required` with `ambiguous_appointment_context` or `appointment_context_required`. The UI must display this block message cleanly and not crash.
- Mocks in the Playwright test must perfectly emulate the Pydantic schemas defined in `app/schemas/appointments.py`.

## Codex Plan Review

- Review result: Accepted with amendment. The proposed card/copy/stale-state guidance was integrated; the "no confirm controls" recommendation was narrowed to "no confirm controls without backend proposal evidence".
- Required changes before implementation: Render confirm only from `BernieToolIntentOut.proposal.safe`, never from staff/model text; keep booking/no-slot UI from bleeding into tool-intent states.
- Approved to proceed: implemented by Ariadne

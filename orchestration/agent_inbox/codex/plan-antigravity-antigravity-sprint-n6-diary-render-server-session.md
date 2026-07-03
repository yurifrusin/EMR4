# plan-antigravity-antigravity-sprint-n6-diary-render-server-session

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n6-diary-render-server-session` |
| Status | integrated |
| Created | 2026-07-03 22:45 +1000 |
| Source HEAD | `6ec3298` |

## Plan Summary

Refactor the Bernie panel UI on the Diary screen to fetch and render from the server-owned session and event endpoints introduced in Sprint N5. The browser will act as a pure presentational renderer of the server's session state and event tail, eliminating client authority over session logic and ensuring zero persistent PHI in local browser storage. We will support active session loading, new session creation, event append tracking with expected_revision/idempotency keys, and a warning banner to handle 409 stale session conflicts.

## My Understanding

The goals for Sprint N6 are:
1. **Consume N5 Bernie Session Endpoints**: Migrate the frontend to fetch the active session snapshot via `GET /api/v1/appointments/bernie/sessions/active` and trigger new session creation or refetch via `POST /api/v1/appointments/bernie/sessions/new`.
2. **Presentational Event Source**: Rewrite the chat transcript to render directly from the `events` list in the server-returned session snapshot, matching actor labels (staff vs. bernie) and event payloads.
3. **Idempotence & Revision Handling**: Format every user interaction as a client event append (`POST /api/v1/appointments/bernie/sessions/{session_id}/events`) specifying the current client-cached `expected_revision` and a unique `idempotency_key`.
4. **Stale Session Conflict Handling**: When the server returns a 409 Conflict (e.g. indicating a revision mismatch or external updates), display a clear warning banner and provide a "Refresh Session" option to refetch the latest server snapshot and realign the client revision.
5. **PHI Minimisation**: Ensure no patient clinical data or instruction text is persisted in `localStorage` or `sessionStorage`. All event payloads must be PHI-minimised (containing IDs and coordinates, and raw instructions only in the permitted `staff_instruction` event structure where expected by the server).
6. **Preserve Current Booking/Confirm Flows**: Ensure all existing proposal and confirmation UI behaviors remain intact and utilize the server's session ID and revision numbers.

## Intended Surface / Boundary

- **Primary UI Surface**: The Bernie sidebar copilot panel (`#bernie-review-panel`) on the Diary page (`docs/diary/diary.html`, `docs/diary/diary.js`, `docs/diary/diary.css`).
- **Visually Adjacent Surfaces (Must Not Change)**: The main diary grid (`#diary-grid`), location selector, roster columns, and appointment creation/edit modals.
- **Visual Changes**: Addition of a compact stale warning banner (`#bernie-stale-warning-banner`) within the sidebar panel, and an inline refresh/refetch button.

## Out Of Scope

- Backend database migration or schema modifications.
- GraphRAG or practice knowledge retrieval engine alterations.
- Client-side auto-confirmation logic.
- Command Center / Office taskpane SPA code modifications.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js): Update the `BernieSession` state machine, `loadBernieLiveReview`, and transcript rendering logic to query session endpoints and append client events.
- [docs/diary/diary.html](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.html): Add HTML markup for the stale revision warning banner and refresh controls.
- [docs/diary/diary.css](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.css): Style the stale revision warning banner with alert styling (yellow/amber warning background, bold indicator, and inline refresh action).
- [review/test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py): Add targeted Playwright smoke tests asserting session/event API contract usage, stale revision banner rendering, idempotency, and the absence of localStorage/sessionStorage PHI.

## Implementation Steps

### Step 1: Update the Frontend `BernieSession` State Machine
- Modify the `BernieSession` class constructor to store `revision` (integer initialized to 0), `sessionId` (dynamically updated from server), and `stale` (boolean).
- Replace direct local array mutation (`this.turns.push(...)`) with a server event append mechanism.
- Map client state names (e.g. `INSTRUCTION_ENTRY`, `CANDIDATE_SELECTION`) to server state values received in the snapshot.

### Step 2: Integrate Active Session Load and New Session Endpoints
- In `loadBernieLiveReview()`, call `GET /api/v1/appointments/bernie/sessions/active` on initialization, passing `surface_id` (defaults to "diary-main") and `reference_date`.
- On context change (e.g., patient selection changes), call `POST /api/v1/appointments/bernie/sessions/new` to reset and establish a clean session revision.
- Cache the returned `session_id` and update the local `revision`.

### Step 3: Implement Client Event Appends with Idempotency
- When submitting an instruction or selecting a candidate, construct the event request body:
  ```json
  {
    "event_type": "staff_instruction",
    "expected_revision": current_revision,
    "surface_id": "diary-main",
    "event_id": "<uuid>",
    "idempotency_key": "<uuid>",
    "payload": { ... }
  }
  ```
- Send a `POST` request to `/api/v1/appointments/bernie/sessions/{session_id}/events`.
- On success (HTTP 200), update the cached `revision` to the value returned by the server and re-render the UI based on the updated session snapshot.

### Step 4: Handle 409 Conflicts and Stale Revision Banner
- If the event append fails with an HTTP 409 Conflict, parse the response error payload.
- Transition the client state to show the stale warning banner (`#bernie-stale-warning-banner`).
- Disable all mutation buttons (like "Confirm Booking") and show an active "Refresh" button.
- Clicking the refresh button triggers a refetch from `/api/v1/appointments/bernie/sessions/active`, realigning the client's revision and restoring the active state.

### Step 5: Render Chat Transcript from Server Event Tail
- Update `updateBernieChatTranscriptUI()` to render exclusively from the `events` list of the server-supplied session snapshot.
- Map event types (`staff_instruction` -> actor: `staff`, `clarification_reply` -> actor: `staff`, server-generated events -> actor: `bernie`) to speech bubbles.
- Strip any client-side history storage to ensure the browser holds only transient presentational state.

### Step 6: Validate PHI minimisation
- Ensure that no instruction text or patient identity details are serialized to `localStorage` or `sessionStorage`.
- Check all payload shapes to ensure no PHI-related keywords (e.g. `patient_name`, `medicare`) are transmitted unless allowed by the backend's strict boundary checks.

## Visual / Behavioural Acceptance Checks

1. **Active Load**: Opening `diary.html?bernie_review=live&bernie_open=true` queries `GET /api/v1/appointments/bernie/sessions/active` and renders the input container.
2. **Event Appends**: Entering a staff instruction posts to `/bernie/sessions/{session_id}/events` and increments the session revision from `0` to `1`.
3. **Stale Session warning**: Simulating a 409 response by setting a mismatched client revision displays a prominent yellow banner with a "Refresh" button, and disables the confirm button.
4. **Refresh/Refetch Execution**: Clicking the "Refresh" button clears the banner, fetches the latest snapshot, and displays the corrected turn log.
5. **No Persistent PHI**: Browser devtools console execution of `localStorage.clear()` / `sessionStorage.clear()` shows no Bernie clinical payload remains stored.

## Risks / Ambiguities

- **State mapping**: Matching asynchronous server state updates to client state machine transitions must be carefully synchronized to prevent visual flickering. We will resolve this by making client rendering purely reactive to the returned snapshot.
- **Idempotency timing**: Ensure that quick clicks do not trigger duplicate events by immediately disabling the input textarea and submit button upon dispatch.

## Codex Plan Review

- Review result: Accepted with Ariadne amendments and integrated locally.
- Required changes before implementation: Do not make the N5 event tail the authoritative conversation transcript in N6. Event payloads must remain PHI-minimised; raw staff text/patient names stay out of the session event endpoint until a later retention/persistence policy and server outcome model exist.
- Approved to proceed: yes, with Ariadne implementation of the amended bridge.

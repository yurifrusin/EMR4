# plan-codex-codex-sprint-n5-session-endpoint-invariants

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Branch | `codex/current` |
| Source Task | `orchestration/agent_inbox/codex/codex-sprint-n5-session-endpoint-invariants.md` |
| Status | accepted |
| Sprint | N5 - Bernie Session Endpoint And Diary Render Tail |

## My Understanding

Sprint N4 gave Bernie an executable, server-owned, in-memory session substrate in
`app/services/bernie/session.py` and `app/services/bernie/session_store.py`.
That substrate already proves the core semantics directly at service level:
session ownership is `(practice_id, user_id, surface_id)`, every append echoes an
`expected_revision`, idempotent replay returns the first result, conflicting replay
fails closed, transient/server-owned states reject client events, diary navigation
marks candidate/proposal evidence stale, PHI-heavy payload keys are rejected, and
confirmation evidence can bind to `session_id` plus `session_revision`.

N5 should expose only the minimum authenticated API and Diary render/refetch tail
needed to use those semantics. The adversarial invariant lane should not decide
the full route design or build UI. It should make the future implementation hard
to weaken: browser state must not become authoritative, stale writes must refetch
from the server, confirm buttons must remain governed by backend evidence, and no
PHI-bearing Bernie session transcript should be persisted in browser storage.

## Intended Surface / Boundary

Backend route invariant surface:

- New or focused route tests for the N5 Bernie session endpoint contract, likely
  near the existing appointment/Bernie route tests and service tests.
- The tests should exercise whichever authenticated route names the backend lane
  chooses, but the expected semantics should map to the N4 store operations:
  active/new session, append event, refetch/current state, typed rejection result.
- Auth must follow existing FastAPI patterns: `get_current_user` /
  `require_role(*MUTATING_APPOINTMENT_ROLES)` and `current_user.practice_id`.

Diary UI smoke surface:

- `docs/diary/diary.js` only insofar as the UI lane wires server session state.
- `review/test_diary_smoke.py` route-intercept tests around Bernie session fetch,
  event append, stale revision handling, latest-message/history rendering,
  storage behaviour, and confirm evidence echo.
- Visually adjacent surfaces that must not change: diary grid layout, booking
  modal, patient-flow panel, waiting-room/admin tabs, taskpane, Command Centre,
  GraphRAG/practice-knowledge UI.

## Out Of Scope

- No production code during this plan gate.
- No PHI-bearing database table, migration, retention policy implementation, or
  full transcript persistence unless Ariadne/Yuri explicitly reapprove it.
- No broad appointments API rewrite, root-to-branch API review, GraphRAG route/UI
  wiring, auto-mode, autonomous booking, taskpane changes, or Command Centre work.
- No redesign of the Bernie panel, diary grid, booking cards, slot rendering,
  waiting room, or patient-flow status controls.

## Files I Expect Implementers To Edit Later

- Backend lane, likely: `app/routers/appointments.py` or a new Bernie/session
  router included from `app/main.py`; possibly `app/schemas/appointments.py` or
  a new small Bernie session schema module; focused route tests under `tests/`.
- UI lane, likely: `docs/diary/diary.js` plus `docs/diary/diary.html` /
  `docs/diary/diary.css` only if new selectors or compact states are required.
- Invariant/review lane: `review/test_diary_smoke.py`; optionally small harness
  data in `review/checks_diary.json` only if a reusable declarative check is a
  better fit than Python route interception.

## Proposed Backend Route Tests

The route tests should complement `tests/test_bernie_session_store.py`, not repeat
every service-level case. Each route assertion should prove that HTTP/auth/schema
wiring preserves the service invariant.

1. Auth and role gate:
   - Unauthenticated requests to active-session, append, and refetch endpoints
     return 401.
   - Authenticated users without a receptionist/practice-owner/admin style
     mutating role cannot append session events if the chosen route can influence
     booking state.
   - Route handlers derive `practice_id` and `user_id` from the JWT user, never
     from request JSON.

2. Session ownership:
   - User A creates or fetches an active session for `surface_id="diary-main"`.
   - User B in the same practice cannot append to User A's session when providing
     User A's `session_id`.
   - User in another practice cannot fetch or append to the session.
   - Wrong `surface_id` rejects with the stable
     `session_owner_mismatch` semantics and leaves revision/events unchanged.

3. Active/new session contract:
   - Active-session returns a server-created `session_id`, `revision=0`,
     `state="instruction_entry"`, the supplied/visible reference date, and an empty
     or PHI-minimised event tail.
   - A `new_session` event or explicit new-session endpoint resets patient,
     practitioner, candidate, proposal, stale, and UI-tail state server-side while
     preserving ownership coordinates.
   - Browser-supplied random client session ids are either ignored or rejected,
     depending on backend design; they must not create authority.

4. Revision conflicts:
   - Append with exact `expected_revision` succeeds once and increments by one.
   - Append with lower revision returns a conflict response, preferably 409, with
     `code="stale_session_revision"` and the current server snapshot/refetch hint.
   - Append with a future revision returns a conflict response with
     `code="future_session_revision"`.
   - Conflict responses do not append an event and do not alter `last_event_id`.

5. Idempotency:
   - Repeating the same event id or idempotency key with identical body returns the
     original accepted event/session result without a second event.
   - Reusing the same key with a changed `event_type`, `expected_revision`, or
     payload returns `idempotency_conflict`.
   - Idempotency keys are scoped by session id and cannot replay across sessions.

6. Event tamper and client authority:
   - Client-supplied `practice_id`, `user_id`, `revision`, `state`, `events`,
     `turn_count`, or `confirmed` fields in payload are ignored or rejected; they
     must not overwrite the server record.
   - Client cannot jump to `confirmed`; `confirm_submitted` may enter
     `confirmation`, and only server advance/confirm outcome may reach
     `confirmed`.
   - Client events in transient states return
     `event_not_allowed_in_transient_state`.

7. PHI minimisation:
   - Payloads containing `raw_instruction`, `instruction_text`, `patient_name`,
     `dob`, `medicare`, `phone`, `address`, `transcript`, or nested variants are
     rejected with `phi_payload_not_allowed`.
   - Accepted event tails returned by route fixtures contain structured ids,
     timestamps, event kinds, and evidence refs only, not patient names or raw
     transcript text.

8. Confirm evidence compatibility:
   - Confirmation-binding response fields include `session_id`,
     `session_revision`, `surface_id`, `practice_id`, `staff_user_id`,
     `reference_date`, candidate/proposal freshness ids, appointment date/time,
     and duration.
   - Existing signed confirm evidence tests still pass when `turn_ref` is absent
     or legacy, but the new session-bound path rejects stale/mismatched
     `session_revision` before booking.
   - Confirm evidence should be echo-compatible with
     `enrichBernieConfirmPayload()` so existing `candidate_freshness_id`,
     `proposal_freshness_id`, and signed envelope fields are preserved.

## Proposed UI Smoke Checks

Use the existing Playwright route-intercept style in `review/test_diary_smoke.py`.
Prefer narrow assertions over screenshots.

1. Render from server state:
   - Intercept the N5 active-session/refetch endpoint with a server snapshot that
     has `session_id`, `revision`, `state`, and a compact event tail.
   - Open `/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true`.
   - Assert the Bernie panel renders the latest server message/history and updates
     the in-memory `bernieSession.sessionId` and revision metadata from the
     response, not from a locally generated id.

2. Append sends server-owned coordinates:
   - Submit a staff instruction and capture the append request.
   - Assert it includes `event_type`, `expected_revision`, and an idempotency key
     or event id, but does not include client-authored `practice_id`, `user_id`,
     `state`, raw `events` array as authority, or any browser-stored PHI.

3. Stale revision refetch:
   - Intercept append with 409
     `{ code: "stale_session_revision", session: { revision: N+1, ... } }`.
   - Assert the composer disables or shows a stale/refetch state until the UI
     applies/refetches the server snapshot.
   - Assert no confirm button is visible while stale and a follow-up append uses
     the new revision.

4. Idempotent replay UI:
   - Simulate a retry where the first append times out or the same idempotency key
     is submitted twice and the second response returns the original accepted
     session.
   - Assert only one rendered staff turn appears and the UI does not duplicate the
     latest message.

5. No PHI browser persistence:
   - After rendering and submitting an instruction containing a patient name in
     smoke mode, evaluate `localStorage` and `sessionStorage`.
   - Assert no key/value contains the instruction text, patient name, Medicare-like
     number, DOB, or raw transcript. Existing non-PHI UI preferences such as flow
     panel open state, collapse state, location id, and auth token fallback are not
     failures unless they begin storing Bernie PHI.

6. Confirm evidence echo:
   - Intercept a server session snapshot or Bernie review payload with signed
     confirmation evidence plus `session_id` and `session_revision`.
   - Click the existing `bernie-review-confirm-button`.
   - Assert the confirm POST body preserves the signed evidence fields and adds no
     browser-invented evidence; if the server marks session/evidence stale, assert
     the confirm button is suppressed or the error state is shown.

7. Diary navigation staleness:
   - With a proposal preview rendered, navigate the visible diary date or trigger
     the session event representing `diary_navigated`.
   - Assert candidate/proposal UI is marked stale, confirm is hidden, and a refetch
     or refresh event is sent with the current server revision.

## Risks / Ambiguities

- Route shape is not yet fixed. The invariant tests should target behaviours, not
  overfit names. A small test helper can adapt to final paths once the backend
  lane lands.
- The current Diary `BernieSession` stores turns in memory and sends `turns` /
  `turn_ref` to legacy Bernie proposal endpoints. N5 should not require a big
  rewrite, but implementers must be explicit about the bridge period so legacy
  interpret/supervised-booking responses and new server session snapshots do not
  fight each other.
- Current `localStorage` use includes auth token fallback and non-PHI UI
  preferences. The no-PHI check must scan values for Bernie PHI instead of
  banning storage outright.
- In-memory N4 storage resets on process restart. N5 route tests can still prove
  semantics, but product language should not imply durable conversation memory
  until persistence/retention is approved.
- Confirm evidence compatibility is the sharpest merge point: session revision
  binding must harden stale confirms without breaking legacy signed evidence tests
  or the current `enrichBernieConfirmPayload()` preservation path.

## Acceptance Criteria

- The accepted implementation plan adds adversarial backend route tests for auth
  ownership, cross-practice/cross-user/cross-surface rejection, revision conflict,
  future revision rejection, idempotent replay, idempotency tamper,
  client-authority tamper, PHI payload rejection, and session-bound confirmation
  evidence.
- The accepted UI plan adds focused smoke checks proving the Diary panel renders
  from server session state, refetches or applies server snapshots after stale
  conflicts, avoids duplicate turns on idempotent retry, stores no Bernie PHI in
  browser storage, hides confirm on stale state, and preserves signed confirm
  evidence fields.
- Backend tests preserve all existing `tests/test_bernie_session_store.py` service
  guarantees and keep route responses typed enough for the Diary UI to branch on
  stable rejection codes.
- UI tests preserve existing Bernie confirm, stale-gate, and visible-date
  reanchor smoke tests.
- Verification for implementation should include focused Bernie session route
  tests, `pytest tests/test_bernie_session_store.py`, relevant existing signed
  evidence/confirm tests, relevant `review/test_diary_smoke.py` Bernie checks,
  `node --check docs\diary\diary.js` if Diary JS changes, Python compile checks
  for touched backend modules, and `git diff --check`.

## Completion Notes

- Files changed: `orchestration/agent_inbox/codex/plan-codex-codex-sprint-n5-session-endpoint-invariants.md`
- Verification run: `git diff --check` passed
- Remaining risks: route names and final UI rendering affordances are owned by the backend/UI N5 lanes; this packet intentionally pins invariants rather than implementation details.

## Codex Plan Review

- Review result: Accepted as N5 adversarial route/UI invariant plan.
- Required changes before implementation: Use backend route tests first; treat UI
  smoke checks as the tail once the endpoint contract exists.
- Approved to proceed: yes

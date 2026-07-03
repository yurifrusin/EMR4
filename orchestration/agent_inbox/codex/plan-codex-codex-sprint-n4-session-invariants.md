# plan-codex-codex-sprint-n4-session-invariants

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Codex N4 Session Invariants |
| Worker Branch | `codex/current` |
| Source Task | `orchestration/agent_inbox/codex/codex-sprint-n4-session-invariants.md` |
| Status | integrated |
| Created | 2026-07-03 |

## Understanding

Sprint N4 should turn the existing persistence-shaped Bernie session/event
contracts into a server-owned session/event foundation without letting browser
state remain the source of truth. The current `app/services/bernie/session.py`
already defines semantic states, client event types, static transition tables,
and JSON-serializable record/event shapes, but it deliberately has no store,
revision, idempotency, session ownership, or endpoint wiring. Existing tests
prove important static rules: no client event reaches `confirmed`, transient
states accept no direct client events, `confirmation` is entered only from
`proposal_preview`, freshness ids are deterministic, stale/mismatched evidence
blocks writes, signed confirmation evidence rejects tamper/mismatch, and diary
suggestions cannot smuggle confirm-grade evidence.

The missing adversarial surface is persistence under hostile or simply messy
real use: two tabs acting on the same session, stale event submissions after a
refresh/navigation, cross-staff or cross-session replay of a proposal, and PHI
leaking into session rows, event payloads, logs, or browser-owned state. The N4
invariant harness should therefore validate the future session store and route
contract as a server-side state machine, not as another client-side helper.

## Files / Surfaces

Expected implementation surfaces after plan approval:

- `app/services/bernie/session.py`: extend the pure contract with persistence
  fields such as `revision`, `last_event_id`, `active_surface_key`, event
  idempotency key, ownership binding, and typed rejection reasons. Keep it pure
  enough for direct unit tests.
- New focused service module if needed, likely `app/services/bernie/session_store.py`
  or equivalent, for append-and-advance semantics over the future DB-backed
  session/event rows.
- Models/migration if the accepted N4 contract includes persistence tables,
  likely session snapshot plus append-only event log. Table shape should be
  minimal and PHI-conscious.
- Router/schema surface only if Claude's contract lane introduces endpoint
  wiring; otherwise this Codex lane should stay at service/test level and avoid
  duplicating route ownership.
- Tests, preferably a new focused file such as
  `tests/test_bernie_session_invariants.py`, plus small additions to
  `tests/test_bernie_domain_package.py`, `tests/test_bernie_turn_contract.py`,
  or `tests/test_bernie_signed_confirmation_evidence.py` only where adjacency
  matters.
- Existing related test/reference files to respect:
  `tests/test_bernie_domain_package.py`,
  `tests/test_bernie_turn_contract.py`,
  `tests/test_bernie_signed_confirmation_evidence.py`,
  `tests/test_diary_confirm_gate.py`,
  `tests/test_diary_action_envelopes.py`,
  and `docs/diary/diary.js` as a compatibility reference, not an implementation
  target for this lane.

Visually adjacent surfaces that should not change in this lane:

- Diary grid layout, appointment cards, waiting room/status controls, and
  Bernie panel rendering in `docs/diary/*`.
- Taskpane, Command Centre, Office manifest, and GitHub Pages deployment assets.
- GraphRAG/practice-knowledge retrieval wiring and advisory UI.

## Out Of Scope

- No production code during this plan-gate pass.
- No frontend implementation, redesign, cache-bust, or render-from-state UI
  migration in the Codex invariant lane.
- No broad appointment API rewrite or root-to-branch API-spine review.
- No GraphRAG route/UI wiring and no auto-mode.
- No live PHI fixtures, full transcript persistence, or retention policy beyond
  naming the decisions the implementation must keep explicit.
- No direct diary mutation path outside the existing confirmed API/write gates.

## Proposed Invariant Tests

1. Static transition closure remains locked:
   - Every `BernieSessionState` has a transition-table entry.
   - No client event targets `confirmed`.
   - `confirmed` is reachable only by server advance from `confirmation`.
   - `confirmation` is reachable only through `confirm_submitted` from
     `proposal_preview`.
   - Client events in transient states are typed rejections, not silent ignores.

2. Persisted event append requires the current revision:
   - A legal event with `expected_revision=N` advances to `N+1`.
   - The same event replayed with stale `expected_revision=N` is rejected with a
     conflict/stale reason and does not append a second event.
   - A future or skipped revision is rejected.
   - `new_session` creates or resets through an explicit server-owned path, not
     by client mutation of the existing row.

3. Idempotency is bounded and safe:
   - Repeating the same `event_id` or idempotency key for the same session and
     same payload returns the original event/result without duplicate append.
   - Reusing the same event id with different payload is rejected as tamper or
     idempotency conflict.
   - Reusing an event id across a different session/practice/user does not
     authorize anything and is rejected or treated as unrelated according to the
     final store design.

4. Cross-tab concurrency:
   - Tab A and Tab B both read revision 3.
   - Tab A appends `candidate_selected` and reaches `proposal_preview` revision
     4.
   - Tab B tries `refresh_requested`, `candidate_selected`, or
     `confirm_submitted` against revision 3 and gets a typed stale-event
     rejection with no state/event mutation.
   - After Tab B refetches revision 4, only transitions legal from the new
     state are allowed.

5. Stale navigation and refresh rejection:
   - `diary_navigated` is allowed only in non-transient states and marks
     proposal/candidate evidence stale or clears confirm affordance according to
     the accepted store contract.
   - `diary_navigated` while `recognition`, `context_enrichment`,
     `slot_search`, or `confirmation` is in progress is rejected because those
     states are server-owned.
   - `refresh_requested` from `proposal_preview` or `candidate_selection`
     invalidates staged proposal/candidate freshness before any confirm can be
     accepted.

6. Cross-staff, cross-practice, and cross-session replay:
   - A session belongs to one `practice_id`, one authenticated staff `user_id`,
     and one diary surface key unless the final contract explicitly supports
     transfer.
   - Another staff user cannot append to, confirm from, or replay events against
     that session.
   - A valid proposal/freshness id from session A cannot confirm session B.
   - A valid signed confirmation envelope minted for one practice/user/session
     cannot confirm for another practice/user/session.

7. Signed evidence/session binding:
   - Signed confirmation evidence payload includes session binding fields in the
     final design: at minimum `practice_id`, `staff_user_id`, `session_id`,
     `proposal_freshness_id`, `candidate_freshness_id` where present,
     `reference_date`, typed slot coordinates, and selected patient/practitioner
     UUIDs.
   - Missing session binding blocks confirmation once the persisted N4 path is
     active.
   - Tampering any binding coordinate rejects before appointment/audit mutation.
   - Old unsigned/weak evidence remains only in an explicitly named compatibility
     lane, if still required, and that lane cannot claim persisted-session
     freshness.

8. PHI minimisation:
   - Session snapshot stores UUIDs, state, dates, freshness ids, revision, and
     compact reason codes, not raw patient names, phone numbers, Medicare,
     clinical free text, or full chat transcript by default.
   - Event payloads for `staff_instruction` store a redacted/summary marker or
     structured intent reference unless Yuri explicitly approves transcript
     retention.
   - Rejection details and audit/log messages do not echo raw instruction text
     or patient labels.
   - Browser-owned local/session storage is not required as source of truth for
     confirm authority.

9. Render-from-state tail assumptions:
   - A serialized session record is sufficient for the UI to know semantic
     state, current revision, stale/blocked reason codes, selected candidate
     index, staged proposal freshness, and whether confirm UI may be shown.
   - Presentation-only state remains absent from the server snapshot: panel
     open/closed, disclosure expanded/collapsed, composer focus, and visual
     layout preferences.

## Implementation Steps After Approval

1. Reconcile this invariant plan with Claude's N4 session contract plan and
   Antigravity's render-from-state UI plan before coding, so ownership does not
   overlap.
2. Add the smallest pure contract extensions needed in `session.py` for
   revision, ownership, idempotency, event rejection codes, stale evidence
   markers, and session-bound evidence coordinates.
3. If persistence lands in this sprint, add minimal models/migration and a
   service-level append function that performs one transaction: load current
   session, verify ownership/revision/event legality, append event, update
   snapshot, return state or typed rejection.
4. Add the adversarial invariant test file first, then implement only enough
   backend/session logic for those tests to pass.
5. Wire signed evidence/session binding at the service or confirmation boundary
   selected by Ariadne, preserving current S1 signed-evidence tests and making
   any legacy compatibility explicit.
6. Run focused Bernie/session/evidence tests, then broader adjacent tests if
   persistence or router behavior changed.

## Risks / Ambiguities

- Retention policy is still a Yuri decision. The implementation should default
  to PHI minimisation and avoid raw transcript persistence unless explicitly
  approved.
- Backward compatibility with Sprint 104/105 clients currently tolerates missing
  freshness ids. N4 should decide when the persisted-session path fails closed
  while preserving any temporary legacy lane by name.
- Cross-tab behavior needs a concrete client contract: the server can reject
  stale revisions, but Antigravity's UI plan should define how the panel refetches
  and rerenders those rejections.
- If Claude owns models/routes, this Codex lane should avoid parallel edits in
  the same files and instead contribute tests or review repairs after plan
  acceptance.
- Session binding in HMAC payloads may require carefully staged changes to
  existing confirm payload builders to avoid breaking current tests before the
  new persisted-session endpoint exists.

## Acceptance Criteria

- The accepted implementation plan names a bounded invariant harness for
  persisted Bernie session/event state and does not require frontend changes.
- Tests prove impossible transitions, transient-state client event rejection,
  stale revision conflicts, cross-tab races, cross-staff/session/practice replay
  rejection, signed evidence/session binding, and PHI minimisation.
- Confirm-grade writes remain gated by existing deterministic policy,
  staleness, and signed evidence checks; retrieval/advisory frames cannot create
  confirm authority.
- The future UI can render semantic Bernie state from server-owned state without
  treating browser memory as authoritative.
- Verification for implementation includes focused Bernie session/evidence
  tests, migration checks if tables are added, py-compile for touched backend
  modules, and `git diff --check`.

## Completion Notes

- Files changed:
  - `orchestration/agent_inbox/codex/plan-codex-codex-sprint-n4-session-invariants.md`
- Verification run:
  - `git diff --check` passed.
- Remaining risks:
  - Needs coordination with Claude/Antigravity N4 plans before production code
    edits, especially around table/route ownership and UI stale-revision
    behavior.

## Codex Plan Review

- Review result: Accepted as the adversarial invariant harness for N4 backend
  session/store implementation.
- Required changes before implementation: Treat persistence table/migration and
  UI route wiring as optional future work; focus this sprint on executable
  server-owned append/concurrency semantics and PHI-minimised contracts.
- Approved to proceed: yes

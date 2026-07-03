# plan-codex-codex-sprint-n7-session-outcome-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-sprint-n7-session-outcome-invariants` |
| Status | integrated |
| Created | 2026-07-03 23:58 +1000 |
| Source HEAD | `076862c` |

## Plan Summary

Plan N7 adversarial invariants for server-owned outcome events and session-bound confirmation

## My Understanding

N7 should make Bernie interpreter/proposal/candidate/confirmation outcomes server-owned session events while preserving N6's boundary: browser state may display and request, but cannot authorise confirmation, overwrite session truth, or persist PHI-heavy transcript state.

## Intended Surface / Boundary

Backend Bernie session store/route tests, signed confirmation/session-binding tests, and narrow Diary smoke checks if UI changes. Nearby surfaces that must not change: taskpane, Command Centre, GraphRAG/practice knowledge, appointment CRUD outside Bernie outcome confirmation, database migrations unless separately approved.

## Out Of Scope

Production code during plan gate, raw transcript storage, browser-owned confirmation authority, broad UI redesign, auto-mode, GraphRAG wiring, PHI-bearing persistence tables.

## Files I Expect To Edit

Expected later edits: app/services/bernie/session.py, app/services/bernie/session_store.py, app/routers/appointments.py and app/schemas/appointments.py only if additive event/evidence schema is required, tests/test_bernie_session_routes.py, tests/test_bernie_session_store.py, tests/test_bernie_signed_confirmation_evidence.py, tests/test_diary_confirm_gate.py, and review/test_diary_smoke.py only if the Diary UI contract changes. Plan packet recovered by Ariadne from Codex worker Boole after worker protocol handin failed on the Windows Store python alias.

## Implementation Steps

1. Define typed server outcome events for interpreter_result, proposal_result, candidate_selected, confirmation_submitted, and confirmation_result with compact non-PHI references.
2. Keep raw staff text, patient names, DOB, Medicare, phone, address, transcript/debug bodies, and broad confirm payloads out of session event storage.
3. Enforce expected_revision and idempotency on outcome event append; stale/future revisions return 409 with the latest snapshot and no mutation.
4. Bind confirmation-grade evidence to the active session id, revision, referenced outcome event ids, candidate/proposal identity, expiry, and appointment coordinates.
5. Reject confirmation if session id, staff/practice ownership, candidate, proposal, practitioner, patient, date/time, revision, or signature is stale/mismatched/tampered.
6. Preserve N6 browser posture: the Diary may append/refetch/render, but cannot invent session authority, store PHI/session snapshots, or confirm from stale client text.
7. Use typed state/reason codes to prevent contradictory no-slot/proposal/confirmation messages rather than ad hoc copy filters.
8. Keep this as process-local session semantics for now; do not add a persisted table until retention and cleanup policy is decided.

## Visual / Behavioural Acceptance Checks

Focused tests must prove stale revision rejection, idempotent replay and idempotency-key conflict rejection, no raw transcript/PHI event persistence, cross-user/cross-practice/cross-session rejection, fail-closed signed confirmation binding, invalid outcome ordering rejection, stale Diary conflict rendering with confirm disabled, no local/session storage PHI, and adjacent evidence/confirm regressions green. Required checks: focused backend session/evidence/confirm suites, `node --check docs\diary\diary.js` and route-intercepted Diary smoke if UI changes, and `git diff --check`.

## Risks / Ambiguities

Existing Diary JS still has a client-side Bernie state object; N7 must not bless that as authority. Outcome payload schemas can accidentally leak PHI through summary/debug/free-text fields. Confirmation binding may require a tiny additive evidence contract change; accept only with tamper/stale tests. Do not accept a formal worker submit from Boole because protocol handin failed; this is Ariadne-recovered plan input.

## Codex Plan Review

- Review result: Accepted as Ariadne-recovered Codex worker plan after Boole's protocol handin failed on the Windows Python alias.
- Required changes before implementation: Keep N7 backend-first; do not change Diary assets unless outcome-state rendering requires it; keep event payloads PHI-minimised and session binding optional for compatibility.
- Approved to proceed: yes; Ariadne implemented and verified the bounded backend/session slice.

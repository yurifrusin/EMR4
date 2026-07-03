# plan-codex-ariadne-sprint-n4-bernie-server-session-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | orchestrator |
| Source Task | `claude-sprint-n4-bernie-server-session-contract` |
| Status | accepted |
| Created | 2026-07-03 |
| Source HEAD | `a07f0ca` |

## Plan Summary

Claude remains capped by the five-hour session limit, so Ariadne replaces the
N4 backend/session contract lane. Sprint N4 should implement the smallest
server-owned Bernie session/event foundation that can later be persisted and
rendered by the Diary UI: typed session records, append-only event semantics,
revision/idempotency rejection, ownership binding, PHI-minimised payloads, and
signed confirmation evidence binding. The implementation should avoid a broad
UI migration in this sprint.

## My Understanding

`app/services/bernie/session.py` already defines semantic session states,
client event types, static transition tables, transient/terminal states, and
persistence-shaped Pydantic models. It deliberately has no store, revision,
idempotency, endpoint, or retention/concurrency rules. Sprint S1 has just added
server-signed confirmation evidence covering practice/staff/session/turn,
selected slot, create command, and freshness ids. N4 should connect these ideas:
server state owns conversation memory and event legality; signed evidence owns
confirmation-grade write authority.

The key product direction remains: one Bernie session per staff user per diary
surface; browser state may render and submit events, but must not be the
authority for semantic state, freshness, or write eligibility.

## Intended Surface / Boundary

Primary backend/domain surface:

- `app/services/bernie/session.py`
- a new pure/service module such as `app/services/bernie/session_store.py`
- `app/services/bernie/__init__.py` facade exports
- focused tests, likely `tests/test_bernie_session_store.py` plus small facade
  assertions in `tests/test_bernie_domain_package.py`
- if necessary, a small signed-evidence payload extension in
  `app/routers/appointments.py` or `app/services/bernie_turn_evidence.py`

Avoid route/UI/migration work unless the implementation proves a tiny boundary
addition is needed. In particular, do not migrate `docs/diary/diary.js` to
render-from-server-state during this backend foundation sprint.

## Out Of Scope

- No broad API-spine rewrite.
- No GraphRAG/practice-knowledge route/UI wiring.
- No auto-mode or autonomous booking.
- No full transcript persistence unless Yuri explicitly approves retention.
- No live PHI fixtures.
- No diary visual redesign or GitHub Pages asset deployment.
- No weakening of existing proposal, staleness, signed evidence, RBAC, or audit
  gates.

## Implementation Steps

1. Extend the session contract with minimal server-state fields: `revision`,
   `practice_id`, `staff_user_id`, `surface_id`, optional active/stale evidence
   refs, and typed rejection reason codes.
2. Add a pure in-memory store/service that models the future DB contract:
   create/reset session, append client event with expected revision and
   idempotency key, validate transition, update snapshot, return typed success
   or typed rejection. This keeps the persistence semantics executable without
   adding a premature PHI-bearing table.
3. Enforce one session owner tuple: practice + staff + surface. Cross-staff,
   cross-practice, and wrong-surface events must fail closed.
4. Enforce optimistic concurrency: stale, skipped, or replayed revisions do not
   append events or advance state.
5. Enforce idempotency: same event id/key and same payload returns the original
   result; same event id/key with different payload rejects as conflict.
6. Keep event payloads PHI-minimised by default. Structured ids/reason codes are
   allowed; raw transcript persistence is not.
7. Add a helper that returns the session-binding coordinates expected in signed
   confirmation evidence, so S1 evidence can later be required to match the
   persisted session path.
8. Add focused tests for the adversarial cases from the Codex invariant plan.

## Acceptance Checks

- Invalid transitions and all client events in transient states are typed
  rejections.
- No client event reaches `confirmed`.
- Appending with the current revision advances exactly once.
- Stale/skipped revisions are rejected without mutation.
- Duplicate idempotent event replay is safe; duplicate id with different
  payload rejects.
- Cross-practice, cross-staff, and cross-surface events reject.
- Session snapshots and event payload validators reject obvious PHI-heavy keys
  such as Medicare, phone, full patient name, or raw transcript text by default.
- Signed-evidence session binding helper includes practice, staff, session,
  reference date, candidate/proposal freshness ids, and slot coordinates.
- Existing S1 signed evidence and Bernie turn/facade tests remain green.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests\test_bernie_session_store.py tests\test_bernie_domain_package.py tests\test_bernie_signed_confirmation_evidence.py tests\test_bernie_turn_contract.py -q`
- `.\.venv\Scripts\python.exe -m py_compile app\services\bernie\session.py app\services\bernie\session_store.py app\services\bernie\__init__.py`
- `git diff --check`

## Risks / Ambiguities

- True server persistence still requires a PHI retention policy and a DB
  migration. This sprint should make the persistence contract executable while
  deferring the actual PHI-bearing table until Yuri/Ariadne explicitly approve
  retention and cleanup rules.
- Antigravity's UI plan should be treated as the render-from-state tail, not
  implemented before the backend has a real state endpoint.
- The old compatibility lane that tolerates missing freshness evidence must stay
  named and isolated. The new persisted-session path should be fail-closed.

## Completion Notes

- Files changed:
  - `orchestration/agent_inbox/codex/plan-codex-ariadne-sprint-n4-bernie-server-session-contract.md`
- Verification run:
  - Pending plan acceptance.
- Remaining risks:
  - Claude did not contribute due session limit; Ariadne should revisit Claude
    once the usage window refreshes if the implementation grows beyond this
    bounded backend foundation.

## Codex Plan Review

- Review result: Accepted as the backend implementation lane replacing capped
  Claude for N4.
- Required changes before implementation: Keep N4 backend-first and avoid
  adding a PHI-bearing database table or UI render-from-state migration in this
  sprint unless Ariadne explicitly reopens the scope.
- Approved to proceed: yes

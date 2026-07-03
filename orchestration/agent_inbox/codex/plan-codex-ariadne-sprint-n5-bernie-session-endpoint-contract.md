# plan-codex-ariadne-sprint-n5-bernie-session-endpoint-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | orchestrator |
| Source Task | `claude-sprint-n5-bernie-session-endpoint-contract` |
| Status | accepted |
| Created | 2026-07-03 |
| Source HEAD | `c185281` |

## Plan Summary

Claude remains capped, so Ariadne replaces the N5 backend lane. Implement the
smallest authenticated API wrapper around the N4 in-memory Bernie session store:
get/create active session, append typed client events with expected revision and
idempotency, return typed conflict responses, and expose a PHI-minimised session
snapshot suitable for the Diary UI to render later.

## Understanding

N4 deliberately avoided a PHI-bearing table. N5 should keep that constraint:
the endpoint makes server-owned state usable in the current backend process, but
does not claim durable retention. This lets the Diary start moving toward
render-from-state while Yuri/Ariadne still decide retention, TTL, cleanup, and
transcript policy.

The route must derive `practice_id` and `user_id` from auth. Client JSON may
choose a `surface_id` and typed event payload, but must not author practice,
user, state, revision, events, or write authority.

## Intended Surface / Boundary

- `app/schemas/appointments.py` for small additive request/response models.
- `app/routers/appointments.py` for minimal Bernie session endpoints near the
  existing Bernie proposal routes.
- `app/services/bernie/session_store.py` only if tiny endpoint-support helpers
  are needed.
- focused tests, likely `tests/test_bernie_session_routes.py`.

No Diary UI change in the first implementation slice unless backend route tests
land cleanly and the UI patch remains very small.

## Out Of Scope

- No database session table or Alembic migration.
- No GraphRAG/practice-knowledge route/UI wiring.
- No auto-mode or autonomous booking.
- No broad appointments API rewrite.
- No browser PHI persistence.
- No taskpane/Command Centre work.

## Implementation Steps

1. Add additive Pydantic schemas for:
   - session snapshot out;
   - active-session request/query;
   - event append in;
   - event append out / typed rejection.
2. Add a process-local `InMemoryBernieSessionStore` instance in the appointments
   router as an explicit dev/session-foundation substrate.
3. Add `GET /appointments/bernie/sessions/active` that takes `surface_id` and
   optional `reference_date`, returns an existing active session for
   practice+user+surface or creates one.
4. Add `POST /appointments/bernie/sessions/new` to explicitly reset/create a new
   session for practice+user+surface.
5. Add `POST /appointments/bernie/sessions/{session_id}/events` to append typed
   events with expected revision/idempotency. Return 200 on accepted events and
   409 on typed conflicts/rejections.
6. Do not persist raw instruction text; route tests should prove PHI-heavy keys
   are rejected by the service and surfaced as typed rejections.
7. Add focused route tests for auth-derived ownership, active/new session,
   stale/future revision conflicts, idempotency replay/conflict, cross-user or
   wrong-surface rejection, and PHI payload rejection.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests\test_bernie_session_routes.py tests\test_bernie_session_store.py tests\test_bernie_domain_package.py -q`
- `.\.venv\Scripts\python.exe -m pytest tests\test_bernie_signed_confirmation_evidence.py tests\test_bernie_confirm_create_proposal.py -q`
- `.\.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py app\services\bernie\session_store.py`
- `git diff --check`

## Risks

- Process-local state resets on backend restart. The response and closeout must
  call this a foundation endpoint, not durable session persistence.
- The route path must not be mistaken for confirmation authority. Confirmation
  remains governed by proposal, staleness, signed evidence, RBAC, and audit
  gates.
- The UI tail should consume only stable rejection codes and snapshots; avoid
  overfitting frontend code before backend tests settle.

## Codex Plan Review

- Review result: Accepted as Ariadne backend implementation lane replacing
  capped Claude.
- Required changes before implementation: Keep DB persistence and UI tail out of
  this first N5 backend slice unless explicitly reapproved.
- Approved to proceed: yes

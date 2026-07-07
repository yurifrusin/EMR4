# API Spine Create-Proposal minLength Readiness Decision

| Item | Value |
|---|---|
| Sprint | 152 |
| Programme | Programme 2G / EMR4 API Spine |
| Decision | Defer runtime `Idempotency-Key` `minLength: 8` enforcement |
| Runtime posture | No route behavior change after Sprint 151 |

## Decision

Sprint 152 keeps `POST /api/v1/appointments/proposals/create` in the Sprint 151
runtime posture:

- missing or blank `Idempotency-Key` fails closed;
- short non-blank keys continue to be accepted;
- OpenAPI still documents the shared `Idempotency-Key` shape as required with
  `minLength: 8` and `maxLength: 128`;
- runtime minLength enforcement remains deferred.

This is not a rejection of OpenAPI's header shape. It is a client-readiness
decision: the runtime should not reject short non-blank keys until the current
client surface is known to satisfy even the existing non-blank proposal header
contract and the sibling proposal routes have an explicit posture.

## Evidence

Claude's Sprint 152 review found the primary diary create-proposal caller still
posts through `apiFetch` without an `Idempotency-Key` header. That means the
project has not yet proved that create-proposal clients send a non-blank key,
let alone that candidate keys are at least 8 characters after trimming.

Antigravity's acceptance lane argued that future diary keys can safely use the
existing event-id generator and would naturally exceed 8 characters. Ariadne
accepts that as the likely client-fix direction, but not as evidence that the
current runtime is ready for stricter rejection.

DeepSeek's adversarial review found the wider API-spine gap: 3 of 4 canonical
OpenAPI proposal operations do not yet bind `Idempotency-Key` in FastAPI:

- `propose_update_appointment`
- `propose_status_update`
- `propose_delete_appointment`

Only `propose_create_appointment` currently binds the header. Tightening
create-proposal to `minLength: 8` alone would make the runtime surface more
uneven while leaving update/status/delete proposal routes completely unwired.

## Preconditions Before Enforcing minLength

Do not enforce runtime `minLength: 8` on create-proposal until a later sprint
records all of these:

1. Create-proposal clients send a non-blank key in the real caller path, not
   only in backend tests.
2. candidate keys are at least 8 characters after trimming.
3. A typed short-key rejection contract is chosen, avoiding raw FastAPI `422`
   validation drift from the existing typed `400 idempotency_key_required`
   missing/blank response.
4. All proposal-route header postures are reviewed together, including update,
   status, and delete proposal routes.
5. Focused tests prove the chosen behavior and preserve no proposal ledger,
   no stored proposal replay, no appointment/audit writes, and no slot
   reservation semantics.

## Guardrail Outcome

Sprint 152 adds static guards for the decision rather than changing behavior:

- all four OpenAPI proposal operations must keep referencing the shared
  `IdempotencyKey` parameter;
- the current FastAPI binding gap for update/status/delete proposal handlers is
  explicitly documented;
- runtime minLength enforcement remains deferred until the preconditions above
  are met.

## Recommended Next Sprint

The next Programme 2G move should close the more concrete client gap before
strict length enforcement: preflight or wire proposal-route header discipline
for the real diary create-proposal caller and/or the next proposal-only
surface. Do not extend the proposal header contract to raw compatibility writes
by default.

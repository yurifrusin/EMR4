# Reception One selected-appointment duration composition threat-model delta

Date: 2026-08-14

Timestamp: 2026-08-14T10:46:25+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: accepted projection-neutral truth kernel and the existing
native Diary update proposal/confirm plus selected-time compositions

## Changed surface

This tranche adds one internal staff duration affordance to Reception One. It
adds no write authority. The bridge fixes start delta at zero, retains the same
practitioner and delegates to `handleMoveResize`, whose existing update
proposal/confirm path remains the sole owner of admission and commit.

## Threats and required controls

| Threat | Required control |
|---|---|
| Reception One becomes a second resize implementation | The bridge validates one target, computes only `deltaDuration`, supplies literal zero `deltaStart` and calls `handleMoveResize`; reject bridge-local network, route, proposal, confirm, signing, idempotency or raw PUT code. |
| Duration intent shifts date, start or practitioner | Resolve exact current truth immediately before delegation, supply zero start delta and the same practitioner column, and compare all frozen fields after every outcome. |
| Invalid target creates excessive or cross-day booking | Admit integer 15..480 targets only when the delta is divisible by 15 and unchanged start plus target remains within the same date; all local denials make zero request. |
| Requested duration is shown as fact | Keep target visibly provisional and show committed duration/end only after an exact fresh read. |
| Conflict or break warnings are bypassed | Reuse the backend-owned proposal. Blocked proposals expose no confirm; warnings require visible staff confirmation. |
| Confirmation evidence is reconstructed | Preserve the server payload opaquely and change only existing acknowledgement fields; use the existing distinct confirmation idempotency key and allowlisted endpoint. |
| Time and duration submissions overlap | Share mutual exclusion across status, time and duration states; while one is active every other submission is disabled. |
| Escape closes Reception One behind the dialog | Suppress workspace Escape while the proposal dialog owns cancellation and restore focus to the duration selector. |
| Cancellation, stale rejection, failure or interruption leaves an optimistic end | Fresh-read and reconcile before re-enabling; only the exact fresh appointment may update duration/end. |
| Raw compatibility update bypasses the kernel | Static and route-intercepted guards require zero raw `PUT` and zero unexpected mutation routes. |
| Synthetic evidence is described as live | Label intercepted cases `route_intercepted_browser`; make no backend/database/provider claim. |

## API Spine preservation

This remains a consumer-only use of the existing REST update command family.
GraphQL is read-only. Existing proposal and confirmation schemas already admit
`duration_minutes`; actor/practice authority, schedule conflicts, freshness,
version, idempotency, audit and atomic commit remain unchanged. No OpenAPI or
generated-client change is required.

## Residual boundary

Fresh UI reconciliation cannot make a stale resize safe; command-time backend
authority and source truth remain decisive. This proves only provider-free
authored-synthetic client composition. Cross-day/cross-practitioner movement,
full edit, real product operation, restart/unknown-commit recovery, deployment
and production remain unproved and closed.

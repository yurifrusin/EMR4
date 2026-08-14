# Reception One selected-appointment practitioner reassignment threat-model delta

Date: 2026-08-14

Timestamp: 2026-08-14T12:47:51+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: accepted projection-neutral truth kernel, active-practitioner
directory read and native Diary update proposal/confirm compositions

## Changed surface

This tranche adds one internal-staff practitioner-reassignment affordance to
Reception One. It adds no write authority. The bridge fixes start and duration
deltas at zero, admits one target from a fresh authenticated practice-scoped
active-practitioner directory and delegates to `handleMoveResize`, whose
existing update proposal/confirm path remains the sole owner of admission and
commit.

## Threats and required controls

| Threat | Required control |
|---|---|
| Reception One becomes a second reassignment implementation | The bridge validates one target, supplies literal zero `deltaStart` and `deltaDuration`, and calls `handleMoveResize`; reject bridge-local update route, proposal, confirm, signing, idempotency or raw `PUT` code. |
| An inactive, other-practice, stale or fabricated practitioner becomes selectable | Render only rows marked `active === true` by the existing authenticated practice-scoped directory; immediately re-read and require exactly one matching active row before delegation. |
| Template or client display data is mistaken for authority | Template-only rows may explain the grid but cannot become Reception One reassignment targets. Directory failure, ambiguity, missing active proof or the accepted 200-row limit fails closed. |
| Reassignment intent shifts date, time, duration or another field | Read exact current appointment truth, supply both deltas as zero and compare all frozen fields after every outcome. |
| Arbitrary practitioner id is injected into the command | Resolve only the exact freshly admitted directory id into the target column/reference; reject same, blank, malformed, unlisted and duplicate targets with zero proposal. |
| Roster or schedule conflict is bypassed | Reuse the backend-owned update proposal. Blocked proposals expose no confirm; warnings require visible staff confirmation and confirm-time revalidation. |
| Requested practitioner is shown as fact | Keep the target visibly provisional and display it as committed only after an exact fresh appointment read. |
| Confirmation evidence is reconstructed | Preserve the server payload opaquely and change only accepted acknowledgement fields; use the existing distinct confirmation idempotency key and allowlisted endpoint. |
| Selected-appointment actions overlap | Share mutual exclusion across status, time, duration and practitioner states; interruption requires fresh reconciliation before re-enabling. |
| Escape closes Reception One behind the dialog | Suppress workspace Escape while the proposal dialog owns cancellation and restore focus to the practitioner selector. |
| Failure or interruption leaves an optimistic practitioner | Exact-read and reconcile after every terminal result; withhold terminal bridge callbacks until the required read succeeds. |
| Compatibility update bypasses the truth kernel | Static and route-intercepted guards require zero raw `PUT` and zero unexpected mutation routes. |
| Synthetic evidence is described as live | Label intercepted cases `route_intercepted_browser`; make no live backend/database/provider claim. |

## API Spine preservation

This remains a consumer-only use of the existing REST update command family.
GraphQL stays read-only. Existing proposal and confirmation schemas already
admit `practitioner_id`; actor/practice authority, practitioner existence and
activity, schedule conflicts, freshness, version, idempotency, audit and atomic
commit remain backend owned. No OpenAPI or generated-client change is required.

## Residual boundary

A fresh directory projection reduces stale client choice but cannot authorize a
write. Command-time backend authority and source truth remain decisive. This
proves only provider-free authored-synthetic client composition. Directory
pagination beyond the accepted 200-row cap, cross-day/time/duration movement,
full edit, real product operation, deployment and production remain unproved
and closed.

# Provider-free read-only status-confirm route-mounting admission review

Date: 2026-08-12

Source HEAD: `d5684d934f80d1db49030b27b34b1b59a0c87f82`

Result: `raisa_provider_free_read_only_status_confirm_route_mounting_admission_review_pass`

Verdict: `mounted_legacy_route_not_admitted_for_physical_convergence`

## Decision

The endpoint is literally mounted, and its exact physical PostgreSQL seam is
already proved. The unchanged mounted handler is nevertheless not admitted
onto that seam: seven composition gaps remain blocking, one API-path matter is
partial, and two foundations are satisfied. No durability work is reopened.

## Exact admission matrix

| Dimension | Classification | Observation | Narrowest prerequisite |
|---|---|---|---|
| Literal route mounting | `satisfied` | The appointments router is included by the application and exposes POST /api/v1/appointments/proposals/status-confirm. | None for literal mounting; do not mistake this fact for physical-seam admission. |
| Canonical API identity and current alias | `partial_gap` | The operation identity is frozen, but the mounted hyphenated path remains only a documented alias candidate for canonical /appointments/proposals/status/confirm. | The unmounted composition must preserve confirmAppointmentStatusProposal and defer any path migration or alias decision. |
| Physical transaction-seam composition | `blocking_gap` | The physical seam exists, but the mounted handler imports and calls the legacy idempotency service and never imports or calls the seam. | Build an unmounted composition callable that maps admitted transport input into status_confirm_locked_transaction without changing the mounted route. |
| Current authority and server-session ingress | `blocking_gap` | Dependencies authenticate active user, tenant and role before the handler, but provide no server-session binding or in-transaction current-authority callback; legacy replay can return first. | Inject a server-only session binding and side-effect-free current-authority callback into the unmounted composition, with no client authority fields. |
| Status-only discrimination | `blocking_gap` | The mounted schema accepts a status-or-waiting-area union while the accepted pure adapter rejects anything except update_appointment_status/status. | Place the accepted status-only discriminator before physical request construction and retain waiting-area behavior outside the seam. |
| Locked source version, warnings and terminal policy | `blocking_gap` | A durable appointment state version now exists and the pure adapter defines exact warnings and terminal deferral, but the mounted handler concatenates warnings and does not call that adapter under the lock. | Recompute the transport-to-kernel decision against the locked appointment and pass the accepted adapter output unchanged into the seam. |
| Atomic audit and private-receipt correlation | `blocking_gap` | The mounted route stages mutation, audit and legacy completion before one commit, but discards the returned audit identity and does not populate the v1 private receipt fields. | Have the unmounted effect callback return the audit identity and complete only through the physical seam's v1 correlation checks. |
| Canonical stored-receipt delivery | `blocking_gap` | The legacy service stores JSON and replay returns it, while initial success returns a separately held response object; the physical seam instead exposes canonical bytes but the handler does not map them. | Define one unmounted public-envelope mapper that consumes only the physical decision's canonical stored bytes for initial and replay delivery. |
| Physical outcome to public response mapping | `blocking_gap` | The seam defines physical decisions and fail-closed exceptions, but the mounted handler has no composition or mapping for them and continues its legacy response paths. | Freeze and rehearse a closed, unmounted mapper for execute, replay, conflicts, incomplete scaffolds, revoked authority and unavailable targets. |
| Accepted physical durability foundation | `satisfied` | The accepted disposable PostgreSQL rehearsal passed all sixteen serial behavior, authority, receipt, revocation and rollback scenarios with complete cleanup. | None; consume this evidence without reopening concurrency, restart or unknown-commit claims. |

## Evidence boundary

All 10 exact source hashes matched; all 25 structural assertions passed; all 45 hostile mutations were rejected.

No application import/edit, route or database execution, provider call,
product or patient data, deployment, release, Pages or protected-ref action
occurred.

## Next safe candidate

Rehearse one provider-free unmounted composition callable joining the
accepted status-only adapter, server authority/session ingress, physical
transaction seam and closed public-response mapper. It must not edit or mount
the live route.

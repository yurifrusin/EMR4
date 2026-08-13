# Reception One selected-appointment time-reschedule threat-model delta

Date: 2026-08-14

Timestamp: 2026-08-14T07:51:51+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: accepted projection-neutral truth kernel, visible native
Diary update proposal/confirm interaction and Yuri's selected reschedule
direction

## Changed surface

This tranche adds one internal staff time-selection affordance to Reception
One. It adds no write authority. The affordance delegates to the ordinary
Diary's existing `handleMoveResize` interaction, whose update proposal/confirm
path and backend transaction remain the sole owners of admission and commit.

## Threats and required controls

| Threat | Required control |
|---|---|
| Reception One becomes a second update implementation | The bridge validates id and `HH:MM`, computes a start delta, fixes duration delta to zero and calls `handleMoveResize`; mechanically reject bridge-local fetch, route, proposal, confirm, signing, idempotency or raw PUT code. |
| Time selection is mistaken for reserved or committed truth | Label it as a proposed time, retain current coordinates until commit, and show success only after a fresh authoritative read. |
| Hidden fields drift during a time-only action | Freeze date, practitioner, duration, patient linkage, type, location, status, waiting area, reason, notes and channel; paired evidence compares all of them after every outcome. |
| Stale or out-of-scope appointment is acted upon | Resolve the exact id from the current client snapshot immediately before delegation; fail closed when absent and rely on command-time backend authority and source-truth revalidation. |
| Confirmation evidence is reconstructed or weakened | Preserve server-generated confirm payload opaquely and alter only `confirmed`; use the existing distinct confirmation idempotency key and proposal-supplied allowlisted endpoint. |
| Warning or blocked proposal bypasses staff review | Reuse the existing accessible dialog; blocked proposals expose no confirm action and warning proposals require explicit confirmation. |
| Escape closes Reception One behind the dialog | Suppress workspace Escape while the proposal dialog owns cancellation; restore focus to the initiating time input. |
| Failure, cancellation or stale rejection leaves optimistic coordinates | Perform a fresh authoritative read after every terminal result and reconcile both projections before enabling another action. |
| Blur/visibility interruption duplicates work | Latch one action, enter privacy mode, start no duplicate and reconcile from fresh truth before re-enabling. |
| Raw compatibility update silently bypasses the kernel | Route interception and static guards assert zero `PUT /appointments/{id}` and zero unexpected mutations in every case. |
| Synthetic evidence is described as live | Label intercepted cases `route_intercepted_browser` and static fixtures `authored_synthetic_client_fixture`; make no live backend/database/provider claim. |

## API Spine preservation

The change is a REST-command UI consumer. GraphQL remains read-only. The
existing update proposal/confirm family retains actor, practice, confirmer,
freshness, version, idempotency, audit and atomic-commit semantics. Events are
optional acceleration hints and never confirmation evidence.

## Residual boundary

Fresh UI reconciliation cannot make a stale command safe. Correctness remains
owned by the backend command-time authority and source-truth check. This tranche
proves only provider-free authored-synthetic client composition. Cross-day,
cross-practitioner and duration changes, real product operation, restart or
unknown-commit recovery, deployment and production remain unproved and closed.

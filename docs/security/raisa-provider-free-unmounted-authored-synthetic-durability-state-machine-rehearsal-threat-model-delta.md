# Threat-model delta: unmounted durability state-machine rehearsal

Date: 2026-08-06

Status: frozen provider-free implementation delta

## Trust boundaries and assets

Untrusted inputs are claimed source/practice/generation coordinates, positions,
predecessors, observation digests, aggregate revisions, decision/reason codes,
affected frame types, copied state, key intervals, restart claims, retention
claims and serialized evidence.

Protected assets are tenant/source isolation, last contiguous checkpoint,
monotonic stale-frame state, obligation uniqueness, receipt identity, minimized
audit, key-schedule integrity and separation from product/read/command/runtime
authority.

## Threats and controls

| Threat | Control |
|---|---|
| Caller declares a duplicate to suppress work | Redelivery is derived only from an exact stored receipt and constant-time digest match. |
| Caller chooses checkpoint disposition | Closed decisions map internally to fixed dispositions; disposition is not an input field. |
| Checkpoint advances after a partial failure | Copy-on-transition staging plus five member-specific injected failures must return byte-equivalent original state. |
| Gap is treated as a known full invalidation | Gap holds the last contiguous position, commits conservative retirement and enters `REBASE_REQUIRED`. |
| Irrelevant event silently skips receipt/audit | Contiguous no-intersection still commits immutable receipt, minimized audit and checkpoint advancement. |
| Watermark rollback makes a stale frame current | Watermarks use `max`; lifecycle has no `RETIRED` to `CURRENT` edge. |
| Duplicate obligations reveal repeated events | One obligation per opaque frame-generation id; later causes coalesce into rolling digest and closed count bucket. |
| Frame/session identity leaks through obligation | Opaque generation id and closed frame type only; no user/session/source alias. |
| Same source position is replaced | Mismatched digest at a classified position is corruption and forces rebase. |
| Observation digest is reused at a new position | Digest index makes reuse corruption and forces rebase. |
| Restart trusts a copied or stale checkpoint | Recompute full state integrity digest, then require equality to a separately trusted recovery anchor before exact-next-position resume. |
| Corrupt restart state supplies its own supposedly prior coordinate | Integrity failure returns `NEW_GENERATION_REQUIRED` with no successor state and adopts no candidate coordinate. |
| Restart skips a missing retained row | Unavailable/non-contiguous next row fully invalidates and requires a new generation. |
| Key schedule overlap or gap chooses an arbitrary key | Validate one ordered gap-free interval partition and resolve exactly one key; never try all keys. |
| Routine key rotation changes history or drops the predecessor key early | Validate one atomic successor schedule at a strictly future position fence; historical intervals remain identical and predecessor-key availability covers all retained dependencies plus safety overlap. |
| Key bytes leak into evidence | Key schedule carries opaque ids/positions only; schema prohibits material recursively. |
| Caller omits the slowest generation to authorize purge | Retention consumes the integrity-bound complete state census, verifies its independent registry/census digest and denies omission, duplication or filtering. |
| Fast checkpoint authorizes unsafe purge | Retention uses the minimum exact non-consumed checkpoint from the complete census plus pins, key overlap and grace. |
| Wall clock or existing event TTL drives purge | Retention inputs contain no event expiry; output is inert eligibility, not deletion. |
| Audit becomes context or command evidence | Closed privacy-safe fields and explicit false authority ceilings. |
| Synthetic fixture smuggles product or free text | Recursively closed schemas plus prohibited-key traversal and adversarial tests. |
| Pure script is imported as application runtime | Static boundary tests forbid `app/**`, migration/API changes and runtime/persistence imports. |
| Passing rehearsal is claimed as live durability | Exact unmounted authored-synthetic evidence label and explicit later migration/runtime gate. |

## Residual risks deliberately deferred

PostgreSQL schema, constraints, transaction isolation, rollback and locking;
RLS/roles; producer availability; operational credentials/key storage; process
concurrency; actual crash recovery; retention capacity; monitoring; database-
backed acceptance; deployment and privacy assessment remain later gates.

## Forbidden openings

No protected holdout, historical PHI, patient/clinical/financial/product data,
raw audit, live database/outbox/feed/watcher/listener/source, migration,
table/view/function/trigger/sequence/role/credential, route, GraphQL/REST
change, operational checkpoint/persistence, provider/model call, command/write,
runtime wiring, deployment, production, release, Pages or protected-ref
movement. Preserve and exclude `docs/branding/` and unrelated untracked files.

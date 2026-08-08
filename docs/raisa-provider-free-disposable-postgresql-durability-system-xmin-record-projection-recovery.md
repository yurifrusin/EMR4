# Disposable PostgreSQL durability system-`xmin` record-projection recovery

Date: 2026-08-09

Status: bounded recovery candidate; behavior runtime remains unaccepted

## Observed failure

Behavior attempt 019 admitted the exact corrected artifact, reproduced the
accepted catalogue and fixture closure, then stopped at `BTR-E01` with
SQLSTATE `42703` before any scenario passed. Exact-ID cleanup removed the newly
owned networkless PostgreSQL 16 container and verified its absence.

One fresh diagnosis-only container reproduced the same bounded failure. Its
ephemeral verbose PostgreSQL coordinate identified
`emr4_context_fabric.cf_fence_stream_head_v1`, line 33: the deferred trigger
loaded a stream-head row into a named table-composite local and then evaluated
`(final_head).xmin`. PostgreSQL table-composite values contain user columns;
the system column `xmin` is available only when the exact query projects it
into a record-shaped result.

The raw server message was not persisted. The safe function, line, relation
type and column coordinate are preserved in the diagnosis receipt, together
with the exact failure-evidence digest and cleanup proof.

## Complete static reconciliation

The first line was one instance of a shared typed-projection defect. Fourteen
`SYSTEM_XMIN` expressions consumed local symbols whose exact reads omitted
`xmin`:

- the common stream-head and outbox reads in the four producer membership
  fences;
- the alias and outbox reads in the alias fence;
- the stream-head and outbox reads in the stream-head fence; and
- the common stream-head and outbox reads in the outbox fence.

All fourteen derive from three closed projection lists: alias, stream head and
outbox. No scenario, principal, transaction, RLS policy, table privilege,
failure meaning or effect set needs to change.

## Narrow repair

The typed trigger programme now:

1. includes PostgreSQL system `xmin` in the exact alias, stream-head and outbox
   projection lists;
2. preserves the existing user-column order and all predicates;
3. causes the inert renderer to declare every corresponding local as
   `record`, so named fields and system `xmin` are both addressable; and
4. adds a validator invariant: a `SYSTEM_XMIN` expression over a `LOCAL` row
   is invalid unless the definitely assigned exact read projected `xmin`.

The regenerated typed body contract is
`sha256:8ede994ba6f9bbeade0eb015bb9dd23dade21934e7c70fa6885a4a67654aab18`
at exact source HEAD `73322f3d86d44f997c054331e06c3017831b345f`.
Its unchanged corrected structural parent remains
`sha256:d481b991fa2d6835babe8372722d00775b31432802bdf9ec40e007369b0d34c6`.

The validator rule closes the class of defect at the architecture boundary.
It does not rely on a later SQL string check. A hostile test removes `xmin`
from one exact reload and requires `xmin_not_selected`; renderer tests require
the affected record locals and their system-column references.

## Required descendant sequence

Before another behavior attempt:

1. regenerate and validate the typed body contract and schema;
2. commit the exact body recovery source so its source HEAD is stable;
3. rebind and regenerate the inert SQL, render manifest and lowering contract;
4. rerun the disposable parse/catalogue gate and bind its accepted evidence;
5. rebind the unchanged twenty-scenario behavior contract;
6. pass the full deterministic and hostile packet plus one fresh exact-HEAD
   Gemini 3.6 Flash/high veto; and
7. run the next behavior attempt once in a fresh owned container.

Every prior failure and diagnosis artifact remains immutable. The mutable
current evidence is not acceptance evidence unless a later complete run
passes all twenty scenarios and exact cleanup.

## Claim and authority boundary

This recovery proves only the representable typed path for selected system-
`xmin` reads after its descendant gates pass. It does not yet prove any
function, trigger, RLS, replay or rollback behavior.

Applied migration, operational database or credentials, durable persistence,
watcher/listener/feed, application/API/Diary wiring, real context,
patient/clinical/product/protected data, provider/model calls, executable tools
or commands, deployment, production, release, Pages and protected refs remain
closed.

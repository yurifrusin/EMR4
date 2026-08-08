# Disposable PostgreSQL behavior rehearsal implementation recovery

Date: 2026-08-08

Status: implementation candidate; fresh exact-HEAD veto required before runtime

## Finding

The accepted planning packet assigned `BTR-T03` to `context_producer` and asked
that role to update the committed Fabric alias so the alias guard would return
`CF601`. The same packet correctly forbids any direct Fabric DML grant. Native
PostgreSQL privilege checking therefore makes that draft path unreachable: the
producer would receive standard privilege denial `42501` before the alias
trigger could execute.

This was a deterministic pre-runtime finding. No container, database or
scenario was started and no evidence claim was released.

The same body reconciliation found that `BTR-T02`'s same-transaction event
deletion is intentionally stopped immediately by `cf_guard_event_v1` as
`F_IMMUTABLE` / `CF601`; it cannot reach the draft's deferred `CF603`. The
corrected scenario now proves that stronger immediate guard, while `BTR-T01`
remains the distinct deferred temporal-bijection `CF603` proof.

## Closed correction

`BTR-T03` retains the same producer principal, trigger category, `CF601`
failure, outer rollback and zero-delta evidence boundary, but now attempts to
update the already committed authored-synthetic `diary_committed_events` row.
The producer already holds the accepted fixture-only application-table update
grant, so the existing committed-event immutable guard is reachable. The
producer receives no new privilege and still cannot update the Fabric alias.

The correction changes no application relation, parent Fabric SQL, trigger,
function, role, RLS policy, runtime surface or claim breadth. It preserves the
stronger architectural property: aliases remain owner-private while reachable
producer authority is stopped by the event immutability trigger.

## Additional containment correction

Implementation review also rejected reuse of the parent catalogue harness's
synthetic initialization password. The behavior harness now starts the exact
local image with an inert argv entrypoint, initializes PostgreSQL with local
peer authentication and host authentication set to `reject`, maps only the
container's fixed `root`/`postgres` operating-system users to the fixed
bootstrap role, and listens only on the container-local Unix socket. It sets
no `POSTGRES_*` credential environment and uses neither trust authentication
nor a role password.

## Gate

The contract hash and exact implementation packet must be recomputed, all
deterministic and hostile tests must pass, and a fresh read-only exact-HEAD
Gemini 3.6 Flash/high veto must accept the corrected packet before the one
authorized disposable PostgreSQL run can begin.

## First runtime failure and bounded repair

After deterministic acceptance and an exact-HEAD independent pass, the first
authorised disposable run failed closed at `catalogue/server_or_database`
before all 20 scenarios. The container was removed and absence was verified.
The immutable failure evidence is
`provider-free-behavior-transaction-failure-evidence-001.json`.

The descendant had reused a parent catalogue assertion whose otherwise useful
structural checks include the parent's distinct disposable database-name
sentinel. The bounded repair now proves `emr4_synthetic_behavior` and
PostgreSQL 16 independently, normalizes only a deep copy to the parent's
private sentinel, and then invokes the unchanged parent structural assertion.
AER-0115 records the error and prevention control. No second run is eligible
until the repair receives deterministic acceptance and a fresh exact-HEAD
independent veto.

## Second runtime failure and bounded repair

The corrected database-binding run passed catalogue reconciliation and then
failed closed during fixture bootstrap, again before any behavior scenario.
The immutable second failure is preserved as
`provider-free-behavior-transaction-failure-evidence-002.json`; exact container
cleanup and absence were verified.

Foreign-key tracing found that the beta-practice isolation fixture omitted the
generation-registry barrier required by its observer generation and the
durability checkpoint required by its invalidation watermark. The repair makes
the entire beta fixture an explicit CTE dependency chain from barrier through
generation, checkpoint, frame, watermark and obligation. No application or
Fabric production DDL changed. AER-0116 records the failure, and a third run is
closed until the repaired exact HEAD receives a fresh independent veto.

## Third runtime failure and diagnostic strengthening

The dependency-chain candidate still failed at the generic fixture/bootstrap
boundary, before any scenario, with verified cleanup. Failure evidence 003 is
preserved. This means the foreign-key omissions were real structural defects
but were not established as the sole runtime cause; AER-0117 corrects that
overclaim.

The harness had captured verbose psql output but intentionally discarded it in
order to prevent SQL or messages from leaving the container. It also discarded
the safe SQLSTATE needed to distinguish this recurring boundary. The next
bounded candidate releases only one unambiguous five-character SQLSTATE from a
tightly anchored psql error line, hashes the otherwise empty safe detail and
continues to release no SQL, rows or error prose. AER-0118 records that harness
gap. The diagnostic run remains closed until fresh deterministic and
independent acceptance.

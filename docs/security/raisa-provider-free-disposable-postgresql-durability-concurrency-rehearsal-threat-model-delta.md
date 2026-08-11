# Threat-model delta: disposable PostgreSQL durability concurrency rehearsal

Date: 2026-08-11

Status: `candidate_planning_control_runtime_closed`

## Scope change

The accepted parent proved twenty scenarios serially. CF-D1 permits two fixed
least-privilege PostgreSQL sessions to overlap inside one newly owned
networkless disposable PostgreSQL 16 container. It introduces no product,
provider, operational database, migration, deployment or production surface.

## Assets

- exact accepted SQL, catalogue and privilege identity;
- generation, stream position, admission and receipt uniqueness;
- transaction atomicity across application-shaped and Fabric fixture rows;
- principal, practice, source, stream and generation binding;
- monotone checkpoint, watermark, frame, obligation and audit effects;
- bounded concurrency evidence and exact cleanup ownership.

## New trust boundaries

1. the host scheduler to two independent `psql` participant processes;
2. participant A's uncommitted locks to participant B's wait and result;
3. privileged `pg_stat_activity` observation to minimized wait-state evidence;
4. PostgreSQL serialization/unique-conflict behavior to the harness outcome
   classifier; and
5. post-race privileged readback to closed repository evidence.

## Threats and controls

| Threat | Control | Required evidence |
|---|---|---|
| Sequential execution is mislabelled concurrent | A must be observed at exact post-function `Timeout/PgSleep`, then B at exact `Lock` wait before A ends | Both closed observations true within fixed ceilings |
| Timing or scheduler jitter chooses an unintended winner | A is launched and proven inside the post-function hold before B starts | Exact participant labels and deterministic A leadership |
| Long-held transaction becomes a denial-of-service path | Fixed short hold plus statement, lock, idle and whole-run ceilings; no external work in transaction | Bounded durations and no timeout/deadlock |
| Different lock order deadlocks sessions | Exercise accepted entry-point order only; `40P01` is never an allowed result | Zero deadlocks and exact expected outcomes |
| Serializable loser is silently retried or double-applied | No participant retry; only a separate fixed post-race replay is allowed | One `40001`, one durable effect, one inert replay where specified |
| Unique race creates duplicate generation, admission, receipt or source position | Exact unique coordinates plus complete row-count and digest readback | Exact frozen counts/digests and contiguous positions |
| Losing transaction leaves partial application/Fabric members | Fresh post-race full selected-set readback | Zero loser residue and atomic winner effect |
| Divergent admission overwrites the first winner | Fixed A packet, exact B packet, `CF004` during invisible-winner race, then one bounded fresh conflict | One immutable PRIMARY plus one stable CONFLICT |
| Rollback winner leaks before the waiting contender commits | Fixed `P0001` before A commit and fresh readback after B | Only B's single transition effect remains |
| Role or tenant scope widens under overlap | One `SET SESSION AUTHORIZATION`, accepted bindings, forced RLS, closed locators and parent privilege packet | Expected session roles; no beta/unbound visibility or mutation |
| Observer leaks query/PID/lock details | Exact `pg_stat_activity` projection maps to closed wait classes in memory | Evidence contains no PID, query, lock key or raw row |
| Parent or fixture changes disguise a result | Exact path/hash and pre/post catalogue/privilege binding | All parent and catalogue digests match |
| Cleanup deletes another object or leaves state | Captured ID plus exact ownership/name/nonce/image/network/mount reverification | Exact-ID removal and exact-ID absence |

## STRIDE summary

- **Spoofing:** exact session identity and fixed application labels prevent
  participant substitution.
- **Tampering:** parent hashes, row-set digests and catalogue equality expose
  changed SQL or partial effects.
- **Repudiation:** scenario/participant labels, SQLSTATEs and before/after
  digests bind each result without raw logs.
- **Information disclosure:** forced RLS, opaque fixtures and closed wait-state
  mapping prevent broad row or activity disclosure.
- **Denial of service:** two sessions, short holds and fixed timeouts bound lock
  contention; `40P01` and timeouts fail closed.
- **Elevation of privilege:** runtime roles retain no membership, inheritance,
  `BYPASSRLS`, direct Fabric DML or foreign entry-point authority.

## Residual risks deliberately deferred

- server crash, restart and unknown client commit outcome;
- free-running or multi-party contention and arbitrary deadlock freedom;
- application retry/backoff and connection-pool behavior;
- migration locks, operational credentials and long-lived storage;
- key rotation, retention/purge, performance and monitoring;
- watcher/listener/source-feed behavior and application integration; and
- patient, clinical, product, provider, deployment and production safety.

## Stop conditions

Stop on wrong parent hash, catalogue drift, unexpected identity/isolation,
unproved overlap, unexpected wait class, timeout, `40P01`, unexpected SQLSTATE,
cross-practice visibility, duplicate or partial effect, evidence leakage,
containment mismatch or cleanup uncertainty.

No failure authorizes broader timing tolerances, missing wait evidence,
participant retries, weaker isolation, superuser substitution, parent SQL
editing, scenario removal, operational data, network access or provider use.

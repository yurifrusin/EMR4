# Disposable PostgreSQL durability concurrency rehearsal design

Date: 2026-08-11

Status: `candidate_planning_design_runtime_closed`

## Purpose

This design adds one controlled two-session layer above the accepted serial
Context Fabric behavior proof. It reuses the byte-identical PostgreSQL 16
artifact and closed authored-synthetic fixture namespace. It changes neither
the schema nor the application.

The selected spine is:

```text
exact parent and catalogue admission
  -> fixed synthetic bootstrap
  -> precondition transaction(s)
  -> participant A reaches the post-function hold
  -> participant B is observed waiting on the protected coordinate
  -> fixed A commit or injected rollback
  -> exact B result
  -> fresh replay/readback
  -> catalogue identity and exact-ID cleanup
```

The design follows consistent lock ordering, short transactions and least
privilege. It does not invent advisory application locks or treat timing as
proof.

## Harness structure

The implementation is a fixed-path Python harness. It imports only stable
containment, parent-validation, SQL-rendering and bounded-readback helpers from
the accepted serial rehearsal. It owns its concurrency scheduler, closed
scenario renderer, evidence schema and result logic.

The harness accepts no CLI inputs. Image, executable, container name prefix,
database, roles, entry points, fixture identifiers, SQL templates, scenario
order, timeouts, evidence path and cleanup target are code- or contract-fixed.
All subprocesses use argv arrays with `shell=False`.

## Connection model

Each race uses:

- participant A: fresh `psql`, exact `application_name`, one
  `SET SESSION AUTHORIZATION`, one top-level transaction;
- participant B: the same shape with a distinct exact label;
- observer: a fixed superuser query limited to `pg_stat_activity` rows whose
  `datname`, `application_name` and participant labels are exact; and
- readback: a new fixed privileged connection after both participants end.

There is no connection pool, prepared statement reuse, session reuse, role
inheritance or transaction retry. Maximum connection count is bounded and
checked. Participant SQL sets local statement, lock and idle-transaction
timeouts before invoking the accepted entry point.

## Observable concurrency barrier

Participant A executes its accepted function and immediately calls fixed
`pg_sleep` inside the same transaction. That sleep retains the function's row
locks. The harness polls the exact A label until PostgreSQL reports
`wait_event_type=Timeout` and `wait_event=PgSleep`. Only then does it start B.

The harness next polls the exact B label until PostgreSQL reports
`wait_event_type=Lock`. No raw query, PID, lock tuple or server log is retained.
The exact pair of closed states proves real overlap. If A completes before B is
observed waiting, the race is unproved and fails even if final row counts look
correct.

The hold is bounded and contains no external work. A participant may never
sleep before the target function because that would prove only simultaneous
connections, not contention on the target coordinate.

## Scenario setup and isolation

Scenarios use disjoint closed observer, appointment and command coordinates
except where the race deliberately shares one locator. Setup and precondition
transactions are committed before the race and are not counted as concurrent
results. Every scenario readback is taken after both participant processes
terminate.

`CFD1-C01`, `CFD1-C05` and `CFD1-C06` use `SERIALIZABLE`, matching the accepted
lifecycle and coordinator entry-point guard. `CFD1-C02`, `CFD1-C03` and
`CFD1-C04` use `READ COMMITTED`, matching the producer and observer guards.
No isolation level is weakened to obtain a pass.

## Expected PostgreSQL outcomes

### Serializable winner/loser

For registration and identical coordinator apply, B begins its serializable
snapshot while A's change is uncommitted and waits on A's row lock. After A
commits, PostgreSQL must abort B with exact `40001`. The harness does not retry
B automatically. A fresh named replay transaction proves the retained state.

For the rollback race, A's changes never commit. B's snapshot therefore
remains compatible with the durable database state after A releases the lock,
and B must commit the one transition.

### Read-committed serialization

For the two producer transactions, B re-evaluates the stream head after A
commits and receives the next contiguous position. Both commits are required.

For identical admission, the accepted `ON CONFLICT DO NOTHING` plus exact
reselection must return the retained PRIMARY to B. For divergent admission,
B's pre-winner execution must stop as exact `CF004`; only a fresh transaction
after the race may create the bounded CONFLICT.

## Lock order and deadlock boundary

The rehearsal observes the parent entry points' existing order; it adds no
business lock. Registration serializes at the registry barrier. Producer
projection serializes at the stream head. Coordinator application locks the
registry barrier before generation, checkpoint, admission/receipt and
downstream projection coordinates. Admission relies on its primary/conflict
unique coordinate and exact reselection.

Any PostgreSQL `40P01` is a tranche failure, not an allowed alternative.
Passing proves only the selected same-coordinate pairs and not arbitrary
deadlock freedom.

## Readback and evidence

Readback reuses the parent allowlisted relation set and adds no unrestricted
table dump. Per scenario it records:

- closed participant outcomes and SQLSTATEs;
- exact identity and isolation markers;
- `leader_post_function_hold_observed` and
  `contender_lock_wait_observed` booleans;
- bounded overlap duration;
- relation counts, positions and canonical ordered row-set digests before and
  after the race and after replay; and
- fixed invariants such as one primary, one receipt, contiguous positions and
  unchanged catalogue/privilege digests.

The process captures stderr only to extract an exact SQLSTATE and stable closed
reason. Raw error text is discarded and cannot enter repository evidence.

## Deliberate omissions

The container process is not stopped or restarted. Connections are not killed
at commit acknowledgement, storage is not persisted across a server lifecycle,
and no ambiguous client outcome is induced. Therefore CF-D1 makes no restart,
crash or unknown-commit claim.

It also omits more than two participants, free-running stress, performance,
key rotation, retention/purge, watcher/listener behavior, application wiring,
operational credentials, providers and real data. Those omissions keep the
first concurrency proof finite and deterministic.

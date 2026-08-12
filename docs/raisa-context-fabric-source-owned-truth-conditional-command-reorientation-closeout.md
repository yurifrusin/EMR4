# Context Fabric source-owned-truth reorientation closeout

Date: 2026-08-12

Result: `raisa_context_fabric_source_owned_truth_conditional_command_reorientation_pass`

Reviewed source: `037eed060d4519f2f3d6721135143ecb6f70e358`

## Outcome

The reorientation passes as repository-only architecture. The first Context
Fabric runtime no longer needs durable watcher delivery to keep appointment
records correct. Current truth and mutation serialization belong to the
authoritative source service. Context Frames remain minimal, expiring and
read-only. Events are acceleration hints that cause fresh authorised reads.
Commands recheck current authority and source truth atomically before mutation.

CF-D1 is retained as useful concurrency evidence. CF-D2 remains stopped and
unproved, but the function it was pursuing is not abandoned: **Durable Event
and Cue Delivery** is now an explicit later extension for restart recovery,
delivery observability and cue latency, not a prerequisite for command safety.

## Conditional-command boundary

The architecture keeps four evidence classes separate:

- a backend-minted freshness precondition;
- human or policy confirmation where the action requires it;
- idempotency identity; and
- audit attribution plus deterministic readback.

Update, status and delete lock and recheck the existing appointment. Create
cannot lock a row that does not yet exist, so every contender for the relevant
schedule-conflict domain must participate in deterministic database-owned
serialization and a final invariant check. A signed token without that
transactional fence does not close the race.

Only `committed` mutates. A same-digest idempotent replay returns the original
receipt. Stale, schedule-conflict, revoked-authority, confirmation-required,
validation and idempotency-conflict outcomes all fail closed with no mutation.

## Watcher topology

One logical watcher per database event partition can serve many users and fan
practice-scoped cues to their sessions. The first runtime may use one physical
watcher for the database. A later highly available deployment may use
active/standby replicas, but external lease/fencing ownership permits only one
checkpoint writer per partition. Brief duplicate observation during takeover
is handled with idempotent at-least-once delivery; two equal writers are not
the steady-state design.

## Legacy compatibility routes

The raw appointment create/update/status/delete routes remain mounted and
unchanged. Their migration target is one shared backend conditional-command
kernel, followed by client movement to the proposal/confirm envelope and route
retirement only after parity evidence. An implicit freshness check is useful on
every route but is not implicit human confirmation.

## Verification

- the closed contract and schema validate with zero canonical errors;
- all 28 independent hostile mutations fail closed;
- 53 focused architecture and API Spine tests pass;
- the canonical fast profile passes 191 tests, Ruff, compilation of 202
  maintained Python sources, Diary JavaScript syntax and Git whitespace;
- exact candidate `037eed060d4519f2f3d6721135143ecb6f70e358`
  received one read-only Sydney Vertex `gemini-2.5-flash` review with HTTP 200,
  no tools, no fallback and no P0-P2 finding; and
- the earlier ADC-expired attempt is preserved as a zero-call receipt: it sent
  no request and produced no model output.

## Claim and authority boundary

This proves a coherent architecture contract, not its runtime implementation.
No route, database, migration, source, watcher, worker, provider tool, patient
or product data, credential/IAM setting, executable, command/write, deployment,
production, release, Pages or protected ref was opened or changed. The provider
review received ordinary repository architecture only.

## Next safe descendant

The next dependency-satisfied tranche is the provider-free, unmounted
conditional-command admission rehearsal. It may instantiate authored-synthetic
preconditions, operation families, lock plans, typed outcomes and
compatibility-route classifications against this exact contract. It may not
change a route, open a database, consume an event, start a watcher, call a
provider or issue a command.

# Provider-free unmounted durability inert DDL rehearsal closeout

Date: 2026-08-07

Result: `raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_pass`

Accepted source HEAD: `46e16622471a192353cb82a33acf301dc2cfb7aa`

Canonical inert SQL artifact:
`sha256:92d234f8f57d5492e0c4215f9c0d3c54efe9e9ec9cbdaa9b4321a5120b983012`

## Accepted result

The two immutable durability parents now have one closed, deterministic and
provider-free compiler into a repository-local PostgreSQL-16 DDL evidence
artifact. The compiler verifies both parent hashes, applies the exact accepted
structural recovery plus the position-sealed PostgreSQL-representability
recovery, emits only the fixed `.sql.inert` path and independently recognizes
the resulting closed SQL subset. It has no database driver, connection,
general SQL input, migration path or caller-selected output.

The canonical artifact is 1,405,495 bytes and 412 statements. It contains the
exact nine entry points, fourteen recovered trigger functions and fourteen
trigger declarations, eighteen fabric relations, forty-four forced-RLS
policies and the accepted privilege ceilings. Seven immediate guards use
ordinary triggers and seven deferred fences use PostgreSQL-16 constraint
triggers. The support helper precedes every policy. The schema, thirty-two
fabric types/domains and all eighteen fabric relations reach their exact
non-login owner, while no application-table owner changes and no runtime schema
`CREATE` grant are emitted.

## PostgreSQL-representability recovery

The first DeepSeek implementation and its one bounded correction remain
rejected evidence. Sol's source and rendered-byte audit found nullable empty-
set counting, policy-before-helper order, invalid deferred-trigger syntax,
incomplete ownership closure, six impossible trigger-row `xmin` references
and an appointment applicability defect that would have obstructed ordinary
non-producer updates.

The accepted recovery uses null-safe bigint counts, orders the helper before
all policies, emits valid immediate and deferred trigger families, closes all
owners and fails unknown lock modes before emission. Four immediate guards
reselect the exact keyed physical row's `xmin` before effect. Three deferred
fences instead bind only the narrow fact already discharged by their mandatory
same-table immediate guard. An additional appointment guard preserves zero-
binding ordinary writers, executes the proof for exactly one producer binding
and fails duplicate bindings with value-free `F_CARDINALITY`/`CF004`.

All eight effective-body transformations bind exact old/new fragment seals and
affected node positions. No `OLD.xmin` or `NEW.xmin` survives. Every one of the
22 immutable parent programs remains accounted for; the sole addition is the
appointment guard, producing 23 effective programs.

## Evidence

- The merged exact candidate passed 62/62 implementation, plan and recovery
  tests; canonical regeneration returned `check: ok`; Ruff and Git whitespace
  checks passed.
- One fresh `gemini-3.6-flash-high`/high exact-HEAD veto independently
  recomputed the 22-to-23 program change, six removed trigger-row `xmin` sites,
  four keyed reselections, three paired-guard dependencies, all eight recovery
  seals, the 7+7 trigger split, owner closure and privilege ceilings.
- The verifier returned one schema-constrained `pass`, found no P0-P3 issue and
  left its exact review worktree clean and unchanged.
- AER-0087 through AER-0091 preserve the failed adapter probe, two materially
  incorrect worker `candidate_ready` claims and two orchestrator preflight HEAD
  binding errors. Register revision 84 closes them with Sol recovery, fresh
  veto and a mandatory literal `git rev-parse HEAD` rule.
- Local and origin protected `master` and `handoff/current` remained fixed at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`. No protected ref moved.

## Closed boundaries

The artifact was never sent to PostgreSQL. This tranche created no migration,
schema, role, function, trigger, table, policy or privilege in a database and
proved no server parse, catalogue acceptance, RLS, trigger behavior,
concurrency, rollback, retry, migration or production safety. It opened no
database/source/outbox/feed/watcher/listener contact, product or patient data,
provider product path, API/Diary change, command/write authority, operational
persistence, runtime wiring, deployment, production, release, Pages rebuild or
protected-ref movement.

## Next safe descendant

Under the standing uninterrupted-development authority, the next planned safe
descendant is a separately bounded provider-free disposable local PostgreSQL-16
parse-and-catalogue rehearsal. Its first action is to freeze a fail-closed plan
that admits only the accepted inert artifact and synthetic prerequisite stubs,
uses an owned disposable database cluster, performs no application migration or
runtime wiring, and proves complete cleanup. Applied Alembic migration,
application transaction behavior, concurrency, live sources, product/patient
data, operational credentials, commands, deployment and production remain
later separate gates.

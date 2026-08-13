# CF-D2 event and cue PostgreSQL parse/catalogue rehearsal — paired closeout

Date: 2026-08-13

Timestamp: 2026-08-13T19:56:16+10:00 (Australia/Brisbane)

Status: accepted and continuing

## Lay summary

The database has now answered the next concrete question: the exact event/cue
schema we designed is valid PostgreSQL 16 and becomes precisely the empty set
of tables and safeguards we intended. The database was a temporary sealed
workbench with no network and no durable disk; after the inspection it was
destroyed and its absence verified.

The first attempt found a small but useful workflow defect. Docker's simple
"ready" signal arrived a moment before an authenticated SQL query was ready.
Nothing had been installed, and cleanup succeeded. The harness now waits for
three consecutive authenticated checks, and the fresh attempt passed. That
failure remains recorded rather than being erased.

What this gives us is confidence that the design is physically representable,
not yet that every multi-step event transaction behaves correctly. Events and
cues are still only prompts to refresh from current source truth; they cannot
make or confirm appointments.

## Technical summary

- Accepted source: `579e9e0e86bd92469d82eb1199e8b3120808844e`.
- Exact input: SHA-256
  `3eebbe132b195ccab2f00283ad20f04c521fa6116bb30d0f38ab49158db1ebd6`,
  12,022 bytes, 18 statements.
- Environment: exact cached `postgres:16-bookworm`, `--pull=never`,
  `--network=none`, no port, tmpfs data only, exact-ID cleanup.
- Catalogue: 3 domains, 7 tables, 50 fields, 7 PKs, 3 unique keys, 18 table
  checks, 7 FKs, zero unexpected executable objects and zero rows.
- Attempt 001: readiness-race stop before SQL; cleanup verified; preserved as
  AER-0293.
- Attempt 002: three authenticated PostgreSQL-16 observations, exact install,
  exact catalogue, zero rows and cleanup all passed.
- Verification: 64 hostile contract rejections, 12 focused checks, 245
  register/focused checks, repaired 48-test latch suite, 193 canonical fast
  tests, 209 maintained Python sources compiled, Diary JavaScript and
  whitespace passed.

## Deliberately closed

No existing database or source, watcher runtime, persistent storage, patient
or product data, provider, credentials/IAM, external network, application
route, command/write, deployment, production, release, Pages or protected ref
was opened. The run proves no concurrency, restart, unknown-commit or
operational-retention behavior.

## Place in the Raisa direction

The result moves CF-D2 from an abstract event/cue shape and inert SQL text to a
schema PostgreSQL can actually represent, while preserving the more important
source-owned-truth rule. We are building a reliable cue-and-reconciliation
layer around the Diary, not a second source of Diary truth.

## Planned next tranche

Freeze and execute the narrowest provider-free disposable PostgreSQL behavior/
transaction rehearsal for the five existing protocols: terminal admission,
pending coalescing, contiguous checkpoint advance, dispatch recording and
reconciliation. Runtime wiring, product data and operational durability remain
later gates.

Yuri's attention is not required; the authorised sequence continues.

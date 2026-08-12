# Provider-free disposable PostgreSQL status-confirm scaffold parse/catalogue rehearsal plan

Date: 2026-08-12

Source HEAD: `163e0403cc3f18ebb2fbd0e47e14d01abf2554b6`

Status: `frozen_for_provider_free_disposable_postgresql_execution`

Reasoning level: material database execution / Extra High

## Purpose

Ask one locally present, disposable PostgreSQL 16 server whether exact migration
`w2x3y4z5a6b7` lowers, parses and installs over the minimum authored-synthetic
prerequisite shapes; whether the resulting columns, constraints, function,
trigger and Alembic head match the accepted scaffold; and whether a bounded set
of transactionally rolled-back invariant probes behaves fail closed.

This is not an application database, route, command or deployment. The server,
data directory and all values are disposable and owned by this one rehearsal.

## API Spine classification

This is private REST-command physical evidence only. Public OpenAPI is unchanged,
GraphQL remains read-only and no event gains command authority. Catalogue facts
and probe results are evidence, never product truth or a receipt.

## Exact source bindings

Only these exact non-protected inputs may be read, hashed or searched:

| SHA-256 | File |
|---|---|
| `f7e90fac3a470300be9b728668f55f459408e98c24e5c04e4ec281ae3632df1c` | `docs/raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-scaffold-closeout.md` |
| `3159e88b74163747a0bcb09e6075310c3517ddc9575d6bd1d16f2a62238ac3de` | `orchestration/agent_inbox/codex/raisa-status-confirm-physical-schema-transaction-scaffold-sol-acceptance.md` |
| `16301ce02d9cd764452f16c0a0dc467bf2182d6953883d214bb7a13b993c14a0` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-scaffold/scaffold-contract.json` |
| `bfa72b627061b8e477903ec9fc2cfbb35a4970b26ab7115db18c3daef1d3696c` | `alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py` |
| `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` | `app/models/appointments.py` |
| `8a70641ffa66bb1c228e16a62d8b7a2111810888819c9c662c17ea72e2d70b49` | `alembic.ini` |
| `5f8f7f752287ce47b507555c43065499fe797c37f724ed827c1d43ebfc5fe346` | `alembic/env.py` |
| `022ba49c8d3a12c3cf32df6f998b357dcb09b013908327d65e110618e2d8c8ab` | `docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal-plan.md` |

The earlier durability plan supplies only the accepted containment pattern. Its
large harness, Context Fabric SQL and catalogue assertions are not imported,
executed or treated as status-confirm evidence.

## Exact owned artifacts

This tranche may add only its plan, threat delta, preplanning receipts, one
closed rehearsal contract/schema, one fixed-path standard-library harness, one
provider-free evidence file, one focused static/hostile test, and eventual
closeout/acceptance/Continuity/Compass/Yuri-summary artifacts. Existing
application, migration, model, service, route and API files must not change.

## Exact executable and containment profile

- Host executable: the locally resolved `docker.exe`; no caller override.
- Image: exact locally present `postgres:16-bookworm`, inspected before create;
  `--pull=never` forbids registry access.
- Container: unique prefix `emr4-status-confirm-pg16-catalogue-` plus a random
  16-hex suffix, with exact harness and cleanup-nonce labels.
- Network: `--network=none`, no published/exposed port and no network join.
- Storage: one container-local tmpfs at `/var/lib/postgresql/data`; no bind,
  named volume, workspace or Docker-socket mount.
- Bounds: one CPU, 512 MiB memory, 128 processes, no restart, 90-second startup,
  30-second commands and 300-second total run.
- Bootstrap identity: fixed authored-synthetic database/user/password values
  used only inside the owned container; they are not operational credentials.
- SQL transport: `docker exec -i` to in-container `psql` over its local Unix
  socket, using argument vectors with `shell=False`; no host database URL.

The harness may inspect only the exact image reference, closed container name
and captured container ID. It may never list, prune, pull, build, login, start a
desktop app or remove an object it did not create and reverify.

## Readiness, prerequisite and migration admission

Before SQL, the exact captured container must pass ownership/profile inspection,
then `pg_isready` plus an authenticated `server_version_num` probe continuously
for three observations. The server major must be 16.

One explicit prerequisite transaction creates only:

- `public.appointments` with UUID id/practice, text status and no version column;
- `public.appointment_command_idempotency` with the exact pre-migration fields
  referenced by the new conditional constraints; and
- `public.alembic_version` containing exactly `v1w2x3y4z5b6`.

It inserts two fixed authored-synthetic appointments: one ordinary cutover row
and one maximum-version probe row only after the migration adds the column. No
person, patient, practice or product-derived value is used.

The host generates SQL only through the exact repository Alembic graph with:

`python -m alembic upgrade v1w2x3y4z5b6:w2x3y4z5a6b7 --sql`

The harness supplies one fixed synthetic `DATABASE_URL` solely because
`alembic/env.py` requires a dialect URL in offline mode; no connection is made.
It rejects unexpected revision text, transaction-control shape or source hash,
removes only the exact outer `BEGIN;`/`COMMIT;` wrapper emitted by Alembic, then
streams the otherwise byte-identical body through `psql --file=-`,
`ON_ERROR_STOP=1` and `--single-transaction`.

## Exact catalogue assertions

Read-only `pg_catalog` queries must prove:

- Alembic head exactly `w2x3y4z5a6b7`;
- `appointments.appointment_state_version` is `int8`, non-null, default `1`;
- the five receipt fields are exactly `int2`, `bytea`, `int8`, `int8`, `bytea`
  and nullable;
- constraints `ck_appointments_state_version_positive`,
  `ck_appt_cmd_idem_receipt_version` and
  `ck_appt_cmd_idem_status_receipt_v1_complete` exist with accepted predicates;
- function `public.emr4_advance_appointment_state_version()` returns trigger,
  uses PL/pgSQL, is invoker/volatile, contains the max guard and `OLD + 1` rule;
- trigger `trg_appointments_advance_state_version` is enabled, row-level,
  `BEFORE UPDATE`, calls that exact function and is not a constraint trigger;
- the existing cutover appointment received version one; and
- no unexpected non-system trigger or status-confirm function exists.

Evidence stores only allowlisted metadata, fixed identifiers, counts, digests,
SQLSTATEs and bounded lifecycle outcomes—never raw server logs.

## Rolled-back authored-synthetic probes

After catalogue admission, fixed scripts prove:

1. a new appointment insert receives default version one, then rolls back;
2. a caller-submitted update version is replaced by old plus one, then rolls
   back and the committed row remains unchanged;
3. inserting version zero fails the positive constraint with SQLSTATE `23514`;
4. updating a fixed maximum-version row fails with SQLSTATE `22003` and leaves
   its status/version unchanged;
5. one exact complete receipt-v1 insert passes inside a rolled-back transaction;
6. bad digest length, non-adjacent versions and receipt version two each fail
   with SQLSTATE `23514`; and
7. legacy rows with all five additive fields null remain admissible and are
   never labelled replayable.

No route, service helper, application command, audit row or patient/product
record is invoked. These are database invariants only.

## Cleanup

Cleanup runs in `finally`. Before `docker container rm --force <captured-id>`,
the harness re-inspects that exact ID and requires exact ID/name/image, both
ownership labels, network none, no bind/named-volume mount, tmpfs data, bounds,
environment and no port bindings. If any fact differs, it refuses removal and
returns `cleanup_ownership_unverified` with the ID for human attention. After
verified removal, exact-ID inspect must return the documented absent condition.
No image, volume, network, workspace path or unrelated container is removed.

## Acceptance

Pass only if the fresh five-source receipt and all eight source hashes pass;
contracts are whole-document schema-valid; at least sixty hostile mutations
fail closed; Docker/image/profile/readiness are exact; offline SQL identifies
only the frozen revision range; installation succeeds atomically; every
catalogue and probe assertion passes; cleanup proves exact absence; focused,
scaffold-lineage, Compass/baton, Ruff and whitespace gates pass; protected refs
and all unrelated untracked files remain unchanged.

## Data, provider, cost and authority boundary

Only repository-authored schema metadata and fixed synthetic UUIDs/strings enter
one local disposable PostgreSQL container. No patient, clinical, real-person,
product, historical diary or protected data; provider, ADC, credential/IAM,
browser or external network; route, watcher/event, command; durable storage;
deployment, production, release, Pages or protected ref is opened. Cloud cost is
zero. The locally cached official PostgreSQL image is the only external binary
artifact and cannot be downloaded by this tranche.

## Recovery and next candidate

Missing Docker/client/daemon/image returns `environment_unavailable` without
fallback. A migration, catalogue, probe or harness defect receives bounded
evidence-backed repair within this exact envelope and a freshly owned container.
Cleanup ownership uncertainty stops destructive action. Pause for Yuri only if
a human-only environment action or materially different unplanned outcome is
required.

Passing would make a provider-free disposable PostgreSQL status-confirm
behavior/transaction rehearsal the next narrow candidate. Route integration,
real application transaction behavior, concurrency/restart/unknown commit,
product data, deployment and production would remain closed.

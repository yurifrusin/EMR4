# Provider-free disposable PostgreSQL status-confirm behavior/transaction rehearsal plan

Date: 2026-08-12

Source HEAD: `d4f637d6c2afadccc95d4b7ae8cfc1f522444133`

Status: `frozen_for_provider_free_disposable_postgresql_execution`

Reasoning level: material database transaction evidence / Extra High

## Purpose

Exercise the exact unmounted `status_confirm_locked_transaction` seam against
the already admitted status-confirm migration in one newly owned disposable
PostgreSQL 16 database. The finite serial proof covers current-authority order,
the emitted practice/appointment/idempotency lock sequence, conflict-safe
idempotency classification, one atomic appointment/audit/v1-receipt write set,
stored replay after response loss and complete rollback at selected failure
boundaries.

This is not a route or product command. The harness is the only caller, supplies
only closed authored-synthetic values and removes every owned runtime object.

## API Spine classification

This is private REST-command transaction evidence. Public OpenAPI remains
byte-identical, GraphQL remains read-only, the status compatibility route is
not imported or called, and no event or Context Fabric surface is involved.
The stored canonical bytes are private rehearsal evidence, not a new public
response shape.

## Exact source bindings

Only these exact non-protected sources may be read, imported or hashed:

| SHA-256 | File |
|---|---|
| `777798e27b226fb7a4adcdade185372cc816f7fd245d8fe7034427a3ae0f3ad2` | `docs/raisa-provider-free-disposable-postgresql-status-confirm-scaffold-parse-catalogue-rehearsal-closeout.md` |
| `cfff73f8e8849ff16144a48a2e863f7c0a97f8222ac05c49209da767ac145c48` | `orchestration/agent_inbox/codex/raisa-status-confirm-scaffold-parse-catalogue-sol-acceptance.md` |
| `97243376111a2546a8bb36c7c615531d50e73ffdac92a2a179ec7747b448e2d8` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-scaffold-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence.json` |
| `9dbc172af43d1f858335d747def4c520643790b89646e2bfeef1a15124ab600d` | `scripts/raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal.py` |
| `4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b` | `app/services/appointment_status_physical.py` |
| `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` | `app/models/appointments.py` |
| `6be0d9ab4fc33a8709268d2f2a4550b6063e3f3e4188349c5fe3b0b6acd14431` | `app/models/tenancy.py` |
| `bfa72b627061b8e477903ec9fc2cfbb35a4970b26ab7115db18c3daef1d3696c` | `alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py` |
| `2b379cbaefeac83a79a3776f78c58b48a94b4695de3356d56a57318a5ab594e7` | `docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal-closeout.md` |
| `18c5bf4f6b6c22ab310e1571f794598a4317ff32f9103445b9d23edc5d112918` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/rehearsal-packet.json` |
| `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` | `docs/api-spine/openapi/appointment-commands.yaml` |

The in-memory rehearsal supplies only the accepted schedule meanings. Its race
cases are not imported because this tranche explicitly excludes concurrency.

## Exact owned artifacts

The tranche may add only this plan, its threat delta, preplanning receipts, one
closed contract/schema, one fixed-path standard-library/SQLAlchemy harness, one
closed evidence schema and evidence file, focused tests and eventual
closeout/acceptance/Continuity/Compass/Yuri-summary artifacts. Existing
application, model, migration, API and route files must remain unchanged.

## Disposable runtime and fixed loopback-relay boundary

The host must execute the repository's exact Python interpreter and locally
resolved `docker.exe`. The only image is the already cached
`postgres:16-bookworm`; `--pull=never` forbids registry access.

The harness creates exactly one uniquely named Docker `--internal` bridge
network and one uniquely named PostgreSQL container attached only to it. The
internal network denies external routing. Docker publishes no container port.
After exact-ID readiness, the harness starts one in-process TCP relay bound by
the operating system to a dynamic port on exactly `127.0.0.1`. Each accepted
connection invokes only the captured container ID with an argv-based,
`shell=False` host process and a fixed literal container-side Bash `/dev/tcp`
relay to `127.0.0.1:5432`. No database host, port, command or container target
is caller-selected or interpolated. This narrow local connection is required
to run the exact host-side SQLAlchemy seam and is not external network or
product traffic. The relay is stopped before Docker cleanup.

The container remains tmpfs-backed with no bind/named volume, workspace or
Docker-socket mount, one CPU, 512 MiB memory, 128 processes, no restart,
90-second startup, 30-second commands and a 300-second total bound. Exact
synthetic database credentials exist only for the disposable server. Evidence
must not retain them or the raw connection URL.

Before connection, inspect the exact image, captured network ID and captured
container ID. Require the unique names, ownership/nonce labels, internal
network, no published ports, tmpfs, bounds and no other mount or network.
Require the relay listener to be exactly IPv4 loopback with an operating-system
selected positive port, the host child command to be argv-based with
`shell=False`, and the container-side command to equal the frozen literal.
Global Docker listing, pull, build, login, prune and unrelated removal are
forbidden.

## Minimum transaction-faithful schema

Bootstrap creates only the mapped columns needed for `Practice`, `Appointment`,
`AppointmentAuditLog` and `AppointmentCommandIdempotency`, plus the exact
selected correlation constraints and Alembic predecessor row. It omits unrelated
application relations and data. The exact migration range
`v1w2x3y4z5b6:w2x3y4z5a6b7` is generated offline and installed atomically as in
the accepted parse/catalogue rehearsal.

The fixture must retain:

- the composite practice/appointment, practice/command and practice/audit
  foreign keys used by the correlated write set;
- the named conflict target
  `uq_appt_cmd_idem_practice_actor_operation_key`;
- unique command-to-audit and audit-to-command correlations; and
- all pre-existing idempotency completion constraints needed by the mapped
  model plus the migration's versioned receipt constraints.

All rows use fixed opaque UUIDs and synthetic enum/text values. There is no
person, patient, reason narrative, clinical value or product-derived value.

## Exact transaction composition

Every invocation uses a new SQLAlchemy `Session`, the exact imported
`status_confirm_locked_transaction` function, `READ COMMITTED`, a fixed
positive transaction-local lock timeout and no nested transaction/savepoint.
An SQLAlchemy statement observer records only normalized statement-class
tokens. It must show, in order:

1. practice `FOR SHARE`;
2. appointment `FOR UPDATE`;
3. `INSERT ... ON CONFLICT DO NOTHING` for the idempotency row;
4. idempotency `FOR UPDATE`; and
5. the second current-authority callback only after the idempotency lock.

The observer records no values or raw SQL in durable evidence. This proves the
actual emitted/acquired serial lock order, not contention or concurrency.

For `new_command`, the harness alone stages an `Arrived` appointment mutation,
one `status_change` audit correlated to the command, and one complete receipt
v1. It flushes and refreshes the appointment so the PostgreSQL trigger-owned
adjacent version is observed, then stores the exact canonical response bytes,
their lowercase SHA-256 and the matching JSON body. The seam's own final guard
must accept the complete set or roll it all back.

## Frozen sixteen-scenario population

Exactly sixteen ordered, independently partitioned serial scenarios are frozen:

| ID | Expected proof |
|---|---|
| `BTR-S01` | clean `new_command` commits exactly one adjacent appointment mutation, correlated audit and complete v1 receipt |
| `BTR-S02` | committed response is discarded; exact retry returns byte-identical stored replay with no second effect |
| `BTR-S03` | same key with a different request digest returns `conflict` without stored-byte disclosure or mutation |
| `BTR-S04` | same key with a different session binding returns `conflict` without stored-byte disclosure or mutation |
| `BTR-S05` | an existing `in_progress` row returns `in_progress_not_replayable` with no disclosure |
| `BTR-S06` | an existing completed legacy row returns `legacy_receipt_not_replayable` with no disclosure |
| `BTR-S07` | a structurally complete row with a mismatched response hash returns `receipt_integrity_failure` with no disclosure |
| `BTR-S08` | inactive-practice policy returns the common target-unavailable error before any appointment/idempotency access |
| `BTR-S09` | absent practice-scoped appointment returns the common target-unavailable error before idempotency access |
| `BTR-S10` | first current-authority check fails before idempotency insert/read and discloses nothing |
| `BTR-S11` | authority lost at the second check rolls back the just-inserted idempotency row and discloses nothing |
| `BTR-S12` | replay after current-authority revocation stops before idempotency inspection and discloses no stored result |
| `BTR-S13` | returning from a new decision without staging writes raises `StatusConfirmScaffoldIncomplete` and rolls back the claim |
| `BTR-S14` | appointment-only staging is rejected by the seam and rolls back the trigger-owned version and claim |
| `BTR-S15` | appointment-plus-audit staging without the complete receipt is rejected and all three candidate effects roll back |
| `BTR-S16` | a fixed harness abort after staging the complete write set rolls back appointment, audit and receipt together |

Each scenario starts from a fixed digest readback and ends with allowlisted
status/version plus audit, idempotency and completed-v1 counts. Expected errors
are admitted only by exact exception class; no raw exception or server text is
evidence. No failed session is reused.

## Evidence and acceptance

Pass only if the fresh five-source receipt and all eleven source hashes match;
the contract/schema are whole-document valid; at least 100 hostile mutations
fail closed; Docker image/network/container/readiness/relay containment is exact;
the migration and selected relational constraints install; the exact service
module is imported and all sixteen scenarios reproduce their outcomes; the
success trace has the frozen lock order; stored replay bytes are identical;
every rollback digest is unchanged; cleanup proves exact container and network
absence; focused/lineage/Compass/baton, Ruff and whitespace gates pass; and all
unrelated untracked paths and protected refs remain unchanged.

Evidence may retain only source/image/network/container digests, containment
booleans, fixed scenario IDs, decision/error labels, counts, state versions,
statement-class tokens and cleanup results. No raw SQL, URL, password, log,
response body, session digest, unrestricted row or runtime identifier is kept.

## Cleanup

Cleanup runs in `finally`. Reinspect the exact captured container ID and require
its ID/name/image, labels, sole internal network ID, tmpfs, bounds, no published
port and no other mount/network before removing that ID.
Confirm exact-ID absence. Then reinspect the exact captured network ID, require
exact name, labels, internal status and no attached containers before removing
that ID and confirming exact-ID absence. Any ownership ambiguity stops
destructive cleanup and requires human attention; no global discovery or
substitute target is allowed.

## Attempt 001 recovery

Attempt 001 stopped before PostgreSQL readiness, migration or scenario SQL when
Docker Desktop retained the requested internal-only network but did not create
the requested host port mapping. The failure evidence contains only the frozen
lifecycle labels. One exact harness-label-filtered Docker event query recovered
the already-owned container ID; exact-ID inspection proved the frozen labels,
image, internal network, tmpfs, bounds and absence of mounts, while also proving
that no port was published. The fixed container-side `/dev/tcp` capability was
tested against the same owned server. Exact ownership was then reverified and
the container and network were removed by exact ID; direct exact-ID inspections
proved both absent. No global listing, database SQL or scenario execution
occurred. The companion recovery record retains only hashes of those runtime
IDs and the categorical recovery facts.

Attempt 002 passed exact image/network/container inspection, PostgreSQL 16
readiness, atomic schema installation and relay start, then stopped before its
first host database connection because the initially frozen SQLAlchemy URL
named the absent psycopg v3 dialect. The exact repository interpreter instead
contains `psycopg2-binary`, matching existing repository PostgreSQL tooling.
The contract now freezes `psycopg2` as the only host SQLAlchemy driver; no
package was installed and no environment was changed. No scenario SQL ran.
The relay stopped and exact cleanup proved the owned container and network
absent. Its recovery record retains only runtime-ID hashes and categorical
facts.

## Closed surfaces and next candidate

No existing/product database, durable data, route mounting/calling, public API
change, concurrency, restart, unknown commit, provider/ADC/credential/browser,
patient/product/protected data, watcher/event, deployment, production, release,
Pages or protected-ref movement is opened. Cloud/provider cost is zero.

If this passes, the next narrow candidate is a provider-free read-only
status-confirm route-mounting admission review against the exact transaction
evidence. It may inspect the exact route/kernel/adaptor boundary only and may
not edit, mount or call a route.

# CF-D2 event and cue disposable PostgreSQL parse/catalogue design

Date: 2026-08-13

Timestamp: 2026-08-13T19:21:56+10:00 (Australia/Brisbane)

Status: `frozen_exact_artifact_catalogue_only`

## Decision

Use one fixed standard-library host harness to carry the exact accepted inert
SQL bytes across a deliberately tiny execution boundary: a cached,
networkless, tmpfs-backed PostgreSQL 16 container. Admit only PostgreSQL parse
success, exact catalogue metadata and zero rows, then destroy the container.

The `.sql.inert` suffix and warning remain true in product terms: the artifact
is not mounted into Alembic and is not an operational migration. This rehearsal
is the separately authorised disposable parser/catalogue question anticipated
by the parent contract.

## Containment shape

The host never receives a database URL. PostgreSQL exposes no host port and has
no network stack. `psql` runs inside the exact captured container and uses the
container-local Unix socket. Data lives only in container tmpfs. All process
invocations use argument vectors, fixed timeouts, capped output and
`shell=False`.

The cached image identity is frozen as both image ID and repo digest. A missing
or changed image fails before create. `--pull=never` closes the registry path.
No image, network or volume is created or deleted by the harness.

## Exact-byte admission

The harness hashes the artifact and its parent contracts before resolving
Docker. It streams the same bytes it hashed; no comment removal, templating,
encoding conversion, statement splitting or wrapper insertion changes the
payload. `psql --single-transaction` owns only the enclosing disposable
installation transaction.

This distinction matters: a successful wrapper rollback would be PostgreSQL
atomicity for this installation attempt, not evidence for terminal admission,
coalescing, checkpoint, dispatch or reconciliation protocols.

## Catalogue projection

Fixed `pg_catalog` queries return closed JSON arrays for domains, tables,
columns, table constraints and object absences. Expected physical column types
are derived mechanically from the accepted manifest:

| Abstract field type | PostgreSQL catalogue type |
|---|---|
| `digest`, `nullable_digest` | `emr4_context_fabric_cue.digest_v1` |
| `opaque_id` | `emr4_context_fabric_cue.opaque_id_v1` |
| `positive_integer`, `nullable_positive_integer` | `emr4_context_fabric_cue.positive_integer_v1` |
| `boolean` | `boolean` |
| `enum`, `nullable_enum` | `text` |

Primary and unique key columns come from the accepted relation manifest plus
the exact names frozen in this tranche. Foreign-key endpoints come from the
accepted representation contract. Check names and table ownership come from
the accepted lowering manifest. All are compared in ordered canonical form.

PostgreSQL's normalized constraint definitions are evidence digests, not a
second source of expected semantics. Exact artifact hash admission already
binds the definitions, while the catalogue establishes that PostgreSQL created
and validated each named object.

## Cleanup state machine

Cleanup runs in `finally` whenever a captured container ID exists:

`captured -> exact profile reverified -> exact ID removed -> exact ID absent`

Any mismatch stops before removal as `cleanup_ownership_unverified`. The
harness never searches by prefix or label and never substitutes a name for the
captured ID during deletion.

## Evidence and non-claims

Passing evidence stores only source hashes, image identity hashes, bounded
lifecycle states, catalogue counts/canonical digests and row counts. It stores
no raw PostgreSQL logs, password, patient/product values or operational data.

The design proves no constraint behavior beyond validated catalogue presence,
transaction protocol, lock/isolation behavior, concurrency, restart, crash or
unknown-commit recovery, delivery, retention, rotation, purge, performance,
source observation, application wiring, migration safety, deployment or
production operation.

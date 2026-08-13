# CF-D2 event and cue inert-DDL lowering design

Date: 2026-08-13

Timestamp: 2026-08-13T18:14:01+10:00 (Australia/Brisbane)

Status: `provider_free_unmounted_deterministic_sql_text_only`

## Decision

The accepted abstract representation will be lowered once, mechanically, into
a non-migration `.sql.inert` artifact. The output is useful because it makes
type, nullability, key, reference and row-check choices concrete before a
database is involved. It is deliberately too weak to establish PostgreSQL
acceptance or operational durability.

## Type mapping

| Abstract scalar | Inert PostgreSQL-16 text |
|---|---|
| `digest` / `nullable_digest` | schema-qualified text domain constrained to `sha256:` plus 64 lowercase hexadecimal characters |
| `opaque_id` | schema-qualified non-empty text domain |
| `positive_integer` / nullable variant | schema-qualified `bigint` domain constrained above zero |
| `boolean` | `pg_catalog.bool` |
| `enum` / nullable variant | `pg_catalog.text` plus a field-specific closed allowlist check |

This avoids inventing a general polymorphic enum or JSON payload type. All
fifty fields remain exact; nullable fields omit `NOT NULL` and no default is
introduced.

## Object order

The artifact declares its schema and three domains, creates the seven tables
in the accepted representation order, then adds references by `ALTER TABLE`.
Separating references preserves the accepted table order while allowing the
terminal receipt to refer to the later cue-obligation table. Only that
nullable reference is `DEFERRABLE INITIALLY DEFERRED`, matching the accepted
future-deferrable marker.

No `IF NOT EXISTS`, drop, replacement, conditional installer or transaction
wrapper is emitted. A later disposable server rehearsal therefore gets a
clean, deterministic create-only candidate and must own all setup and cleanup.

## Honest invariant mapping

Named primary, unique, foreign-key and check constraints cover only structural
and row-local facts. The partition tuple digest is checked with PostgreSQL core
`convert_to`, `sha256` and `encode`; closed classification, coordinate and
reconciliation shapes are explicit Boolean checks.

`coordinate_is_non_authoritative` and every `mutable_fields` list are retained
as exact inert annotations, not database enforcement. Likewise, the five
protocols—terminal admission, pending coalescing, contiguous checkpoint
advance, dispatch recording and reconciliation—are manifest-only unmet
dependencies. Their locks, fencing and atomicity cannot be honestly derived
from table DDL alone.

## Static evidence

The manifest records the accepted parent digest, canonical SQL digest, byte and
statement counts, relation order, field count, key/reference census, check
dispositions, mutability declarations, unlowered protocols and closed effects.
The recognizer rejects anything other than the exact canonical bytes and also
checks structural tokens and forbidden families so failures remain legible.

The evidence label is
`provider_free_unmounted_inert_postgresql_16_ddl_text`. It means only that a
deterministic closed renderer and recognizer agree on an inert artifact.

## Authority

The DDL owns no Diary truth and creates no API authority. Events and cues remain
acceleration hints; a cue can prompt one fresh authorised read, never directly
change the display, approve a proposal or perform a command. Existing backend
REST command paths retain mutation, precondition, idempotency, audit and
readback ownership.

## Non-claims

This design does not prove PostgreSQL parsing, catalogue creation, constraint
behavior, transactions, locks, isolation, concurrency, crash recovery,
restart, unknown commit, delivery, retention, rotation, purge, performance,
source observation, application wiring, migration safety, deployment or
production.

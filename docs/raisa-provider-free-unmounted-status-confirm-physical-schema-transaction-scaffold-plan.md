# Provider-free unmounted status-confirm physical schema-and-transaction scaffold plan

Date: 2026-08-12

Source HEAD: `a30db2e8bfcb6b067b55985cabf2e6200906f182`

Status: `frozen_for_provider_free_unmounted_implementation`

Reasoning level: material security/transaction implementation / Extra High

## Purpose

Lower only the accepted physical-design contract into an additive SQLAlchemy
mapping, one inert Alembic descendant, a still-unmounted backend helper seam and
deterministic provider-free tests. Nothing in this tranche mounts or calls a
route, executes a migration or SQL statement, opens a database or real lock, or
handles product or patient data.

## API Spine classification

This remains a private REST/OpenAPI status-confirm command implementation seam.
The public `AppointmentStatusResult` and
`AppointmentConfirmResultEnvelope` stay byte-for-byte unchanged. GraphQL stays
read-only and events remain non-authoritative acceleration hints.

## Exact source allowlist and frozen hashes

Only these exact non-protected sources may be read, hashed or searched:

| SHA-256 | File |
|---|---|
| `0c7a02078aa360ecc14a6af1af8a12047bad39c68c38862d9e4360c9577556c0` | `docs/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-plan.md` |
| `3ca874ef0215fb57c74bb8e886c9bc48a912666830c9530e4165a21186dfcfc5` | `docs/security/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-threat-model-delta.md` |
| `f129c571af6115ac511cab657b80469c8ae7f31397882e2831af377259b480c0` | `docs/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-closeout.md` |
| `87b58e839e1f27339c2ca5759a02f518691a39fa3fb2aeae6d01848b3e7cb2a8` | `orchestration/agent_inbox/codex/raisa-status-confirm-physical-design-architecture-sol-acceptance.md` |
| `a9c173091ab428732e176d90450fde388ef16d8557465b34c2b5cc9719420548` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-design-architecture/physical-design-contract.json` |
| `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `af00f7318da3f19732843c75b56721db89a3fa0c94b6e0feeb12a614850c4952` | `app/models/appointments.py` |
| `52650eeb8bc97abd79de78cfc47c78396d38e5f714b512ca065603b1cfefeecc` | `app/models/__init__.py` |
| `6be0d9ab4fc33a8709268d2f2a4550b6063e3f3e4188349c5fe3b0b6acd14431` | `app/models/tenancy.py` |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` |
| `78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae` | `alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py` |

The one permitted provider-free, non-database `alembic heads` invocation
returned exactly `v1w2x3y4z5b6 (head)`. The new migration's frozen
`down_revision` is therefore `v1w2x3y4z5b6`. No migration filename was
enumerated or opened by that check. Any later graph mismatch stops rather than
silently creating another branch.

## Exact owned paths

Existing paths that may be edited:

- `app/models/appointments.py`

New paths that may be created:

- `alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py`
- `app/services/appointment_status_physical.py`
- `tests/test_raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold.py`
- `scripts/raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold.py`
- `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-scaffold/scaffold-contract.json`
- `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-scaffold/scaffold-contract.schema.json`
- `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-scaffold/provider-free-scaffold-evidence.json`

The plan, threat delta, fresh preplanning runtime state/receipt and eventual
closeout, acceptance, continuity update and Yuri summary are tranche-owned
evidence paths. No other existing application, migration, service, route or test
source may change.

## Frozen implementation

### Mapping and inert DDL

- Map `appointments.appointment_state_version` as non-null SQLAlchemy
  `BigInteger` with server default `1` and a positive-range check.
- Map exactly five nullable-for-legacy receipt fields using `SmallInteger`,
  `LargeBinary` and `BigInteger`.
- Add conditional ORM constraints for exact completed-v1 status-confirm
  receipts: all five additive values, 32 digest bytes, positive adjacent
  versions, non-empty canonical bytes and existing target/audit/status/hash/JSON
  completion primitives.
- The one migration follows all seven accepted phases and installs one
  synchronous `BEFORE UPDATE` trigger. The trigger overwrites submitted values,
  advances `OLD + 1`, and raises on the maximum value. It emits no event or cue.
- Existing receipt rows remain null/legacy. No legacy receipt is backfilled.
- Downgrade first raises if any v1 receipt exists; only a never-adopted schema
  may remove the fields, trigger and version column.

### Pure helpers and unmounted transaction seam

- Canonical response bytes contain the five public fields in fixed order and
  use UTF-8 JSON without whitespace or a BOM. Duplicate warning codes and
  non-contract input fail closed.
- Session binding is raw 32-byte HMAC-SHA-256 over domain-separated,
  length-framed practice, actor and authenticated-session values. Empty inputs
  or secret fail closed; no raw session is persisted by the helper.
- Stored response integrity uses lowercase SHA-256 and constant-time compare.
- The transaction seam is unreferenced by routes. If a future caller invokes
  it, it owns one `READ COMMITTED` transaction, applies one positive bounded
  lock timeout, locks Practice `FOR SHARE`, scoped Appointment `FOR UPDATE`, then
  the idempotency row `FOR UPDATE`, and calls a caller-supplied current-authority
  predicate both before idempotency access and while all locks are held.
- Existing receipt classification occurs only after the second authority check.
  New rows are inserted only after the first check and remain target-bound.
  Replay releases only exact complete v1 bytes whose digest is valid; legacy,
  in-progress, conflict and corrupt states release no body.
- This scaffold does not stage an appointment mutation, audit or receipt
  completion and therefore executes no product command. It returns a locked
  new-command context to a future separately admitted kernel integration.

## Deterministic verification

The provider-free validator and focused tests must verify exact input hashes,
ORM types/constraints, migration ordering and trigger text, pure-helper byte
vectors, constant-time integrity, transaction AST/query ordering, two authority
checks, no route import/mount, unchanged OpenAPI hash and an allowlisted changed
path set. At least sixty hostile mutations must fail closed. Tests may import
the pure helper/model source but must not create an engine, open a database,
execute migration/SQL, acquire a lock or call a route.

## Acceptance

Pass only if the five-source receipt passes; the sole Alembic head and all
source hashes are frozen; exact focused, API Spine, migration-static,
architecture-lineage, register, Compass and baton checks pass; Ruff and
whitespace checks pass; public OpenAPI remains unchanged; and all protected
refs/unrelated untracked paths remain unchanged.

## Forbidden surfaces

No route edit, import, mount or call; no migration/database/SQL/real-lock
execution; no product/patient data; no provider, ADC, credential/IAM, browser or
network use; no watcher/event authority; no product command; no deployment,
production, release, Pages or protected-ref movement. Preserve and never stage
`docs/branding/` or any unrelated untracked file. Explicit-path staging only.

## Recovery and next candidate

Mechanical repair is allowed within the exact owned paths if it changes no
frozen semantic or authority. A material contradiction returns
`revision_required` without route or database execution. After a pass, the next
narrow candidate is a provider-free disposable PostgreSQL parse/catalogue
rehearsal of only this migration, before any behavior or route integration.

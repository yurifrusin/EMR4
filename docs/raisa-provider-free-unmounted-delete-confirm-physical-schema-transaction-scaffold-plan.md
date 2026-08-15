# Provider-free unmounted delete-confirm physical schema-and-transaction scaffold plan

Date: 2026-08-15

Timestamp: 2026-08-15T21:08:13+10:00 (Australia/Brisbane)

Source HEAD: `0a01e93319f302256f2b8af0aa74e494256808a8`

Status: `frozen_for_provider_free_unmounted_implementation`

Plan correction timestamp: 2026-08-15T22:06:25+10:00 (Australia/Brisbane)

Reasoning level: material authority / migration / transaction implementation / Extra High

## Purpose

Lower only the accepted delete-confirm physical design into additive SQLAlchemy
mapping, one inert Alembic descendant, pure deterministic helpers, and a
still-unmounted backend transaction seam. This tranche proves source
representability only. It does not mount or call a route, execute a migration
or SQL statement, open a database or real lock, provision a capability,
complete a product write, or handle patient, clinical or product data.

## API Spine classification

This remains a private REST/OpenAPI delete-confirm command-security, audit and
idempotency seam. `confirmAppointmentDeleteProposal` / `delete-confirm` is the
only future eligible ingress. The current public
`AppointmentConfirmDeleteProposalOut`, `AppointmentOut`, routes and OpenAPI stay
byte-for-byte unchanged because the six-field response transition is a later
explicit gate. GraphQL stays read-only. Events stay non-authoritative
acceleration hints. Model, Context Fabric and channel output stay inert.

## Five-source and Git admission

The fresh preplanning receipt is
`orchestration/agent_inbox/codex/raisa-delete-confirm-physical-schema-transaction-scaffold-preplanning-receipt.json`.
It passes with all five named sources. At admission, the task branch and its
origin were exact `0a01e93319f302256f2b8af0aa74e494256808a8`; local/origin
`master` and `handoff/current` were exact protected
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. All unrelated untracked paths,
including `docs/branding/`, remain excluded.

The provider-free revision-only command `python -m alembic heads` returned the
sole head `w2x3y4z5a6b7 (head)`. It opened no database. The new migration must be
the single inert descendant `x3y4z5a6b7c8` with
`down_revision = "w2x3y4z5a6b7"`; a graph mismatch stops the tranche.

## Exact source allowlist and frozen hashes

| SHA-256 | File |
|---|---|
| `32bf0e71fff17606686f5b98b0b808ea26baed882a34020f0cd609ee6f341d04` | `docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-plan.md` |
| `394d3bf9325a94fed599755fea1a7b2b2261abe67f89b5412bd21f23ba8dd449` | `docs/security/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-threat-model-delta.md` |
| `584405db5d49a56e18061f80fcd1faa72c278cf0d4975cf95febc86783609019` | `docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-closeout.md` |
| `43b560b6c19beede9bfd12db5a39d0f5698438274e5e7b3cc9cee88a64c1cfed` | `orchestration/agent_inbox/codex/raisa-delete-confirm-physical-design-architecture-sol-acceptance.md` |
| `235f800deec76aee84f9085447d7b0fb666fcd67f3edea07cc7826f9b64b8f72` | `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/physical-design-contract.json` |
| `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `6be0d9ab4fc33a8709268d2f2a4550b6063e3f3e4188349c5fe3b0b6acd14431` | `app/models/tenancy.py` |
| `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` | `app/models/appointments.py` |
| `52650eeb8bc97abd79de78cfc47c78396d38e5f714b512ca065603b1cfefeecc` | `app/models/__init__.py` |
| `c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf` | `app/schemas/appointments.py` |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` |
| `4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b` | `app/services/appointment_status_physical.py` |
| `bfa72b627061b8e477903ec9fc2cfbb35a4970b26ab7115db18c3daef1d3696c` | `alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py` |
| `28060c2f5b1cb4ff00f62b498511995a35a630963e586920115f34740c5d1ac3` | `tests/test_raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold.py` |
| `16301ce02d9cd764452f16c0a0dc467bf2182d6953883d214bb7a13b993c14a0` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-scaffold/scaffold-contract.json` |
| `f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624` | `app/routers/appointments.py` |

No protected-evidence path may be discovered or opened. Any necessary source
expansion requires an explicit plan revision with an exact path and hash.

## Exact owned paths

Existing application paths that may be edited:

- `app/models/tenancy.py`;
- `app/models/appointments.py`.

One pre-existing test-only conformance path may receive exactly one mechanical
repair after its failure is reproduced at both the plan source and candidate:

- `tests/test_raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold.py`
  may change only the expected frozen OpenAPI SHA-256 from
  `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6`
  to the already-current, independently bound and unchanged OpenAPI digest
  `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a`.
  Its admitted pre-repair file digest is
  `28060c2f5b1cb4ff00f62b498511995a35a630963e586920115f34740c5d1ac3`.
  No other line in that test and no OpenAPI/product path may change.

New application and deterministic evidence paths that may be created:

- `alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py`;
- `app/services/appointment_delete_physical.py`;
- `tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py`;
- `scripts/raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/scaffold-contract.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/scaffold-contract.schema.json`; and
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/provider-free-scaffold-evidence.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/operation-journal.json`.

This plan, its threat delta, tranche receipts, worker/reviewer packets and
receipts, eventual closeout, Sol acceptance, continuity updater/test and Yuri
summary are also tranche-owned evidence. No router, schema, OpenAPI, current
idempotency service, status-confirm service or earlier migration may change.
The single corrected stale hash assertion above is the sole exception and does
not alter status-confirm behavior.

## Frozen implementation

### Product authority mapping and inert migration

- Map `users.authority_generation` as non-null `BigInteger`, server default
  one, with positive range and `UNIQUE (practice_id, id)` constraints.
- Add `UserCapabilityGrant` with the exact composite primary key and composite
  user foreign key from the accepted design. A check constraint admits only
  `appointment.cancel.confirm` and `appointment.read`; no wildcard or JSON
  grant is representable. `app.models.__init__` already imports the complete
  tenancy module, so no new export or edit is needed.
- The migration creates the grant table empty and grants no row. It adds the
  user column nullable without default, installs default one, backfills only
  baseline one, validates the domain and sets non-null before any consumer.
- PostgreSQL owns generation. A `BEFORE INSERT OR UPDATE` user trigger forces
  insert generation one, advances exactly once when practice, role or active
  membership changes, rejects overflow, and ignores all direct submitted
  generations. A capability `BEFORE INSERT OR DELETE` trigger locks and
  advances the exact parent user before the row changes; only that nested
  database-owned `OLD + 1` transition is admitted by the user trigger. Grant
  updates are rejected, so reassignment is delete then insert and advances each
  affected parent. Missing parents and overflow abort the whole transaction.
- Migration assertions require positive user generations, an empty grant
  table, no orphan and no unknown capability. No role-derived or existing-user
  grant is created.
- Downgrade is allowed only before any grant, delete v1 receipt or delete audit
  v1 exists. After first use it raises and requires forward recovery. A safe
  pre-use downgrade restores the unchanged status-only receipt constraint.

### Receipt and audit mapping

- Add only nullable `authority_generation BIGINT` to
  `appointment_command_idempotency`.
- Widen the existing named status-only v1 completeness constraint in place to an exact
  family-qualified disjunction: the status-confirm branch remains semantically
  unchanged; the delete-confirm branch requires the exact operation/route,
  completed confirmed write, positive authority generation, 32-byte session
  digest, positive adjacent versions, non-empty canonical bytes and existing
  target/audit/status/hash/JSON fields. No third family may set version one.
- Add the seven nullable delete-audit fields accepted by the physical design.
  Audit version one requires delete action, command identity, positive
  authority and adjacent state versions, `Cancelled`, a structured reason,
  null waiting-area after state, and JSON-array warning/evidence containers.
  No legacy row is backfilled or reinterpreted.

### Pure helpers and the unmounted transaction seam

- Canonical response bytes contain exactly six fields in frozen order. Status
  is constructed as `Cancelled`; waiting area is constructed as JSON null;
  reason code must be one of the exact ten dedicated codes; cancellation text
  is null or at most 500 Unicode characters; warning codes are non-empty,
  unique strings whose already-validated order is preserved. UTF-8 compact
  JSON is the sole byte representation.
- Session binding is raw 32-byte HMAC-SHA-256 using domain
  `appointment-delete-session:v1` and unsigned 32-bit length framing of
  practice, actor and authenticated-session values. Empty values fail closed.
  Raw session identity and secret are not stored.
- Stored response integrity is lowercase hexadecimal SHA-256 with
  constant-time comparison. Only exact stored canonical bytes can be returned
  by a replay decision; JSONB is never delivery authority.
- The seam is unreferenced by routes. It owns one `READ COMMITTED` transaction
  and one monotonic cumulative 2000 ms wait deadline. Before every potentially
  blocking authority, appointment or idempotency access it applies only the
  positive remaining budget; it never resets the deadline and uses no NOWAIT,
  SKIP LOCKED, advisory lock or effect retry.
- Lock/query order is exact: server-selected `User` by practice/actor
  `FOR SHARE`; practice-scoped Appointment `FOR UPDATE`; first complete current
  authority check; select an existing exact idempotency row `FOR UPDATE`; only
  when absent, attempt one target-bound conflict-do-nothing insert and then
  select the unique winning row `FOR UPDATE`; second complete authority check;
  classification. The status scaffold's insert-first pattern is not copied.
- Both checks are internal and require the locked active user, exact server
  role in the admitted role set, positive signed generation equal to locked
  truth, and exact `appointment.cancel.confirm` row. Caller callbacks cannot
  weaken this check.
- Binding classification covers actor, role, authority generation, session,
  operation, route, target and request. Legacy, in-progress, conflicting or
  corrupt rows release no body. Replay requires a complete integrity-valid
  family-qualified delete v1 receipt and current authority.
- A new-command decision exposes only the still-locked context to a future
  separately admitted kernel. This scaffold does not verify proposal evidence,
  mutate the appointment, create an audit row or complete the receipt. On
  context exit, an incomplete future atomic write set raises and rolls back.
  Thus direct use cannot silently commit a partial command.

## Deterministic verification

The provider-free validator and tests must verify all frozen hashes, sole-head
lineage, ORM types/constraints, migration order and trigger bodies, empty grant
cutover, downgrade guard, exact pure-helper vectors, reason/text rejection,
constant-time receipt integrity, cumulative-deadline logic, select-first ordered transaction
AST, two complete internal authority checks, replay classification, unchanged
OpenAPI/router/schema/generic-idempotency/status-scaffold hashes, no route import
and an explicit changed-path allowlist.

At least ninety hostile mutations must fail closed, including automatic grants,
wildcards, role-only authority, client generation selection, non-advancing grant
changes, mutable capability identity, generation overflow/wrap, synthetic-auth
reuse, weakened composite identity, missing reason, legacy reason promotion,
full appointment response, JSONB replay, raw sessions, status-branch regression,
receipt-family widening, merged audit arrays, reset wait budgets, reordered or
missing locks, one authority check, authority after disclosure, hidden retry,
readback-as-commit, route mounting and migration/database execution.

Tests may import the mapped models and pure unmounted helper, but must not
create an engine, connect to a database, execute DDL/SQL or migration functions,
acquire a lock, call a route, or process product data.

The tranche operation journal uses the accepted Ariadne journal schema. Its
stable request digest is the exact frozen-plan byte digest; manually appended
`received`, `running` and eventual terminal evidence executes nothing and
grants no command authority.

## Parallelism and review allocation

- Sol owns semantic closure, source admission, integration, acceptance and Git.
- One native subagent performs a read-only exact-path delta/omission audit and
  edits nothing.
- DeepSeek V4 Flash/high may implement one closed mechanical package after this
  plan is committed. It receives only the exact owned paths and no semantic,
  acceptance, integration or protected-ref authority.
- Gemini 3.7 Flash/high performs one fresh independent exact-candidate veto
  after deterministic admission. Gemini 3.6 is historical compatibility only;
  there is no silent fallback.

## Acceptance

Pass only if:

1. the five-source receipt and every frozen source hash pass;
2. the sole migration head remains one exact descendant;
3. every mapping, trigger, helper, authority and transaction invariant is
   represented without route or database execution;
4. focused tests and at least ninety hostile mutations pass;
5. API Spine, architecture lineage, canonical fast profile, Ruff, whitespace,
   register, Compass and baton checks pass;
6. OpenAPI and router hashes remain unchanged;
7. one fresh Gemini 3.7 Flash/high exact-candidate veto and clean postflight
   pass; and
8. protected refs and all unrelated untracked paths remain unchanged.

## Forbidden surfaces

No route/schema/OpenAPI edit, import, mount or call; no migration, DDL, SQL,
database, real transaction or lock execution; no capability provisioning; no
provider, ADC, credentials, IAM, browser or network; no product, patient or
clinical data; no watcher/event authority; no product command; no deployment,
production, release, Pages or protected-ref movement. Preserve and never stage
`docs/branding/` or any unrelated untracked file. Use explicit-path staging
only.

## Recovery and next candidate

Mechanical correction is allowed only within exact owned paths and cannot
change a frozen semantic or authority. A material contradiction stops as
`revision_required` with the candidate preserved. After acceptance, the next
narrow candidate is a provider-free disposable PostgreSQL parse/catalogue
rehearsal of this one migration; behavior, route convergence, provisioning and
product data remain separately gated.

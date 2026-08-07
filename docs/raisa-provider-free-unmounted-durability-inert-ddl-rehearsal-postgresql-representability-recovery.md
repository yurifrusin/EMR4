# Inert durability DDL PostgreSQL-representability recovery

Date: 2026-08-07

Status: accepted and implemented at exact reviewed source HEAD
`46e16622471a192353cb82a33acf301dc2cfb7aa`

Base task HEAD: `4a1cf9ce811a60aab6eac28cb17a72fa8a7aec09`

Immutable body parent:
`sha256:f71287f266a3252d2a0736e511287600939a40bc70397710600c12581e24d4f3`

## Why this recovery is required

The first renderer candidate and its sole bounded DeepSeek correction remain
rejected evidence. The corrected candidate passes its own 58 deterministic
checks, but source and rendered-byte review found five material classes of
defect:

1. bare `array_length(value, 1)` returns null for an empty PostgreSQL array, so
   the accepted complete-set `COUNT == 0` branches do not work;
2. 44 RLS policies are emitted before their sole support function exists;
3. deferrable row fences are emitted as ordinary `CREATE TRIGGER` statements
   with invalid deferrability placement rather than PostgreSQL-16 constraint
   triggers;
4. the schema, fabric types and eighteen fabric relations do not reach the
   accepted final owners and the manifest does not prove owner closure; and
5. six accepted trigger expressions treat `OLD` as if it contained system
   column `xmin`. PostgreSQL trigger `OLD`/`NEW` records have the table row
   structure; system columns must instead be read from the physical relation.

The same audit also found that the deferred appointment fence's exact binding
read would reject ordinary non-producer appointment updates despite the
accepted statement that other credentials are inert. This is repaired here,
not silently waived.

## Authority and provenance

The accepted body contract remains immutable and every one of its 22 programs
must still be verified, consumed and provenance-linked. This descendant may
derive one `postgresql_16_representability_recovery_v1` inside the closed
lowering contract. The lowering contract and its whole-contract schema must
position-close the exact operations below, their affected node IDs, old/new
expression seals, relation keys, dependency edges and effective population.
An additional, missing, reordered-with-effect or differently sealed operation
fails before rendering.

The effective population is nine entry points, fourteen trigger functions,
fourteen trigger declarations and twenty-three programs. The sole addition is
`emr4_context_fabric.cf_guard_appointment_update_v1` bound by
`trg_cf_appointment_guard` as a non-deferrable `BEFORE UPDATE FOR EACH ROW`
trigger on `public.appointments`. It is a guard, not a callable entry point,
and receives no runtime execute grant.

## Exact effective-body recovery

The recovery operation order is:

1. `ADD_APPOINTMENT_GUARD_SIGNATURE`;
2. `ADD_APPOINTMENT_GUARD_PROGRAM`;
3. `ADD_APPOINTMENT_GUARD_DECLARATION` immediately before the existing
   appointment deferred fence;
4. `ADD_APPOINTMENT_PRODUCER_APPLICABILITY` to both appointment triggers;
5. `RESELECT_BEFORE_TRIGGER_OLD_XMIN` for the exact claim, appointment, event
   and outbox immediate guards;
6. `REMOVE_DEFERRED_APPOINTMENT_OLD_XMIN` and bind second-update enforcement to
   the new immediate guard;
7. `REMOVE_DEFERRED_EVENT_DELETE_OLD_XMIN` and bind current-event deletion
   enforcement to `cf_guard_event_v1`; and
8. `REMOVE_DEFERRED_OUTBOX_DELETE_OLD_XMIN` and bind current-outbox deletion
   enforcement to `cf_guard_outbox_v1`.

The exact reselect keys are:

| Relation | Key used before effect |
|---|---|
| `public.appointment_command_idempotency` | `practice_id`, `id` |
| `public.appointments` | `practice_id`, `id` |
| `public.diary_committed_events` | `practice_id`, `id` |
| `emr4_context_fabric.diary_context_observation_outbox_v1` | `practice_id`, `source_contract_id`, `stream_id`, `stream_epoch`, `transaction_position` |

Each immediate reselect reads only `xmin`, occurs before row modification or
deletion, has exact-one cardinality and maps zero/ambiguous outcomes to the
registered value-free `F_CARDINALITY`/`CF004`. Its result is compared with the
accepted PostgreSQL-16 current-XID32 expression. No trigger row-image field
named `xmin`, raw system-column interpolation or caller-supplied provenance is
permitted.

The appointment applicability predicate is the existing active
`session_user`/`PRODUCER`/practice/`diary.appointment_rescheduled.v1` binding
predicate. Zero matches returns `NEW` in the immediate guard and `NULL` in the
deferred fence. One match executes the exact proof. More than one fails
`F_CARDINALITY`/`CF004`; it never chooses a stream. The immediate guard rejects
a current-XID old appointment before a second update. The deferred fence keeps
the final tuple reload and complete temporal/non-temporal membership proof.

The event and outbox deferred delete arms rederive all still-observable exact
classification, retention binding and policy facts. Only the current-XID fact
is discharged by their mandatory same-table immediate guard. This is an
explicit narrow dependency, not a claim that a deleted physical row can be
reloaded, and not a dependency on cross-table deferred-trigger order.

## Exact PostgreSQL-16 lowering recovery

- `COUNT(set)` is always
  `coalesce(pg_catalog.array_length(set, 1), 0)::pg_catalog.bigint`.
- The phase-one dependency order is roles; schema authorization; domains,
  enums and composites; relations, constraints and indexes; the sole support
  helper; RLS enable/force and all policies; then exact fabric object owner
  transfers. A policy may not precede its helper.
- Deferrable `AFTER ... FOR EACH ROW` fences use `CREATE CONSTRAINT TRIGGER`
  with `DEFERRABLE INITIALLY DEFERRED` in PostgreSQL-16 order. Immediate guards
  use ordinary `CREATE TRIGGER` and cannot carry deferrability clauses.
- `CREATE SCHEMA ... AUTHORIZATION context_schema_owner` fixes schema owner.
  Every fabric domain, enum, composite and all eighteen fabric relations end
  owned by `context_schema_owner`. Function owner remains signature-specific;
  the admission function remains owned by `context_admission_receiver`.
  Application relation owners are untouched.
- The future installation executor is an external migration precondition, not
  a runtime principal. No `SET ROLE`, membership grant, retained trigger-install
  privilege, runtime ownership or schema `CREATE` grant is emitted.
- The manifest records exact schema/type/relation/function owners, policy-to-
  helper dependencies, trigger kind/order, the four paired-guard dependencies,
  and negative assertions for application ownership changes and runtime schema
  creation.
- Unknown lock modes fail before emission; no raw-mode fallback is legal.
- A complete-set read may omit an unobservable selected `xmin` only when the
  effective-body proof shows the set is used solely for cardinality. That
  elimination is named and sealed; all observable projections remain exact.

## Static hostile acceptance

In addition to inherited acceptance, digest-resealed attacks must reject:

- bare `array_length`, nullable empty-set count or a non-bigint count result;
- any policy before the helper or an omitted dependency edge;
- ordinary `CREATE TRIGGER` for a deferred fence, `CREATE CONSTRAINT TRIGGER`
  for an immediate guard, or misplaced deferrability;
- any emitted `OLD.xmin`, `NEW.xmin` or trigger-record system-column access;
- a missing/widened keyed reselect, a reselect after effect, or a non-CF004
  cardinality outcome;
- removal of the appointment guard, zero-binding inert branch, duplicate-
  binding failure or paired-guard dependency;
- a deferred event/outbox delete fence claiming independent old-`xmin` proof;
- wrong schema/type/relation/function owner, an application owner change,
  runtime schema `CREATE` or a receiver ownership widening;
- a raw unknown lock mode, hidden extra helper/program/trigger or an effective
  population other than 9/14/14/23; and
- any database/parser/subprocess/socket/provider/runtime/output-path opening.

## Claim and next boundary

Passing this recovery and its renderer proves only a byte-stable inert artifact
within the closed static PostgreSQL-16 subset. It does not prove server parse,
catalogue acceptance, ownership transfer, trigger execution, paired-guard
behavior, RLS, concurrency or migration safety. Those require the separately
bounded disposable local PostgreSQL gate. No SQL execution, database/source
contact, application/API/Diary change, patient/product data, command/write,
runtime wiring, deployment, production, release, Pages or protected-ref
authority is granted.

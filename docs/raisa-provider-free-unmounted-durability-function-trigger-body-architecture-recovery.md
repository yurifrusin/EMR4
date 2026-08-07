# Durability function-and-trigger-body structural-feasibility recovery

Date: 2026-08-07

Status: normative recovery frozen before body implementation

Initial plan commit:
`f1de5fbb903e304ca4923bb17cbee00e5f955bd7`

Accepted immutable parent:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

## Why recovery is required

Independent read-only entry-point and trigger analyses found no P0, but found
material contradictions that would force a SQL renderer to invent authority or
behavior. No body contract, SQL, DDL, database object or runtime path had been
created. This recovery invokes Sol's bounded architecture lease and supersedes
only the initial child plan as an implementation source. It does not rewrite
the accepted parent artifact.

The child contract must carry one closed
`structural_feasibility_recovery_v1`, bind the accepted parent hash, derive one
effective parent and prove that every effective change is exactly one of the
items below. Unknown, missing or additional delta operations fail.

## Closed effective-parent delta

### One stream per active service binding

Add non-null `stream_id uuid` to
`emr4_context_fabric.context_service_practice_binding`. The active binding is
therefore exactly one login, logical capability, practice, source contract,
stream, binding revision and credential epoch.

Add non-null `stream_id uuid` to the two previously practice/source-only fabric
relations:

- `diary_context_aggregate_aliases_v1`; and
- `context_retention_policy`.

Include `stream_id` in their primary/unique/foreign-key coordinates and in the
outbox-to-alias foreign key. No runtime caller chooses a stream independently:
the producer derives it from the one active binding; typed observer,
coordinator, lifecycle and retention locators must equal it.

Extend the existing `session_binding_allows_v1` helper with exact
`requested_stream_id uuid` input while preserving `STRICT`, Boolean output,
fixed search path and non-login ownership. Its count-one predicate must also
require `binding.stream_id = requested_stream_id`. Every stream-bearing RLS
policy and entry-point check passes the row or locator stream. The binding
table's own select policy remains a session-login/time-bounded row policy.

No overload or second helper is introduced.

### Exact non-runtime privilege additions

The non-login `context_schema_owner` gains `SELECT` only on:

- `public.appointment_command_idempotency`;
- `public.appointments`;
- `public.appointment_audit_log`; and
- `public.diary_committed_events`.

This table-level `SELECT` is required to inspect PostgreSQL system `xmin` as
well as the closed body-program columns. It grants no application-table
`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, ownership, role inheritance or runtime
login. The body effect allowlist remains column-exact and rejects any unused
product-field read. Product rows are already locked by the existing one-session
update-confirm route or are current-transaction inserts; the body must not seek
an `UPDATE` privilege merely to reacquire them.

The non-login `context_admission_receiver` adds exact `SELECT` on
`emr4_context_fabric.context_service_practice_binding` so it atomically derives
and records `observer_binding_revision`. It retains only admission `INSERT` and
its previously accepted reads. No runtime role gains direct product access.

The future migration executor requires bounded installation-time `TRIGGER`
authority on the four application tables. That is a renderer/migration
precondition, not a runtime grant, and must not be inherited by any bureau or
runtime login.

### Truthful coordinator result

Add enum `durability_transition_result_kind` with exactly:

- `RECEIPT_APPLIED`;
- `RECEIPT_REPLAYED`;
- `REBASE_APPLIED`; and
- `TERMINAL_REPLAYED`.

Add composite `durability_transition_result_v1` with exactly:

- `result_kind durability_transition_result_kind`;
- `checkpoint_state checkpoint_state`;
- `source_position bigint`;
- `decision observation_decision`;
- `reason_code observation_reason`;
- `checkpoint_disposition checkpoint_disposition`;
- `lifecycle_revision bigint`; and
- `evidence_digest digest_sha256`.

Change only `apply_durability_transition_v1`'s output from a mandatory receipt
row to this composite. On receipt apply/replay, `evidence_digest` is the stored
receipt digest. On rebase/terminal apply/replay it is the resulting checkpoint
integrity digest. A missing PRIMARY, conflict-only admission, later conflict,
gap, predecessor/epoch mismatch or key uncertainty can therefore atomically
rebase and return truth without fabricating a PRIMARY receipt.

### Complete generation and lifecycle inputs

Append `initial_key_interval future_key_interval_v1` to
`generation_registration_v1`. Registration runs at `SERIALIZABLE`, locks the
shared registry barrier, creates a missing stream head at position zero or
reloads the existing head, and establishes the new generation at that exact
head position. It atomically creates:

- generation and checkpoint;
- one CURRENT diary frame and one CURRENT waiting-room frame;
- their zero-or-head-position watermarks;
- the initial key interval beginning at checkpoint plus one; and
- the independently lifecycle-authored baseline anchor.

Generated frame identifiers use the sole closed UUID primitive. Exact
registration replay reloads and compares the complete baseline; mismatch
fails.

Add nullable `terminal_reason generation_terminal_reason` to
`context_observer_generation`, with a check requiring NULL for ACTIVE or
REBASE_REQUIRED and non-NULL for REVOKED or CONSUMED. Consumption stores it;
same-reason terminal replay is inert and a different terminal reason fails.

Recovery-pin creation/release is not falsely assigned to registration. The
pin relation remains ungrantable and mutation-inert in this descendant.
Retention conservatively honours valid rows; a separate future lifecycle gate
must add pin mutation authority before operational use.

Exact rotation replay is checked before the current-anchor requirement for a
new effect. An identical stored interval returns inertly. A differing interval
fails. Only a new interval requires current anchor, future partition proof and
an atomic KEY_ROTATION lifecycle/checkpoint update.

### Dedicated retention result

Add enum `source_retention_reason` with exactly:

- `ELIGIBLE`;
- `EXECUTION_DISABLED`;
- `CHECKPOINT_LAG`;
- `ACTIVE_PIN`;
- `KEY_OVERLAP`;
- `GRACE_PENDING`;
- `AMBIGUOUS_CENSUS`; and
- `NO_NON_CONSUMED_GENERATION`.

Change only the `reason_code` field of
`context_source_retention_eligibility_v1` from `observation_reason` to
`source_retention_reason`. Evaluation is read-only under `SERIALIZABLE` and the
registry barrier. Purge rederives the same census in its transaction. The
current policy constraint keeps execution disabled; no success path is claimed
until a later policy gate changes that contract.

## Corrected producer proofs

The producer derives practice, source and stream from the one active binding.
It reselects the exact claim, appointment, audit and sole event under the
existing route-held top-level transaction. It acquires no product DML
privilege. It proves their current-XID provenance and transaction-start facts,
then performs owner-private fabric effects.

`aggregate_revision` is not an Appointment column. It is rederived exactly as
the count of `public.appointment_audit_log.id` for the same practice and
appointment after the new audit insert, matching
`app/services/diary_committed_events.py`. The event and outbox revisions must
equal that count. No locked product revision is invented.

Alias provenance is conditional:

- a newly inserted alias has current-XID provenance and one current outbox
  reference; and
- a reused alias is an older immutable exact practice/source/stream/product
  mapping and must not be required to have current `xmin`.

Head and outbox effects remain current-XID. Alias uniqueness races use exact
winner reload and comparison, never `ON CONFLICT DO NOTHING` as an outcome.

## Exact trigger applicability and return matrix

All functions assert qualified table, timing, row level and declared `TG_OP`.
Unexpected trigger context raises a closed value-free failure. Allowed
immediate `UPDATE` returns `NEW`; allowed immediate `DELETE` returns `OLD`.
Deferred fences return `NULL` only after complete proof. Every shared-table
discriminator uses both `OLD` and `NEW` so rows cannot adopt or escape the exact
family.

| Function | Exact behavior |
|---|---|
| `cf_guard_claim_v1` | Unrelated operation/route updates return `NEW`; exact adoption or escape fails. Exact updates require producer binding, immutable identity/digest fields, current provenance, monotonic target/audit population and only `IN_PROGRESS` to `IN_PROGRESS` or `COMPLETED`. Deleting a current exact claim fails; later cleanup is inert only when explicitly outside this family. |
| `cf_fence_claim_v1` | Exact insert/update reloads final state and proves current XID, transaction-start creation, completed state, target/audit and complete membership. Current exact deletion fails; classified prior cleanup is inert. |
| `cf_fence_appointment_update_v1` | Exact producer binding only. Practice/id cannot change; final tuple equals `NEW`; a second update whose `OLD.xmin` is current-XID fails. Obligation is only the exact OLD/NEW start/duration predicate. True requires exactly one audit/reschedule-event/alias/head/outbox set; false requires no event, alias insertion, head advance or outbox. Other credentials are inert. |
| `cf_guard_audit_v1` | Exact audit membership is immutable. Both images classify command family; unrelated audits retain existing behavior. |
| `cf_fence_audit_v1` | Exact insert proves producer binding, current XID, claim/appointment and complete membership. Exact update/delete fails; unrelated operations are inert. |
| `cf_guard_event_v1` | Update fails if either image is the exact reschedule type/schema; check-in remains outside. Delete fails only for a current-XID exact event; an older exact event returns `OLD` for independent product retention. |
| `cf_fence_event_v1` | Exact insert proves producer binding, current XID, claim/audit/appointment, fixed payload keys and time/duration agreement, aggregate-revision count and exactly one outbox. Exact current update/delete fails; older retention deletion is inert and never requires outbox deletion. |
| `cf_guard_alias_v1` | Update/delete always fails for this exact source/stream mapping. |
| `cf_fence_alias_v1` | Insert proves producer binding, current XID, exact appointment mapping and one current outbox reference. Existing aliases cause no trigger event and are accepted by other fences without current-XID provenance. Update/delete fails. |
| `cf_guard_stream_head_v1` | Lifecycle insert is handled by the baseline fence. Producer update preserves identity/epoch and advances exactly one; delete fails. |
| `cf_fence_stream_head_v1` | Lifecycle insert requires registration-created position-zero head and no producer effects. Producer update proves temporal event/outbox position and final head. Delete fails. |
| `cf_guard_outbox_v1` | Update always fails. Delete returns `OLD` only for a non-current row under the exact retention binding reached through `purge_source_rows_v1` with enabled policy; producer/current or any other delete fails. |
| `cf_fence_outbox_v1` | Insert proves producer binding, current XID, exact event, alias, claim/audit/appointment and head. Update fails. Authorized older retention delete is source-independent and inert; every other delete fails. |

Every deferred fence is read-only, lock-free, sibling-call-free and valid from
final transaction state. No declared trigger order supplies correctness.

## Closed body-program mechanics

In addition to relation operations, `body_program_v1` must have exact typed
primitives for:

- trigger context, legal row-image access and typed trigger return;
- `session_user`, transaction timestamp and isolation assertion;
- PostgreSQL-16 current-XID32 derivation and system `xmin` comparison;
- exact-one/zero/complete-set cardinality;
- fixed JSON keys and typed JSON casts;
- `IS DISTINCT FROM` and timestamp-plus-minutes;
- canonical domain-separated digest profiles;
- `gen_random_uuid()` as the sole opaque UUID source;
- unique insert followed by winner reload/compare;
- immutable final-row reload; and
- propagate-only retry SQLSTATE behavior.

No generic SQL/function call, unqualified identifier, exception catch,
savepoint, transaction control, internal retry, dynamic execution or sibling
trigger call is allowed.

Lifecycle, coordinator and retention entry points explicitly assert
`SERIALIZABLE`; producer and admission assert `READ COMMITTED`. Retryable
`40001` and `40P01` propagate beyond the entire transaction.

## Recovery acceptance

Tests must first prove the accepted parent files and digest are unchanged, then
derive and validate the effective parent. Digest-resealed attacks must cover at
least:

- missing/additional recovery operation;
- product DML privilege or runtime product read;
- missing stream binding or cross-stream RLS;
- Boolean-only admission revision guess;
- fabricated PRIMARY receipt or ambiguous result kind;
- missing initial key material or terminal reason;
- observation reason reused for retention;
- alias reuse forced to current XID;
- unqualified application identifier;
- aggregate revision treated as an Appointment field;
- check-in capture or OLD/NEW discriminator escape;
- second same-transaction appointment update;
- prior-event retention rejection;
- producer outbox deletion or retention deletion rejection;
- absent/wrong head baseline writer;
- order-dependent or mutating deferred fence; and
- missing trigger/body primitive or raw SQL escape.

This recovery grants no implementation, SQL, migration, database, source,
provider, data, runtime, deployment, release, Pages or protected-ref authority.

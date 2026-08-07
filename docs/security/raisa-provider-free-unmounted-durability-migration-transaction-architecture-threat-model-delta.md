# Threat-model delta: durability migration-and-transaction architecture

Date: 2026-08-06

Status: ninth recovered architecture candidate pending independent veto

## Trust boundaries and assets

Newly specified future boundaries are the producer transaction, payload-free
outbox, observer login/projection, authenticated admission receiver, immutable
admission, coordinator transaction, append-only lifecycle/anchor authority,
database binding registry, generation-local key-interval metadata and retention
barrier. None is implemented by this tranche.

Protected assets are practice isolation, appointment/source confidentiality,
gap-free source order, the last contiguous checkpoint, permanent retirement,
complete generation census, recovery anchors, key continuity, minimized audit
and the separation between invalidation and current truth/commands.

## Threats and controls

| Threat | Frozen control |
|---|---|
| Existing feed/cursor is relabelled durable | Exact distinct outbox; staff route, expiry and `(occurred_at,event_id)` cursor remain ineligible. |
| Sequence/identity rollback creates apparent gap | Ordinary row-locked per-practice stream head; head and outbox roll back with the producer transaction. |
| Appointment commits without control row | Enabled producer is in the same transaction; no best-effort after-commit append or bypass. |
| Aggregate revision is treated as continuity | It is anomaly/freshness metadata only; only transaction position/predecessor determine continuity. |
| Outbox leaks product or patient data | Closed columns only; no JSON/text/payload/product identifiers; raw event UUID is non-semantic, normalized and discarded. |
| Alias bridge contradicts the product-identifier ceiling or leaks appointment identity | `diary_context_aggregate_aliases_v1` is the sole closed exception; only an owner-mediated producer entry point can create/return an alias, all other principals have no SELECT/DML/function path, and only the opaque alias enters durability evidence. |
| Producer invokes alias creation outside the signed command | There is no separately executable alias helper. The sole producer projection entry point rederives `session_user` and requires the exact `IN_PROGRESS` update-confirm claim, matching locked appointment/revision and just-authored bound event before any alias/head/outbox effect. |
| Atomic command is split across identities, capabilities or transactions | The signed update-confirm and projection use one physical connection, one transaction, one logical capability and one `session_user`; no second login, `SET ROLE` or transaction hand-off is permitted. |
| Caller substitutes a claim, event or revision | The entry point locks the exact operation/route/request-digest claim, loads the sole event through its existing practice-scoped `(practice_id, command_id)` foreign key plus unique `command_id` constraint and verifies event type/schema, target appointment, audit and aggregate revision against the claim and locked product state. |
| Same login reuses committed in-progress rows in a later transaction | PostgreSQL-16 exact XID32 comparison, immutable transaction-start creation time, zero legacy census, no state reversion and no committed exact-operation `IN_PROGRESS` row. The application contract forbids savepoints/subtransactions and the exact route has none; every relevant subtransaction-authored tuple fails. A no-write savepoint is not database-observable and no broader detection is claimed. XID is ephemeral, non-caller-supplied, non-retained and never a durability position. |
| Temporal update evades publication by suppressing or deleting its event | The appointment `OLD`/`NEW` start/duration transition is the database-derived obligation. A deferred row-level all-`UPDATE` appointment trigger sees both temporal and non-temporal transitions. Exact claim/appointment/audit/event/alias/head/outbox immediate/deferred operations reject missing, extra, updated or insert-deleted members; non-temporal updates require projection absence. |
| Producer call passes but a partial combination commits | Owner-only fixed-search-path guards and deferred constraint triggers forbid prior-transaction claim adoption, state reversion and any committed exact-operation `IN_PROGRESS` row, then fail commit unless the temporal transition, event, completed claim, target/audit, outbox/head and any first alias are bidirectionally complete in the same top-level transaction. |
| Two product appointments share one alias or delete/recreate changes identity | Forward and reverse practice/source uniqueness make the mapping bijective; rows and aliases are immutable and non-deletable for the v1 epoch, same-appointment races return the winner and collision rolls back the command. |
| Durability retention deletes or uses the product alias bridge as purge authority | The bridge is outside all three durability retention families, update/delete are prohibited for v1 and any future erasure/non-reuse scheme requires a new reviewed contract/epoch; it never cascades or rewrites retained opaque evidence. |
| Alias-only failure survives command rollback | Appointment truth, audit, event, alias, head, outbox and idempotency result share one transaction; standalone/mismatched invocation fails before effect and every member rolls back together. |
| Outbox retention silently pins product-bearing events | The raw event UUID is checked transaction-locally by paired deferred fences, but the outbox has no persistent foreign key to `diary_committed_events`. Product-event expiry or later separately authorised deletion does not delete or invalidate the independent outbox and grants no source-purge authority. |
| Observer reads base/product tables | Exact projection privilege only; direct base-table access denied. |
| Observer packet is altered or forged at the coordinator | Receiver rederives observer `session_user`, reselects exact source membership and appends one immutable packet/source/binding admission; coordinator accepts only stored admission meaning. |
| Observer gains persistence authority through admission | Observer has no DML/checkpoint privilege. The distinct non-login receiver owner has exact source/generation/checkpoint/receipt/key/binding reads and admission `INSERT` only; its function admits only the exact closed packet and has no update/delete or durability-effect authority. |
| Conflicting admission cannot be represented without overwriting the primary | The receiver stores at most one immutable `PRIMARY` and one immutable `CONFLICT` sentinel per generation/position; the sentinel binds authenticated identity, source coordinate, attempted digest and a closed reason without storing the packet. |
| Repeated conflicting submissions create an unbounded storage attack | Exact duplicate is inert; the first mismatch/reuse creates the sole conflict sentinel and every later mismatch returns it without another append. |
| Concurrent first admissions suppress a mismatch through a uniqueness race | On a primary or generation-local observation-digest uniqueness conflict, the receiver reloads the winner; equality is inert and inequality appends or returns the sole conflict sentinel. |
| Coordinator becomes generic writer | One typed entry point; no direct table DML, raw source/product read, admission creation, API or command authority. |
| Caller forges `app.current_practice_id` | Authority derives from authenticated `session_user` binding; caller GUC/packet/argument is never sufficient. |
| Pool reuses one broad login across practices/capabilities | Exactly one active practice/capability/source/epoch binding per credential-bearing login; duplicate binding and cross-boundary pool reuse fail closed. |
| RLS is bypassed through owner/inheritance/SET ROLE | Forced RLS, non-login owner, NOINHERIT/NOBYPASSRLS roles, public/default revoke and negative privilege matrix. |
| Unsafe security-definer resolves attacker objects | Fixed empty/schema-qualified search path, no dynamic SQL, owner non-login, public execute revoked. |
| Partial coordinator effects survive | SERIALIZABLE transaction and exact checkpoint lock; receipt/watermark/retirement/obligation/lifecycle/audit/checkpoint are atomic. |
| `ON CONFLICT DO NOTHING` hides corruption | Exact redelivery comparison; mismatch, reuse or gap atomically rebase. |
| Safe source purge hides a later altered resubmission or breaks redelivery | Receiver compares retained primary/receipt before source selection and can append the sole conflict sentinel after purge; coordinator loads the complete retained set, so clean redelivery needs no source and a conflict remains visible. |
| Rotation revision is rewritten as audit | One total-order lifecycle journal with one-to-one decision audit details. |
| Obligation count drifts | Bucket rederived from canonical admitted history under checkpoint lock; no caller or convenience counter authority. |
| Coordinator self-anchors restart | Append-only anchor per checkpoint lifecycle revision is created by separate lifecycle authority; next transition is fenced until exact anchor/state agreement. |
| Crash occurs after checkpoint commit but before anchor | Receiver-owned bounded admissions may continue, but no coordinator consumption or next decision/rotation transition occurs; lifecycle authority independently verifies the complete committed state before appending the pending anchor, otherwise a new generation is required. |
| Key rotation silently diverges across generations | Each partition and rotation is keyed to one exact generation; its schedule/lifecycle/checkpoint transaction changes no other generation. |
| Key interval is retroactively edited or key tried by fallback | Exact generation-local gap-free future-fenced partition; no historical change, key bytes or try-every-key behavior; failure consumes that generation. |
| Fast consumer/self-supplied census authorizes purge | SERIALIZABLE registry barrier and complete backend-derived non-consumed census; caller supplies no retention authority. |
| Concurrent generation is omitted during purge | Registration/rebaseline and purge lock the same barrier. |
| Source purge erases admission/anchor/receipt/audit evidence | Three separate retention families, primary/conflict admissions and anchors in the receipt/checkpoint family, retained together for their meaning, and no cascade. |
| Capacity pressure silently drops continuity | Block/retry or consume/rebaseline under later policy; never discard unseen rows. |
| Disabled/default state acquires credentials or moves data | No runtime binding and retention executor disabled; later gate proves zero capability. |
| Event starts a fresh read or command | Event may invalidate and create inert obligation only; later read requires application principal and new grant. |
| Digest chain is claimed cryptographically authentic | Explicit tamper-evidence/integrity label; no MAC or compromised-owner claim. |
| Machine schema lists relations but leaves unsafe columns/keys/roles/triggers unconstrained | The normative v3 contract closes builtins/domains/enums/composites, every structured column/nullability/default, named key/index/FK/check, exact forced-RLS `USING`/`WITH CHECK` policy, role/function ownership and internal grant, entry-point input/output, trigger-function signature/event and cross-invariant enforcement reference. The schema is a whole-contract constant, while digest-resealed semantic variants are tested independently of that hash. |
| Structural renderer invents security-critical PL/pgSQL from prose | The contract marks entry-point and trigger bodies absent, requires the structural renderer to omit those functions/triggers and their execute grants, and blocks DDL rehearsal until a separately reviewed function-and-trigger-body architecture closes them. |
| Admission function owner gains product read or broader DML | Renderer semantics require exact closed ownership, read, INSERT and execute lists and digest-resealed tests add product SELECT and UPDATE authority independently; any widening fails. |
| Architecture artifacts execute SQL | Static boundary tests and exact Git pre/postflight forbid migrations, app/API/runtime/database changes. |

## Residual risks deliberately deferred

Executable DDL correctness, actual PostgreSQL version behavior, migration locks,
connection pooling/session identity, operational credentials and key store,
real crash recovery, monitoring/alerting, production retention duration and
capacity, privacy assessment, live source load, deployment and incident
response remain later gates.

## Forbidden openings

No protected evidence or historical PHI. No app/Alembic/API change, executable
SQL, database/source/network/provider contact, table/role/credential creation,
product/patient data, command/write authority, runtime wiring, deployment,
production, release, Pages or protected-ref movement.

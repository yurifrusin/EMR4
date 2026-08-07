# Provider-free unmounted durability function-and-trigger-body architecture design

Date: 2026-08-07

Status: deterministic builder, schema and hostile-packet candidate pass;
pending exact-head independent veto

Parent result:
`raisa_provider_free_unmounted_durability_migration_transaction_architecture_pass`

Immutable parent source HEAD:
`c55d25d6c9704ae4612ef2d123158f71302ab411`

Immutable parent contract:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

Normative recovery:
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-recovery.md`

Normative implementation recovery:
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-implementation-recovery.md`

Rejected label-only candidate:
`sha256:c16930c2d6c400c93ea2c2b413ccf084ceb38c4f980fa4edae032b74e3112622`

Rejected typed-but-misbound candidate:
`sha256:f8afd0ce97169b0fae926dbe7999b9961d9be7506f711de579a3c035f75b2064`

Current deterministic typed-IR candidate:
`sha256:8871663b121dedff089b7517406f8223a3df2153bce66716d624b2f321e20dde`

## Purpose and derivation

This design closes the machine-readable body boundary deliberately left open by
the accepted PostgreSQL 16 migration-and-transaction architecture. It defines
how exactly nine security-definer entry points and thirteen trigger functions
can be represented, checked and later lowered without emitting or executing
SQL in this tranche.

The first uncommitted implementation candidate is not an implementation source.
Its programs selected ordered semantic labels whose operands, branches,
cardinality, assignments and terminals were not represented. A renderer would
therefore have had to invent executable meaning. This recovered design instead
requires a closed, discriminated and typed abstract syntax tree (AST) from which
the validator can derive effects, locks, calls, failures and terminals without
interpreting prose or labels. A second, superficially typed candidate was also
rejected because its actual operands targeted wrong relations, omitted sources
and crossed trigger row-image boundaries. No program or profile from either
rejected candidate is an implementation source.

The accepted parent remains byte-immutable. The child first verifies its exact
hash, applies one closed `structural_feasibility_recovery_v1`, and derives one
effective parent. Every recovery operation is enumerated and typed; a missing,
unknown, reordered-with-semantic-effect or additional operation fails. Bodies
bind only the effective parent. The recovery is not a general override surface
and cannot weaken an unchanged parent invariant.

The effective parent differs only by:

- one non-null `stream_id` on the active service binding, aggregate-alias and
  retention-policy coordinates, plus stream-aware keys, foreign keys, RLS and
  the existing `session_binding_allows_v1` helper;
- exact `SELECT` for `context_schema_owner` on the four qualified application
  relations, exact binding-table `SELECT` for `context_admission_receiver`, and
  migration-only installation-time `TRIGGER` authority;
- the truthful `durability_transition_result_v1` coordinator result;
- registration's typed initial key interval, a stored terminal reason,
  registration-owned position-zero stream-head baseline and independently
  lifecycle-authored baseline anchor;
- exact inert rotation replay before the new-effect anchor fence;
- the dedicated closed `source_retention_reason` vocabulary; and
- corrected aggregate-revision, alias-provenance and trigger-applicability
  semantics.

The final grammar additionally makes complete-set values explicit as
`<qualified-relation>[]`, constructs every composite result from exact typed
field operands, exposes the bounded purge count, and derives the real slowest
checkpoint with a closed `MIN_FIELD` over an already selected complete set.

No other parent type, relation, signature, role, policy, invariant or authority
changes.

## API Spine and authority boundary

This remains internal async durability architecture. GraphQL is read-only and
unchanged. REST/OpenAPI remains the only command plane and receives no route or
operation. The existing signed `confirmAppointmentUpdateProposal` /
`update-confirm` REST transaction is the only future producer mutation
boundary. An event, outbox row, admission, receipt, checkpoint, anchor,
watermark or obligation is an observation or integrity record, never current
truth, command evidence, command authority or a substitute for a fresh
authorised product read.

The existing `GET /api/v1/diary/events/committed` feed and its signed
`(occurred_at,event_id)` cursor are explicitly ineligible for durability
position, acknowledgement or observer authority. Check-in events remain
outside the exact reschedule discriminator. This design adds no GraphQL
mutation/subscription, REST command, event consumer, acknowledgement, fresh
read, provider invocation or product write.

## Trust principals and privilege ceiling

The planes remain distinct:

| Principal | Exact ceiling |
|---|---|
| `context_schema_owner` | Non-login, `NOINHERIT`, `NOBYPASSRLS` owner of fabric objects and all bodies except admission. It receives exact application-table `SELECT`, never application DML. |
| `context_producer` | Login that may execute only `project_update_confirm_reschedule_v1`; no direct alias, head, outbox or product-table grant from this architecture. |
| `context_observer` | Login with exact scoped payload-free outbox read and execution of admission only; no admission DML or durability transition. |
| `context_admission_receiver` | Non-login owner of admission only, with exact source/generation/checkpoint/receipt/key/binding reads and admission `INSERT`; no product read, update/delete, coordinator or lifecycle effect. |
| `context_coordinator` | Login that may execute only the typed transition entry point; no admission creation, source/product read or direct durability DML. |
| `context_lifecycle` | Login that may execute registration, independent anchor append, rotation and terminal consumption only. |
| `context_retention` | Login that may evaluate and, only behind a later enabled policy, request bounded source purge. |
| `context_application_read` | Separate current-truth read principal; no durability write or command authority. |

The owner reads only these qualified product relations and only the columns
declared by body effects: `public.appointment_command_idempotency`,
`public.appointments`, `public.appointment_audit_log` and
`public.diary_committed_events`. Table-level `SELECT` exists so the owner can
inspect system `xmin`; body-level column effects remain narrower. It receives
no product `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, ownership or login.
Application rows are already locked by the existing top-level route or are
current-transaction inserts; a body does not reacquire an application update
lock or invent an application DML privilege.

Migration installation authority is not a runtime grant. Trigger functions are
owner-internal, have no runtime execute grant, and `PUBLIC` execute is revoked.
Every security-definer body derives `session_user`, uses fixed search path
`pg_catalog, emr4_context_fabric`, resolves every relation/type with a qualified
catalogue identifier, contains no dynamic SQL and cannot change role or
configuration.

## Stream and binding scope

An active service binding is exactly one database login, logical capability,
practice, source contract, stream, binding revision and credential epoch.
Every entry point rederives that binding from `session_user`; caller-supplied
practice/source/stream values are locators to compare, not authority. An
absent, duplicate, inactive, cross-capability, cross-practice, cross-source,
cross-stream or wrong-epoch binding fails before effect.

The producer never chooses `stream_id`: it derives the one active stream. Typed
observer, coordinator, lifecycle and retention locators must equal that stream.
Every stream-bearing RLS check passes the row or locator stream to the
stream-scoped `session_binding_allows_v1`. The alias bridge and retention policy
are keyed by practice/source/stream, and the outbox-to-alias reference carries
the same coordinates. A Boolean binding result cannot substitute for recording
and comparing the exact observer binding revision at admission.

## Closed typed body-program language

Each body is exactly one `body_program_v1` containing an ordered tree of
discriminated `instruction_node_v1` objects. A node is selected by one closed
opcode and the schema branch for that opcode requires every operand and forbids
all operands belonging to another opcode. A node is never a step label,
statement, SQL fragment or prose reference. Its children are exact node IDs in
that body, and reachability, convergence and terminal coverage are validated
from the root.

The finite instruction family covers only:

- exact trigger-context and transaction-isolation assertions;
- binding rederivation from `session_user`;
- exact-cardinality relation reads and stable-primary-key row locks;
- typed assignment and canonical digest derivation;
- typed predicate assertion and conditional branching with explicit children;
- bounded iteration over a database-derived complete set;
- exact insert, unique-race winner reload/compare, exact update and the sole
  bounded source-row delete;
- exact allowlisted support-function invocation;
- immutable final-row reload;
- typed row, composite and trigger terminals; and
- one value-free failure raise, with `40001` and `40P01` propagated rather than
  caught or retried.

Each operation carries only its required qualified relation/column references,
typed input/output symbols, cardinality, lock mode and ordinal, expressions,
column-to-expression write bindings, branch children, call arguments, return
source or failure ID. A reference cannot name a relation, column, symbol,
primitive, function, row image or type that is not valid at that exact node.

Expressions are a second discriminated AST, not strings. `REF` selects one
in-scope declared symbol, qualified row column, legal trigger system field or
exact primitive result. `CONST` carries an allowlisted type and closed value.
Every other operator has schema-fixed arity, operand types and result type.
Dedicated expression nodes close `session_user`, transaction timestamp,
PostgreSQL-16 current-XID32, system `xmin`, fixed JSON-key extraction and typed
casts, exact cardinality, `IS DISTINCT FROM`, timestamp-plus-minutes,
domain-separated canonical digests and `gen_random_uuid()` as the sole opaque
UUID generator. Generic calls, free-form expression leaves and caller-selected
identifiers are unrepresentable.

Every program has a closed symbol table. Entry-point inputs, row-shape outputs,
locals and composite returns are declared with exact effective-parent types.
For trigger programs, `TG_OP`, `OLD` and `NEW` are typed system bindings, and
row-column access is legal only inside an event arm for which the declaration
provides that image. Every declared event has one reachable arm; a default arm
raises the closed unexpected-context failure. An instruction may not refer to
an undeclared symbol or one declared in another body.

Raw or dynamic SQL, interpolation, generic execute/call, recursion, exception
swallowing, savepoints, internal retry, transaction control, DDL, role or
configuration mutation, notifications, network/file access and unallowlisted
extension calls have no schema representation.

## Full signatures, trigger declarations and terminals

The effective-parent derivation emits twenty-two full ordered signature
objects: the nine entry points followed by the thirteen trigger functions.
Each signature binds exact ordered input modes and types, output type and
cardinality, language, owner, executor where applicable, strictness,
volatility, parallel safety, security-definer state, fixed search path,
`PUBLIC` execute denial and invariant IDs. Name-only or summary signatures are
not admissible.

Each of the thirteen trigger declarations independently binds its exact
qualified relation, timing, row level, ordered event set, deferrability,
initially-deferred state and function. A declaration and its function signature
must match the derived effective parent exactly.

All thirteen trigger functions have the same function-signature result:
`pg_catalog.trigger`. `RETURN_NEW`, `RETURN_OLD`, `RETURN_NULL` and `RAISE` are
typed branch terminals only. They never replace or specialize the function
signature. The per-event matrix and the reachable terminal in the corresponding
`TG_OP` arm must agree exactly.

## Derived effects, lock order and call graph

Every instruction has a column-minimal local footprint determined by its opcode
and operands. The validator walks reachable nodes in deterministic program
order and rederives, rather than trusts:

- exact relation/column reads, including legal `OLD`/`NEW` and system-column
  reads;
- relation, key, lock mode and stable acquisition ordinal;
- inserted, updated and deleted columns;
- called support functions and structured `{from,to}` edges;
- reachable failure IDs and branch terminals; and
- output source and cardinality.

The aggregate must equal a separately frozen body-specific effect summary and
stay within the effective-parent privilege ceiling. Relation-wide profiles are
forbidden unless one instruction really references every listed column.
Branch-specific proofs also compare exact path effects: retained exact replay,
terminal replay and authorized retention delete cannot inherit source/product
reads merely because another branch uses them.

Lock order is the traversal-derived sequence of typed lock nodes, not a copied
list. The producer, admission, coordinator, lifecycle and retention orders are
compared independently. Removing, swapping or changing a lock mode fails even
when the modified relation and lock mode are otherwise allowlisted.

Call edges are derived only from typed call nodes and stored as structured
fully qualified `{from,to}` pairs. The validator computes acyclicity. Entry
points do not call sibling entry points, trigger functions do not call sibling
triggers, and no trusted `acyclic` or `no_sibling_calls` Boolean can substitute
for graph analysis.

## Whole-contract and positional closure

The whole-contract schema closes both membership and position. Ordered
`prefixItems`, body-specific `const` branches or an equivalent exact
construction bind all twenty-six recovery operations, twenty-two signatures,
thirteen trigger declarations, twenty-two programs, their symbol tables,
instruction trees, branch children, expressions, exact summaries and
terminals. A globally valid program, instruction, relation, column, predicate,
return or declaration is invalid when moved to another body or position.

The top-level contract digest and section seals are tamper checks only. Static
semantic validation must still reject a hostile candidate after its top-level
and schema digests have been refreshed. Required attacks include unknown
expression operators/leaves, symbol invention/removal, swapped instructions or
bodies, missing provenance, changed `OLD`/`NEW` columns, removed/reordered
locks, widened product reads, changed owner/output, swapped trigger declaration
or terminal, invented recovery operation and a derived call cycle.

The failure registry remains closed and value-free. Each custom failure family
has one unique five-character uppercase alphanumeric SQLSTATE and one stable
non-sensitive reason code. Metadata may name only the contract reason and body;
it cannot expose a practice, appointment, patient, actor, UUID, digest,
credential, packet or row value. Unexpected database failures propagate and
roll back. Uniqueness errors may be classified only by reloading and comparing
the immutable winner.

## Nine entry-point semantics

| Entry point | Exact body contract |
|---|---|
| `project_update_confirm_reschedule_v1` | At `READ COMMITTED`, rederive the one producer binding/stream; before fabric effect reselect and prove the exact eligible current-XID `IN_PROGRESS` claim, locked appointment tuple, current audit and sole reschedule event. Prove transaction-start creation, exact operation/route/request digest, target/audit bindings, fixed payload and temporal agreement. Derive `aggregate_revision` as the count of `public.appointment_audit_log.id` for the same practice/appointment after the insert, and require event/outbox equality. Create or reload/compare one immutable practice/source/stream/product alias; only a new alias requires current-XID provenance. Lock the one stream head, append one payload-free outbox row, advance by exactly one and return the immutable outbox row. No fabric effect precedes full proof. |
| `admit_proofread_observation_v1` | At `READ COMMITTED`, rederive the observer and exact binding revision. First lock/load the retained admission set and receipt without source access. Then branch in this exact order: return inert exact primary replay; if a retained primary differs, append/reload the sole conflict sentinel without source access and return it; return any already retained conflict; if no admission exists at the locator, reselect and authenticate the exact source row and generation-local key membership; only after that authentication detect cross-position observation-digest reuse and persist/reload the sole conflict sentinel, otherwise persist/reload the primary. A first cross-position conflict can never precede source authentication. Every uniqueness race reloads and compares the winner. Record the actual binding revision; never accept a guessed Boolean binding. |
| `apply_durability_transition_v1` | At `SERIALIZABLE`, accept only an admission locator; rederive binding and follow the fixed lock order below. Exact retained receipt replay is source-independent and inert only with a matching primary and no conflict. A conflict, demonstrated gap, wrong predecessor/epoch, missing primary or key uncertainty atomically rebases without fabricating a receipt. Receipt, watermarks, one-way retirement, coalesced obligation, lifecycle, audit and checkpoint commit together. Return exactly one `durability_transition_result_v1` whose kind is `RECEIPT_APPLIED`, `RECEIPT_REPLAYED`, `REBASE_APPLIED` or `TERMINAL_REPLAYED`; evidence is the stored receipt digest only for receipt results and the resulting checkpoint integrity digest otherwise. `TERMINAL_REPLAYED` is derived from the stored terminal generation, checkpoint and result-integrity state. This entry point has no caller terminal-reason symbol and never applies the consumption-only terminal-reason-equality rule. |
| `register_observer_generation_v1` | At `SERIALIZABLE`, rederive lifecycle binding and lock the shared registry barrier. Create a missing position-zero stream head or reload the existing head, then establish the generation at that exact position. Atomically create generation, checkpoint, CURRENT diary/waiting-room frames, watermarks, the supplied initial key interval beginning at checkpoint plus one, and an independently lifecycle-authored baseline anchor. Generated frame identifiers use only the closed UUID primitive. Exact replay compares the complete baseline; any difference fails. |
| `append_recovery_anchor_v1` | At `SERIALIZABLE`, independently reload and reverify the complete committed checkpoint, lifecycle, receipt/audit and controlling digests before appending the one immutable anchor for the requested lifecycle revision. It cannot trust a coordinator candidate, repair state or advance a checkpoint. Exact replay reloads/compares; mismatch requires a new generation or rebase under the parent rules. |
| `rotate_observation_key_v1` | At `SERIALIZABLE`, check an identical stored interval first and return it inertly; a differing replay fails. Only a new interval locks barrier, generation/checkpoint, current anchor and schedule, proves a future-only gap-free partition and predecessor overlap, appends one `KEY_ROTATION` lifecycle row and advances only that generation's schedule/checkpoint revision. It cannot change historical intervals or another generation. |
| `consume_observer_generation_v1` | At `SERIALIZABLE`, lock the lifecycle scope and perform only a one-way terminal transition. Store the exact `terminal_reason`; same-state/same-reason replay is inert and a different reason fails. It cannot reactivate, rebase or mutate another generation. |
| `evaluate_source_retention_v1` | Read-only at `SERIALIZABLE`; lock the shared registry barrier, derive the complete non-consumed-generation census, slowest checkpoint, valid pins, key overlap and policy grace in the database, and return the dedicated eligibility/reason result. Caller filters, counts, clock claims and supplied minima have no authority. Ambiguous or empty unsafe census states deny eligibility. |
| `purge_source_rows_v1` | At `SERIALIZABLE`, rederive the same complete census and policy in the purge transaction. Delete only qualified payload-free outbox source rows through the exact eligible position and return the exact purge result. Current policy is disabled, so no successful deletion path is claimed in this descendant. No product event, alias, admission, anchor, receipt, checkpoint, lifecycle, audit, frame, key or pin deletion and no cascade are representable. |

The common lock order is binding check, registry barrier,
generation/checkpoint, current recovery anchor, retained admission/receipt, key
intervals, then dependent rows in stable primary-key order. Producer uses claim,
existing appointment/audit/event proof, alias, then stream head/outbox; admission
uses retained admissions/receipt before source/key. No body acquires another
plane's locks in reverse order.

Recovery-pin mutation remains absent and ungrantable. Evaluation conservatively
honours any valid pin rows, but no current entry point claims pin creation or
release authority.

## Thirteen-trigger matrix

All functions assert qualified table, timing, row level and exact declared
`TG_OP`; unexpected context raises a closed value-free failure. Immediate
allowed updates return `NEW`, allowed deletes return `OLD`; deferred fences
return `NULL` only after proof. Shared-table discriminators inspect both images
to stop adoption and escape.

| Function | Events | Closed semantics |
|---|---|---|
| `cf_guard_claim_v1` | `BEFORE UPDATE, DELETE` | Unrelated operation/route updates return `NEW`; exact adoption/escape fails. Exact updates preserve identity/digests and current provenance, advance target/audit monotonically and allow only `IN_PROGRESS` to `IN_PROGRESS`/`COMPLETED`. Current exact deletion fails; classified later cleanup is inert only outside the family. |
| `cf_fence_claim_v1` | deferred `AFTER INSERT, UPDATE, DELETE` | Exact final insert/update proves current XID, transaction-start creation, completed claim, target/audit and complete membership. Current exact deletion fails; classified prior cleanup is inert. |
| `cf_fence_appointment_update_v1` | deferred `AFTER UPDATE` | Only exact producer binding is relevant; practice/id cannot change and final tuple equals `NEW`. If `OLD.xmin` is current-XID, reject a second same-top-level-transaction update. Obligation is exclusively `OLD.start_time IS DISTINCT FROM NEW.start_time OR OLD.duration_minutes IS DISTINCT FROM NEW.duration_minutes`: true requires exactly one audit/event/alias/head/outbox set; false requires event absence, no alias insert, no head advance and no outbox. Other credentials are inert. |
| `cf_guard_audit_v1` | `BEFORE UPDATE, DELETE` | Classify both images; for each potentially exact image, perform an exact-cardinality read of its matching qualified `public.appointment_command_idempotency` row using only `practice_id`, `id`, `operation_id` and `route_family`. Exact command-family audit membership is immutable; adoption/escape fails and unrelated audits retain existing behavior. The read is present in this body's derived column-minimal effect summary. |
| `cf_fence_audit_v1` | deferred `AFTER INSERT, UPDATE, DELETE` | Exact insert proves producer binding, current XID, claim/appointment and complete membership. Exact update/delete fails; unrelated operations are inert. |
| `cf_guard_event_v1` | `BEFORE UPDATE, DELETE` | Update fails if either image is exact reschedule type/schema. Check-in and every other family remain outside. Delete fails only for a current-XID exact event; an older exact event returns `OLD` for independent product retention. |
| `cf_fence_event_v1` | deferred `AFTER INSERT, UPDATE, DELETE` | Exact insert proves producer binding, current XID, claim/audit/appointment, fixed keys/casts, temporal agreement, audit-count aggregate revision and exactly one outbox. Exact current update/delete fails; older product-retention deletion is inert and never requires outbox deletion. |
| `cf_guard_alias_v1` | `BEFORE UPDATE, DELETE` | Every update/delete of the exact source/stream mapping fails. |
| `cf_fence_alias_v1` | deferred `AFTER INSERT, UPDATE, DELETE` | Insert proves binding, current XID, exact appointment mapping and one current outbox reference. Reused aliases fire no insert trigger and are accepted without current-XID provenance. Update/delete fails. |
| `cf_guard_stream_head_v1` | `BEFORE UPDATE, DELETE` | This function has no `INSERT` arm or insert terminal. Registration's position-zero insert is owned and validated only by `cf_fence_stream_head_v1`. Producer update preserves identity/epoch and advances exactly one; delete fails. |
| `cf_fence_stream_head_v1` | deferred `AFTER INSERT, UPDATE, DELETE` | Lifecycle insert requires registration-created position-zero head and no producer effects. Producer update proves the temporal event/outbox position and final head. Delete fails. |
| `cf_guard_outbox_v1` | `BEFORE UPDATE, DELETE` | Update always fails. Delete returns `OLD` only for a non-current row under the exact enabled retention binding reached through `purge_source_rows_v1`; producer/current or any other deletion fails. |
| `cf_fence_outbox_v1` | deferred `AFTER INSERT, UPDATE, DELETE` | Insert proves producer binding, current XID, exact event, alias, claim/audit/appointment and head. Update fails. Authorised older retention deletion is source-independent and inert; every other deletion fails. |

Every deferred fence is read-only, lock-free and sibling-call-free. It derives
correctness independently from final transaction state; trigger firing order is
never an input. Queued insert/delete events plus current-XID provenance prevent
erasing a required current member. The appointment second-update check prevents
queued temporal and non-temporal obligations from contradicting each other.

## Renderer order and claim ceiling

The only admissible later inert renderer order is:

1. derived effective-parent schema, types, relations, constraints, forced RLS
   and the stream-scoped existing support helper;
2. the nine exact entry-point signatures and mechanically lowered programs;
3. the thirteen trigger-function signatures and mechanically lowered programs;
4. the thirteen parent trigger declarations;
5. `PUBLIC` revocation, exact effective-parent owner/receiver grants,
   migration-only trigger installation and exact runtime execute grants; and
6. static catalogue and privilege assertions.

This design does not perform that lowering. It creates no SQL, DDL, migration,
function, trigger, grant, role, relation, database object, credential, source
connection, persisted state or runtime path. It contacts no database, source,
provider, network service or product data. It grants no product/patient read,
command/write, application change, deployment, release, Pages rebuild or
protected-ref authority.

Passing this candidate's later static acceptance would prove only an exact
provider-free unmounted body architecture. It would not prove PostgreSQL
grammar, executable DDL, transaction/trigger behavior, operational privileges,
migration locks, performance, cryptographic authenticity or production safety.

# Provider-free unmounted durability function-and-trigger-body architecture plan

Date: 2026-08-07

Status: initial plan superseded by bounded structural-feasibility recovery;
first label-only and second misbound typed implementation candidates rejected;
normative Sol implementation recovery active

Parent result:
`raisa_provider_free_unmounted_durability_migration_transaction_architecture_pass`

Parent source HEAD:
`c55d25d6c9704ae4612ef2d123158f71302ab411`

Parent contract:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

Normative recovery:
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-recovery.md`

Normative implementation recovery:
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-implementation-recovery.md`

Normative typed-IR replacement recovery:
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-typed-ir-recovery.md`

## Objective

Freeze the exact machine-readable bodies for the nine security-definer entry
points and thirteen trigger functions deliberately omitted by the accepted
durability migration/transaction structural architecture. The child contract
must make control flow, relation and column references, lock order, database
effects, failure SQLSTATEs, trigger return behavior, privilege effects and the
later renderer order deterministic without rendering or executing SQL. It must
preserve the accepted parent artifact byte-for-byte, bind its hash, apply only
the closed normative recovery delta, and mechanically derive one effective
parent before body validation.

The intended result is
`raisa_provider_free_unmounted_durability_function_trigger_body_architecture_pass`.

This tranche is pure, provider-free, unmounted and repository-local. It creates
no function, trigger, grant, role, relation, migration, database object,
credential, source connection, runtime or product-data path.

## API Spine classification

This remains internal async durability architecture:

- GraphQL remains read-only and unchanged;
- REST/OpenAPI remains the only command plane and gains no operation;
- the existing signed appointment update-confirm command remains the sole
  future producer mutation boundary;
- events and the future payload-free outbox remain observations, never current
  truth, command authority or a fresh-read substitute;
- the existing staff committed-event GET route and cursor remain ineligible as
  observer durability authority; and
- no route, subscription, acknowledgement, provider call, command or
  event-triggered read is added.

The governing sources are `orchestration/api_spine_adr.md`,
`orchestration/api_spine_programme.md`,
`orchestration/bernie_release_gates.md`,
`docs/api-spine/async/integration-events.yaml`,
`docs/api-spine/openapi/diary-committed-events.yaml` and
`docs/api-spine/graphql/practice-context-fabric-read.graphql`.

## Frozen architecture surface

This tranche may add only:

- this plan, its normative recovery, one design and one threat-model delta;
- one child contract and whole-contract JSON Schema under a new
  `orchestration/continuity/` directory;
- static and authored-synthetic adversarial tests;
- bounded read-only analysis and independent-veto artifacts; and
- closeout, acceptance, error-register and Continuity/Compass artifacts.

The accepted parent contract and every application/API artifact are immutable
inputs. The child may contain one closed
`structural_feasibility_recovery_v1` delta exactly matching the normative
recovery; no other override is legal. No `app/**`, `alembic/**`,
`docs/diary/**`, `docs/api-spine/**`, runtime
configuration, existing model, source adapter or parent contract may change.
Preserve and exclude `docs/branding/` and every unrelated untracked
receipt/state/evidence/cost-ledger artifact.

## Exact body population

The child contract must bind exactly these nine parent entry points:

1. `project_update_confirm_reschedule_v1`;
2. `admit_proofread_observation_v1`;
3. `apply_durability_transition_v1`;
4. `register_observer_generation_v1`;
5. `append_recovery_anchor_v1`;
6. `rotate_observation_key_v1`;
7. `consume_observer_generation_v1`;
8. `evaluate_source_retention_v1`; and
9. `purge_source_rows_v1`.

It must also bind exactly these thirteen trigger functions:

1. `cf_guard_claim_v1`;
2. `cf_fence_claim_v1`;
3. `cf_fence_appointment_update_v1`;
4. `cf_guard_audit_v1`;
5. `cf_fence_audit_v1`;
6. `cf_guard_event_v1`;
7. `cf_fence_event_v1`;
8. `cf_guard_alias_v1`;
9. `cf_fence_alias_v1`;
10. `cf_guard_stream_head_v1`;
11. `cf_fence_stream_head_v1`;
12. `cf_guard_outbox_v1`; and
13. `cf_fence_outbox_v1`.

No helper, overload, generic procedure or unlisted body may be introduced. The
effective-parent delta may change only the existing
`session_binding_allows_v1` signature/body to add exact stream scoping; it does
not add a support function. The child still contains exactly nine entry-point
and thirteen trigger body programs.

## Normative body-program representation

The child contract is normative. Each body is one closed `body_program_v1`, not
PL/pgSQL prose and not a SQL string. It must contain:

- exact parent signature, owner, executor, security-definer, strictness,
  volatility, parallel-safety and fixed-search-path binding;
- an ordered typed instruction tree with no free-form statement field;
- closed input, local symbol, row-shape and return bindings;
- exact relation/column reads, row-locks, inserts, updates and permitted deletes;
- exact support-function or sibling-body calls and an acyclic call graph;
- exact predicates as a closed boolean/expression AST;
- exact branch coverage, including empty, duplicate, conflict, terminal,
  retryable and fail-closed outcomes;
- exact SQLSTATE and non-sensitive reason code for every explicit rejection;
- exact trigger `TG_OP`/`OLD`/`NEW` access and `RETURN NEW`, `RETURN OLD` or
  `RETURN NULL` behavior; and
- exact output row source and cardinality.

The instruction vocabulary must be a finite allowlist sufficient for this
contract only. It may include typed operations for binding rederivation,
load-one/load-set, stable-primary-key row locking, assignment, digest
derivation, conditionals, bounded iteration over a database-derived complete
set, insert, exact update, source-row purge, invariant assertion, immutable
winner reload, support call, return and raise. It must not contain raw SQL,
dynamic SQL, interpolation, arbitrary identifiers, arbitrary expressions,
generic execute, recursion, exception swallowing, autonomous retry, transaction
control, savepoints, DDL, role change, configuration mutation, notification,
network/file access or extension calls.

Closed composite construction must expose every catalogue field and typed value
operand in exact field order. The source-row purge must expose its bounded
affected-row count as a typed `pg_catalog.bigint` local so its returned result
is derived from the delete rather than asserted as prose.

The finite vocabulary must additionally close, rather than imply, exact
trigger context assertions; legal `OLD`/`NEW` access; `session_user`;
transaction isolation and transaction timestamp; PostgreSQL-16 current-XID32
derivation and system `xmin`; exact-cardinality loads; fixed JSON-key
extraction and typed casts; `IS DISTINCT FROM`; timestamp-plus-minutes;
domain-separated canonical digests; `gen_random_uuid()` as the only opaque UUID
generator; unique-insert winner reload/compare; and typed
`RETURN_NEW`/`RETURN_OLD`/`RETURN_NULL`. These are named closed primitives, not
generic function calls or free-form expressions.

Complete-set reads have the explicit type `<qualified-relation>[]`. The closed
`MIN_FIELD` primitive may derive the minimum of one selected, catalogued column
from such a complete set; it cannot name a new relation or column. Retention
eligibility and purge use that operand-derived minimum rather than a fixed or
authored through-position.

Every identifier is selected from the parent type/relation/column/function
catalogue or the exact read-only existing-model fields parsed from
`app/models/appointments.py`, `app/models/diary_events.py`,
`app/routers/appointments.py`, `app/services/appointment_idempotency.py`,
`app/services/diary_committed_events.py` and
`app/schemas/diary_events.py`. Those application files are evidence-only and
may not change. Application relations are identified as `public.<relation>`;
fabric relations and types are identified as
`emr4_context_fabric.<identifier>`. The body contract may not use an
unqualified relation or type.

## Body effect and authority closure

For every body, the contract must derive and store one exact effect summary:

- relations/columns read;
- relations/rows locked and lock mode;
- relations/columns inserted, updated or deleted;
- functions called;
- explicit SQLSTATE/reason outcomes;
- return source; and
- principal/owner privilege required.

The effect summary must be mechanically rederived from the body program and
must equal the declared exact value. A widened read, DML effect, lock, call,
return or error surface fails even when the contract digest is resealed.

The effective-parent privilege matrix after the closed recovery delta is the
ceiling. The non-login schema owner receives exact `SELECT` only on the four
qualified application tables needed by the producer and fences; it receives no
application-table `INSERT`, `UPDATE` or `DELETE`. Existing route-owned product
locks remain held by the same top-level transaction, and the projection body
reselects and proves those rows without acquiring or inventing a product DML
privilege. The admission receiver gains the exact active binding read required
to record `observer_binding_revision`, plus its already accepted source,
generation, checkpoint, receipt and key reads and admission `INSERT`. No
runtime role gains direct product-table access. Migration-only trigger
installation authority is not runtime authority and must not survive as a
runtime grant. The producer can reach the owner-private alias bridge only
through `project_update_confirm_reschedule_v1`. Trigger functions are
owner-internal and receive no runtime execute grant.

## Entry-point semantic closure

The body programs must freeze at least these non-negotiable effects:

- **Producer projection:** rederive the exact producer binding including its
  one stream; reselect under the existing route-held transaction locks and
  prove the current top-level transaction's eligible `IN_PROGRESS` update-confirm
  claim, appointment tuple, audit and sole committed reschedule event; enforce
  the exact PostgreSQL-16 low-XID32 comparison and immutable transaction-start
  timestamp; create-or-reload one immutable bijective opaque alias; lock one
  practice/stream head; append one payload-free outbox row; advance the head;
  and return that row. No effect precedes complete command-context proof.
- **Admission:** compare retained admission/receipt through exact reads before
  source access, without acquiring an update-requiring row lock; make
  exact primary redelivery inert; append or return one bounded conflict
  sentinel for mismatch or digest reuse; reselect and authenticate source only
  for first primary/conflict membership; handle uniqueness races by reloading
  and comparing the winner, never `ON CONFLICT DO NOTHING`. The unique
  insertion/winner protocol, not broadened receiver privilege, serializes
  admission races.
- **Coordinator:** rederive binding; lock barrier, generation/checkpoint,
  current anchor, admission/receipt and dependent rows in the accepted order;
  make clean exact redelivery source-independent and inert; force conflict,
  demonstrated gap, predecessor/epoch, key or admission uncertainty to an
  atomic rebase; atomically write receipt where a PRIMARY exists, watermarks,
  one-way retirement, coalesced obligation, decision lifecycle, minimized audit
  and checkpoint; and return the closed effective-parent
  `durability_transition_result_v1`, which truthfully distinguishes receipt
  apply/replay from rebase/terminal apply/replay without fabricating a PRIMARY.
- **Registration/anchor/rotation/consumption:** keep lifecycle authority
  separate; establish the stream head when absent, exact checkpoint, frames,
  watermarks, initial key interval and baseline anchor; independently
  reverify before an anchor append; future-fence a generation-local rotation;
  and permit only one-way terminal generation transitions with a durably
  stored exact terminal reason. Exact rotation replay is detected before the
  new-effect anchor fence; a different replay fails.
- **Retention:** assert `SERIALIZABLE`, lock the shared registry barrier;
  derive the complete
  non-consumed-generation census, slowest checkpoint, pins, key overlap and
  policy grace in the database; return eligibility without caller authority;
  and permit deletion only from the payload-free source relation, only through
  the exact admitted position, only when execution is enabled and the same
  eligibility is rederived in the purge transaction. No cascade or product
  event/alias/admission/anchor/receipt/checkpoint/audit deletion is permitted.
  Eligibility uses its dedicated closed retention-reason vocabulary, not an
  observation-decision reason.

Registration accepts one typed `initial_key_interval`; its start must equal
the newly established checkpoint plus one. Recovery pins remain inert and
ungrantable in this descendant: their later create/release authority requires
a separately accepted lifecycle gate, while retention conservatively honours
any valid rows. No current entry point falsely claims to enforce pin mutation.

The body contract must preserve the exact retry boundary: `40001` and `40P01`
propagate to the caller for a complete-transaction retry outside the function;
no body retries internally. Unknown commit outcomes remain resolved by existing
idempotency or exact stored-receipt readback.

## Trigger semantic closure

Every trigger body must be total over its declared `TG_OP` set and reject an
unexpected operation. Immediate guards must reject immutable update/delete,
claim reversion/adoption and non-monotonic head changes before effect. Deferred
fences must rederive the complete bidirectional same-top-level-transaction
membership at commit and return `NULL` only after proof.

The all-`UPDATE` appointment fence must compute the obligation exclusively from
`OLD.start_time IS DISTINCT FROM NEW.start_time OR OLD.duration_minutes IS
DISTINCT FROM NEW.duration_minutes`. Temporal transitions require the exact
claim/audit/event/alias/head/outbox set; non-temporal transitions require the
complete absence of event/alias/head/outbox effects. Queued insert-delete
trigger events and the current-XID provenance checks must prevent erasure of a
required member.

Trigger bodies may not grant direct runtime execute, read product state outside
their exact parent invariant, mutate business truth, generate a replacement
ContextFrameSet or catch and downgrade an error.

The exact per-trigger applicability, row-image, shared-table escape/adoption,
check-in exclusion, alias-reuse, stream-head baseline and retention-delete
matrix in the normative recovery is binding. Every deferred fence is read-only,
lock-free, sibling-call-free and independently valid against final transaction
state; no fence relies on cross-table trigger firing order. For the exact
producer appointment, a second same-top-level-transaction update is rejected
by detecting current-XID provenance in `OLD`, so queued temporal and
non-temporal obligations cannot conflict.

## Failure contract

The child contract must define one exact closed failure registry. Every custom
SQLSTATE is five uppercase alphanumeric characters, is unique by semantic
failure family and is paired with a non-sensitive stable reason code. Failure
metadata may identify only contract reason and body; it must not include
practice, appointment, patient, actor, UUID, digest, credential, packet or row
values.

Standard retryable PostgreSQL SQLSTATEs remain unaltered. Constraint/uniqueness
failures may be translated only where the body must distinguish exact duplicate
from conflict by reloading the winner; all other unexpected database failures
propagate and roll back.

## Later renderer order

The child contract must freeze the only admissible later inert renderer order:

1. the mechanically derived effective-parent schema/types/relations,
   constraints/RLS and stream-scoped existing support helper;
2. the nine entry-point signatures plus mechanically lowered body programs;
3. the thirteen trigger-function signatures plus mechanically lowered body
   programs;
4. the thirteen parent trigger declarations;
5. `PUBLIC` revocation, exact effective-parent non-login/receiver grants,
   migration-only trigger installation and exact runtime execute grants; and
6. static catalogue and privilege assertions.

This tranche does not perform that lowering. It emits no `CREATE`, `ALTER`,
`DROP`, `GRANT`, `REVOKE`, `DO`, transaction or dollar-quoted SQL artifact.
DDL rehearsal remains blocked until this child contract passes independent
review.

## Authored-synthetic static/adversarial acceptance

Acceptance must mechanically prove:

1. exact parent hash/schema/body-boundary binding, byte-unchanged parent files,
   exact recovery delta and deterministic effective-parent derivation;
2. exactly nine entry-point and thirteen trigger bodies, with no overload or
   helper drift;
3. every parent signature, owner, invariant and trigger mapping is preserved
   except the closed typed coordinator result and stream-scoped helper changes
   explicitly authorized by the recovery delta;
4. every body program validates against the whole-contract child schema;
5. every instruction, expression, identifier, relation, column, function call,
   `TG_OP`, row image, return and SQLSTATE belongs to the exact allowlist;
6. the call graph is acyclic and contains no dynamic/generic execution path;
7. declared effects are exactly rederived from programs and stay within parent
   roles and privileges;
8. lock acquisition follows the accepted producer, admission, coordinator,
   lifecycle/rotation and retention orders;
9. each entry point covers success, exact redelivery/race where applicable and
   every fail-closed branch named above;
10. each trigger is total over its declared event set, returns the correct row
    image/null and cannot suppress or downgrade invariant failure;
11. producer and trigger programs preserve current-XID, temporal/non-temporal,
    insert-delete, rollback and sole-event/alias/outbox/head bijection semantics;
12. admission remains retained-evidence-first, source-independent on exact
    redelivery and bounded to primary plus conflict;
13. coordinator effects remain all-or-nothing and anchor-fenced;
14. rotation is generation-local and retention uses a complete serialized
    database-derived census with execution disabled by default;
15. renderer ordering is exact while renderer execution remains absent;
16. digest-resealed independent mutations reject a missing/swapped lock,
    dropped proof, wrong relation/column, widened read/DML/call, altered
    SQLSTATE/return, incomplete `TG_OP`, non-temporal publication, source read
    on redelivery, direct alias access, internal retry, dynamic/raw SQL,
    transaction control, DDL/grant text, product-event retention pin, cascade,
    filtered census, body omission, extra body, call cycle, unqualified
    application relation, `current_user` substitution, stream omission,
    alias-current-XID overreach, check-in capture, prior-event retention
    rejection, unauthorised outbox deletion, wrong `OLD`/`NEW` image,
    same-transaction second appointment update, order-dependent fence, missing
    initial key, fabricated receipt result or ambiguous retention reason; and
17. explicit Git pre/postflight proves that no application, migration, API,
    Diary, parent contract, database/runtime, provider/data, deployment or
    protected artifact changed.

Passing static architecture tests proves machine closure only. It does not
prove PostgreSQL grammar, executable DDL, actual transaction/trigger behavior,
database privileges, migration locks, performance or operational safety.

## Data, provider, cost and licence posture

- Data: repository-authored architecture metadata and opaque synthetic cases.
- Patient/product/protected/historical-PHI data: none.
- Provider/model/external retrieval: none.
- Database/source/network/browser contact: none.
- Cost: zero provider/cloud cost.
- Licence: no external content or corpus.

## Recovery and stop

A deterministic schema/test defect may receive one bounded correction. The
initial plan at `f1de5fbb903e304ca4923bb17cbee00e5f955bd7` invoked this
recovery before body authoring; it is evidence, not an implementation source.
Any conceptual defect in body completeness, privilege/effect closure, trigger
totality, current-XID/temporal fencing, admission conflict handling,
coordinator atomicity, anchor/key lifecycle, retention census or API
classification invokes Sol's recovery lease and a fresh candidate-independent
veto. No rejected body contract may be silently admitted.

## Claim boundary and next dependency

Passing this tranche will prove only an exact provider-free unmounted
machine-readable body architecture. It will not create, render, parse through
PostgreSQL, execute or validate SQL; create a function/trigger/grant/migration
or database object; contact a source/database/provider; process patient/product
data; wire runtime; add command authority; deploy or establish production
safety.

Only after independent acceptance may a separate provider-free unmounted inert
DDL rehearsal mechanically lower the exact parent signatures and child body
programs into repository-local SQL artifacts. Applied local migration,
database-backed execution, operational credentials and live source/product
access remain later separately bounded gates.

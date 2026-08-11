# Provider-free disposable PostgreSQL durability restart and unknown-commit recovery rehearsal plan

Date: 2026-08-11

Status: `frozen_for_provider_free_planning_review_runtime_closed`

Planning baseline HEAD:
`e690eefaf91115343b8fcbbecc7c3f5fe0b25193`

Accepted concurrency parent result:
`raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_pass`

Accepted concurrency runtime source:
`fed81847b4155d49cf997905e79cf31808ceb017`

Exact independently reviewed concurrency functional source:
`43f168f3d5d1f71ec0f9071c40fadf14b6107621`

Target result:
`raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_pass`

Evidence label:
`provider_free_disposable_postgresql_authored_synthetic_restart_unknown_commit_recovery`

## Authority and objective

CF-D2 is the next dependency-satisfied Context Fabric durability descendant
under Yuri's standing uninterrupted-development authority. It is not an AES
extension and opens no real product or operational source.

The tranche will test the exact accepted PostgreSQL 16 durability artifact
across four deliberately bounded process crashes and same-cluster restarts. It
must distinguish:

- a commit whose terminal result was observed;
- a rollback whose fixed terminal SQLSTATE was observed;
- a lost terminal result whose complete durable state proves commit; and
- a lost terminal result whose exact pre-transition state proves rollback.

Connection loss is evidence only that the caller lacks a terminal result. It
is never evidence of commit or rollback. An indeterminate outcome is resolved
only by a complete, independently queried post-restart durable packet. Partial,
contradictory or unresolved state fails the scenario and releases no success.

## Exact inherited boundary

The machine contract binds the accepted CF-D1 pass evidence, contract,
evidence schema, harness, closeout and Sol acceptance by exact SHA-256. It also
binds the unchanged 424-statement inert SQL artifact and render manifest.

The inherited database functions, roles, RLS policies, atomic transition
members, immutable receipts, checkpoints, lifecycle rows and independent
recovery anchors are the system under test. CF-D2 may not repair or replace the
SQL, relax a role, add a database function, interpret a server mismatch as a
pass or apply the artifact as an operational migration.

The accepted serial and concurrent evidence remains immutable. CF-D2 creates a
new contract, evidence schema and evidence path and never rewrites a prior
attempt or mutable historical alias.

## API Spine classification

This is internal provider-free database durability evidence. It adds no
GraphQL field, subscription or mutation and no REST/OpenAPI operation. It does
not call FastAPI, the Diary, an application route, product source, product
command or provider.

The authored-synthetic outbox, admission and receipt rows remain inert context
rehearsal data with `command_authority: false`. Events are signals, not current
truth or command evidence.

## Runtime containment and durability profile

One later implementation may use exactly one newly owned local disposable
`postgres:16-bookworm` container with:

- `--pull=never`, `--network=none`, no published port, bind mount, named volume,
  anonymous volume or later network join;
- one tmpfs shield at the image-declared default `PGDATA` volume path solely to
  prevent an implicit anonymous volume;
- the actual test cluster at a distinct fixed path in the owned container's
  writable layer, so it survives restart of that exact container and disappears
  when the container is removed;
- one fixed behavior database and local Unix-socket peer authentication only;
- `fsync=on`, `synchronous_commit=on`, `full_page_writes=on` and data checksums
  verified before each scenario and after each restart;
- no restart policy, savepoint, prepared transaction, two-phase commit,
  `pg_resetwal`, recovery target, WAL payload inspection, server-log inspection,
  replication, backup, host storage or external connection; and
- exact captured-container-ID crash, restart and cleanup operations only after
  name, nonce, image, network, port, mount, storage-path and current-state
  reverification.

Each scenario uses one exact `SIGKILL` of the captured container followed by a
start of that same ID. A graceful PostgreSQL stop, a new container or a fresh
cluster cannot substitute for crash/restart evidence. Startup must reach an
allowlisted ready state within 15 seconds. A crash count other than four or a
cluster identity change fails the whole artifact.

The final cleanup removes only the exact captured container ID after ownership
reverification and proves it absent plus zero containers with the exact
tranche label. It never removes an image, volume, network, unrelated container,
workspace path or database.

## Identity and transaction controls

Every product-shaped precondition remains fixed authored-synthetic fixture
work performed by the accepted owner-only fixture path. Every measured entry
point uses a fresh connection and exactly one `SET SESSION AUTHORIZATION`
before `BEGIN`:

- `context_producer` creates the fixed payload-free source positions;
- `context_observer` admits the fixed proofread packets;
- `context_coordinator` applies or replays a transition; and
- `context_lifecycle` registers a generation or appends an independently
  reverified anchor.

Participants receive no superuser, role membership, `SET ROLE` after begin,
inheritance, `BYPASSRLS`, direct Fabric DML, trigger-function execution or
operational credential. The recovery classifier uses only fixed owner-side
canonical relation snapshots; it cannot act as a participant or alter state.

All measured coordinator transactions are `SERIALIZABLE`. There is no
automatic retry. Fixed `statement_timeout` and idle-transaction ceilings apply.
The only injected rollback is the already accepted exact `P0001` outer abort.

## Client-observation boundary

The measured caller boundary is one one-shot client process. A terminal result
exists only when that process exits normally and the harness admits the exact
allowlisted result. Output fragments from a client that loses its database
process are neither parsed nor retained as terminal evidence.

For the committed indeterminate case, the fixed one-shot batch commits the
coordinator transaction and then enters a bounded server-side `pg_sleep` before
the one-shot process can return a terminal result to the harness. For the
rolled-back indeterminate case, the fixed batch stages the transition and
enters the same hold before issuing `COMMIT`. A separate fixed observer must
see exact `Timeout/PgSleep` before the container is killed. Timing alone is not
sufficient.

The cutpoint proves only that the required test topology was reached. The
recovery classifier is forbidden from using whether the hold was before or
after commit. Its only inputs are post-restart canonical receipt, checkpoint,
lifecycle, audit, watermark, frame, obligation and recovery-anchor facts.
`stdout`, `stderr`, raw errors, server logs, WAL, the schedule and connection
loss are forbidden decision inputs.

This is a one-shot caller-level unknown-result proof. It is deliberately not a
claim that the crash landed inside PostgreSQL's WAL commit or wire-protocol
acknowledgement instruction.

## Complete durable classification rule

`COMMITTED_RECOVERED` is admissible only when all atomic transition members are
present once and mutually consistent:

1. the exact immutable receipt and stored admission agree;
2. the checkpoint is at the exact position and lifecycle revision;
3. the decision lifecycle row and minimized audit reproduce their digests;
4. watermarks, one-way frame retirement and the coalesced obligation match;
5. the prior anchor remains exact and the new revision anchor is absent until
   lifecycle recovery; and
6. a fresh exact coordinator replay returns `RECEIPT_REPLAYED` without changing
   any canonical relation digest.

`ROLLED_BACK_RECOVERED` is admissible only when the entire post-restart state is
byte-equivalent at the canonical digest level to the pre-transition snapshot:
no receipt, decision lifecycle row, decision audit, checkpoint advance,
watermark advance, frame retirement or obligation residue may exist, and the
baseline anchor must still be exact. Only after this absence proof may one
controlled coordinator transaction apply the same stored admission.

Any mixed state, missing expected member, duplicate member, digest mismatch,
unexpected anchor or state that fits neither class is `recovery_unresolved` and
fails closed. The harness may not choose the more convenient class, accept
eventual convergence or retry until an expected answer appears.

## Frozen four-scenario population

### `CFD2-R01` — confirmed commit survives restart and resumes

A fresh observer generation receives fixed positions one and two. Position one
is admitted and applied under `SERIALIZABLE`; the client observes exact
`RECEIPT_APPLIED`, and lifecycle authority appends the independently verified
second recovery anchor at lifecycle revision one. The baseline anchor at
lifecycle revision zero is the first anchor. The complete snapshot is captured,
the container is killed, and the same cluster is restarted.

Post-restart readback must match the pre-crash snapshot exactly. A fresh
position-one call returns `RECEIPT_REPLAYED` without mutation. Position two then
applies once as the exact contiguous successor. This proves restart persistence
and anchored continuation for this fixed path only.

### `CFD2-R02` — confirmed rollback survives restart without residue

For a disjoint generation, the coordinator applies position one and then the
harness raises exact `P0001` before commit. The client observes that rollback.
Canonical readback must equal the pre-transition state before the container is
killed and again after restart.

Only after the exact zero-residue proof may one controlled transaction apply
position one, lifecycle authority append its second anchor at lifecycle revision
one, and one fresh
replay return `RECEIPT_REPLAYED` inertly. A receipt or partial effect surviving
the acknowledged rollback fails the whole artifact.

### `CFD2-R03` — lost terminal result resolved as committed

For a disjoint generation, the one-shot client applies and commits position one
then reaches the fixed post-commit server hold. The observer proves
`Timeout/PgSleep`; the exact container is killed, so the one-shot caller returns
only `CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT`.

After restart, the classifier must derive `COMMITTED_RECOVERED` solely from the
complete durable packet. Exact replay must be inert. Position two must fail
exact `CF303` while the lifecycle-revision-one recovery anchor is pending.
Lifecycle authority may append that anchor only by calling the accepted entry
point that reverifies the complete committed state. Position two may then apply
once.

### `CFD2-R04` — lost terminal result resolved as rolled back

For a disjoint generation, the one-shot client stages position one and reaches
the fixed pre-commit server hold. The observer proves `Timeout/PgSleep`; the
exact container is killed, so the caller again has no terminal result.

After restart, the classifier must derive `ROLLED_BACK_RECOVERED` solely from
the exact pre-transition state and zero-residue proof. Only then may one
controlled transaction apply position one, lifecycle authority append its
lifecycle-revision-one anchor and a fresh exact replay remain inert.

## Evidence minimization

The final whole-document evidence may retain only:

- scenario, observation, cutpoint and recovery-class labels;
- exact allowed result kinds, SQLSTATEs and stable reason codes;
- closed session-role/isolation/read-only classifications;
- closed container lifecycle states and bounded durations;
- exact relation counts, lifecycle revisions and canonical SHA-256 row-set
  digests over opaque authored-synthetic coordinates;
- exact image/container/cluster identity digests and containment facts; and
- exact cleanup disposition plus zero provider/product/external-operation
  counters.

It must not retain raw SQL, query text, client stdout/stderr fragments from an
indeterminate attempt, server logs, WAL content, backend PIDs, lock keys,
database URLs, credentials, environment values, timestamps as semantic
identity, names, patient/product values, prompts, model output or raw payloads.

## Planning, review and execution gates

1. Complete five-source rehydration and a fresh pre-planning Ariadne receipt.
2. Freeze this plan, design, threat delta, closed machine contract/schema and
   hostile planning tests at the exact task HEAD.
3. Pass whole-document schema validation, exact parent hashes, scenario order,
   classification completeness, containment, evidence, claim and closed-surface
   tests plus `git diff --check`.
4. Commit the planning packet by explicit paths only.
5. Obtain one fresh exact-HEAD Gemini 3.6 Flash/high read-only veto over the
   non-protected planning packet. The verifier may not start Docker or edit.
6. Only after that veto, implement the fixed harness, result evidence schema
   and hostile tests without altering the accepted inert SQL.
7. Pass the deterministic implementation gate and a second fresh exact-HEAD
   veto before Docker contact.
8. Execute the four scenarios once, in order, in one newly owned disposable
   container; admit one immutable evidence artifact as a whole document and
   prove exact cleanup.

A deterministic failure means no external review or Docker run. A verifier
finding or PostgreSQL mismatch is preserved and recovered only within the
frozen boundary. It cannot authorize a graceful-stop substitute, a fresh
cluster after crash, ambiguous partial acceptance, blind retry, weaker
durability setting, superuser participant, SQL mutation, network, provider or
operational source.

## Worker allocation

Sol owns planning, implementation, the shared stateful crash/restart sequence,
recovery, acceptance and task-branch publication. The work is tightly coupled
to one mutable disposable PostgreSQL lifecycle, so a DeepSeek implementation
packet would not save a meaningful cycle. No native subagent is assigned.

Gemini 3.6 Flash/high through fresh Antigravity projects owns only the two
risk-triggered read-only vetoes. It receives an exact allowlisted non-protected
worktree and no implementation, self-acceptance, integration, data, runtime,
deployment, production, release or protected-ref authority.

Every repository change is staged by explicit path only. All 494 existing
untracked files, including the five `docs/branding/` paths, remain preserved,
unstaged and outside tranche ownership.

## Stop and recovery

Stop before or during the single runtime attempt on parent/hash/catalogue
drift, wrong storage path, implicit volume, wrong durability setting, wrong
principal or isolation, missing cutpoint wait proof, unexpected client result,
unexpected SQLSTATE, partial or ambiguous state, anchor mismatch, retry,
cross-practice visibility, evidence leakage, cluster/container identity drift,
or cleanup ownership uncertainty.

Every attempted container is uniquely named and nonce-labelled. Cleanup may
remove only the captured ID after exact ownership and containment
reverification; otherwise stop as `cleanup_ownership_unverified` and preserve
the ID for inspection.

One bounded mechanical correction is permitted for a deterministic schema,
test, serialization or launcher defect. A semantic defect in commit
classification, atomic membership, anchor authority, restart identity,
durability setting or claim meaning invokes Sol's recovery lease and a fresh
exact-head veto. No failed evidence is rewritten or promoted.

## Claim boundary and next direction

Passing CF-D2 proves only the four fixed authored-synthetic PostgreSQL process
crash/same-cluster-restart outcomes. It proves confirmed commit, confirmed
rollback and two deliberately constructed no-terminal-result cases are
resolved by complete durable state, with pending-anchor fencing, exact replay,
controlled rollback recovery, least privilege and exact cleanup.

It does not prove a literal crash inside WAL commit or protocol acknowledgement,
hardware or filesystem power-loss durability, arbitrary crash points, repeated
restart safety, driver/pool retry behavior, operational availability, automatic
retry, load, performance, key rotation, retention/purge, migration operation,
long-lived persistence, application/API/Diary wiring, source/watcher access,
real/product/patient/clinical data, provider use, tools, commands, deployment,
production, release, Pages or protected-ref safety.

If CF-D2 passes, the next architecture-strengthening durability direction is a
separate provider-free disposable key-rotation and retention/purge rehearsal.
It must receive fresh five-source rehydration and its own narrow fail-closed
plan; CF-D2 grants none of that runtime scope.

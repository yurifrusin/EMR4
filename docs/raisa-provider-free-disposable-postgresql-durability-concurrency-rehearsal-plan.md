# Provider-free disposable PostgreSQL durability concurrency rehearsal plan

Date: 2026-08-11

Status: `frozen_for_provider_free_planning_review_runtime_closed`

Planning baseline HEAD:
`c72d712bcccbfb225d3c71ad3b633c33bec56d29`

Accepted serial parent result:
`raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_pass`

Accepted serial evidence source:
`f3383dc4099b4ee590014bea62dddb146f5d2a16`

Target result:
`raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_pass`

Evidence label:
`provider_free_disposable_postgresql_authored_synthetic_concurrency`

## Authority and objective

Yuri selected the recommended first post-AES programme descendant and directed
continued work under the standing uninterrupted-development authority. This is
not AES-C6. It is the narrowest database-durability successor to the accepted
serial Context Fabric behavior slice.

CF-D1 will prove whether the exact accepted Context Fabric PostgreSQL 16
functions remain fail closed when two fresh authored-synthetic database
sessions overlap on the same protected coordinate. The proof is limited to six
fixed races over generation registration, source-position allocation,
proofread admission and coordinator application. It must show exact winner,
loser/replay, row-count, digest, authority, transaction and cleanup results.

The existing inert DDL is the system under test. Planning and implementation
may not silently repair, replace or apply it as an operational migration. A
server mismatch is diagnosis evidence. Any material SQL correction would be a
separately sealed recovery descendant with new hashes and a fresh veto.

## API Spine classification

This is internal provider-free Context Fabric durability evidence. It adds no
GraphQL field, subscription or mutation and no REST/OpenAPI operation. It does
not call FastAPI, the Diary, an application route, a product command or a
provider. Fixture-shaped appointment, idempotency, audit and committed-event
rows reproduce only the already accepted synthetic transaction membership.

Events remain signals, not current truth or commands. Every resulting Fabric
row remains read-only context with `command_authority: false`.

## Exact inputs

The machine contract binds the current accepted serial pass evidence, serial
contract, evidence schema, harness, closeout, Sol acceptance, inert SQL and
render manifest by exact path and SHA-256. The accepted serial evidence remains
immutable and is read only for identity and claim inheritance. The mutable
historical evidence alias is neither opened as authority nor rewritten.

The exact SQL artifact remains PostgreSQL 16, 424 statements and SHA-256
`dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`.
No concurrent scenario may begin unless every bound parent byte, the installed
catalogue/privilege identity and the closed fixture catalogue match.

## Runtime and transaction boundary

One later implementation may use exactly one newly owned local disposable
`postgres:16-bookworm` container with:

- `--pull=never`, `--network=none`, no port, bind mount, named volume or later
  network join;
- one container-local tmpfs cluster and one fixed behavior database;
- local Unix-socket peer authentication only, no password, credential or trust
  host rule;
- exactly two scenario participant sessions plus bounded harness observation
  and readback sessions;
- a fresh connection and exactly one `SET SESSION AUTHORIZATION` before each
  participant transaction;
- fixed `statement_timeout`, `lock_timeout` and idle-transaction ceilings;
- no savepoint, nested transaction, role switch, participant retry, external
  call or caller-selected SQL; and
- exact captured-container-ID cleanup after name, nonce, image, network, port
  and mount reverification.

Each participant transaction contains only the exact entry-point call, a fixed
harness synchronization hold where required, and commit or the fixed injected
rollback. The hold is bounded and exists only to make overlap observable; no
application, provider or human work occurs while locks are held.

## Deterministic overlap proof

Timing alone is not acceptance evidence. Each pair uses fixed distinct
`application_name` labels. After participant A returns from the target function
but before its transaction ends, it enters one fixed bounded `pg_sleep` hold.
The harness must observe A at the exact `Timeout/PgSleep` state before starting
B. It then must observe B waiting on a PostgreSQL lock before A releases.

The repository evidence retains only the allowlisted state classification,
not backend PIDs, query text, server logs or lock keys. Failure to observe both
states within the fixed ceiling stops the scenario as
`concurrency_overlap_unproved`; it cannot be relabelled a pass.

Participant A is always the deterministically scheduled leader. Participant B
is the contender. No random winner claim is permitted. A participant receives
no automatic retry. Where a frozen race expects PostgreSQL `40001`, `CF004` or
the fixed `P0001`, a separate fresh post-race transaction may perform only the
exact replay named in the scenario.

## Frozen six-scenario population

### `CFD1-C01` — identical generation registration

Two `context_lifecycle` sessions submit the same closed generation
registration under `SERIALIZABLE`. A registers the generation and holds the
registry barrier before commit. B must be observed waiting, then terminate
with exact `40001` after A commits. One fresh exact replay returns the retained
generation without another barrier increment.

Readback must show exactly one generation, checkpoint, baseline anchor, initial
key interval and two current frames, one stream head at zero and one effective
registry increment. No partial loser rows or widened principal/binding are
permitted.

### `CFD1-C02` — distinct producers on one stream head

Two `context_producer` sessions run separate complete authored-synthetic
update-confirm projections for distinct appointments and commands under
`READ COMMITTED`. A allocates position one and holds the stream-head lock. B
must wait, then allocate position two after A commits.

Both transactions commit. Readback must show two and only two completed claims,
audits, events, immutable aliases and payload-free outbox rows, contiguous
positions `1,2`, no lost update and no duplicate application or Fabric member.
The identities remain distinct and no ordering is inferred from wall-clock
timestamps.

### `CFD1-C03` — identical proofread admission

Two `context_observer` sessions submit the exact same admitted packet for the
same registered generation and source position under `READ COMMITTED`. A
inserts the PRIMARY and holds it uncommitted. B must wait on the unique
coordinate, then return the same retained PRIMARY after A commits.

Both calls commit, but readback must show exactly one PRIMARY, zero CONFLICT,
one admission digest and no coordinator effect. Server-authored timestamps are
not semantic identity.

### `CFD1-C04` — divergent proofread admission

A submits the frozen primary packet and holds it uncommitted. B concurrently
submits one exact different packet for the same locator. Because B began before
the winner was visible, it must fail closed as exact `CF004` after waiting; it
must not guess or overwrite the winner. A fresh post-race submission of B's
same packet must append exactly one receiver-authored CONFLICT, and one further
exact replay must return that same conflict.

Readback must remain exactly one PRIMARY plus one CONFLICT, with the primary
unchanged and no third row or coordinator advance.

### `CFD1-C05` — identical coordinator application

Two `context_coordinator` sessions apply the same stored PRIMARY locator under
`SERIALIZABLE`. A creates the receipt and full selected transition effect, then
holds the locked coordinate before commit. B must wait and terminate exact
`40001` after A commits. One fresh exact replay must return the stored receipt
without source access or duplicate effect.

Readback must show one receipt, one checkpoint advance, the exact watermarks,
retired matching frames, one coalesced obligation, one lifecycle row and one
minimal audit. All counts and canonical digests remain stable across replay.

### `CFD1-C06` — coordinator rollback with waiting contender

A applies the stored PRIMARY under `SERIALIZABLE`, enters the fixed hold and
then raises the harness-owned exact `P0001` before commit. B starts while A
holds the coordinate and must be observed waiting. After A rolls back, B must
apply and commit the transition without a participant retry.

Readback must show exactly the single B-owned durable transition effect. No
partial A effect, second receipt, skipped checkpoint, duplicate obligation or
source mutation is permitted. One fresh exact replay remains inert.

## Authority, tenancy and provenance controls

All participants use the accepted least-privilege roles and exact alpha
practice/source/stream binding. The harness records `session_user`,
`current_user`, transaction isolation and read-only state through closed
markers. Direct Fabric DML, role membership, `SET ROLE`, `BYPASSRLS`, trigger
execution and cross-practice selectors remain denied exactly as in the parent.

The six races do not create an AES capability lease and do not import an AES
credential. Database authorization is rederived by the existing entry point
from `session_user`, the current practice binding and the closed locator.
Source membership, admission, receipt, checkpoint and lifecycle provenance are
recomputed by the accepted SQL and verified by canonical row digests.

The parent serial RLS/privilege packet and pass evidence are mandatory
preconditions. CF-D1 adds no beta binding or wider role. A concurrent result is
invalid if any unbound or beta-practice row becomes visible or changes.

## Evidence minimization

The final artifact may retain only:

- closed scenario and participant labels;
- expected/observed outcome class, exact SQLSTATE and stable reason;
- isolation/read-only state and allowlisted session-role labels;
- overlap observations as closed wait-state classes and bounded durations;
- exact per-relation counts, contiguous positions, lifecycle revisions and
  canonical SHA-256 row-set digests over opaque synthetic coordinates;
- exact image/container identity digests and containment facts; and
- exact cleanup disposition.

It must not retain raw SQL, query text, server logs, backend PIDs, stack traces,
unrestricted error text, database URLs, credentials, environment values,
patient/product values, names, prompts, model output or raw payloads.

## Planning, review and execution gates

1. Complete five-source rehydration and a fresh pre-planning Ariadne receipt.
2. Freeze this plan, design, threat delta, closed machine contract/schema and
   hostile planning tests at the exact task HEAD.
3. Pass whole-document schemas, parent hashes, scenario order/coverage,
   overlap, identity, effect, evidence, containment, closed-surface and hostile
   mutation tests, Ruff where applicable and `git diff --check`.
4. Commit the planning packet by explicit paths only.
5. Obtain one fresh exact-HEAD Gemini 3.6 Flash/high read-only veto over the
   non-protected packet. The verifier may not start Docker or edit files.
6. Only after that veto, implement the fixed-path harness, evidence schema and
   hostile tests without altering the accepted inert SQL.
7. Pass the deterministic implementation gate and a second fresh exact-HEAD
   veto before Docker contact.
8. Run the six scenarios once in one newly owned disposable container, write
   one immutable evidence artifact, validate it as a whole document, and prove
   exact cleanup.

A deterministic failure means no external review or Docker run. A verifier
finding or PostgreSQL mismatch is preserved and recovered only inside the
frozen boundary. It cannot authorize weaker isolation, broader SQLSTATEs,
superuser substitution, omitted lock observations, scenario deletion, parent
SQL mutation, another database, network access or a provider.

## Worker allocation

Sol owns planning, implementation, the shared stateful database sequence,
recovery, acceptance and task-branch publication. The work is tightly coupled
to one mutable disposable PostgreSQL instance, so a DeepSeek implementation
packet would not save a meaningful cycle. No native subagent is assigned.

Gemini 3.6 Flash/high through a fresh Antigravity project owns only the two
risk-triggered read-only vetoes. It receives an exact allowlisted non-protected
worktree and no implementation, self-acceptance, integration, data, runtime,
deployment, production, release or protected-ref authority.

Every repository change is staged by explicit task path only. The existing
494 untracked files, including `docs/branding/`, remain preserved, unstaged and
outside tranche ownership.

## Stop, cleanup and recovery

Stop before or during the single runtime attempt on parent/hash/catalogue
drift, wrong principal or isolation, unproved overlap, unexpected wait class,
unexpected SQLSTATE, deadlock, timeout, cross-practice visibility, duplicate
or partial effect, evidence leakage, containment mismatch or cleanup ownership
uncertainty.

Every attempted container is newly named and nonce-labelled. Cleanup may
remove only the captured ID after exact ownership and containment
reverification; otherwise it stops as `cleanup_ownership_unverified` and leaves
the ID for human inspection. No image, global container, volume, network,
workspace path or unrelated database may be removed.

A source defect may be diagnosed without changing accepted evidence. Any SQL
repair must be a separately hash-bound recovery artifact and fresh review; no
failed evidence is rewritten or promoted.

## Claim boundary and next tranche

Passing CF-D1 proves only the six fixed concurrent-session outcomes against the
exact accepted authored-synthetic PostgreSQL 16 durability schema, including
bounded lock overlap, monotone winner/loser accounting, replay, outer rollback,
least-privilege identity and exact cleanup.

It does not prove crash or server restart behavior, unknown commit, arbitrary
deadlock freedom, automatic retry policy, more than two participants, load or
performance, key rotation, retention/purge, migration operation, long-lived
persistence, application/API/Diary wiring, watcher/listener/source access,
real/product/patient/clinical data, provider use, tools, commands, deployment,
production, release, Pages or protected-ref safety.

In short, CF-D1 makes no crash/restart or unknown-commit claim.

If CF-D1 passes, the next dependency-satisfied planned direction is CF-D2:
provider-free disposable restart and unknown-commit recovery rehearsal. CF-D2
must receive a fresh five-source rehydration and its own narrow fail-closed plan
before execution.

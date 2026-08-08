# Provider-free disposable PostgreSQL durability behavior/transaction rehearsal plan

Date: 2026-08-08

Status: candidate pending deterministic plan gate and fresh exact-HEAD
independent veto; runtime remains closed

Parent result:
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`

Accepted parent runtime source HEAD:
`c3ca2515b9f2c4b20cb7230364de7417f48eab54`

Planning baseline HEAD:
`bc0120f574ff4a9fb34a5d463537542f906c5916`

Canonical inert SQL SHA-256:
`sha256:a33baca6f622835b62fc84c378f05a49c2936cf28925db6fb5fe4a4fb4d50a36`

## Objective

Freeze the first finite database-backed behavior proof for the accepted Raisa
Practice Context Fabric durability design. A later implementation may install
the exact already accepted SQL in one newly owned, local, network-isolated,
disposable PostgreSQL 16 container and use only closed authored-synthetic
fixtures. It will exercise one serial end-to-end thread from generation
registration through update-confirm projection, proofread admission and
coordinator application, together with exact trigger, RLS, replay, conflict
and rollback attacks.

The intended planning result is
`raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_pass`.
That result will authorize implementation of this exact rehearsal only. It is
not the runtime result and does not authorize a container before the plan,
threat delta, whole-document contract/schema, hostile tests and fresh
independent veto all pass.

## API Spine classification

This is internal async/context-durability evidence. It adds no GraphQL field,
subscription or mutation and no REST/OpenAPI operation. The existing signed
update-confirm command remains the future producer boundary, but the rehearsal
does not call an application route or mount the Fabric in FastAPI or the Diary.
The authored-synthetic `appointment_command_idempotency`, audit and committed-
event tuples are fixture-shaped transaction members only. They are not product
commands, receipts or authority.

Events remain signals that require fresh authorized reads; they never become
Diary truth. All Fabric outputs have `command_authority: false` by construction.

## Exact accepted inputs

The machine contract binds six parent surfaces:

1. the accepted parse/catalogue closeout and exact runtime source HEAD;
2. the exact 1,404,433 canonical LF-byte, 412-statement inert SQL artifact;
3. its exact render manifest;
4. the accepted structural migration/transaction contract;
5. the accepted function/trigger body contract; and
6. the accepted empty synthetic prerequisite-table contract.

Every value-bearing parent is SHA-256 bound in
`behavior-transaction-rehearsal-contract.json`. All six text-parent hashes use
canonical UTF-8/LF bytes: a checkout may receive only mechanical CRLF-to-LF
normalization, lone carriage returns are rejected, and every other byte must
remain exact. The later harness must refuse parent, path, source-HEAD, byte,
manifest, function, trigger, role, privilege or scenario drift before Docker
contact. The SQL path retains the accepted parse/catalogue artifact's exact
canonical byte and statement-count checks in addition to this common text-hash
rule.

## Planning gate and runtime separation

This tranche may write only the plan, design, threat-model delta, closed
contract/schema, deterministic plan tests and bounded review evidence. It may
not start Docker or PostgreSQL, render or alter SQL, create a database or role,
run an entry point or trigger, or generate behavior evidence.

Only after a fresh exact-HEAD veto accepts this packet may a later Sol-owned
implementation add the fixed-path harness, fixed scenario SQL/templates,
evidence schema, focused hostile tests and one runtime evidence artifact. That
implementation must itself pass deterministic preflight and a fresh exact-HEAD
veto before the first container run.

## Exact disposable runtime boundary

The future runtime inherits the accepted containment profile:

- exact already-local image `postgres:16-bookworm` and `--pull=never`;
- `--network=none`, no published/exposed host port and no later network join;
- no bind mount, named volume, workspace mount or Docker socket mount;
- one container-local tmpfs for database storage;
- exactly one owned container, one database and one serial scenario sequence;
- fixed CPU, memory, process, startup, command and total-run ceilings;
- no caller-selected executable, image, SQL, path, database, query, role,
  scenario, timeout, evidence path or cleanup target;
- argv-only process execution with `shell=False`;
- no `POSTGRES_HOST_AUTH_METHOD=trust`, role passwords or operational
  credentials; and
- all connections inside the owned container over its local Unix socket.

The harness may inspect only the exact image reference, closed container name
and captured container ID. It must not list global containers, images, networks
or volumes; pull, build, login, prune, start Docker Desktop or touch an object
it did not create and reverify.

The accepted parse/catalogue readiness rule remains binding: socket readiness
and the fixed authenticated PostgreSQL-major probe must both remain successful
for the exact stability interval, with bootstrap handoff resetting the
interval.

## Authored-synthetic fixture boundary

The four accepted prerequisite relation shapes remain the only `public.*`
application shapes. The behavior overlay may add only the minimum fixed
authored-synthetic keys needed to reproduce the already accepted one-command/
one-audit/one-event coupling and exact fixture-only application-table grants
to `context_producer`. It may not add product triggers, RLS, application logic,
patient columns or any new application relation. Parent Fabric SQL, roles,
grants, functions, triggers and policies remain byte-unchanged.

Every identifier, time, digest, generation, key interval, appointment,
command, audit and event coordinate is position-closed in the contract.
Appointments have only opaque synthetic UUIDs, practitioner/location UUIDs,
times and duration. There is no name, patient identifier, reason narrative,
clinical value or product-derived value. The reschedule event payload contains
only the exact already accepted allowlisted keys and synthetic values.

Bootstrap privilege is allowed only before scenarios to install the fixed
table shapes, accepted artifact, exact fixture grants, service bindings and
baseline synthetic appointments. It is never behavior evidence. Each behavior
scenario uses a fresh connection and exactly one `SET SESSION AUTHORIZATION`
before `BEGIN`, leaving a stable `session_user` for the entire transaction.
There is no in-transaction role switch, `SET ROLE`, second login, savepoint or
nested transaction.

The fixture grants change no Fabric direct privilege. No runtime role receives
Fabric-table DML, trigger-function execute, role membership, inheritance,
`BYPASSRLS`, schema `CREATE` or owner authority.

## Frozen twenty-scenario population

The contract position-closes exactly twenty ordered scenarios across all five
required categories:

| Category | Count | Exact scope |
|---|---:|---|
| Entry point | 6 | three isolated generation registrations; temporal projection; first primary admission; first coordinator apply; non-temporal inert update; missing-source admission rejection |
| Trigger | 4 | temporal member omission; insert-then-delete erasure; immutable alias mutation; same-transaction second appointment update |
| RLS/privilege | 3 | same-practice application reads; cross-practice locator denial; exact forbidden DML/execute/role matrix |
| Idempotency | 4 | exact primary admission replay; bounded primary-plus-conflict replay; coordinator receipt replay; committed command projection reinvocation |
| Rollback | 3 | fixed post-projection, post-admission and post-coordinator injected aborts |

### Positive serial thread

`BTR-E01` registers three isolated observer generations against one exact
practice/source/stream and establishes one stream head at position zero. The
registrations create exact checkpoints, baseline anchors, initial key
intervals and frame generations under the lifecycle principal.

`BTR-E02` uses a single read-committed top-level producer transaction. It
inserts the exact `IN_PROGRESS` update-confirm claim, updates one pre-existing
synthetic appointment's start time, inserts the matching audit and exact sole
committed reschedule event, invokes
`project_update_confirm_reschedule_v1`, then moves the same claim to
`completed`. Commit must leave exactly one immutable alias, stream position
one and one payload-free outbox row, with every application/Fabric member
sharing the required current-XID transaction provenance.

`BTR-E03` admits one exact proofread PRIMARY for position one under the observer
binding. Its source membership digest is read only from the exact same outbox
locator; no caller or external value may select it. `BTR-I01` repeats the exact
packet and must return the same primary without a second row.

`BTR-E04` applies that stored admission locator under the coordinator binding.
Commit must atomically create the exact receipt, checkpoint advance,
watermarks, matching frame retirement, coalesced pending obligation, decision
lifecycle and minimal audit. `BTR-I03` repeats the exact locator and must be
source-independent and inert: no count, checkpoint, digest or lifecycle change.

`BTR-E05` changes only an exact non-temporal appointment field on a distinct
synthetic appointment. It must commit with no reschedule event, alias, head,
outbox or checkpoint effect. This directly separates ordinary appointment
updates from temporal Context Fabric publication.

### Entry-point and idempotency negatives

`BTR-E06` submits a valid registered generation with a source position absent
from the exact outbox. It must fail with `F_ADMISSION_SOURCE` / SQLSTATE
`CF201`, leaving no primary or conflict.

`BTR-I02` first produces exact position two on the same stream, then admits a
primary for the isolated conflict generation, submits one different proofread
packet for that same locator and repeats the exact mismatch. The retained set
must remain exactly one PRIMARY plus one CONFLICT; the primary is immutable,
the conflict identity is stable and no third row or coordinator advance occurs.

`BTR-I04` reinvokes the producer projection for the already committed position-
one command in a new transaction. The old claim cannot satisfy current-XID and
transaction-start provenance, so exact `F_CLAIM` / `CF101` must roll back with
no new alias, outbox or consumed position.

### Trigger negatives

`BTR-T01` performs a temporal appointment update with a current claim and audit
but no committed event or projection. Deferred commit must fail exact
`F_TEMPORAL_BIJECTION` / `CF603`, restoring the appointment and leaving no
claim, audit or Fabric effect.

`BTR-T02` inserts and then deletes the required reschedule event before commit.
Queued trigger work must not permit member erasure; commit must fail `CF603`
and consume no position.

`BTR-T03` attempts to change the already committed opaque alias. The immediate
guard must fail exact `F_IMMUTABLE` / `CF601`; the row digest and all relation
counts remain unchanged.

`BTR-T04` updates the same appointment twice in one top-level transaction. The
second update must fail exact `F_SECOND_UPDATE` / `CF604`, rolling back the
first update and every related member.

### RLS and privilege negatives

`BTR-R01` uses `context_application_read` with only the alpha-practice binding
to read the three granted projection relations. Exact alpha rows are visible;
synthetic beta and unbound rows are invisible. The transaction is read-only.

`BTR-R02` uses the alpha observer identity with a beta-practice locator. The
binding rederivation finds no exact row and fails exact `F_CARDINALITY` /
`CF004`; no source or admission row crosses tenants.

`BTR-R03` runs every closed forbidden operation in a fresh connection so one
denial cannot hide another. Direct Fabric DML, trigger-function execute,
another role's entry point, `SET ROLE`, role inheritance and `BYPASSRLS` must
all fail or read back false. PostgreSQL privilege denials bind exact standard
SQLSTATE `42501`; every relation count and digest remains unchanged.

### Transaction rollback negatives

`BTR-B01`, `BTR-B02` and `BTR-B03` use fixed harness-owned `P0001` aborts after
the producer, admission and coordinator entry points return but before commit.
The connection then ends with the transaction aborted. A fresh privileged
allowlisted readback must prove respectively:

- no appointment/claim/audit/event/alias/head/outbox effect and no position
  consumption;
- no admission while the source row and checkpoint stay unchanged; and
- the precommitted primary remains while receipt, checkpoint, watermarks,
  frames, obligations, lifecycle and audit stay unchanged.

These cases prove outer-transaction rollback for the selected complete effect
sets. They do not claim an injection after every internal statement or unknown-
commit recovery.

## Scenario isolation and readback

All scenarios run serially in the one behavior database. Success cases use
closed isolated appointment, command, observer-generation and source-position
partitions. Expected-failure cases run in top-level transactions whose only
acceptable terminal state is rollback. No failed connection is reused.

Before and after each scenario, a fixed superuser readback script emits only:

- scenario ID, principal, `session_user`, `current_user`, isolation and
  read-only state;
- exact SQLSTATE and stable reason identifier for expected failures;
- allowlisted per-relation counts and canonical row digests over opaque
  coordinates; and
- expected head/checkpoint positions, lifecycle revisions and enum outcomes.

Raw SQL error text, server logs, payload bodies, credentials and unrestricted
rows are forbidden. A database value can never choose a later executable,
path, role, SQL template, scenario or cleanup target. The sole bounded internal
data flow is the same-locator outbox source-contract digest into the fixed
proofread packet.

## Cleanup and absence proof

Cleanup inherits the accepted exact-ID rule. In `finally`, the harness must
inspect the captured container ID and reverify exact ID, name, both ownership
labels and nonce, image identity, `NetworkMode=none`, zero port bindings and
zero bind/named-volume mounts. If any fact differs it must stop destructive
cleanup as `cleanup_ownership_unverified` and report the exact ID for human
inspection.

Only a reverified exact ID may be force-removed. Exact-ID post-inspection must
then return the documented absent condition. No image, volume, network,
workspace path, database outside the container or unrelated container may be
removed.

## Deterministic and hostile plan gate

Before independent review, repository tests must prove:

1. both JSON documents are whole-document schema-valid and reject added,
   missing, reordered or widened surfaces;
2. all six parent paths, source heads and hashes match the accepted files;
3. the scenario order and scenario-object order are identical, unique and
   exactly twenty;
4. category counts are exactly `6/4/3/4/3` and every required category is
   non-empty;
5. every failure scenario binds one exact SQLSTATE and applicable custom
   failure ID from the accepted body failure registry;
6. success, no-effect, replay, custom-failure, standard-denial and injected-
   rollback outcomes obey coherent null/non-null failure fields;
7. the fixed fixture identifiers are valid UUIDs, digests are exact
   `sha256:` values and no patient/name/free-text field exists;
8. runtime containment is exactly no-pull/no-network/no-port/no-mount/tmpfs/
   argv-only/exact-ID cleanup;
9. fixture grants cannot change Fabric direct privileges or runtime role
   ceilings;
10. hostile digest-resealed mutations to scenario count/order/category,
    principal, SQLSTATE, effect/readback, parent hash, runtime profile,
    identity method, direct grants, data ceiling, cleanup or closed surfaces
    fail; and
11. explicit Git checks prove no application, Alembic, API Spine, Diary,
    branding, provider, deployment or protected artifact changed.

A deterministic failure forbids external review and runtime.

### Pre-existing API Spine baseline observation

The broader planning regression packet reproduced one pre-existing failure at
the untouched planning baseline HEAD
`bc0120f574ff4a9fb34a5d463537542f906c5916` in the separate clean r72
worktree:
`test_idempotency_continuity_index_covers_openapi_command_paths`. The current
idempotency continuity index omits three already-tracked OpenAPI paths:
`/appointments/proposals/check-in/{appointment_id}`,
`/appointments/proposals/check-in/confirm` and
`/appointments/proposals/reception-one/compose`.

This planning candidate changes no API Spine file and does not claim to repair
that repository defect. The exact failing node is excluded from this tranche's
candidate pass count while the other tests in its module remain included. A
later separately scoped API Spine maintenance descendant must reconcile those
three paths; omission evidence must not be erased or misattributed to this
Context Fabric plan.

## Allowed artifacts

This planning tranche may add only:

- this plan, one design and one threat-model delta;
- the closed behavior/transaction contract and JSON Schema;
- one deterministic plan-test module; and
- bounded preflight, review and acceptance evidence.

No harness, SQL scenario template, runtime evidence, closeout, continuity
advance or handover acceptance is created until the planning veto passes.

## Data, provider, cost and licence posture

- Data: repository-authored metadata and closed opaque synthetic fixtures only.
- Patient, clinical, product-derived, protected and historical-PHI data: none.
- Provider/model runtime, external retrieval and browser/product traffic: none.
- Database: none during planning; later exactly one disposable local
  PostgreSQL 16 container under the frozen profile.
- Cost: zero provider/cloud/product/database cost.
- Licence: repository content and the already-local official PostgreSQL image
  only; no new corpus or dependency.

## Worker allocation

Sol owns planning because it freezes a material transaction/security boundary.
Sol will also own the later serial disposable-database implementation,
execution, recovery, cleanup and acceptance because the state is tightly
coupled and non-separable. No implementation worker is economical here.

A fresh Gemini 3.6 Flash/high Antigravity project may perform only the required
read-only exact-HEAD independent veto after deterministic checks pass. It may
receive only this repository-local plan/design/threat/contract/schema/test
packet. It may not start Docker, edit the candidate, access product/protected
data, accept its own work, push, move the baton or touch protected refs.

## Acceptance

The planning tranche passes only when:

1. the five-source Ariadne pre-planning receipt passes at the exact task HEAD;
2. API Spine classification and all closed command/product surfaces remain
   unchanged;
3. parent bytes, hashes, source heads and accepted claim limits are exact;
4. the twenty finite scenarios and `6/4/3/4/3` coverage are internally
   coherent and implementation-complete without runtime improvisation;
5. synthetic fixture identity, role, transaction and data ceilings are exact;
6. every success/failure/readback claim is no broader than the selected
   behavior;
7. containment, evidence minimization and exact-ID cleanup remain fail closed;
8. whole-document schemas, static tests, hostile mutations, Ruff where
   applicable and `git diff --check` pass;
9. the candidate branch contains only explicit-path intended files and
   `docs/branding/` plus every unrelated untracked path remains unstaged; and
10. one fresh exact-HEAD Gemini 3.6 Flash/high veto reports no P0-P2 finding,
    explicitly reconciles the exact test packet and leaves its bounded
    worktree unchanged.

A P3 editorial finding may be corrected mechanically and rechecked; any
finding that changes scenario meaning, principal separation, rollback scope,
tenant isolation, data ceiling or claim boundary requires a fresh candidate
and fresh independent veto.

## Recovery and stop

A deterministic plan/schema/test defect receives evidence-backed correction
under Sol ownership. A later PostgreSQL rejection is diagnosis evidence, not
authority to weaken a SQLSTATE, omit a scenario, use superuser as the tested
principal, modify the parent artifact, bypass RLS, add a provider, use an
operational database or install/pull software. Each repaired runtime attempt
must use a newly owned container and fresh exact-ID cleanup.

Pause for Yuri only if recovery exposes a genuinely non-inferable product,
privacy, licence, clinical or operational choice outside the accepted
sequence, or a human-only environment action becomes necessary. Plan repair,
test failure, reviewer correction or PostgreSQL behavior mismatch is not a
user gate.

At successful closeout Sol reports in lay terms what became possible, what
remains closed and any issue exposed/resolved, then immediately proceeds to
the next dependency-satisfied descendant under Yuri's standing uninterrupted-
development authority.

## Claim boundary and next dependency

Passing this planning tranche proves only that the exact first database-
behavior experiment is safely and completely specified. It proves no SQL
behavior and opens no runtime by itself.

If accepted, the next action is to implement the fixed-path provider-free
rehearsal harness, evidence schema and hostile tests, obtain a fresh exact-HEAD
implementation veto, then run the twenty scenarios once in a newly owned
disposable container. Concurrency, key rotation, retention execution,
unknown-commit recovery, applied Alembic migration, application/API/Diary
wiring, operational credentials/persistence, watcher/listener/source access,
patient/product data, providers, deployment, production, release, Pages and
protected-ref movement remain later closed gates.

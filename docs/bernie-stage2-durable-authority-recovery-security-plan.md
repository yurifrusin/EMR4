# Bernie Stage 2 Durable Authority, Recovery, and Security Plan

Date: 2026-07-19

Owner: GPT Sol / Extra High

Decision: `approved_scope_frozen_for_implementation`

## 1. Authority and outcome sought

Yuri explicitly approved this bounded Stage 2 scope on 2026-07-19. This plan
implements only the already accepted provider-free appointment-create vertical
in a local synthetic development environment.

Stage 2 succeeds only when a Bernie booking session and its staff-confirmed
appointment creation survive process restart, concurrent revision attempts,
same-key retries, and realistic transaction failure without cross-practice
access, duplicate writes, mutable audit history, or broken correlation.

The backend remains authoritative for identity, practice scope, availability,
conflicts, freshness, explicit confirmation, appointment writes, idempotency,
audit, and receipts. Bernie remains proposal-only. The sole Bernie mutation is
the existing REST confirmation command. GraphQL remains read-only.

## 2. Frozen scope

Authorized changes are limited to:

1. additive PostgreSQL schema and Alembic migration work for durable Bernie
   session/event state;
2. transactional event revision and event-idempotency enforcement;
3. atomic appointment-create command idempotency under concurrency and retry;
4. complete command, appointment, audit, session, and receipt correlation for
   the existing staff-confirmed create vertical;
5. database-enforced append-only appointment audit evidence;
6. same-practice route authorization and PostgreSQL RLS policies/tests on the
   Stage 2 vertical tables;
7. restart, concurrency, rollback, post-commit replay, retention, and cleanup
   evidence;
8. JWT/practice-claim and persisted-field protection review with only bounded
   corrections needed by this vertical; and
9. the focused threat-model delta in
   `docs/security/bernie-stage2-threat-model-delta.md`.

No additional appointment action, GraphQL mutation, provider adapter, provider
call, PII path, deployment surface, production role, release action, general
platform migration, memory/RAG surface, corpus, or protected evidence is in
scope.

## 3. Source inventory and pre-change evidence

The plan binds to:

- `AGENTS.md` and all 38 documents in its pre-Stage-2 Current Baton;
- `docs/bernie-current-strategic-transition-review.md`;
- `docs/bernie-stage1-provider-free-supervised-booking-acceptance-plan.md`;
- `orchestration/agent_inbox/codex/bernie-stage1-tranche-d-extra-high-sol-acceptance.md`;
- the API Spine ADR, programme, release gates, OpenAPI command contract,
  read-only GraphQL contract, permission matrix, idempotency continuity, and
  audit-correlation continuity sources;
- `app/services/bernie/session.py` and `session_store.py`;
- the session, confirmation, idempotency, audit, authentication, database, and
  Alembic implementation named by this plan; and
- the fresh rehydration and pre-plan receipts under
  `orchestration/agent_inbox/codex/`.

Fresh readback established:

- all five protected Git refs were clean and aligned at
  `8cadc64c56d014a7f3fbd70d82ac5c041e63fed8`;
- the Alembic head and local development database were both
  `l1m2n3o4p5q6`;
- the session implementation was process-local;
- appointments, appointment audit, and appointment idempotency had no RLS;
- four existing completed appointment-create command rows each had one
  matching create audit but zero direct `audit_log_id` links; and
- the exact focused pre-change population passed 73 tests serially.

A broad local filename inventory exposed protected fixture/support path names
only. No protected file was opened, hashed, content-searched, run, or used.
The metadata-only incident was contained immediately; every subsequent source
read and test selection is explicit and protected-safe.

## 4. Non-negotiable invariants

1. No proposal, interpretation, slot search, or selection creates an
   appointment.
2. A human staff principal must explicitly confirm through the existing REST
   command before one appointment can be created.
3. One confirmation transaction owns the session confirmation transition,
   appointment, audit, completed idempotency result, and stored receipt.
4. A rollback before commit leaves none of those new effects durable.
5. A retry after commit returns the stored response and never creates a second
   appointment, audit, confirmation outcome, or command result.
6. Session revision changes serialize through a row lock; concurrent requests
   based on one revision cannot both advance it.
7. Session events store bounded structured evidence only. Raw instructions,
   transcripts, names, credentials, raw idempotency keys, and provider content
   are forbidden.
8. Practice scope is enforced in route queries and independently by RLS under a
   non-bypass database role.
9. Appointment audit rows cannot be updated or deleted by ordinary SQL, even
   through the table owner path used by the local development database.
10. GraphQL remains read-only and async integration remains observational.

## 5. Additive data design

### 5.1 `bernie_booking_sessions`

The durable session row stores the current semantic snapshot:

- opaque `session_id` primary key;
- `practice_id`, `staff_user_id`, and `surface_id` ownership;
- state, revision, immutable request reference date, turn count, and last event;
- structured patient/practitioner ids and confidence bands;
- bounded candidate/proposal freshness coordinates;
- stale reason, active-surface marker, completion time, expiry time, and stored
  UTC creation/update timestamps.

Database checks keep revision and turn count non-negative and state values in
the existing statechart. A partial unique index permits one latest active
session per practice, staff user, and Diary surface. Owner/surface lookup,
practice expiry, patient, and practitioner fields are indexed.

### 5.2 `bernie_session_events`

Each accepted transition appends one event row containing:

- a UUID row id plus the existing opaque event id;
- practice and session ownership;
- event type, resulting session revision, turn index, occurrence timestamp, and
  expected revision;
- an HMAC/SHA-256 identity hash when an idempotency key is supplied;
- a SHA-256 canonical event-payload hash; and
- the bounded structured JSON event payload.

Unique constraints cover session/event id, session/result revision, and a
non-null session/idempotency hash. The raw key is never persisted. Events
cascade only when their retained session is purged.

### 5.3 Command/audit/session correlation

The existing appointment command idempotency UUID is the confirmation
correlation id.

- `appointment_command_idempotency.audit_log_id` becomes populated for every
  completed appointment-create confirmed write;
- an additive `bernie_session_id` associates bound Bernie confirmations while
  remaining null for the ordinary staff-create alias;
- `appointment_audit_log.command_id` reciprocally identifies the command;
- `appointment_audit_log.bernie_session_id` identifies a bound session while
  it is retained; and
- the successful v1 receipt gains optional `correlation_id`, `audit_event_id`,
  and `session_id` fields derived only from committed server records.

The migration deterministically backfills the four existing local synthetic
create commands from their same-practice target appointment's create audit,
then validates a completed-create correlation check. Reciprocal command/audit
links are one-to-one. Audit and command rows retain the opaque session id as a
correlation coordinate without a foreign key, so purging session detail neither
updates immutable audit evidence nor loses the minimal correlation chain.

Composite `(practice_id, id)` foreign keys additionally bind events to their
own practice's session and bind commands/audits to their own practice's
appointment and reciprocal correlation row. RLS therefore cannot be bypassed
by placing a foreign practice's opaque id inside an otherwise same-practice
row.

### 5.4 Append-only audit

RLS supplies only `SELECT` and `INSERT` policy paths for appointment audit.
A PostgreSQL trigger independently rejects `UPDATE` and `DELETE`. The trigger
is created after migration backfill so historical correlation can be repaired
once without granting future mutability.

## 6. Transaction and recovery semantics

### 6.1 Session transitions

Every session append locks the owned session row before checking idempotency,
expected revision, and the existing static transition table. The transaction
appends the event and updates the snapshot together. Two concurrent requests
from one revision yield exactly one accepted transition; the loser returns a
typed stale-revision response.

New/active-session creation serializes on the owning staff row before replacing
the active surface pointer. A new process or SQLAlchemy session reconstructs
the exact retained snapshot and ordered event tail from PostgreSQL.

### 6.2 Confirmation idempotency

Command claims use PostgreSQL `INSERT ... ON CONFLICT DO NOTHING`, then lock the
single ledger row. This removes the current check-then-insert race. Lock order is
always command ledger, then Bernie session, then appointment/audit writes.

On success, one transaction performs:

1. command claim/lock;
2. current proposal, identity, freshness, and conflict revalidation;
3. `confirm_submitted` session transition for a bound session;
4. one appointment insert;
5. one correlated append-only audit insert;
6. one correlated `confirmation_outcome` transition;
7. completed idempotency response and receipt storage; and
8. commit.

Deterministic blocks before confirmation roll back the provisional claim. A
post-transition revalidation block removes the uncommitted provisional claim,
records the bound blocked outcome transactionally, and commits no appointment
or audit. Unexpected failure rolls back the whole transaction.

## 7. Practice isolation and authentication

The request authentication dependency must reject a signed token whose
practice claim differs from the current database user's practice. It sets a
transaction-local PostgreSQL practice context from the database user, never
from unchecked request input.

The migration enables and forces RLS on:

- `bernie_booking_sessions`;
- `bernie_session_events`;
- `appointments`;
- `appointment_audit_log`; and
- `appointment_command_idempotency`.

Policies compare each row's `practice_id` with the transaction-local practice
context. Missing context fails closed. Because the local connection owner is a
PostgreSQL superuser, acceptance also creates an isolated temporary non-login,
non-bypass role in the disposable migration database and proves direct reads
and writes cannot cross practices. The tranche does not create or provision a
production runtime role; production remains blocked.

Route-level same-practice checks remain mandatory even with RLS.

## 8. Field protection, JWT, and retention

JWT remains fixed to reviewed HS256 PyJWT verification, with the existing
non-development insecure-secret startup rejection. Stage 2 adds practice-claim
consistency and retains database role/authorization as the source of current
permissions.

Persisted session payloads are size-bounded and key-screened. Raw appointment
instructions, transcripts, patient labels/names, debug content, tokens,
secrets, and raw idempotency keys are rejected. Structured synthetic UUIDs and
freshness identifiers are permitted. No field encryption claim is made: this
Stage 2 authorization excludes PII and production, and a fresh production
field-encryption decision remains required.

Retention is frozen as follows:

- incomplete sessions receive a sliding 24-hour recovery expiry from their
  latest accepted transition;
- completed sessions receive 30 days from terminal completion;
- purging an expired session also purges its event detail;
- appointments, append-only audit, completed command idempotency/receipt, and
  their minimal mutual correlation remain for the life of the development
  database; and
- no production retention claim or scheduler/deployment work is authorized.

The cleanup service is explicit, batch-bounded, lock-safe, and directly tested.

## 9. Focused threat model

The Stage 2 delta treats the following as primary threats:

- duplicate appointment creation through concurrent same-key claims;
- lost or contradictory semantic state through concurrent revisions or restart;
- cross-practice session, appointment, command-response, or audit access;
- a crash leaving session confirmation without its appointment/audit chain, or
  an appointment without its completed command result;
- audit deletion/update or command/audit correlation drift;
- raw instruction, idempotency-key, secret, or provider-content persistence;
- stale token practice claims setting the wrong database tenant context; and
- expired session detail accumulating beyond the approved window.

The exact controls, residuals, and verification map are frozen in the focused
delta document. Protected evidence, historical material, provider execution,
production roles, real PII, and deployment are not threat-model inputs here.

## 10. Implementation phases

### Phase A — schema and migration

Add the two durable tables, correlation columns/checks/indexes, deterministic
local synthetic backfill, audit immutability trigger, and five RLS policy sets.
Prove upgrade, downgrade, and fresh upgrade on a disposable database. Never run
the destructive downgrade against the preserved development database.

### Phase B — durable store and route wiring

Add a PostgreSQL store beside the pure in-memory unit-test reference, wire all
runtime session routes/outcomes to the durable store, preserve the statechart,
and commit session-only routes explicitly. There is no runtime in-memory
fallback.

### Phase C — atomic confirmation and correlation

Replace check-then-insert command claim, bind the session, appointment, audit,
ledger, and receipt in one transaction, and preserve exact replay behavior.

### Phase D — security, retention, and recovery evidence

Enforce practice-claim consistency, set transaction-local practice context,
exercise restricted-role RLS and append-only triggers, prove cleanup, and run
restart/concurrency/failure tests.

### Phase E — Extra High acceptance and protected integration

Rehydrate, reproduce every gate serially, review the migration/threat delta,
inspect the exact diff, and integrate only through the ordinary protected PR
workflow. No worker or reviewer receives acceptance or integration authority.

## 11. Acceptance gates

| Gate | Requirement |
|---|---|
| G1 Authority | Fresh five-source receipt passes; approved scope and protected boundaries reproduce |
| G2 Migration | Disposable database passes upgrade, downgrade, and upgrade; preserved database upgrades additively with four historical create links backfilled |
| G3 Restart | A new SQLAlchemy session/process-local store instance recovers the same retained session and ordered events |
| G4 Revision concurrency | Two independent transactions using one expected revision yield one accepted transition and one typed stale result |
| G5 Same-key concurrency | Two independent confirmation transactions yield one appointment, one audit, one completed ledger, one confirmation outcome, and one stored response |
| G6 Pre-commit failure | Injected failure before commit leaves no partial appointment/audit/ledger/session-confirmation effects and a clean retry succeeds once |
| G7 Post-commit retry | A fresh database session returns the stored receipt with no second mutation or event |
| G8 Correlation | Command target, audit link, reciprocal audit command id, retained session link, and receipt ids agree exactly |
| G9 Practice isolation | Cross-practice HTTP access fails and restricted-role RLS hides/rejects foreign rows even when query predicates are omitted |
| G10 Audit immutability | Direct audit `UPDATE` and `DELETE` fail while insert/read remain practice-scoped |
| G11 Retention | Incomplete 24-hour and completed 30-day expiries reproduce; bounded purge removes only expired session/event detail |
| G12 Field/JWT protection | Raw/oversized payload and raw-key storage are absent; mismatched JWT practice claim fails closed; fixed-algorithm tests pass |
| G13 API Spine | REST remains the sole mutation command; GraphQL remains read-only; no async/provider bypass exists |
| G14 Regression/security | Explicit focused and complete Stage 1-compatible regression populations pass serially; Bandit/security contracts show no new accepted finding |
| G15 Scope | No provider, protected, historical, PII, production, deployment, release, additional action, or broad migration surface changed |

Any gate failure returns `revision_required`. There is no Stage 2 override.

## 12. Worker mix and evidence handling

Sol owns planning, migration, implementation, database execution, review,
recovery, acceptance, and protected integration. The work is serial, stateful,
and tightly coupled to one disposable PostgreSQL lifecycle; an external worker
packet would not save a meaningful implementation/test cycle. No provider lane
is reopened and no native subagent is assigned.

All pytest processes that load `tests/conftest.py` run serially. Browser work is
not required unless a route or receipt change creates a visible regression; if
used, it must follow the existing exact protected-safe allowlist and evidence
labels.

Durable closeout must record migration revision, exact test populations,
transaction/RLS/retention evidence, hashes where required, Git refs, PR/check
result, the contained metadata-only protected-path incident, unresolved
production boundaries, and the next user decision.

## 13. Closed gates after a pass

Even a complete Stage 2 pass does not authorize Stage 3, receptionist
participants, PII, production, provider calls, cloud changes, deployment,
release, new appointment actions, GraphQL mutations, external corpora,
historical diary expansion, protected evidence, autonomous confirmation, or a
production retention/encryption/runtime-role design. Each remains a fresh Yuri
decision.

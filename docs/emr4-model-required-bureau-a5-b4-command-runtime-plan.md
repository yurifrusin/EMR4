# EMR4 Model-Required Bureaus — Paired A5.1/B4.1 Command Runtime Plan

Date: 2026-08-05
Status: revision 3 candidate for independent architecture veto before implementation
Parent authority: `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
API authority: `orchestration/api_spine_adr.md`

## 1. Exact result sought

This descendant implements two provider-free, backend-owned and human-confirmed
command paths without joining their domain authority:

1. **A5.1 Rayleen check-in** adds a dedicated command operation built from the
   existing appointment status primitives for the exact
   `Booked|Confirmed -> Arrived` transition, with an optional compatible active
   waiting area. It uses a server-minted expiring signed token whose hash is
   durably consumed once, a dedicated idempotency namespace, row locking, exact
   current-state revalidation, one immutable appointment audit row, one
   patient-free committed check-in event and a bounded patient-free readback.
2. **B4.1 Davida default location** mounts the already designed single-purpose
   practitioner default-location proposal/attestation/confirm family. Davida is
   proposal provenance only. Only a currently authenticated human `Admin`
   (runtime mapping of `practice_manager`) or `PracticeOwner` (runtime mapping
   of `practice_owner`) may attest or confirm. One transaction updates one
   practitioner aggregate, increments its version, consumes one server-held
   confirmation evidence record, appends one immutable audit row and one
   transactional outbox row, and completes one durable idempotency receipt.

Neither path grants authority to Rayleen, Davida, a model, a provider response,
GraphQL, an event consumer or a client-supplied role assertion. Both paths use
the ordinary authenticated EMR4 staff user as the sole human actor and practice
authority source.

## 2. Closed boundaries

The descendant is local, provider-free and exercised only with authored
synthetic fixtures. It must not:

- call Gemini, Vertex or any other provider as product runtime;
- admit patient, clinical, participant, protected, production or
  product-derived evidence into model prompts or acceptance artifacts;
- add GraphQL mutations, autonomous action, model-to-database writes, external
  event transport, a publisher/worker, patient kiosk behavior, voice, clinical
  reasoning or any second administrative command family;
- mount the A4 Rayleen read token as command authority or convert a read
  capability into a write capability;
- alter deployment, release, Pages, production, protected refs or protected
  evidence;
- touch or stage `docs/branding/` or dispose of the preserved pre-push
  receipt/state files.

The existing raw appointment status route remains a compatibility surface and
is not evidence for A5.1. This descendant does not widen its authority.

## 3. Shared authority seam, separate domain runtimes

The lanes share only these invariants:

- REST/OpenAPI owns commands; GraphQL remains read-only.
- A proposal is non-authoritative and changes no product truth.
- The authenticated server session supplies practice, actor and current role.
- Client practice/actor/role values, where present, are exact-match assertions
  only and reject before resource disclosure on mismatch.
- A visible human-confirmation request is necessary but never sufficient: the
  backend freshly reauthorizes, locks and revalidates current truth.
- Every committed command has durable same-key/same-fingerprint replay,
  same-key/different-fingerprint conflict and no second effect.
- Truth, audit, outbox/event and idempotency completion are one transaction.
- Events describe committed truth and never confer command authority.

There is deliberately no generic cross-domain command executor, universal
payload, agent action grammar or shared business-aggregate table in this
descendant. Domain services own their schemas, failure codes and persistence.

## 4. A5.1 Rayleen check-in contract

### 4.1 Dedicated operation, shared Diary truth

Add two routes to the existing appointment REST router:

- `POST /api/v1/appointments/proposals/check-in/{appointment_id}`
- `POST /api/v1/appointments/proposals/check-in/confirm`

The routes reuse the authoritative appointment/waiting-area models and internal
status/audit/idempotency primitives, but use closed A5-specific schemas and
operation id `confirmAppointmentCheckInProposal`. This avoids changing the
generic status-confirm token semantics or admitting arbitrary status changes,
GP/Nurse roles and patient-bearing `AppointmentOut` into A5 evidence.

The initial path is default-off and admitted only for explicitly configured
authored-synthetic practice ids. The confirmer is exactly a current
`Receptionist`. `Admin`, `PracticeOwner`, GP and Nurse remain outside this
initial A5.1 route. Rayleen may supply bounded proposal provenance; the current
authenticated receptionist remains the only actor and confirmer. The route is
not a private Rayleen action grammar: it invokes the one backend-owned Diary
check-in command.

### 4.2 Exact check-in admission

The A5.1 committed-event branch applies only when all of these hold:

- current status is `Booked` or `Confirmed`;
- requested status is exactly `Arrived`;
- the proposal and server-minted evidence bind the same appointment, practice,
  authenticated receptionist, current status, current waiting area, target
  status, target waiting area, evidence nonce/expiry and freshness identifier;
- an optional target waiting area is active, belongs to the same practice and
  has the same non-null location as the appointment; an appointment without a
  resolved location cannot be assigned a waiting area through A5.1;
- `confirmed=true`, the default-off practice gate is open for the exact
  authored-synthetic practice and the dedicated Receptionist dependency admits
  the current human user;
- the exact appointment row is locked before the final state/evidence check.

The proposal changes no database state. Its HMAC-signed opaque evidence contains
a cryptographically random nonce, exact purpose, issued-at and bounded expiry;
the client cannot mint or alter it. Confirmation hashes that evidence and
records the hash on the dedicated durable command claim under a unique partial
constraint on `(practice_id, operation_id, confirmation_evidence_hash)`. The
token is one opaque patient-free base64url value; client-visible structured
claims cannot be submitted as a substitute. Same-key exact replay is resolved
from the stored receipt before evidence consumption. A first-use claim uses a
conflict-aware insert/savepoint so the losing concurrent transaction is
deterministically classified rather than leaking a database integrity error.
Any different-key reuse of the same evidence hash returns
`confirmation_replay_rejected`, including after appointment state is later
restored. Other existing status confirmations keep their present behavior and
produce no check-in event. `Arrived -> Arrived`, terminal-to-arrived, stale,
expired, tampered, wrong-purpose, wrong-actor, wrong-practice, cross-practice,
inactive/incompatible-area and role/session mismatch paths produce no truth,
audit, idempotency completion, evidence consumption or event effect.

The optional `waiting_area_id` means assignment when a UUID is supplied and no
waiting-area change when omitted or null; A5.1 cannot remove or move an already
assigned waiting area. Any existing area is also revalidated as active,
same-practice and location-compatible before it is preserved. Waiting-area move
or removal remains a later separately frozen A5 descendant.

### 4.3 Atomic unit and event

Within the dedicated check-in transaction, using the existing durable
appointment-command primitives, A5.1 must:

1. return an exact same-key/same-fingerprint completed receipt if present;
2. claim the A5-scoped idempotency key, canonical request fingerprint and
   unique signed-evidence hash;
3. lock and revalidate the exact practice-scoped appointment;
4. verify the A5 evidence purpose, signature, nonce, expiry and exact freshness;
5. update status to `Arrived` and apply the explicitly supplied waiting area;
6. append exactly one `AppointmentAuditLog` row bound to the command id;
7. append exactly one `DiaryCommittedEvent` with:
   - event type `diary.appointment_checked_in`;
   - schema version `diary.appointment_checked_in.v1`;
   - exact allowlisted patient-free payload fields
     `appointment_id`, `practitioner_id`, `location_id`, `status_before`,
     `status_after`, `waiting_area_id_before`, `waiting_area_id_after`,
     `reason_codes`;
   - reason codes exactly `["appointment_checked_in"]`;
8. complete the idempotency receipt with appointment, evidence and audit
   correlation;
9. commit once and return a freshly reloaded bounded receipt containing only
   appointment id, resulting status, resulting waiting-area id, audit id, event
   id, command id and commit time.

The committed-event table and schema are extended by an exact conditional
allowlist for the second event family; the existing reschedule event contract
must remain byte-for-byte equivalent in behavior. The existing reschedule feed
must filter `event_type = diary.appointment_rescheduled` during both cursor
validation and row selection so an interleaved check-in row cannot be parsed as
a reschedule payload or corrupt cursor semantics. No check-in consumer,
external publisher or worker is added.

### 4.4 A5.1 persistence and declarative contracts

The sequential descendant migration must deliberately add nullable
`confirmation_evidence_hash` and `confirmation_evidence_consumed_at` columns to
`appointment_command_idempotency`. Operation
`confirmAppointmentCheckInProposal` requires both values; other existing
operations preserve null. A unique partial index over
`(practice_id, operation_id, confirmation_evidence_hash)` where the hash is
non-null prevents the same evidence from being committed by two command rows.
A completed confirmed check-in additionally requires target appointment and
audit correlation. The migration must also replace, by exact name, all three
existing `diary_committed_events` constraints that otherwise admit only
reschedule rows:

- `ck_diary_committed_events_type`;
- `ck_diary_committed_events_schema`; and
- `ck_diary_committed_events_payload_allowlist`.

The replacements are conditional on the exact event type and require the exact
matching schema/payload for either reschedule or check-in. The existing source,
evidence-mode, revision, expiry and correlation constraints remain unchanged.
The migration upgrade and downgrade must each restore one valid Alembic head.

Update the declarative appointment OpenAPI and async-event manifests with only
the dedicated check-in proposal/confirm family and the patient-free checked-in
event. YAML remains documentation/manifest policy and does not confer runtime
authority.

## 5. B4.1 Davida default-location contract

### 5.1 Routes

Mount one practice-administration router under `/api/v1`:

- `POST /practice-administration/practitioners/default-location/proposals`
  recomputes a signed, self-contained, maximum-120-second proposal from current
  practice truth and writes no database row.
- `POST /practice-administration/practitioners/default-location/proposals/{proposal_id}/confirmation-evidence`
  records a current human attestation and returns only an opaque short-lived
  server-held one-use reference. It changes no practitioner truth.
- `POST /practice-administration/practitioners/default-location/proposals/{proposal_id}/confirm`
  consumes the evidence and commits the single administrative command.

All three routes are default-off and admitted only when both the exact B4.1
feature flag is enabled and the authenticated practice is in a separate
authored-synthetic practice allowlist. Gate rejection occurs before practitioner
or location lookup. This descendant proves local synthetic command semantics;
it does not open the route for ordinary, product or production practices.

The explicit attestation route closes the historical contract gap between a
read-only proposal and a confirmation command that must carry pre-existing
server-held evidence. It does not authorize the domain mutation; the later
confirm transaction must still reauthorize and revalidate everything.

### 5.2 Proposal

The backend authenticates and authorizes before exact resource disclosure,
loads one active same-practice practitioner and one active same-practice
location, rejects no-op/stale version, computes the current before-state hash,
and returns a deterministic signed opaque proposal. The existing Davida dry-run
proposal hash/context revision/expiry may be preserved as non-authoritative
provenance, but never decides or widens the command. The signed proposal binds:

- practice, actor and runtime role;
- practitioner and before default location;
- requested active default location;
- expected aggregate version and before-state hash;
- dry-run provenance hashes;
- correlation id, generated time and expiry.

### 5.3 Human attestation evidence

Only current `Admin` or `PracticeOwner` users may request evidence. The backend
verifies the proposal signature, proposal/path/hash/body equality, practice,
actor, role, expiry and current resource state before inserting evidence. The
stored row binds the exact proposal hash and canonical confirmation payload
hash. The client receives only a random opaque reference; it cannot construct a
valid evidence record from structured claims. An exact retry returns the same
still-live unconsumed reference. Consumed, expired, changed-role or changed-
payload evidence requires a fresh proposal and attestation.

Role assertion normalization is exact and server-owned. Before comparing the
non-authoritative body assertion, the server maps only
`UserRole.Admin -> practice_manager` and
`UserRole.PracticeOwner -> practice_owner`; there are no aliases, case folding,
fallbacks or client-selected mappings. The mapped value must equal the asserted
value. The underlying current enum remains authoritative for authorization.

Evidence issuance uses a canonical attestation payload hash and one unique
practice/actor/proposal-hash record. A concurrent exact retry may return the
same still-live unconsumed reference; a changed payload conflicts. An expired
or consumed record cannot be renewed from the old proposal.

Every B4 route requires bounded nonblank `Idempotency-Key` and correlation
headers. The correlation header, body session-binding assertion and signed
proposal correlation value must be equal; mismatch rejects before domain
effect. Raw idempotency keys and session credentials are never persisted.
Proposal signing uses a dedicated server-only B4 command secret obtained from
configuration, never a client field, provider response, database row, log or
receipt. Missing/invalid configuration fails the feature closed.

### 5.4 Confirmation transaction

The confirm route, in order:

1. authenticates and authorizes `Admin|PracticeOwner` before disclosure;
2. claims durable idempotency on practice, actor, operation and key;
3. locks the exact practitioner aggregate and confirmation-evidence row;
4. reauthorizes the exact practice/action/resource with current user state;
5. verifies signed proposal, canonical request/proposal hashes, expiry,
   evidence binding, expected aggregate version, before-state hash and active
   same-practice location;
6. rejects a no-op, stale state or already consumed evidence without effects;
7. updates `Practitioner.default_location_id` once and increments
   `Practitioner.aggregate_version` once;
8. marks the evidence consumed by this command;
9. appends one immutable practice-administration audit row;
10. appends one unpublished transactional outbox row for exact event type
    `practice.practitioner_default_location_changed`, schema version
    `practice.practitioner_default_location_changed.v1`, and exact patient-free
    payload fields `practitioner_id`, `before_location_id`,
    `after_location_id`, `aggregate_version` and `reason_codes`, with reason
    codes exactly `["practitioner_default_location_changed"]`;
11. stores the exact bounded commit receipt on the idempotency row;
12. commits once, freshly reloads deterministic practitioner state and returns
    the receipt/readback.

Same key plus the same canonical fingerprint returns the stored receipt and an
`Idempotent-Replayed: true` transport marker with no new effect. Same key with a
different fingerprint returns `idempotency_conflict`. A different key using
consumed evidence returns `confirmation_replay_rejected`. In-progress fails
closed. Any transactional failure rolls back all seven persisted members.

### 5.5 Persistence

Add one sequential Alembic descendant after the current head with:

- non-null `practitioners.aggregate_version`, initial/server default `0`;
- `practice_administration_confirmation_evidence`;
- `practice_administration_command_idempotency`;
- `practice_administration_audit_events`;
- `practice_administration_outbox_events`.

The accepted OpenAPI artifact
`docs/api-spine/openapi/practice-administration-default-location-commands.yaml`
must be revised from architecture-only to this exact authorized local runtime
and must add the missing
`/proposals/{proposal_id}/confirmation-evidence` operation, its closed request
and response schemas, idempotency/replay semantics, role normalization and
zero-domain-mutation effect. Its proposal and confirm operations must be made
consistent with the three-step contract. This declarative update alone grants
no authority.

Every table is practice-scoped. Durable rows store hashes and bounded enum/code
values, never raw idempotency keys, provider output, patient data or free text.
Audit and outbox rows are append-only. Row-level security is enabled and forced
with exact current-practice policies. The outbox is storage only; publication
and workers remain closed.

## 6. Expected implementation ownership

After this freeze passes independent architecture review:

- a DeepSeek V4 Flash/high worker may implement the bounded A5.1 lane in an
  isolated descendant worktree;
- a separate DeepSeek V4 Flash/high worker may implement B4.1 in another
  isolated descendant worktree;
- Sol resolves the single Alembic chain, integrates by explicit paths, owns all
  acceptance and performs repairs that cross the lane boundary;
- a fresh Gemini 3.6 Flash/high Antigravity project performs the final
  read-only independent veto after deterministic gates pass.

Workers must not edit `AGENTS.md`, protected/historical acceptance artifacts,
provider configuration, deployment files or `docs/branding/`.

## 7. Acceptance matrix

### A5.1 deterministic acceptance

- proposal is non-mutating and expiring signed evidence binds current state,
  purpose, actor and a random nonce;
- exact Booked/Confirmed-to-Arrived success, with and without active waiting
  area;
- default-off practice admission and exact Receptionist-only role behavior;
- same-practice waiting area must be active and location-compatible;
- row-lock/current-state revalidation under stale and concurrent change;
- same-key replay returns exact stored response and no second audit/event;
- same-key changed body conflicts and in-progress fails closed;
- different-key same-evidence replay fails even after the appointment is
  deliberately restored to its original state;
- two concurrent distinct-key confirms of one evidence token produce exactly
  one success and one replay rejection;
- tampered/wrong-purpose/expired evidence, cross-practice appointment/area,
  inactive area, terminal source and no-op all produce zero effects;
- appointment status, waiting area, command-bound audit, committed event and
  idempotency completion are atomic;
- injected failures at evidence claim, audit, event and idempotency completion
  roll back every member;
- event payload contains no patient identifier/name or clinical/free text;
- the A5 receipt serialization is patient-free;
- an interleaved check-in row cannot enter or corrupt the reschedule feed;
- existing reschedule event, generic status-confirm, past-date and raw
  compatibility suites remain green;
- deterministic bounded readback matches committed PostgreSQL truth.

### B4.1 deterministic acceptance

- unauthorized roles reject before resource disclosure;
- default-off feature/practice admission rejects ordinary practices before
  resource disclosure;
- proposal performs zero database writes and is bounded to 120 seconds;
- attestation returns only a server-held opaque reference and changes no
  practitioner truth;
- the OpenAPI attestation operation is closed-schema and exactly matches the
  mounted route, role normalization and retry rules;
- exact Admin and PracticeOwner success paths;
- signed proposal/path/body/hash/actor/role/practice/version/before-state and
  evidence-payload binding adversarial cases;
- inactive/foreign practitioner or location, no-op, expiry, role revocation and
  current-state drift all fail closed;
- same-key replay, key conflict, in-progress and different-key evidence replay
  match the frozen semantics;
- aggregate version increments exactly once;
- practitioner truth, evidence consumption, audit, outbox and idempotency
  completion are atomic and rollback together;
- outbox/audit are patient-free, append-only and unpublished;
- deterministic readback matches committed PostgreSQL truth;
- migration upgrade/downgrade, forced RLS/policy and exact-schema tests pass.

### Whole descendant

- focused and full serial pytest pass;
- Ruff, Python compile and `git diff --check` pass;
- source and evidence hashes are bound from canonical LF bytes;
- provider call count is zero and no provider/runtime/product-data gate opens;
- exact task-branch-only Git state is verified before commit and push;
- fresh Gemini veto returns exactly one `pass` before Sol acceptance.

## 8. Stop conditions

The standing authority carries this descendant through ordinary plan, worker,
repair, test, review, commit and non-protected task-branch publication gates.
Stop only for a genuinely unplanned authority expansion, protected evidence or
protected-ref action, provider/product-data/production/deployment request,
conflicting evidence that changes acceptance meaning, or bounded recovery
exhaustion with no safe descendant.

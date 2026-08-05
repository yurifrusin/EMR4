# EMR4 Model-Required Bureaus — Paired A5.1/B4.1 Command Runtime Plan

Date: 2026-08-05
Status: frozen candidate for independent architecture veto before implementation
Parent authority: `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
API authority: `orchestration/api_spine_adr.md`

## 1. Exact result sought

This descendant implements two provider-free, backend-owned and human-confirmed
command paths without joining their domain authority:

1. **A5.1 Rayleen check-in** deliberately extends the existing appointment
   status proposal/confirm family for the exact `Booked|Confirmed -> Arrived`
   transition, with an optional current-practice active waiting area. The
   existing signed confirmation evidence remains the proposal binding. The
   confirmation transaction gains row locking, exact current-state
   revalidation, durable idempotency correlation, one immutable appointment
   audit row, one patient-free committed check-in event and deterministic
   readback.
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

### 4.1 Reused surface

Reuse and deliberately extend:

- `POST /api/v1/appointments/proposals/status/{appointment_id}`
- `POST /api/v1/appointments/proposals/status-confirm`
- `AppointmentStatusProposalIn`, `AppointmentStatusProposalConfirmationIn`
- the accepted HMAC signed status-confirm evidence and freshness binding
- `AppointmentCommandIdempotency` and `AppointmentAuditLog`

No Rayleen-only mutation endpoint or private action grammar is added. Rayleen
may supply proposal provenance; the current authenticated human remains the
actor and confirmer.

### 4.2 Exact check-in admission

The A5.1 committed-event branch applies only when all of these hold:

- current status is `Booked` or `Confirmed`;
- requested status is exactly `Arrived`;
- the proposal and signed evidence bind the same appointment, practice,
  authenticated staff user, current status, current waiting area, target
  status, target waiting area and freshness identifier;
- an optional target waiting area is active and belongs to the same practice;
- `confirmed=true` and the ordinary status-confirm role dependency admits the
  current human user;
- the exact appointment row is locked before the final state/evidence check.

Other existing status confirmations keep their present behavior and produce no
new check-in event. `Arrived -> Arrived`, terminal-to-arrived, stale, tampered,
cross-practice, inactive-area and role/session mismatch paths produce no truth,
audit, idempotency completion or event effect.

### 4.3 Atomic unit and event

Within the existing durable status-confirm transaction, A5.1 must:

1. claim the scoped idempotency key and canonical request fingerprint;
2. lock and revalidate the exact practice-scoped appointment;
3. verify the accepted signed status evidence and exact freshness;
4. update status to `Arrived` and apply the explicitly supplied waiting area;
5. append exactly one `AppointmentAuditLog` row bound to the command id;
6. append exactly one `DiaryCommittedEvent` with:
   - event type `diary.appointment_checked_in`;
   - schema version `diary.appointment_checked_in.v1`;
   - exact allowlisted patient-free payload fields
     `appointment_id`, `practitioner_id`, `location_id`, `status`,
     `waiting_area_id`, `reason_codes`;
   - reason codes exactly `["appointment_checked_in"]`;
7. complete the idempotency receipt with appointment and audit correlation;
8. commit once and return the freshly reloaded appointment.

The committed-event table and schema are extended by an exact conditional
allowlist for the second event family; the existing reschedule event contract
must remain byte-for-byte equivalent in behavior. No external publisher or
consumer is added.

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
    `practice.practitioner_default_location_changed.v1` with an allowlisted,
    patient-free payload;
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

- proposal is non-mutating and signed evidence binds current state;
- exact Booked/Confirmed-to-Arrived success, with and without active waiting
  area;
- row-lock/current-state revalidation under stale and concurrent change;
- same-key replay returns exact stored response and no second audit/event;
- same-key changed body conflicts and in-progress fails closed;
- tampered/wrong-purpose/expired evidence, cross-practice appointment/area,
  inactive area, terminal source and no-op all produce zero effects;
- appointment status, waiting area, command-bound audit, committed event and
  idempotency completion are atomic;
- event payload contains no patient identifier/name or clinical/free text;
- existing reschedule event, other status-confirm and raw compatibility suites
  remain green;
- deterministic readback matches committed PostgreSQL truth.

### B4.1 deterministic acceptance

- unauthorized roles reject before resource disclosure;
- proposal performs zero database writes and is bounded to 120 seconds;
- attestation returns only a server-held opaque reference and changes no
  practitioner truth;
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

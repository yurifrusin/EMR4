# API Spine Appointment Idempotency Storage Design

| Item | Value |
|---|---|
| Sprint | 126 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Storage design only; no model, migration, route behavior, provider, or GraphQL wiring changed |
| Steward posture | Define durable replay ledger shape and transaction boundary before implementation |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_appointment_idempotency_policy_packet.md`
- `orchestration/api_spine_appointment_idempotency_gap.md`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `app/routers/appointments.py`
- `app/models/appointments.py`
- `app/models/audit.py`
- `alembic/versions/`

## Proposed Storage Contract

Future implementation should add an appointment command replay ledger, tentatively
named `appointment_command_idempotency`.

Proposed columns:

| Column | Shape | Notes |
|---|---|---|
| `id` | UUID primary key | Internal ledger row id. |
| `practice_id` | UUID, indexed, required | Tenant scope. |
| `actor_user_id` | UUID/string, indexed, required | Human staff actor id; future non-human actors must use an explicit scoped service identity, not a null or shared placeholder. |
| `actor_role` | String, required | Audit evidence, not uniqueness scope. |
| `operation_id` | String, required | Canonical semantic operation id. |
| `route_family` | String, required | Backend route family or alias group. |
| `idempotency_key_hash` | Fixed string, required | HMAC/SHA-256 of the submitted key; never store raw key. |
| `request_body_hash` | Fixed string, required | Deterministic canonical body hash. |
| `request_body_canonicalization_version` | Integer, required | Start with version `1`. |
| `state` | Enum/string, required | `in_progress`, `completed`, `failed_transient`. |
| `response_status_code` | Integer, nullable until completed | Stored response status for replay. |
| `response_body_hash` | Fixed string, nullable until completed | Integrity check for stored response. |
| `response_body_json` | JSON, nullable until completed | Store only the response envelope needed for replay; no raw request body. |
| `result_kind` | String, nullable until completed | `confirmed_write`, `blocked`, or future typed result. |
| `target_appointment_id` | UUID, nullable | Appointment affected when one exists. |
| `audit_log_id` | UUID, nullable | Link to audit evidence when available. |
| `created_at` | Timestamp, required | Server time. |
| `updated_at` | Timestamp, required | Server time. |
| `expires_at` | Timestamp, nullable | Null for confirmation-write entries unless a later review approves expiry. |

Indexes and constraints:

- unique `(practice_id, actor_user_id, operation_id, idempotency_key_hash)`;
- index `(practice_id, target_appointment_id)`;
- index `(practice_id, created_at)`;
- check `state in ('in_progress', 'completed', 'failed_transient')`;
- check completed rows have `response_status_code`, `response_body_hash`, and
  `response_body_json`.

## Operation Identity

Operation ids must be canonical across backend aliases:

Alias naming must not weaken command-plane policy.

| Backend family | Canonical operation id |
|---|---|
| `POST /appointments/proposals/create/confirm` | `confirmAppointmentCreateProposal` |
| `POST /appointments/proposals/create/confirm-bernie` | `confirmAppointmentCreateProposal` |
| `POST /appointments/proposals/update/confirm` | `confirmAppointmentUpdateProposal` |
| `POST /appointments/proposals/status-confirm` | `confirmAppointmentStatusProposal` |
| `POST /appointments/proposals/delete-confirm` | `confirmAppointmentDeleteProposal` |

If proposal routes later require syntactic keys, they should use their canonical
OpenAPI proposal operation ids but must not create write replay authority.

## Canonical Body Hash

Version `1` canonicalization:

- parse JSON request body into typed schema first;
- dump model data with stable JSON-compatible values;
- sort object keys recursively;
- use compact separators with no insignificant whitespace;
- normalize UUIDs, dates, times, and datetimes to their canonical string forms;
- exclude transient request metadata such as correlation id;
- include the confirmation payload fields that the write depends on.

The hash should be SHA-256 over UTF-8 canonical JSON. The submitted
`Idempotency-Key` should be separately HMAC/SHA-256 hashed with a server secret
or equivalent keyed digest so raw keys are never stored.

## Transaction Boundary

Confirmation write flow:

1. Authenticate and authorize actor/practice.
2. Normalize and hash `Idempotency-Key`.
3. Canonicalize body and compute `request_body_hash`.
4. In a database transaction, insert an `in_progress` ledger row for the unique
   `(practice_id, actor_user_id, operation_id, idempotency_key_hash)` tuple.
5. If insert conflicts, lock the existing row:
   - `completed` + same body hash: return stored response without writing;
   - `completed` + different body hash: return `409 idempotency_key_conflict`;
   - `in_progress` + same body hash: return `409 idempotency_key_in_progress`
     or `425 too_early` without writing;
   - `in_progress` + different body hash: return `409 idempotency_key_conflict`.
6. Only the transaction that owns the new `in_progress` row may run freshness,
   signed evidence, warning acknowledgement, current-state, role/tenant, and
   audit preparation checks.
7. Perform the appointment mutation, audit write, and ledger completion in the
   same transaction.
8. Commit only after the appointment mutation, audit evidence, and completed ledger response are all durable.
9. If any part fails before commit, roll back the appointment write and ledger
   row together. The caller may retry with the same key.

This design uses the ledger row as the mutual exclusion point before the
appointment write, so concurrent same-key requests cannot both write.

Lock ordering must be ledger-first and appointment-row-second everywhere this
policy is implemented. A route or helper that can take an appointment lock before
the idempotency ledger lock must be refactored before it enters this command
plane, otherwise mixed ordering could deadlock under retries.

## Replay Semantics

- Same actor/practice/operation/key/body after completed confirmation returns the stored response, including the same appointment id.
- Same actor/practice/operation/key with a different body returns
  `409 idempotency_key_conflict`.
- Same user with a later role change still replays or conflicts by
  `actor_user_id`; `actor_role` remains first-execution audit evidence.
- New key with stale proposal evidence still fails freshness checks.
- Expired or deleted confirmation-write rows are not allowed by default.
- Stored-response replay should be visible to compliance without re-executing
  the mutation. Future implementation should either create a distinct
  idempotency-replay audit event or record replay telemetry that is explicitly
  linked to the original `audit_log_id`; it must not look like a second
  appointment mutation.

## Rollback And Recovery

- No appointment write may commit without the matching completed ledger row.
- No completed ledger row may commit without the matching appointment/audit
  result.
- A crash before transaction commit leaves no durable write and no completed
  replay result.
- A crash after transaction commit leaves both the appointment/audit result and
  replay result available.
- `failed_transient` is only for explicit recoverable infrastructure states; it
  must not mask an appointment write that may have committed.
- Stale `in_progress` rows require a reviewed recovery policy before route
  enforcement. The minimum acceptable policy must distinguish a genuinely active
  transaction from an orphaned row after process death, must avoid a second
  appointment write, and must be covered by concurrency/rollback tests.
- Confirmation-write `completed` rows do not expire by default. Any TTL for
  non-confirmation proposal/read rows, transient `failed_transient` rows, or
  orphaned `in_progress` rows is a separate reviewed decision and must not imply
  deletion of durable confirmation-write replay evidence.

## Raw Compatibility Writes

Raw compatibility writes remain a separate migration decision. Storage design
should support them by using route-family operation ids such as
`rawCompatAppointmentCreate`, but enforcement should wait until the
compatibility policy is chosen.

## Required Implementation Tests

Future storage implementation must prove:

- unique constraint rejects concurrent same-key insert attempts;
- an `in_progress` row is created before appointment mutation;
- same-key concurrent request cannot create a second appointment;
- same-key/same-body completed replay returns stored response;
- same-key/different-body returns `idempotency_key_conflict`;
- rollback before commit leaves no appointment and no completed ledger result;
- stale `in_progress` recovery cannot create a second appointment;
- completed confirmation-write rows do not expire by default;
- any non-confirmation TTL policy is explicit and separate from confirmation
  replay evidence;
- stored-response replay produces replay-specific audit/telemetry evidence
  without looking like a second appointment mutation;
- canonical JSON hash is stable across key ordering and whitespace changes;
- backend aliases share canonical operation ids;
- actor role changes do not create a second write for the same user/key;
- future system/integration actors use explicit scoped identities rather than
  null or shared actor placeholders;
- lock ordering is ledger-first and appointment-row-second.

## Out of Scope

This design does not:

- add SQLAlchemy models;
- add Alembic migrations;
- add FastAPI `Header(...)` bindings;
- require clients to send `Idempotency-Key` today;
- change raw compatibility route behavior;
- add GraphQL mutations;
- wire providers, runtime FGA clients, external patient clients, H15/H-series
  runtime imports, memory/RAG/GraphRAG, broad trove mining, or model-to-database
  writes.

## Smallest Next Alignment Slice

Recommended Sprint 127:

**Appointment command idempotency storage artifact guard.**

Add a non-runtime guard that compares this storage design with the future model
and migration names before any route enforcement. If implementation begins,
start with the model/migration and storage helper tests only; do not wire
appointment routes until the storage layer passes concurrency and rollback
tests.

## Gates Still Closed

This storage design does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.

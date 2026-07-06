# API Spine Appointment Idempotency Storage Artifact Guard

| Item | Value |
|---|---|
| Sprint | 127 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Guard only; no model, migration, route behavior, provider, or GraphQL wiring changed |
| Steward posture | Prevent partial storage implementation or route enforcement before the Sprint 126 storage contract exists in artifacts |

## Boundary Classification

This is a command-plane storage guard for future appointment confirmation
idempotency. It is not a runtime feature.

The accepted API Spine pattern remains:

1. appointment proposal command;
2. deterministic backend checks;
3. typed proposal envelope with evidence/freshness;
4. explicit staff confirmation;
5. REST confirm command with idempotency, evidence, and revalidation;
6. appointment write plus audit event;
7. durable idempotency replay evidence.

GraphQL remains read-only and receives no mutation or replay authority.

## Guarded Artifact Names

Future storage implementation is expected to introduce:

- table name: `appointment_command_idempotency`;
- model name: `AppointmentCommandIdempotency`;
- migration that creates `appointment_command_idempotency`;
- storage helper tests before route enforcement;
- route enforcement only after the model and migration satisfy the storage
  contract.

The guard scans current model and migration sources. If the table appears in one
artifact family but not the other, the test fails as a partial implementation.

## Required Model Signals

When the model appears, it must expose the Sprint 126 contract signals:

- `__tablename__ = "appointment_command_idempotency"`;
- `practice_id`;
- `actor_user_id`;
- `actor_role`;
- `operation_id`;
- `route_family`;
- `idempotency_key_hash`;
- `request_body_hash`;
- `request_body_canonicalization_version`;
- `state`;
- `response_status_code`;
- `response_body_hash`;
- `response_body_json`;
- `result_kind`;
- `target_appointment_id`;
- `audit_log_id`;
- `created_at`;
- `updated_at`;
- `expires_at`;
- unique constraint over
  `(practice_id, actor_user_id, operation_id, idempotency_key_hash)`;
- indexes for `(practice_id, target_appointment_id)` and
  `(practice_id, created_at)`;
- no `raw_idempotency_key`, `idempotency_key_raw`, `raw_request_body`, or
  `request_body_json` request storage field.
- a state check constraint for `in_progress`, `completed`, and
  `failed_transient`;
- completed-row nullability/check semantics for stored response status, hash,
  and JSON.

## Required Migration Signals

When the migration appears, it must create the same table and include the same
core columns, uniqueness scope, and indexes before any appointment route starts
requiring or consuming `Idempotency-Key`. It must also include the same state
check constraint and completed-row response-field checks as the storage design.

## Route Enforcement Gate

`app/routers/appointments.py` must not bind or enforce the HTTP
`Idempotency-Key` header for appointment commands until the model and migration
exist and storage helper tests prove at least:

- same-key/same-body replay returns the stored response;
- same-key/different-body conflicts;
- concurrent same-key attempts cannot create a second appointment;
- rollback before commit leaves no appointment and no completed replay row;
- stale `in_progress` recovery cannot create a second appointment;
- replay audit/telemetry is distinct from first execution;
- lock ordering is ledger-first and appointment-row-second.

The artifact guard treats these scenario names as route-enforcement
prerequisites. A future route-wiring sprint must add or reference concrete
storage-helper tests for each scenario before the HTTP header binding lands.

## Out Of Scope

This guard does not:

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

Recommended Sprint 128:

**Appointment command idempotency model/migration preflight.**

If implementation begins, add the SQLAlchemy model and Alembic migration plus
storage-helper tests only. Do not wire appointment routes until concurrency,
rollback, replay, stale `in_progress`, lock-ordering, and replay-audit tests
pass.

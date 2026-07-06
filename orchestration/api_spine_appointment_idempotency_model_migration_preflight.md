# API Spine Appointment Idempotency Model/Migration Preflight

| Item | Value |
|---|---|
| Sprint | 128 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Model and migration preflight only; no appointment route enforcement |
| Steward posture | Add storage artifacts required by Sprint 126/127 before any HTTP `Idempotency-Key` binding |

## What Exists Now

Sprint 128 adds the first storage artifacts for the appointment command
idempotency ledger:

- SQLAlchemy model `AppointmentCommandIdempotency`;
- table name `appointment_command_idempotency`;
- Alembic migration `l1m2n3o4p5q6_add_appointment_command_idempotency.py`;
- deterministic metadata/migration tests;
- continued artifact guard coverage from Sprint 127.

## Storage Contract Covered

The model and migration include:

- practice scope;
- actor identity and actor role evidence;
- canonical operation and route-family identity;
- HMAC/hash storage for submitted idempotency keys;
- deterministic request body hash;
- response status/hash/body envelope for replay;
- target appointment and audit-log links;
- created/updated/expiry timestamps;
- unique `(practice_id, actor_user_id, operation_id, idempotency_key_hash)`;
- indexes for `(practice_id, target_appointment_id)` and
  `(practice_id, created_at)`;
- state check for `in_progress`, `completed`, and `failed_transient`;
- completed-row check requiring replay response fields.

`actor_user_id` is a required string field so future scoped service identities
can be represented without null or shared placeholders.

## Still Not Implemented

Sprint 128 does not:

- bind or require HTTP `Idempotency-Key` in appointment routes;
- add storage helper functions;
- add route-level replay, conflict, stale `in_progress`, or lock-ordering
  behavior;
- change proposal or confirmation responses;
- add provider calls, GraphQL mutations, runtime FGA clients, external patient
  clients, H15/H-series runtime imports, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database writes beyond the migration artifact itself.

## Smallest Next Alignment Slice

Recommended Sprint 129:

**Appointment command idempotency storage helper tests.**

Add storage-layer helper behavior and tests for same-key replay, same-key body
conflict, ledger-first lock ordering, rollback, stale `in_progress`, and
replay audit/telemetry distinction. Keep appointment routes unwired until those
tests pass.

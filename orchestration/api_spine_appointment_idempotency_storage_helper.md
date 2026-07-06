# API Spine Appointment Idempotency Storage Helper

| Item | Value |
|---|---|
| Sprint | 129 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Storage helper foundation only; appointment routes remain unwired |
| Steward posture | Add storage-layer replay/conflict primitives before any HTTP `Idempotency-Key` enforcement |

## Helper Surface

Sprint 129 adds `app/services/appointment_idempotency.py` with storage-layer
helpers for:

- canonical JSON serialization;
- SHA-256 request and response body hashes;
- HMAC/SHA-256 idempotency-key hashing;
- ledger claim with ledger-first `with_for_update()` lookup;
- `started`, `replay`, `conflict`, `in_progress`, `stale_in_progress`, and
  `failed_transient` decisions;
- completed replay metadata storage through `complete_appointment_command()`.

The helper flushes rows but does not commit. Route handlers will still own the
larger transaction boundary when a later reviewed sprint wires HTTP command
enforcement.

`stale_in_progress` deliberately leaves the ledger row in `in_progress`; Sprint
130 must decide whether route callers surface an error, escalate, or recover
through a reviewed overwrite path. `expires_at` is not read or written by this
helper yet; any TTL or cleanup behavior remains a later policy decision.

## Guarded Behavior

The focused tests prove:

- canonical body hash is stable across JSON key ordering;
- submitted raw idempotency keys are not stored;
- first claim creates an `in_progress` ledger row;
- same-key/same-body completed replay returns the stored response;
- same-key/different-body returns `conflict`;
- same-key in-progress retry does not create a second row;
- stale `in_progress` is refused without creating a second write;
- `failed_transient` rows are surfaced as `failed_transient` decisions rather
  than being silently retried;
- helper source does not call `db.commit()` or create `Appointment` rows;
- appointment routes still do not bind HTTP `Idempotency-Key` or import the
  ledger model.

## Still Not Implemented

Sprint 129 does not:

- bind HTTP `Idempotency-Key` in appointment routes;
- wrap appointment mutation, audit write, and ledger completion in route
  transactions;
- implement replay audit events;
- implement concurrent worker integration tests;
- add provider calls, GraphQL mutations, runtime FGA clients, external patient
  clients, H15/H-series runtime imports, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database writes beyond the existing storage table.

## Smallest Next Alignment Slice

Recommended Sprint 130:

**Appointment idempotency route integration preflight.**

Add route-level integration tests or a reviewed wiring plan for one confirm
family, proving the helper is called before appointment mutation and that route
transactions include appointment write, audit evidence, and ledger completion
atomically. Keep the first route wiring narrow and reversible.

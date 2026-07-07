# Idempotency And Audit Metadata Preflight

Date: 2026-07-08

Sprint: 199

## Purpose

`tests/test_api_spine_idempotency_audit_metadata.py` is a static structural
preflight over `docs/api-spine/openapi/appointment-commands.yaml`.

It upgrades the earlier API Spine text checks into per-path and per-schema
guards for appointment command metadata. It does not import FastAPI routers,
issue HTTP requests, execute handlers, open database sessions, call providers,
read memory/RAG/GraphRAG, import H15/H-series runtime material, access
historical diary material, invoke GraphQL, or perform writes.

## Guarded Shape

- Appointment proposal and confirmation command paths carry both
  `Idempotency-Key` and `X-Correlation-Id` parameters.
- Slot-search command-style read paths carry `X-Correlation-Id` but not
  `Idempotency-Key`.
- Proposal envelopes retain structural `AuditIntent`, `FreshnessRef`, and
  signed-confirmation evidence metadata.
- Confirmation commands retain `confirmer`, `confirmed`, `freshness`, and
  `confirmed_warnings`, with `confirmed` pinned to `true`.
- Confirmation audit events retain `idempotency_key` and `correlation_id`
  fields so the idempotency/audit linkage remains representable.
- The OpenAPI artifact remains documentation-only and keeps blocked gates listed.

## Boundary

This preflight proves committed OpenAPI metadata shape only. It is not evidence
that backend handlers enforce idempotency storage, replay semantics, audit
durability, or production command behavior.

Runtime idempotency storage, append-only audit logging, provider enablement,
memory/RAG/GraphRAG wiring, H15/H-series runtime imports, broad historical diary
trove access, GraphQL mutation work, and model-to-database writes remain closed
gates requiring separate reviewed sprints.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_audit_metadata.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
```

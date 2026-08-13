# Threat-model delta — status-confirm HTTP route convergence

Date: 2026-08-13

Timestamp: 2026-08-13T12:24:35+10:00 (Australia/Brisbane)

## New seam

One existing authenticated FastAPI status-confirm route will invoke the
accepted application adapter and physical PostgreSQL transaction. A canonical
path and one compatibility alias share the handler. The status proposal adds
an opaque signed binding to the current database-owned appointment generation.

## Threats and controls

| Threat | Required control |
|---|---|
| Client selects a database generation | Mint the version binding server-side from the signed evidence signature and current positive `appointment_state_version`; verify its exact shape and HMAC before opening the command session, then compare under lock. |
| Binding or evidence key is reused across purposes | Derive separate domain-labelled keys for evidence, version, authenticated-session reference, idempotency and stored-session binding from the backend secret. |
| Raw bearer enters audit or durable receipt | Give the adapter the already-authenticated token only to derive a keyed session reference; persist neither token nor reversible token material. Closed evidence forbids both. |
| Request-scoped auth transaction is closed or reused as command transaction | Inject a distinct fresh command-session factory; the adapter exclusively owns and closes that session. |
| RLS blocks auth or client practice opens tenant context | Verify the JWT first, establish transaction-local context from its signed practice claim before user lookup, then require the current active user's database practice to match. |
| Canonical and old path diverge | Register two decorators on one handler, expose only the canonical path in OpenAPI, and forbid a second route-local implementation. |
| Waiting-area command inherits status write authority | Preserve the adapter's exact `AppointmentStatusProposalOut` admission and return typed `unsupported_status_confirm_variant`; never fall back to old local logic. |
| Framework reserialisation changes replay bytes | Return the physical receipt's validated `stored_response_bytes` directly in a Starlette response for both first success and replay. |
| Pre-deployment proposal survives key/contract change | Fail closed when the proposal lacks the new binding or its prior evidence signature does not verify under the domain-separated key; require a fresh proposal. |
| Error response leaks target existence | Preserve the accepted 404 closed unavailable mapping for cross-practice/missing targets and value-free blocked/error bodies. |
| Partial mutation occurs on projection or receipt failure | Keep all status, audit, version and private receipt work inside the accepted transaction; map failure only after rollback. |
| Test server reaches external systems or retains data | Cached image, internal Docker network, no published port, fixed loopback relay, tmpfs, bounded resources, no mounts and exact-ID cleanup. |

## Residual boundary

This tranche does not prove browser/Diary interaction, durable cue delivery,
restart, crash/unknown-commit recovery, production secret rotation, deployment
or operational data. The legacy raw compatibility status route remains outside
this seam. Other command families and CF-D2 remain separately gated.

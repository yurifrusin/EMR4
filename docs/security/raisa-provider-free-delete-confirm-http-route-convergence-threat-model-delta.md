# Threat-model delta — provider-free delete-confirm HTTP route convergence

Date: 2026-08-17

Timestamp: 2026-08-17T04:36:29.1514011+10:00 (Australia/Brisbane)

Status: frozen

Source HEAD: `d4a360640b2a50ae7c26ff5d020eca68c60c4533`

## Security boundary

This tranche exposes the already accepted delete-confirm adapter through one
authenticated FastAPI handler without executing its database command. The
route is transport only: it may carry returned opaque proposal evidence and a
human confirmation, but it cannot manufacture current authority, current
appointment truth, an idempotency result or command effect.

## Threats and controls

| Threat | Required control |
|---|---|
| Canonical and historical paths drift into separate writes | Both decorators bind one handler; the alias is hidden and contains no implementation. |
| Client selects a source generation | Server mints an HMAC binding over the signed evidence signature and current positive appointment version; input requires the opaque object. |
| Bearer or backend secret leaks into request/response/evidence | Bearer reaches only the accepted adapter; five keys are server-derived and never serialized or logged. |
| Route bypasses locked re-admission | Route calls only `compose_product_delete_confirm`; no route-local claim, read, mutation, audit, receipt or commit is permitted. |
| Private six-field command receipt is returned as HTTP | Successful content is freshly canonicalized from the validated public body; `stored_response_bytes` is never response content. |
| Replay reconstructs mutable appointment state | Committed and replay delivery share the same pure public-envelope serializer and contain no live appointment projection. |
| Broad response leaks patient or operational data | Versioned minimal schema rejects appointment, patient, practitioner, schedule, notes, audit identity and unknown fields. |
| Invalid adapter outcome triggers legacy fallback | Every blocked/error result returns its typed status/body; there is no fallback path. |
| Raw DELETE gains kernel authority by proximity | Raw DELETE remains unchanged, separately tagged and outside the confirmation envelope. |
| Test evidence accidentally becomes runtime proof | Evidence is labelled provider-free route composition only; no database, SQL or command effect is exercised. |

## Residual boundary

Passing does not prove a real database transaction through HTTP, product-data
behavior, concurrency, restart/unknown-commit recovery, client compatibility,
performance, provider safety, deployment or production. Those claims remain
closed. Protected evidence, `docs/branding/`, unrelated untracked files and
protected refs are outside scope.

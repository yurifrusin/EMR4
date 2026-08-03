# Threat-model delta: provider-free Office directory lifecycle descendants

Date: 2026-08-03

Parent: `docs/security/raisa-provider-free-office-practitioner-directory-consumer-threat-model-delta.md`

## Boundary change

No data or authority boundary opens. The existing task-scoped active-practitioner
consumer gains explicit lifecycle controls for navigation, session loss, replay
and sanitized observation, plus a route-free decision adapter.

| Threat | Control | Failure outcome |
|---|---|---|
| Reload leaves the first DOM authoritative | The first repeated delivery requests session revocation before returning an endpoint-free inert page and expired cookies | 503 if revocation cannot be established; no replacement launch |
| Back/forward cache restores opaque values | `pagehide` clears in-memory material; a persisted `pageshow` renders inert and sends nothing | Explicit close/reopen instruction |
| Double action issues multiple reads | One-use listener, synchronous in-flight guard and disabled button | No second request |
| Expired/revoked session leaks transport detail | 401/403 map to one fixed `session_unavailable` terminal copy | List cleared; no fallback or partial release |
| Desktop authority crosses into Word Online | Runtime surface binding plus independent cookie/CSRF partitions | 401/403 and zero product read |
| Result nonce crosses a surface or is replayed | Surface-specific digest comparison and atomic one-use admission | Fixed 400/409 response |
| Lifecycle evidence becomes a covert identifier log | Typed ten-reason counter set; no identifier fields or free-form reason input | Evidence gate fails |
| Extracted adapter is mistaken for a product mount | No router, database, cookie or identity dependency; absent from `app.main` | Static acceptance fails |

## Residual gates

This does not establish live Microsoft interoperability, real identity, patient,
clinical or document access, broader product reads, commands/writes, distributed
abuse resistance, monitoring/SIEM, organisational deployment, production,
protected integration or release.

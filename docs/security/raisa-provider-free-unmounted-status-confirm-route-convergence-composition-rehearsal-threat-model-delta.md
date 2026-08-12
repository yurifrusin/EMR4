# Status-confirm route-convergence composition rehearsal threat-model delta

Date: 2026-08-12

Status: frozen

`implementation_authorized: false`

## Assets

- server-owned practice, actor, role, session and current-authority facts;
- the idempotency key HMAC, request digest and opaque session digest;
- the locked appointment state version;
- the atomic mutation, audit and completed-receipt correlation; and
- the exact stored public response envelope.

## Threats and controls

| Threat | Control |
|---|---|
| A five-field private projection is mistaken for the complete public response | Freeze the full current envelope as canonical receipt bytes and validate the five-field projection inside it. |
| Replay rebuilds a response from later appointment state | Release only exact stored bytes after current-authority and integrity checks. |
| Client-supplied authority or session data opens the seam | Accept these facts only through the server-owned ingress object. |
| A waiting-area union member reaches the status kernel | Exact status-only adapter discrimination stops before transaction ingress. |
| Conflict or stored receipt leaks after revocation or target removal | Preserve practice/appointment/current-authority checks before idempotency classification. |
| Partial effect survives a failed response or incomplete scaffold | One physical transaction verifies mutation, audit, version and complete receipt before commit. |
| JSONB and canonical bytes diverge | Require parsed canonical bytes, stored JSON and stored SHA-256 to agree exactly. |
| Composition accidentally mounts or executes | The service remains unimported by routers and all scenarios use injected authored-synthetic doubles. |

No route, real database, provider, network, credential, product/patient data,
deployment, release, Pages or protected-ref authority is opened.

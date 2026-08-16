# Threat-model delta — delete-confirm route-mounting readiness review

Date: 2026-08-17

Timestamp: 2026-08-17T00:46:11.8521710+10:00 (Australia/Brisbane)

Status: frozen

`implementation_authorized: false`

| Threat | Required control |
|---|---|
| An unmounted adapter is mistaken for mounted behavior | Record current route behavior and accepted lower-layer prerequisites separately in every dimension. |
| Private receipt bytes are returned as the public HTTP body | Require the future route to serialize only the validated minimal public projection; private six-field bytes remain command truth and never become the client envelope. |
| The client selects or advances appointment generation | Treat proposal-version binding as opaque server-minted carriage and require locked comparison by the physical seam. |
| Canonical and historical paths diverge | Require canonical `/proposals/delete/confirm` plus hidden `/proposals/delete-confirm` decorators over one handler and one adapter call. |
| Request-scoped authentication session becomes the command transaction | Require the existing distinct command-session factory; the adapter alone owns and closes it. |
| Route-local claim/write logic survives as fallback | A future candidate must remove route-local idempotency, unlocked truth, mutation, audit, receipt and commit ownership from the confirmation handler. |
| The old response schema continues disclosing `AppointmentOut` | Treat the current full-appointment schema as a transition gap and require the exact minimal receipt envelope. |
| Raw compatibility DELETE inherits confirmation authority | Keep raw DELETE isolated and unchanged; no inference from the confirmed family is permitted. |
| OpenAPI claims canonical convergence before runtime | The read-only verdict records a route transition gap until one bounded route candidate changes router, schema and API Spine together. |
| Settled PostgreSQL behavior is reopened as ceremony | Consume the exact Continuity 303 evidence without Docker, SQL or database execution. |
| Review code imports product runtime | Use strict text/hash inspection only, deny `app` imports and run through the provider-free test surface. |

No patient, clinical, product, provider, credential, network, command,
deployment, release, Pages or protected-ref authority is opened.

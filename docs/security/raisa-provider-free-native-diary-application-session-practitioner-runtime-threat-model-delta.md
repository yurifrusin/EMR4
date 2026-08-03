# Threat-model delta: provider-free native-Diary application-session practitioner runtime

Date: 2026-08-03

Status: default-off provider-free runtime + direct HTTP/PostgreSQL evidence

## Boundary change

No product or data boundary opens beyond the exercised authored-synthetic
native-Diary application-session practitioner read.  The accepted shared router
intentionally accepts `practiceId`, display-safe field subsets and bounded
pagination variations; the native-Diary contract instead requires one fixed
request with no client-selected practice or projection.  A stricter outer
pre-auth admission guard is added while the accepted bridge/router is reused
unchanged underneath it.

## Threat controls

| Threat | Control | Failure outcome |
|---|---|---|
| A client selects practice, fields, pagination or operation | Bounded ASGI pre-auth guard requires POST, `application/json`, the fixed query constant and exact variables `{activeOnly: true, limit: 200, offset: 0}`, with no `practiceId`, alias, fragment, directive, introspection, mutation, field subset/extra field, pagination drift or extra JSON key | Generic 403 + `Cache-Control: no-store` before bridge authentication |
| Body replay or unbounded buffering | Guard buffers/replays at most 8192 bytes and rejects larger bodies | Oversized or malformed request denied before auth |
| Feature is on by default or mounted | Default-off factory; no product route, docs or OpenAPI when disabled; only literal explicit enablement constructs the router | Disabled app never opens a DB/session or releases a product row |
| The shared bridge/router is weakened | Accepted `create_application_session_practitioner_directory_router` reused unchanged, bound to `Surface.NATIVE_DIARY` | No shared surface change |
| The composition depends on Office terminal semantics | Native Diary is a long-lived surface; two sequential reads succeed on one session; revocation is backend-owned | Office one-use reload/logout lifecycle stays out |
| A bearer/localStorage or REST fallback is added on the enabled path | Enabled app exposes only the exact GraphQL product path; no bearer/localStorage/REST fallback | Fallback rejection in static checks |
| Wrong origin, missing/mismatched CSRF, Word-surface session, unknown/unmapped session, stale role or inactive user is admitted | Accepted bridge + runtime fail closed; post-revocation next request is 401 with no product row | No data release |
| Required audit cannot be admitted | Bridge releases no directory data when authorization audit is unavailable | 503 with no data release |
| Evidence records DSN, role names, passwords, UUIDs, names, session/CSRF values or authority envelopes | Harness persists counts, booleans, safe reason/status codes and hashes only | Evidence-sensitive scan rejects |
| The guard or adapter imports Office consumer or provider code | New file imports only the accepted product-read/bridge/runtime surfaces | Forbidden-dependency test fails |
| Convenience staging captures the user-owned branding directory | Explicit-path staging only; `git add -A`/`.` forbidden | Pre-commit gate fails |

## Residual gates

Live providers, browsers, real identity, patient/clinical data, product writes,
deployment, production, release, protected evidence and protected refs remain
closed.  There is no provider call, no browser automation and no real identity
use.  The evidence label is exactly `live_local_backend_postgres`; no provider,
no browser, no real identity, no patient/clinical, no product write, no
deployment and no production claim is made.  The evidence does not prove
rejection of an already-returned in-flight response before UI render;
request-time freshness and post-revocation denial are not a UI reconciliation
proof and that remains a later UI reconciliation obligation.  `docs/branding/`
remains user-owned and excluded.
